# Getting Started with CMVK

Welcome to the Cross-Model Verification Kernel! This guide will get you up and running in minutes.

## Quick Start (5 minutes)

### 1. Install

```bash
# Install from PyPI
pip install cross-model-verification-kernel

# Or install from source
pip install git+https://github.com/imran-siddique/cross-model-verification-kernel.git
```

### 2. Set Up API Keys

Create a `.env` file in your project root:

```bash
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-api-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

Or set environment variables:

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-openai-key-here"
export GOOGLE_API_KEY="your-google-api-key-here"

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-openai-key-here"
$env:GOOGLE_API_KEY="your-google-api-key-here"
```

### 3. Run Your First Verification

Using the CLI:

```bash
cmvk run --task "Write a fast Fibonacci function" \
         --generator gpt-4o \
         --verifier gemini-1.5-pro \
         --max-loops 5 \
         --seed 42
```

Or via Python:

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
    task="Write a Python function to check if a number is prime",
    max_loops=5,
)

print(f"Success: {result.success}")
print(f"Code:\n{result.final_code}")
```

## Understanding the System

### The Problem

Traditional code generation systems have a fatal flaw:

```
┌─────────┐      ┌─────────┐
│ GPT-4o  │ ───→ │ GPT-4o  │
│Generate │      │ Verify  │
└─────────┘      └─────────┘
    Same Model = Shared Blind Spots!
```

When the same model generates and verifies code, it misses its own mistakes.

### Our Solution

```
┌─────────┐      ┌─────────┐
│ GPT-4o  │ ───→ │ Gemini  │
│Generate │      │ Verify  │
└─────────┘      └─────────┘
Different Models = Independent Views!
```

Using different models in an adversarial relationship dramatically reduces shared blind spots.

### Blind Spot Analysis

Every verification includes mathematical analysis:

```
Blind Spot Analysis:
- Single model error probability: 0.1500 (15%)
- Combined error probability: 0.0480 (4.8%)
- Risk reduction factor: 3.12x
```

## Choosing Models

### Best: Different Providers (Recommended)

Maximum diversity = maximum benefit

| Generator | Verifier | Correlation | Risk Reduction |
|-----------|----------|-------------|----------------|
| GPT-4o | Gemini 1.5 Pro | 0.2 | ~3x |
| GPT-4o | Claude 3.5 Sonnet | 0.2 | ~3x |
| o1 | Gemini 2.0 Flash | 0.15 | ~4x |

### Good: Same Provider, Different Models

Lower diversity but still helpful

| Generator | Verifier | Correlation | Risk Reduction |
|-----------|----------|-------------|----------------|
| GPT-4o | GPT-4 Turbo | 0.5 | ~1.7x |
| Claude 3.5 | Claude 3 Opus | 0.4 | ~2x |

### Blocked: Same Model

The system prevents this to ensure effectiveness.

## Running Experiments

### Download the HumanEval Dataset

```bash
python -c "from cross_model_verification_kernel.datasets import download_full_humaneval; download_full_humaneval()"
```

### Run the Blind Spot Benchmark

```bash
python experiments/blind_spot_benchmark.py
```

This runs a comprehensive benchmark comparing baseline GPT-4o vs. CMVK across 50 HumanEval problems.

**Expected Runtime:** 20-40 minutes  
**Expected Improvement:** +7-9% accuracy

### Visualize Execution Traces

```bash
# List all traces
python -m cross_model_verification_kernel.tools.visualizer --list

# Replay the latest trace
python -m cross_model_verification_kernel.tools.visualizer --latest

# Instant playback
python -m cross_model_verification_kernel.tools.visualizer --latest --speed 0
```

## Configuration

### YAML Configuration

Edit `config/settings.yaml`:

```yaml
kernel:
  max_loops: 5
  retry_delay: 2
  prosecutor_mode: true

generator:
  model: gpt-4o
  temperature: 0.7
  max_tokens: 2000

verifier:
  model: gemini-1.5-pro
  temperature: 0.2
  adversarial_mode: true
```

### Python Configuration

```python
from cross_model_verification_kernel import VerificationKernel

kernel = VerificationKernel(
    generator=OpenAIGenerator(
        model="gpt-4o",
        temperature=0.7,
    ),
    verifier=GeminiVerifier(
        model="gemini-1.5-pro",
        temperature=0.2,
        prosecutor_mode=True,
    ),
    max_loops=5,
)
```

## Troubleshooting

### "Must use DIFFERENT models" Error

This is expected! CMVK enforces model diversity. Use different models for generator and verifier.

### API Rate Limits

Increase the retry delay in `config/settings.yaml`:

```yaml
kernel:
  retry_delay: 5  # seconds
```

### Import Errors

Ensure you're importing from the correct package:

```python
# Correct
from cross_model_verification_kernel import VerificationKernel

# Incorrect
from src import VerificationKernel  # Don't use this
```

### Missing API Keys

```bash
# Verify keys are set
echo $OPENAI_API_KEY
echo $GOOGLE_API_KEY
```

## Next Steps

1. **Read the [Architecture](architecture.md)** - Deep dive into system design
2. **Explore [Examples](../examples/)** - Working code samples
3. **Check [Safety](safety.md)** - AI safety considerations
4. **Run Experiments** - Try different model combinations

## CLI Reference

```bash
# Basic usage
cmvk run --task "Your task" --generator gpt-4o --verifier gemini-1.5-pro

# All options
cmvk run --help

# Version info
cmvk --version

# List available models
cmvk models

# View traces
cmvk trace --list
cmvk trace --latest
```

---

**Questions?** Open an issue on [GitHub](https://github.com/imran-siddique/cross-model-verification-kernel/issues)
