# Changelog

All notable changes to the Self-Correcting Agent Kernel (SCAK) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-18

### Added
- Real LLM integrations (OpenAI GPT-4o, o1-preview, Anthropic Claude 3.5 Sonnet)
- Multi-agent orchestration framework with supervisor, analyst, and verifier roles
- Dynamic tool registry with multi-modal support (text, vision, audio, code)
- Advanced security and governance layer with ML-based threat detection
- Constitutional AI principles enforcement
- Red-team security benchmark (60+ adversarial prompts)
- Streamlit dashboard for real-time monitoring and visualization
- CLI tool (`scak`) for agent management and benchmarks
- Docker Compose setup for production deployment
- Comprehensive research citations throughout codebase
- Production features demo showcasing all capabilities

### Enhanced
- Shadow Teacher implementation with o1-preview reasoning traces
- Memory Controller with write-through protocol
- Telemetry system with structured JSON logging
- Test suite expanded to 183+ tests
- Documentation with detailed research foundations

### Fixed
- Async/await patterns for non-blocking I/O throughout
- Type safety with Pydantic v2 models
- Error handling with structured telemetry (no silent failures)

## [1.0.0] - 2026-01-15

### Added
- Dual-Loop Architecture (Runtime Safety + Alignment Engine)
- Completeness Auditor for laziness detection
- Shadow Teacher diagnostic agent
- Semantic Purge mechanism with Type A/B decay taxonomy
- Three-tier memory hierarchy (Kernel → Skill Cache → Archive)
- Triage Engine for sync/async routing
- Agent Patcher with rollback support
- SkillMapper for tool-lesson correlation
- Rubric system for lesson scoring
- Phase 3 Memory Lifecycle implementation

### Experiments
- GAIA Benchmark for laziness detection (70%+ correction rate)
- Amnesia Test for context efficiency (40-60% reduction)
- Chaos Engineering for robustness (<30s MTTR)
- Ablation studies (Semantic Purge, Differential Auditing)

### Documentation
- Comprehensive wiki with architectural deep dives
- Three Failure Types guide
- Adaptive Memory Hierarchy documentation
- Data Contracts and Schemas reference
- Contributing guidelines

## [0.1.0] - 2025-12-01

### Added
- Initial release of Self-Correcting Agent Kernel
- Basic failure detection and correction
- Simple prompt patching mechanism
- Memory hierarchy prototype (single-tier)
- Legacy API (`agent_kernel` module)
- Core data models with Pydantic
- Basic telemetry and logging
- Initial test suite (50+ tests)
- Example scripts and demos

### Core Components
- `SelfCorrectingAgentKernel` main class
- Basic triage for failure routing
- Simple patch application without simulation
- Redis cache integration
- Vector DB placeholder

### Documentation
- Initial README with architecture overview
- Basic installation instructions
- Quick-start examples
- License and contribution guidelines

---

## Version History Summary

- **v1.1.0** (2026-01-18): Production-ready with LLM integrations, multi-agent orchestration, security layer
- **v1.0.0** (2026-01-15): Complete dual-loop architecture, all experiments validated
- **v0.1.0** (2025-12-01): Initial prototype release

---

## Upgrade Guide

### From 1.0.0 to 1.1.0

**New Features:**
- LLM clients now async: `await client.generate()`
- Orchestrator for multi-agent workflows
- GovernanceLayer for security screening
- CLI tool: `scak --help`

**Breaking Changes:**
- None (backward compatible)

**Recommended Actions:**
1. Install optional dependencies: `pip install -e ".[llm]"`
2. Update async code patterns to use new LLM clients
3. Review security governance policies
4. Try new CLI commands

### From 0.1.0 to 1.0.0

**New Architecture:**
- Modern `src/` structure (recommended over legacy `agent_kernel/`)
- Dual-loop replaces single-loop correction
- Three-tier memory replaces single-tier cache

**Breaking Changes:**
- `src.kernel.triage.FixStrategy` enum values changed (SYNC_JIT, ASYNC_BATCH)
- Memory controller API redesigned
- Telemetry format changed to structured JSON

**Migration Path:**
1. Update imports: `from src.kernel.triage import FailureTriage`
2. Replace memory calls with new MemoryController API
3. Update telemetry to emit structured events
4. Run tests to validate changes

---

## Deprecation Notices

### Deprecated in 1.1.0
- None

### Deprecated in 1.0.0
- Legacy `agent_kernel/` API (still supported, but use `src/` for new code)
- Print-based logging (use structured telemetry instead)
- Synchronous LLM calls (use async/await patterns)

---

## Release Notes

### How to Cite

```bibtex
@software{scak2026,
  title={Self-Correcting Agent Kernel: Automated Alignment via Differential Auditing and Semantic Memory Hygiene},
  author={Self-Correcting Agent Team},
  year={2026},
  version={1.1.0},
  url={https://github.com/imran-siddique/self-correcting-agent-kernel}
}
```

### Links

- **PyPI:** https://pypi.org/project/scak/
- **GitHub:** https://github.com/imran-siddique/self-correcting-agent-kernel
- **Documentation:** https://github.com/imran-siddique/self-correcting-agent-kernel/wiki
- **Paper:** https://arxiv.org (to be published)

---

**Maintained by:** Self-Correcting Agent Team  
**License:** MIT
