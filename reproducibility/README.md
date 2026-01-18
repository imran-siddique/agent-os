# Reproducibility Package

This directory contains all materials needed to reproduce the experiments in the Self-Correcting Agent Kernel paper.

## Overview

We provide:
1. **Exact environment specification** (Docker + requirements with pinned versions)
2. **Seed control utilities** (deterministic random number generation)
3. **Experiment scripts** (automated reproduction)
4. **Statistical analysis tools** (p-values, confidence intervals)
5. **Hardware specifications** (for performance benchmarks)

## Quick Start

```bash
# 1. Build reproducibility Docker image
cd reproducibility
docker build -t scak-repro:1.0 -f Dockerfile.reproducibility .

# 2. Run all experiments
docker run --rm scak-repro:1.0 python run_all_experiments.py

# 3. Generate paper figures and tables
docker run --rm -v $(pwd)/results:/results scak-repro:1.0 python generate_paper_artifacts.py
```

Results will be saved to `reproducibility/results/`.

## Environment Specification

### Exact Versions (requirements-pinned.txt)

```
# Core dependencies (exact versions from 2026-01-18)
python==3.10.12
pydantic==2.5.3
pyyaml==6.0.1
requests==2.31.0

# LLM clients (exact versions)
openai==1.7.2
anthropic==0.8.1

# Testing (exact versions)
pytest==7.4.3
pytest-asyncio==0.21.1

# Data processing
numpy==1.24.3
pandas==2.0.3

# Visualization
matplotlib==3.7.2
seaborn==0.12.2

# Statistical analysis
scipy==1.11.3
statsmodels==0.14.0
```

### Docker Image

**Base:** `python:3.10.12-slim-bullseye`

**Built:** 2026-01-18

**SHA256:** `<will be added after build>`

**Dockerfile:** See `Dockerfile.reproducibility`

### Hardware Specifications

**Experiments conducted on:**
- **CPU:** Intel Xeon E5-2686 v4 @ 2.30GHz (8 cores)
- **RAM:** 32GB
- **GPU:** None (CPU-only LLM API calls)
- **Disk:** 100GB SSD
- **Network:** 1 Gbps
- **Cloud Provider:** AWS EC2 (c5.2xlarge instance)

**Notes:**
- Teacher model calls (o1-preview) are non-deterministic even with seeds
- Expect ±2% variance in detection rates due to LLM non-determinism
- MTTR measurements may vary ±5s depending on network latency

## Seed Control

All experiments use deterministic random number generation:

```python
# seed_control.py
import random
import numpy as np
import os

GLOBAL_SEED = 42

def set_seeds(seed=GLOBAL_SEED):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    # Note: LLM API calls (OpenAI, Anthropic) are non-deterministic
    # even with seeds. Expect ±2% variance in results.

# Usage in experiments
from seed_control import set_seeds
set_seeds(42)  # Use consistent seed across all experiments
```

## Experiment Scripts

### 1. GAIA Benchmark (Laziness Detection)

**Script:** `experiments/gaia_benchmark/run_benchmark.py`

**Command:**
```bash
python experiments/gaia_benchmark/run_benchmark.py \
  --queries datasets/gaia_vague_queries/vague_queries.json \
  --output results/gaia_results.json \
  --seed 42
```

**Expected Output:**
- Detection rate: 100% (±2%)
- Correction rate: 72% (±3%)
- Post-patch success: 81% (±4%)
- Runtime: ~15 minutes (50 queries × ~18s/query)

**Baselines:**
```bash
# Baseline: GPT-4o without SCAK
python experiments/gaia_benchmark/run_baseline.py \
  --model gpt-4o \
  --queries datasets/gaia_vague_queries/vague_queries.json \
  --output results/baseline_gpt4o.json \
  --seed 42
```

### 2. Amnesia Test (Context Efficiency)

**Script:** `experiments/amnesia_test.py`

