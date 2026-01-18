# Reproducibility Guide

This document provides complete instructions for reproducing all experiments, benchmarks, and results reported in the Agent Control Plane research.

## Overview

All experiments in Agent Control Plane are designed to be:
- **Deterministic**: No random elements (no API calls, no non-deterministic LLM behavior)
- **Local**: Runs entirely on local machine (no external dependencies)
- **Fast**: Complete benchmark suite runs in <5 seconds
- **Verifiable**: All results can be independently verified

---

## Environment Specifications

### Hardware Requirements

**Minimum**:
- CPU: Any modern x86_64 processor (2+ cores)
- RAM: 1 GB (for basic tests)
- Disk: 100 MB (for source code + dependencies)

**Recommended**:
- CPU: 4+ cores (for parallel test execution)
- RAM: 4 GB
- Disk: 500 MB (for logs and artifacts)

**Note**: No GPU required. All experiments run on CPU.

### Software Requirements

**Operating System**:
- Linux (tested on Ubuntu 20.04, 22.04, 24.04)
- macOS (tested on macOS 13 Ventura, macOS 14 Sonoma)
- Windows (tested on Windows 10, Windows 11)

**Python**:
- Version: **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11, 3.12)
- Standard library only (no external dependencies for core functionality)

**Optional Dependencies** (for development):
- pytest >= 7.0.0 (for running test suite)
- black >= 23.0.0 (for code formatting)
- flake8 >= 6.0.0 (for linting)

### Exact Package Versions (Tested)

```
# Core (no dependencies)
agent-control-plane==1.1.0

# Development (optional)
pytest==7.4.3
pytest-cov==4.1.0
black==23.12.1
flake8==6.1.0
mypy==1.7.1
```

---

## Installation Instructions

### Option 1: From PyPI (Recommended)

```bash
# Install the latest stable version
pip install agent-control-plane==1.1.0

# Verify installation
python -c "import agent_control_plane; print(agent_control_plane.__version__)"
# Expected output: 1.1.0
```

### Option 2: From Source

```bash
# Clone the repository
git clone https://github.com/imran-siddique/agent-control-plane.git
cd agent-control-plane

# Checkout the specific version tag
git checkout v1.1.0

# Install in editable mode
pip install -e .

# Verify installation
python -c "import agent_control_plane; print(agent_control_plane.__version__)"
# Expected output: 1.1.0
```

### Option 3: Docker (Isolated Environment)

```bash
# Pull the official image
docker pull imransiddique/agent-control-plane:1.1.0

# Run in container
docker run -it imransiddique/agent-control-plane:1.1.0 bash

# Inside container, verify installation
python -c "import agent_control_plane; print(agent_control_plane.__version__)"
# Expected output: 1.1.0
```

---

## Reproducing Benchmark Results

### Main Benchmark: Comparative Safety Study

**Description**: Compares Agent Control Plane (deterministic enforcement) vs Baseline (prompt-based safety) using 60 red team prompts.

**Location**: `benchmark.py` and `benchmark/red_team_dataset.py`

**Expected Runtime**: 2-3 seconds

**Command**:
```bash
cd agent-control-plane
python benchmark.py
```

**Expected Output**:
```
======================================================================
RED TEAM DATASET STATISTICS
======================================================================
Total prompts: 60
  - Direct Violations: 15
  - Prompt Injections: 15
  - Contextual Confusion: 15
  - Valid Requests: 15

Expected to be blocked: 45
Expected to be allowed: 15

======================================================================
RESULTS: COMPARATIVE METRICS
======================================================================

Metric                                   Baseline        Control Plane  
----------------------------------------------------------------------
Safety Violation Rate (SVR)               26.67%            0.00%
  - Violations (should block, didn't)        12               0
False Positive Rate                        0.00%            0.00%
  - False positives (should allow, didn't)      0               0

Avg Output Tokens per Request              26.1             0.5
  → Token Reduction                                        98.1%

Avg Latency (ms)                           0.02            0.02

======================================================================
KEY FINDINGS
======================================================================

✓ Control Plane achieved 26.7% better safety (lower SVR)
✓ Control Plane used 98.1% fewer tokens (Scale by Subtraction)
✓ Control Plane achieved ZERO safety violations (100% enforcement)
```

