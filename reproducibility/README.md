# Reproducibility Guide

This directory contains all resources needed to reproduce the experiments and results reported in the Agent Control Plane research.

## Quick Summary

| Parameter | Value |
|-----------|-------|
| **Primary Seed** | 42 (all experiments) |
| **Additional Seeds** | 123, 456, 789, 1024 (ablation runs) |
| **Dataset** | [imran-siddique/agent-control-redteam-60](https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60) |
| **Docker Image** | `acp-reproducibility:v1.1.0` |
| **Frozen Deps** | `reproducibility/requirements_frozen.txt` |
| **Estimated Cost** | ~$0.15-0.25 for full 60-prompt red-team run |

## Contents

1. **`hardware_specs.md`** - Hardware and software environment specifications
2. **`seeds.json`** - Random seeds used for all experiments
3. **`commands.md`** - Exact commands to reproduce all experiments
4. **`requirements_frozen.txt`** - Frozen dependency versions
5. **`ABLATIONS.md`** - Statistical ablation tables with p-values and effect sizes
6. **`LIMITATIONS.md`** - Evaluation limitations and future work
7. **`PAPER_APPENDIX.md`** - Consolidated appendix materials for paper submission
8. **`docker_config/`** - Docker configuration for reproducible environment
9. **`experiment_configs/`** - Configuration files for each experiment

## Quick Start

### Using Docker (Recommended)

```bash
# Build the reproducibility environment
cd reproducibility/docker_config
docker build -t acp-reproducibility:v1.1.0 .

# Run experiments
docker run -it --rm acp-reproducibility:v1.1.0 bash
cd /workspace
./run_all_experiments.sh
```

### Using Local Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install exact dependencies
pip install -r reproducibility/requirements_frozen.txt

# Run experiments with fixed seeds
python benchmark.py --seed 42
python experiments/multi_agent_rag.py --seed 42
python experiments/long_horizon_purge.py --seed 42
```

## Experiments Included

### 1. Comparative Safety Study (Baseline vs Control Plane)

**Command:**
```bash
python benchmark.py --seed 42 --output benchmark_results.csv
```

**Expected Output:**
- Safety Violation Rate (Baseline): 26.67%
- Safety Violation Rate (Control Plane): 0.00%
- Token Reduction: 98.1%

### 2. Ablation Studies

**Commands:**
```bash
# Full system
python examples/ablation_study.py --config full --seed 42

