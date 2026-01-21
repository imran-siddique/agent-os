# experiments/paper_data_generator.py
"""
Paper Data Generator - Generates experimental data for research paper.

This script compares:
1. Baseline: Single agent (OpenAI) without verification
2. CMVK: Cross-Model Verification Kernel (OpenAI + Gemini + Trace)

The generated traces can be used for charts and supplementary material.

Now supports loading problems from the HumanEval dataset for large-scale experiments.
"""
import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simple_kernel import SimpleVerificationKernel
from src.agents.generator_openai import OpenAIGenerator
from src.datasets.humaneval_loader import HumanEvalLoader


# 1. The Dataset (Subtle bugs that standard models miss)
# Legacy hardcoded problems - kept for backward compatibility
LEGACY_PROBLEMS = [
    {
        "id": "prob_001",
        "query": "Write a Python function to merge two sorted arrays into one sorted array WITHOUT using 'sorted()' or 'sort()'. Optimize for O(n)."
    },
    {
        "id": "prob_002", 
        "query": "Write a regex to validate an email address that DOES NOT allow uppercase letters."
    }
]


def run_baseline_agent(problem):
    """
    Control Group: Just OpenAI, no Verification Loop.
    
    This represents the traditional approach where a single LLM
    generates code without adversarial verification.
    
    Args:
        problem: Problem dictionary with 'id' and 'query' keys
    """
    print(f"\n{'='*80}")
    print(f"--- Running Baseline for {problem['id']} ---")
    print(f"{'='*80}")
    
    agent = OpenAIGenerator()
    code = agent.generate_solution(problem['query'])
    
    # In a real paper, we'd run automated testing on this code.
    # For now, we just save it.
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/baseline_{problem['id']}.py", "w") as f:
        f.write(code)
    
    print(f"💾 Baseline solution saved to: logs/baseline_{problem['id']}.py")


def run_our_kernel(problem):
    """
    Experimental Group: CMVK (OpenAI + Gemini + Trace).
    
    This represents our approach with adversarial verification
    and full traceability.
    
    Args:
        problem: Problem dictionary with 'id' and 'query' keys
    """
    print(f"\n{'='*80}")
    print(f"--- Running CMVK for {problem['id']} ---")
    print(f"{'='*80}")
    
    kernel = SimpleVerificationKernel()
    solution = kernel.solve(problem['query'], run_id=f"cmvk_{problem['id']}")
    
    if solution:
        print(f"✅ CMVK found verified solution for {problem['id']}")
    else:
        print(f"❌ CMVK failed to find solution for {problem['id']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate experimental data comparing Baseline vs CMVK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with legacy 2 problems
  python experiments/paper_data_generator.py --legacy
  
  # Run with first 5 HumanEval problems
  python experiments/paper_data_generator.py --humaneval --count 5
  
  # Run with HumanEval problems 10-20
  python experiments/paper_data_generator.py --humaneval --start 10 --count 10
  
  # Run with all problems in sample dataset
  python experiments/paper_data_generator.py --humaneval
        """
    )
    
    parser.add_argument(
        '--humaneval',
        action='store_true',
        help='Use HumanEval dataset instead of legacy problems'
    )
    parser.add_argument(
        '--legacy',
        action='store_true',
        help='Use legacy hardcoded problems (default if neither flag specified)'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='Starting index for HumanEval problems (default: 0)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=None,
        help='Number of problems to run (default: all available)'
    )
    parser.add_argument(
        '--dataset-path',
        type=str,
        default=None,
        help='Path to custom HumanEval dataset JSON file'
    )
    
    args = parser.parse_args()
    
    # Determine which dataset to use
    if args.humaneval:
        print("="*80)
        print("PAPER DATA GENERATOR - HumanEval Dataset")
        print("Comparing Baseline (Single Agent) vs CMVK (Adversarial Verification)")
        print("="*80)
        
        # Load HumanEval dataset
        loader = HumanEvalLoader(args.dataset_path)
        problems = loader.format_all_for_kernel(start=args.start, count=args.count)
        
        print(f"\n📊 Experiment Configuration:")
        print(f"   Dataset: HumanEval")
        print(f"   Starting index: {args.start}")
        print(f"   Number of problems: {len(problems)}")
        print(f"   Total problems in dataset: {len(loader)}")
    else:
        # Use legacy problems by default
        print("="*80)
        print("PAPER DATA GENERATOR - Legacy Problems")
        print("Comparing Baseline (Single Agent) vs CMVK (Adversarial Verification)")
        print("="*80)
        
        problems = LEGACY_PROBLEMS
        print(f"\n📊 Experiment Configuration:")
        print(f"   Dataset: Legacy (hardcoded)")
        print(f"   Number of problems: {len(problems)}")
        print(f"\n💡 Tip: Use --humaneval flag to run with HumanEval dataset")
    
    print("\n" + "="*80)
    print("STARTING EXPERIMENTS")
    print("="*80)
    
    for i, p in enumerate(problems, 1):
        print(f"\n{'='*80}")
        print(f"Problem {i}/{len(problems)}: {p['id']}")
        print(f"{'='*80}")
        
        # 1. Run Baseline
        run_baseline_agent(p)
        
        # 2. Run Our Kernel
        run_our_kernel(p)
    
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print(f"\n📊 Completed {len(problems)} problem(s)")
    print("\n💾 Results saved to:")
    print("   - Baseline solutions: logs/baseline_*.py")
    print("   - CMVK traces: logs/traces/cmvk_*.json")
    print("\n💡 Next Steps:")
    print("   1. Visualize the Traces:")
    print("      python -m src.tools.visualizer --latest")
    print("   2. Scale the Experiment:")
    print("      python experiments/paper_data_generator.py --humaneval --count 50")
    print("   3. Review PAPER.md for research methodology")
    print("="*80)
