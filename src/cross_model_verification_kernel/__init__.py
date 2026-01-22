"""
Cross-Model Verification Kernel (CMVK)

A research framework for adversarial multi-model verification.
Core Philosophy: "Trust, but Verify (with a different brain)."
"""

from .agents import AnthropicVerifier, BaseAgent, GeminiVerifier, OpenAIGenerator
from .core import (
    GenerationResult,
    GraphMemory,
    KernelState,
    Node,
    NodeStatus,
    VerificationKernel,
    VerificationOutcome,
    VerificationResult,
)
from .core.kernel import set_reproducibility_seed
from .tools import SandboxExecutor, WebSearchTool

__version__ = "1.0.0"

__all__ = [
    # Core
    "VerificationKernel",
    "GraphMemory",
    "Node",
    "NodeStatus",
    "VerificationResult",
    "VerificationOutcome",
    "GenerationResult",
    "KernelState",
    "set_reproducibility_seed",
    # Agents
    "BaseAgent",
    "OpenAIGenerator",
    "GeminiVerifier",
    "AnthropicVerifier",
    # Tools
    "SandboxExecutor",
    "WebSearchTool",
]
