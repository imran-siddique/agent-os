"""
Example: Model Diversity Comparison

Demonstrates the difference between single-model and multi-model verification,
showing the mathematical reduction in blind spot probability.
"""

from cross_model_verification_kernel.generator import GeneratorConfig
from cross_model_verification_kernel.kernel import VerificationKernel
from cross_model_verification_kernel.models import ModelProvider
from cross_model_verification_kernel.verifier import VerifierConfig


def test_single_model_approach() -> None:
    """Test with same model for both (NOT recommended)"""
    print("\n" + "=" * 80)
    print("APPROACH 1: Single Model (Self-Refinement)")
    print("=" * 80)
    print("Generator: GPT-4o")
    print("Verifier: GPT-4o (SAME MODEL)")
    print("This approach has higher blind spot probability!\n")

    try:
        generator_config = GeneratorConfig(model=ModelProvider.GPT4O)
        verifier_config = VerifierConfig(model=ModelProvider.GPT4O)

        # This should raise an error enforcing model diversity!
        _kernel = VerificationKernel(generator_config, verifier_config)
        print("WARNING: Should not reach here - model diversity not enforced!")
    except ValueError as e:
        print("✓ Model diversity enforcement working:")
        print(f"  Error: {e}\n")


def test_diverse_models() -> None:
    """Test with different models (recommended)"""
    print("\n" + "=" * 80)
    print("APPROACH 2: Model Diversity (Adversarial Architecture)")
    print("=" * 80)
    print("Generator: GPT-4o")
    print("Verifier: Gemini 1.5 Pro (DIFFERENT MODEL)")
    print("This approach reduces blind spot probability!\n")

    generator_config = GeneratorConfig(model=ModelProvider.GPT4O)
    verifier_config = VerifierConfig(model=ModelProvider.GEMINI_15_PRO, adversarial_mode=True)

    kernel = VerificationKernel(generator_config, verifier_config)

    task = "Create a function to validate email addresses"
    result = kernel.verify_task(task_description=task)

    print("Verification completed!")
    print(f"Status: {'PASSED' if result.success else 'FAILED'}")
    print(f"\n{result.blind_spot_analysis}")


def compare_provider_combinations() -> None:
    """Compare different provider combinations"""
    print("\n" + "=" * 80)
    print("MODEL CORRELATION ANALYSIS")
    print("=" * 80)

    combinations = [
        (ModelProvider.GPT4O, ModelProvider.GEMINI_15_PRO, "OpenAI → Google"),
        (ModelProvider.GPT4O, ModelProvider.CLAUDE_35_SONNET, "OpenAI → Anthropic"),
        (ModelProvider.GEMINI_15_PRO, ModelProvider.CLAUDE_35_SONNET, "Google → Anthropic"),
        (ModelProvider.GPT4O, ModelProvider.GPT4_TURBO, "OpenAI → OpenAI (not ideal)"),
    ]

    task = "Create a secure password hashing function"

    for gen_model, ver_model, desc in combinations:
        print(f"\n{desc}:")
        generator_config = GeneratorConfig(model=gen_model)
        verifier_config = VerifierConfig(model=ver_model)

        kernel = VerificationKernel(generator_config, verifier_config)
        result = kernel.verify_task(task_description=task)

        analysis = result.blind_spot_analysis
        print(f"  Correlation: {analysis.correlation_coefficient:.2f}")
        print(f"  Combined Error Probability: {analysis.combined_error_prob:.4f}")
        print(f"  Risk Reduction: {analysis.risk_reduction_factor:.2f}x")


def main() -> None:
    """Run model diversity comparison"""
    print("Cross-Model Verification Kernel - Model Diversity Analysis")

    # Test 1: Show enforcement of model diversity
    test_single_model_approach()

    # Test 2: Show diverse models working
    test_diverse_models()

    # Test 3: Compare different combinations
    compare_provider_combinations()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("1. Model diversity is ENFORCED - you cannot use the same model for both")
    print("2. Different providers (e.g., GPT vs Gemini) have lower correlation")
    print("3. Lower correlation = better blind spot reduction")
    print("4. Adversarial verification catches issues that self-refinement misses")
    print("=" * 80)


if __name__ == "__main__":
    main()
