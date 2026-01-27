# Exact Commands for Reproducibility

This document contains the **exact commands** used to generate all results in the Agent Control Plane research.

## Prerequisites

```bash
# Clone repository
git clone https://github.com/imran-siddique/agent-control-plane.git
cd agent-control-plane

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install exact dependencies
pip install -r reproducibility/requirements_frozen.txt

# Set environment variables for determinism
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
```

---

## Main Experiments

### 1. Comparative Safety Study

**Description**: Compare baseline prompt-based safety vs Control Plane governance.

**Command**:
```bash
python benchmark.py \
  --seed 42 \
  --output results/comparative_study.csv \
  --summary results/comparative_summary.csv
```

**Expected Duration**: ~2 minutes

**Expected Output Files**:
- `results/comparative_study.csv` - Detailed per-prompt results
- `results/comparative_summary.csv` - Aggregate metrics

**Expected Results**:
```
Safety Violation Rate (Baseline): 26.67%
Safety Violation Rate (Control Plane): 0.00%
Token Efficiency: 98.1% reduction
```

---

### 2. Ablation Study (Full System Baseline)

**Command**:
```bash
python examples/ablation_study.py \
  --config full \
  --seed 42 \
  --output results/ablation_full.csv
```

**Expected Results**:
- SVR: 0.00%
- Tokens: 0.5 ± 0.02
- Latency: 0.020 ± 0.001 ms

---

### 3. Ablation Study (Without Mute Agent)

**Command**:
```bash
python examples/ablation_study.py \
  --config no-mute \
  --seed 42 \
  --output results/ablation_no_mute.csv
```

**Expected Results**:
- SVR: 0.00% (no change)
- Tokens: 26.3 ± 1.2 (+5160%)
- Latency: 0.030 ± 0.002 ms (+50%)

---

### 4. Ablation Study (Without Constraint Graphs)

**Command**:
```bash
python examples/ablation_study.py \
  --config no-graphs \
  --seed 42 \
  --output results/ablation_no_graphs.csv
```

**Expected Results**:
- SVR: 3.33% (+3.33%)
- Tokens: 0.5 ± 0.02 (no change)
- Latency: 0.018 ± 0.001 ms (-10%)

---

### 5. Ablation Study (Without Supervisors)

**Command**:
```bash
python examples/ablation_study.py \
  --config no-supervisors \
  --seed 42 \
  --output results/ablation_no_supervisors.csv
```

**Expected Results**:
- SVR: 0.00% (no change in single-agent tests)
- Tokens: 0.5 ± 0.02 (no change)
- Latency: 0.019 ± 0.001 ms (-5%)

---

### 6. Ablation Study (Without Policy Engine)

**Command**:
```bash
python examples/ablation_study.py \
  --config no-policy \
  --seed 42 \
  --output results/ablation_no_policy.csv
```

**Expected Results**:
- SVR: 40.00% (+40%, catastrophic)
- Tokens: 26.3 ± 1.2 (+5160%)
- Latency: 0.030 ± 0.002 ms (+50%)

---

### 7. Ablation Study (Without Flight Recorder)

**Command**:
```bash
python examples/ablation_study.py \
  --config no-audit \
  --seed 42 \
  --output results/ablation_no_audit.csv
```

**Expected Results**:
- SVR: 0.00% (no change)
- Tokens: 0.5 ± 0.02 (no change)
- Latency: 0.015 ± 0.001 ms (-25%, faster without logging)

---

### 8. Ablation Study (Without Sandboxing)

**Command**:
```bash
python examples/ablation_study.py \
  --config no-sandbox \
  --seed 42 \
  --output results/ablation_no_sandbox.csv
```

**Expected Results**:
- SVR: 0.00% (no change)
- Tokens: 0.5 ± 0.02 (no change)
- Latency: 0.018 ± 0.001 ms (-10%)

---

### 9. Statistical Analysis (5 Replications)

**Description**: Run each ablation 5 times with different seeds for statistical analysis.

**Command**:
```bash
# Run batch script for all seeds
bash reproducibility/run_ablation_batch.sh
```

**Or manually**:
```bash
for seed in 42 123 456 789 1024; do
  for config in full no-mute no-graphs no-supervisors no-policy no-audit no-sandbox; do
    python examples/ablation_study.py \
      --config $config \
      --seed $seed \
      --output results/ablation_${config}_seed${seed}.csv
  done
done

# Aggregate results
python reproducibility/aggregate_results.py \
  --input-dir results/ \
  --output results/statistical_summary.csv
```

**Expected Duration**: ~15 minutes total (7 configs × 5 seeds)

---

## New Experiments

### 10. Governed Multi-Agent RAG Chain

**Description**: Tests coordination of multiple agents under governance constraints with retrieval-augmented generation.

**Command**:
```bash
python experiments/multi_agent_rag.py \
  --seed 42 \
  --config reproducibility/experiment_configs/rag_config.json \
  --output results/multi_agent_rag.json
```

