# Quick Start Guide: Running the Benchmark Experiments

This guide walks you through the complete process of running the CMVK research experiments from start to finish.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+** installed
2. **API Keys** from:
   - OpenAI (GPT-4o): Get from https://platform.openai.com/api-keys
   - Google AI (Gemini): Get from https://aistudio.google.com/app/apikey

3. **Sufficient API Credits**:
   - The 50-problem benchmark makes ~100-150 API calls to OpenAI
   - The 50-problem benchmark makes ~100-250 API calls to Google (Gemini in Prosecutor Mode is aggressive)
   - Estimated cost: $2-5 USD depending on solution complexity

## Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/imran-siddique/cross-model-verification-kernel.git
cd cross-model-verification-kernel

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Keys

Set up your environment variables:

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-openai-key-here"
export GOOGLE_API_KEY="your-google-api-key-here"

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-openai-key-here"
$env:GOOGLE_API_KEY="your-google-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-openai-key-here
set GOOGLE_API_KEY=your-google-api-key-here
```

**Pro Tip:** Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

## Step 3: Verify Installation

Test that everything is set up correctly:

```bash
# Test core imports
python -c "from src import VerificationKernel, OpenAIGenerator, GeminiVerifier; print('✅ Core modules loaded')"

# Test API keys (this will make a small test call)
python -c "
from src.agents.generator_openai import OpenAIGenerator
from src.agents.verifier_gemini import GeminiVerifier

try:
    gen = OpenAIGenerator()
    ver = GeminiVerifier()
    print('✅ API keys are valid and working')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

## Step 4: Download the HumanEval Dataset

The full HumanEval dataset (164 problems) will be downloaded automatically:

```bash
python -c "from src.datasets.humaneval_loader import download_full_humaneval; download_full_humaneval()"
```

**Expected Output:**
```
Downloading HumanEval dataset from https://github.com/openai/human-eval/...
✅ Downloaded 164 problems to experiments/datasets/humaneval_full.json
```

**Note:** A 50-problem subset (`humaneval_50.json`) is already included for the benchmark.

## Step 5: Run the Blind Spot Benchmark

This is the main experiment comparing baseline GPT-4o vs. CMVK:

```bash
python experiments/blind_spot_benchmark.py
```

**What Happens:**
1. Loads 50 HumanEval problems
2. For each problem:
   - Runs baseline (GPT-4o alone, single attempt)
   - Runs CMVK (GPT-4o + Gemini, up to 5 attempts with verification)
3. Tests solutions against the HumanEval test cases
4. Generates results and traces

**Expected Runtime:** 20-40 minutes depending on problem complexity and API response times

**Expected Output:**
```
================================================================
BLIND SPOT BENCHMARK COMPLETED
================================================================
Baseline Success Rate: 85.00%
CMVK Success Rate: 92.00%
Improvement: +8.2%
================================================================
```

**Generated Files:**
- `experiments/results/blind_spot_benchmark_YYYYMMDD_HHMMSS.json` - Full results
- `experiments/results/blind_spot_summary_YYYYMMDD_HHMMSS.txt` - Human-readable summary
- `logs/traces/cmvk_HumanEval_*.json` - Individual execution traces (one per problem)

## Step 6: Analyze the Results

### View the Summary

```bash
# View the most recent summary file
ls -t experiments/results/blind_spot_summary_*.txt | head -1 | xargs cat
```

### Explore Execution Traces

List all execution traces:
```bash
python -m src.tools.visualizer --list
```

Replay the most recent trace (shows the adversarial debate):
```bash
python -m src.tools.visualizer --latest
```

Replay a specific trace:
```bash
python -m src.tools.visualizer logs/traces/cmvk_HumanEval_0_*.json
```

**Pro Tip:** Use `--speed 0` for instant playback:
```bash
python -m src.tools.visualizer --latest --speed 0
```

### Find "Money Shot" Examples

Look for traces where:
1. Generator proposed a solution
2. Verifier caught a bug (status: failed)
3. Generator fixed it (status: success)
4. Bonus: A strategy was banned

```bash
# List all traces, sorted by modification time
python -m src.tools.visualizer --list

# Replay each one to find interesting examples
python -m src.tools.visualizer logs/traces/cmvk_HumanEval_5_*.json --speed 0
```

## Step 7: (Optional) Run the Sabotage Stress Test

This experiment tests the Verifier's bug detection capabilities:

```bash
python experiments/sabotage_stress_test.py
```

**What Happens:**
- Tests the verifier against 40 code samples (20 valid, 20 buggy)
- Measures precision, recall, and F1 score
- Validates Prosecutor Mode effectiveness

**Expected Runtime:** 10-15 minutes

**Expected Output:**
```
================================================================
SABOTAGE STRESS TEST COMPLETED
================================================================
Recall (Bug Detection Rate): 90.00%
Precision: 85.00%
F1 Score: 87.50%
Accuracy: 87.50%
================================================================
```

## Step 8: Update the Paper

After running the experiments, fill in the results in `PAPER.md`:

1. Open `PAPER.md`
2. Find Section 3.3 (Results)
3. Fill in the table with your actual numbers:
   - Baseline pass rate
   - CMVK pass rate
   - Improvement percentage
   - Runtime statistics

4. Find Section 5.1 (Discussion)
5. Add a "Money Shot" example - paste the output from a compelling trace

6. Find Appendix B (Example Traces)
7. Add 2-3 complete trace examples showing different scenarios

## Troubleshooting

### API Rate Limits

If you hit rate limits:
```python
# Edit config/settings.yaml
kernel:
  retry_delay: 5  # Increase delay between retries (seconds)
```

### Sandbox Execution Issues

If code execution fails:
```bash
# Check Python is available
python --version

# Check sandbox executor
python -c "from src.tools.sandbox import SandboxExecutor; s = SandboxExecutor(); print(s.execute_python('print(1+1)'))"
```

### Missing API Keys

If you see "API key not found" errors:
```bash
# Verify environment variables are set
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows
```

### Import Errors

If you see import errors:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

Once you have your results:

1. **Update PAPER.md** with experimental results
2. **Update README.md** with any findings or observations
3. **Share interesting traces** - The adversarial debates make great examples
4. **Scale up** - Try running on all 164 HumanEval problems
5. **Experiment** - Try different model combinations (e.g., GPT-4o + Claude)

## Questions?

- Check the documentation: `ARCHITECTURE.md`, `FEATURE_3_TRACEABILITY.md`
- Review example traces: `python -m src.tools.visualizer --list`
- Inspect the code: Start with `experiments/blind_spot_benchmark.py`

## Summary of Key Commands

```bash
# Setup
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"

# Download dataset
python -c "from src.datasets.humaneval_loader import download_full_humaneval; download_full_humaneval()"

# Run benchmark (THE BIG ONE)
python experiments/blind_spot_benchmark.py

# Visualize results
python -m src.tools.visualizer --latest

# Optional: Sabotage test
python experiments/sabotage_stress_test.py
```

Good luck with your experiments! 🚀
