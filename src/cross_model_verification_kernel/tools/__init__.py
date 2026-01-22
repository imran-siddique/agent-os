"""
Tools module for the Cross-Model Verification Kernel.
Contains utilities for code execution, web search, statistics, and HuggingFace integration.
"""

from .sandbox import SandboxExecutor
from .web_search import WebSearchTool

# Optional imports (may not have all dependencies)
try:
    from .statistics import (
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
except ImportError:
    pass

try:
    from .huggingface_upload import (
        check_huggingface_auth,
        upload_all,
        upload_dataset,
        upload_experiment_results,
        upload_traces,
    )
except ImportError:
    pass

__all__ = [
    "SandboxExecutor",
    "WebSearchTool",
]
