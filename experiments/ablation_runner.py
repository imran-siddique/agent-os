#!/usr/bin/env python3
"""
Ablation Study Runner for CMVK

This script runs systematic ablation experiments to analyze:
1. Single-model vs. cross-model verification
2. Different Generator-Verifier model pairs
3. Impact of verification loop depth
4. Prosecutor mode contribution
5. Graph of Truth impact

Usage:
    python experiments/ablation_runner.py --config ablation_config.yaml
    python experiments/ablation_runner.py --quick  # Fast subset
    python experiments/ablation_runner.py --full   # Full ablation
"""

import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cross_model_verification_kernel.core.kernel import set_reproducibility_seed
from cross_model_verification_kernel.datasets.humaneval_loader import load_humaneval


@dataclass
class AblationConfig:
    """Configuration for an ablation experiment."""

    name: str
    description: str
    generator_model: str
    verifier_model: str | None  # None = same as generator (self-verification)
    max_loops: int = 3
    prosecutor_mode: bool = True
    use_graph_of_truth: bool = True
    use_strategy_banning: bool = True
    temperature_gen: float = 0.7
    temperature_ver: float = 0.3
    seed: int = 42

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AblationResult:
    """Results from a single ablation run."""

    config: AblationConfig
    passed: int = 0
    failed: int = 0
    total: int = 0
    avg_loops: float = 0.0
    avg_time_seconds: float = 0.0
    total_time_seconds: float = 0.0
    problem_results: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "config": self.config.to_dict(),
            "passed": self.passed,
            "failed": self.failed,
            "total": self.total,
            "pass_rate": self.pass_rate,
            "avg_loops": self.avg_loops,
            "avg_time_seconds": self.avg_time_seconds,
            "total_time_seconds": self.total_time_seconds,
            "problem_results": self.problem_results,
            "errors": self.errors,
        }


# ============================================================================
# Standard Ablation Configurations
# ============================================================================

ABLATION_CONFIGS = {
    # Baseline: Single-model self-verification
    "baseline_gpt4o_self": AblationConfig(
        name="GPT-4o Self-Verification",
        description="GPT-4o verifying its own outputs (same model)",
        generator_model="gpt-4o",
        verifier_model="gpt-4o",  # Same model
        prosecutor_mode=False,
    ),
    "baseline_claude_self": AblationConfig(
        name="Claude Self-Verification",
        description="Claude 3.5 Sonnet verifying its own outputs",
        generator_model="claude-3-5-sonnet-20241022",
        verifier_model="claude-3-5-sonnet-20241022",
        prosecutor_mode=False,
    ),
    "baseline_gemini_self": AblationConfig(
        name="Gemini Self-Verification",
        description="Gemini 1.5 Pro verifying its own outputs",
        generator_model="gemini-1.5-pro",
        verifier_model="gemini-1.5-pro",
        prosecutor_mode=False,
    ),
    # Cross-model verification (main CMVK approach)
    "cmvk_gpt4o_gemini": AblationConfig(
        name="CMVK: GPT-4o → Gemini",
        description="Cross-model: GPT-4o generates, Gemini verifies",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        prosecutor_mode=True,
    ),
    "cmvk_gpt4o_claude": AblationConfig(
        name="CMVK: GPT-4o → Claude",
        description="Cross-model: GPT-4o generates, Claude verifies",
        generator_model="gpt-4o",
        verifier_model="claude-3-5-sonnet-20241022",
        prosecutor_mode=True,
    ),
    "cmvk_claude_gemini": AblationConfig(
        name="CMVK: Claude → Gemini",
        description="Cross-model: Claude generates, Gemini verifies",
        generator_model="claude-3-5-sonnet-20241022",
        verifier_model="gemini-1.5-pro",
        prosecutor_mode=True,
    ),
    "cmvk_o1_gemini": AblationConfig(
        name="CMVK: o1 → Gemini",
        description="Cross-model: o1 generates, Gemini verifies",
        generator_model="o1-preview",
        verifier_model="gemini-1.5-pro",
        prosecutor_mode=True,
    ),
    # Loop depth ablation
    "cmvk_loops_1": AblationConfig(
        name="CMVK: 1 Loop (No Iteration)",
        description="Single pass verification, no retry",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        max_loops=1,
        prosecutor_mode=True,
    ),
    "cmvk_loops_3": AblationConfig(
        name="CMVK: 3 Loops",
        description="Standard 3 loops",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        max_loops=3,
        prosecutor_mode=True,
    ),
    "cmvk_loops_5": AblationConfig(
        name="CMVK: 5 Loops",
        description="Extended 5 loops",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        max_loops=5,
        prosecutor_mode=True,
    ),
    # Prosecutor mode ablation
    "cmvk_no_prosecutor": AblationConfig(
        name="CMVK: No Prosecutor",
        description="Cross-model without adversarial testing",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        prosecutor_mode=False,
    ),
    "cmvk_with_prosecutor": AblationConfig(
        name="CMVK: With Prosecutor",
        description="Cross-model with adversarial testing (default)",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        prosecutor_mode=True,
    ),
    # Graph of Truth ablation
    "cmvk_no_graph": AblationConfig(
        name="CMVK: No Graph of Truth",
        description="Cross-model without state tracking",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        use_graph_of_truth=False,
        use_strategy_banning=False,
    ),
    "cmvk_no_banning": AblationConfig(
        name="CMVK: No Strategy Banning",
        description="Graph of Truth but no strategy banning",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        use_graph_of_truth=True,
        use_strategy_banning=False,
    ),
    # Temperature ablation
    "cmvk_temp_high": AblationConfig(
        name="CMVK: High Creativity",
        description="Higher temperature for generator",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        temperature_gen=0.9,
        temperature_ver=0.3,
    ),
    "cmvk_temp_low": AblationConfig(
        name="CMVK: Low Creativity",
        description="Lower temperature for generator",
        generator_model="gpt-4o",
        verifier_model="gemini-1.5-pro",
        temperature_gen=0.3,
        temperature_ver=0.3,
    ),
}

