# Appendix: Supplementary Materials

This appendix contains detailed reproducibility information, full ablation tables, and additional experimental data.

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
bash reproducibility/run_all_experiments.sh
```

---

## Appendix C: Statistical Methods

**Test Used**: Welch's t-test (two-sample, unequal variances)

**Correction**: Bonferroni adjustment for 6 comparisons (α = 0.05/6 = 0.0083)

**Effect Size**: Cohen's d with interpretation (small: 0.2, medium: 0.5, large: 0.8)

```python
from scipy import stats
import numpy as np

def compute_stats(full_results, ablation_results):
    t_stat, p_value = stats.ttest_ind(full_results, ablation_results, equal_var=False)
    pooled_std = np.sqrt((np.std(full_results)**2 + np.std(ablation_results)**2) / 2)
    cohens_d = abs((np.mean(ablation_results) - np.mean(full_results)) / pooled_std)
    return {'p_value': p_value, 'cohens_d': cohens_d}
```

---

## Appendix D: Hardware & Environment

| Component | Specification |
|-----------|---------------|
| CPU | Intel i7-12700K (12 cores, 3.6GHz) |
| RAM | 32GB DDR4-3200 |
| GPU | NVIDIA RTX 3080 (10GB VRAM) |
| OS | Ubuntu 22.04 LTS |

**Cloud Alternatives**: AWS g5.xlarge (~$1.00/hr), GCP n1-standard-4 + T4 (~$0.75/hr)

---

## Appendix E: Cost Estimates

| Experiment | Prompts | Est. Cost |
|------------|---------|-----------|
| Red-Team Safety | 60 | $0.15-0.25 |
| Ablation Suite | 2,100 | $5-8 |
| Full Benchmark | ~2,500 | $8-12 |

---

## Appendix F: Raw Data by Seed

```
Configuration    | Seed 42 | Seed 123 | Seed 456 | Seed 789 | Seed 1024
-----------------|---------|----------|----------|----------|-----------
Full Kernel      | 0.00%   | 0.00%    | 0.00%    | 0.00%    | 0.00%
No PolicyEngine  | 38.33%  | 41.67%   | 40.00%   | 43.33%   | 36.67%
No ConstraintGraphs | 3.33% | 5.00%   | 3.33%    | 1.67%    | 3.33%
```

---

## Appendix G: Dataset Details

| Category | Count | Description |
|----------|-------|-------------|
| Direct Violations | 15 | Explicit harmful requests |
| Prompt Injections | 15 | Embedded malicious instructions |
| Contextual Confusion | 15 | Ambiguous/edge cases |
| Valid Requests | 15 | Benign baseline |
| **Total** | **60** | — |

**Access**: [HuggingFace](https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60)

---

## Appendix H: Limitations

1. **Dataset scope**: Synthetic red-team prompts; real-world attacks may differ
2. **Modality**: Primarily text/tool agents; vision/audio needs more evaluation
3. **Baselines**: Compared against no-governance only
4. **LLM stochasticity**: Averaged over 5 seeds; production variance may be higher

See `../reproducibility/LIMITATIONS.md` for detailed discussion.

---

*Last updated: January 2026 | Version 1.1.0*
