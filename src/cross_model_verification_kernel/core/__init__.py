"""
Core module for the Cross-Model Verification Kernel.
Contains the kernel logic, graph memory, and type definitions.
"""

from .graph_memory import GraphMemory
from .kernel import VerificationKernel
from .types import (
    GenerationResult,
    KernelState,
    Node,
    NodeStatus,
    VerificationOutcome,
    VerificationResult,
)

__all__ = [
    "VerificationKernel",
    "GraphMemory",
    "Node",
    "NodeStatus",
    "VerificationResult",
    "VerificationOutcome",
    "GenerationResult",
    "KernelState",
]
