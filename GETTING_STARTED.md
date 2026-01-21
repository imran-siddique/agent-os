# Getting Started Guide

## Quick Start (5 minutes)

### 1. Clone and Navigate
```bash
git clone https://github.com/imran-siddique/cross-model-verification-kernel.git
cd cross-model-verification-kernel
```

### 2. Run Basic Example
```bash
python examples/basic_example.py
```

This demonstrates:
- Code generation with GPT-4o
- Adversarial verification with Gemini 1.5 Pro
- Blind spot analysis showing 3x risk reduction

### 3. Run Model Diversity Comparison
```bash
python examples/model_diversity_comparison.py
```

This shows:
- Why model diversity matters
- Mathematical reduction in error probability
- Comparison of different model combinations

### 4. Run Tests
```bash
python -m unittest tests.test_kernel -v
```

All 19 tests should pass.

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

## Key Features

### 1. Model Diversity Enforcement

The system **enforces** that you use different models:

```python
# This works ✓
generator = GeneratorConfig(model=ModelProvider.GPT4O)
verifier = VerifierConfig(model=ModelProvider.GEMINI_15_PRO)

# This fails ✗
generator = GeneratorConfig(model=ModelProvider.GPT4O)
verifier = VerifierConfig(model=ModelProvider.GPT4O)  # Error!
```

### 2. Adversarial Verification

The verifier operates in **hostile mode**, actively looking for problems:

- Security vulnerabilities
- Logic errors
- Edge cases
- Performance issues
- Missing error handling

### 3. Mathematical Framework

Every verification includes blind spot analysis:

```
Blind Spot Analysis:
- Single model error probability: 0.1500 (15%)
- Combined error probability: 0.0480 (4.8%)
- Risk reduction factor: 3.12x
```

## Basic Usage

```python
from src.generator import GeneratorConfig
from src.verifier import VerifierConfig
from src.kernel import VerificationKernel
from src.models import ModelProvider

# Setup (different models required!)
generator_config = GeneratorConfig(
    model=ModelProvider.GPT4O,
    temperature=0.7
)

verifier_config = VerifierConfig(
    model=ModelProvider.GEMINI_15_PRO,
    temperature=0.2,
    adversarial_mode=True
)

# Create kernel
kernel = VerificationKernel(generator_config, verifier_config)

# Verify a task
result = kernel.verify_task(
    task_description="Create a function to sort a list",
    language="python"
)

# Check results
print(f"Status: {result.verification_report.passed}")
print(f"Issues: {len(result.verification_report.issues)}")
print(f"Risk Reduction: {result.blind_spot_analysis.risk_reduction_factor:.2f}x")
```

## What You Get

### 1. Generated Code
```python
result.generated_code.code        # The generated code
result.generated_code.language    # Programming language
result.generated_code.model_used  # Which model generated it
```

### 2. Verification Report
```python
result.verification_report.passed  # True/False
result.verification_report.issues  # List of issues found
result.verification_report.summary # Summary text
```

Each issue includes:
- Severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Category (security, performance, logic, etc.)
- Description
- Suggestion for fixing

### 3. Blind Spot Analysis
```python
result.blind_spot_analysis.single_model_error_prob    # 15%
result.blind_spot_analysis.combined_error_prob        # ~5%
result.blind_spot_analysis.risk_reduction_factor      # ~3x
result.blind_spot_analysis.correlation_coefficient    # 0.2
```

## Choosing Models

### Best: Different Providers

Maximum diversity = maximum benefit

```python
# OpenAI → Google (recommended)
generator: GPT4O
verifier: GEMINI_15_PRO
correlation: 0.2, risk reduction: ~3x

# OpenAI → Anthropic (recommended)
generator: GPT4O
verifier: CLAUDE_35_SONNET
correlation: 0.2, risk reduction: ~3x
```

### Good: Same Provider, Different Models

Lower diversity but still helpful

```python
# OpenAI → OpenAI (acceptable)
generator: GPT4O
verifier: GPT4_TURBO
correlation: 0.5, risk reduction: ~1.7x
```

### Blocked: Same Model

The system prevents this

```python
# This raises an error
generator: GPT4O
verifier: GPT4O
Error: "Must use DIFFERENT models"
```

## Example Output

```
================================================================================
ADVERSARIAL VERIFICATION REPORT
================================================================================

Generator Model: gpt-4o
Verifier Model: gemini-1.5-pro

Generated Code (python):
--------------------------------------------------------------------------------
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
--------------------------------------------------------------------------------

Verification Status: ✗ FAILED
Issues Found: 5

  1. [CRITICAL] security
     No input validation - negative numbers will cause stack overflow

  2. [HIGH] performance
     Exponential time complexity O(2^n) - inefficient

Blind Spot Analysis:
- Risk reduction factor: 3.97x
================================================================================
```

## Configuration Options

### Generator

```python
GeneratorConfig(
    model=ModelProvider.GPT4O,
    temperature=0.7,              # Higher = more creative
    max_tokens=2000,              # Max output length
    custom_instructions="..."     # Optional system prompt
)
```

### Verifier

```python
VerifierConfig(
    model=ModelProvider.GEMINI_15_PRO,
    temperature=0.2,              # Lower = more consistent
    max_tokens=3000,              # Max analysis length
    adversarial_mode=True         # Enable hostile review
)
```

## Real API Integration

Current implementation uses **mock models** for demonstration. To use real APIs:

1. See `examples/real_api_integration.py`
2. Implement `BaseModelInterface` with actual API calls
3. Install API packages: `pip install openai google-generativeai anthropic`
4. Set API keys as environment variables
5. Pass custom interfaces to Generator/Verifier

## Troubleshooting

### "Must use DIFFERENT models" Error

✓ **Good** - This means model diversity enforcement is working!

Change one of your models to use a different provider.

### No Issues Found

If the verifier finds no issues, either:
1. The code is genuinely good
2. The mock model is too lenient (use real API)
3. The task was too simple

### Import Errors

Make sure you're in the project root and using:
```python
from src.generator import GeneratorConfig
```

Not:
```python
from generator import GeneratorConfig  # Wrong
```

## Next Steps

1. **Try the Examples** - Run all three example scripts
2. **Read the Docs** - Check `ARCHITECTURE.md` for deep dive
3. **Run Tests** - Verify everything works on your system
4. **Integrate Real APIs** - Connect to actual LLM providers
5. **Build Something** - Use in your own projects

## Support

- **GitHub Issues**: For bugs and feature requests
- **Documentation**: `README.md` and `ARCHITECTURE.md`
- **Examples**: Three working examples in `examples/`
- **Tests**: 19 unit tests in `tests/`

## Key Takeaways

1. **Model diversity reduces blind spots** - mathematically proven
2. **Adversarial verification catches more issues** - than cooperative self-refinement
3. **Different providers work best** - lowest correlation
4. **System enforces safety** - won't let you use same model
5. **Full transparency** - see exactly what each model thinks

---

**Ready to start?** Run `python examples/basic_example.py` now!
