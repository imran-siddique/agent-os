#!/usr/bin/env python3
"""
reproduce_results.py - Reproducible experiment runner for emk.

This script provides a controlled environment to benchmark emk performance
and reproduce results for research purposes. It measures:
- Episode creation latency
- Storage write latency  
- Retrieval latency
- Memory usage
- Tag generation performance

Usage:
    python experiments/reproduce_results.py
    python experiments/reproduce_results.py --episodes 1000 --seed 42
    
Output:
    Saves results to experiments/results.json

Author: Imran Siddique
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import random
import statistics
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from emk import Episode, FileAdapter, Indexer, __version__


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    
    name: str
    iterations: int
    total_time_ms: float
    mean_time_ms: float
    std_dev_ms: float
    min_time_ms: float
    max_time_ms: float
    ops_per_second: float


@dataclass  
class ExperimentResults:
    """Complete experiment results."""
    
    emk_version: str
    python_version: str
    timestamp: str
    seed: int
    num_episodes: int
    benchmarks: Dict[str, Dict[str, Any]]
    system_info: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def set_seed(seed: int) -> None:
    """
    Set random seed for reproducibility.
    
    Args:
        seed: The random seed to use.
    """
    random.seed(seed)
    # Note: numpy seed would be set here if numpy.random was used


def generate_sample_episodes(n: int, seed: int) -> List[Episode]:
    """
    Generate sample episodes for benchmarking.
    
    Args:
        n: Number of episodes to generate.
        seed: Random seed for reproducibility.
        
    Returns:
        List of generated Episode objects.
    """
    set_seed(seed)
    
    goals = [
        "Retrieve user preferences from database",
        "Process incoming API request",
        "Validate user authentication token",
        "Update cache with new data",
        "Send notification to user",
        "Parse configuration file",
        "Execute scheduled task",
        "Handle webhook callback",
        "Generate analytics report",
        "Sync data with external service",
    ]
    
    actions = [
        "Queried primary database with indexed lookup",
        "Parsed JSON payload and validated schema",
        "Verified JWT signature and claims",
        "Updated Redis cache with TTL",
        "Pushed message to notification queue",
        "Loaded YAML config with defaults",
        "Ran background job processor",
        "Processed incoming POST request",
        "Aggregated metrics from time series",
        "Called external REST API endpoint",
    ]
    
    results = [
        "Successfully completed operation",
        "Partial success with retry needed",
        "Completed with warnings",
        "Operation timed out, fallback used",
        "Cached result returned",
    ]
    
    reflections = [
        "Performance was within acceptable bounds",
        "Consider adding more caching for this operation",
        "Error handling could be improved",
        "This pattern should be extracted to a utility",
        "Latency was higher than expected, investigate",
    ]
    
    episodes = []
    for i in range(n):
        episode = Episode(
            goal=random.choice(goals),
            action=random.choice(actions),
            result=random.choice(results),
            reflection=random.choice(reflections),
            metadata={
                "experiment_id": i,
                "batch": i // 100,
                "priority": random.choice(["low", "medium", "high"]),
            }
        )
        episodes.append(episode)
    
    return episodes


def benchmark_episode_creation(n: int, seed: int) -> BenchmarkResult:
    """
    Benchmark episode creation latency.
    
    Args:
        n: Number of episodes to create.
        seed: Random seed for reproducibility.
        
    Returns:
        BenchmarkResult with timing statistics.
    """
    set_seed(seed)
    
    timings = []
    for i in range(n):
        start = time.perf_counter()
        _ = Episode(
            goal=f"Goal {i}",
            action=f"Action {i}",
            result=f"Result {i}",
            reflection=f"Reflection {i}",
            metadata={"index": i}
        )
        end = time.perf_counter()
        timings.append((end - start) * 1000)  # Convert to ms
    
    return BenchmarkResult(
        name="episode_creation",
        iterations=n,
        total_time_ms=sum(timings),
        mean_time_ms=statistics.mean(timings),
        std_dev_ms=statistics.stdev(timings) if len(timings) > 1 else 0,
        min_time_ms=min(timings),
        max_time_ms=max(timings),
        ops_per_second=n / (sum(timings) / 1000) if sum(timings) > 0 else 0,
    )


def benchmark_storage_write(episodes: List[Episode], filepath: Path) -> BenchmarkResult:
    """
    Benchmark storage write latency.
    
    Args:
        episodes: Episodes to store.
        filepath: Path to storage file.
        
    Returns:
        BenchmarkResult with timing statistics.
    """
    store = FileAdapter(str(filepath))
    
    timings = []
    for episode in episodes:
        start = time.perf_counter()
        store.store(episode)
        end = time.perf_counter()
        timings.append((end - start) * 1000)
    
    return BenchmarkResult(
        name="storage_write",
        iterations=len(episodes),
        total_time_ms=sum(timings),
        mean_time_ms=statistics.mean(timings),
        std_dev_ms=statistics.stdev(timings) if len(timings) > 1 else 0,
        min_time_ms=min(timings),
        max_time_ms=max(timings),
        ops_per_second=len(episodes) / (sum(timings) / 1000) if sum(timings) > 0 else 0,
    )


def benchmark_retrieval(store: FileAdapter, n_queries: int) -> BenchmarkResult:
    """
    Benchmark retrieval latency.
    
    Args:
        store: FileAdapter with stored episodes.
        n_queries: Number of retrieval queries to run.
        
    Returns:
        BenchmarkResult with timing statistics.
    """
    timings = []
    filters_list = [
        None,
        {"priority": "high"},
        {"priority": "medium"},
        {"priority": "low"},
    ]
    
    for i in range(n_queries):
        filters = filters_list[i % len(filters_list)]
        start = time.perf_counter()
        _ = store.retrieve(filters=filters, limit=10)
        end = time.perf_counter()
        timings.append((end - start) * 1000)
    
    return BenchmarkResult(
        name="retrieval",
        iterations=n_queries,
        total_time_ms=sum(timings),
        mean_time_ms=statistics.mean(timings),
        std_dev_ms=statistics.stdev(timings) if len(timings) > 1 else 0,
        min_time_ms=min(timings),
        max_time_ms=max(timings),
        ops_per_second=n_queries / (sum(timings) / 1000) if sum(timings) > 0 else 0,
    )


def benchmark_indexer(episodes: List[Episode]) -> BenchmarkResult:
    """
    Benchmark indexer tag generation.
    
    Args:
        episodes: Episodes to generate tags for.
        
    Returns:
        BenchmarkResult with timing statistics.
    """
    timings = []
    for episode in episodes:
        start = time.perf_counter()
        _ = Indexer.generate_episode_tags(episode)
        _ = Indexer.create_search_text(episode)
        _ = Indexer.enrich_metadata(episode, auto_tags=True)
        end = time.perf_counter()
        timings.append((end - start) * 1000)
    
    return BenchmarkResult(
        name="indexer",
        iterations=len(episodes),
        total_time_ms=sum(timings),
        mean_time_ms=statistics.mean(timings),
        std_dev_ms=statistics.stdev(timings) if len(timings) > 1 else 0,
        min_time_ms=min(timings),
        max_time_ms=max(timings),
        ops_per_second=len(episodes) / (sum(timings) / 1000) if sum(timings) > 0 else 0,
    )


def get_system_info() -> Dict[str, Any]:
    """
    Collect system information for reproducibility.
    
    Returns:
        Dictionary with system information.
    """
    import platform
    
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_implementation": platform.python_implementation(),
        "python_build": platform.python_build(),
    }


def run_experiments(
    num_episodes: int = 100,
    seed: int = 42,
    output_path: Optional[Path] = None,
) -> ExperimentResults:
    """
    Run all experiments and collect results.
    
    Args:
        num_episodes: Number of episodes for benchmarks.
        seed: Random seed for reproducibility.
        output_path: Path to save results (optional).
        
    Returns:
        ExperimentResults with all benchmark data.
    """
    print(f"🧪 EMK Reproducibility Experiment Runner v{__version__}")
    print(f"=" * 60)
    print(f"Configuration:")
    print(f"  - Episodes: {num_episodes}")
    print(f"  - Seed: {seed}")
    print(f"  - Python: {sys.version}")
    print()
    
    # Force garbage collection before benchmarks
    gc.collect()
    
    # Generate sample episodes
    print("📝 Generating sample episodes...")
    episodes = generate_sample_episodes(num_episodes, seed)
    print(f"   Generated {len(episodes)} episodes")
    
    # Run benchmarks
    benchmarks = {}
    
    print("\n⏱️  Running benchmarks...")
    
    # Episode creation benchmark
    print("   [1/4] Episode creation...")
    result = benchmark_episode_creation(num_episodes, seed)
    benchmarks["episode_creation"] = asdict(result)
    print(f"         Mean: {result.mean_time_ms:.4f}ms, Ops/sec: {result.ops_per_second:.0f}")
    
    # Storage write benchmark
    print("   [2/4] Storage write...")
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "benchmark.jsonl"
        result = benchmark_storage_write(episodes, filepath)
        benchmarks["storage_write"] = asdict(result)
        print(f"         Mean: {result.mean_time_ms:.4f}ms, Ops/sec: {result.ops_per_second:.0f}")
        
        # Retrieval benchmark (uses the same store)
        print("   [3/4] Retrieval...")
        store = FileAdapter(str(filepath))
        result = benchmark_retrieval(store, min(num_episodes, 100))
        benchmarks["retrieval"] = asdict(result)
        print(f"         Mean: {result.mean_time_ms:.4f}ms, Ops/sec: {result.ops_per_second:.0f}")
    
    # Indexer benchmark
    print("   [4/4] Indexer...")
    result = benchmark_indexer(episodes[:min(num_episodes, 100)])
    benchmarks["indexer"] = asdict(result)
    print(f"         Mean: {result.mean_time_ms:.4f}ms, Ops/sec: {result.ops_per_second:.0f}")
    
    # Compile results
    results = ExperimentResults(
        emk_version=__version__,
        python_version=sys.version,
        timestamp=datetime.now(timezone.utc).isoformat(),
        seed=seed,
        num_episodes=num_episodes,
        benchmarks=benchmarks,
        system_info=get_system_info(),
    )
    
    # Save results
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results.to_dict(), f, indent=2)
        print(f"\n💾 Results saved to: {output_path}")
    
    # Print summary
    print(f"\n{'=' * 60}")
    print("📊 Summary")
    print(f"{'=' * 60}")
    for name, data in benchmarks.items():
        print(f"  {name}:")
        print(f"    - Mean latency: {data['mean_time_ms']:.4f} ms")
        print(f"    - Throughput: {data['ops_per_second']:.0f} ops/sec")
    
    return results


def main() -> None:
    """Main entry point for the experiment runner."""
    parser = argparse.ArgumentParser(
        description="EMK Reproducibility Experiment Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reproduce_results.py
  python reproduce_results.py --episodes 1000 --seed 123
  python reproduce_results.py --output custom_results.json
        """
    )
    parser.add_argument(
        "--episodes", "-n",
        type=int,
        default=100,
        help="Number of episodes for benchmarks (default: 100)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (default: experiments/results.json)"
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(__file__).parent / "results.json"
    
    # Run experiments
    run_experiments(
        num_episodes=args.episodes,
        seed=args.seed,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
