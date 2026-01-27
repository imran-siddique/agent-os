"""
Reproducible Experiment Runner for CMVK

Runs experiments with full reproducibility:
- Fixed random seeds
- Hardware/runtime statistics
- Deterministic execution
- Complete logging

Usage:
    python -m experiments.reproducible_runner --dataset humaneval_50 --seed 42
"""

import argparse
import json
import logging
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cross_model_verification_kernel.agents.generator_openai import OpenAIGenerator
from cross_model_verification_kernel.agents.verifier_gemini import GeminiVerifier
from cross_model_verification_kernel.core.kernel import VerificationKernel, set_reproducibility_seed

logger = logging.getLogger(__name__)


def get_hardware_info() -> dict[str, Any]:
    """Collect hardware and system information for reproducibility."""
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "timestamp": datetime.now().isoformat(),
    }

    # CPU info
    try:
        import multiprocessing

        info["cpu_count"] = multiprocessing.cpu_count()
    except Exception:
        info["cpu_count"] = "unknown"

    # Memory info (if psutil available)
    try:
        import psutil

        mem = psutil.virtual_memory()
        info["memory_total_gb"] = round(mem.total / (1024**3), 2)
        info["memory_available_gb"] = round(mem.available / (1024**3), 2)
    except ImportError:
        info["memory_total_gb"] = "unknown (install psutil)"

    # GPU info (if available)
    try:
        import torch

        if torch.cuda.is_available():
            info["gpu"] = torch.cuda.get_device_name(0)
            info["gpu_memory_gb"] = round(
                torch.cuda.get_device_properties(0).total_memory / (1024**3), 2
            )
        else:
            info["gpu"] = "none"
    except ImportError:
        info["gpu"] = "unknown (torch not installed)"

    return info


def get_package_versions() -> dict[str, str]:
    """Get versions of key packages for reproducibility."""
    packages = [
        "openai",
        "google-generativeai",
        "anthropic",
        "numpy",
        "pandas",
        "torch",
        "transformers",
    ]

    versions = {}
    for pkg in packages:
        try:
            import importlib

            mod = importlib.import_module(pkg.replace("-", "_"))
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            versions[pkg] = "not installed"

    # Add CMVK version
    try:
        from src import __version__

        versions["cmvk"] = __version__
    except Exception:
        versions["cmvk"] = "unknown"

    return versions


def load_dataset(dataset_name: str) -> list[dict[str, Any]]:
    """Load a dataset from the experiments/datasets directory."""
    dataset_path = Path(f"experiments/datasets/{dataset_name}.json")

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    with open(dataset_path) as f:
        data = json.load(f)

    # Handle different dataset formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "problems" in data:
        return data["problems"]
    else:
        raise ValueError(f"Unknown dataset format in {dataset_path}")


