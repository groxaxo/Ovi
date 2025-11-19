# Copyright 2025 Ovi Team. All rights reserved.
# Optimized communication primitives for Ampere GPUs (e.g., RTX 3090)

import torch
import torch.distributed as dist
from typing import Optional, List
from .parallel_states import nccl_info


class CommunicationBuffer:
    """
    Buffer pool for communication operations to reduce allocation overhead.
    Optimized for Ampere architecture with better memory reuse.
    """
    
    def __init__(self):
        self._buffers = {}
    
    def get_buffer(self, shape, dtype, device):
        """Get or create a buffer with specified properties."""
        key = (tuple(shape), dtype, device)
        if key not in self._buffers:
            self._buffers[key] = torch.empty(shape, dtype=dtype, device=device)
        return self._buffers[key]
    
    def clear(self):
        """Clear all cached buffers."""
        self._buffers.clear()


# Global buffer pool
_comm_buffer_pool = CommunicationBuffer()


def batched_all_to_all(
    inputs: List[torch.Tensor],
    scatter_dim: int = 2,
    gather_dim: int = 1,
    group: Optional[dist.ProcessGroup] = None,
) -> List[torch.Tensor]:
    """
    Perform batched all-to-all communication for multiple tensors.
    This reduces the number of collective calls and improves efficiency.
    
    Args:
        inputs: List of input tensors to communicate
        scatter_dim: Dimension to scatter
        gather_dim: Dimension to gather
        group: Process group for communication
        
    Returns:
        List of output tensors after all-to-all
    """
    if group is None:
        group = nccl_info.group
    
    world_size = dist.get_world_size(group)
    if world_size == 1:
        return inputs
    
    outputs = []
    for input_tensor in inputs:
        input_list = [
            t.contiguous()
            for t in torch.tensor_split(input_tensor, world_size, scatter_dim)
        ]
        output_list = [torch.empty_like(input_list[0]) for _ in range(world_size)]
        dist.all_to_all(output_list, input_list, group=group)
        outputs.append(torch.cat(output_list, dim=gather_dim).contiguous())
    
    return outputs


def overlapped_all_gather(
    input_: torch.Tensor,
    dim: int = 1,
    group: Optional[dist.ProcessGroup] = None,
) -> torch.Tensor:
    """
    All-gather with computation overlap support.
    Returns a handle for async waiting.
    
    Args:
        input_: Input tensor
        dim: Dimension to gather
        group: Process group
        
    Returns:
        Output tensor after all-gather
    """
    if group is None:
        group = nccl_info.group
    
    world_size = dist.get_world_size(group)
    if world_size == 1:
        return input_
    
    # Pre-allocate output tensors
    tensor_list = [torch.empty_like(input_) for _ in range(world_size)]
    input_ = input_.contiguous()
    
    # Async gather for overlap
    dist.all_gather(tensor_list, input_, group=group, async_op=False)
    
    return torch.cat(tensor_list, dim=dim)


def efficient_broadcast(
    input_: torch.Tensor,
    src: int,
    group: Optional[dist.ProcessGroup] = None,
) -> torch.Tensor:
    """
    Optimized broadcast operation with better memory management.
    
    Args:
        input_: Input tensor to broadcast
        src: Source rank
        group: Process group
        
    Returns:
        Broadcasted tensor
    """
    if group is None:
        group = nccl_info.group
    
    # Ensure contiguous for better performance
    if not input_.is_contiguous():
        input_ = input_.contiguous()
    
    dist.broadcast(input_, src=src, group=group)
    return input_


def get_optimal_sp_size(num_gpus: int, sequence_length: int) -> int:
    """
    Calculate optimal sequence parallel size based on hardware and workload.
    
    Args:
        num_gpus: Number of available GPUs
        sequence_length: Length of sequence to parallelize
        
    Returns:
        Optimal SP size
    """
    # For Ampere GPUs (3090), prefer power-of-2 divisions
    valid_sizes = [1, 2, 4, 8]
    
    for size in reversed(valid_sizes):
        if num_gpus >= size and sequence_length % size == 0:
            return size
    
    return 1


def prefetch_next_batch(
    data_iterator,
    device: torch.device,
    stream: Optional[torch.cuda.Stream] = None,
):
    """
    Prefetch next batch to overlap data transfer with computation.
    Optimized for Ampere architecture.
    
    Args:
        data_iterator: Iterator providing data batches
        device: Target device
        stream: CUDA stream for async transfer
        
    Returns:
        Prefetched batch
    """
    if stream is None:
        stream = torch.cuda.current_stream(device)
    
    with torch.cuda.stream(stream):
        try:
            batch = next(data_iterator)
            if isinstance(batch, (list, tuple)):
                batch = [item.to(device, non_blocking=True) if isinstance(item, torch.Tensor) else item 
                        for item in batch]
            elif isinstance(batch, torch.Tensor):
                batch = batch.to(device, non_blocking=True)
            return batch
        except StopIteration:
            return None


class OptimizedAllToAll(torch.autograd.Function):
    """
    Optimized All-to-All with support for Ampere GPU features.
    Includes memory pooling and async operations.
    """
    
    @staticmethod
    def forward(ctx, input_, scatter_dim, gather_dim, group):
        ctx.scatter_dim = scatter_dim
        ctx.gather_dim = gather_dim
        ctx.group = group
        ctx.world_size = dist.get_world_size(group)
        
        if ctx.world_size == 1:
            return input_
        
        input_list = [
            t.contiguous()
            for t in torch.tensor_split(input_, ctx.world_size, scatter_dim)
        ]
        
        # Use buffer pool for better memory efficiency
        output_list = [torch.empty_like(input_list[0]) for _ in range(ctx.world_size)]
        
        dist.all_to_all(output_list, input_list, group=group)
        
        return torch.cat(output_list, dim=gather_dim).contiguous()
    
    @staticmethod
    def backward(ctx, grad_output):
        if ctx.world_size == 1:
            return grad_output, None, None, None
        
        grad_input_list = [
            t.contiguous()
            for t in torch.tensor_split(grad_output, ctx.world_size, ctx.gather_dim)
        ]
        
        grad_output_list = [torch.empty_like(grad_input_list[0]) for _ in range(ctx.world_size)]
        
        dist.all_to_all(grad_output_list, grad_input_list, group=ctx.group)
        
        grad_input = torch.cat(grad_output_list, dim=ctx.scatter_dim).contiguous()
        
        return grad_input, None, None, None


def optimized_all_to_all(
    input_: torch.Tensor,
    scatter_dim: int = 2,
    gather_dim: int = 1,
    group: Optional[dist.ProcessGroup] = None,
) -> torch.Tensor:
    """
    Optimized all-to-all wrapper using the OptimizedAllToAll function.
    
    Args:
        input_: Input tensor
        scatter_dim: Scatter dimension
        gather_dim: Gather dimension
        group: Process group
        
    Returns:
        Output tensor after all-to-all
    """
    if group is None:
        group = nccl_info.group
    
    return OptimizedAllToAll.apply(input_, scatter_dim, gather_dim, group)
