"""
LoRA Lightning Support for Ovi
Fast inference with LoRA adapters
"""

import os
import torch
import torch.nn as nn
from typing import Dict, Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class LoRALayer(nn.Module):
    """
    LoRA (Low-Rank Adaptation) layer for fast fine-tuning and inference.
    Optimized for Ampere GPUs.
    """
    
    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int = 4,
        alpha: float = 1.0,
        dropout: float = 0.0,
    ):
        super().__init__()
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank
        
        # LoRA matrices
        self.lora_A = nn.Parameter(torch.zeros(in_features, rank))
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))
        
        # Dropout for regularization
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        
        # Initialize
        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        nn.init.zeros_(self.lora_B)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with LoRA adaptation.
        x shape: [batch, ..., in_features]
        """
        # Apply LoRA: x @ A @ B * scaling
        lora_out = x @ self.lora_A @ self.lora_B * self.scaling
        return self.dropout(lora_out)


class LoRALinear(nn.Module):
    """
    Linear layer with LoRA adaptation.
    Can be merged for faster inference.
    """
    
    def __init__(
        self,
        base_layer: nn.Linear,
        rank: int = 4,
        alpha: float = 1.0,
        dropout: float = 0.0,
    ):
        super().__init__()
        self.base_layer = base_layer
        self.lora = LoRALayer(
            base_layer.in_features,
            base_layer.out_features,
            rank=rank,
            alpha=alpha,
            dropout=dropout,
        )
        self.merged = False
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.merged:
            return self.base_layer(x)
        else:
            return self.base_layer(x) + self.lora(x)
    
    def merge_weights(self):
        """Merge LoRA weights into base layer for faster inference."""
        if self.merged:
            return
        
        with torch.no_grad():
            # Compute LoRA contribution
            lora_weight = self.lora.lora_A @ self.lora.lora_B * self.lora.scaling
            # Add to base weight
            self.base_layer.weight.data += lora_weight.T
            
        self.merged = True
        logger.info("LoRA weights merged into base layer")
        
    def unmerge_weights(self):
        """Unmerge LoRA weights from base layer."""
        if not self.merged:
            return
            
        with torch.no_grad():
            lora_weight = self.lora.lora_A @ self.lora.lora_B * self.lora.scaling
            self.base_layer.weight.data -= lora_weight.T
            
        self.merged = False
        logger.info("LoRA weights unmerged from base layer")


class LoRAManager:
    """
    Manages multiple LoRA adapters and their application to models.
    Supports LoRA Lightning fast inference.
    """
    
    def __init__(self):
        self.adapters: Dict[str, Dict[str, torch.Tensor]] = {}
        self.active_adapter: Optional[str] = None
        
    def load_adapter(self, name: str, path: str):
        """
        Load a LoRA adapter from disk.
        
        Args:
            name: Identifier for this adapter
            path: Path to adapter weights
        """
        logger.info(f"Loading LoRA adapter '{name}' from {path}")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"LoRA adapter not found: {path}")
        
        # Load weights
        state_dict = torch.load(path, map_location='cpu')
        self.adapters[name] = state_dict
        
        logger.info(f"LoRA adapter '{name}' loaded successfully")
        
    def apply_adapter(
        self,
        model: nn.Module,
        adapter_name: str,
        target_modules: Optional[List[str]] = None,
        rank: int = 4,
        alpha: float = 1.0,
        merge: bool = True,
    ):
        """
        Apply LoRA adapter to model.
        
        Args:
            model: Model to adapt
            adapter_name: Name of adapter to apply
            target_modules: List of module names to adapt (e.g., ['q', 'v'])
            rank: LoRA rank
            alpha: LoRA alpha
            merge: Whether to merge weights for faster inference
        """
        if adapter_name not in self.adapters:
            raise ValueError(f"Adapter '{adapter_name}' not loaded")
        
        logger.info(f"Applying LoRA adapter '{adapter_name}' to model")
        
        adapter_state = self.adapters[adapter_name]
        
        # Default target modules for DiT-style models
        if target_modules is None:
            target_modules = ['q', 'k', 'v', 'o']
        
        # Apply LoRA to matching layers
        for name, module in model.named_modules():
            # Check if this module should be adapted
            should_adapt = any(target in name for target in target_modules)
            
            if should_adapt and isinstance(module, nn.Linear):
                # Get parent module
                parent_name = '.'.join(name.split('.')[:-1])
                child_name = name.split('.')[-1]
                parent = model.get_submodule(parent_name) if parent_name else model
                
                # Create LoRA layer
                lora_linear = LoRALinear(module, rank=rank, alpha=alpha)
                
                # Load adapter weights if available
                lora_a_key = f"{name}.lora_A"
                lora_b_key = f"{name}.lora_B"
                
                if lora_a_key in adapter_state and lora_b_key in adapter_state:
                    lora_linear.lora.lora_A.data = adapter_state[lora_a_key]
                    lora_linear.lora.lora_B.data = adapter_state[lora_b_key]
                
                # Replace module
                setattr(parent, child_name, lora_linear)
                
                # Merge if requested (Lightning mode)
                if merge:
                    lora_linear.merge_weights()
        
        self.active_adapter = adapter_name
        logger.info(f"LoRA adapter '{adapter_name}' applied successfully")
        
    def remove_adapter(self, model: nn.Module):
        """Remove active LoRA adapter from model."""
        if self.active_adapter is None:
            return
        
        logger.info("Removing LoRA adapter from model")
        
        # Unmerge and restore original layers
        for name, module in model.named_modules():
            if isinstance(module, LoRALinear):
                if module.merged:
                    module.unmerge_weights()
                    
                # Get parent and replace with base layer
                parent_name = '.'.join(name.split('.')[:-1])
                child_name = name.split('.')[-1]
                parent = model.get_submodule(parent_name) if parent_name else model
                setattr(parent, child_name, module.base_layer)
        
        self.active_adapter = None
        logger.info("LoRA adapter removed")
        
    def save_adapter(self, model: nn.Module, name: str, path: str):
        """
        Save current LoRA weights to disk.
        
        Args:
            model: Model with LoRA layers
            name: Name for this adapter
            path: Save path
        """
        logger.info(f"Saving LoRA adapter '{name}' to {path}")
        
        state_dict = {}
        for module_name, module in model.named_modules():
            if isinstance(module, LoRALinear):
                state_dict[f"{module_name}.lora_A"] = module.lora.lora_A.data
                state_dict[f"{module_name}.lora_B"] = module.lora.lora_B.data
        
        torch.save(state_dict, path)
        self.adapters[name] = state_dict
        
        logger.info(f"LoRA adapter '{name}' saved successfully")


def create_lora_config(
    rank: int = 4,
    alpha: float = 1.0,
    target_modules: Optional[List[str]] = None,
    dropout: float = 0.0,
) -> Dict:
    """
    Create LoRA configuration dictionary.
    
    Args:
        rank: LoRA rank (lower = faster, higher = more capacity)
        alpha: LoRA alpha (scaling factor)
        target_modules: Module names to adapt
        dropout: Dropout rate
        
    Returns:
        Configuration dictionary
    """
    if target_modules is None:
        # Default for DiT models
        target_modules = ['q', 'k', 'v', 'o']
    
    return {
        'rank': rank,
        'alpha': alpha,
        'target_modules': target_modules,
        'dropout': dropout,
    }


# Preset configurations for common use cases
LORA_CONFIGS = {
    'lightning': {
        'rank': 4,
        'alpha': 4.0,
        'target_modules': ['q', 'v'],  # Minimal for speed
        'dropout': 0.0,
        'merge': True,  # Merge for Lightning mode
    },
    'quality': {
        'rank': 16,
        'alpha': 16.0,
        'target_modules': ['q', 'k', 'v', 'o'],
        'dropout': 0.1,
        'merge': False,
    },
    'balanced': {
        'rank': 8,
        'alpha': 8.0,
        'target_modules': ['q', 'v', 'o'],
        'dropout': 0.05,
        'merge': True,
    },
}


def get_lora_config(preset: str = 'lightning') -> Dict:
    """Get a preset LoRA configuration."""
    if preset not in LORA_CONFIGS:
        raise ValueError(f"Unknown preset: {preset}. Choose from {list(LORA_CONFIGS.keys())}")
    return LORA_CONFIGS[preset].copy()
