# Experiments

This directory contains the validation experiments for the Cross-Model Verification Kernel (CMVK).

## Phase 3: Validation Experiments

These experiments provide empirical evidence for the research paper, demonstrating the effectiveness of adversarial multi-model verification.

### Experiment A: Blind Spot Benchmark

**Goal:** Prove CMVK > Single Model in reliability

**What it measures:**
- Success rate on coding benchmarks (HumanEval-style problems)
- Comparison between single-model (GPT-4o alone) and CMVK (GPT-4o + Gemini)

**How to run:**
```bash
python experiments/blind_spot_benchmark.py
```

**Dataset:** `experiments/datasets/humaneval_sample.json`
- Contains 5 sample HumanEval problems
- Each problem includes:
  - Function prompt
  - Test cases
  - Entry point function name

**Output:**
- `results/blind_spot_benchmark_[timestamp].json` - Full results
- `results/blind_spot_summary_[timestamp].txt` - Human-readable summary

**Expected results:**
- CMVK success rate should be higher than baseline
- Demonstrates that cross-model verification catches errors missed by self-correction

---

### Experiment B: Sabotage Stress Test

**Goal:** Prove the Verifier actually catches bugs (Recall Rate)

**What it measures:**
- Bug detection recall rate
- Precision of bug detection
- F1 score and accuracy

**How to run:**
```bash
python experiments/sabotage_stress_test.py
```

**Dataset:** `experiments/datasets/sabotage.json`
- 20 valid code samples (should pass verification)
- 20 buggy code samples (should fail verification)
- Bugs include:
  - Division by zero
  - Index out of bounds
  - Infinite recursion
  - Missing error handling
  - Off-by-one errors
  - Syntax errors

**Output:**
- `results/sabotage_stress_test_[timestamp].json` - Full results
- `results/sabotage_summary_[timestamp].txt` - Human-readable summary with confusion matrix

**Key metrics:**
- **Recall**: Of all real bugs, how many did we detect? (Most important!)
- **Precision**: Of all bugs we detected, how many were real?
- **F1 Score**: Harmonic mean of precision and recall

**Expected results:**
- High recall rate (>80%) demonstrates effective bug detection
- Uses Prosecutor Mode to generate hostile tests

---

### Experiment C: Efficiency Curve

**Goal:** Address the criticism "Two models are too expensive"

**What it measures:**
- Token usage per task
- Number of iterations needed
- Total cost comparison

**How to run:**
```bash
python experiments/efficiency_curve.py
```

**Dataset:** Uses `experiments/datasets/sample.json` or any task dataset

**Output:**
- `results/efficiency_curve_[timestamp].json` - Full results with per-task breakdown
- `results/efficiency_summary_[timestamp].txt` - Summary with token counts

**Hypothesis:**
- Single models hallucinate and loop many times (high token cost)
- CMVK catches errors early and converges faster (lower total cost)
- Even though CMVK uses two models, it may be more efficient overall

**Key metrics:**
- Average tokens per task
- Average loops per task
- Success rate
- Total cost

---

## Running All Experiments

To run all three experiments in sequence:

```bash
# Run Blind Spot Benchmark
python experiments/blind_spot_benchmark.py

# Run Sabotage Stress Test
python experiments/sabotage_stress_test.py

# Run Efficiency Curve
python experiments/efficiency_curve.py
```

## Results Directory

All experiment results are saved to `experiments/results/` with timestamps:

```
experiments/results/
├── blind_spot_benchmark_20240315_143022.json
├── blind_spot_summary_20240315_143022.txt
├── sabotage_stress_test_20240315_143545.json
├── sabotage_summary_20240315_143545.txt
├── efficiency_curve_20240315_144102.json
└── efficiency_summary_20240315_144102.txt
```

## Creating Custom Datasets

### HumanEval Format (Experiment A)

```json
[
  {
    "task_id": "HumanEval/0",
    "prompt": "def function_name(args):\n    \"\"\"Description\"\"\"\n",
    "test": "def check(candidate):\n    assert candidate(input) == expected\n",
    "entry_point": "function_name"
  }
]
```

### Sabotage Format (Experiment B)

```json
[
  {
    "id": "valid_1",
    "type": "valid",
    "code": "def valid_function():\n    return True",
    "description": "A valid function"
  },
  {
    "id": "buggy_1",
    "type": "buggy",
    "code": "def buggy_function(x):\n    return 1/x",
    "description": "Division by zero bug",
    "bug": "No check for x == 0"
  }
]
```

## Dependencies

Make sure you have the required API keys set:

```bash
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Mock Mode

If API keys are not available, experiments will run in mock mode for testing the infrastructure. Mock mode generates synthetic results but doesn't make real API calls.

## Notes for Research Paper

These experiments provide the empirical data for the paper:

1. **Experiment A** provides the reliability comparison (Table 1)
2. **Experiment B** provides the security/safety metrics (Table 2)
3. **Experiment C** provides the efficiency analysis (Figure 1)

Each experiment generates both machine-readable JSON and human-readable summary files for easy integration into the paper.

## Citation

If you use these experiments in your research, please cite:

```bibtex
@software{cmvk2024,
  author = {Siddique, Imran},
  title = {Cross-Model Verification Kernel: Adversarial Multi-Model Verification},
  year = {2024},
  url = {https://github.com/imran-siddique/cross-model-verification-kernel}
}
```
