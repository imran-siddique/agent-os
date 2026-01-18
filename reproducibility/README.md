# Reproducibility Guide

This directory contains all resources needed to reproduce the experiments and results reported in the Agent Control Plane research.

## Contents

1. **`hardware_specs.md`** - Hardware and software environment specifications
2. **`seeds.json`** - Random seeds used for all experiments
3. **`commands.md`** - Exact commands to reproduce all experiments
4. **`requirements_frozen.txt`** - Frozen dependency versions
5. **`docker_config/`** - Docker configuration for reproducible environment
6. **`experiment_configs/`** - Configuration files for each experiment

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

## Timing Expectations

| Experiment | Expected Duration | Output Size |
|------------|------------------|-------------|
| Comparative Study | ~2 minutes | ~50KB CSV |
| Full Ablation Suite | ~15 minutes | ~500KB CSV |
| Multi-Agent RAG | ~5 minutes | ~100KB JSON |
| Long-Horizon Purge | ~10 minutes | ~200KB JSON |

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
