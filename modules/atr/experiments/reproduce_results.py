#!/usr/bin/env python3
"""Reproducibility script for ATR experiments.

This script provides a controlled environment for running experiments
and measuring performance metrics for the Agent Tool Registry.

Usage:
    python experiments/reproduce_results.py
    python experiments/reproduce_results.py --seed 42 --experiment full_suite

Example:
    $ python experiments/reproduce_results.py --seed 42
    Running ATR Experiments (seed=42)
    ================================
    ✓ registration_benchmark: 1.234s (1000 tools registered)
    ✓ discovery_benchmark: 0.567s (avg 0.12ms per search)
    ✓ schema_conversion: 0.089s (100% compatible)

    Results saved to: experiments/results/results_20260123_100000.json
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import atr
from atr import Registry


@dataclass
class ExperimentMetrics:
    """Metrics collected from an experiment run."""

    name: str
    duration_seconds: float
    iterations: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_ops_per_sec: float = 0.0
    memory_mb: float = 0.0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """Complete result of an experiment run."""

    metadata: Dict[str, Any]
    experiments: Dict[str, ExperimentMetrics]
    summary: Dict[str, Any]


def set_seed(seed: int) -> None:
    """Set random seed for reproducibility.

    Args:
        seed: Integer seed value for random number generators.
    """
    random.seed(seed)


def calculate_percentiles(latencies: List[float]) -> Dict[str, float]:
    """Calculate latency percentiles.

    Args:
        latencies: List of latency measurements in milliseconds.

    Returns:
        Dictionary with p50, p95, p99 values.
    """
    if not latencies:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)

    return {
        "p50": sorted_latencies[int(n * 0.50)],
        "p95": sorted_latencies[int(n * 0.95)] if n >= 20 else sorted_latencies[-1],
        "p99": sorted_latencies[int(n * 0.99)] if n >= 100 else sorted_latencies[-1],
    }


def create_sample_function(idx: int) -> Callable[..., str]:
    """Create a sample tool function for benchmarking.

    Args:
        idx: Index for unique function naming.

    Returns:
        A callable function with proper type hints.
    """

    def sample_tool(
        input_text: str,
        count: int = 1,
        uppercase: bool = False,
    ) -> str:
        """Process input text with various transformations.

        Args:
            input_text: The text to process.
            count: Number of times to repeat.
            uppercase: Whether to convert to uppercase.

        Returns:
            Processed text string.
        """
        result = input_text * count
        if uppercase:
            result = result.upper()
        return result

    sample_tool.__name__ = f"sample_tool_{idx}"
    sample_tool.__doc__ = f"Sample tool {idx} for benchmarking."
    return sample_tool


def run_registration_benchmark(
    registry: Registry,
    num_tools: int = 1000,
) -> ExperimentMetrics:
    """Benchmark tool registration performance.

    Args:
        registry: Registry instance to use.
        num_tools: Number of tools to register.

    Returns:
        ExperimentMetrics with registration performance data.
    """
    latencies: List[float] = []
    success_count = 0
    failure_count = 0

    tags_pool = ["math", "text", "web", "file", "api", "data", "ml", "util"]
    costs = ["free", "low", "medium", "high"]

    start_time = time.perf_counter()

    for i in range(num_tools):
        func = create_sample_function(i)
        selected_tags = random.sample(tags_pool, k=random.randint(1, 3))
        selected_cost = random.choice(costs)

        try:
            op_start = time.perf_counter()

            # Use the decorator directly
            decorator = atr.register(
                name=f"benchmark_tool_{i}",
                description=f"Benchmark tool number {i}",
                version="1.0.0",
                author="Benchmark Suite",
                cost=selected_cost,
                tags=selected_tags,
                registry=registry,
            )
            decorator(func)

            op_end = time.perf_counter()
            latencies.append((op_end - op_start) * 1000)  # Convert to ms
            success_count += 1

        except Exception as e:
            failure_count += 1
            print(f"  Warning: Failed to register tool {i}: {e}")

    end_time = time.perf_counter()
    total_duration = end_time - start_time

    percentiles = calculate_percentiles(latencies)

    return ExperimentMetrics(
        name="registration_benchmark",
        duration_seconds=total_duration,
        iterations=num_tools,
        success_count=success_count,
        failure_count=failure_count,
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
        min_latency_ms=min(latencies) if latencies else 0,
        max_latency_ms=max(latencies) if latencies else 0,
        p50_latency_ms=percentiles["p50"],
        p95_latency_ms=percentiles["p95"],
        p99_latency_ms=percentiles["p99"],
        throughput_ops_per_sec=success_count / total_duration if total_duration > 0 else 0,
        extra={"tools_registered": success_count},
    )


def run_discovery_benchmark(
    registry: Registry,
    num_searches: int = 500,
) -> ExperimentMetrics:
    """Benchmark tool discovery and search performance.

    Args:
        registry: Registry instance with registered tools.
        num_searches: Number of search operations to perform.

    Returns:
        ExperimentMetrics with discovery performance data.
    """
    search_queries = [
        "benchmark",
        "tool",
        "text",
        "math",
        "process",
        "sample",
        "data",
        "api",
    ]
    tags_to_search = ["math", "text", "web", "file", "api", "data", "ml", "util"]

    latencies: List[float] = []
    results_count: List[int] = []

    start_time = time.perf_counter()

    for i in range(num_searches):
        # Alternate between search methods
        if i % 3 == 0:
            # Search by query
            query = random.choice(search_queries)
            op_start = time.perf_counter()
            results = registry.search_tools(query)
            op_end = time.perf_counter()
        elif i % 3 == 1:
            # List by tag
            tag = random.choice(tags_to_search)
            op_start = time.perf_counter()
            results = registry.list_tools(tag=tag)
            op_end = time.perf_counter()
        else:
            # List all
            op_start = time.perf_counter()
            results = registry.list_tools()
            op_end = time.perf_counter()

        latencies.append((op_end - op_start) * 1000)
        results_count.append(len(results))

    end_time = time.perf_counter()
    total_duration = end_time - start_time

    percentiles = calculate_percentiles(latencies)

    return ExperimentMetrics(
        name="discovery_benchmark",
        duration_seconds=total_duration,
        iterations=num_searches,
        success_count=num_searches,
        failure_count=0,
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
        min_latency_ms=min(latencies) if latencies else 0,
        max_latency_ms=max(latencies) if latencies else 0,
        p50_latency_ms=percentiles["p50"],
        p95_latency_ms=percentiles["p95"],
        p99_latency_ms=percentiles["p99"],
        throughput_ops_per_sec=num_searches / total_duration if total_duration > 0 else 0,
        extra={
            "avg_results_per_search": sum(results_count) / len(results_count)
            if results_count
            else 0,
        },
    )


def run_schema_conversion_benchmark(
    registry: Registry,
    num_conversions: int = 100,
) -> ExperimentMetrics:
    """Benchmark schema conversion to OpenAI format.

    Args:
        registry: Registry instance with registered tools.
        num_conversions: Number of schema conversions to perform.

    Returns:
        ExperimentMetrics with schema conversion performance data.
    """
    tools = registry.list_tools()
    if not tools:
        return ExperimentMetrics(
            name="schema_conversion",
            duration_seconds=0,
            iterations=0,
            extra={"error": "No tools available for conversion"},
        )

    latencies: List[float] = []
    valid_schemas = 0

    start_time = time.perf_counter()

    for i in range(num_conversions):
        tool = tools[i % len(tools)]

        op_start = time.perf_counter()
        schema = tool.to_openai_function_schema()
        op_end = time.perf_counter()

        latencies.append((op_end - op_start) * 1000)

        # Validate schema structure
        if (
            "name" in schema
            and "description" in schema
            and "parameters" in schema
            and "type" in schema["parameters"]
            and "properties" in schema["parameters"]
        ):
            valid_schemas += 1

    end_time = time.perf_counter()
    total_duration = end_time - start_time

    percentiles = calculate_percentiles(latencies)

    return ExperimentMetrics(
        name="schema_conversion",
        duration_seconds=total_duration,
        iterations=num_conversions,
        success_count=valid_schemas,
        failure_count=num_conversions - valid_schemas,
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
        min_latency_ms=min(latencies) if latencies else 0,
        max_latency_ms=max(latencies) if latencies else 0,
        p50_latency_ms=percentiles["p50"],
        p95_latency_ms=percentiles["p95"],
        p99_latency_ms=percentiles["p99"],
        throughput_ops_per_sec=num_conversions / total_duration if total_duration > 0 else 0,
        extra={
            "schema_validity_rate": valid_schemas / num_conversions if num_conversions > 0 else 0,
        },
    )


def run_experiments(
    seed: int = 42,
    experiments: Optional[List[str]] = None,
) -> ExperimentResult:
    """Run the full experiment suite.

    Args:
        seed: Random seed for reproducibility.
        experiments: List of specific experiments to run. If None, runs all.

    Returns:
        ExperimentResult containing all metrics and metadata.
    """
    set_seed(seed)

    # Create a fresh registry for experiments
    registry = Registry()

    available_experiments = {
        "registration_benchmark": lambda: run_registration_benchmark(registry),
        "discovery_benchmark": lambda: run_discovery_benchmark(registry),
        "schema_conversion": lambda: run_schema_conversion_benchmark(registry),
    }

    if experiments is None or "full_suite" in experiments:
        experiments_to_run = list(available_experiments.keys())
    else:
        experiments_to_run = [e for e in experiments if e in available_experiments]

    # Collect metadata
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "atr_version": atr.__version__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "seed": seed,
    }

    results: Dict[str, ExperimentMetrics] = {}

    print(f"\nRunning ATR Experiments (seed={seed})")
    print("=" * 40)

    total_start = time.perf_counter()

    for exp_name in experiments_to_run:
        print(f"Running {exp_name}...", end=" ", flush=True)
        metrics = available_experiments[exp_name]()
        results[exp_name] = metrics
        print(f"✓ {metrics.duration_seconds:.3f}s")

    total_duration = time.perf_counter() - total_start

    # Generate summary
    summary = {
        "total_duration_seconds": total_duration,
        "experiments_run": len(results),
        "total_iterations": sum(m.iterations for m in results.values()),
        "overall_success_rate": (
            sum(m.success_count for m in results.values())
            / sum(m.iterations for m in results.values())
            if sum(m.iterations for m in results.values()) > 0
            else 0
        ),
    }

    return ExperimentResult(
        metadata=metadata,
        experiments={name: asdict(metrics) for name, metrics in results.items()},
        summary=summary,
    )


def save_results(result: ExperimentResult, output_path: Path) -> None:
    """Save experiment results to JSON file.

    Args:
        result: ExperimentResult to save.
        output_path: Path to output JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")


def main() -> None:
    """Main entry point for the experiment script."""
    parser = argparse.ArgumentParser(
        description="Run ATR reproducibility experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reproduce_results.py                    # Run all experiments
  python reproduce_results.py --seed 42          # Set random seed
  python reproduce_results.py --experiment registration_benchmark
  python reproduce_results.py --output results/my_run.json
        """,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--experiment",
        type=str,
        nargs="+",
        choices=[
            "registration_benchmark",
            "discovery_benchmark",
            "schema_conversion",
            "full_suite",
        ],
        help="Specific experiment(s) to run",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for results JSON",
    )

    args = parser.parse_args()

    # Run experiments
    result = run_experiments(seed=args.seed, experiments=args.experiment)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).parent / "results" / f"results_{timestamp}.json"

    # Save results
    save_results(result, output_path)

    # Print summary
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"  Total duration: {result.summary['total_duration_seconds']:.2f}s")
    print(f"  Experiments run: {result.summary['experiments_run']}")
    print(f"  Total iterations: {result.summary['total_iterations']}")
    print(f"  Success rate: {result.summary['overall_success_rate']:.1%}")


if __name__ == "__main__":
    main()
