# Experiments Directory

This folder contains reproducibility scripts for the CaaS paper.

## Quick Start

```bash
# Run the main reproducibility script
python experiments/reproduce_results.py

# Run with custom seed
python experiments/reproduce_results.py --seed 42 --output experiments/results.json
```

## Files

- `reproduce_results.py` - Main reproducibility script for paper claims
- `results.json` - Output results (generated after running)

## Full Benchmarks

For comprehensive benchmarks including the full corpus evaluation, see:

```bash
python benchmarks/run_evaluation.py --corpus benchmarks/data/sample_corpus/
```

## Paper Claims

The reproducibility script validates the following claims from the paper:

| Claim | Metric | Expected |
|-------|--------|----------|
| Sub-millisecond routing | Router latency | < 0.01 ms |
| High routing accuracy | Heuristic accuracy | > 90% |
| Fast context operations | Triad add operations | < 0.1 ms/item |

## Requirements

```bash
pip install caas-core numpy
```
