# Changelog

All notable changes to the Inter-Agent Trust Protocol (IATP) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-23

### Added
- **Go Sidecar**: Production-ready high-performance sidecar implementation in Go
  - 10k+ concurrent connection support
  - Zero-copy proxying for efficient data transfer
  - Single static binary with no runtime dependencies
  - ~10MB memory footprint
  - Dockerfile and comprehensive documentation
- **Cascading Hallucination Experiment**: Complete experimental setup to demonstrate IATP's prevention of cascading failures
  - Agent A (User), Agent B (Summarizer with poisoning), Agent C (Database)
  - Control group (no IATP) and test group (with IATP) implementations
  - Automated experiment runner with result visualization
  - Documentation for reproducing the "money slide" results
- **Docker Compose Deployment**: One-line deployment configuration
  - Complete docker-compose.yml with secure bank agent and honeypot
  - Dockerfiles for agents and Python sidecar
  - Network configuration for sidecar pattern
  - Comprehensive deployment documentation
- **PyPI Distribution Preparation**: Package ready for distribution
  - MANIFEST.in for proper file inclusion
  - Updated setup.py with proper metadata
  - CHANGELOG.md for version tracking
  - Blog post draft for community launch

### Changed
- Enhanced README with Docker deployment instructions
- Improved documentation structure across all components
- Updated examples to work with Docker deployment

### Documentation
- Added Go sidecar README with performance benchmarks
- Added experiment README with detailed instructions
- Added Docker deployment guide
- Added blog post draft for community launch

## [0.1.0] - 2026-01-15

### Added
- Initial release of IATP protocol and Python SDK
- Capability manifest schema and protocol specification
- Trust score calculation algorithm (0-10 scale)
- Security validation with credit card (Luhn) and SSN detection
- Privacy policy enforcement (block/warn/allow)
- Flight recorder for distributed tracing
- User override mechanism for risky operations
- Python sidecar implementation with FastAPI
- Integration with agent-control-plane (policy engine)
- Integration with scak (recovery engine)
- Comprehensive test suite (32 tests)
- Example agents: secure bank, untrusted/honeypot, generic backend
- Complete documentation and implementation guide

### Features
- **Trust Levels**: verified_partner, trusted, standard, unknown, untrusted
- **Reversibility**: full, partial, none
- **Retention Policies**: ephemeral, temporary, permanent
- **Policy Enforcement**:
  - Trust score >= 7: Allow immediately
  - Trust score 3-6: Warn (requires override)
  - Trust score < 3: Warn (requires override)
  - Credit card + permanent retention: Block (403)
  - SSN + non-ephemeral retention: Block (403)
- **Flight Recorder**: JSONL logging with request/response/error/blocked events
- **Distributed Tracing**: Unique trace IDs for all requests
- **Sensitive Data Scrubbing**: Automatic redaction in logs

[0.2.0]: https://github.com/imran-siddique/inter-agent-trust-protocol/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/imran-siddique/inter-agent-trust-protocol/releases/tag/v0.1.0
