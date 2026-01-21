"""
Cross-Model Verification Kernel

An adversarial architecture for code generation and verification using model diversity.
"""

__version__ = "0.1.0"

from .generator import Generator, GeneratorConfig
from .verifier import Verifier, VerifierConfig
from .kernel import VerificationKernel
from .models import ModelProvider

__all__ = [
    "Generator",
    "GeneratorConfig",
    "Verifier",
    "VerifierConfig",
    "VerificationKernel",
    "ModelProvider",
]
