#!/bin/bash
# Run all experiments for reproducibility

set -e  # Exit on error

echo "========================================================================"
echo "Running All Agent Control Plane Experiments"
echo "========================================================================"
echo ""

# Set environment variables
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# Create results directory
mkdir -p results

echo "1. Running Comparative Safety Study..."
python benchmark.py --seed 42 --output results/comparative_study.csv

echo ""
echo "2. Running Multi-Agent RAG Experiment..."
python experiments/multi_agent_rag.py --seed 42 \
  --config reproducibility/experiment_configs/rag_config.json \
  --output results/multi_agent_rag.json

echo ""
echo "3. Running Long-Horizon Purge Experiment..."
python experiments/long_horizon_purge.py --seed 42 \
  --config reproducibility/experiment_configs/purge_config.json \
  --output results/long_horizon_purge.json

echo ""
echo "========================================================================"
echo "All experiments completed successfully!"
echo "========================================================================"
echo ""
echo "Results saved to:"
echo "  - results/comparative_study.csv"
echo "  - results/multi_agent_rag.json"
echo "  - results/long_horizon_purge.json"
echo ""
echo "To verify reproducibility, compare with reference results in"
echo "reproducibility/reference_results/"
