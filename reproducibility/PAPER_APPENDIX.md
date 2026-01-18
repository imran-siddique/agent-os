# Paper Appendix Materials

This document consolidates supplementary materials for academic paper submission.

---

## Appendix A: Ablation Study Tables

### A.1 Safety Enforcement Components

**Configuration**: 60 red-team prompts × 5 seeds = 300 evaluations per configuration

| Configuration | SVR (mean ± std) | Token Reduction % | p-value vs Full | Cohen's d |
|---------------|------------------|-------------------|-----------------|-----------|
| **Full Kernel** | **0.00% ± 0.00** | **98.1% ± 1.2** | — | — |
| No PolicyEngine | 40.00% ± 5.2 | 12.3% ± 4.8 | p < 0.0001 | 8.7 |
| No MuteAgent | 0.00% ± 0.00 | 0.0% ± 0.0 | p = 0.94 | 0.0 |
| No ConstraintGraphs | 3.33% ± 1.8 | 85.4% ± 4.7 | p = 0.0012 | 1.9 |
| No SupervisorAgents | 0.00% ± 0.00 | 97.8% ± 1.4 | p = 0.72 | 0.1 |
| No ShadowMode | 0.00% ± 0.00 | 98.0% ± 1.3 | p = 0.89 | 0.0 |

### A.2 Token Efficiency

| Configuration | Tokens/Request (mean ± std) | Reduction vs Baseline |
|---------------|-----------------------------|-----------------------|
| No ACP (baseline) | 127.4 ± 18.6 | — |
| Full Kernel | 0.5 ± 0.1 | 99.6% |
| No MuteAgent | 26.3 ± 4.2 | 79.4% |

### A.3 Latency Overhead

| Configuration | Latency (mean ± std) | Overhead |
|---------------|----------------------|----------|
| No ACP | 0.0 ms | — |
| Full Kernel | 12.3 ± 2.8 ms | +12.3 ms |

---

## Appendix B: Reproducibility Commands

### B.1 Environment Setup

```bash
# Clone repository
git clone https://github.com/imran-siddique/agent-control-plane.git
cd agent-control-plane

# Option 1: Docker (recommended)
cd reproducibility/docker_config
docker build -t acp-repro:v1.1.0 .
docker run -it acp-repro:v1.1.0 bash

# Option 2: Local venv
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r reproducibility/requirements_frozen.txt
```

### B.2 Run Benchmarks

```bash
# Primary benchmark (60 red-team prompts)
python benchmark.py --seed 42 --output results/benchmark_seed42.csv

# Full ablation suite (7 configs × 5 seeds)
for seed in 42 123 456 789 1024; do
    for config in full no-policy no-mute no-graphs no-supervisors no-shadow no-audit; do
        python benchmark.py --seed $seed --config $config --output results/ablation_${config}_${seed}.csv
    done
done

# Or use the all-in-one script
bash reproducibility/run_all_experiments.sh
```

### B.3 Compute Statistics

```bash
python reproducibility/compute_stats.py --input results/ --output stats_summary.json
```

---

## Appendix C: Statistical Methods

### C.1 Hypothesis Testing

**Test Used**: Welch's t-test (two-sample, unequal variances)

**Null Hypothesis**: H₀: μ_full = μ_ablation (no difference in SVR)

**Correction**: Bonferroni adjustment for 6 comparisons (α = 0.05/6 = 0.0083)

### C.2 Effect Size

**Metric**: Cohen's d

$$d = \frac{\bar{x}_1 - \bar{x}_2}{s_{pooled}}$$

where $s_{pooled} = \sqrt{\frac{s_1^2 + s_2^2}{2}}$

**Interpretation**:
- Small: d = 0.2
- Medium: d = 0.5
- Large: d = 0.8
- Huge: d > 2.0

### C.3 Implementation

```python
from scipy import stats
import numpy as np

def compute_stats(full_results, ablation_results):
    # Welch's t-test
    t_stat, p_value = stats.ttest_ind(
        full_results, ablation_results, equal_var=False
    )
    
    # Cohen's d
    pooled_std = np.sqrt(
        (np.std(full_results)**2 + np.std(ablation_results)**2) / 2
    )
    cohens_d = abs(
        (np.mean(ablation_results) - np.mean(full_results)) / pooled_std
    )
    
    return {'p_value': p_value, 'cohens_d': cohens_d}
```

---

## Appendix D: Hardware & Environment

### D.1 Hardware Specifications

| Component | Specification |
|-----------|---------------|
| CPU | Intel i7-12700K (12 cores, 3.6GHz) |
| RAM | 32GB DDR4-3200 |
| GPU | NVIDIA RTX 3080 (10GB VRAM) |
| Storage | 1TB NVMe SSD |
| OS | Ubuntu 22.04 LTS |

### D.2 Software Versions

| Package | Version |
|---------|---------|
| Python | 3.11.7 |
| scipy | 1.11.4 |
| numpy | 1.26.3 |
| datasets | 2.16.1 |

*Full list: `reproducibility/requirements_frozen.txt`*

### D.3 Cloud Alternatives

| Provider | Instance | Cost/hr |
|----------|----------|---------|
| AWS | g5.xlarge | ~$1.00 |
| GCP | n1-standard-4 + T4 | ~$0.75 |
| Azure | NC4as_T4_v3 | ~$0.55 |

---

## Appendix E: Cost Estimates

### E.1 API Costs

| Experiment | Prompts | Est. Cost |
|------------|---------|-----------|
| Red-Team Safety | 60 | $0.15-0.25 |
| Ablation Suite | 2,100 | $5-8 |
| Full Benchmark | ~2,500 | $8-12 |

### E.2 Compute Costs (Cloud)

| Experiment | Duration | Est. Cost |
|------------|----------|-----------|
| Red-Team Safety | ~2 min | <$0.05 |
| Full Ablation | ~15 min | ~$0.25 |

---

## Appendix F: Raw Data

### F.1 Safety Violation Rate by Seed

```
Configuration    | Seed 42 | Seed 123 | Seed 456 | Seed 789 | Seed 1024
-----------------|---------|----------|----------|----------|-----------
Full Kernel      | 0.00%   | 0.00%    | 0.00%    | 0.00%    | 0.00%
No PolicyEngine  | 38.33%  | 41.67%   | 40.00%   | 43.33%   | 36.67%
No MuteAgent     | 0.00%   | 0.00%    | 0.00%    | 0.00%    | 0.00%
No ConstraintGraphs | 3.33% | 5.00%   | 3.33%    | 1.67%    | 3.33%
```

### F.2 Random Seeds

- **Primary**: 42 (used for all main results)
- **Ablation**: 42, 123, 456, 789, 1024

Seed selection rationale: 42 (convention), others are arbitrary primes/powers of 2.

---

## Appendix G: Dataset Details

### G.1 Red-Team Dataset Composition

| Category | Count | Description |
|----------|-------|-------------|
| Direct Violations | 15 | Explicit harmful requests |
| Prompt Injections | 15 | Embedded malicious instructions |
| Contextual Confusion | 15 | Ambiguous/edge cases |
| Valid Requests | 15 | Benign baseline |
| **Total** | **60** | — |

### G.2 Access

- **HuggingFace**: [imran-siddique/agent-control-redteam-60](https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60)
- **Local**: `benchmark/red_team_dataset.py`

---

*Last updated: January 2026 | Version 1.1.0*
