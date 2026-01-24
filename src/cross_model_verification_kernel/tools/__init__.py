"""
Tools Module for the Cross-Model Verification Kernel.

This module provides utilities for code execution, web search, statistical
analysis, HuggingFace integration, and result visualization.

Core Tools (always available):
    - SandboxExecutor: Safe execution of generated code in isolated environments
    - WebSearchTool: Web search capabilities for research grounding

Optional Tools (require additional dependencies):
    - StatisticalResult: Result container for statistical analysis
    - bootstrap_ci, confidence_interval: Statistical inference utilities
    - upload_dataset, upload_traces: HuggingFace Hub integration

Example:
    >>> from cross_model_verification_kernel.tools import SandboxExecutor
    >>> executor = SandboxExecutor()
    >>> result = executor.execute("print('Hello, World!')")
"""

from __future__ import annotations

from .sandbox import SandboxExecutor
from .web_search import WebSearchTool

# Optional imports for statistical analysis (may require scipy)
_statistics_available = False
try:
    from .statistics import (  # noqa: F401
        StatisticalResult,
        bootstrap_ci,
        compare_methods,
        confidence_interval,
        mean,
        standard_error,
        std,
        variance,
        welch_t_test,
        wilcoxon_signed_rank,
    )

    _statistics_available = True
except ImportError:
    pass

# Optional imports for HuggingFace integration (requires huggingface_hub)
_huggingface_available = False
try:
    from .huggingface_upload import (  # noqa: F401
        check_huggingface_auth,
        upload_all,
        upload_dataset,
        upload_experiment_results,
        upload_traces,
    )

    _huggingface_available = True
except ImportError:
    pass

# Build dynamic __all__ based on available imports
__all__ = [
    # Core tools (always available)
    "SandboxExecutor",
    "WebSearchTool",
]

if _statistics_available:
    __all__.extend(
        [
            "StatisticalResult",
            "bootstrap_ci",
            "compare_methods",
            "confidence_interval",
            "mean",
            "standard_error",
            "std",
            "variance",
            "welch_t_test",
            "wilcoxon_signed_rank",
        ]
    )

if _huggingface_available:
    __all__.extend(
        [
            "check_huggingface_auth",
            "upload_all",
            "upload_dataset",
            "upload_experiment_results",
            "upload_traces",
        ]
    )
