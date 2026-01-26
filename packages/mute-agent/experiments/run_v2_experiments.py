"""
Mute Agent v2: Comprehensive Test Suite Runner

Runs all 4 scenario suites to validate that "Graph Constraints" 
outperform "Prompt Engineering" in complex, multi-step, and adversarial scenarios.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
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
    print("Objective: Prove that graph-based constraints provide superior:")
    print("  1. Deep dependency resolution")
    print("  2. Adversarial attack resistance")
    print("  3. User experience (low false positives)")
    print("  4. Performance and token efficiency")
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
        # Check if first result successfully identified dependencies
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
        false_positives = sum(1 for r in scenario_3 if hasattr(r, 'is_false_positive') and r.is_false_positive)
        valid_intents = sum(1 for r in scenario_3 if hasattr(r, 'is_false_positive'))
        fp_rate = (false_positives / valid_intents * 100) if valid_intents > 0 else 0
        print(f"  Test Cases:             {len(scenario_3)}")
        print(f"  False Positives:        {false_positives}")
        print(f"  False Positive Rate:    {fp_rate:.1f}%")
        print(f"  UX Status:              {'✓ LOW FRICTION' if fp_rate < 20 else '✗ HIGH FRICTION'}")
    print()
    
    print("SCENARIO 4: PERFORMANCE & SCALE")
    print("-" * 80)
    scenario_4 = all_results.get("scenario_4", [])
    if scenario_4:
        # Calculate averages
        avg_latency = sum(r.latency_ms for r in scenario_4) / len(scenario_4) if scenario_4 else 0
        avg_tokens = sum(r.estimated_tokens for r in scenario_4) / len(scenario_4) if scenario_4 else 0
        
        # Check if we have both small and large graph results
        small_results = [r for r in scenario_4 if r.graph_size == 10]
        large_results = [r for r in scenario_4 if r.graph_size == 10000]
        
        if small_results and large_results:
            avg_small = sum(r.latency_ms for r in small_results) / len(small_results)
            avg_large = sum(r.latency_ms for r in large_results) / len(large_results)
            scaling = avg_large / avg_small if avg_small > 0 else 0
            print(f"  Avg Latency (10 nodes):    {avg_small:.2f}ms")
            print(f"  Avg Latency (10k nodes):   {avg_large:.2f}ms")
            print(f"  Scaling Factor:            {scaling:.2f}x")
            print(f"  Complexity:                {'O(1)' if scaling < 2 else 'O(log N)' if scaling < 10 else 'O(N)'}")
        else:
            print(f"  Avg Latency:            {avg_latency:.2f}ms")
        
        print(f"  Avg Tokens:             {avg_tokens:.0f}")
        print(f"  Performance Status:     {'✓ EFFICIENT' if avg_latency < 100 else '✓ ACCEPTABLE' if avg_latency < 500 else '✗ SLOW'}")
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
    
    # Scenario 3: Check false positive rate
    if scenario_3:
        false_positives = sum(1 for r in scenario_3 if hasattr(r, 'is_false_positive') and r.is_false_positive)
        valid_intents = sum(1 for r in scenario_3 if hasattr(r, 'is_false_positive'))
        fp_rate = (false_positives / valid_intents * 100) if valid_intents > 0 else 100
        if fp_rate < 20:
            pass_count += 1
            print("  ✓ Scenario 3: False Positive Prevention - PASS")
        else:
            print("  ✗ Scenario 3: False Positive Prevention - FAIL")
    
    # Scenario 4: Check performance
    if scenario_4:
        avg_latency = sum(r.latency_ms for r in scenario_4) / len(scenario_4)
        if avg_latency < 500:
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
    # Convert dataclass objects to dicts
    serializable_results = {}
    
    for scenario_name, results in all_results.items():
        serializable_results[scenario_name] = []
        for result in results:
            if hasattr(result, '__dict__'):
                result_dict = {}
                for key, value in result.__dict__.items():
                    # Convert non-serializable types
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
    """Run all scenario suites."""
    print_header()
    
    all_results = {}
    
    try:
        # Scenario 1: Deep Dependency Chain
        print("\n")
        print("Running Scenario Suite 1...")
        print()
        results_1 = run_deep_dependency_experiment()
        all_results["scenario_1"] = results_1
        
        input("\nPress Enter to continue to Scenario 2...")
        
        # Scenario 2: Adversarial Gauntlet
        print("\n")
        print("Running Scenario Suite 2...")
        print()
        results_2 = run_adversarial_experiment()
        all_results["scenario_2"] = results_2
        
        input("\nPress Enter to continue to Scenario 3...")
        
        # Scenario 3: False Positive Prevention
        print("\n")
        print("Running Scenario Suite 3...")
        print()
        results_3 = run_synonym_experiment()
        all_results["scenario_3"] = results_3
        
        input("\nPress Enter to continue to Scenario 4...")
        
        # Scenario 4: Performance Experiments
        print("\n")
        print("Running Scenario Suite 4...")
        print()
        results_4 = run_performance_experiments()
        all_results["scenario_4"] = results_4
        
        # Print final summary
        print_summary(all_results)
        
        # Save results
        save_results(all_results)
        
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user.")
        print_summary(all_results)
        save_results(all_results)
    except Exception as e:
        print(f"\n\nError during experiment: {e}")
        import traceback
        traceback.print_exc()
        print_summary(all_results)
        save_results(all_results)


if __name__ == "__main__":
    main()
