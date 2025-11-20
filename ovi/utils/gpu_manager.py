"""
GPU Management and Multi-GPU Allocation
Handles GPU selection, VRAM optimization, and workload distribution
"""

import torch
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VRAMConfig:
    """Configuration for VRAM optimization modes"""
    mode: str
    fp8: bool
    cpu_offload: bool
    qint8: bool
    max_batch_size: int
    description: str


# Predefined VRAM optimization modes based on aistudynow.com guide
VRAM_MODES = {
    'standard': VRAMConfig(
        mode='standard',
        fp8=False,
        cpu_offload=False,
        qint8=False,
        max_batch_size=1,
        description='Best quality for high-end GPUs (32GB+ VRAM)'
    ),
    'fp8': VRAMConfig(
        mode='fp8',
        fp8=True,
        cpu_offload=False,
        qint8=False,
        max_batch_size=1,
        description='FP8 quantization for 24GB VRAM GPUs'
    ),
    'fp8_offload': VRAMConfig(
        mode='fp8_offload',
        fp8=True,
        cpu_offload=True,
        qint8=False,
        max_batch_size=1,
        description='FP8 with CPU offload for 16-24GB VRAM'
    ),
    'ultra_low': VRAMConfig(
        mode='ultra_low',
        fp8=False,
        cpu_offload=True,
        qint8=True,
        max_batch_size=1,
        description='QINT8 with CPU offload for 8-16GB VRAM'
    ),
}


@dataclass
class GPUAllocation:
    """GPU allocation configuration"""
    mode: str
    num_gpus: int
    sp_size: int
    use_fsdp: bool
    fsdp_strategy: Optional[str]
    description: str


# GPU allocation strategies
GPU_ALLOCATIONS = {
    'auto': GPUAllocation(
        mode='auto',
        num_gpus=-1,  # Auto-detect
        sp_size=1,
        use_fsdp=False,
        fsdp_strategy=None,
        description='Automatically distribute across available GPUs'
    ),
    'single': GPUAllocation(
        mode='single',
        num_gpus=1,
        sp_size=1,
        use_fsdp=False,
        fsdp_strategy=None,
        description='Use single GPU'
    ),
    'multi_2': GPUAllocation(
        mode='multi_2',
        num_gpus=2,
        sp_size=2,
        use_fsdp=False,
        fsdp_strategy=None,
        description='Sequence parallel across 2 GPUs'
    ),
    'multi_4': GPUAllocation(
        mode='multi_4',
        num_gpus=4,
        sp_size=4,
        use_fsdp=False,
        fsdp_strategy=None,
        description='Sequence parallel across 4 GPUs'
    ),
    'multi_8': GPUAllocation(
        mode='multi_8',
        num_gpus=8,
        sp_size=8,
        use_fsdp=False,
        fsdp_strategy=None,
        description='Sequence parallel across 8 GPUs'
    ),
    'fsdp': GPUAllocation(
        mode='fsdp',
        num_gpus=-1,  # Auto-detect
        sp_size=1,
        use_fsdp=True,
        fsdp_strategy='FULL_SHARD',
        description='FSDP sharded inference for memory efficiency'
    ),
}


