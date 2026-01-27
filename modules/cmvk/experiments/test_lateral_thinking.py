"""
Experiment: Lateral Thinking Feature Test

This experiment tests Feature 2: Lateral Thinking (Graph Branching).
It validates that the kernel can detect failed strategies and branch to different approaches.

Scenario: Ask for a factorial function, but ban recursion.
- Round 1: Agent tries Recursion (Default). Verifier fails it (simulated constraint or logic check).
- Round 2: Kernel bans "Recursion". Agent switches to math.factorial or Iteration.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cross_model_verification_kernel.agents.generator_openai import OpenAIGenerator
from cross_model_verification_kernel.agents.verifier_gemini import GeminiVerifier
from cross_model_verification_kernel.core.kernel import VerificationKernel


def main():
    """
    Run the Lateral Thinking experiment.

    This simulates the flow where:
    1. Generator writes recursive code.
    2. Verifier (Prosecutor) writes a test with input=10000.
    3. Code crashes (RecursionError).
    4. Kernel adds "Recursion" to forbidden list.
    5. Generator rewrites using 'for' loop.
    """
    print("=" * 80)
    print("EXPERIMENT: Lateral Thinking (Graph Branching)")
    print("=" * 80)
    print()

    # Initialize the kernel
    generator = OpenAIGenerator()
    verifier = GeminiVerifier()
    kernel = VerificationKernel(generator=generator, verifier=verifier)

    # Define the query that will force lateral thinking
    query = "Calculate the factorial of a number. Ensure it handles stack overflow risks for large inputs."

    print(f"Query: {query}")
    print()
    print("Starting verification loop...")
    print("=" * 80)
    print()

    # Execute the kernel
    result = kernel.execute(query)

    print()
    print("=" * 80)
    print("EXPERIMENT RESULTS")
    print("=" * 80)
    print()

    if result.is_complete:
        print("✅ Solution found!")
        print()
        print("Final Solution:")
        print("-" * 80)
        print(result.final_result)
        print("-" * 80)
    else:
        print("❌ No solution found within max iterations")

    print()
    print("Statistics:")
    print(f"- Total loops: {result.current_loop}/{result.max_loops}")
    print(f"- Verification attempts: {len(result.verification_history)}")

    # Get graph statistics to see lateral thinking in action
    stats = kernel.get_graph_stats()
    print()
    print("Graph Statistics:")
    print(f"- Total nodes: {stats['total_nodes']}")
    print(f"- Verified nodes: {stats['verified_nodes']}")
    print(f"- Failed nodes: {stats['failed_nodes']}")
    print(f"- Approach failures: {stats['approach_failures']}")
    print(f"- Forbidden approaches: {stats['forbidden_approaches']}")
    print(f"- Conversation entries: {stats['conversation_entries']}")

    # Show verification history
    print()
    print("Verification History:")
    print("-" * 80)
    for i, verification in enumerate(result.verification_history, 1):
        print(f"Attempt {i}:")
        print(f"  - Outcome: {verification.outcome.value}")
        print(f"  - Confidence: {verification.confidence:.2f}")
        print(f"  - Critical Issues: {len(verification.critical_issues)}")
        print(f"  - Logic Flaws: {len(verification.logic_flaws)}")
        print(f"  - Missing Edge Cases: {len(verification.missing_edge_cases)}")
        if verification.hostile_tests:
            print(f"  - Hostile Tests Generated: {len(verification.hostile_tests)}")
        print()

    # Export conversation trace
    trace_file = Path(__file__).parent / "outputs" / "lateral_thinking_trace.json"
    trace_file.parent.mkdir(exist_ok=True)
    kernel.export_conversation_trace(str(trace_file))
    print(f"📊 Conversation trace exported to: {trace_file}")

    print()
    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
