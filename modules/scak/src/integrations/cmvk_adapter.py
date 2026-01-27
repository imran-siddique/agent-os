"""
CMVK Adapter - Integration with Claim-based Model Verification Kernel.

SCAK (Layer 4) uses CMVK to verify if correction is needed.
This adapter provides:
1. Mock implementation for testing/development
2. Production adapter for actual CMVK integration
3. Verification utilities for laziness detection

Publication Target: pip install scak
Dependency: cmvk (pip install cmvk)

The adapter follows "Telemetry over Logging" - all operations emit
structured JSON events, never print statements.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..interfaces.protocols import (
    CMVKVerifier,
    CMVKVerificationRequest,
    CMVKVerificationResponse,
    VerificationResult,
)
from ..interfaces.telemetry import TelemetryEmitter, EventType

logger = logging.getLogger(__name__)


class VerificationOutcome(BaseModel):
    """Concrete implementation of VerificationResult protocol."""
    
    is_valid: bool = Field(..., description="Whether verification passed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    verification_type: str = Field(..., description="Type of verification")
    details: Dict[str, Any] = Field(default_factory=dict, description="Verification details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    verification_id: str = Field(default="", description="Unique verification ID")


class MockCMVKVerifier:
    """
    Mock CMVK Verifier for testing and development.
    
    This implements the CMVKVerifier protocol without requiring
    the actual cmvk package. Use for:
    - Unit testing
    - Local development
    - Demonstrations
    
    In production, replace with ProductionCMVKVerifier.
    """
    
    def __init__(self, telemetry: Optional[TelemetryEmitter] = None):
        """
        Initialize mock verifier.
        
        Args:
            telemetry: Optional telemetry emitter for structured logging
        """
        self.telemetry = telemetry or TelemetryEmitter(agent_id="cmvk-mock")
        self._verification_count = 0
        
        # Give-up signals that indicate potential laziness
        self.give_up_signals = [
            "i couldn't find",
            "no data found", 
            "unable to locate",
            "i don't have access",
            "no results",
            "data not available",
            "cannot determine",
            "i'm not sure",
            "i cannot",
            "there is no",
        ]
    
    async def verify(
        self,
        claim: str,
        context: Dict[str, Any],
        verification_type: str = "completeness"
    ) -> VerificationOutcome:
        """
        Verify a claim (mock implementation).
        
        In production CMVK, this would:
        1. Parse the claim
        2. Cross-reference with knowledge base
        3. Run verification models
        4. Return confidence-scored result
        
        Args:
            claim: The claim/output to verify
            context: Context for verification
            verification_type: Type of verification
            
        Returns:
            VerificationOutcome with validity and confidence
        """
        self._verification_count += 1
        verification_id = f"verify-{self._verification_count:06d}"
        
        # Emit telemetry
        self.telemetry.emit_event(
            event_type=EventType.AUDIT_TRIGGERED,
            data={
                "verification_id": verification_id,
                "verification_type": verification_type,
                "claim_length": len(claim),
                "context_keys": list(context.keys()),
            }
        )
        
        # Mock verification logic
        is_give_up = any(signal in claim.lower() for signal in self.give_up_signals)
        
        if is_give_up:
            # Potential laziness - needs deeper verification
            result = VerificationOutcome(
                is_valid=False,
                confidence=0.65,
                verification_type=verification_type,
                details={
                    "reason": "give_up_signal_detected",
                    "matched_signals": [s for s in self.give_up_signals if s in claim.lower()],
                    "recommendation": "trigger_completeness_audit",
                },
                verification_id=verification_id,
            )
        else:
            # Claim appears valid
            result = VerificationOutcome(
                is_valid=True,
                confidence=0.85,
                verification_type=verification_type,
                details={"reason": "no_give_up_signals_detected"},
                verification_id=verification_id,
            )
        
        # Emit completion telemetry
        self.telemetry.emit_event(
            event_type=EventType.AUDIT_COMPLETED,
            data={
                "verification_id": verification_id,
                "is_valid": result.is_valid,
                "confidence": result.confidence,
            }
        )
        
        return result
    
    async def verify_completeness(
        self,
        agent_output: str,
        expected_coverage: List[str],
        context: Dict[str, Any]
    ) -> VerificationOutcome:
        """
        Verify that agent output covers expected information.
        
        Used by Completeness Auditor to detect laziness.
        
        Args:
            agent_output: The agent's response
            expected_coverage: Topics/data that should be covered
            context: Execution context
            
        Returns:
            VerificationOutcome indicating completeness
        """
        self._verification_count += 1
        verification_id = f"complete-{self._verification_count:06d}"
        
        # Mock: Check if expected topics are mentioned in output
        output_lower = agent_output.lower()
        covered = [topic for topic in expected_coverage if topic.lower() in output_lower]
        coverage_ratio = len(covered) / max(len(expected_coverage), 1)
        
        # Check for give-up signals
        has_give_up = any(signal in output_lower for signal in self.give_up_signals)
        
        if has_give_up and coverage_ratio < 0.5:
            # Laziness detected: gave up with low coverage
            return VerificationOutcome(
                is_valid=False,
                confidence=0.78,
                verification_type="completeness",
                details={
                    "coverage_ratio": coverage_ratio,
                    "covered_topics": covered,
                    "missing_topics": [t for t in expected_coverage if t not in covered],
                    "laziness_indicator": True,
                    "give_up_detected": has_give_up,
                },
                verification_id=verification_id,
            )
        else:
            return VerificationOutcome(
                is_valid=coverage_ratio >= 0.7,
                confidence=0.8 + (coverage_ratio * 0.15),
                verification_type="completeness",
                details={
                    "coverage_ratio": coverage_ratio,
                    "covered_topics": covered,
                    "give_up_detected": has_give_up,
                },
                verification_id=verification_id,
            )
    
    async def verify_correctness(
        self,
        agent_output: str,
        ground_truth: Optional[str],
        context: Dict[str, Any]
    ) -> VerificationOutcome:
        """
        Verify that agent output is factually correct.
        
        Args:
            agent_output: The agent's response
            ground_truth: Known correct answer (if available)
            context: Execution context
            
        Returns:
            VerificationOutcome indicating correctness
        """
        self._verification_count += 1
        verification_id = f"correct-{self._verification_count:06d}"
        
        if ground_truth is None:
            # No ground truth available - use heuristics
            return VerificationOutcome(
                is_valid=True,
                confidence=0.5,
                verification_type="correctness",
                details={
                    "reason": "no_ground_truth_available",
                    "heuristic_only": True,
                },
                verification_id=verification_id,
            )
        
        # Mock: Simple similarity check
        output_words = set(agent_output.lower().split())
        truth_words = set(ground_truth.lower().split())
        overlap = len(output_words & truth_words) / max(len(truth_words), 1)
        
        return VerificationOutcome(
            is_valid=overlap >= 0.6,
            confidence=min(0.95, 0.5 + (overlap * 0.45)),
            verification_type="correctness",
            details={
                "word_overlap": overlap,
                "has_ground_truth": True,
            },
            verification_id=verification_id,
        )


class ProductionCMVKVerifier:
    """
    Production CMVK Verifier that integrates with the real cmvk package.
    
    This is the production implementation that requires:
        pip install cmvk
    
    Usage:
        from cmvk import Verifier  # Real CMVK package
        verifier = ProductionCMVKVerifier(cmvk_client=Verifier())
    """
    
    def __init__(
        self,
        cmvk_client: Any = None,
        telemetry: Optional[TelemetryEmitter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize production verifier.
        
        Args:
            cmvk_client: The actual CMVK client instance
            telemetry: Telemetry emitter
            config: Additional configuration
        """
        self._cmvk = cmvk_client
        self.telemetry = telemetry or TelemetryEmitter(agent_id="cmvk-prod")
        self.config = config or {}
        self._verification_count = 0
        
        if self._cmvk is None:
            logger.warning(
                "ProductionCMVKVerifier initialized without cmvk_client. "
                "Install with: pip install cmvk"
            )
    
    async def verify(
        self,
        claim: str,
        context: Dict[str, Any],
        verification_type: str = "completeness"
    ) -> VerificationOutcome:
        """
        Verify a claim using the real CMVK client.
        
        Args:
            claim: The claim/output to verify
            context: Context for verification
            verification_type: Type of verification
            
        Returns:
            VerificationOutcome from CMVK
        """
        self._verification_count += 1
        verification_id = f"cmvk-{self._verification_count:06d}"
        
        self.telemetry.emit_event(
            event_type=EventType.AUDIT_TRIGGERED,
            data={
                "verification_id": verification_id,
                "verification_type": verification_type,
                "production": True,
            }
        )
        
        if self._cmvk is None:
            # Fallback to mock if cmvk not available
            logger.warning("CMVK client not available, using mock verification")
            mock = MockCMVKVerifier(telemetry=self.telemetry)
            return await mock.verify(claim, context, verification_type)
        
        try:
            # Call real CMVK - API may vary based on actual cmvk package
            # This is a placeholder for the actual integration
            result = await self._cmvk.verify(
                claim=claim,
                context=context,
                verification_type=verification_type
            )
            
            return VerificationOutcome(
                is_valid=result.is_valid,
                confidence=result.confidence,
                verification_type=verification_type,
                details=result.details if hasattr(result, 'details') else {},
                verification_id=verification_id,
            )
            
        except Exception as e:
            self.telemetry.emit_event(
                event_type=EventType.FAILURE_DETECTED,
                data={
                    "verification_id": verification_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                severity="ERROR"
            )
            raise
    
    async def verify_completeness(
        self,
        agent_output: str,
        expected_coverage: List[str],
        context: Dict[str, Any]
    ) -> VerificationOutcome:
        """Verify completeness using CMVK."""
        return await self.verify(
            claim=agent_output,
            context={
                **context,
                "expected_coverage": expected_coverage,
                "check_type": "completeness"
            },
            verification_type="completeness"
        )
    
    async def verify_correctness(
        self,
        agent_output: str,
        ground_truth: Optional[str],
        context: Dict[str, Any]
    ) -> VerificationOutcome:
        """Verify correctness using CMVK."""
        return await self.verify(
            claim=agent_output,
            context={
                **context,
                "ground_truth": ground_truth,
                "check_type": "correctness"
            },
            verification_type="correctness"
        )


def create_verifier(
    use_production: bool = False,
    cmvk_client: Any = None,
    telemetry: Optional[TelemetryEmitter] = None
) -> CMVKVerifier:
    """
    Factory function to create appropriate CMVK verifier.
    
    Args:
        use_production: Whether to use production verifier
        cmvk_client: CMVK client instance (for production)
        telemetry: Telemetry emitter
        
    Returns:
        CMVKVerifier instance
    """
    if use_production:
        return ProductionCMVKVerifier(
            cmvk_client=cmvk_client,
            telemetry=telemetry
        )
    else:
        return MockCMVKVerifier(telemetry=telemetry)


__all__ = [
    "VerificationOutcome",
    "MockCMVKVerifier",
    "ProductionCMVKVerifier",
    "create_verifier",
]
