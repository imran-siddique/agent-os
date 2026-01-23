"""
emk - Episodic Memory Kernel

An immutable, append-only ledger of agent experiences.
"""

__version__ = "0.1.0"

from emk.schema import Episode
from emk.store import VectorStoreAdapter, FileAdapter
from emk.indexer import Indexer

__all__ = ["Episode", "VectorStoreAdapter", "FileAdapter", "Indexer"]

# Only import ChromaDBAdapter if chromadb is installed
try:
    from emk.store import ChromaDBAdapter
    __all__.append("ChromaDBAdapter")
except ImportError:
    pass