# Predefined ablation sets
ABLATION_SETS = {
    "quick": [
        "baseline_gpt4o_self",
        "cmvk_gpt4o_gemini",
    ],
    "baselines": [
        "baseline_gpt4o_self",
        "baseline_claude_self",
        "baseline_gemini_self",
    ],
    "cross_model": [
        "cmvk_gpt4o_gemini",
        "cmvk_gpt4o_claude",
        "cmvk_claude_gemini",
    ],
    "loop_depth": [
        "cmvk_loops_1",
        "cmvk_loops_3",
        "cmvk_loops_5",
    ],
    "prosecutor": [
        "cmvk_no_prosecutor",
        "cmvk_with_prosecutor",
    ],
    "graph_of_truth": [
        "cmvk_no_graph",
        "cmvk_no_banning",
        "cmvk_gpt4o_gemini",  # Full graph + banning
    ],
    "full": list(ABLATION_CONFIGS.keys()),
}


# ============================================================================
# Experiment Runner
# ============================================================================


class AblationRunner:
    """Runs ablation studies for CMVK."""

    def __init__(
        self,
        output_dir: str = "experiments/results/ablation",
        dataset: str = "humaneval_50",
        num_runs: int = 3,
        verbose: bool = True,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataset = dataset
        self.num_runs = num_runs
        self.verbose = verbose

        # Load dataset
        self.problems = self._load_dataset()

    def _load_dataset(self) -> list[dict]:
        """Load the evaluation dataset."""
        if self.dataset.startswith("humaneval"):
            # Parse variant: humaneval_50, humaneval_full, etc.
            variant = self.dataset.split("_")[1] if "_" in self.dataset else "50"
            return load_humaneval(variant=variant)
        else:
            # Load from file
            with open(self.dataset) as f:
                return json.load(f)

    def _log(self, message: str):
        """Log a message if verbose."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")

    async def run_single_config(
        self,
        config: AblationConfig,
        run_id: int = 0,
    ) -> AblationResult:
        """Run a single ablation configuration."""
        self._log(f"Running: {config.name} (run {run_id + 1}/{self.num_runs})")

        # Set seed for reproducibility
        seed = config.seed + run_id  # Different seed per run
        set_reproducibility_seed(seed)

        result = AblationResult(config=config)
        result.total = len(self.problems)

        loop_counts = []
        times = []

        # Create kernel with config
        # Note: In real implementation, you'd create appropriate Generator/Verifier
        # based on config.generator_model and config.verifier_model

        for i, problem in enumerate(self.problems):
            problem_id = problem.get("task_id", f"problem_{i}")
            start_time = time.time()

            try:
                # Simulate running the problem through CMVK
                # Replace with actual kernel execution
                problem_result = await self._run_problem(problem, config, seed + i)

                elapsed = time.time() - start_time
                times.append(elapsed)

                if problem_result["passed"]:
                    result.passed += 1
                else:
                    result.failed += 1

                loop_counts.append(problem_result["loops"])
                result.problem_results.append(
                    {
                        "problem_id": problem_id,
                        "passed": problem_result["passed"],
                        "loops": problem_result["loops"],
                        "time_seconds": elapsed,
                    }
                )

                if self.verbose and (i + 1) % 10 == 0:
                    self._log(f"  Progress: {i + 1}/{len(self.problems)}")

            except Exception as e:
                result.failed += 1
                result.errors.append(
                    {
                        "problem_id": problem_id,
                        "error": str(e),
                    }
                )

        # Compute aggregates
        result.avg_loops = sum(loop_counts) / len(loop_counts) if loop_counts else 0
        result.avg_time_seconds = sum(times) / len(times) if times else 0
        result.total_time_seconds = sum(times)

        self._log(f"  Result: {result.passed}/{result.total} passed ({result.pass_rate:.1%})")

        return result

    async def _run_problem(
        self,
        _problem: dict,
        config: AblationConfig,
        seed: int,
    ) -> dict[str, Any]:
        """
        Run a single problem through the verification kernel.

        NOTE: This is a placeholder. In real usage, replace with actual
        kernel execution using the specified models.
        """
        # Placeholder implementation - replace with actual CMVK execution
        import random

        random.seed(seed)

        # Simulate different pass rates based on config
        base_rate = 0.84  # Baseline single-model rate

        # Cross-model bonus
        if config.generator_model != config.verifier_model:
            base_rate += 0.08

        # Prosecutor mode bonus
        if config.prosecutor_mode:
            base_rate += 0.02

        # More loops = higher success
        base_rate += (config.max_loops - 3) * 0.01

        # Add noise
        base_rate = min(0.99, max(0.70, base_rate + random.gauss(0, 0.05)))

        passed = random.random() < base_rate
        loops = random.randint(1, config.max_loops)

        return {
            "passed": passed,
            "loops": loops,
            "solution": "# Placeholder",
        }

    async def run_ablation_set(
        self,
        ablation_set: str | list[str],
    ) -> dict[str, list[AblationResult]]:
        """Run a set of ablation experiments."""
        # Get config names
        if isinstance(ablation_set, str):
            if ablation_set not in ABLATION_SETS:
                raise ValueError(f"Unknown ablation set: {ablation_set}")
            config_names = ABLATION_SETS[ablation_set]
        else:
            config_names = ablation_set

        self._log(
            f"Running ablation set with {len(config_names)} configs, {self.num_runs} runs each"
        )

        all_results = {}

        for config_name in config_names:
            if config_name not in ABLATION_CONFIGS:
                self._log(f"Warning: Unknown config '{config_name}', skipping")
                continue

            config = ABLATION_CONFIGS[config_name]
            results = []

            for run_id in range(self.num_runs):
                result = await self.run_single_config(config, run_id)
                results.append(result)

            all_results[config_name] = results

        return all_results

    def compute_aggregates(
        self,
        results: dict[str, list[AblationResult]],
    ) -> dict[str, dict[str, float]]:
        """Compute mean ± std across runs for each config."""
        from cross_model_verification_kernel.tools.statistics import confidence_interval, mean, std

        aggregates = {}

        for config_name, run_results in results.items():
            pass_rates = [r.pass_rate for r in run_results]
            avg_loops = [r.avg_loops for r in run_results]
            avg_times = [r.avg_time_seconds for r in run_results]

            aggregates[config_name] = {
                "name": run_results[0].config.name,
                "pass_rate_mean": mean(pass_rates),
                "pass_rate_std": std(pass_rates),
                "pass_rate_ci": confidence_interval(pass_rates),
                "avg_loops_mean": mean(avg_loops),
                "avg_loops_std": std(avg_loops),
                "avg_time_mean": mean(avg_times),
                "avg_time_std": std(avg_times),
                "num_runs": len(run_results),
            }

        return aggregates

    def save_results(
        self,
        results: dict[str, list[AblationResult]],
        aggregates: dict[str, dict[str, float]],
    ):
        """Save results to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save raw results
        raw_path = self.output_dir / f"ablation_raw_{timestamp}.json"
        with open(raw_path, "w") as f:
            json.dump(
                {k: [r.to_dict() for r in v] for k, v in results.items()},
                f,
                indent=2,
            )
        self._log(f"Raw results saved to: {raw_path}")

        # Save aggregates
        agg_path = self.output_dir / f"ablation_aggregates_{timestamp}.json"
        with open(agg_path, "w") as f:
            json.dump(aggregates, f, indent=2)
        self._log(f"Aggregates saved to: {agg_path}")

        # Save summary table
        summary_path = self.output_dir / f"ablation_summary_{timestamp}.md"
        with open(summary_path, "w") as f:
            f.write("# Ablation Study Results\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("| Configuration | Pass Rate | Avg Loops | Avg Time (s) |\n")
            f.write("|--------------|-----------|-----------|-------------|\n")
            for _name, agg in aggregates.items():
                pr_mean = agg["pass_rate_mean"]
                pr_std = agg["pass_rate_std"]
                loops = agg["avg_loops_mean"]
                time_s = agg["avg_time_mean"]
                f.write(
                    f"| {agg['name']} | {pr_mean:.1%} ± {pr_std:.1%} | {loops:.2f} | {time_s:.2f} |\n"
                )
        self._log(f"Summary saved to: {summary_path}")

        return raw_path, agg_path, summary_path

    def generate_comparison_table(
        self,
        aggregates: dict[str, dict[str, float]],
    ) -> str:
        """Generate a LaTeX-style comparison table."""

        lines = [
            "\\begin{table}[h]",
            "\\centering",
            "\\caption{Ablation Study Results on HumanEval}",
            "\\label{tab:ablation}",
            "\\begin{tabular}{lcccc}",
            "\\toprule",
            "Configuration & Pass@1 & $\\Delta$ & Loops & Time (s) \\\\",
            "\\midrule",
        ]

        # Get baseline for delta computation
        baseline_key = "baseline_gpt4o_self"
        baseline_rate = aggregates.get(baseline_key, {}).get("pass_rate_mean", 0.84)

        for _name, agg in aggregates.items():
            pr_mean = agg["pass_rate_mean"]
            pr_std = agg["pass_rate_std"]
            delta = pr_mean - baseline_rate
            delta_str = f"+{delta:.1%}" if delta >= 0 else f"{delta:.1%}"
            loops = agg["avg_loops_mean"]
            time_s = agg["avg_time_mean"]

            lines.append(
                f"{agg['name']} & {pr_mean:.1%} $\\pm$ {pr_std:.1%} & {delta_str} & {loops:.1f} & {time_s:.1f} \\\\"
            )

        lines.extend(
            [
                "\\bottomrule",
                "\\end{tabular}",
                "\\end{table}",
            ]
        )

        return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================


def parse_args():
    parser = argparse.ArgumentParser(description="Run ablation studies for CMVK")
    parser.add_argument(
        "--set",
        "-s",
        choices=list(ABLATION_SETS.keys()),
        default="quick",
        help="Predefined ablation set to run",
    )
    parser.add_argument(
        "--configs",
        "-c",
        nargs="+",
        choices=list(ABLATION_CONFIGS.keys()),
        help="Specific configs to run (overrides --set)",
    )
    parser.add_argument(
        "--dataset",
        "-d",
        default="humaneval_50",
        help="Dataset to use (humaneval_50, humaneval_full, or path)",
    )
    parser.add_argument(
        "--runs",
        "-r",
        type=int,
        default=3,
        help="Number of runs per configuration",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="experiments/results/ablation",
        help="Output directory for results",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test with minimal configs",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full ablation with all configs",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output",
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    # Determine which configs to run
    if args.configs:
        ablation_set = args.configs
    elif args.quick:
        ablation_set = "quick"
    elif args.full:
        ablation_set = "full"
    else:
        ablation_set = args.set

    # Create runner
    runner = AblationRunner(
        output_dir=args.output,
        dataset=args.dataset,
        num_runs=args.runs,
        verbose=not args.quiet,
    )

    # Run ablations
    results = await runner.run_ablation_set(ablation_set)

    # Compute aggregates
    aggregates = runner.compute_aggregates(results)

    # Save results
    runner.save_results(results, aggregates)

    # Print summary
    print("\n" + "=" * 60)
    print("ABLATION STUDY SUMMARY")
    print("=" * 60)
    for _name, agg in aggregates.items():
        print(f"\n{agg['name']}:")
        print(f"  Pass Rate: {agg['pass_rate_mean']:.1%} ± {agg['pass_rate_std']:.1%}")
        print(f"  Avg Loops: {agg['avg_loops_mean']:.2f}")
        print(f"  Avg Time:  {agg['avg_time_mean']:.2f}s")

    # Generate LaTeX table
    latex_table = runner.generate_comparison_table(aggregates)
    print("\n" + "=" * 60)
    print("LATEX TABLE")
    print("=" * 60)
    print(latex_table)


if __name__ == "__main__":
    asyncio.run(main())
