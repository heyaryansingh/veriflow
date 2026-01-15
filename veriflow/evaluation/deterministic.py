"""Deterministic evaluation utilities for Veriflow."""

from contextlib import contextmanager
from typing import Optional
import random
import numpy as np


def set_deterministic_seed(seed: int = 42) -> None:
    """Sets seeds for all random number generators to ensure deterministic behavior.
    
    Args:
        seed: Random seed value (default: 42)
    """
    # Python's random module
    random.seed(seed)
    
    # NumPy random
    np.random.seed(seed)
    
    # Try to set PyTorch seed if available
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass  # PyTorch not available, skip


def get_evaluation_seed(config_seed: Optional[int] = None) -> int:
    """Gets evaluation seed from config or returns default.
    
    Args:
        config_seed: Seed from config (optional)
        
    Returns:
        Seed value (default: 42)
    """
    return config_seed if config_seed is not None else 42


@contextmanager
def ensure_deterministic(seed: int = 42):
    """Context manager that ensures deterministic behavior during evaluation.
    
    Sets seeds at entry and restores state at exit (if needed).
    
    Args:
        seed: Random seed value (default: 42)
        
    Yields:
        None
    """
    # Set seeds
    set_deterministic_seed(seed)
    
    try:
        yield
    finally:
        # Seeds persist, but we could reset if needed
        # For now, we keep them set for the rest of the evaluation
        pass
