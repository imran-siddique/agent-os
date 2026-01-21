"""
Verification Kernel

The main orchestrator for the adversarial architecture.
Coordinates Generator and Verifier to provide model-diverse verification.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import math
from .generator import Generator, GeneratorConfig, GeneratedCode
from .verifier import Verifier, VerifierConfig, VerificationReport
from .models import ModelProvider


@dataclass
class BlindSpotAnalysis:
    """Mathematical analysis of blind spot reduction through model diversity"""
    single_model_error_prob: float
    independent_error_prob: float
    correlation_coefficient: float
    combined_error_prob: float
    risk_reduction_factor: float
    
    def __str__(self) -> str:
        return f"""Blind Spot Analysis:
- Single model error probability: {self.single_model_error_prob:.4f}
- Independent error probability: {self.independent_error_prob:.4f}
- Model correlation coefficient: {self.correlation_coefficient:.4f}
- Combined error probability: {self.combined_error_prob:.4f}
- Risk reduction factor: {self.risk_reduction_factor:.2f}x"""


@dataclass
class VerificationResult:
    """Complete result of adversarial verification"""
    generated_code: GeneratedCode
    verification_report: VerificationReport
    blind_spot_analysis: BlindSpotAnalysis
    generator_model: str
    verifier_model: str
    success: bool


class VerificationKernel:
    """
    Main kernel that orchestrates adversarial verification with model diversity.
    
    This kernel implements the mathematical framework that demonstrates how
    using different models for generation and verification reduces the
    probability of shared blind spots.
    """
    
    def __init__(
        self,
        generator_config: GeneratorConfig,
        verifier_config: VerifierConfig
    ):
        """
        Initialize the Verification Kernel
        
        Args:
            generator_config: Configuration for the generator
            verifier_config: Configuration for the verifier
        
        Raises:
            ValueError: If generator and verifier use the same model
        """
        # Enforce model diversity
        if generator_config.model == verifier_config.model:
            raise ValueError(
                f"Generator and Verifier must use DIFFERENT models for adversarial verification. "
                f"Both are configured to use {generator_config.model.value}. "
                f"This defeats the purpose of model diversity."
            )
        
        self.generator = Generator(generator_config)
        self.verifier = Verifier(verifier_config)
        self.verification_history = []
    
    def verify_task(
        self,
        task_description: str,
        language: str = "python",
        **kwargs
    ) -> VerificationResult:
        """
        Execute the full adversarial verification pipeline
        
        Args:
            task_description: Description of the task to generate code for
            language: Programming language
            **kwargs: Additional parameters
        
        Returns:
            VerificationResult with complete analysis
        """
        # Step 1: Generate code with Generator model
        generated_code = self.generator.generate_code(
            task_description=task_description,
            language=language,
            **kwargs
        )
        
        # Step 2: Verify with different Verifier model (adversarial)
        verification_report = self.verifier.verify_code(
            code=generated_code.code,
            description=task_description,
            language=language,
            **kwargs
        )
        
        # Step 3: Calculate blind spot analysis
        blind_spot_analysis = self._calculate_blind_spot_reduction(
            generator_model=self.generator.config.model,
            verifier_model=self.verifier.config.model
        )
        
        # Create result
        result = VerificationResult(
            generated_code=generated_code,
            verification_report=verification_report,
            blind_spot_analysis=blind_spot_analysis,
            generator_model=generated_code.model_used,
            verifier_model=verification_report.model_used,
            success=verification_report.passed
        )
        
        self.verification_history.append(result)
        return result
    
    def _calculate_blind_spot_reduction(
        self,
        generator_model: ModelProvider,
        verifier_model: ModelProvider
    ) -> BlindSpotAnalysis:
        """
        Calculate the mathematical reduction in blind spot probability
        
        Using probability theory:
        - P(error) = probability a single model makes an error
        - P(both_error) = probability both models make the SAME error
        - If models are independent: P(both_error) = P(error)²
        - If models are correlated: P(both_error) = P(error)² + ρ*P(error)*(1-P(error))
        
        Where ρ is the correlation coefficient between models.
        
        Model diversity reduces ρ, thus reducing P(both_error).
        """
        # Estimated error probabilities (can be calibrated from real data)
        single_model_error_prob = 0.15  # 15% chance of missing a bug
        
        # Correlation coefficient based on model diversity
        correlation = self._estimate_model_correlation(generator_model, verifier_model)
        
        # Independent case (theoretical minimum)
        independent_error_prob = single_model_error_prob ** 2
        
        # Actual combined error probability with correlation
        combined_error_prob = (
            single_model_error_prob ** 2 + 
            correlation * single_model_error_prob * (1 - single_model_error_prob)
        )
        
        # Risk reduction factor
        risk_reduction = single_model_error_prob / combined_error_prob
        
        return BlindSpotAnalysis(
            single_model_error_prob=single_model_error_prob,
            independent_error_prob=independent_error_prob,
            correlation_coefficient=correlation,
            combined_error_prob=combined_error_prob,
            risk_reduction_factor=risk_reduction
        )
    
    def _estimate_model_correlation(
        self,
        model1: ModelProvider,
        model2: ModelProvider
    ) -> float:
        """
        Estimate correlation coefficient between two models
        
        Models from different providers have lower correlation.
        Models from the same provider have higher correlation.
        
        Returns:
            Correlation coefficient ρ ∈ [0, 1]
        """
        # Extract provider families
        provider1 = self._get_provider_family(model1)
        provider2 = self._get_provider_family(model2)
        
        if provider1 != provider2:
            # Different providers: low correlation (0.1-0.3)
            return 0.2
        else:
            # Same provider: higher correlation (0.4-0.6)
            return 0.5
    
    def _get_provider_family(self, model: ModelProvider) -> str:
        """Get the provider family (GPT, Gemini, Claude)"""
        if model.value.startswith('gpt'):
            return 'openai'
        elif model.value.startswith('gemini'):
            return 'google'
        elif model.value.startswith('claude'):
            return 'anthropic'
        return 'unknown'
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the verification kernel"""
        total_verifications = len(self.verification_history)
        passed = sum(1 for r in self.verification_history if r.success)
        failed = total_verifications - passed
        
        avg_risk_reduction = (
            sum(r.blind_spot_analysis.risk_reduction_factor for r in self.verification_history) / 
            total_verifications if total_verifications > 0 else 0
        )
        
        return {
            "generator": self.generator.get_stats(),
            "verifier": self.verifier.get_stats(),
            "total_verifications": total_verifications,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total_verifications if total_verifications > 0 else 0,
            "average_risk_reduction_factor": avg_risk_reduction,
            "model_diversity": {
                "generator": self.generator.config.model.value,
                "verifier": self.verifier.config.model.value,
                "are_different": self.generator.config.model != self.verifier.config.model
            }
        }
    
    def print_verification_summary(self, result: VerificationResult):
        """Print a human-readable summary of verification results"""
        print("=" * 80)
        print("ADVERSARIAL VERIFICATION REPORT")
        print("=" * 80)
        print(f"\nGenerator Model: {result.generator_model}")
        print(f"Verifier Model: {result.verifier_model}")
        print(f"\nTask: {result.generated_code.description}")
        print(f"\nGenerated Code ({result.generated_code.language}):")
        print("-" * 80)
        print(result.generated_code.code)
        print("-" * 80)
        print(f"\nVerification Status: {'✓ PASSED' if result.success else '✗ FAILED'}")
        print(f"Summary: {result.verification_report.summary}")
        print(f"\nIssues Found: {len(result.verification_report.issues)}")
        for i, issue in enumerate(result.verification_report.issues, 1):
            print(f"\n  {i}. [{issue.severity.value.upper()}] {issue.category}")
            print(f"     {issue.description}")
            if issue.suggestion:
                print(f"     Suggestion: {issue.suggestion}")
        print(f"\n{result.blind_spot_analysis}")
        print("=" * 80)


