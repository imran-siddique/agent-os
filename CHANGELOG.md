# Changelog

All notable changes to the Cross-Model Verification Kernel (CMVK) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-21

### Changed
- **BREAKING**: Renamed package from `src` to `cross_model_verification_kernel`
  - All imports must now use `from cross_model_verification_kernel import ...`
  - CLI entry point updated to `cross_model_verification_kernel.cli:app`
- Reorganized documentation into `docs/` directory
  - `ARCHITECTURE.md` → `docs/architecture.md`
  - `SAFETY.md` → `docs/safety.md`
  - `NEW_FEATURES.md` → `docs/features.md`
  - `INNOVATION_LAYER.md` → `docs/innovation_layer.md`
  - `FEATURE_3_TRACEABILITY.md` → `docs/traceability.md`
- Reorganized tests into `tests/unit/` and `tests/integration/`
- Moved example scripts to `examples/` directory
- Moved paper-related files to `paper/` directory
- Updated `.pre-commit-config.yaml` to v5.0.0 hooks
- Modernized `.gitignore` with comprehensive patterns

### Added
- `src/cross_model_verification_kernel/__main__.py` for `python -m` support
- `CONTRIBUTING.md` with development guidelines
- `requirements-dev.txt` for contributors
- `tests/conftest.py` with shared pytest fixtures
- Merged `docs/getting_started.md` (combined GETTING_STARTED + QUICKSTART)
- Professional README.md with badges, benchmarks, and quick start guide

### Removed
- Redundant files: `IMPLEMENTATION_COMPLETE.md`, `IMPLEMENTATION_SUMMARY.md`,
  `PROJECT_COMPLETE.md`, `NEXT_STEPS.md`, `LAUNCH_CHECKLIST.md`, `hf_readme.md`
- Old `sys.path` hacks in example files (now uses proper package imports)

## [Unreleased]

### Added
- **LaTeX paper** (`paper/cmvk_neurips.tex`)
  - NeurIPS 2025 format with full methodology
  - BibTeX references (`paper/references.bib`)
  - Publication-ready tables and algorithm
- **SVG figures** for paper/presentations
  - Architecture diagram (`paper/figures/architecture.svg`)
  - Results bar chart with error bars (`paper/figures/results_bar.svg`)
  - Ablation study chart (`paper/figures/ablation.svg`)
  - Figure generation script (`paper/generate_figures.py`)
- **LICENSE** file (MIT)
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
- Benchmark results table in README (with actual numbers, means±std, p-values)
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
- Architecture diagrams (`docs/DIAGRAMS.md`)
  - Mermaid diagrams for architecture, verification loop, state machine
  - ASCII art diagrams for terminals
  - Export instructions for draw.io and LaTeX
  - Color scheme reference
- arXiv submission checklist (`ARXIV_CHECKLIST.md`)
  - NeurIPS/ICLR/ICML requirements
  - LLM usage disclosure templates
  - Reproducibility checklist
  - Anonymization guidelines
- Ablation experiment runner (`experiments/ablation_runner.py`)
  - Predefined configurations for baselines, cross-model, loop depth
  - Statistical aggregation across runs
  - LaTeX table generation
- Results visualization (`experiments/visualize_results.py`)
  - ASCII bar charts and tables
  - SVG chart generation (no dependencies)
  - LaTeX table export
- Enhanced PAPER.md
  - Formal problem definition with mathematical notation
  - Blind spot reduction theorem
  - Computational complexity analysis
  - Expanded related work with positioning table
  - Complete reference list (14 citations)

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
