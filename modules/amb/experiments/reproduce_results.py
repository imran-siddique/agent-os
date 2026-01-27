"""
AMB Benchmark Suite - Reproducible Experiments
==============================================

This script provides a reproducible benchmark for the Agent Message Bus (AMB).
It measures key performance metrics across different message patterns and
saves results for research reproducibility.

Usage:
    python experiments/reproduce_results.py [--seed 42] [--iterations 1000]

Metrics Collected:
    - Latency (publish, subscribe, request-response)
    - Throughput (messages/second)
    - Memory usage
    - Concurrent subscriber scaling
"""

import asyncio
import json
import random
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from amb_core import Message, MessageBus

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class ExperimentConfig:
    """Configuration for reproducible experiments."""

    seed: int = 42
    iterations: int = 1000
    warmup_iterations: int = 100
    message_sizes: List[int] = None  # Bytes in payload
    concurrent_subscribers: List[int] = None

    def __post_init__(self):
        if self.message_sizes is None:
            self.message_sizes = [100, 1000, 10000]  # 100B, 1KB, 10KB
        if self.concurrent_subscribers is None:
            self.concurrent_subscribers = [1, 5, 10, 25, 50]


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    name: str
    iterations: int
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    std_dev_ms: float
    throughput_msg_per_sec: float
    total_time_sec: float
    config: Dict[str, Any]


# ============================================================================
# Utility Functions
# ============================================================================

def set_seed(seed: int) -> None:
    """Set random seed for reproducibility."""
    random.seed(seed)


def generate_payload(size_bytes: int, seed: int) -> Dict[str, Any]:
    """Generate a deterministic payload of approximately the given size."""
    set_seed(seed)
    # Generate random string to fill payload
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    data = "".join(random.choice(chars) for _ in range(max(10, size_bytes - 50)))
    return {
        "data": data,
        "seed": seed,
        "size_target": size_bytes,
        "timestamp": time.time()
    }


