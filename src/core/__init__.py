"""
Core module for the Cross-Model Verification Kernel.
Contains the kernel logic, graph memory, and type definitions.
"""
from .kernel import VerificationKernel
from .graph_memory import GraphMemory
from .types import (
    Node, NodeStatus, VerificationResult, VerificationOutcome,
    GenerationResult, KernelState
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
