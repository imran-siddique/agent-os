"""
Datasets Module for the Cross-Model Verification Kernel.

This module provides utilities for loading and processing benchmark datasets
used for evaluating the adversarial verification system.

Available Loaders:
    - HumanEvalLoader: Load and process the HumanEval code generation benchmark

Example:
    >>> from cross_model_verification_kernel.datasets import HumanEvalLoader
    >>> loader = HumanEvalLoader()
    >>> problems = loader.get_all_problems()
"""

from .humaneval_loader import HumanEvalLoader

__all__ = [
    "HumanEvalLoader",
]
