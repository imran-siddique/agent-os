"""
Run a larger experiment with 50 scenarios for statistical significance.
"""

import random
from ambiguity_test import AmbiguityTestExperiment


def main():
    """
    Run the experiment with 50 scenarios.
    """
    # Set random seed for reproducibility
    random.seed(42)
    
    # Create and run experiment with 50 runs
    print("Running extended experiment with 50 scenarios...")
    print("This will generate more statistically significant results.\n")
    
    experiment = AmbiguityTestExperiment(num_runs=50)
    experiment.run_experiment()
    
    # Print results
    experiment.print_results()
    
    # Save results with different filenames
    experiment.save_results_to_csv("ambiguity_test_results_50runs.csv")
    experiment.save_comparison_to_csv("agent_comparison_50runs.csv")
    
    print("\n" + "=" * 80)
    print("EXTENDED EXPERIMENT COMPLETED!")
    print("=" * 80)
    print("\nFiles generated:")
    print("  - ambiguity_test_results_50runs.csv (detailed results)")
    print("  - agent_comparison_50runs.csv (comparison table)")
    print()


if __name__ == "__main__":
    main()