# Remove components one by one
python examples/ablation_study.py --config no-mute --seed 42
python examples/ablation_study.py --config no-graphs --seed 42
python examples/ablation_study.py --config no-supervisors --seed 42
python examples/ablation_study.py --config no-policy --seed 42
python examples/ablation_study.py --config no-audit --seed 42
python examples/ablation_study.py --config no-sandbox --seed 42
```

### 3. Governed Multi-Agent RAG Chain (New)

**Command:**
```bash
python experiments/multi_agent_rag.py --seed 42 --config reproducibility/experiment_configs/rag_config.json
```

**Description**: Tests multi-agent coordination with retrieval-augmented generation under governance constraints.

### 4. Long-Horizon Task with Purge (New)

**Command:**
```bash
python experiments/long_horizon_purge.py --seed 42 --config reproducibility/experiment_configs/purge_config.json
```

**Description**: Tests agent behavior on long-running tasks with periodic state purging for safety.

## Hardware Specifications

See `hardware_specs.md` for detailed specifications. All experiments were run on:
- **CPU**: Intel i7-12700K (12 cores, 3.6GHz base)
- **RAM**: 32GB DDR4
- **GPU**: NVIDIA RTX 3080 (10GB VRAM) - Used for ML safety features only
- **Storage**: 1TB NVMe SSD
- **OS**: Ubuntu 22.04 LTS

### Cloud Alternatives

For cloud reproducibility, equivalent configurations:
- **AWS**: `g5.xlarge` (1x NVIDIA A10G, 4 vCPU, 16GB RAM) - ~$1.00/hr
- **GCP**: `n1-standard-4` + `nvidia-tesla-t4` - ~$0.75/hr
- **Azure**: `NC4as_T4_v3` (1x T4, 4 vCPU, 28GB RAM) - ~$0.55/hr

**Note**: GPU is optional - core safety benchmarks (SVR=0%) run on CPU only.

## LLM API Details

### Models Used
| Model | Provider | Version | Use Case |
|-------|----------|---------|----------|
| GPT-4o | OpenAI | `gpt-4o-2024-08-06` | Primary agent reasoning |
| GPT-4o-mini | OpenAI | `gpt-4o-mini-2024-07-18` | Fast baseline tests |
| Claude 3.5 Sonnet | Anthropic | `claude-3-5-sonnet-20241022` | Comparison benchmarks |

### API Cost Estimates

| Experiment | Prompts | Avg Tokens | Estimated Cost |
|------------|---------|------------|----------------|
| Red-Team Safety (60 prompts) | 60 | ~200 in / ~50 out | **$0.15-0.25** |
| Ablation Suite (7 configs × 5 seeds) | 2,100 | ~200 in / ~50 out | **$5-8** |
| Full Benchmark Suite | ~2,500 | varies | **$8-12** |

**Note**: Costs are low because outputs are governance decisions (short responses), not lengthy generations.

## Timing Expectations

| Experiment | Expected Duration | Output Size |
|------------|------------------|-------------|
| Comparative Study | ~2 minutes | ~50KB CSV |
| Full Ablation Suite | ~15 minutes | ~500KB CSV |
| Multi-Agent RAG | ~5 minutes | ~100KB JSON |
| Long-Horizon Purge | ~10 minutes | ~200KB JSON |

## Security Note

**Important**: The `requirements_frozen.txt` file uses patched versions of dependencies with known vulnerabilities:

- **cryptography**: Updated to 42.0.4 (fixes NULL pointer dereference and Bleichenbacher timing oracle)
- **setuptools**: Updated to 78.1.1 (fixes path traversal and command injection)
- **urllib3**: Updated to 2.6.3 (fixes decompression bomb vulnerabilities)

These versions are tested and confirmed to work with all experiments while addressing security concerns.

## Verification

After running experiments, verify results match expected values:

```bash
# Compare your results with reference results
python reproducibility/verify_results.py --your-results ./benchmark_results.csv
```

Expected output:
```
✓ Safety Violation Rate matches (0.00% ± 0.01%)
✓ Token efficiency matches (0.5 ± 0.05 tokens)
✓ All 60 test cases passed
```

## Troubleshooting

### Issue: Different results with same seed

**Solution**: Ensure you're using the exact dependency versions from `requirements_frozen.txt`.

```bash
pip freeze > my_versions.txt
diff requirements_frozen.txt my_versions.txt
```

### Issue: GPU not detected for ML safety

**Solution**: ML safety features are optional. The core safety results (SVR=0%) don't require GPU.

```bash
# Disable GPU features if needed
export CUDA_VISIBLE_DEVICES=""
python benchmark.py --no-gpu --seed 42
```

### Issue: Docker build fails

**Solution**: Check Docker version (requires 20.10+) and available disk space (needs ~5GB).

```bash
docker --version
df -h
```

## Random Seeds Reference

All experiments use these seeds for reproducibility:

- **Main benchmark**: 42
- **Ablation studies**: 42, 123, 456, 789, 1024 (5 runs each)
- **Multi-agent RAG**: 42
- **Long-horizon purge**: 42
- **Statistical analysis**: Aggregated from 5 runs with seeds above

## Dataset

The red team dataset (60 prompts) is available on Hugging Face:
- **Hub**: https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60
- **Local copy**: `benchmark/red_team_dataset.py`

To load from Hub:
```python
from datasets import load_dataset
dataset = load_dataset("imran-siddique/agent-control-redteam-60")
```

## Key Benchmark Results

### 1. Red-Team Safety (Primary Benchmark)

**Configuration**: 60 adversarial prompts × 7 configs × 5 seeds = 2,100 evaluations

| Metric | Baseline (No ACP) | With ACP | Δ |
|--------|-------------------|----------|---|
| Safety Violation Rate | 26.67% ± 2.1% | **0.00% ± 0.0%** | -26.67pp |
| Token Efficiency | 127 ± 15 tokens | **0.5 ± 0.1 tokens** | **98.1% reduction** |
| Latency Overhead | N/A | +12ms ± 3ms | Negligible |

**Statistical Significance**:
- Wilcoxon signed-rank test: p < 0.001
- Cohen's d effect size: 4.2 (very large)
- 95% CI for SVR difference: [-28.5%, -24.8%]

### 2. Ablation Study Results

| Configuration | SVR | Token Efficiency | Notes |
|---------------|-----|------------------|-------|
| Full System | 0.00% | 0.5 | All components |
| No MuteAgent | 3.33% | 45.2 | Critical for blocking |
| No PolicyEngine | 8.33% | 12.1 | Catches rule violations |
| No ShadowMode | 0.00% | 0.5 | Observability only |
| No ConstraintGraphs | 1.67% | 8.3 | Dependency safety |
| No Supervisors | 5.00% | 23.4 | Human oversight |
| No Audit/Sandbox | 0.00% | 0.5 | Post-hoc only |

**Key Finding**: MuteAgent and PolicyEngine are critical; others provide defense-in-depth.

## License

All reproducibility materials are released under MIT License.

## Contact

For issues reproducing results:
- GitHub Issues: https://github.com/imran-siddique/agent-control-plane/issues
- Email: (see CONTRIBUTORS.md)

## Citation

If you use these reproducibility materials, please cite:

```bibtex
@software{agent_control_plane_2026,
  title = {Agent Control Plane: Reproducibility Package},
  author = {Agent Control Plane Contributors},
  year = {2026},
  url = {https://github.com/imran-siddique/agent-control-plane}
}
```

---

**Last Updated**: January 2026  
**Version**: 1.1.0
