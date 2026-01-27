# ATR Experiments

This folder contains reproducibility scripts and experiment results for the Agent Tool Registry.

## Structure

```
experiments/
├── README.md                 # This file
├── reproduce_results.py      # Main reproducibility script
├── results/                  # Output directory for experiment results
│   └── .gitkeep
└── configs/                  # Experiment configurations
    └── default.json
```

## Running Experiments

### Quick Start

```bash
# Run default experiment suite
python experiments/reproduce_results.py

# Run with custom seed for reproducibility
python experiments/reproduce_results.py --seed 42

# Run specific experiment
python experiments/reproduce_results.py --experiment registration_benchmark

# Save results to custom location
python experiments/reproduce_results.py --output experiments/results/my_run.json
```

### Available Experiments

1. **registration_benchmark**: Measures tool registration latency
2. **discovery_benchmark**: Measures tool discovery/search performance
3. **schema_conversion**: Tests OpenAI/Anthropic schema generation
4. **full_suite**: Runs all experiments

## Results Format

Results are saved as JSON with the following structure:

```json
{
  "metadata": {
    "timestamp": "2026-01-23T10:00:00Z",
    "atr_version": "0.1.0",
    "python_version": "3.11.0",
    "seed": 42
  },
  "experiments": {
    "registration_benchmark": {
      "metrics": {...},
      "duration_seconds": 1.23
    }
  }
}
```

## Reproducing Paper Results

To reproduce the results from the paper:

```bash
python experiments/reproduce_results.py --seed 42 --experiment full_suite
```