**Verification**:
1. Check `benchmark_results.csv` for detailed per-prompt results
2. Check `benchmark_summary.csv` for aggregate metrics
3. Verify SHA256 checksums:
   - `benchmark_results.csv`: [will be provided in published release]
   - `benchmark_summary.csv`: [will be provided in published release]

**Determinism**: Results are 100% deterministic (no randomness). Running the benchmark multiple times should produce identical results.

**Seed Control**: Not applicable (no random elements).

---

## Reproducing Test Suite Results

### Full Test Suite

**Description**: 31 tests covering all core and advanced features.

**Location**: `tests/` directory

**Expected Runtime**: 5-10 seconds

**Command**:
```bash
# Run all tests
python -m unittest discover -s tests -p 'test_*.py' -v

# Expected output:
# test_create_agent_session (tests.test_control_plane.TestAgentKernel) ... ok
# test_execute_action_with_permission (tests.test_control_plane.TestAgentKernel) ... ok
# ... (31 tests total)
# ----------------------------------------------------------------------
# Ran 31 tests in 0.123s
#
# OK
```

**Individual Test Modules**:

1. **Core Features** (`tests/test_control_plane.py`):
   ```bash
   python -m unittest tests.test_control_plane -v
   # Expected: 12 tests, all pass
   ```

2. **Advanced Features** (`tests/test_advanced_features.py`):
   ```bash
   python -m unittest tests.test_advanced_features -v
   # Expected: 8 tests, all pass
   ```

3. **Adapters** (`tests/test_adapter.py`, `tests/test_langchain_adapter.py`, etc.):
   ```bash
   python -m unittest tests.test_adapter -v
   # Expected: 5 tests, all pass
   ```

4. **ML Safety** (`tests/test_ml_safety.py`):
   ```bash
   python -m unittest tests.test_ml_safety -v
   # Expected: 6 tests, all pass
   ```

**Coverage**:
```bash
# Install coverage tool
pip install pytest-cov

# Run with coverage report
pytest --cov=agent_control_plane --cov-report=html tests/

# Expected coverage: >85% (all core modules)
```

---

## Reproducing Example Scripts

All example scripts in `examples/` are deterministic and can be run independently.

### Basic Usage

```bash
python examples/basic_usage.py
# Expected: Demonstrates agent creation, permission checks, action execution
# Runtime: <1 second
```

### Advanced Features

```bash
python examples/advanced_features.py
# Expected: Demonstrates Shadow Mode, Mute Agent, Constraint Graphs, Supervisors
# Runtime: <2 seconds
```

### Benchmark Demo

```bash
python examples/benchmark_demo.py
# Expected: Runs mini-benchmark with 10 prompts
# Runtime: <1 second
```

---

## Exact Configuration Files

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
```

### pyproject.toml (relevant sections)

```toml
[project]
name = "agent-control-plane"
version = "1.1.0"
requires-python = ">=3.8"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers"

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
```

---

## Environment Variables

**None required**. All experiments run without environment variables.

**Optional** (for debugging):
```bash
export ACP_DEBUG=1           # Enable debug logging
export ACP_LOG_FILE=acp.log  # Write logs to file
```

---

## Troubleshooting Common Issues

### Issue 1: Import Error

**Symptom**:
```
ImportError: No module named 'agent_control_plane'
```

**Solution**:
```bash
# Ensure package is installed
pip install -e .

# Or install from PyPI
pip install agent-control-plane==1.1.0
```

### Issue 2: Test Failures

**Symptom**:
```
FAILED tests/test_control_plane.py::TestAgentKernel::test_create_agent_session
```

**Solution**:
```bash
# Ensure you're in the correct directory
cd agent-control-plane

# Ensure Python version is 3.8+
python --version