class GPUManager:
    """
    Manages GPU allocation and workload distribution
    Inspired by ComfyUI-MultiGPU concepts for optimal GPU utilization
    """
    
    def __init__(self):
        self.num_gpus = torch.cuda.device_count()
        self.gpu_memory = self._get_gpu_memory()
        logger.info(f"GPUManager initialized: {self.num_gpus} GPUs available")
        for i, mem in enumerate(self.gpu_memory):
            logger.info(f"  GPU {i}: {mem / 1024**3:.2f} GB VRAM")
    
    def _get_gpu_memory(self) -> List[int]:
        """Get total memory for each GPU"""
        memory = []
        for i in range(self.num_gpus):
            props = torch.cuda.get_device_properties(i)
            memory.append(props.total_memory)
        return memory
    
    def get_available_gpus(self) -> List[int]:
        """Get list of available GPU indices"""
        return list(range(self.num_gpus))
    
    def get_best_gpu(self) -> int:
        """Get GPU with most free memory"""
        if self.num_gpus == 0:
            raise RuntimeError("No GPUs available")
        
        free_memory = []
        for i in range(self.num_gpus):
            torch.cuda.set_device(i)
            free_mem = torch.cuda.mem_get_info()[0]
            free_memory.append(free_mem)
        
        best_gpu = free_memory.index(max(free_memory))
        logger.info(f"Best GPU: {best_gpu} with {free_memory[best_gpu] / 1024**3:.2f} GB free")
        return best_gpu
    
    def allocate_gpus(self, allocation_mode: str = 'auto') -> GPUAllocation:
        """
        Allocate GPUs based on mode and availability
        
        Args:
            allocation_mode: One of 'auto', 'single', 'multi_2', 'multi_4', 'multi_8', 'fsdp'
            
        Returns:
            GPUAllocation configuration
        """
        if allocation_mode not in GPU_ALLOCATIONS:
            logger.warning(f"Unknown allocation mode '{allocation_mode}', using 'auto'")
            allocation_mode = 'auto'
        
        allocation = GPU_ALLOCATIONS[allocation_mode]
        
        # Handle auto mode
        if allocation_mode == 'auto':
            if self.num_gpus == 1:
                allocation = GPU_ALLOCATIONS['single']
            elif self.num_gpus == 2:
                allocation = GPU_ALLOCATIONS['multi_2']
            elif self.num_gpus >= 4:
                allocation = GPU_ALLOCATIONS['multi_4']
            else:
                allocation = GPU_ALLOCATIONS['single']
        
        # Validate GPU count
        if allocation.num_gpus > 0 and allocation.num_gpus > self.num_gpus:
            logger.warning(
                f"Requested {allocation.num_gpus} GPUs but only {self.num_gpus} available. "
                f"Using {self.num_gpus} GPUs instead."
            )
            # Fallback to available GPUs
            if self.num_gpus >= 4:
                allocation = GPU_ALLOCATIONS['multi_4']
            elif self.num_gpus == 2:
                allocation = GPU_ALLOCATIONS['multi_2']
            else:
                allocation = GPU_ALLOCATIONS['single']
        
        logger.info(f"GPU allocation: {allocation.description}")
        return allocation
    
    def get_vram_config(self, vram_mode: str = 'standard') -> VRAMConfig:
        """
        Get VRAM optimization configuration
        
        Args:
            vram_mode: One of 'standard', 'fp8', 'fp8_offload', 'ultra_low'
            
        Returns:
            VRAMConfig with optimization settings
        """
        if vram_mode not in VRAM_MODES:
            logger.warning(f"Unknown VRAM mode '{vram_mode}', using 'standard'")
            vram_mode = 'standard'
        
        config = VRAM_MODES[vram_mode]
        logger.info(f"VRAM optimization: {config.description}")
        return config
    
    def estimate_vram_usage(
        self,
        resolution: Tuple[int, int],
        duration: str,
        vram_mode: str = 'standard'
    ) -> float:
        """
        Estimate VRAM usage for a generation task
        
        Args:
            resolution: (height, width) tuple
            duration: '5s' or '10s'
            vram_mode: VRAM optimization mode
            
        Returns:
            Estimated VRAM usage in GB
        """
        height, width = resolution
        frames = 121 if duration == '5s' else 241
        
        # Base VRAM usage calculation (rough estimates)
        base_vram = 80.0  # GB for standard mode, 720x720, 5s
        
        # Adjust for resolution
        area_factor = (height * width) / (720 * 720)
        vram = base_vram * area_factor
        
        # Adjust for duration
        if duration == '10s':
            vram *= 1.5
        
        # Apply VRAM mode optimizations
        vram_config = self.get_vram_config(vram_mode)
        if vram_config.fp8:
            vram *= 0.3  # FP8 reduces to ~24GB
        if vram_config.qint8:
            vram *= 0.3  # QINT8 similar reduction
        if vram_config.cpu_offload:
            vram *= 0.4  # CPU offload significantly reduces peak VRAM
        
        logger.info(
            f"Estimated VRAM usage: {vram:.2f} GB "
            f"(resolution={resolution}, duration={duration}, mode={vram_mode})"
        )
        return vram
    
    def can_run_on_gpu(
        self,
        gpu_id: int,
        resolution: Tuple[int, int],
        duration: str,
        vram_mode: str = 'standard'
    ) -> bool:
        """Check if a GPU has enough memory for a task"""
        required_vram = self.estimate_vram_usage(resolution, duration, vram_mode)
        available_vram = self.gpu_memory[gpu_id] / 1024**3  # Convert to GB
        
        can_run = available_vram >= required_vram
        logger.info(
            f"GPU {gpu_id}: {available_vram:.2f} GB available, "
            f"{required_vram:.2f} GB required - {'OK' if can_run else 'INSUFFICIENT'}"
        )
        return can_run
    
    def get_optimal_settings(
        self,
        resolution: Tuple[int, int],
        duration: str
    ) -> Dict:
        """
        Automatically determine optimal VRAM mode and GPU allocation
        
        Returns:
            Dictionary with recommended settings
        """
        # Check what we can run with standard mode
        for gpu_id in range(self.num_gpus):
            if self.can_run_on_gpu(gpu_id, resolution, duration, 'standard'):
                return {
                    'vram_mode': 'standard',
                    'gpu_allocation': 'auto',
                    'reason': f'GPU {gpu_id} has sufficient VRAM for standard mode'
                }
        
        # Try FP8
        for gpu_id in range(self.num_gpus):
            if self.can_run_on_gpu(gpu_id, resolution, duration, 'fp8'):
                return {
                    'vram_mode': 'fp8',
                    'gpu_allocation': 'auto',
                    'reason': 'Requires FP8 quantization'
                }
        
        # Try FP8 + offload
        for gpu_id in range(self.num_gpus):
            if self.can_run_on_gpu(gpu_id, resolution, duration, 'fp8_offload'):
                return {
                    'vram_mode': 'fp8_offload',
                    'gpu_allocation': 'single',
                    'reason': 'Requires FP8 + CPU offload'
                }
        
        # Fall back to ultra low
        return {
            'vram_mode': 'ultra_low',
            'gpu_allocation': 'single',
            'reason': 'Requires ultra low VRAM mode'
        }


# Global GPU manager instance
_gpu_manager = None


def get_gpu_manager() -> GPUManager:
    """Get or create global GPU manager instance"""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUManager()
    return _gpu_manager
