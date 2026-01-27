"""
Seed control utilities for reproducible experiments.

All experiments should use these utilities to ensure consistent random number generation.
"""

import random
import numpy as np
import os
from typing import Optional

# Global seed for all experiments
GLOBAL_SEED = 42


def set_seeds(seed: Optional[int] = GLOBAL_SEED) -> None:
    """
    Set all random seeds for reproducibility.
    
    Args:
        seed: Random seed (default: 42)
    
    Note:
        LLM API calls (OpenAI, Anthropic) are non-deterministic even with seeds.
        Expect ±2% variance in results due to LLM sampling.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    
    print(f"[SEED] Set random seed to {seed}")
    print("[WARNING] LLM API calls are non-deterministic. Expect ±2% variance.")


def get_seed() -> int:
    """Get the global seed value."""
    return GLOBAL_SEED


if __name__ == "__main__":
    # Test seed control
    set_seeds(42)
    
    # Test Python random
    print(f"Python random.random(): {random.random()}")
    
    # Test NumPy random
    print(f"NumPy random.rand(): {np.random.rand()}")
    
    # Reset and verify
    set_seeds(42)
    print(f"Python random.random() (reset): {random.random()}")
    print(f"NumPy random.rand() (reset): {np.random.rand()}")