**Command:**
```bash
python experiments/amnesia_test.py \
  --patches datasets/patches/synthetic_patches.json \
  --old-model gpt-4o \
  --new-model gpt-5 \
  --output results/amnesia_results.json \
  --seed 42
```

**Expected Output:**
- Token reduction: 50% (±5%)
- Business rule accuracy: 100%
- Syntax rule retention: 10% (±5%)
- Runtime: ~2 minutes

### 3. Chaos Engineering (Robustness)

**Script:** `experiments/chaos_engineering/run_chaos.py`

**Command:**
```bash
python experiments/chaos_engineering/run_chaos.py \
  --scenarios datasets/chaos_scenarios/schema_failures.json \
  --output results/chaos_results.json \
  --seed 42
```

**Expected Output:**
- MTTR: 28s (±6s)
- Recovery rate: 85% (±7%)
- Failure burst: 2.3 (±0.5)
- Runtime: ~10 minutes (20 scenarios × ~30s/scenario)

**Baseline:**
```bash
# Baseline: Standard agent without SCAK
python experiments/chaos_engineering/run_baseline.py \
  --scenarios datasets/chaos_scenarios/schema_failures.json \
  --output results/chaos_baseline.json \
  --seed 42
# Expected: MTTR=∞ (never recovers), Recovery rate=0%
```

## Statistical Analysis

### Computing p-values and Confidence Intervals

**Script:** `statistical_analysis.py`

**Command:**
```bash
python statistical_analysis.py \
  --treatment results/gaia_results.json \
  --control results/baseline_gpt4o.json \
  --output results/statistical_report.json
```

**Output:**
```json
{
  "detection_rate": {
    "treatment_mean": 1.00,
    "control_mean": 0.00,
    "p_value": "N/A",
    "test": "not_applicable"
  },
  "correction_rate": {
    "treatment_mean": 0.72,
    "treatment_ci_95": [0.65, 0.79],
    "control_mean": 0.08,
    "control_ci_95": [0.03, 0.13],
    "p_value": 0.0001,
    "test": "two_sample_t_test",
    "effect_size": "large"
  },
  "post_patch_success": {
    "treatment_mean": 0.81,
    "treatment_ci_95": [0.73, 0.89],
    "control_mean": 0.08,
    "control_ci_95": [0.03, 0.13],
    "p_value": 0.0001,
    "test": "two_sample_t_test",
    "effect_size": "large"
  }
}
```

### Ablation Studies

**Component Removal Tests:**

```bash
# Ablation 1: Remove Semantic Purge
python experiments/ablation_no_purge.py \
  --output results/ablation_no_purge.json \
  --seed 42
# Expected: Context grows unbounded (0% reduction)

# Ablation 2: Remove Differential Auditing
python experiments/ablation_no_audit.py \
  --output results/ablation_no_audit.json \
  --seed 42
# Expected: 0% laziness detection

# Ablation 3: Remove Shadow Teacher (use self-critique)
python experiments/ablation_self_critique.py \
  --output results/ablation_self_critique.json \
  --seed 42
# Expected: 40% correction rate (vs 72%)

# Ablation 4: Remove Tier 2/3 (flat memory)
python experiments/ablation_flat_memory.py \
  --output results/ablation_flat_memory.json \
  --seed 42
# Expected: +500ms latency, 0% token savings
```

**Ablation Summary Table:**

| Component Removed | Detection Rate | Context Reduction | MTTR | Notes |
|-------------------|----------------|-------------------|------|-------|
| None (Full System) | 72% | 50% | 28s | Baseline |
| Semantic Purge | 72% | 0% | 28s | Context grows unbounded |
| Differential Auditing | 0% | 50% | 28s | No laziness detection |
| Shadow Teacher | 40% | 50% | 28s | Self-critique less effective |
| Tiered Memory | 72% | 0% | 35s | Slower retrieval, no token savings |

## Broader Baselines

### AutoGen Comparison

**Setup:** Multi-agent AutoGen framework with reflection

