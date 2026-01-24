"""
Cross-Model Verification Kernel (CMVK)
======================================

A research framework for adversarial multi-model verification.

Core Philosophy: "Trust, but Verify (with a different brain)."

This package implements the full verification kernel that orchestrates:
- A Generator (System 1) for code synthesis
- A Verifier (System 2) for adversarial testing
- An Arbiter for deterministic decision-making with strategy banning

Example Usage
-------------

Basic verification loop::

    from cross_model_verification_kernel import (
        VerificationKernel,
        OpenAIGenerator,
        GeminiVerifier,
    )

    kernel = VerificationKernel(
        generator=OpenAIGenerator(model="gpt-4o"),
        verifier=GeminiVerifier(model="gemini-1.5-pro"),
        seed=42,  # For reproducibility
    )

    result = kernel.execute("Write a function to compute Fibonacci numbers")
    print(f"Status: {result.final_result}")

For the lightweight verification primitives, see the `cmvk` package::

    import cmvk
    score = cmvk.verify(output_a, output_b)

See Also
--------
- cmvk : Lightweight verification primitives (pip install cmvk)
- docs/architecture.md : System architecture documentation
- paper/cmvk_neurips.tex : Research paper draft
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Imran Siddique"
__email__ = "imran.siddique@example.com"
__license__ = "MIT"

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

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Core Kernel
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
