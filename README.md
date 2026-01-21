# Cross-Model Verification Kernel (CMVK)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Research Complete](https://img.shields.io/badge/Status-Research%20Ready-green.svg)](https://github.com/imran-siddique/cross-model-verification-kernel)

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

## 🎬 See It In Action

### Watch the Adversarial Debate

CMVK provides a powerful visualization tool that lets you watch the "debate" between the Generator and Verifier in real-time:

```bash
# Replay the most recent execution trace
python -m src.tools.visualizer --latest

# List all available traces
python -m src.tools.visualizer --list

# Replay a specific trace
python -m src.tools.visualizer logs/traces/cmvk_HumanEval_0_*.json

# Speed up playback (0 = instant, default = 0.5 seconds between messages)
python -m src.tools.visualizer --latest --speed 0
```

**Example Output:**
```
🎭 ADVERSARIAL KERNEL REPLAY 🎭
================================================================================

>>> GPT-4o (The Builder): I'll solve this using Built-In Sort...
    [Generated Code]

>>> Gemini (The Prosecutor): OBJECTION! The solution violates 
    the constraint 'WITHOUT using sorted()'.

>>> Kernel (The Arbiter): ⚖️  Objection Sustained. Solution REJECTED.
>>> Kernel (The Arbiter): 🚫 Strategy 'Built-In Sort' is now BANNED.

>>> GPT-4o (The Builder): I'll solve this using Iterative Sorting...
    [New Solution]

>>> Gemini (The Prosecutor): Verification PASSED. All tests successful.
>>> Kernel (The Arbiter): ✅ Solution ACCEPTED.
```

This visualization shows exactly how CMVK prevents blind spots through adversarial verification!

## 🔬 Running Research Experiments

### Quick Start: Automated Pipeline Test

Run the complete pipeline in one command:

```bash
# Quick sanity check (5 problems, ~30 seconds)
python test_full_pipeline.py

# With 50-problem dataset (better statistical significance)
python test_full_pipeline.py --dataset experiments/datasets/humaneval_50.json

# Full science run (164 problems, ~15-20 minutes)
python test_full_pipeline.py --full
```

The pipeline test automates:
1. Running the benchmark
2. Checking for execution traces
3. Visualizing the adversarial debate

### Manual Step-by-Step Instructions

#### Step 1: Run the "Sanity Check" (Fast)

Before running the full benchmark, ensure the pipeline works on the sample dataset:

```bash
# Run the benchmark on the small sample (5 problems)
python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_sample.json
```

**Success Indicator:** It should finish in ~30 seconds and save a JSON file to `experiments/results/`.

#### Step 2: The "Science Run" (Full Data)

To get statistically significant results for your paper, run on the full dataset:

```bash
# Option A: Download the full dataset first (if not already present)
python -c "from src.datasets.humaneval_loader import download_full_humaneval; download_full_humaneval()"

# Option B: Use the included full dataset (164 problems)
python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_full.json
```

**Note:** This will take ~15-20 minutes and consume ~50-100 API calls per model.

#### Step 3: Watch the Debate (The Demo)

Once the benchmark finishes, use the **Visualizer** to see the "Prosecutor" in action:

```bash
# List all recorded debates
python -m src.tools.visualizer --list

# Play back the latest one (Adversarial Replay)
python -m src.tools.visualizer --latest

# Or view a specific trace
python -m src.tools.visualizer logs/traces/cmvk_HumanEval_0_*.json
```

**Look for:** A moment where Gemini says "FAIL" and GPT-4o says "I'll try a different strategy." Take a screenshot of this for your `README.md`.

### What Gets Generated

After running the benchmark, you'll find:
- **Results JSON**: `experiments/results/blind_spot_benchmark_YYYYMMDD_HHMMSS.json`
- **Summary Report**: `experiments/results/blind_spot_summary_YYYYMMDD_HHMMSS.txt`
- **Execution Traces**: `logs/traces/cmvk_HumanEval_*.json` (if trace logging is enabled)

### Expected Outcomes

The benchmark compares:
- **Baseline**: Single-model GPT-4o (no verification loop)
- **CMVK**: GPT-4o + Gemini with adversarial verification

Key metrics:
- Pass rate (% of problems solved correctly)
- Average attempts needed per problem
- Strategy banning frequency
- Critical bugs caught by the verifier

### Additional Experiments

```bash
# Run the Sabotage Stress Test
python experiments/sabotage_stress_test.py

# Test lateral thinking feature
python experiments/test_lateral_thinking.py

# Compare model diversity
python examples/model_diversity_comparison.py
```

## Project Structure

```
cross-model-verification-kernel/
├── config/                       # Configuration and prompts
│   ├── settings.yaml            # API keys, model settings
│   └── prompts/                 # System prompts by role
├── src/                         # Core source code
│   ├── core/                    # Kernel logic
│   │   ├── kernel.py           # Main verification loop
│   │   ├── graph_memory.py     # Graph of Truth
│   │   └── types.py            # Data classes
│   ├── agents/                  # LLM interfaces
│   │   ├── generator_openai.py
│   │   └── verifier_gemini.py
│   ├── datasets/                # Dataset loaders
│   │   └── humaneval_loader.py # HumanEval integration
│   └── tools/                   # Utilities
│       ├── sandbox.py          # Code execution
│       ├── visualizer.py       # Trace replay tool
│       └── web_search.py       # Fact-checking
├── experiments/                 # Research experiments
│   ├── datasets/               # Test datasets
│   │   ├── humaneval_50.json  # 50-problem benchmark set
│   │   ├── humaneval_full.json # Complete 164 problems
│   │   └── sabotage.json      # Bug detection test cases
│   ├── blind_spot_benchmark.py # Main benchmark script
│   ├── sabotage_stress_test.py # Verifier evaluation
│   ├── baseline_runner.py      # Single-model baseline
│   └── results/                # Generated results
├── logs/
│   └── traces/                 # Execution traces for visualization
├── tests/                       # Unit tests
├── notebooks/                   # Analysis notebooks
├── PAPER.md                     # Research paper draft
└── requirements.txt
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

- Model providers and names (OpenAI, Google, Anthropic)
- Temperature and token limits
- Max verification loops (default: 5)
- Confidence thresholds (default: 0.85)
- Sandbox execution settings
- Prosecutor Mode (hostile testing)

## 📊 Research Metrics

CMVK tracks the following metrics for evaluation:

1. **Pass Rate**: Percentage of problems solved correctly
2. **Blind Spot Detection**: Cases where Verifier caught errors missed by Generator
3. **Strategy Diversity**: Number of unique approaches explored via banning
4. **Verification Accuracy**: True positive rate for bug detection
5. **Efficiency**: Average attempts needed to reach solution

## 📖 Documentation

- **[PAPER.md](PAPER.md)**: Complete research paper draft with methodology, experiments, and results
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system architecture
- **[GETTING_STARTED.md](GETTING_STARTED.md)**: Step-by-step tutorial
- **[FEATURE_3_TRACEABILITY.md](FEATURE_3_TRACEABILITY.md)**: Trace logging and visualization guide

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
