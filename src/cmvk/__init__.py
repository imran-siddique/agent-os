"""
CMVK - Cross-Model Verification Kernel
======================================

A mathematical and adversarial verification library for calculating
drift/hallucination scores between outputs.

Layer 1: The Primitive
Publication Target: PyPI (pip install cmvk)

This library provides pure functions for verification:

- :func:`verify` - Compare two text outputs for semantic drift
- :func:`verify_embeddings` - Compare embedding vectors
- :func:`verify_distributions` - Compare probability distributions (KL divergence)
- :func:`verify_sequences` - Compare sequences with alignment

All functions are pure (no side effects) and use only numpy/scipy.

Example Usage
-------------

Basic text verification::

    import cmvk

    score = cmvk.verify(
        output_a="def add(a, b): return a + b",
        output_b="def add(x, y): return x + y"
    )
    print(f"Drift: {score.drift_score:.2f}")  # ~0.15 (low = similar)

Embedding comparison::

    import cmvk
    import numpy as np

    emb_a = np.random.randn(768)
    emb_b = emb_a + np.random.randn(768) * 0.1  # Small perturbation

    score = cmvk.verify_embeddings(emb_a, emb_b)
    print(f"Semantic drift: {score.drift_score:.2f}")

Batch verification::

    outputs_a = ["Solution 1", "Solution 2", "Solution 3"]
    outputs_b = ["Answer 1", "Answer 2", "Answer 3"]

    scores = cmvk.verify_batch(outputs_a, outputs_b)
    summary = cmvk.aggregate_scores(scores)
    print(f"Mean drift: {summary.drift_score:.2f}")

For Hugging Face Hub integration, see :mod:`cmvk.hf_utils`.
"""

from __future__ import annotations

from typing import Any

__version__ = "0.1.0"
__author__ = "Imran Siddique"
__email__ = "imran.siddique@example.com"
__license__ = "MIT"

from .types import DriftType, VerificationScore
from .verification import (
    aggregate_scores,
    verify,
    verify_batch,
    verify_distributions,
    verify_embeddings,
    verify_sequences,
)

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Types (exported for type annotations)
    "DriftType",
    "VerificationScore",
    # Core verification functions
    "verify",
    "verify_embeddings",
    "verify_distributions",
    "verify_sequences",
    # Batch operations
    "verify_batch",
    "aggregate_scores",
]


def __getattr__(name: str) -> Any:
    """Lazy loading for optional submodules."""
    if name == "hf_utils":
        from . import hf_utils

        return hf_utils
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