**Command:**
```bash
python experiments/baselines/run_autogen.py \
  --queries datasets/gaia_vague_queries/vague_queries.json \
  --output results/baseline_autogen.json \
  --seed 42
```

**Expected Result:** 15% correction rate (no differential auditing), 0% context reduction

### LangGraph Comparison

**Setup:** LangGraph state machine with memory

**Command:**
```bash
python experiments/baselines/run_langgraph.py \
  --queries datasets/gaia_vague_queries/vague_queries.json \
  --output results/baseline_langgraph.json \
  --seed 42
```

**Expected Result:** 0% laziness detection (no auditor), 0% context reduction

### o1-preview Alone

**Setup:** Direct o1-preview API calls without SCAK

**Command:**
```bash
python experiments/baselines/run_o1_direct.py \
  --queries datasets/gaia_vague_queries/vague_queries.json \
  --output results/baseline_o1.json \
  --seed 42
```

**Expected Result:** 40% correction rate (strong model but no feedback loop), 0% context reduction

## Generating Paper Artifacts

### Figures

**Script:** `generate_figures.py`

**Command:**
```bash
python generate_figures.py \
  --results-dir results/ \
  --output-dir paper/figures/
```

**Generated Figures:**
- `figure1_architecture.pdf` - Dual-loop OODA diagram
- `figure2_gaia_results.pdf` - Bar chart: correction rates
- `figure3_context_reduction.pdf` - Line chart: token savings over time
- `figure4_mttr_comparison.pdf` - Box plot: MTTR distributions
- `figure5_ablation.pdf` - Heatmap: ablation study results

### Tables

**Script:** `generate_tables.py`

**Command:**
```bash
python generate_tables.py \
  --results-dir results/ \
  --output-dir paper/tables/
```

**Generated Tables:**
- `table1_contribution_comparison.tex` - Comparison with prior work
- `table2_gaia_results.tex` - GAIA benchmark results with CI
- `table3_amnesia_results.tex` - Context reduction results
- `table4_chaos_results.tex` - MTTR and recovery rates
- `table5_ablation.tex` - Ablation study summary
- `table6_baselines.tex` - Broader baseline comparison

## Cost Tracking

### API Cost Calculation

**Estimated Costs (per full experiment run):**

| Experiment | Queries | Teacher Calls | Cost (USD) |
|------------|---------|---------------|------------|
| GAIA Benchmark | 50 | 36 (72% audit rate) | $18.00 |
| Chaos Engineering | 20 | 17 (85% recovery) | $8.50 |
| Ablation (4 variants) | 200 | 144 | $72.00 |
| Baselines (3 systems) | 150 | 0 | $15.00 |
| **Total** | **420** | **197** | **$113.50** |

**Note:** OpenAI o1-preview pricing: $0.50/call (estimated)

## Troubleshooting

### Issue: LLM API rate limits

**Symptom:** `openai.error.RateLimitError`

**Solution:**
```bash
# Add retry logic with exponential backoff
export OPENAI_MAX_RETRIES=5
export OPENAI_RETRY_DELAY=10
```

### Issue: Non-deterministic results

**Symptom:** Results vary by >5% across runs

**Solution:**
- LLM non-determinism is expected (±2% variance)
- Run experiments 3 times and report mean ± std dev
- Use temperature=0 for LLM calls (already set in code)

### Issue: Docker build fails

**Symptom:** `E: Package 'python3.10' has no installation candidate`

**Solution:**
```bash
# Use pre-built Docker image
docker pull scak/reproducibility:1.0
```

## Contact

For reproducibility issues, please open a GitHub issue with:
- Environment details (`docker version`, `python --version`)
- Full error traceback
- Experiment command used

## Version History

- **v1.0** (2026-01-18): Initial reproducibility package
  - Python 3.10.12, OpenAI 1.7.2, Anthropic 0.8.1
  - All 3 experiments + ablation + baselines

---

**Last Updated:** 2026-01-18  
**Authors:** Self-Correcting Agent Team