def prosecutor_check(kernel, code_snippet: str) -> bool:
    """
    Execute the Prosecutor Workflow: Generate and run hostile tests against code.
    
    This is a demonstration function showing how to use the Prosecutor Mode
    to verify code by attempting to break it with adversarial tests.
    
    Args:
        kernel: VerificationKernel instance (used for verifier access)
        code_snippet: The code to test
        
    Returns:
        bool: True if code survived the attack, False if it was broken
        
    Security Note:
        The code_snippet is executed in a sandbox with timeout and resource limits.
        While the sandbox provides isolation, this function is intended for trusted
        code verification workflows, not for arbitrary untrusted code execution.
    """
    from .agents.verifier_gemini import GeminiVerifier
    from .tools.sandbox import Sandbox
    
    verifier = GeminiVerifier()
    sandbox = Sandbox()
    
    print(f"🕵️ Prosecutor (Gemini) is analyzing code...")
    
    # 1. Generate the Attack
    attack_script = verifier.generate_hostile_test(code_snippet)
    print(f"⚔️ Generated Hostile Test:\n{attack_script}\n")
    
    # 2. Combine Target + Attack
    # Note: Both code_snippet and attack_script are executed in the sandbox
    full_execution_script = f"{code_snippet}\n\n{attack_script}"
    
    # 3. Run in Sandbox (with timeout and resource limits)
    print("RUNNING IN SANDBOX...")
    result = sandbox.execute(full_execution_script)
    
    # 4. Judgement
    if result['status'] == 'success':
        # If the script ran without error, the code SURVIVED the attack
        # (Assuming the attack was meant to assert/crash on bug)
        print("✅ PASSED: The code survived the hostile test.")
        return True
    else:
        print(f"❌ FAILED: The Prosecutor broke the code.\nError: {result['error']}")
        return False
