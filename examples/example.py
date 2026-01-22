#!/usr/bin/env python3
"""
Simple example demonstrating the Cross-Model Verification Kernel.

This shows how to use CMVK to solve a simple programming task
with adversarial verification.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging

from src import GeminiVerifier, OpenAIGenerator, VerificationKernel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run a simple example task."""
    print("=" * 60)
    print("Cross-Model Verification Kernel - Example")
    print("=" * 60)
    print()

    # Define a task
    task = """
Write a Python function called 'fibonacci' that takes an integer n
and returns the nth Fibonacci number. Handle edge cases for n < 0.
Include proper error handling and docstrings.
"""

    print(f"Task: {task.strip()}")
    print()

    try:
        # Initialize agents
        logger.info("Initializing agents...")
        generator = OpenAIGenerator(model_name="gpt-4o")
        verifier = GeminiVerifier(model_name="gemini-1.5-pro")

        # Create kernel
        logger.info("Creating verification kernel...")
        kernel = VerificationKernel(
            generator=generator, verifier=verifier, config_path="config/settings.yaml"
        )

        # Execute verification loop
        logger.info("Starting verification loop...")
        print("Executing verification loop...")
        print()

        result = kernel.execute(task)

        # Display results
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Success: {result.is_complete}")
        print(f"Verification Loops: {result.current_loop}/{result.max_loops}")
        print(f"Total Verifications: {len(result.verification_history)}")
        print()

        if result.final_result:
            print("Final Solution:")
            print("-" * 60)
            print(result.final_result)
            print("-" * 60)
        else:
            print("No solution found.")

        # Display verification history
        if result.verification_history:
            print()
            print("Verification History:")
            for i, verification in enumerate(result.verification_history):
                print(f"\nLoop {i+1}:")
                print(f"  Outcome: {verification.outcome.value}")
                print(f"  Confidence: {verification.confidence:.2f}")
                if verification.critical_issues:
                    print(f"  Critical Issues: {len(verification.critical_issues)}")
                if verification.logic_flaws:
                    print(f"  Logic Flaws: {len(verification.logic_flaws)}")

        # Display graph stats
        stats = kernel.get_graph_stats()
        print()
        print("Graph Statistics:")
        print(f"  Total Nodes: {stats['total_nodes']}")
        print(f"  Verified Nodes: {stats['verified_nodes']}")
        print(f"  Failed Nodes: {stats['failed_nodes']}")

    except Exception as e:
        logger.error(f"Error: {e}")
        print()
        print("ERROR: Could not complete execution.")
        print("Make sure you have set your API keys:")
        print("  export OPENAI_API_KEY='your-key'")
        print("  export GOOGLE_API_KEY='your-key'")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