def run_single_problem(
    kernel: VerificationKernel, problem: dict[str, Any], problem_idx: int
) -> dict[str, Any]:
    """Run a single problem through the verification kernel."""
    task = problem.get("prompt", problem.get("task", ""))
    task_id = problem.get("task_id", f"problem_{problem_idx}")

    start_time = time.time()

    try:
        result = kernel.execute(task)
        elapsed = time.time() - start_time

        return {
            "task_id": task_id,
            "success": result.is_complete and result.final_result is not None,
            "loops": result.current_loop,
            "elapsed_seconds": elapsed,
            "solution": result.final_result,
            "error": None,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error on {task_id}: {e}")

        return {
            "task_id": task_id,
            "success": False,
            "loops": 0,
            "elapsed_seconds": elapsed,
            "solution": None,
            "error": str(e),
        }


def run_experiment(
    dataset_name: str,
    generator_model: str = "gpt-4o",
    verifier_model: str = "gemini-1.5-pro",
    max_loops: int = 5,
    seed: int = 42,
    max_problems: int | None = None,
    output_dir: str = "experiments/results",
) -> dict[str, Any]:
    """
    Run a full reproducible experiment.

    Args:
        dataset_name: Name of dataset file (without .json)
        generator_model: OpenAI model for generation
        verifier_model: Model for verification
        max_loops: Maximum verification loops per problem
        seed: Random seed for reproducibility
        max_problems: Limit number of problems (for testing)
        output_dir: Directory to save results

    Returns:
        Complete experiment results
    """
    # Set reproducibility
    set_reproducibility_seed(seed)

    # Collect metadata
    experiment_id = f"exp_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    metadata = {
        "experiment_id": experiment_id,
        "dataset": dataset_name,
        "generator_model": generator_model,
        "verifier_model": verifier_model,
        "max_loops": max_loops,
        "seed": seed,
        "hardware": get_hardware_info(),
        "package_versions": get_package_versions(),
        "start_time": datetime.now().isoformat(),
    }

    logger.info(f"Starting experiment: {experiment_id}")
    logger.info(f"Seed: {seed}, Generator: {generator_model}, Verifier: {verifier_model}")

    # Load dataset
    problems = load_dataset(dataset_name)
    if max_problems:
        problems = problems[:max_problems]

    metadata["num_problems"] = len(problems)
    logger.info(f"Loaded {len(problems)} problems")

    # Initialize kernel
    generator = OpenAIGenerator(model_name=generator_model, temperature=0.0)
    verifier = GeminiVerifier(model_name=verifier_model, temperature=0.0)

    kernel = VerificationKernel(
        generator=generator, verifier=verifier, seed=seed, enable_trace_logging=True
    )
    kernel.max_loops = max_loops

    # Run experiments
    results = []
    total_start = time.time()

    for i, problem in enumerate(problems):
        logger.info(f"Problem {i+1}/{len(problems)}: {problem.get('task_id', f'#{i}')}")
        result = run_single_problem(kernel, problem, i)
        results.append(result)

        # Progress update
        success_count = sum(1 for r in results if r["success"])
        logger.info(
            f"  Result: {'✓' if result['success'] else '✗'} in {result['elapsed_seconds']:.1f}s, {result['loops']} loops"
        )
        logger.info(
            f"  Running: {success_count}/{len(results)} ({100*success_count/len(results):.1f}%)"
        )

    total_elapsed = time.time() - total_start

    # Compute summary statistics
    success_count = sum(1 for r in results if r["success"])
    total_loops = sum(r["loops"] for r in results)

    summary = {
        "total_problems": len(results),
        "successful": success_count,
        "failed": len(results) - success_count,
        "pass_rate": success_count / len(results) if results else 0,
        "avg_loops": total_loops / len(results) if results else 0,
        "total_time_seconds": total_elapsed,
        "avg_time_per_problem": total_elapsed / len(results) if results else 0,
        "total_generator_tokens": generator.total_tokens_used,
        "total_verifier_tokens": verifier.total_tokens_used,
    }

    # Complete experiment record
    experiment = {
        "metadata": metadata,
        "summary": summary,
        "results": results,
        "end_time": datetime.now().isoformat(),
    }

    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / f"{experiment_id}.json"
    with open(output_file, "w") as f:
        json.dump(experiment, f, indent=2)

    logger.info("\nExperiment complete!")
    logger.info(f"Results saved to: {output_file}")
    logger.info(
        f"Pass rate: {summary['pass_rate']*100:.1f}% ({summary['successful']}/{summary['total_problems']})"
    )
    logger.info(f"Avg loops: {summary['avg_loops']:.2f}")
    logger.info(f"Total time: {summary['total_time_seconds']:.1f}s")

    return experiment


def main():
    parser = argparse.ArgumentParser(description="Run reproducible CMVK experiments")
    parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        default="humaneval_sample",
        help="Dataset name (e.g., humaneval_50, humaneval_full)",
    )
    parser.add_argument("--generator", "-g", type=str, default="gpt-4o", help="Generator model")
    parser.add_argument(
        "--verifier", "-v", type=str, default="gemini-1.5-pro", help="Verifier model"
    )
    parser.add_argument("--max-loops", "-l", type=int, default=5, help="Maximum verification loops")
    parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--max-problems",
        "-n",
        type=int,
        default=None,
        help="Limit number of problems (for testing)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="experiments/results",
        help="Output directory for results",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    )

    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not set")
        sys.exit(1)
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY not set")
        sys.exit(1)

    # Run experiment
    run_experiment(
        dataset_name=args.dataset,
        generator_model=args.generator,
        verifier_model=args.verifier,
        max_loops=args.max_loops,
        seed=args.seed,
        max_problems=args.max_problems,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
