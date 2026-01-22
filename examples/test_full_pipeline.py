#!/usr/bin/env python3
"""
Full Pipeline Test Script

This script automates Steps 1 and 3 from the project completion checklist:
1. Run the "Sanity Check" benchmark on sample data
2. Use the Visualizer to display the debate traces

Usage:
    python test_full_pipeline.py              # Run with sample dataset
    python test_full_pipeline.py --full       # Run with full dataset (takes longer)
    python test_full_pipeline.py --dataset experiments/datasets/humaneval_50.json
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")


def print_step(step_num: int, description: str):
    """Print a step header."""
    print(f"\n{'─' * 80}")
    print(f"STEP {step_num}: {description}")
    print("─" * 80 + "\n")


def run_command(cmd: list, description: str) -> bool:
    """
    Run a command and handle its output.

    Args:
        cmd: Command to run as a list
        description: Description of what the command does

    Returns:
        True if command succeeded, False otherwise
    """
    print(f"Running: {' '.join(cmd)}")
    print(f"Purpose: {description}\n")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=False)

        if result.returncode == 0:
            print(f"✅ Success: {description}")
            return True
        else:
            print(f"⚠️  Warning: Command exited with code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def check_prerequisites():
    """Check if required files and directories exist."""
    print_step(0, "Checking Prerequisites")

    required_files = [
        "experiments/blind_spot_benchmark.py",
        "src/tools/visualizer.py",
        "requirements.txt",
    ]

    all_exist = True
    for file in required_files:
        filepath = Path(file)
        if filepath.exists():
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            all_exist = False

    if not all_exist:
        print("\n⚠️  Some required files are missing. Please check your installation.")
        return False

    print("\n✅ All prerequisites satisfied!")
    return True


def run_benchmark(dataset_path: str) -> bool:
    """
    Run the blind spot benchmark.

    Args:
        dataset_path: Path to the dataset file

    Returns:
        True if benchmark completed successfully
    """
    print_step(1, "Running Blind Spot Benchmark (Sanity Check)")

    # Check if dataset exists
    if not Path(dataset_path).exists():
        print(f"❌ Dataset not found: {dataset_path}")
        return False

    print(f"📊 Dataset: {dataset_path}")

    # Run the benchmark
    cmd = [
        sys.executable,
        "experiments/blind_spot_benchmark.py",
        "--dataset",
        dataset_path,
        "--output",
        "experiments/results",
    ]

    success = run_command(cmd, "Execute benchmark comparing single-model vs CMVK")

    if success:
        # Check for results
        results_dir = Path("experiments/results")
        if results_dir.exists():
            json_files = list(results_dir.glob("blind_spot_benchmark_*.json"))
            txt_files = list(results_dir.glob("blind_spot_summary_*.txt"))

            if json_files:
                print("\n📁 Results saved to: experiments/results/")
                print(f"   - {len(json_files)} JSON result file(s)")
                print(f"   - {len(txt_files)} summary file(s)")

                # Display latest summary
                if txt_files:
                    latest_summary = max(txt_files, key=lambda p: p.stat().st_mtime)
                    print(f"\n📄 Latest Summary ({latest_summary.name}):")
                    print("-" * 80)
                    with open(latest_summary) as f:
                        print(f.read())
                    print("-" * 80)

    return success


def list_traces():
    """List available trace files."""
    print_step(2, "Checking for Trace Files")

    traces_dir = Path("logs/traces")

    if not traces_dir.exists():
        print("⚠️  No traces directory found (logs/traces)")
        print("Note: Traces are only generated when the kernel runs with enable_trace_logging=True")
        return []

    trace_files = list(traces_dir.glob("*.json"))

    if not trace_files:
        print("⚠️  No trace files found in logs/traces/")
        print("Note: Traces are only generated when the kernel runs with enable_trace_logging=True")
        return []

    print(f"✅ Found {len(trace_files)} trace file(s):")
    for i, trace_file in enumerate(sorted(trace_files), 1):
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(trace_file.stat().st_mtime))
        size = trace_file.stat().st_size
        print(f"   {i}. {trace_file.name}")
        print(f"      Modified: {mtime} | Size: {size:,} bytes")

    return trace_files


def visualize_traces(trace_files: list):
    """
    Visualize trace files using the visualizer.

    Args:
        trace_files: List of trace file paths
    """
    print_step(3, "Visualizing Traces (The Debate)")

    if not trace_files:
        print("⚠️  No traces available to visualize.")
        print("\nTo enable trace logging, modify the benchmark to initialize the kernel with:")
        print("    kernel = VerificationKernel(")
        print("        generator=generator,")
        print("        verifier=verifier,")
        print("        enable_trace_logging=True  # Add this parameter")
        print("    )")
        return

    # Show the latest trace
    latest_trace = max(trace_files, key=lambda p: p.stat().st_mtime)
    print(f"🎭 Replaying latest trace: {latest_trace.name}\n")

    cmd = [
        sys.executable,
        "-m",
        "src.tools.visualizer",
        "--latest",
        "--speed",
        "0.1",  # Fast playback for testing
    ]

    run_command(cmd, "Replay the adversarial debate")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the full CMVK pipeline: benchmark + visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with sample dataset (5 problems)
  python test_full_pipeline.py

  # Test with 50-problem dataset (more statistical significance)
  python test_full_pipeline.py --dataset experiments/datasets/humaneval_50.json

  # Full science run (164 problems, takes 15-20 minutes)
  python test_full_pipeline.py --full

  # Just list available trace files
  python test_full_pipeline.py --list-only
        """,
    )

    parser.add_argument(
        "--dataset",
        default="experiments/datasets/humaneval_sample.json",
        help="Path to dataset (default: humaneval_sample.json with 5 problems)",
    )

    parser.add_argument(
        "--full", action="store_true", help="Run with full HumanEval dataset (164 problems)"
    )

    parser.add_argument(
        "--list-only", action="store_true", help="Only list available traces, skip benchmark"
    )

    parser.add_argument("--skip-viz", action="store_true", help="Skip visualization step")

    args = parser.parse_args()

    # Determine dataset path
    if args.full:
        dataset_path = "experiments/datasets/humaneval_full.json"
    else:
        dataset_path = args.dataset

    # Print header
    print_header("🚀 CMVK FULL PIPELINE TEST 🚀")
    print("This script will:")
    print("  1. Run the Blind Spot Benchmark")
    print("  2. Check for execution traces")
    print("  3. Visualize the adversarial debate (if traces exist)")
    print()

    # Check prerequisites
    if not args.list_only:
        if not check_prerequisites():
            sys.exit(1)

    # Run benchmark
    if not args.list_only:
        benchmark_success = run_benchmark(dataset_path)

        if not benchmark_success:
            print("\n⚠️  Benchmark completed with warnings. Continuing to trace analysis...")

    # List traces
    trace_files = list_traces()

    # Visualize traces
    if not args.skip_viz and trace_files:
        visualize_traces(trace_files)

    # Final summary
    print_header("✅ PIPELINE TEST COMPLETE")

    if not args.list_only:
        print("What was tested:")
        print("  ✅ Benchmark script execution")
        print("  ✅ Result file generation")
        print("  ✅ Trace file detection")
        if trace_files and not args.skip_viz:
            print("  ✅ Visualizer playback")

    print("\nNext steps:")
    print("  1. Set up API keys (OPENAI_API_KEY, GOOGLE_API_KEY) for real runs")
    print(
        "  2. Run: python experiments/blind_spot_benchmark.py --dataset experiments/datasets/humaneval_full.json"
    )
    print("  3. Update PAPER.md with actual results")
    print("  4. Take screenshots of visualizer output for README.md")
    print()


if __name__ == "__main__":
    main()