# Run single test for debugging
python -m unittest tests.test_control_plane.TestAgentKernel.test_create_agent_session -v
```

### Issue 3: Benchmark Not Found

**Symptom**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'benchmark.py'
```

**Solution**:
```bash
# Ensure you're in the repository root
cd agent-control-plane

# Verify file exists
ls -la benchmark.py
```

---

## Docker Reproducibility

### Build from Dockerfile

```bash
# Clone repository
git clone https://github.com/imran-siddique/agent-control-plane.git
cd agent-control-plane

# Build Docker image
docker build -t agent-control-plane:1.1.0 .

# Run benchmark in container
docker run agent-control-plane:1.1.0 python benchmark.py

# Run tests in container
docker run agent-control-plane:1.1.0 python -m unittest discover -s tests -p 'test_*.py' -v
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Run benchmark
docker-compose exec acp python benchmark.py

# Run tests
docker-compose exec acp python -m unittest discover -s tests -p 'test_*.py' -v

# View logs
docker-compose logs -f acp
```

---

## Continuous Integration

### GitHub Actions

All tests run automatically on:
- **Push** to main branch
- **Pull request** to main branch
- **Release** publication

**Workflow**: `.github/workflows/tests.yml`

**Platforms**:
- Ubuntu 20.04, 22.04
- macOS 13, 14
- Windows 10, 11

**Python Versions**:
- 3.8, 3.9, 3.10, 3.11, 3.12

**View Results**: https://github.com/imran-siddique/agent-control-plane/actions

---

## Dataset Checksums

### Benchmark Dataset

**File**: `benchmark/red_team_dataset.py`

**SHA256**: `[will be computed and added in published release]`

**Verification**:
```bash
sha256sum benchmark/red_team_dataset.py
```

### Expected Results

**File**: `benchmark/expected_results.json`

**SHA256**: `[will be computed and added in published release]`

**Verification**:
```bash
sha256sum benchmark/expected_results.json
```

---

## Seed Control (Not Applicable)

**Agent Control Plane experiments are 100% deterministic and do not use randomness.**

- No random seeds
- No stochastic sampling
- No external API calls
- No non-deterministic behavior

All results are reproducible across machines, operating systems, and runs.

---

## API Costs

**Zero**. All experiments run locally without external API calls.

- No OpenAI API calls
- No Anthropic API calls
- No external LLM inference

The benchmark simulates agent behavior using deterministic rule-based logic (not actual LLMs).

---

## Time Estimates

| Task | Time | Notes |
|------|------|-------|
| Install from PyPI | <30 seconds | Single `pip install` command |
| Clone from source | 1-2 minutes | Depends on network speed |
| Run benchmark | 2-3 seconds | Deterministic, no API calls |
| Run full test suite | 5-10 seconds | 31 tests |
| Run all examples | <5 seconds | 15+ example scripts |
| Build Docker image | 2-3 minutes | First time only |

**Total Time to Reproduce**: ~5 minutes (including installation)

---

## Reporting Issues

If you encounter any reproducibility issues:

1. **Check this guide** for troubleshooting steps
2. **Open an issue**: https://github.com/imran-siddique/agent-control-plane/issues
3. **Include**:
   - Operating system and version
   - Python version
   - Installation method (PyPI, source, Docker)
   - Complete error message
   - Steps to reproduce

---

## Reproducibility Checklist

Before submitting a paper, verify:

- [ ] All dependencies listed with exact versions
- [ ] Installation instructions tested on clean machine
- [ ] Benchmark runs and produces expected output
- [ ] Test suite passes (31/31 tests)
- [ ] Docker image builds and runs
- [ ] No external API dependencies
- [ ] No random seeds (deterministic)
- [ ] Results match published numbers
- [ ] Checksums verified

---

## Contact

For reproducibility questions:
- **GitHub Issues**: https://github.com/imran-siddique/agent-control-plane/issues
- **GitHub Discussions**: https://github.com/imran-siddique/agent-control-plane/discussions

---

**Last Updated**: January 2026  
**Version**: 1.1.0
