"""
Self-Correcting Agent Kernel - Layer 4 Extension for Control Plane.

This is the main entry point for SCAK as a plugin that fits into the Control Plane.
It implements:
1. Laziness Detection via CMVK verification
2. Self-Correction loops with patch lifecycle management
3. Generic agent support (no application-specific logic)

Architecture: Layer 4 (Extension/Plugin)
    - Inherits from Control Plane protocols
    - Uses CMVK for verification
    - Emits structured telemetry

Usage:
    # Standalone (with mocks)
    from scak import SelfCorrectingKernel
    kernel = SelfCorrectingKernel()
    
    # With Control Plane
    from agent_control_plane import ControlPlane
    from scak import SelfCorrectingKernel
    
    cp = ControlPlane()
    kernel = SelfCorrectingKernel(control_plane=cp)
    
    # With CMVK
    from cmvk import Verifier
    kernel = SelfCorrectingKernel(cmvk_verifier=Verifier())
"""

import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from src.interfaces.protocols import (
    CMVKVerifier,
    KernelExtension,
    AgentOutcomeEvent,
    PatchInstruction,
    AbstractCorrectionEngine,
    AbstractLazinessDetector,
)
from src.interfaces.telemetry import TelemetryEmitter, EventType
from src.integrations.cmvk_adapter import MockCMVKVerifier, VerificationOutcome, create_verifier
from src.integrations.control_plane_adapter import (
    AgentOutcome,
    CorrectionPatch,
    MockControlPlane,
    SCAKExtension,
    create_control_plane,
)
from src.kernel.circuit_breaker import CircuitBreakerRegistry, LoopDetectedError
from src.kernel.lazy_evaluator import LazyEvaluatorRegistry

logger = logging.getLogger(__name__)


