#!/usr/bin/env python3
"""
Demo: Running Benchmark with Trace Logging Enabled

This script demonstrates how to run the benchmark with trace logging enabled
so that you can visualize the adversarial debate using the visualizer tool.

By default, the benchmark runs without trace logging to save disk space.
This demo shows how to enable it for analysis and visualization.

Usage:
    python experiments/demo_with_traces.py
"""
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


from src import GeminiVerifier, OpenAIGenerator, VerificationKernel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_with_traces():
    """Run a simple example with trace logging enabled."""
    print("\n" + "=" * 80)
    print("DEMO: Cross-Model Verification with Trace Logging")
    print("=" * 80 + "\n")

    # Load a sample problem
    dataset_path = Path("experiments/datasets/humaneval_sample.json")

    if not dataset_path.exists():
        print(f"❌ Sample dataset not found: {dataset_path}")
        print("Please ensure the dataset exists.")
        return

    with open(dataset_path) as f:
        problems = json.load(f)

    # Take the first problem
    problem = problems[0]
    print(f"📋 Problem: {problem['task_id']}")
    print(f"   Entry Point: {problem['entry_point']}")
    print()

    try:
        # Initialize agents
        generator = OpenAIGenerator()
        verifier = GeminiVerifier(enable_prosecutor_mode=True)

        # Initialize kernel WITH trace logging enabled
        kernel = VerificationKernel(
            generator=generator,
            verifier=verifier,
            enable_trace_logging=True,  # ← This enables trace logging!
        )

        print("✅ Initialized CMVK system with trace logging enabled")
        print()

        # Prepare the task
        task = f"{problem['prompt']}\n\nImplement the function above."

        # Execute with CMVK
        print("🚀 Starting verification loop...")
        print("   This will generate a trace file in logs/traces/")
        print()

        state = kernel.execute(task)

        print("\n✅ Execution complete!")
        print(f"   Success: {state.is_complete}")
        print(f"   Loops: {state.current_loop}")

        # Note: Trace logging integration is planned but not yet implemented
        # The TraceLogger exists but needs to be called explicitly after execution
        print()
        print("ℹ️  Note: Automatic trace generation from the kernel is not yet implemented.")
        print("   The trace logging infrastructure exists but needs integration.")
        print()
        print("To manually create traces for testing the visualizer:")
        print("  1. The TraceLogger class exists in src/core/trace_logger.py")
        print("  2. The Visualizer works with NodeState JSON traces")
        print("  3. See test_trace_logger.py for examples of creating traces")

    except Exception as e:
        print(f"⚠️  Error: {e}")
        print()
        print("To run with real APIs:")
        print("  1. Set environment variables: OPENAI_API_KEY, GOOGLE_API_KEY")
        print("  2. Install API libraries: pip install openai google-generativeai")
        print("  3. Run this script again")

    print()
    print("=" * 80)
    print("Demo complete!")
    print("=" * 80)


if __name__ == "__main__":
    run_with_traces()