def calculate_percentile(data: List[float], percentile: float) -> float:
    """Calculate the given percentile from a list of values."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile / 100)
    return sorted_data[min(index, len(sorted_data) - 1)]


# ============================================================================
# Benchmark Functions
# ============================================================================

async def benchmark_publish_latency(
    bus: MessageBus,
    iterations: int,
    payload_size: int,
    seed: int,
    wait_for_confirmation: bool = False
) -> BenchmarkResult:
    """Benchmark publish latency for fire-and-forget pattern."""

    latencies: List[float] = []
    pattern = "confirmed" if wait_for_confirmation else "fire_and_forget"

    for i in range(iterations):
        payload = generate_payload(payload_size, seed + i)

        start = time.perf_counter()
        await bus.publish(
            "benchmark.publish",
            payload,
            wait_for_confirmation=wait_for_confirmation
        )
        end = time.perf_counter()

        latencies.append((end - start) * 1000)  # Convert to ms

    total_time = sum(latencies) / 1000  # Back to seconds

    return BenchmarkResult(
        name=f"publish_{pattern}_{payload_size}B",
        iterations=iterations,
        mean_latency_ms=statistics.mean(latencies),
        median_latency_ms=statistics.median(latencies),
        p95_latency_ms=calculate_percentile(latencies, 95),
        p99_latency_ms=calculate_percentile(latencies, 99),
        min_latency_ms=min(latencies),
        max_latency_ms=max(latencies),
        std_dev_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
        throughput_msg_per_sec=iterations / total_time if total_time > 0 else 0,
        total_time_sec=total_time,
        config={"payload_size": payload_size, "pattern": pattern}
    )


async def benchmark_pubsub_e2e(
    bus: MessageBus,
    iterations: int,
    payload_size: int,
    seed: int
) -> BenchmarkResult:
    """Benchmark end-to-end pub/sub latency."""

    latencies: List[float] = []
    received_event = asyncio.Event()
    receive_time: float = 0

    async def handler(msg: Message):
        nonlocal receive_time
        receive_time = time.perf_counter()
        received_event.set()

    sub_id = await bus.subscribe("benchmark.e2e", handler)

    try:
        for i in range(iterations):
            payload = generate_payload(payload_size, seed + i)
            received_event.clear()

            start = time.perf_counter()
            await bus.publish("benchmark.e2e", payload)

            # Wait for message to be received
            await asyncio.wait_for(received_event.wait(), timeout=5.0)

            latencies.append((receive_time - start) * 1000)
    finally:
        await bus.unsubscribe(sub_id)

    total_time = sum(latencies) / 1000

    return BenchmarkResult(
        name=f"pubsub_e2e_{payload_size}B",
        iterations=iterations,
        mean_latency_ms=statistics.mean(latencies),
        median_latency_ms=statistics.median(latencies),
        p95_latency_ms=calculate_percentile(latencies, 95),
        p99_latency_ms=calculate_percentile(latencies, 99),
        min_latency_ms=min(latencies),
        max_latency_ms=max(latencies),
        std_dev_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
        throughput_msg_per_sec=iterations / total_time if total_time > 0 else 0,
        total_time_sec=total_time,
        config={"payload_size": payload_size, "pattern": "pubsub_e2e"}
    )


async def benchmark_request_response(
    bus: MessageBus,
    iterations: int,
    payload_size: int,
    seed: int
) -> BenchmarkResult:
    """Benchmark request-response pattern latency."""

    latencies: List[float] = []

    # Set up responder
    async def responder(msg: Message):
        await bus.reply(msg, {"response": "ack", "original_id": msg.id})

    sub_id = await bus.subscribe("benchmark.request", responder)

    try:
        for i in range(iterations):
            payload = generate_payload(payload_size, seed + i)

            start = time.perf_counter()
            response = await bus.request(
                "benchmark.request",
                payload,
                timeout=5.0
            )
            end = time.perf_counter()

            latencies.append((end - start) * 1000)
    finally:
        await bus.unsubscribe(sub_id)

    total_time = sum(latencies) / 1000

    return BenchmarkResult(
        name=f"request_response_{payload_size}B",
        iterations=iterations,
        mean_latency_ms=statistics.mean(latencies),
        median_latency_ms=statistics.median(latencies),
        p95_latency_ms=calculate_percentile(latencies, 95),
        p99_latency_ms=calculate_percentile(latencies, 99),
        min_latency_ms=min(latencies),
        max_latency_ms=max(latencies),
        std_dev_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
        throughput_msg_per_sec=iterations / total_time if total_time > 0 else 0,
        total_time_sec=total_time,
        config={"payload_size": payload_size, "pattern": "request_response"}
    )


async def benchmark_concurrent_subscribers(
    bus: MessageBus,
    iterations: int,
    num_subscribers: int,
    seed: int
) -> BenchmarkResult:
    """Benchmark message fanout to multiple subscribers."""

    latencies: List[float] = []
    received_counts: Dict[int, int] = dict.fromkeys(range(num_subscribers), 0)
    all_received = asyncio.Event()
    expected_total = 0

    def make_handler(subscriber_id: int):
        async def handler(msg: Message):
            received_counts[subscriber_id] += 1
            if sum(received_counts.values()) >= expected_total:
                all_received.set()
        return handler

    # Subscribe all handlers
    sub_ids = []
    for i in range(num_subscribers):
        sub_id = await bus.subscribe("benchmark.fanout", make_handler(i))
        sub_ids.append(sub_id)

    try:
        for i in range(iterations):
            payload = generate_payload(100, seed + i)  # Fixed small payload
            all_received.clear()
            expected_total = (i + 1) * num_subscribers

            start = time.perf_counter()
            await bus.publish("benchmark.fanout", payload)

            # Wait for all subscribers to receive
            await asyncio.wait_for(all_received.wait(), timeout=5.0)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)
    finally:
        for sub_id in sub_ids:
            await bus.unsubscribe(sub_id)

    total_time = sum(latencies) / 1000

    return BenchmarkResult(
        name=f"fanout_{num_subscribers}_subscribers",
        iterations=iterations,
        mean_latency_ms=statistics.mean(latencies),
        median_latency_ms=statistics.median(latencies),
        p95_latency_ms=calculate_percentile(latencies, 95),
        p99_latency_ms=calculate_percentile(latencies, 99),
        min_latency_ms=min(latencies),
        max_latency_ms=max(latencies),
        std_dev_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
        throughput_msg_per_sec=iterations / total_time if total_time > 0 else 0,
        total_time_sec=total_time,
        config={"num_subscribers": num_subscribers, "pattern": "fanout"}
    )


# ============================================================================
# Main Experiment Runner
# ============================================================================

async def run_experiments(config: ExperimentConfig) -> Dict[str, Any]:
    """Run all experiments and collect results."""

    print("=" * 60)
    print("AMB Benchmark Suite")
    print("=" * 60)
    print(f"Seed: {config.seed}")
    print(f"Iterations: {config.iterations}")
    print(f"Message sizes: {config.message_sizes}")
    print(f"Subscriber counts: {config.concurrent_subscribers}")
    print("=" * 60)

    set_seed(config.seed)
    results: List[Dict[str, Any]] = []

    async with MessageBus() as bus:
        # Warmup
        print("\n🔥 Running warmup...")
        for _ in range(config.warmup_iterations):
            await bus.publish("warmup", {"warmup": True})

        # Benchmark 1: Publish latency (fire and forget)
        print("\n📤 Benchmarking publish latency (fire and forget)...")
        for size in config.message_sizes:
            result = await benchmark_publish_latency(
                bus, config.iterations, size, config.seed, wait_for_confirmation=False
            )
            results.append(asdict(result))
            print(f"  {size}B: {result.mean_latency_ms:.3f}ms mean, "
                  f"{result.throughput_msg_per_sec:.0f} msg/s")

        # Benchmark 2: Publish latency (with confirmation)
        print("\n📤 Benchmarking publish latency (with confirmation)...")
        for size in config.message_sizes:
            result = await benchmark_publish_latency(
                bus, config.iterations, size, config.seed, wait_for_confirmation=True
            )
            results.append(asdict(result))
            print(f"  {size}B: {result.mean_latency_ms:.3f}ms mean, "
                  f"{result.throughput_msg_per_sec:.0f} msg/s")

        # Benchmark 3: End-to-end pub/sub
        print("\n🔄 Benchmarking end-to-end pub/sub latency...")
        for size in config.message_sizes:
            result = await benchmark_pubsub_e2e(
                bus, config.iterations, size, config.seed
            )
            results.append(asdict(result))
            print(f"  {size}B: {result.mean_latency_ms:.3f}ms mean, "
                  f"{result.throughput_msg_per_sec:.0f} msg/s")

        # Benchmark 4: Request-response
        print("\n📨 Benchmarking request-response latency...")
        for size in config.message_sizes:
            result = await benchmark_request_response(
                bus, config.iterations, size, config.seed
            )
            results.append(asdict(result))
            print(f"  {size}B: {result.mean_latency_ms:.3f}ms mean, "
                  f"{result.throughput_msg_per_sec:.0f} msg/s")

        # Benchmark 5: Concurrent subscribers (fanout)
        print("\n👥 Benchmarking subscriber fanout...")
        for num_subs in config.concurrent_subscribers:
            result = await benchmark_concurrent_subscribers(
                bus, min(config.iterations, 100), num_subs, config.seed
            )
            results.append(asdict(result))
            print(f"  {num_subs} subscribers: {result.mean_latency_ms:.3f}ms mean")

    # Compile final results
    experiment_output = {
        "metadata": {
            "experiment_name": "AMB Performance Benchmark",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "seed": config.seed,
            "iterations": config.iterations,
            "python_version": sys.version,
            "platform": sys.platform
        },
        "config": asdict(config),
        "results": results,
        "summary": {
            "total_benchmarks": len(results),
            "avg_latency_ms": statistics.mean(r["mean_latency_ms"] for r in results),
            "avg_throughput": statistics.mean(r["throughput_msg_per_sec"] for r in results)
        }
    }

    return experiment_output


def save_results(results: Dict[str, Any], output_path: Path) -> None:
    """Save experiment results to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved to: {output_path}")


def main():
    """Main entry point for experiments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AMB Reproducible Benchmark Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python reproduce_results.py
    python reproduce_results.py --seed 123 --iterations 500
    python reproduce_results.py --output custom_results.json
        """
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--iterations", type=int, default=1000, help="Iterations per benchmark (default: 1000)")
    parser.add_argument("--output", type=str, default="results.json", help="Output file name (default: results.json)")

    args = parser.parse_args()

    config = ExperimentConfig(
        seed=args.seed,
        iterations=args.iterations
    )

    # Run experiments
    results = asyncio.run(run_experiments(config))

    # Save results
    output_path = Path(__file__).parent / args.output
    save_results(results, output_path)

    # Print summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Total benchmarks run: {results['summary']['total_benchmarks']}")
    print(f"Average latency: {results['summary']['avg_latency_ms']:.3f}ms")
    print(f"Average throughput: {results['summary']['avg_throughput']:.0f} msg/s")
    print("=" * 60)


if __name__ == "__main__":
    main()
