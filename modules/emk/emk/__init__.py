"""
emk - Episodic Memory Kernel.

An immutable, append-only ledger of agent experiences for AI systems.

This package provides a Layer 1 primitive for storing agent experiences
as structured episodes following the pattern: Goal → Action → Result → Reflection.

Example:
    >>> from emk import Episode, FileAdapter
    >>> store = FileAdapter("memories.jsonl")
    >>> episode = Episode(
    ...     goal="Retrieve user data",
    ...     action="Query database",
    ...     result="Success",
    ...     reflection="Efficient query"
    ... )
    >>> episode_id = store.store(episode)

Attributes:
    __version__: Package version string.
    __author__: Package author.
    __license__: Package license.

See Also:
    - GitHub: https://github.com/imran-siddique/emk
    - Documentation: https://github.com/imran-siddique/emk#readme
"""

from typing import TYPE_CHECKING, List

__version__ = "0.2.0"
__author__ = "Imran Siddique"
__license__ = "MIT"

# Core exports - always available
from emk.schema import Episode, SemanticRule
from emk.store import VectorStoreAdapter, FileAdapter
from emk.indexer import Indexer
from emk.sleep_cycle import MemoryCompressor

# Define explicit public API
__all__: List[str] = [
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    # Core classes
    "Episode",
    "SemanticRule",
    "VectorStoreAdapter", 
    "FileAdapter",
    "Indexer",
    "MemoryCompressor",
]

# Optional ChromaDB adapter - only import if chromadb is installed
try:
    from emk.store import ChromaDBAdapter
    __all__.append("ChromaDBAdapter")
except ImportError:
    # ChromaDB not installed, ChromaDBAdapter will not be available
    if TYPE_CHECKING:
        from emk.store import ChromaDBAdapter  # noqa: F401

# Optional Hugging Face utilities - only import if huggingface_hub is installed
try:
    from emk.hf_utils import (
        upload_episodes_to_hub,
        download_episodes_from_hub,
        push_experiment_results,
    )
    __all__.extend([
        "upload_episodes_to_hub",
        "download_episodes_from_hub", 
        "push_experiment_results",
    ])
except ImportError:
    # huggingface_hub not installed
    pass


def get_version_info() -> dict:
    """
    Get detailed version information about the emk package.
    
    Returns:
        dict: A dictionary containing version, author, license, and
            available optional features.
    
    Example:
        >>> import emk
        >>> info = emk.get_version_info()
        >>> print(info['version'])
        '0.1.0'
    """
    features = {
        "chromadb": "ChromaDBAdapter" in __all__,
        "huggingface": "upload_episodes_to_hub" in __all__,
    }
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "features": features,
    }
