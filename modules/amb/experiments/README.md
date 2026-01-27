# Experiments Directory

This directory contains reproducible experiments and benchmarks for AMB (Agent Message Bus).

## Quick Start

```bash
# Run full benchmark suite
python reproduce_results.py

# Run with custom parameters
python reproduce_results.py --seed 42 --iterations 500

# Run with custom output file
python reproduce_results.py --output my_results.json
```

## Files

- `reproduce_results.py` - Main benchmark script with reproducible experiments
- `results.json` - Output from benchmark runs (generated)

## Benchmarks Included

1. **Publish Latency (Fire & Forget)** - Measures raw publish speed without confirmation
2. **Publish Latency (With Confirmation)** - Measures publish speed with broker acknowledgment
3. **End-to-End Pub/Sub** - Measures complete message delivery latency
4. **Request-Response** - Measures round-trip time for request-response pattern
5. **Subscriber Fanout** - Measures scaling with multiple concurrent subscribers

## Reproducibility

All experiments use a configurable random seed (default: 42) to ensure reproducible results across runs. Results are saved in JSON format with full metadata including:

- Timestamp
- Python version
- Platform
- Configuration used
- Individual benchmark results with statistics

## Citation

If you use these benchmarks in your research, please cite:

```bibtex
@software{amb2024,
  author = {Siddique, Imran},
  title = {AMB: Agent Message Bus},
  year = {2024},
  url = {https://github.com/imran-siddique/amb}
}
```
