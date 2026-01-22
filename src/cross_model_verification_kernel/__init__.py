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
from .core.kernel import set_reproducibility_seed
from .agents import (
    BaseAgent,
    OpenAIGenerator,
    GeminiVerifier,
    AnthropicVerifier,
)
from .tools import (
    SandboxExecutor,
    WebSearchTool,
)

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
