"""
Tools module for the Cross-Model Verification Kernel.
Contains utilities for code execution, web search, statistics, and HuggingFace integration.
"""
from .sandbox import SandboxExecutor
from .web_search import WebSearchTool

# Optional imports (may not have all dependencies)
try:
    from .statistics import (
        mean, std, variance, standard_error,
        confidence_interval, welch_t_test, wilcoxon_signed_rank,
        bootstrap_ci, compare_methods, StatisticalResult
    )
except ImportError:
    pass

try:
    from .huggingface_upload import (
        upload_dataset, upload_traces, upload_experiment_results,
        upload_all, check_huggingface_auth
    )
except ImportError:
    pass

__all__ = [
    "SandboxExecutor",
    "WebSearchTool",
]
