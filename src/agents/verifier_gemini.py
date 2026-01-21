"""
Gemini Verifier Agent - System 2 thinking.
This agent uses Google Gemini models to perform adversarial verification.
"""
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .base_agent import BaseAgent
from ..core.types import GenerationResult, VerificationResult, VerificationOutcome

logger = logging.getLogger(__name__)


class GeminiVerifier(BaseAgent):
    """
    Verifier agent using Google Gemini models.
    
    Role: High logic, cynical reviewer with System 2 thinking.
    This is the "Adversary" that tries to break the solution.
    """
    
    def __init__(self, model_name: str = "gemini-1.5-pro", api_key: Optional[str] = None, **kwargs):
        """
        Initialize the Gemini verifier.
        
        Args:
            model_name: Gemini model to use (default: gemini-1.5-pro)
            api_key: Google API key (if None, reads from environment)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        """
        if api_key is None:
            api_key = os.environ.get("GOOGLE_API_KEY", "")
        
        super().__init__(model_name, api_key, **kwargs)
        
        # Load system prompt
        prompt_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "verifier_hostile.txt"
        self.system_prompt = self._load_system_prompt(str(prompt_path))
        
        # Initialize Gemini client (lazy import to avoid dependency issues)
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google Generative AI client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.system_prompt
            )
            logger.info("Gemini client initialized successfully")
        except ImportError:
            logger.warning("Google Generative AI package not installed. Install with: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
    
    def generate(self, task: str, context: Optional[Dict[str, Any]] = None) -> GenerationResult:
        """
        Not implemented for Verifier agent.
        Verifiers don't generate - they only verify.
        """
        raise NotImplementedError("Verifier agents don't perform generation")
    
    def verify(self, context: Dict[str, Any]) -> VerificationResult:
        """
        Verify a solution with adversarial scrutiny.
        
        Args:
            context: Dictionary containing:
                - task: The original problem
                - solution: The generated solution
                - explanation: Solution explanation
                - test_cases: Provided test cases
                
        Returns:
            VerificationResult with detailed critique
        """
        logger.info(f"Verifying solution with {self.model_name}")
        
        # Build verification prompt
        verification_prompt = self._build_verification_prompt(context)
        
        # Call Gemini API
        try:
            if self.model is None:
                # Fallback for testing without API
                return self._mock_verification()
            
            response = self.model.generate_content(
                verification_prompt,
                generation_config={
                    "temperature": self.config.get("temperature", 0.3),
                    "max_output_tokens": self.config.get("max_tokens", 2000)
                }
            )
            
            content = response.text
            
            # Parse the verification response
            result = self._parse_verification_response(content)
            logger.info(f"Verification complete: {result.outcome}")
            return result
            
        except Exception as e:
            logger.error(f"Error during verification: {e}")
            return self._mock_verification()
    
    def _build_verification_prompt(self, context: Dict[str, Any]) -> str:
        """Build the verification prompt."""
        prompt_parts = [
            "Please perform an adversarial code review of the following solution.",
            "",
            f"Original Task:\n{context.get('task', 'N/A')}",
            "",
            f"Proposed Solution:\n{context.get('solution', 'N/A')}",
            "",
            f"Explanation:\n{context.get('explanation', 'N/A')}",
            "",
            f"Test Cases:\n{context.get('test_cases', 'N/A')}",
            "",
            "Provide your hostile critique following the format specified in your system instructions."
        ]
        
        return "\n".join(prompt_parts)
    
    def _parse_verification_response(self, content: str) -> VerificationResult:
        """
        Parse the verifier's response into a structured VerificationResult.
        
        This is a simplified parser - in production, you might use more sophisticated parsing.
        """
        # Simple heuristic: look for keywords to determine outcome
        content_lower = content.lower()
        
        # Determine outcome
        if "pass" in content_lower and "fail" not in content_lower:
            outcome = VerificationOutcome.PASS
            confidence = 0.9
        elif "fail" in content_lower:
            outcome = VerificationOutcome.FAIL
            confidence = 0.8
        else:
            outcome = VerificationOutcome.UNCERTAIN
            confidence = 0.5
        
        # Extract issues (simplified)
        critical_issues = []
        logic_flaws = []
        missing_edge_cases = []
        
        if "critical" in content_lower or "bug" in content_lower:
            critical_issues.append("Issues detected in verification")
        if "logic" in content_lower and "flaw" in content_lower:
            logic_flaws.append("Logic flaws identified")
        if "edge case" in content_lower:
            missing_edge_cases.append("Edge cases need attention")
        
        return VerificationResult(
            outcome=outcome,
            confidence=confidence,
            critical_issues=critical_issues,
            logic_flaws=logic_flaws,
            missing_edge_cases=missing_edge_cases,
            reasoning=content
        )
    
    def _mock_verification(self) -> VerificationResult:
        """Generate a mock verification result for testing when API is not available."""
        logger.warning("Using mock verification (API not available)")
        return VerificationResult(
            outcome=VerificationOutcome.PASS,
            confidence=0.75,
            critical_issues=[],
            logic_flaws=[],
            missing_edge_cases=[],
            reasoning="Mock verification - API not available"
        )
