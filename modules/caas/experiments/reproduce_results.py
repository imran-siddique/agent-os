#!/usr/bin/env python3
"""
CaaS Reproducibility Script.

This script provides a simple, reproducible way to run the CaaS benchmarks
and verify the results reported in the paper.

Usage:
    python experiments/reproduce_results.py
    python experiments/reproduce_results.py --seed 42 --output results.json

The script will:
    1. Set up a controlled environment with fixed random seed
    2. Run the core CaaS components against sample inputs
    3. Measure metrics (latency, accuracy, token efficiency)
    4. Save results to experiments/results.json

For full benchmark evaluation, see: benchmarks/run_evaluation.py

Requirements:
    pip install caas-core numpy

Author: Imran Siddique
License: MIT
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Add parent directory for imports if running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from caas import __version__ as CAAS_VERSION
    from caas.routing.heuristic_router import HeuristicRouter
    from caas.triad import ContextTriadManager
    from caas.decay import TimeDecayCalculator
    from caas.models import ModelTier

    CAAS_AVAILABLE = True
except ImportError as e:
    CAAS_AVAILABLE = False
    CAAS_VERSION = "unknown"
    print(f"Warning: CaaS not fully available ({e}). Running in demo mode.")


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_SEED = 42
DEFAULT_OUTPUT = "experiments/results.json"

# Sample queries for routing benchmark
SAMPLE_QUERIES = [
    # Greetings (should route to CANNED)
    "Hi",
    "Hello there",
    "Thanks!",
    "Ok",
    # Short queries (should route to FAST)
    "What is RAG?",
    "Define context window",
    "List the files",
    # Complex queries (should route to SMART)
    "Summarize the architecture of this system and explain the tradeoffs",
    "Analyze the performance implications of using vector similarity search",
    "Compare the Context Triad approach with traditional RAG systems",
    "Please provide a comprehensive review of the code structure",
]

# Expected routing results for accuracy calculation
EXPECTED_ROUTING = {
    "Hi": ModelTier.CANNED,
    "Hello there": ModelTier.CANNED,
    "Thanks!": ModelTier.CANNED,
    "Ok": ModelTier.CANNED,
    "What is RAG?": ModelTier.FAST,
    "Define context window": ModelTier.FAST,
    "List the files": ModelTier.FAST,
    "Summarize the architecture of this system and explain the tradeoffs": ModelTier.SMART,
    "Analyze the performance implications of using vector similarity search": ModelTier.SMART,
    "Compare the Context Triad approach with traditional RAG systems": ModelTier.SMART,
    "Please provide a comprehensive review of the code structure": ModelTier.SMART,
}


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class BenchmarkConfig:
    """Configuration for the benchmark run."""

    seed: int = DEFAULT_SEED
    n_iterations: int = 100
    warmup_iterations: int = 10


@dataclass
class MetricResult:
    """A single metric measurement."""

    name: str
    value: float
    std: Optional[float] = None
    unit: str = ""
    n_samples: int = 1


@dataclass
class ExperimentResults:
    """Complete experiment results."""

    timestamp: str
    caas_version: str
    python_version: str
    seed: int
    metrics: Dict[str, Any]
    config: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "caas_version": self.caas_version,
            "python_version": self.python_version,
            "seed": self.seed,
            "metrics": self.metrics,
            "config": self.config,
        }


# ============================================================================
# Benchmark Functions
# ============================================================================


def set_seed(seed: int) -> None:
    """Set random seed for reproducibility.

    Args:
        seed: Random seed value.
    """
    random.seed(seed)
    np.random.seed(seed)


def benchmark_router_latency(
    router: HeuristicRouter,
    queries: List[str],
    n_iterations: int = 100,
    warmup: int = 10,
) -> MetricResult:
    """Benchmark the heuristic router latency.

    Args:
        router: The HeuristicRouter instance.
        queries: List of queries to route.
        n_iterations: Number of timing iterations.
        warmup: Number of warmup iterations.

    Returns:
        MetricResult with latency statistics.
    """
    # Warmup
    for _ in range(warmup):
        for query in queries:
            router.route(query)

    # Timed iterations
    latencies = []
    for _ in range(n_iterations):
        for query in queries:
            start = time.perf_counter()
            router.route(query)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms

    latencies_arr = np.array(latencies)

    return MetricResult(
        name="router_latency",
        value=float(np.mean(latencies_arr)),
        std=float(np.std(latencies_arr)),
        unit="ms",
        n_samples=len(latencies),
    )


def benchmark_router_accuracy(
    router: HeuristicRouter,
    queries: List[str],
    expected: Dict[str, ModelTier],
) -> MetricResult:
    """Benchmark the heuristic router accuracy.

    Args:
        router: The HeuristicRouter instance.
        queries: List of queries to route.
        expected: Dictionary mapping queries to expected ModelTier.

    Returns:
        MetricResult with accuracy percentage.
    """
    correct = 0
    total = 0

    for query in queries:
        if query in expected:
            decision = router.route(query)
            if decision.model_tier == expected[query]:
                correct += 1
            total += 1

    accuracy = (correct / total * 100) if total > 0 else 0.0

    return MetricResult(
        name="router_accuracy",
        value=accuracy,
        unit="%",
        n_samples=total,
    )


def benchmark_context_triad(
    n_items: int = 100,
) -> Dict[str, MetricResult]:
    """Benchmark Context Triad operations.

    Args:
        n_items: Number of context items to add.

    Returns:
        Dictionary of MetricResults for various operations.
    """
    triad = ContextTriadManager()
    results = {}

    # Benchmark add_hot_context
    start = time.perf_counter()
    for i in range(n_items):
        triad.add_hot_context(f"Hot context item {i}", metadata={"index": i})
    hot_time = (time.perf_counter() - start) * 1000

    results["add_hot_context"] = MetricResult(
        name="add_hot_context",
        value=hot_time / n_items,
        unit="ms/item",
        n_samples=n_items,
    )

    # Benchmark add_warm_context
    start = time.perf_counter()
    for i in range(n_items):
        triad.add_warm_context(f"Warm context item {i}", metadata={"index": i})
    warm_time = (time.perf_counter() - start) * 1000

    results["add_warm_context"] = MetricResult(
        name="add_warm_context",
        value=warm_time / n_items,
        unit="ms/item",
        n_samples=n_items,
    )

    # Benchmark add_cold_context
    start = time.perf_counter()
    for i in range(n_items):
        triad.add_cold_context(f"Cold context item {i}", metadata={"index": i})
    cold_time = (time.perf_counter() - start) * 1000

    results["add_cold_context"] = MetricResult(
        name="add_cold_context",
        value=cold_time / n_items,
        unit="ms/item",
        n_samples=n_items,
    )

    return results


def benchmark_decay_calculator(
    n_items: int = 1000,
) -> MetricResult:
    """Benchmark time decay calculations.

    Args:
        n_items: Number of decay calculations.

    Returns:
        MetricResult with timing statistics.
    """
    calculator = TimeDecayCalculator()

    # Generate random ages (in hours)
    ages = np.random.exponential(scale=24, size=n_items)

    start = time.perf_counter()
    for age in ages:
        calculator.calculate_decay(float(age))
    elapsed = (time.perf_counter() - start) * 1000

    return MetricResult(
        name="decay_calculation",
        value=elapsed / n_items,
        unit="ms/calculation",
        n_samples=n_items,
    )


# ============================================================================
# Main
# ============================================================================


def run_experiments(config: BenchmarkConfig) -> ExperimentResults:
    """Run all benchmark experiments.

    Args:
        config: Benchmark configuration.

    Returns:
        ExperimentResults with all metrics.
    """
    print(f"Setting random seed: {config.seed}")
    set_seed(config.seed)

    metrics: Dict[str, Any] = {}

    if not CAAS_AVAILABLE:
        print("CaaS not available. Returning empty results.")
        return ExperimentResults(
            timestamp=datetime.utcnow().isoformat(),
            caas_version=CAAS_VERSION,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            seed=config.seed,
            metrics={},
            config=asdict(config),
        )

    # 1. Router benchmarks
    print("\n[1/4] Benchmarking Heuristic Router...")
    router = HeuristicRouter()

    latency_result = benchmark_router_latency(
        router,
        SAMPLE_QUERIES,
        n_iterations=config.n_iterations,
        warmup=config.warmup_iterations,
    )
    metrics["router_latency_ms"] = latency_result.value
    metrics["router_latency_std"] = latency_result.std
    print(f"  - Latency: {latency_result.value:.4f} ± {latency_result.std:.4f} ms")

    accuracy_result = benchmark_router_accuracy(router, SAMPLE_QUERIES, EXPECTED_ROUTING)
    metrics["router_accuracy_pct"] = accuracy_result.value
    print(f"  - Accuracy: {accuracy_result.value:.1f}%")

    # 2. Context Triad benchmarks
    print("\n[2/4] Benchmarking Context Triad...")
    triad_results = benchmark_context_triad(n_items=100)
    for name, result in triad_results.items():
        metrics[f"triad_{name}_ms"] = result.value
        print(f"  - {name}: {result.value:.4f} {result.unit}")

    # 3. Decay calculator benchmarks
    print("\n[3/4] Benchmarking Time Decay Calculator...")
    decay_result = benchmark_decay_calculator(n_items=1000)
    metrics["decay_calculation_ms"] = decay_result.value
    print(f"  - Decay calculation: {decay_result.value:.6f} {decay_result.unit}")

    # 4. Summary statistics
    print("\n[4/4] Computing summary statistics...")
    metrics["total_queries_tested"] = len(SAMPLE_QUERIES)
    metrics["n_iterations"] = config.n_iterations

    return ExperimentResults(
        timestamp=datetime.utcnow().isoformat(),
        caas_version=CAAS_VERSION,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        seed=config.seed,
        metrics=metrics,
        config=asdict(config),
    )


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CaaS Reproducibility Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of timing iterations (default: 100)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("CaaS Reproducibility Benchmark")
    print("=" * 60)
    print(f"CaaS Version: {CAAS_VERSION}")
    print(f"Python Version: {sys.version}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")

    config = BenchmarkConfig(
        seed=args.seed,
        n_iterations=args.iterations,
    )

    results = run_experiments(config)

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results.to_dict(), f, indent=2)

    print("\n" + "=" * 60)
    print(f"Results saved to: {output_path}")
    print("=" * 60)

    # Print summary
    print("\nSummary:")
    print(f"  - Router latency: {results.metrics.get('router_latency_ms', 'N/A'):.4f} ms")
    print(f"  - Router accuracy: {results.metrics.get('router_accuracy_pct', 'N/A'):.1f}%")
    print(f"  - Seed: {results.seed}")


if __name__ == "__main__":
    main()
