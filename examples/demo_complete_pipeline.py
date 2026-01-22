#!/usr/bin/env python3
"""
Demo: Complete Workflow for Cross-Model Verification Kernel

This demo shows the full pipeline from data loading to visualization:
1. Load problems from HumanEval dataset
2. Run experiments (simulated - no real API calls for demo)
3. Visualize the traces

Run this demo to see all the new features in action.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cross_model_verification_kernel.core.trace_logger import TraceLogger
from cross_model_verification_kernel.core.types import ExecutionTrace, NodeState
from cross_model_verification_kernel.datasets.humaneval_loader import HumanEvalLoader


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_humaneval_loader():
    """Demonstrate the HumanEval loader."""
    print_header("STEP 1: HumanEval Dataset Loader")

    print("Loading HumanEval sample dataset...")
    loader = HumanEvalLoader()

    print(f"✅ Loaded {len(loader)} problems")
    print("\nSample problems:")

    for i, problem in enumerate(loader.get_problem_subset(0, 3), 1):
        print(f"  {i}. {problem['task_id']} - {problem['entry_point']}")

    print("\n📝 Formatting problems for kernel...")
    formatted = loader.format_all_for_kernel(start=0, count=3)

    print(f"✅ Formatted {len(formatted)} problems")
    print(f"\nExample formatted problem ID: {formatted[0]['id']}")
    print(f"Query preview: {formatted[0]['query'][:100]}...")

    return formatted


def demo_trace_generation(problems):
    """Demonstrate trace generation (simulated)."""
    print_header("STEP 2: Generating Traces (Simulated)")

    print("In a real experiment, this would:")
    print("  1. Run baseline (single GPT-4o) on each problem")
    print("  2. Run CMVK (GPT-4o + Gemini) on each problem")
    print("  3. Save traces to logs/traces/")

    print("\nFor demo purposes, generating a sample trace...")

    # Create a simulated trace
    state = NodeState(
        input_query=problems[0]["query"][:100] + "...",
        current_code="def solution():\n    # Final verified solution\n    pass",
        status="verified",
    )

    # Add some history
    trace1 = ExecutionTrace(
        step_id=1,
        code_generated="def solution():\n    # First attempt\n    return []",
        verifier_feedback="OBJECTION! Missing edge case handling for empty input",
        status="failed",
        strategy_used="naive",
    )

    trace2 = ExecutionTrace(
        step_id=2,
        code_generated="def solution():\n    # Second attempt with edge cases\n    if not input:\n        return default\n    return process(input)",
        verifier_feedback="PASS: Correctly handles edge cases",
        status="success",
        strategy_used="defensive",
    )

    state.history.extend([trace1, trace2])
    state.forbidden_strategies.append("naive")

    # Save trace
    logger = TraceLogger()
    trace_file = logger.save_trace("demo_experiment", state)

    print("\n✅ Sample trace generated and saved")

    return trace_file


def demo_visualizer(trace_file):
    """Demonstrate the trace visualizer."""
    print_header("STEP 3: Visualizing Traces")

    print("The visualizer replays traces as adversarial debates:")
    print(f"\nCommand: python -m src.tools.visualizer {trace_file}\n")

    print("Output shows:")
    print("  🎭 Problem statement")
    print("  🔄 Each attempt with:")
    print("     - Builder (GPT-4o) generating solution")
    print("     - Prosecutor (Gemini) finding flaws")
    print("     - Kernel making decisions")
    print("  🏁 Final result and statistics")

    print("\n💡 Try these commands:")
    print("  python -m src.tools.visualizer --list")
    print("  python -m src.tools.visualizer --latest")
    print(f"  python -m src.tools.visualizer {trace_file} --speed 0")


def demo_paper_generator():
    """Demonstrate the updated paper data generator."""
    print_header("STEP 4: Scaling Experiments")

    print("The paper_data_generator.py now supports HumanEval:\n")

    print("📊 Run experiments at different scales:")
    print("\n  # Small scale (5 problems)")
    print("  python experiments/paper_data_generator.py --humaneval --count 5")

    print("\n  # Medium scale (50 problems - suitable for paper)")
    print("  python experiments/paper_data_generator.py --humaneval --count 50")

    print("\n  # Full dataset (all problems)")
    print("  python experiments/paper_data_generator.py --humaneval")

    print("\n  # Legacy mode (original 2 problems)")
    print("  python experiments/paper_data_generator.py --legacy")


def demo_paper_structure():
    """Show the paper structure."""
    print_header("STEP 5: Research Paper Draft")

    print("PAPER.md contains the complete research narrative:\n")

    sections = [
        ("Abstract", "Overview of CMVK and key results"),
        ("Introduction", "Problem statement and motivation"),
        ("Methodology", "Architecture and adversarial design"),
        ("Experiments", "HumanEval benchmark and results"),
        ("Tools", "Reproducibility and visualization"),
        ("Discussion", "Why multi-model verification works"),
        ("Conclusion", "Key insights and future work"),
    ]

    for section, description in sections:
        print(f"  📄 {section:20} - {description}")

    print("\n💡 Next steps for publication:")
    print("  1. Run full HumanEval experiments (n=50+)")
    print("  2. Fill in results tables in Section 3.3")
    print("  3. Add system prompts to Appendix A")
    print("  4. Include example traces in Appendix B")


def main():
    """Run the complete demo."""
    print("\n" + "=" * 80)
    print("  🎭 CROSS-MODEL VERIFICATION KERNEL (CMVK) - DEMO  🎭")
    print("  From Engineering to Science: The Complete Pipeline")
    print("=" * 80)

    # Step 1: Load data
    problems = demo_humaneval_loader()

    # Step 2: Generate traces
    trace_file = demo_trace_generation(problems)

    # Step 3: Visualize
    demo_visualizer(trace_file)

    # Step 4: Scale experiments
    demo_paper_generator()

    # Step 5: Paper structure
    demo_paper_structure()

    # Summary
    print_header("🎉 DEMO COMPLETE")

    print("You now have a complete research pipeline:")
    print("\n✅ Data ingestion (HumanEval)")
    print("✅ Experiment automation (paper_data_generator.py)")
    print("✅ Traceability (TraceLogger)")
    print("✅ Visualization (visualizer.py)")
    print("✅ Research narrative (PAPER.md)")

    print("\n🚀 Ready to publish! Next immediate actions:")
    print("\n1. Set up API keys for OpenAI and Gemini")
    print("2. Run: python experiments/paper_data_generator.py --humaneval --count 5")
    print("3. Review traces: python -m src.tools.visualizer --latest")
    print("4. Scale to 50+ problems for statistical significance")

    print("\n📖 Read PAPER.md for complete methodology and context")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
