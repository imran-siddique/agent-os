"""
Example: Basic Adversarial Verification

Demonstrates the basic usage of the Cross-Model Verification Kernel
with GPT-4o as Generator and Gemini 1.5 Pro as Verifier.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.generator import GeneratorConfig
from src.verifier import VerifierConfig
from src.kernel import VerificationKernel
from src.models import ModelProvider


def main():
    """Run basic adversarial verification example"""
    
    print("Cross-Model Verification Kernel - Basic Example")
    print("=" * 80)
    print("\nInitializing adversarial architecture...")
    print("- Generator: GPT-4o")
    print("- Verifier: Gemini 1.5 Pro (hostile code review mode)\n")
    
    # Configure Generator with GPT-4o
    generator_config = GeneratorConfig(
        model=ModelProvider.GPT4O,
        temperature=0.7,
        max_tokens=2000
    )
    
    # Configure Verifier with Gemini 1.5 Pro (different model!)
    verifier_config = VerifierConfig(
        model=ModelProvider.GEMINI_15_PRO,
        temperature=0.2,
        adversarial_mode=True
    )
    
    # Create the Verification Kernel
    # Note: This will enforce that generator and verifier use different models
    kernel = VerificationKernel(
        generator_config=generator_config,
        verifier_config=verifier_config
    )
    
    # Task: Generate a Fibonacci function
    task = "Create a function to calculate the nth Fibonacci number"
    
    print(f"Task: {task}\n")
    print("Executing adversarial verification pipeline...")
    print("1. Generating code with GPT-4o...")
    print("2. Hostile code review with Gemini 1.5 Pro...")
    print("3. Calculating blind spot probability reduction...\n")
    
    # Execute verification
    result = kernel.verify_task(
        task_description=task,
        language="python"
    )
    
    # Print detailed results
    kernel.print_verification_summary(result)
    
    # Print statistics
    print("\n\nKernel Statistics:")
    print("-" * 80)
    stats = kernel.get_statistics()
    print(f"Total Verifications: {stats['total_verifications']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    print(f"Average Risk Reduction: {stats['average_risk_reduction_factor']:.2f}x")
    print(f"Model Diversity Enforced: {stats['model_diversity']['are_different']}")
    print("-" * 80)


if __name__ == "__main__":
    main()
