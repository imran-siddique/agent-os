"""
Cross-Model Verification Kernel (CMVK)

A research framework for adversarial multi-model verification.
Core Philosophy: "Trust, but Verify (with a different brain)."
"""
from .core import (
    VerificationKernel,
    GraphMemory,
    Node,
    NodeStatus,
    VerificationResult,
    VerificationOutcome,
    GenerationResult,
    KernelState,
)
from .agents import (
    BaseAgent,
    OpenAIGenerator,
    GeminiVerifier,
)
from .tools import (
    SandboxExecutor,
    WebSearchTool,
)

__version__ = "1.0.0"

__all__ = [
    "VerificationKernel",
    "GraphMemory",
    "Node",
    "NodeStatus",
    "VerificationResult",
    "VerificationOutcome",
    "GenerationResult",
    "KernelState",
    "BaseAgent",
    "OpenAIGenerator",
    "GeminiVerifier",
    "SandboxExecutor",
    "WebSearchTool",
]
