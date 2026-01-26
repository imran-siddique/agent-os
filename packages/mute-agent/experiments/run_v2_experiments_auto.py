"""
Mute Agent v2: Automated Test Suite Runner (Non-interactive)

Runs all 4 scenario suites automatically without user prompts.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path to allow imports when running this script directly
# This is necessary because experiments can be run from various working directories
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from v2_scenarios.scenario_1_deep_dependency import run_deep_dependency_experiment
from v2_scenarios.scenario_2_adversarial import run_adversarial_experiment
from v2_scenarios.scenario_3_false_positive import run_synonym_experiment
from v2_scenarios.scenario_4_performance import run_performance_experiments


def print_header():
    """Print the main header."""
    print("\n")
    print("=" * 80)
    print("=" * 80)
    print("                    MUTE AGENT V2: ROBUSTNESS & SCALE")
    print("           Validating Graph Constraints vs Prompt Engineering")
    print("=" * 80)
    print("=" * 80)
    print()


def print_summary(all_results):
    """Print final summary of all experiments."""
    print("\n")
    print("=" * 80)
    print("=" * 80)
    print("                         FINAL SUMMARY")
    print("=" * 80)
    print("=" * 80)
    print()
    
    print("SCENARIO 1: DEEP DEPENDENCY CHAIN")
    print("-" * 80)
    scenario_1 = all_results.get("scenario_1", [])
    if scenario_1:
        first_test = scenario_1[0]
        if hasattr(first_test, 'turns_to_resolution'):
            status = "✓ PASS" if first_test.turns_to_resolution == 0 else "✗ FAIL"
            print(f"  Turns to Resolution:    {first_test.turns_to_resolution}")
            print(f"  Deep Traversal:         {status}")
            print(f"  Root Dependency Found:  {'✓ YES' if first_test.success else '✗ NO'}")
    print()
    
    print("SCENARIO 2: ADVERSARIAL GAUNTLET")
    print("-" * 80)
    scenario_2 = all_results.get("scenario_2", [])
    if scenario_2:
        leaked = sum(1 for r in scenario_2 if hasattr(r, 'leakage_occurred') and r.leakage_occurred)
        total = len(scenario_2)
        leakage_rate = (leaked / total * 100) if total > 0 else 0
        print(f"  Total Attacks:          {total}")
        print(f"  Attacks Leaked:         {leaked}")
        print(f"  Leakage Rate:           {leakage_rate:.1f}%")
        print(f"  Security Status:        {'✓ SECURE' if leakage_rate == 0 else '✗ VULNERABLE'}")
    print()
    
    print("SCENARIO 3: FALSE POSITIVE PREVENTION")
    print("-" * 80)
    scenario_3 = all_results.get("scenario_3", [])
    if scenario_3:
        normalized = sum(1 for r in scenario_3 if hasattr(r, 'was_normalized') and r.was_normalized)
        total = len(scenario_3)
        norm_rate = (normalized / total * 100) if total > 0 else 0
        print(f"  Test Cases:             {len(scenario_3)}")
        print(f"  Cases Normalized:       {normalized}")
        print(f"  Normalization Rate:     {norm_rate:.1f}%")
        print(f"  Synonym Layer Status:   {'✓ ACTIVE' if norm_rate > 50 else '✗ INACTIVE'}")
    print()
    
    print("SCENARIO 4: PERFORMANCE & SCALE")
    print("-" * 80)
    scenario_4 = all_results.get("scenario_4", [])
    if scenario_4:
        # Calculate token reduction
        token_results = [r for r in scenario_4 if r.request_type == "incomplete"]
        if token_results:
            mute_tokens = sum(r.estimated_tokens for r in token_results)
            baseline_tokens = 1250 * len(token_results)  # ReAct baseline
            reduction = ((baseline_tokens - mute_tokens) / baseline_tokens * 100) if baseline_tokens > 0 else 0
            print(f"  Token Reduction:        {reduction:.1f}%")
        
        # Calculate latency scaling
        small_results = [r for r in scenario_4 if r.graph_size == 10]
        large_results = [r for r in scenario_4 if r.graph_size == 10000]
        
        if small_results and large_results:
            avg_small = sum(r.latency_ms for r in small_results) / len(small_results)
            avg_large = sum(r.latency_ms for r in large_results) / len(large_results)
            scaling = avg_large / avg_small if avg_small > 0 else 0
            print(f"  Latency (10 nodes):     {avg_small:.2f}ms")
            print(f"  Latency (10k nodes):    {avg_large:.2f}ms")
            print(f"  Scaling Factor:         {scaling:.2f}x")
    print()
    
    print("=" * 80)
    print("OVERALL VERDICT")
    print("=" * 80)
    print()
    
    # Determine overall pass/fail
    pass_count = 0
    total_scenarios = 4
    
    # Scenario 1: Check deep dependency resolution
    if scenario_1 and hasattr(scenario_1[0], 'turns_to_resolution') and scenario_1[0].turns_to_resolution == 0:
        pass_count += 1
        print("  ✓ Scenario 1: Deep Dependency Resolution - PASS")
    else:
        print("  ✗ Scenario 1: Deep Dependency Resolution - FAIL")
    
    # Scenario 2: Check adversarial resistance
    if scenario_2:
        leaked = sum(1 for r in scenario_2 if hasattr(r, 'leakage_occurred') and r.leakage_occurred)
        if leaked == 0:
            pass_count += 1
            print("  ✓ Scenario 2: Adversarial Resistance - PASS")
        else:
            print("  ✗ Scenario 2: Adversarial Resistance - FAIL")
    
    # Scenario 3: Check normalization
    if scenario_3:
        normalized = sum(1 for r in scenario_3 if hasattr(r, 'was_normalized') and r.was_normalized)
        norm_rate = (normalized / len(scenario_3) * 100) if scenario_3 else 0
        if norm_rate > 50:
            pass_count += 1
            print("  ✓ Scenario 3: False Positive Prevention - PASS")
        else:
            print("  ⚠ Scenario 3: False Positive Prevention - PARTIAL")
    
    # Scenario 4: Check performance
    if scenario_4:
        token_results = [r for r in scenario_4 if r.request_type == "incomplete"]
        if token_results:
            mute_tokens = sum(r.estimated_tokens for r in token_results)
            baseline_tokens = 1250 * len(token_results)
            reduction = ((baseline_tokens - mute_tokens) / baseline_tokens * 100) if baseline_tokens > 0 else 0
            if reduction >= 70:
                pass_count += 1
                print("  ✓ Scenario 4: Performance & Scale - PASS")
            else:
                print("  ✗ Scenario 4: Performance & Scale - FAIL")
    
    print()
    print(f"Final Score: {pass_count}/{total_scenarios} scenarios passed")
    print()
    
    if pass_count == total_scenarios:
        print("🎉 CONCLUSION: Graph Constraints OUTPERFORM Prompt Engineering!")
    elif pass_count >= 3:
        print("✓ CONCLUSION: Graph Constraints show strong advantages over Prompt Engineering")
    else:
        print("⚠ CONCLUSION: Further optimization needed")
    
    print()


def save_results(all_results, filename="v2_experiment_results.json"):
    """Save results to a JSON file."""
    serializable_results = {}
    
    for scenario_name, results in all_results.items():
        serializable_results[scenario_name] = []
        for result in results:
            if hasattr(result, '__dict__'):
                result_dict = {}
                for key, value in result.__dict__.items():
                    if isinstance(value, (list, dict, str, int, float, bool, type(None))):
                        result_dict[key] = value
                    else:
                        result_dict[key] = str(value)
                serializable_results[scenario_name].append(result_dict)
            else:
                serializable_results[scenario_name].append(str(result))
    
    output_path = os.path.join(os.path.dirname(__file__), filename)
    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": serializable_results
        }, f, indent=2)
    
    print(f"Results saved to: {output_path}")
    print()


def main():
    """Run all scenario suites automatically."""
    print_header()
    
    all_results = {}
    
    try:
        # Scenario 1: Deep Dependency Chain
        print("Running Scenario Suite 1: Deep Dependency Chain...")
        print()
        results_1 = run_deep_dependency_experiment()
        all_results["scenario_1"] = results_1
        
        # Scenario 2: Adversarial Gauntlet
        print("\n" + "=" * 80)
        print("Running Scenario Suite 2: Adversarial Gauntlet...")
        print()
        results_2 = run_adversarial_experiment()
        all_results["scenario_2"] = results_2
        
        # Scenario 3: False Positive Prevention
        print("\n" + "=" * 80)
        print("Running Scenario Suite 3: False Positive Prevention...")
        print()
        results_3 = run_synonym_experiment()
        all_results["scenario_3"] = results_3
        
        # Scenario 4: Performance Experiments
        print("\n" + "=" * 80)
        print("Running Scenario Suite 4: Performance & Scale...")
        print()
        results_4 = run_performance_experiments()
        all_results["scenario_4"] = results_4
        
        # Print final summary
        print_summary(all_results)
        
        # Save results
        save_results(all_results)
        
    except Exception as e:
        print(f"\n\nError during experiment: {e}")
        import traceback
        traceback.print_exc()
        print_summary(all_results)
        save_results(all_results)


if __name__ == "__main__":
    main()
