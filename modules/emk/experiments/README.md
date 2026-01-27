# Experiments

This folder contains reproducible experiments for the EMK (Episodic Memory Kernel) project.

## Running Experiments

```bash
# Basic run (100 episodes, seed=42)
python experiments/reproduce_results.py

# Custom configuration
python experiments/reproduce_results.py --episodes 1000 --seed 123

# Custom output file
python experiments/reproduce_results.py --output my_results.json
```

## Output

Results are saved to `experiments/results.json` with the following structure:

```json
{
  "emk_version": "0.1.0",
  "python_version": "3.11.x",
  "timestamp": "2026-01-23T...",
  "seed": 42,
  "num_episodes": 100,
  "benchmarks": {
    "episode_creation": { ... },
    "storage_write": { ... },
    "retrieval": { ... },
    "indexer": { ... }
  },
  "system_info": { ... }
}
```

## Benchmarks

| Benchmark | Description |
|-----------|-------------|
| `episode_creation` | Time to create Episode objects with ID generation |
| `storage_write` | Time to write episodes to FileAdapter |
| `retrieval` | Time to retrieve episodes with filters |
| `indexer` | Time to generate tags and search text |

## Reproducibility

All experiments use a fixed random seed for reproducibility. To reproduce results:

1. Use the same seed value
2. Use the same Python version
3. Use the same emk version

```bash
# Reproduce exact results
python experiments/reproduce_results.py --seed 42 --episodes 100
```
