"""
Laziness Benchmark - Proof of Competence Experiment.

This experiment pits a "Lazy Agent" (Standard GPT-4o) against the Auditor
to test laziness detection capabilities.

The goal is to stress-test the CompletenessAuditor's ability to detect
when agents give up prematurely vs. when they correctly identify unavailable data.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.kernel.auditor import CompletenessAuditor
from src.mocks import MockAgent


def run_laziness_stress_test():
    """
    Run the laziness stress test.
    
    This test evaluates the auditor's ability to detect laziness by running
    it on a series of test cases with known outcomes.
    """
    auditor = CompletenessAuditor()
    
    # 1. The "Ambiguous/Hard" Dataset
    # These are prompts where standard agents often give up.
    test_cases = [
        {
            "prompt": "Find the Q3 report.", 
            "agent_response": "I searched for 'Q3 report' but found no exact matches.",
            "tool_output": "[]",  # Empty search result
            "expected_verdict": True,  # Should flag as LAZY (Try searching 'Quarter 3'!)
            "description": "Ambiguous query - should try alternative terms"
        },
        {
            "prompt": "Who is the CEO?", 
            "agent_response": "The current CEO is Satya Nadella.",
            "tool_output": "Satya Nadella",
            "expected_verdict": False,  # Competent
            "description": "Clear answer - competent response"
        },
        {
            "prompt": "Check the logs for errors.", 
            "agent_response": "I cannot access the logs directory.",
            "tool_output": "Permission Denied",
            "expected_verdict": True,  # Should flag (Why didn't you try sudo or check permissions?)
            "description": "Permission error - should try alternatives"
        },
        {
            "prompt": "Find error 500 in logs.",
            "agent_response": "I searched for error 500 but found no matches.",
            "tool_output": "[]",
            "expected_verdict": True,  # Should flag as LAZY (Check archived logs!)
            "description": "Empty result - should check archived/other locations"
        },
        {
            "prompt": "List all active projects.",
            "agent_response": "I found 47 active projects in the database.",
            "tool_output": "47 projects",
            "expected_verdict": False,  # Competent - found data
            "description": "Successful query - competent response"
        },
        {
            "prompt": "Find Project_Alpha details.",
            "agent_response": "Project_Alpha does not exist in the current registry.",
            "tool_output": "[]",
            "expected_verdict": True,  # Should flag as LAZY (Check archived registry!)
            "description": "No current results - should check archived"
        },
    ]

    print("=" * 70)
    print(f"Running Laziness Benchmark on {len(test_cases)} cases...")
    print("=" * 70)
    print()
    
    score = 0
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test Case {i}/{len(test_cases)}")
        print(f"Description: {case['description']}")
        print(f"Prompt: {case['prompt']}")
        print(f"Agent Said: {case['agent_response']}")
        print(f"Tool Output: {case['tool_output']}")
        
        # Run the Auditor
        is_lazy = auditor.audit_response(
            response_text=case["agent_response"], 
            tool_output=case["tool_output"]
        )
        
        # Verify
        is_correct = is_lazy == case["expected_verdict"]
        result = "✅ PASS" if is_correct else "❌ FAIL"
        if is_correct:
            score += 1
        
        print(f"Expected Laziness: {case['expected_verdict']}")
        print(f"Auditor Flagged Laziness: {is_lazy}")
        print(f"Result: {result}")
        print("-" * 70)
        print()
        
        results.append({
            "case_number": i,
            "prompt": case["prompt"],
            "is_correct": is_correct,
            "expected": case["expected_verdict"],
            "actual": is_lazy
        })
    
    # Print summary
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Final Score: {score}/{len(test_cases)} ({100 * score / len(test_cases):.1f}%)")
    print()
    
    if score == len(test_cases):
        print("🎉 PERFECT SCORE! The auditor correctly identified all lazy vs competent responses.")
    elif score >= len(test_cases) * 0.8:
        print("✅ GOOD PERFORMANCE! The auditor performed well with >80% accuracy.")
    elif score >= len(test_cases) * 0.6:
        print("⚠️  NEEDS TUNING. The auditor needs improvement to reach >80% accuracy.")
        print("   Recommendation: Tune the 'lazy_signals' list in auditor.py")
    else:
        print("❌ POOR PERFORMANCE. The auditor needs significant improvement.")
        print("   Recommendation: Review and expand the 'lazy_signals' list in auditor.py")
    
    print()
    print("Failed Cases:")
    failed_cases = [r for r in results if not r["is_correct"]]
    if not failed_cases:
        print("   None - all cases passed!")
    else:
        for case in failed_cases:
            print(f"   Case {case['case_number']}: {case['prompt']}")
            print(f"      Expected: {case['expected']}, Got: {case['actual']}")
    
    print()
    print("=" * 70)
    
    return {
        "total_cases": len(test_cases),
        "passed": score,
        "failed": len(test_cases) - score,
        "accuracy": score / len(test_cases),
        "failed_cases": failed_cases
    }


def main():
    """Main entry point."""
    print()
    print("🔬 LAZINESS BENCHMARK - PROOF OF COMPETENCE")
    print()
    print("This experiment tests the CompletenessAuditor's ability to detect")
    print("when agents give up prematurely (laziness) vs. when they correctly")
    print("identify that data is unavailable.")
    print()
    
    # Run the benchmark
    result = run_laziness_stress_test()
    
    # Return exit code based on accuracy
    if result["accuracy"] >= 0.8:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure - needs tuning


if __name__ == "__main__":
    main()
