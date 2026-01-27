"""
Experiment Runner - Runs experiments using the "New Way" (Cross-Model Verification).

This script evaluates the cross-model verification approach and compares
it against the baseline.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import GeminiVerifier, OpenAIGenerator, VerificationKernel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """
    Runs experiments using the Cross-Model Verification Kernel.

    This evaluates the effectiveness of adversarial multi-model verification
    and provides metrics for comparison with the baseline.
    """

    def __init__(
        self, config_path: str = "config/settings.yaml", output_dir: str = "experiments/results"
    ):
        """
        Initialize the experiment runner.

        Args:
            config_path: Path to configuration file
            output_dir: Directory to save results
        """
        self.config_path = config_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize agents
        try:
            self.generator = OpenAIGenerator()
            self.verifier = GeminiVerifier()
            self.kernel = VerificationKernel(
                generator=self.generator, verifier=self.verifier, config_path=config_path
            )
            logger.info("Experiment runner initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize with real APIs: {e}")
            logger.info("Running in mock mode for testing")
            self.kernel = None

    def run_dataset(self, dataset_path: str) -> dict[str, Any]:
        """
        Run experiments on a dataset.

        Args:
            dataset_path: Path to dataset file

        Returns:
            Results dictionary with metrics
        """
        logger.info(f"Running experiments on dataset: {dataset_path}")

        # Load dataset
        tasks = self._load_dataset(dataset_path)

        results = {
            "approach": "cross-model-verification",
            "generator": "gpt-4o",
            "verifier": "gemini-1.5-pro",
            "dataset": dataset_path,
            "total_tasks": len(tasks),
            "successful": 0,
            "failed": 0,
            "loops_used": [],
            "total_time": 0,
            "task_results": [],
        }

        # Run each task
        for i, task in enumerate(tasks):
            logger.info(f"Processing task {i+1}/{len(tasks)}")

            start_time = time.time()
            task_result = self._run_single_task(task)
            elapsed = time.time() - start_time

            task_result["time"] = elapsed
            results["task_results"].append(task_result)
            results["total_time"] += elapsed
            results["loops_used"].append(task_result.get("loops", 0))

            if task_result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1

        # Calculate metrics
        if results["total_tasks"] > 0:
            results["accuracy"] = results["successful"] / results["total_tasks"]
            results["avg_time"] = results["total_time"] / results["total_tasks"]
        else:
            results["accuracy"] = 0.0
            results["avg_time"] = 0.0

        if results["loops_used"]:
            results["avg_loops"] = sum(results["loops_used"]) / len(results["loops_used"])
        else:
            results["avg_loops"] = 0.0

        # Save results
        self._save_results(results, "cross_model")

        logger.info(f"Experiments complete: {results['accuracy']:.2%} accuracy")
        logger.info(f"Average loops: {results['avg_loops']:.2f}")
        return results

    def _run_single_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Run a single task with the verification kernel.

        Args:
            task: Task dictionary

        Returns:
            Result dictionary
        """
        if self.kernel is None:
            return {
                "task_id": task.get("id", "unknown"),
                "success": False,
                "solution": "# Mock mode",
                "error": "Kernel not initialized (API keys missing)",
                "loops": 0,
            }

        try:
            # Execute with kernel
            state = self.kernel.execute(task.get("description", ""))

            return {
                "task_id": task.get("id", "unknown"),
                "success": state.is_complete and state.final_result is not None,
                "solution": state.final_result,
                "loops": state.current_loop,
                "verification_count": len(state.verification_history),
            }
        except Exception as e:
            logger.error(f"Error running task: {e}")
            return {
                "task_id": task.get("id", "unknown"),
                "success": False,
                "solution": None,
                "error": str(e),
                "loops": 0,
            }

    def _load_dataset(self, dataset_path: str) -> list[dict[str, Any]]:
        """Load dataset from file."""
        path = Path(dataset_path)

        if not path.exists():
            logger.warning(f"Dataset not found: {dataset_path}, using mock data")
            return self._get_mock_dataset()

        with open(path) as f:
            data = json.load(f)

        return data.get("tasks", [])

    def _get_mock_dataset(self) -> list[dict[str, Any]]:
        """Return a mock dataset for testing."""
        return [
            {
                "id": "task_1",
                "description": "Write a function to reverse a string",
                "expected_output": "function that reverses strings",
            },
            {
                "id": "task_2",
                "description": "Implement binary search",
                "expected_output": "binary search implementation",
            },
        ]

    def _save_results(self, results: dict[str, Any], experiment_name: str) -> None:
        """Save results to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{experiment_name}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {filename}")

    def compare_with_baseline(
        self, baseline_results: dict[str, Any], cmvk_results: dict[str, Any]
    ) -> None:
        """
        Compare CMVK results with baseline.

        Args:
            baseline_results: Baseline experiment results
            cmvk_results: CMVK experiment results
        """
        print("\n" + "=" * 60)
        print("COMPARISON: Baseline vs. Cross-Model Verification")
        print("=" * 60)

        print("\nAccuracy:")
        print(f"  Baseline: {baseline_results['accuracy']:.2%}")
        print(f"  CMVK:     {cmvk_results['accuracy']:.2%}")
        print(
            f"  Accuracy difference (percentage points): {(cmvk_results['accuracy'] - baseline_results['accuracy'])*100:.2f}"
        )

        print("\nAverage Time:")
        print(f"  Baseline: {baseline_results['avg_time']:.2f}s")
        print(f"  CMVK:     {cmvk_results['avg_time']:.2f}s")

        if "avg_loops" in cmvk_results:
            print(f"\nAverage Verification Loops: {cmvk_results['avg_loops']:.2f}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    runner = ExperimentRunner()
    results = runner.run_dataset("experiments/datasets/sample.json")
    print("\nCross-Model Verification Results:")
    print(f"Accuracy: {results['accuracy']:.2%}")
    print(f"Avg Time: {results['avg_time']:.2f}s")
    print(f"Avg Loops: {results.get('avg_loops', 0):.2f}")