**Configuration** (`rag_config.json`):
```json
{
  "num_agents": 3,
  "agent_roles": ["retriever", "processor", "validator"],
  "rag_queries": 10,
  "vector_store": "faiss",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "governance_level": "strict",
  "max_iterations": 5
}
```

**Expected Results**:
- All agents respect governance constraints
- Zero unauthorized data access
- Successful RAG chain completion in 5-10 iterations
- Audit trail for all agent actions

**Expected Duration**: ~5 minutes

---

### 11. Long-Horizon Task with Purge

**Description**: Tests agent behavior on long-running tasks with periodic state purging for safety.

**Command**:
```bash
python experiments/long_horizon_purge.py \
  --seed 42 \
  --config reproducibility/experiment_configs/purge_config.json \
  --output results/long_horizon_purge.json
```

**Configuration** (`purge_config.json`):
```json
{
  "task_steps": 100,
  "purge_interval": 10,
  "purge_strategy": "lru",
  "retention_threshold": 0.8,
  "safety_checks": true,
  "checkpoint_frequency": 5
}
```

**Expected Results**:
- Task completion in 100 steps
- Memory purged 10 times (every 10 steps)
- No safety violations during purges
- Successful state recovery after each purge

**Expected Duration**: ~10 minutes

---

## Dataset Upload

### 12. Upload Dataset to Hugging Face

**Command**:
```bash
# Login to Hugging Face (one-time)
huggingface-cli login

# Upload dataset
python scripts/upload_dataset_to_hf.py \
  --repo-id imran-siddique/agent-control-redteam-60
```

**Result**: Dataset available at https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60

---

## Verification

### 13. Verify Reproducibility

**Command**:
```bash
python reproducibility/verify_results.py \
  --your-results results/comparative_study.csv \
  --reference results/reference_comparative_study.csv \
  --tolerance 0.01
```

**Expected Output**:
```
✓ Safety Violation Rate matches (0.00% ± 0.01%)
✓ Token efficiency matches (0.5 ± 0.05 tokens)
✓ All 60 test cases passed
✓ Results are reproducible within tolerance
```

---

## Batch Scripts

### 14. Run All Experiments

**Command**:
```bash
bash reproducibility/run_all_experiments.sh
```

**What it does**:
1. Runs comparative study
2. Runs all 7 ablation configurations
3. Runs statistical replications (5 seeds)
4. Runs new experiments (RAG, long-horizon)
5. Aggregates results
6. Generates plots and tables

**Expected Duration**: ~30 minutes total

**Output Directory**: `results/`

---

## Docker Commands

### 15. Run in Docker Container

**Build Image**:
```bash
cd reproducibility/docker_config
docker build -t acp-reproducibility:v1.1.0 .
```

**Run Experiments**:
```bash
docker run -it --rm \
  -v $(pwd)/results:/workspace/results \
  acp-reproducibility:v1.1.0 \
  bash -c "source venv/bin/activate && bash reproducibility/run_all_experiments.sh"
```

**Interactive Shell**:
```bash
docker run -it --rm acp-reproducibility:v1.1.0 bash
```

---

## GPU-Enabled Commands (Optional, for ML Safety Features)

### 16. Run with GPU for ML Safety

**Command**:
```bash
CUDA_VISIBLE_DEVICES=0 python benchmark.py \
  --seed 42 \
  --enable-ml-safety \
  --jailbreak-detection \
  --anomaly-detection \
  --output results/comparative_study_ml.csv
```

**Note**: Core results (SVR=0%) are identical with or without GPU. ML features add:
- Jailbreak detection confidence scores
- Anomaly detection alerts
- Behavioral analysis insights

---

## Cleanup

### 17. Clean Generated Files

**Command**:
```bash
# Remove all result files
rm -rf results/*.csv results/*.json

# Remove cache
rm -rf __pycache__ .pytest_cache

# Remove virtual environment
deactivate
rm -rf venv/
```

---

## Performance Tuning (Advanced)

### 18. Disable CPU Frequency Scaling

**For consistent timing benchmarks**:

```bash
# Check current governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Set to performance mode (requires sudo)
sudo cpupower frequency-set --governor performance

# Disable turbo boost
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo

# After experiments, restore
sudo cpupower frequency-set --governor powersave
echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
```

**Note**: This is optional and only affects latency measurements (~5% variance). Safety results are identical.

---

## Troubleshooting Commands

### Check Environment

```bash
# Verify Python version
python --version  # Should be 3.10.x

# Verify dependencies
pip freeze | grep -E "(numpy|pandas|torch)"

# Check CUDA (if using ML features)
nvidia-smi

# Check disk space
df -h

# Check memory
free -h
```

### Debug Failed Experiments

```bash
# Run with verbose logging
python benchmark.py --seed 42 --verbose --log-level DEBUG

# Run single test case
python benchmark.py --seed 42 --test-id 0 --verbose

# Validate dataset
python benchmark/red_team_dataset.py
```

---

**Last Updated**: January 2026  
**Command Set Version**: 1.1.0
