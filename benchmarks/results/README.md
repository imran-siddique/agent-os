# Benchmark Results

This directory stores benchmark results and performance metrics.

## Structure

```
results/
├── README.md                    # This file
├── baseline/                    # Baseline comparison results
│   └── .gitkeep
├── ablation/                    # Ablation study results
│   └── .gitkeep
└── performance/                 # Performance metrics
    └── .gitkeep
```

## Result Format

Benchmark results should be stored as JSON files with timestamps:

```json
{
  "timestamp": "2026-01-21T00:00:00Z",
  "version": "0.1.0",
  "corpus": "sample_corpus",
  "metrics": {
    "precision_at_5": 0.82,
    "ndcg_at_10": 0.78,
    "query_latency_p95_ms": 45,
    "context_token_efficiency": 0.71
  },
  "config": {
    "time_decay_enabled": true,
    "structure_aware": true,
    "metadata_injection": true
  }
}
```

## Viewing Results

Use the visualization scripts:

```bash
# Generate plots from results
python benchmarks/visualize_results.py --results-dir benchmarks/results/

# Compare multiple runs
python benchmarks/compare_runs.py \
    --run1 results/baseline/2026-01-15.json \
    --run2 results/baseline/2026-01-21.json
```

## Publishing Results

When publishing results in papers or reports:

1. Include full configuration details
2. Specify hardware and environment
3. Provide statistical significance tests
4. Document any deviations from defaults

## Results Archive

Historical results are archived in Git to track performance over time. Do not delete old results unless they are clearly erroneous.
