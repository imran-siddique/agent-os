"""
Experiment B: Sabotage Stress Test

This experiment evaluates the verifier's ability to detect subtle bugs
in code using the Prosecutor Mode hostile testing.

Goal: Prove the Verifier actually catches bugs (Recall Rate).
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cross_model_verification_kernel.agents.verifier_gemini import GeminiVerifier
from cross_model_verification_kernel.core.types import VerificationOutcome

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SabotageStressTest:
    """
    Runs the Sabotage Stress Test experiment.

    This evaluates the verifier's bug detection capabilities by testing
    it against a dataset of valid and buggy code samples.
    """

    def __init__(
        self,
        dataset_path: str = "experiments/datasets/sabotage.json",
        output_dir: str = "experiments/results",
    ):
        """
        Initialize the experiment.

        Args:
            dataset_path: Path to sabotage dataset
            output_dir: Directory to save results
        """
        self.dataset_path = Path(dataset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize verifier with prosecutor mode
        try:
            self.verifier = GeminiVerifier(enable_prosecutor_mode=True)
            logger.info("Initialized verifier with Prosecutor Mode")
        except Exception as e:
            logger.warning(f"Failed to initialize with real API: {e}")
            logger.info("Running in mock mode for testing")
            self.verifier = GeminiVerifier(enable_prosecutor_mode=False)

    def load_dataset(self) -> list[dict[str, Any]]:
        """Load the sabotage dataset."""
        with open(self.dataset_path) as f:
            dataset = json.load(f)

        logger.info(f"Loaded {len(dataset)} test cases from {self.dataset_path}")
        return dataset

    def run_experiment(self) -> dict[str, Any]:
        """
        Run the sabotage stress test experiment.

        Returns:
            Dictionary with experiment results and metrics
        """
        logger.info("Starting Sabotage Stress Test Experiment")

        dataset = self.load_dataset()

        results = {
            "experiment": "sabotage_stress_test",
            "dataset": str(self.dataset_path),
            "total_cases": len(dataset),
            "valid_cases": sum(1 for item in dataset if item["type"] == "valid"),
            "buggy_cases": sum(1 for item in dataset if item["type"] == "buggy"),
            "true_positives": 0,  # Correctly identified bugs
            "true_negatives": 0,  # Correctly identified valid code
            "false_positives": 0,  # Incorrectly flagged valid code as buggy
            "false_negatives": 0,  # Missed bugs
            "test_results": [],
            "total_time": 0,
        }

        # Process each test case
        for i, test_case in enumerate(dataset):
            logger.info(f"Processing test case {i+1}/{len(dataset)}: {test_case['id']}")

            start_time = time.time()
            result = self._verify_test_case(test_case)
            elapsed = time.time() - start_time

            result["time"] = elapsed
            results["test_results"].append(result)
            results["total_time"] += elapsed

            # Update metrics
            if test_case["type"] == "buggy":
                if result["detected_bug"]:
                    results["true_positives"] += 1
                else:
                    results["false_negatives"] += 1
            else:  # valid
                if result["detected_bug"]:
                    results["false_positives"] += 1
                else:
                    results["true_negatives"] += 1

        # Calculate metrics
        results["metrics"] = self._calculate_metrics(results)

        # Save results
        self._save_results(results)

        logger.info(
            f"Experiment complete: Recall={results['metrics']['recall']:.2%}, "
            f"Precision={results['metrics']['precision']:.2%}"
        )

        return results

    def _verify_test_case(self, test_case: dict[str, Any]) -> dict[str, Any]:
        """
        Verify a single test case.

        Args:
            test_case: The test case to verify

        Returns:
            Dictionary with verification results
        """
        context = {
            "task": test_case.get("description", "Verify this code"),
            "solution": test_case["code"],
            "explanation": test_case.get("description", ""),
            "test_cases": "",
        }

        try:
            verification_result = self.verifier.verify(context)

            # A bug is detected if:
            # 1. Verification fails (outcome is FAIL)
            # 2. There are critical issues
            # 3. Hostile tests failed
            detected_bug = (
                verification_result.outcome == VerificationOutcome.FAIL
                or verification_result.has_critical_issues()
                or (
                    verification_result.hostile_test_results
                    and verification_result.hostile_test_results.get("failures", 0) > 0
                )
            )

            return {
                "test_id": test_case["id"],
                "type": test_case["type"],
                "detected_bug": detected_bug,
                "outcome": verification_result.outcome.value,
                "confidence": verification_result.confidence,
                "critical_issues": verification_result.critical_issues,
                "hostile_tests_count": (
                    len(verification_result.hostile_tests)
                    if verification_result.hostile_tests
                    else 0
                ),
                "hostile_test_failures": (
                    verification_result.hostile_test_results.get("failures", 0)
                    if verification_result.hostile_test_results
                    else 0
                ),
                "reasoning": (
                    verification_result.reasoning[:200] if verification_result.reasoning else ""
                ),
            }

        except Exception as e:
            logger.error(f"Error verifying test case {test_case['id']}: {e}")
            return {
                "test_id": test_case["id"],
                "type": test_case["type"],
                "detected_bug": False,
                "error": str(e),
            }

    def _calculate_metrics(self, results: dict[str, Any]) -> dict[str, float]:
        """Calculate precision, recall, and F1 score."""
        tp = results["true_positives"]
        tn = results["true_negatives"]
        fp = results["false_positives"]
        fn = results["false_negatives"]

        # Precision: Of all bugs we detected, how many were real?
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        # Recall: Of all real bugs, how many did we detect? (Most important!)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # F1 Score: Harmonic mean of precision and recall
        f1_score = (
            2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        )

        # Accuracy: Overall correctness
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": accuracy,
        }

    def _save_results(self, results: dict[str, Any]) -> None:
        """Save results to JSON file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"sabotage_stress_test_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {output_file}")

        # Also create a summary file
        summary_file = self.output_dir / f"sabotage_summary_{timestamp}.txt"
        with open(summary_file, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("SABOTAGE STRESS TEST RESULTS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Cases: {results['total_cases']}\n")
            f.write(f"Valid Cases: {results['valid_cases']}\n")
            f.write(f"Buggy Cases: {results['buggy_cases']}\n\n")
            f.write(f"True Positives (Bugs Caught): {results['true_positives']}\n")
            f.write(f"True Negatives (Valid Passed): {results['true_negatives']}\n")
            f.write(f"False Positives (Valid Flagged): {results['false_positives']}\n")
            f.write(f"False Negatives (Bugs Missed): {results['false_negatives']}\n\n")
            f.write("METRICS:\n")
            f.write(f"Recall (Bug Detection Rate): {results['metrics']['recall']:.2%}\n")
            f.write(f"Precision: {results['metrics']['precision']:.2%}\n")
            f.write(f"F1 Score: {results['metrics']['f1_score']:.2%}\n")
            f.write(f"Accuracy: {results['metrics']['accuracy']:.2%}\n\n")
            f.write(f"Total Time: {results['total_time']:.2f}s\n")
            f.write(f"Average Time per Case: {results['total_time']/results['total_cases']:.2f}s\n")

        logger.info(f"Summary saved to {summary_file}")


def main():
    """Run the sabotage stress test."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the Sabotage Stress Test to evaluate verifier bug detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default dataset
  python experiments/sabotage_stress_test.py

  # Specify custom dataset and output directory
  python experiments/sabotage_stress_test.py --dataset custom.json --output results/
        """,
    )

    parser.add_argument(
        "--dataset",
        default="experiments/datasets/sabotage.json",
        help="Path to sabotage dataset (default: experiments/datasets/sabotage.json)",
    )

    parser.add_argument(
        "--output",
        default="experiments/results",
        help="Output directory for results (default: experiments/results)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("SABOTAGE STRESS TEST")
    print("=" * 80)
    print(f"Dataset: {args.dataset}")
    print(f"Output: {args.output}")
    print("=" * 80 + "\n")

    experiment = SabotageStressTest(dataset_path=args.dataset, output_dir=args.output)
    results = experiment.run_experiment()

    print("\n" + "=" * 60)
    print("SABOTAGE STRESS TEST COMPLETED")
    print("=" * 60)
    print(f"Recall (Bug Detection Rate): {results['metrics']['recall']:.2%}")
    print(f"Precision: {results['metrics']['precision']:.2%}")
    print(f"F1 Score: {results['metrics']['f1_score']:.2%}")
    print(f"Accuracy: {results['metrics']['accuracy']:.2%}")
    print("=" * 60)


if __name__ == "__main__":
    main()