class CorrectionResult(BaseModel):
    """Result of a self-correction operation."""
    
    success: bool = Field(..., description="Whether correction succeeded")
    agent_id: str = Field(..., description="Agent that was corrected")
    laziness_detected: bool = Field(default=False, description="Whether laziness was detected")
    patch: Optional[CorrectionPatch] = Field(None, description="Applied patch if any")
    verification_confidence: float = Field(default=0.0, description="CMVK verification confidence")
    message: str = Field(default="", description="Human-readable result message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SelfCorrectingKernel(AbstractCorrectionEngine, AbstractLazinessDetector):
    """
    Self-Correcting Agent Kernel - Layer 4 Extension.
    
    This is the main orchestrator that implements:
    1. Dual-Loop Architecture (Runtime Safety + Offline Alignment)
    2. Laziness Detection via CMVK verification
    3. Self-Correction with semantic patch lifecycle
    
    SCAK is GENERIC - it works with ANY agent through the Control Plane.
    No application-specific logic (e.g., mute-agent) is included.
    
    Dependencies:
        - agent-control-plane (optional, uses mock if not installed)
        - cmvk (optional, uses mock if not installed)
    """
    
    def __init__(
        self,
        control_plane: Any = None,
        cmvk_verifier: Optional[CMVKVerifier] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Self-Correcting Kernel.
        
        Args:
            control_plane: Control Plane instance (uses mock if None)
            cmvk_verifier: CMVK verifier for validation (uses mock if None)
            config: Configuration options
        """
        self.config = config or {}
        
        # Initialize Control Plane integration
        self._control_plane = control_plane or MockControlPlane()
        
        # Initialize CMVK verifier
        self._verifier = cmvk_verifier or MockCMVKVerifier()
        
        # Initialize telemetry
        self._agent_id = f"scak-kernel-{uuid.uuid4().hex[:8]}"
        self.telemetry = TelemetryEmitter(agent_id=self._agent_id)
        
        # Create and register SCAK extension with Control Plane
        self._extension = SCAKExtension(
            verifier=self._verifier,
            telemetry=self.telemetry,
            config=self.config,
        )
        self._control_plane.register_extension(self._extension)
        
        # Laziness detection configuration
        self._give_up_signals = self.config.get("give_up_signals", [
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
            "i apologize",
            "unfortunately",
        ])
        
        # Correction thresholds
        self._verification_threshold = self.config.get("verification_threshold", 0.6)
        self._auto_patch = self.config.get("auto_patch", True)
        
        # Statistics
        self._outcomes_processed = 0
        self._corrections_applied = 0
        self._laziness_count = 0
        
        # Model version tracking for semantic purge
        self._current_model_version = self.config.get("model_version", "gpt-4o")
        
        # Initialize Circuit Breaker (Loop Detection)
        self._enable_circuit_breaker = self.config.get("enable_circuit_breaker", True)
        self._circuit_breaker_registry = CircuitBreakerRegistry(
            default_repetition_threshold=self.config.get("loop_threshold", 3),
            default_history_window=self.config.get("loop_history_window", 10),
            telemetry=self.telemetry
        )
        
        # Initialize Lazy Evaluator (Deferred Computation)
        self._enable_lazy_eval = self.config.get("enable_lazy_eval", True)
        self._lazy_evaluator_registry = LazyEvaluatorRegistry(
            enable_lazy_eval=self._enable_lazy_eval,
            max_deferred_tasks=self.config.get("max_deferred_tasks", 100),
            telemetry=self.telemetry
        )
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "action": "kernel_initialized",
                "model_version": self._current_model_version,
                "auto_patch": self._auto_patch,
                "verification_threshold": self._verification_threshold,
                "circuit_breaker_enabled": self._enable_circuit_breaker,
                "lazy_eval_enabled": self._enable_lazy_eval,
            }
        )
        
        logger.info("=" * 80)
        logger.info("Self-Correcting Agent Kernel initialized (Layer 4)")
        logger.info(f"  Extension ID: {self._extension.extension_id}")
        logger.info(f"  Model Version: {self._current_model_version}")
        logger.info(f"  CMVK Verifier: {type(self._verifier).__name__}")
        logger.info(f"  Control Plane: {type(self._control_plane).__name__}")
        logger.info(f"  Circuit Breaker: {'Enabled' if self._enable_circuit_breaker else 'Disabled'}")
        logger.info(f"  Lazy Evaluation: {'Enabled' if self._enable_lazy_eval else 'Disabled'}")
        logger.info("=" * 80)
    
    # =========================================================================
    # AbstractCorrectionEngine Implementation
    # =========================================================================
    
    async def should_correct(
        self,
        outcome: AgentOutcomeEvent,
        verifier: CMVKVerifier
    ) -> bool:
        """
        Determine if correction is needed using CMVK verification.
        
        Args:
            outcome: Agent execution outcome
            verifier: CMVK verifier instance
            
        Returns:
            True if correction is needed
        """
        # Step 1: Check for give-up signals
        give_up_detected = self._detect_give_up_in_response(outcome.response)
        
        if not give_up_detected and outcome.success:
            return False
        
        # Step 2: Verify with CMVK
        verification = await verifier.verify(
            claim=outcome.response,
            context={
                "prompt": outcome.prompt,
                "agent_id": outcome.agent_id,
                "success": outcome.success,
            },
            verification_type="completeness"
        )
        
        return not verification.is_valid and verification.confidence >= self._verification_threshold
    
    async def generate_correction(
        self,
        outcome: AgentOutcomeEvent,
        verification_result: VerificationOutcome
    ) -> Optional[CorrectionPatch]:
        """
        Generate a correction patch for the agent.
        
        Args:
            outcome: Agent execution outcome
            verification_result: CMVK verification result
            
        Returns:
            CorrectionPatch if correction is possible
        """
        # Generate context-aware instruction
        prompt_lower = outcome.prompt.lower()
        
        if "log" in prompt_lower or "error" in prompt_lower:
            instruction = (
                "When searching for logs or errors, check archived partitions "
                "and historical data stores before reporting 'not found'."
            )
        elif "project" in prompt_lower or "resource" in prompt_lower:
            instruction = (
                "When looking up projects or resources, always check both "
                "active and archived registries."
            )
        elif "user" in prompt_lower or "customer" in prompt_lower:
            instruction = (
                "When querying user or customer data, ensure proper time windows "
                "and consider data partitioning."
            )
        else:
            instruction = (
                "Before reporting 'not found', verify all data sources "
                "have been checked including archived and backup stores."
            )
        
        patch = CorrectionPatch(
            agent_id=outcome.agent_id,
            instruction=instruction,
            patch_type="competence",
            confidence=verification_result.confidence,
            decay_type="TYPE_A",  # Can be purged on model upgrade
            source="scak-kernel",
            metadata={
                "verification_details": verification_result.details,
                "prompt_context": outcome.prompt[:100],
            }
        )
        
        self.telemetry.emit_event(
            event_type=EventType.PATCH_CREATED,
            data={
                "patch_id": patch.patch_id,
                "agent_id": patch.agent_id,
                "patch_type": patch.patch_type,
                "confidence": patch.confidence,
            }
        )
        
        return patch
    
    async def apply_correction(
        self,
        agent_id: str,
        patch: PatchInstruction
    ) -> bool:
        """
        Apply a correction to the agent.
        
        Args:
            agent_id: Target agent identifier
            patch: Patch to apply
            
        Returns:
            True if patch was applied successfully
        """
        return self._control_plane.apply_patch(patch)
    
    # =========================================================================
    # AbstractLazinessDetector Implementation
    # =========================================================================
    
    async def detect_laziness(
        self,
        agent_output: str,
        prompt: str,
        context: Dict[str, Any],
        verifier: CMVKVerifier
    ) -> bool:
        """
        Detect if agent was lazy (gave up prematurely).
        
        Args:
            agent_output: Agent's response
            prompt: Original user prompt
            context: Execution context
            verifier: CMVK verifier for validation
            
        Returns:
            True if laziness detected
        """
        # First check for give-up signals
        if not self._detect_give_up_in_response(agent_output):
            return False
        
        # Verify with CMVK that the give-up was premature
        verification = await verifier.verify_completeness(
            agent_output=agent_output,
            expected_coverage=self._extract_expected_topics(prompt),
            context=context
        )
        
        # Laziness = gave up signal + CMVK says incomplete
        is_lazy = not verification.is_valid and verification.confidence >= self._verification_threshold
        
        if is_lazy:
            self._laziness_count += 1
            self.telemetry.emit_event(
                event_type=EventType.LAZINESS_DETECTED,
                data={
                    "prompt_preview": prompt[:100],
                    "response_preview": agent_output[:100],
                    "verification_confidence": verification.confidence,
                }
            )
        
        return is_lazy
    
    def get_give_up_signals(self) -> List[str]:
        """Get the list of phrases that indicate agent gave up."""
        return self._give_up_signals.copy()
    
    # =========================================================================
    # Main API Methods
    # =========================================================================
    
    async def handle_outcome(
        self,
        agent_id: str,
        user_prompt: str,
        agent_response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> CorrectionResult:
        """
        Handle an agent outcome through the self-correction loop.
        
        This is the main entry point for processing agent outputs.
        
        Enhanced with:
        - Circuit Breaker: Detect and break loops (3x same action → same result)
        - Lazy Evaluation: Defer non-critical computations
        
        Args:
            agent_id: Identifier of the agent
            user_prompt: Original user request
            agent_response: Agent's response
            context: Additional context
            
        Returns:
            CorrectionResult with outcome analysis
            
        Raises:
            LoopDetectedError: If circuit breaker detects a loop
        """
        self._outcomes_processed += 1
        context = context or {}
        
        # Circuit Breaker: Record action-result pair and check for loops
        if self._enable_circuit_breaker:
            try:
                breaker = self._circuit_breaker_registry.get_or_create(agent_id)
                action = context.get("action", "unknown_action")
                action_params = context.get("action_params", {})
                result_summary = agent_response[:200]  # Truncate for comparison
                
                loop_detected = breaker.record_action_result(
                    action=action,
                    action_params=action_params,
                    result=result_summary
                )
                
                if loop_detected:
                    # Loop detected - this will raise LoopDetectedError if strategy is STOP_ITERATION
                    # Otherwise it returns True and we handle it here
                    logger.warning(f"Loop detected for agent {agent_id} - switching strategy")
                    
                    # Record loop event
                    self.telemetry.emit_event(
                        event_type=EventType.FAILURE_DETECTED,
                        data={
                            "agent_id": agent_id,
                            "loop_detected": True,
                            "action": action,
                            "message": "Agent stuck in loop - circuit breaker triggered"
                        }
                    )
                    
                    return CorrectionResult(
                        success=False,
                        agent_id=agent_id,
                        laziness_detected=False,
                        message="Loop detected - agent repeating same action with same result. "
                                "Circuit breaker triggered to prevent wasted computation.",
                    )
            except LoopDetectedError as e:
                # Loop detected with STOP_ITERATION strategy - re-raise
                logger.error(f"Circuit breaker stopped agent {agent_id}: {e}")
                raise
        
        # Create AgentOutcome
        outcome = AgentOutcome(
            agent_id=agent_id,
            prompt=user_prompt,
            response=agent_response,
            success=True,  # If we got a response, execution succeeded
            execution_time_ms=context.get("execution_time_ms", 0),
            context=context,
        )
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "agent_id": agent_id,
                "prompt_preview": user_prompt[:100],
                "response_preview": agent_response[:100],
            }
        )
        
        # Check if correction is needed
        needs_correction = await self.should_correct(outcome, self._verifier)
        
        if not needs_correction:
            return CorrectionResult(
                success=True,
                agent_id=agent_id,
                laziness_detected=False,
                message="Agent output verified - no correction needed",
            )
        
        # Lazy Evaluation: Check if correction can be deferred
        if self._enable_lazy_eval:
            evaluator = self._lazy_evaluator_registry.get_or_create(agent_id)
            decision = evaluator.should_defer(
                description=f"Correction analysis for: {user_prompt[:100]}",
                context=context,
                estimated_cost_ms=context.get("estimated_correction_cost_ms", 1000)
            )
            
            if decision.should_defer:
                # Defer the correction - create TODO token
                todo_token = evaluator.defer(
                    description=f"Analyze and correct: {user_prompt[:100]}",
                    reason=decision.reason,
                    context={
                        "prompt": user_prompt,
                        "response": agent_response,
                        "agent_id": agent_id
                    },
                    priority=context.get("priority", 5),
                    estimated_cost_ms=decision.estimated_savings_ms
                )
                
                logger.info(f"Correction deferred for agent {agent_id}: {decision.explanation}")
                
                return CorrectionResult(
                    success=True,
                    agent_id=agent_id,
                    laziness_detected=False,
                    message=f"Correction deferred: {decision.explanation}. "
                            f"TODO token created: {todo_token.token_id}",
                )
        
        # Verify with CMVK for confidence score
        verification = await self._verifier.verify(
            claim=agent_response,
            context={
                "prompt": user_prompt,
                "agent_id": agent_id,
            },
            verification_type="completeness"
        )
        
        # Generate correction
        patch = await self.generate_correction(outcome, verification)
        
        if patch and self._auto_patch:
            applied = await self.apply_correction(agent_id, patch)
            if applied:
                self._corrections_applied += 1
        
        return CorrectionResult(
            success=True,
            agent_id=agent_id,
            laziness_detected=True,
            patch=patch,
            verification_confidence=verification.confidence,
            message="Laziness detected - correction patch applied" if patch else "Laziness detected - no patch generated",
        )
    
    async def handle_failure(
        self,
        agent_id: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        user_prompt: Optional[str] = None,
    ) -> CorrectionResult:
        """
        Handle an explicit agent failure.
        
        Args:
            agent_id: Identifier of the failed agent
            error_message: Error message from the failure
            context: Additional context
            user_prompt: Original user prompt
            
        Returns:
            CorrectionResult with failure handling outcome
        """
        self._outcomes_processed += 1
        context = context or {}
        
        self.telemetry.emit_event(
            event_type=EventType.FAILURE_DETECTED,
            data={
                "agent_id": agent_id,
                "error_message": error_message[:200],
                "has_user_prompt": user_prompt is not None,
            }
        )
        
        # Create failure outcome
        outcome = AgentOutcome(
            agent_id=agent_id,
            prompt=user_prompt or "",
            response=error_message,
            success=False,
            execution_time_ms=context.get("execution_time_ms", 0),
            context=context,
        )
        
        # Generate correction patch for failure
        patch = CorrectionPatch(
            agent_id=agent_id,
            instruction=f"Previous failure: {error_message[:100]}. Avoid this error pattern.",
            patch_type="safety",
            confidence=0.7,
            decay_type="TYPE_A",
            source="scak-failure-handler",
            metadata={"error_message": error_message},
        )
        
        if self._auto_patch:
            await self.apply_correction(agent_id, patch)
            self._corrections_applied += 1
        
        self.telemetry.emit_event(
            event_type=EventType.FAILURE_ANALYZED,
            data={
                "agent_id": agent_id,
                "patch_id": patch.patch_id,
                "patch_type": patch.patch_type,
            }
        )
        
        return CorrectionResult(
            success=True,
            agent_id=agent_id,
            laziness_detected=False,
            patch=patch,
            verification_confidence=0.7,
            message="Failure handled - safety patch applied",
        )
    
    def upgrade_model(self, new_model_version: str) -> Dict[str, Any]:
        """
        Upgrade model version and trigger semantic purge.
        
        Type A patches (syntax/capability) are purged on model upgrade.
        Type B patches (business/context) are retained.
        
        Args:
            new_model_version: New model version
            
        Returns:
            Purge statistics
        """
        old_version = self._current_model_version
        self._current_model_version = new_model_version
        
        # Emit model upgrade event to Control Plane
        self._control_plane.emit_event(
            "model_upgrade",
            {
                "old_version": old_version,
                "new_version": new_model_version,
            }
        )
        
        self.telemetry.emit_event(
            event_type=EventType.MODEL_UPGRADE,
            data={
                "old_version": old_version,
                "new_version": new_model_version,
                "action": "semantic_purge_triggered",
            }
        )
        
        # In production, this would trigger actual patch purge
        return {
            "old_version": old_version,
            "new_version": new_model_version,
            "purge_triggered": True,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get kernel statistics including circuit breaker and lazy evaluation metrics."""
        stats = {
            "agent_id": self._agent_id,
            "model_version": self._current_model_version,
            "outcomes_processed": self._outcomes_processed,
            "corrections_applied": self._corrections_applied,
            "laziness_count": self._laziness_count,
            "laziness_rate": self._laziness_count / max(self._outcomes_processed, 1),
            "extension_stats": self._extension.get_statistics(),
        }
        
        # Add circuit breaker statistics
        if self._enable_circuit_breaker:
            stats["circuit_breaker"] = {
                "enabled": True,
                "agents": self._circuit_breaker_registry.get_all_statistics()
            }
        
        # Add lazy evaluation statistics
        if self._enable_lazy_eval:
            stats["lazy_evaluation"] = {
                "enabled": True,
                "agents": self._lazy_evaluator_registry.get_all_statistics(),
                "global": self._lazy_evaluator_registry.get_global_statistics()
            }
        
        return stats
    
    # =========================================================================
    # Private Helper Methods
    # =========================================================================
    
    def _detect_give_up_in_response(self, response: str) -> bool:
        """Check if response contains give-up signals."""
        response_lower = response.lower()
        return any(signal in response_lower for signal in self._give_up_signals)
    
    def _extract_expected_topics(self, prompt: str) -> List[str]:
        """Extract expected topics from prompt for completeness verification."""
        # Simple extraction - in production, use NLP
        words = prompt.lower().split()
        # Filter to nouns (simple heuristic)
        topics = [w for w in words if len(w) > 4 and w.isalpha()]
        return topics[:5]  # Limit to 5 topics


# =============================================================================
# Factory Functions
# =============================================================================

def create_kernel(
    control_plane: Any = None,
    cmvk_verifier: Optional[CMVKVerifier] = None,
    config: Optional[Dict[str, Any]] = None,
) -> SelfCorrectingKernel:
    """
    Factory function to create a Self-Correcting Kernel.
    
    Args:
        control_plane: Control Plane instance (optional)
        cmvk_verifier: CMVK verifier (optional)
        config: Configuration options
        
    Returns:
        Configured SelfCorrectingKernel
    """
    return SelfCorrectingKernel(
        control_plane=control_plane,
        cmvk_verifier=cmvk_verifier,
        config=config,
    )


__all__ = [
    "SelfCorrectingKernel",
    "CorrectionResult",
    "create_kernel",
]
