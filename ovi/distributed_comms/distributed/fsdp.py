# Copyright 2024-2025 The Alibaba Wan Team Authors. All rights reserved.
from functools import partial
import logging

import torch
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import MixedPrecision, ShardingStrategy, CPUOffload
from torch.distributed.fsdp.wrap import lambda_auto_wrap_policy, transformer_auto_wrap_policy
from torch.distributed.algorithms._checkpoint.checkpoint_wrapper import (
    checkpoint_wrapper,
    CheckpointImpl,
    apply_activation_checkpointing,
)


def shard_model(
    model,
    device_id,
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.float32,
    buffer_dtype=torch.float32,
    process_group=None,
    sharding_strategy=ShardingStrategy.FULL_SHARD,
    sync_module_states=True,
):
    """
    Original shard_model function for training/fine-tuning.
    """
    model = FSDP(
        module=model,
        process_group=process_group,
        sharding_strategy=sharding_strategy,
        auto_wrap_policy=partial(
            lambda_auto_wrap_policy, lambda_fn=lambda m: m in model.blocks),
        mixed_precision=MixedPrecision(
            param_dtype=param_dtype,
            reduce_dtype=reduce_dtype,
            buffer_dtype=buffer_dtype),
        device_id=device_id,
        sync_module_states=sync_module_states)
    return model


def shard_model_for_inference(
    model,
    device_id,
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.float32,
    buffer_dtype=torch.float32,
    process_group=None,
    sharding_strategy=ShardingStrategy.FULL_SHARD,
    cpu_offload=False,
    use_activation_checkpointing=False,
):
    """
    Shard model for inference with optimizations for Ampere GPUs.
    
    Args:
        model: Model to shard
        device_id: Device ID
        param_dtype: Parameter dtype (bf16 for Ampere optimization)
        reduce_dtype: Reduction dtype
        buffer_dtype: Buffer dtype
        process_group: Process group for FSDP
        sharding_strategy: Sharding strategy (FULL_SHARD, SHARD_GRAD_OP, HYBRID_SHARD, etc.)
        cpu_offload: Whether to offload parameters to CPU
        use_activation_checkpointing: Whether to use activation checkpointing
        
    Returns:
        Sharded model ready for inference
    """
    logging.info(f"Sharding model for inference with strategy: {sharding_strategy}")
    
    # Configure CPU offload if requested
    cpu_offload_config = CPUOffload(offload_params=True) if cpu_offload else None
    
    # Auto-wrap policy for transformer blocks
    auto_wrap_policy = partial(
        lambda_auto_wrap_policy, 
        lambda_fn=lambda m: m in getattr(model, 'blocks', [])
    )
    
    # Mixed precision config optimized for Ampere
    mixed_precision_policy = MixedPrecision(
        param_dtype=param_dtype,
        reduce_dtype=reduce_dtype,
        buffer_dtype=buffer_dtype
    )
    
    # Wrap model with FSDP
    sharded_model = FSDP(
        module=model,
        process_group=process_group,
        sharding_strategy=sharding_strategy,
        auto_wrap_policy=auto_wrap_policy,
        mixed_precision=mixed_precision_policy,
        device_id=device_id,
        cpu_offload=cpu_offload_config,
        sync_module_states=True,  # Sync states across ranks for inference
        use_orig_params=True,  # Use original parameters for better compatibility
    )
    
    # Apply activation checkpointing if requested
    if use_activation_checkpointing and hasattr(model, 'blocks'):
        logging.info("Applying activation checkpointing to transformer blocks")
        non_reentrant_wrapper = partial(
            checkpoint_wrapper,
            checkpoint_impl=CheckpointImpl.NO_REENTRANT,
        )
        
        check_fn = lambda submodule: isinstance(submodule, type(model.blocks[0]))
        apply_activation_checkpointing(
            sharded_model,
            checkpoint_wrapper_fn=non_reentrant_wrapper,
            check_fn=check_fn,
        )
    
    logging.info(f"Model sharded successfully for inference on device {device_id}")
    return sharded_model


def get_optimal_sharding_strategy(
    num_gpus: int,
    model_size_gb: float,
    available_memory_gb: float,
) -> ShardingStrategy:
    """
    Determine optimal sharding strategy based on hardware constraints.
    
    Args:
        num_gpus: Number of GPUs available
        model_size_gb: Model size in GB
        available_memory_gb: Available memory per GPU in GB
        
    Returns:
        Recommended ShardingStrategy
    """
    memory_per_gpu = model_size_gb / num_gpus
    
    # If model fits comfortably in memory, use SHARD_GRAD_OP for better performance
    if memory_per_gpu < available_memory_gb * 0.5:
        logging.info("Using SHARD_GRAD_OP for better performance")
        return ShardingStrategy.SHARD_GRAD_OP
    
    # If model is tight on memory, use FULL_SHARD
    elif memory_per_gpu < available_memory_gb * 0.8:
        logging.info("Using FULL_SHARD for memory efficiency")
        return ShardingStrategy.FULL_SHARD
    
    # If model doesn't fit, use HYBRID_SHARD with CPU offload
    else:
        logging.info("Using HYBRID_SHARD due to memory constraints")
        return ShardingStrategy.HYBRID_SHARD


def configure_fsdp_for_ampere(model, device_id, num_gpus, cpu_offload=False):
    """
    Configure FSDP with optimizations specific to Ampere architecture (RTX 3090).
    
    Args:
        model: Model to configure
        device_id: Device ID
        num_gpus: Number of GPUs
        cpu_offload: Whether to enable CPU offload
        
    Returns:
        Configured FSDP model
    """
    # Ampere GPUs benefit from bf16 for better performance
    param_dtype = torch.bfloat16
    
    # Estimate model size (rough approximation)
    total_params = sum(p.numel() for p in model.parameters())
    model_size_gb = (total_params * 2) / (1024**3)  # Assuming bf16
    
    # RTX 3090 has 24GB memory
    available_memory_gb = 20.0  # Conservative estimate
    
    # Get optimal strategy
    sharding_strategy = get_optimal_sharding_strategy(
        num_gpus=num_gpus,
        model_size_gb=model_size_gb,
        available_memory_gb=available_memory_gb,
    )
    
    # Shard model for inference
    return shard_model_for_inference(
        model=model,
        device_id=device_id,
        param_dtype=param_dtype,
        reduce_dtype=torch.float32,
        buffer_dtype=torch.float32,
        sharding_strategy=sharding_strategy,
        cpu_offload=cpu_offload,
        use_activation_checkpointing=False,  # Disabled for inference
    )
