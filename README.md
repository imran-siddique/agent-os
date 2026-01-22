# Cross-Model Verification Kernel (CMVK)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/imran-siddique/cross-model-verification-kernel/actions/workflows/ci.yml/badge.svg)](https://github.com/imran-siddique/cross-model-verification-kernel/actions)
[![PyPI version](https://badge.fury.io/py/cross-model-verification-kernel.svg)](https://badge.fury.io/py/cross-model-verification-kernel)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Adversarial multi-model verification for more reliable LLM code generation.**

> *"Trust, but Verify (with a different brain)."*

## Quick Start

```bash
# Install
pip install cross-model-verification-kernel

# Set API keys
export OPENAI_API_KEY=sk-...
export GOOGLE_API_KEY=...

# Run
cmvk run --task "Write a fast Fibonacci function" \
         --generator gpt-4o \
         --verifier gemini-1.5-pro \
         --max-loops 5
```

See [docs/getting_started.md](docs/getting_started.md) for detailed setup instructions.

## The Problem

Traditional "self-correcting" AI agents suffer from **correlated error blindness**: when an LLM generates buggy code, it often uses the same flawed logic to "verify" itself—missing its own mistakes.

```
┌─────────┐      ┌─────────┐
│ GPT-4o  │ ───→ │ GPT-4o  │
│Generate │      │ Verify  │
└─────────┘      └─────────┘
    Same Model = Shared Blind Spots
```

## The Solution

CMVK uses **adversarial multi-model verification** where different models with different training data verify each other's work:

```
┌─────────┐      ┌─────────────┐      ┌─────────┐
│ GPT-4o  │ ───→ │   Kernel    │ ───→ │ Gemini  │
│Generator│      │  (Arbiter)  │      │Verifier │
└─────────┘      └─────────────┘      └─────────┘
                       │
              ┌────────▼─────────┐
              │  Graph of Truth  │
              │  (State Machine) │
              └──────────────────┘
```

**Key insight**: Different models have *different* blind spots. By using an adversarial verifier from a different provider, we dramatically reduce the probability of shared errors.

## Benchmark Results

### HumanEval (n=164, 5 runs)

| Method | Pass@1 | Δ vs Baseline | Avg Loops |
|--------|--------|---------------|-----------|
| GPT-4o (baseline) | 84.1% ± 1.2 | — | 1.0 |
| GPT-4o self-verify | 85.2% ± 1.4 | +1.1 | 1.6 |
| **CMVK (GPT-4o → Gemini)** | **92.4% ± 0.9** | **+8.3** | 1.8 |
| **CMVK (GPT-4o → Claude)** | **91.8% ± 1.0** | **+7.7** | 1.7 |

*All CMVK results statistically significant (p < 0.01, Welch's t-test)*

### Sabotage Detection (Prosecutor Mode)

| Method | Recall | Precision | F1 Score |
|--------|--------|-----------|----------|
| GPT-4o self-review | 61% | 72% | 0.66 |
| **CMVK Prosecutor** | **89%** | 84% | **0.86** |

## Usage

### CLI

```bash
# Basic verification
cmvk run --task "Implement binary search"

# Specify models
cmvk run --task "Sort without built-in functions" \
         --generator gpt-4o \
         --verifier claude-3-5-sonnet-20241022

# Reproducible experiments
cmvk run --task "Check if prime" --seed 42 --output json

# List available models
cmvk models
```

### Python API

```python
from cross_model_verification_kernel import (
    VerificationKernel,
    OpenAIGenerator,
    GeminiVerifier,
)

# Create agents
generator = OpenAIGenerator(model="gpt-4o")
verifier = GeminiVerifier(model="gemini-1.5-pro")

# Create kernel
kernel = VerificationKernel(generator=generator, verifier=verifier)

# Run verification
result = kernel.run(
    task="Write a function to find the longest palindrome",
    max_loops=5,
)

print(f"Success: {result.success}")
print(f"Solution:\n{result.final_code}")
```

### Watch the Adversarial Debate

```bash
# Replay execution traces
cmvk trace --latest

# Example output:
# >>> GPT-4o: I'll solve this using built-in sort...
# >>> Gemini: OBJECTION! Violates constraint 'without sorted()'
# >>> Kernel: ⚖️ Objection sustained. Strategy 'Built-In Sort' BANNED.
# >>> GPT-4o: I'll try iterative sorting instead...
# >>> Gemini: Verification PASSED. All tests successful.
# >>> Kernel: ✅ Solution ACCEPTED.
```

## Installation

### From PyPI

```bash
pip install cross-model-verification-kernel
```

### From Source (Development)

```bash
git clone https://github.com/imran-siddique/cross-model-verification-kernel.git
cd cross-model-verification-kernel

# Install with all dependencies
pip install -e ".[all]"

# Or install dev dependencies separately
pip install -e ".[dev]"
```

### Docker

```bash
docker build -t cmvk:latest .
docker run -it --rm \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  cmvk:latest cmvk run --task "Implement quicksort"
```

## Project Structure

```
cross-model-verification-kernel/
├── src/cross_model_verification_kernel/  # Main package
│   ├── core/                # Kernel logic & graph memory
│   ├── agents/              # LLM interfaces (OpenAI, Gemini, Claude)
│   ├── tools/               # Sandbox execution, visualization
│   └── datasets/            # Dataset loaders
├── tests/                   # Unit & integration tests
├── experiments/             # Research benchmarks
│   ├── datasets/           # HumanEval, sabotage tests
│   └── scripts/            # Experiment runners
├── docs/                    # Documentation
├── paper/                   # Research paper & figures
└── config/                  # Configuration files
```

## Key Features

- **Adversarial Verification**: Verifier actively tries to break solutions
- **Model Diversity**: Enforces different models for generator/verifier
- **Prosecutor Mode**: Hostile testing catches 89% of bugs
- **Graph of Truth**: Prevents infinite loops, caches proven solutions
- **Strategy Banning**: Automatically avoids failing approaches
- **Full Traceability**: Replay any execution step-by-step

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting_started.md) | Installation and first steps |
| [Architecture](docs/architecture.md) | System design deep-dive |
| [Safety](docs/safety.md) | Responsible use guidelines |
| [Paper](paper/PAPER.md) | Full research paper |

## Running Experiments

```bash
# Quick sanity check (5 problems)
python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_sample.json

# Full benchmark (164 problems)
python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_full.json

# Sabotage stress test
python experiments/sabotage_stress_test.py
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
pre-commit run --all-files

# Type checking
mypy src/
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas of interest:
- Additional model providers (LLaMA, Mistral, etc.)
- Enhanced adversarial prompts
- New benchmark datasets
- Improved graph memory algorithms

## Citation

```bibtex
@software{cmvk2026,
  author = {Siddique, Imran},
  title = {Cross-Model Verification Kernel: Adversarial Multi-Model Verification},
  year = {2026},
  url = {https://github.com/imran-siddique/cross-model-verification-kernel}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Core Philosophy</strong>: <em>"Trust, but Verify (with a different brain)."</em>
</p>
