# Launch Checklist for Adversarial Kernel Architecture

This document provides a final checklist for completing and launching the CMVK research project.

## ✅ What's Complete

### Core Features Implemented

- [x] **Feature 1: The Prosecutor** - `GeminiVerifier` generates hostile test cases
- [x] **Feature 2: Lateral Thinking** - `VerificationKernel` tracks forbidden approaches and forces branching
- [x] **Feature 3: The Witness** - `TraceLogger` and `Visualizer` capture and replay debates
- [x] **Benchmarks** - `BlindSpotBenchmark` class generates data for research papers

### Infrastructure Ready

- [x] Benchmark script (`experiments/blind_spot_benchmark.py`)
- [x] Dataset loader with full HumanEval (164 problems) available
- [x] Visualizer tool for replaying adversarial debates
- [x] Automated pipeline test script (`test_full_pipeline.py`)
- [x] Sample trace file for demonstration
- [x] Comprehensive documentation in README.md and PAPER.md

### Testing Verified

- [x] Benchmark runs successfully on sample dataset (5 problems)
- [x] Benchmark can handle 50-problem dataset
- [x] Full HumanEval dataset (164 problems) is available
- [x] Visualizer successfully displays traces
- [x] Pipeline test script works end-to-end

## 📋 Pre-Launch Checklist

Before running the full benchmark for publication, complete these steps:

### 1. Environment Setup

- [ ] Set up API keys:
  ```bash
  export OPENAI_API_KEY="your-openai-key-here"
  export GOOGLE_API_KEY="your-google-key-here"
  ```

- [ ] Verify API access:
  ```bash
  # Test OpenAI
  python -c "from openai import OpenAI; client = OpenAI(); print('OpenAI: OK')"
  
  # Test Google
  python -c "import google.generativeai as genai; genai.configure(); print('Google: OK')"
  ```

- [ ] Ensure sufficient API credits:
  - Estimated cost for full run (164 problems): $10-20 per model
  - Total: ~$30-40 for both models

### 2. Quick Sanity Check (~30 seconds)

Run the sanity check to ensure everything works:

```bash
python test_full_pipeline.py
```

Expected output:
- Benchmark completes successfully
- Results saved to `experiments/results/`
- Summary shows success rates (will be 0% in mock mode, >0% with real APIs)

### 3. Pilot Run (50 problems, ~5-10 minutes)

Before the full run, test with 50 problems:

```bash
python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_50.json
```

This provides:
- Statistical significance (n=50)
- Faster iteration for testing
- Enough data for preliminary results

### 4. Full Science Run (164 problems, ~15-20 minutes)

Run the complete benchmark:

```bash
python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_full.json
```

This generates:
- Complete results for 164 HumanEval problems
- JSON and summary files in `experiments/results/`
- Data for publication-quality results

### 5. Visualize Results

After the benchmark completes:

```bash
# List all traces
python -m src.tools.visualizer --list

# View the most interesting debates
python -m src.tools.visualizer --latest

# Find specific examples for paper
python -m src.tools.visualizer logs/traces/cmvk_HumanEval_X_*.json
```

**Look for:**
- Cases where Gemini caught bugs that GPT-4o missed
- Examples of strategy banning forcing new approaches
- Edge cases requiring multiple iterations

### 6. Update Documentation

After running experiments:

1. **Update PAPER.md:**
   - Fill in the results table with actual numbers
   - Add key findings section with specific examples
   - Include visualizations or screenshots

2. **Update README.md:**
   - Add a screenshot of the visualizer output
   - Update the "Expected Outcomes" section with actual results
   - Add any interesting findings or examples

3. **Create presentation materials:**
   - Select 2-3 best examples from traces
   - Create visualizations of success rates
   - Prepare demo for talks/presentations

## 🚀 Launch Commands

### Quick Start (Testing)
```bash
# Run everything in one command
python test_full_pipeline.py
```

### For Publication (Full Run)
```bash
# Step 1: Sanity check
python test_full_pipeline.py

# Step 2: Full benchmark
python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_full.json

# Step 3: Visualize results
python -m src.tools.visualizer --latest

# Step 4: Check results
cat experiments/results/blind_spot_summary_*.txt | tail -20
```

## 📊 Expected Results

Based on similar research and the architecture design, you should expect:

**Baseline (Single-Model GPT-4o):**
- Pass rate: ~70-80% (HumanEval baseline for GPT-4o)
- Single attempt per problem
- No strategy adaptation

**CMVK (GPT-4o + Gemini):**
- Pass rate: ~85-95% (expected improvement)
- Average 2-3 attempts per problem
- Strategy banning in ~15-20% of cases
- Catches edge cases and constraint violations

**Key Metrics to Report:**
- Absolute improvement: +5-15 percentage points
- Relative improvement: +10-20%
- Bugs caught by Verifier: ~10-20 cases
- Strategy banning effectiveness: ~5-10 cases

## 🎯 Success Criteria

The launch is successful if:

- [ ] Benchmark runs without errors
- [ ] CMVK outperforms baseline (even by small margin)
- [ ] At least 5 examples of Verifier catching Generator bugs
- [ ] At least 3 examples of strategy banning working
- [ ] Results are reproducible
- [ ] Visualizer provides clear examples for paper

## 📝 Post-Launch

After successful run:

1. Archive results:
   ```bash
   mkdir -p experiments/archive/run_YYYYMMDD/
   cp experiments/results/* experiments/archive/run_YYYYMMDD/
   cp logs/traces/* experiments/archive/run_YYYYMMDD/traces/
   ```

2. Commit results to repository:
   ```bash
   git add PAPER.md README.md
   git commit -m "Add experimental results from full HumanEval benchmark"
   git push
   ```

3. Prepare publication materials:
   - Update paper with results
   - Create presentation slides
   - Prepare demo for talks
   - Write blog post

## 🔧 Troubleshooting

### API Errors
- Check API keys are set correctly
- Verify API credits are available
- Check rate limits (may need to add delays)

### Low Performance
- Verify prompts in `config/prompts/`
- Check if models are using latest versions
- Review failed cases in traces

### Memory Issues
- Run in batches if needed
- Use smaller dataset for testing
- Clear cache between runs

## 📚 Additional Resources

- Full documentation: `README.md`
- Research paper draft: `PAPER.md`
- Architecture details: `ARCHITECTURE.md`
- Feature documentation: `FEATURE_3_TRACEABILITY.md`, `NEW_FEATURES.md`

## 🎉 Ready to Launch!

Once all pre-launch checklist items are complete:

```bash
# THE MOMENT OF TRUTH
python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_full.json
```

Good luck! 🚀
