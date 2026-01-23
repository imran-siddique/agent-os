# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-23

### Added

#### Layer 3: The Framework - Dependency Injection Architecture
- **KernelInterface**: Abstract interface for custom kernel implementations
  - `KernelInterface` - Base interface for all kernels (SCAK can now implement this)
  - `SelfCorrectingKernelInterface` - Extended interface for self-correcting kernels
  - `CapabilityRestrictedKernelInterface` - For Mute Agent pattern implementations
  - `KernelCapability` enum for declaring kernel capabilities
  - `KernelMetadata` dataclass for kernel information

- **Plugin Interfaces**: Extensible component architecture
  - `ValidatorInterface` - For custom request validators
  - `CapabilityValidatorInterface` - For capability-based validation (Mute Agent pattern)
  - `ExecutorInterface` - For custom action executors
  - `ContextRouterInterface` - For context routing plugins
  - `PolicyProviderInterface` - For custom policy sources
  - `SupervisorInterface` - For supervisor agent plugins
  - `PluginCapability` and `PluginMetadata` for plugin information

- **Protocol Interfaces**: Integration points for Layer 2 protocols
  - `MessageSecurityInterface` - For iatp (Inter-Agent Transport Protocol) integration
  - `VerificationInterface` - For cmvk (Cryptographic Message Verification Kit) integration
  - `ContextRoutingInterface` - For caas (Context-as-a-Service) integration

- **PluginRegistry**: Central dependency injection system
  - Singleton pattern for global plugin management
  - Runtime registration of kernels, validators, executors, routers
  - Forbidden dependency enforcement (scak, mute-agent cannot be hard-imported)
  - Plugin discovery and loading from paths
  - Health check and lifecycle management

### Changed

- **AgentControlPlane**: Now supports dependency injection
  - New `use_plugin_registry` parameter for plugin-based architecture
  - New `kernel` parameter for injecting custom KernelInterface implementations
  - New `validators` parameter for injecting ValidatorInterface implementations
  - New `context_router` parameter for caas integration
  - New `message_security` parameter for iatp integration
  - New `verifier` parameter for cmvk integration
  - New methods: `register_validator()`, `register_kernel()`, `register_context_router()`, etc.

- **MuteAgentValidator**: Refactored to implement CapabilityValidatorInterface
  - Now implements `CapabilityValidatorInterface` for plugin compatibility
  - Returns `ValidationResult` instead of tuple for new interface
  - Backward compatible with legacy usage
  - Added deprecation notice for direct imports

### Documentation

- Added `docs/LAYER3_FRAMEWORK.md` - Comprehensive architecture guide for Layer 3

### Dependency Policy

- **Allowed Dependencies**: iatp, cmvk, caas (optional protocol integrations)
- **Forbidden Dependencies**: scak, mute-agent (must implement interfaces instead)

## [1.1.0] - 2026-01-18

### Added

#### ML-Based Safety & Anomaly Detection
- **JailbreakDetector**: Pattern-based and embedding-based jailbreak detection with 60+ attack vectors
  - Supports ignore instructions, roleplay, system override, hypothetical scenarios, and encoding tricks
  - Behavioral analysis with context-aware threat scoring
  - Ensemble detection combining patterns, embeddings, and behavioral signals
- **AnomalyDetector**: Behavioral anomaly detection for agent actions
  - Baseline establishment through historical behavior
  - Novel action type detection
  - Statistical anomaly scoring

#### Compliance & Regulatory Frameworks
- **ComplianceEngine**: Multi-framework compliance checking
  - EU AI Act support with risk category assessment (unacceptable, high-risk, limited-risk, minimal-risk)
  - SOC 2 Trust Service Criteria validation
  - GDPR, HIPAA, PCI-DSS, ISO 27001 framework templates
  - Automated control validation and audit trail generation
  - Compliance reporting and dashboard
- **ConstitutionalAI**: Value alignment framework
  - Inspired by Anthropic's Constitutional AI research
  - Default principles: harmlessness, honesty, privacy, transparency, fairness
  - Self-critique capability for pre-response validation
  - Custom constitutional rule support
  - Automatic compliance scoring and violation detection

#### Multimodal Capabilities
- **VisionCapability**: Image analysis with governance
  - Support for JPEG, PNG, GIF, WebP formats
  - Safety checking and content moderation hooks
  - Integration-ready for GPT-4V, Claude Vision, etc.
- **AudioCapability**: Audio processing
  - Transcription support (MP3, WAV, OGG, FLAC)
  - Safety checking for audio content
  - Duration and file size limits
- **VectorStoreIntegration**: RAG support with multiple backends
  - In-memory, Pinecone, Weaviate, ChromaDB, Qdrant, Milvus support
  - Document storage with embeddings
  - Semantic search with metadata filtering
  - Hybrid search capabilities
- **RAGPipeline**: Complete Retrieval-Augmented Generation pipeline
  - Document retrieval and context assembly
  - Citation tracking
  - RAG-optimized prompt engineering

#### Production Observability
- **PrometheusExporter**: Metrics export for Prometheus scraping
  - Counter, gauge, histogram, and summary metrics
  - Multi-dimensional labels
  - Prometheus text format export
- **AlertManager**: Rule-based alerting system
  - Configurable alert rules with severity levels
  - Alert aggregation and deduplication
  - Alert history and resolution tracking
- **TraceCollector**: Distributed tracing
  - OpenTelemetry-compatible span collection
  - Parent-child span relationships
  - Trace visualization data generation
  - Performance analysis capabilities
- **ObservabilityDashboard**: Unified observability interface
  - Real-time metrics aggregation
  - Active alert monitoring
  - Trace visualization
  - System health status reporting

### Enhanced
- Extended `__init__.py` exports to include all new modules
- Updated README with v1.1 feature highlights
- Comprehensive test coverage: 196 tests (68 new tests added)

### Documentation
- New comprehensive guide: `docs/ADVANCED_FEATURES.md`
- Example scripts for all new features:
  - `examples/ml_safety_demo.py`: Jailbreak and anomaly detection examples
  - `examples/compliance_demo.py`: Compliance and Constitutional AI examples
  - `examples/multimodal_demo.py`: Vision, audio, and RAG examples
  - `examples/observability_demo.py`: Metrics, alerting, and tracing examples

### Research Foundations
All new features are grounded in peer-reviewed research:
- Universal and Transferable Adversarial Attacks (arXiv:2307.15043)
- Red-Teaming Large Language Models (arXiv:2308.10263)
- Multimodal Agents: A Survey (arXiv:2404.12390)
- Constitutional AI from Anthropic research
- EU AI Act (2024) regulatory framework
- Prometheus and OpenTelemetry observability standards

## [0.1.0] - 2025-01-11

### Added
- Initial release of Agent Control Plane
- Core agent kernel functionality
- Policy engine with rate limiting and quotas
- Execution engine with sandboxing
- Advanced features:
  - Mute Agent (capability-based execution)
  - Shadow Mode (simulation without execution)
  - Constraint Graphs (multi-dimensional context)
  - Supervisor Agents (recursive governance)
- Comprehensive test suite (31 tests)
- Example scripts:
  - Getting Started tutorial
  - Basic usage examples
  - Advanced features showcase
  - Real-world use cases
  - Configuration patterns
- Documentation:
  - Quick Start Guide
  - Implementation Guide
  - Philosophy document
  - Architecture overview
  - Contributing guidelines
- Project structure:
  - src/agent_control_plane/ package
  - tests/ directory
  - examples/ directory
  - docs/ directory
- CI/CD with GitHub Actions
- Package configuration (setup.py, pyproject.toml)
- MIT License

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)
