# Changelog

All notable changes to the Cross-Model Verification Kernel (CMVK) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Anthropic Claude verifier support (`AnthropicVerifier`)
- CLI interface with `cmvk` command
  - `cmvk run` - Run verification on a task
  - `cmvk config` - Manage configuration
  - `cmvk benchmark` - Run benchmark experiments
  - `cmvk visualize` - Visualize trace files
  - `cmvk models` - List available models
- Reproducibility controls with seed configuration
- `pyproject.toml` for modern Python packaging
- GitHub Actions CI/CD pipeline
- Docker multi-stage build with production/sandbox/development targets
- Per-agent temperature controls
- Benchmark results table in README
- HuggingFace Hub integration (`src/tools/huggingface_upload.py`)
  - Upload datasets, traces, and results
  - Auto-generate dataset cards
- Statistical analysis utilities (`src/tools/statistics.py`)
  - Welch's t-test, Wilcoxon signed-rank test
  - Confidence intervals, bootstrap CI
  - Effect size (Cohen's d)
  - Results table formatting
- Reproducible experiment runner (`experiments/reproducible_runner.py`)
  - Hardware/runtime stats collection
  - Deterministic execution with seeds
  - Complete experiment logging
- Safety and ethics documentation (`SAFETY.md`)
  - Sandbox security guidelines
  - Prompt injection defenses
  - Dual-use considerations
  - Responsible disclosure policy
- Comprehensive test suite for new components
  - `test_anthropic_verifier.py` - Anthropic adapter tests
  - `test_cli.py` - CLI tests
  - `test_reproducibility.py` - Seed/reproducibility tests
- Pre-commit configuration (`.pre-commit-config.yaml`)

### Changed
- Pinned all dependency versions in `requirements.txt`
- Updated README with installation via pip, CLI usage, and Docker instructions
- Improved configuration handling with seed support
- Dockerfile now uses multi-stage build with separate targets

### Fixed
- N/A

## [1.0.0] - 2024-01-21

### Added
- Initial release of Cross-Model Verification Kernel
- OpenAI Generator agent (GPT-4o, GPT-4 Turbo, o1 models)
- Gemini Verifier agent (Gemini 1.5 Pro/Flash)
- Graph of Truth state machine for loop prevention
- Prosecutor Mode for hostile test generation
- Trace logging and visualization system
- HumanEval dataset integration
- Lateral thinking via strategy banning
- Sandbox code execution
- Configuration via YAML files
- Basic test suite
- Research paper draft (PAPER.md)

### Security
- Basic sandbox isolation for code execution
- API key handling via environment variables

---

## Version History

- **1.0.0**: Initial research release with OpenAI + Gemini support
- **1.1.0** (upcoming): Anthropic support, CLI, improved reproducibility
