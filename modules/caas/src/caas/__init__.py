"""
CaaS Core: Layer 1 Primitive for Context Management.

A pure, logic-only library for routing context, handling RAG fallacies,
and managing context windows. This library does not know what an "agent" is;
it only knows about text and vectors.

Publication Target: PyPI (pip install caas-core)

Design Philosophy:
    - Stateless: Context routing logic is stateless and processes only the data passed to it
    - No Agent Dependencies: No imports of Agent, Supervisor, or agent frameworks
    - Pure Functions: Methods accept generic strings (identifiers) or dicts (metadata)
    - Decoupled: Does not query active agent runtimes

Forbidden Dependencies:
    - agent-control-plane
    - iatp
    - scak

Allowed Dependencies:
    - numpy / pandas (for data handling)
    - openai / langchain (optional, only for embeddings if needed)

Example:
    Basic usage of the CaaS framework::

        from caas import (
            ContextTriadManager,
            HeuristicRouter,
            PragmaticTruthManager,
            DocumentProcessor,
        )

        # Route a query to the appropriate model tier
        router = HeuristicRouter()
        decision = router.route("Summarize this document")
        print(decision.model_tier)  # ModelTier.SMART

        # Manage context tiers (Hot/Warm/Cold)
        triad = ContextTriadManager()
        triad.add_hot_context("Current error: ConnectionTimeout")
        triad.add_warm_context("User prefers verbose explanations")

Note:
    This package follows semantic versioning. Breaking changes will only
    occur in major version increments.
"""

from typing import TYPE_CHECKING

__version__ = "0.3.0"
__author__ = "Imran Siddique"
__email__ = "imran.siddique@microsoft.com"
__license__ = "MIT"

# Core data models - always available
from caas.models import (
    # Enums
    ContentTier,
    ContextLayer,
    DocumentType,
    ContentFormat,
    SourceType,
    ModelTier,
    FileType,
    # Data classes
    Section,
    Document,
    SourceCitation,
    ContextRequest,
    ContextResponse,
    RoutingDecision,
    ContextTriadItem,
    ContextTriadState,
    FileNode,
    FileEdit,
    VFSState,
    FileResponse,
    FileListResponse,
)

# Context Triad - Hot/Warm/Cold context management
from caas.triad import ContextTriadManager

# Pragmatic Truth - Official vs. Practical knowledge tracking
from caas.pragmatic_truth import SourceDetector, ConflictDetector, CitationFormatter

# Decay functions for time-based retrieval
from caas.decay import calculate_decay_factor, apply_decay_to_score, get_time_weighted_score

# Conversation management
from caas.conversation import ConversationManager

# Heuristic Router - Zero-latency query routing
from caas.routing import HeuristicRouter

# Document Detection
from caas.detection import DocumentTypeDetector, StructureAnalyzer

# Ingestion & Processing
from caas.ingestion import (
    BaseProcessor,
    PDFProcessor,
    HTMLProcessor,
    CodeProcessor,
    ProcessorFactory,
    StructureParser,
)

# Storage & Extraction
from caas.storage import DocumentStore, ContextExtractor

# Tuning
from caas.tuning import WeightTuner, CorpusAnalyzer

# Trust Gateway - Enterprise deployment
from caas.gateway import (
    TrustGateway,
    DeploymentMode,
    SecurityPolicy,
    SecurityLevel,
)

# Metadata enrichment
from caas.enrichment import MetadataEnricher

# Virtual File System - Project state management for SDLC agents
from caas.vfs import VirtualFileSystem

# Context Caching - Cost optimization for LLM APIs (CAAS-008)
from caas.caching import (
    ContextCache,
    CacheConfig,
    CacheStrategy,
    AnthropicCacheStrategy,
    OpenAICacheStrategy,
    LocalCacheStrategy,
    CacheProvider,
    CacheType,
    CacheResult,
    CacheStats,
    create_cache,
)

# Public API - explicit exports for `from caas import *`
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Enums
    "ContentTier",
    "ContextLayer",
    "DocumentType",
    "ContentFormat",
    "SourceType",
    "ModelTier",
    "FileType",
    # Data Models
    "Section",
    "Document",
    "SourceCitation",
    "ContextRequest",
    "ContextResponse",
    "RoutingDecision",
    "ContextTriadItem",
    "ContextTriadState",
    "FileNode",
    "FileEdit",
    "VFSState",
    "FileResponse",
    "FileListResponse",
    # Core Managers
    "ContextTriadManager",
    "SourceDetector",
    "ConflictDetector",
    "CitationFormatter",
    "calculate_decay_factor",
    "apply_decay_to_score",
    "get_time_weighted_score",
    "ConversationManager",
    # Routing
    "HeuristicRouter",
    # Detection
    "DocumentTypeDetector",
    "StructureAnalyzer",
    # Ingestion
    "BaseProcessor",
    "PDFProcessor",
    "HTMLProcessor",
    "CodeProcessor",
    "ProcessorFactory",
    "StructureParser",
    # Storage
    "DocumentStore",
    "ContextExtractor",
    # Tuning
    "WeightTuner",
    "CorpusAnalyzer",
    # Enterprise
    "TrustGateway",
    "DeploymentMode",
    "SecurityPolicy",
    "SecurityLevel",
    # Enrichment
    "MetadataEnricher",
    # Virtual File System
    "VirtualFileSystem",
    # Context Caching
    "ContextCache",
    "CacheConfig",
    "CacheStrategy",
    "AnthropicCacheStrategy",
    "OpenAICacheStrategy",
    "LocalCacheStrategy",
    "CacheProvider",
    "CacheType",
    "CacheResult",
    "CacheStats",
    "create_cache",
]


def get_version() -> str:
    """Return the current version of CaaS.

    Returns:
        str: The semantic version string (e.g., "0.2.0").
    """
    return __version__
