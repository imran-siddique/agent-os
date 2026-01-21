# Datasets Directory

This directory contains benchmark datasets used for evaluating CMVK.

## Files

### HumanEval Datasets

1. **`humaneval_sample.json`** (5 problems)
   - Minimal sample for quick testing
   - Manually curated from HumanEval
   - Always included in repository

2. **`humaneval_50.json`** (50 problems)
   - Default benchmark dataset
   - First 50 problems from HumanEval
   - Used for statistical significance testing
   - Generated from humaneval_full.json
   - **Included in repository for convenience**

3. **`humaneval_full.json`** (164 problems)
   - Complete HumanEval benchmark
   - Downloaded from official OpenAI repository
   - Source: https://github.com/openai/human-eval
   - **Included in repository for convenience**

### Regenerating Datasets

If you need to regenerate these datasets:

```bash
# Download the full HumanEval dataset
python -c "from src.datasets.humaneval_loader import download_full_humaneval; download_full_humaneval()"

# Create the 50-problem subset
python -c "
import json
with open('experiments/datasets/humaneval_full.json', 'r') as f:
    full_data = json.load(f)
subset = full_data[:50]
with open('experiments/datasets/humaneval_50.json', 'w') as f:
    json.dump(subset, f, indent=2)
print(f'Created humaneval_50.json with {len(subset)} problems')
"
```

### Other Datasets

4. **`sabotage.json`** (40 test cases)
   - Custom dataset for testing verifier bug detection
   - 20 valid code samples
   - 20 buggy code samples
   - Used by `sabotage_stress_test.py`

5. **`sample.json`** (2 problems)
   - Simple test problems
   - Used for quick integration tests

## Dataset Format

All HumanEval datasets follow the same format:

```json
[
  {
    "task_id": "HumanEval/0",
    "prompt": "from typing import List\n\ndef function_name(...):\n    \"\"\"Docstring\"\"\"\n",
    "test": "def check(candidate):\n    assert ...\n",
    "entry_point": "function_name"
  }
]
```

## License and Attribution

The HumanEval dataset is from:
- **Paper**: "Evaluating Large Language Models Trained on Code" (Chen et al., 2021)
- **Source**: https://github.com/openai/human-eval
- **License**: MIT License

## Usage in Experiments

- **Blind Spot Benchmark** (`blind_spot_benchmark.py`): Uses `humaneval_50.json` by default
- **Full Evaluation**: Can be run with `humaneval_full.json` for complete results
- **Quick Testing**: Use `humaneval_sample.json` for rapid iteration
