# Cross-Model Verification Kernel (CMVK)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Core Philosophy**: *"Trust, but Verify (with a different brain)."*

## Overview

The Cross-Model Verification Kernel (CMVK) is a research framework that addresses the "Grading Your Own Homework" fallacy in self-correcting AI agents. Instead of having a single LLM verify its own work, CMVK uses **adversarial multi-model verification** where different models with different training data and architectures verify each other's output.

### The Problem: Correlated Error Blindness

Current "self-correcting" agents suffer from a fundamental flaw: when an LLM generates a solution with a bug due to a gap in its training data or reasoning, it often uses the same flawed logic to "verify" itself. This leads to hallucinations that look like corrections.

### The Solution: Adversarial Architecture

CMVK implements a three-component system:

1. **Generator (System 1)**: High creativity, high speed builder (e.g., GPT-4o)
2. **Verifier (System 2)**: High logic, cynical adversary (e.g., Gemini 1.5 Pro)
3. **Arbiter (The Kernel)**: Deterministic logic managing the verification loop

## Key Features

- **Adversarial Engineering**: The Verifier is explicitly prompted to break the solution, not fix it
- **Runtime Unit Testing**: No action is taken without proof via executable tests
- **Graph of Truth**: A persistent state machine that prevents deadlocks and caches proven solutions
- **Model Agnostic**: Easily swap OpenAI, Google, Anthropic, or open-source models

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Verification Kernel                     │
│                     (The Arbiter)                        │
└───────────┬─────────────────────────────┬───────────────┘
            │                             │
    ┌───────▼────────┐          ┌────────▼────────┐
    │   Generator    │          │    Verifier     │
    │   (System 1)   │◄────────►│   (System 2)    │
    │   GPT-4o/o1    │  Hostile │  Gemini 1.5 Pro │
    └────────────────┘  Review  └─────────────────┘
            │                             │
            └──────────┬──────────────────┘
                       │
              ┌────────▼─────────┐
              │  Graph of Truth  │
              │  (State Machine) │
              └──────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/imran-siddique/cross-model-verification-kernel.git
cd cross-model-verification-kernel

# Install dependencies
pip install -r requirements.txt

# Set up API keys
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
```

## Quick Start

```python
from src import VerificationKernel, OpenAIGenerator, GeminiVerifier

# Initialize agents
generator = OpenAIGenerator(model_name="gpt-4o")
verifier = GeminiVerifier(model_name="gemini-1.5-pro")

# Create kernel
kernel = VerificationKernel(
    generator=generator,
    verifier=verifier,
    config_path="config/settings.yaml"
)

# Execute verification loop
task = "Write a function to find the longest palindromic substring"
result = kernel.execute(task)

print(f"Success: {result.is_complete}")
print(f"Solution: {result.final_result}")
print(f"Loops: {result.current_loop}")
```

## Project Structure

```
cross-model-verification-kernel/
├── config/                    # Configuration and prompts
│   ├── settings.yaml         # API keys, model settings
│   └── prompts/              # System prompts by role
├── src/                      # Core source code
│   ├── core/                 # Kernel logic
│   │   ├── kernel.py        # Main verification loop
│   │   ├── graph_memory.py  # Graph of Truth
│   │   └── types.py         # Data classes
│   ├── agents/               # LLM interfaces
│   │   ├── generator_openai.py
│   │   └── verifier_gemini.py
│   └── tools/                # Utilities
│       ├── sandbox.py       # Code execution
│       └── web_search.py    # Fact-checking
├── experiments/              # Research experiments
│   ├── datasets/            # Test datasets
│   ├── baseline_runner.py   # Single-model baseline
│   └── experiment_runner.py # CMVK experiments
├── tests/                    # Unit tests
├── notebooks/                # Analysis notebooks
└── requirements.txt
```

## Running Experiments

### Baseline (Single Model)
```bash
python experiments/baseline_runner.py
```

### Cross-Model Verification
```bash
python experiments/experiment_runner.py
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Configuration

Edit `config/settings.yaml` to customize:

- Model providers and names
- Temperature and token limits
- Max verification loops
- Confidence thresholds
- Sandbox settings

## Research Metrics

CMVK tracks the following success metrics:

1. **Reliability Score**: % of tasks solved correctly vs. single-model baseline
2. **Verification Accuracy**: Ability to detect subtle bugs (False Positive Rate)
3. **Efficiency**: Cost comparison with large Chain-of-Thought loops

## Contributing

This is a research project. Contributions are welcome! Areas of interest:

- Additional model providers (Anthropic Claude, LLaMA, etc.)
- Enhanced prompt engineering for adversarial verification
- New test datasets (HumanEval, LogicGrids, etc.)
- Improved graph memory algorithms
- Better response parsing

## License

MIT License - see LICENSE file for details

## Citation

If you use this work in your research, please cite:

```bibtex
@software{cmvk2024,
  author = {Siddique, Imran},
  title = {Cross-Model Verification Kernel: Adversarial Multi-Model Verification},
  year = {2024},
  url = {https://github.com/imran-siddique/cross-model-verification-kernel}
}
```

## Acknowledgments

This research is inspired by the observation that diverse models have different blind spots, and adversarial verification can catch errors that self-verification misses.

---

**Core Philosophy**: *"Trust, but Verify (with a different brain)."*
