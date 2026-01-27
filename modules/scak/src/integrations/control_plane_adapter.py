"""
Control Plane Adapter - Integration with Agent Control Plane (Layer 3).

SCAK (Layer 4) is a specialized "brain" that fits into the Control Plane.
This adapter provides:
1. Base classes that inherit from Control Plane abstractions
2. Event handling for agent outcomes
3. Patch application through Control Plane APIs

Publication Target: pip install scak
Dependency: agent-control-plane (pip install agent-control-plane)

Key Principle: SCAK is GENERIC - it can power ANY agent through the Control Plane,
not tied to specific applications like mute-agent.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..interfaces.protocols import (
    AgentOutcomeEvent,
    PatchInstruction,
    ControlPlaneKernel,
    KernelExtension,
    CMVKVerifier,
    AbstractCorrectionEngine,
    AbstractLazinessDetector,
)
from ..interfaces.telemetry import TelemetryEmitter, EventType
from .cmvk_adapter import MockCMVKVerifier, VerificationOutcome

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models for Control Plane Integration
# =============================================================================

class AgentOutcome(BaseModel):
    """Concrete implementation of AgentOutcomeEvent."""
    
    agent_id: str = Field(..., description="Unique agent identifier")
    prompt: str = Field(..., description="Original user prompt")
    response: str = Field(..., description="Agent's response")
    success: bool = Field(..., description="Whether execution succeeded")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Extended fields for SCAK
    give_up_detected: bool = Field(default=False, description="Whether agent gave up")
    tool_trace: Optional[str] = Field(None, description="Trace of tool invocations")
    chain_of_thought: Optional[List[str]] = Field(None, description="Reasoning steps")


class CorrectionPatch(BaseModel):
    """Concrete implementation of PatchInstruction."""
    
    patch_id: str = Field(default_factory=lambda: f"patch-{uuid.uuid4().hex[:8]}")
    agent_id: str = Field(..., description="Target agent identifier")
    instruction: str = Field(..., description="Patch instruction/lesson")
    patch_type: str = Field(..., description="Type of patch (competence, safety, etc.)")
    
    # Extended fields for SCAK
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    decay_type: str = Field(default="TYPE_A", description="TYPE_A (purge on upgrade) or TYPE_B (permanent)")
    source: str = Field(default="scak", description="Source of the patch")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Mock Control Plane for Testing
# =============================================================================

class MockControlPlane:
    """
    Mock Control Plane for testing and development.
    
    In production, this would be replaced by:
        from agent_control_plane import ControlPlane
        cp = ControlPlane()
    """
    
    def __init__(self, telemetry: Optional[TelemetryEmitter] = None):
        """Initialize mock control plane."""
        self.telemetry = telemetry or TelemetryEmitter(agent_id="control-plane-mock")
        self._extensions: Dict[str, KernelExtension] = {}
        self._patches: Dict[str, List[CorrectionPatch]] = {}
        self._event_log: List[Dict[str, Any]] = []
    
    def register_extension(self, extension: KernelExtension) -> None:
        """Register an extension with the control plane."""
        ext_id = extension.extension_id
        self._extensions[ext_id] = extension
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "action": "extension_registered",
                "extension_id": ext_id,
                "subscribed_events": extension.subscribed_events,
            }
        )
        logger.info(f"Extension registered: {ext_id}")
    
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to all subscribed extensions."""
        self._event_log.append({
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Route to subscribed extensions
        for ext_id, ext in self._extensions.items():
            if event_type in ext.subscribed_events:
                try:
                    # Note: In production, this would be async
                    # For mock, we ignore the coroutine
                    import asyncio
                    coro = ext.on_event(event_type, data)
                    if asyncio.iscoroutine(coro):
                        # In sync context, we can't await - log warning
                        logger.warning(f"Async event handler in sync context for {ext_id}")
                except Exception as e:
                    self.telemetry.emit_event(
                        event_type=EventType.FAILURE_DETECTED,
                        data={
                            "extension_id": ext_id,
                            "event_type": event_type,
                            "error": str(e),
                        },
                        severity="ERROR"
                    )
    
    async def handle_outcome(self, outcome: AgentOutcomeEvent) -> None:
        """Handle an agent outcome event."""
        for ext_id, ext in self._extensions.items():
            if "agent_outcome" in ext.subscribed_events:
                try:
                    patch = await ext.on_agent_outcome(outcome)
                    if patch:
                        self.apply_patch(patch)
                except Exception as e:
                    self.telemetry.emit_event(
                        event_type=EventType.FAILURE_DETECTED,
                        data={
                            "extension_id": ext_id,
                            "agent_id": outcome.agent_id,
                            "error": str(e),
                        },
                        severity="ERROR"
                    )
    
    def apply_patch(self, patch: PatchInstruction) -> bool:
        """Apply a patch instruction to an agent."""
        agent_id = patch.agent_id
        
        if agent_id not in self._patches:
            self._patches[agent_id] = []
        
        # Store as generic patch instruction
        self._patches[agent_id].append(CorrectionPatch(
            patch_id=patch.patch_id,
            agent_id=patch.agent_id,
            instruction=patch.instruction,
            patch_type=patch.patch_type,
        ))
        
        self.telemetry.emit_event(
            event_type=EventType.PATCH_APPLIED,
            data={
                "patch_id": patch.patch_id,
                "agent_id": agent_id,
                "patch_type": patch.patch_type,
                "instruction_preview": patch.instruction[:100],
            }
        )
        
        logger.info(f"Patch {patch.patch_id} applied to agent {agent_id}")
        return True
    
    def get_patches(self, agent_id: str) -> List[CorrectionPatch]:
        """Get all patches for an agent."""
        return self._patches.get(agent_id, [])


# =============================================================================
# SCAK Extension - The Self-Correcting Brain
# =============================================================================

class SCAKExtension(KernelExtension):
    """
    SCAK Extension for Control Plane.
    
    This is the main integration point - SCAK as a plugin that:
    1. Subscribes to agent outcomes
    2. Uses CMVK to verify if correction is needed
    3. Generates and applies patches through Control Plane
    
    Usage:
        from agent_control_plane import ControlPlane
        from scak.integrations import SCAKExtension
        
        cp = ControlPlane()
        scak = SCAKExtension(verifier=my_cmvk_verifier)
        cp.register_extension(scak)
    """
    
    def __init__(
        self,
        verifier: Optional[CMVKVerifier] = None,
        telemetry: Optional[TelemetryEmitter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize SCAK extension.
        
        Args:
            verifier: CMVK verifier for validation (uses mock if None)
            telemetry: Telemetry emitter
            config: Configuration options
        """
        self._extension_id = f"scak-{uuid.uuid4().hex[:8]}"
        self._verifier = verifier or MockCMVKVerifier()
        self.telemetry = telemetry or TelemetryEmitter(agent_id=self._extension_id)
        self.config = config or {}
        
        # Laziness detection configuration
        self.give_up_signals = self.config.get("give_up_signals", [
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
        self.verification_threshold = self.config.get("verification_threshold", 0.7)
        self.auto_patch = self.config.get("auto_patch", True)
        
        # Statistics
        self._outcomes_processed = 0
        self._patches_generated = 0
        self._laziness_detected = 0
    
    @property
    def extension_id(self) -> str:
        """Unique identifier for this extension."""
        return self._extension_id
    
    @property
    def subscribed_events(self) -> List[str]:
        """List of event types this extension handles."""
        return [
            "agent_outcome",
            "agent_failure",
            "model_upgrade",
        ]
    
    async def on_event(self, event_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle an event from the control plane.
        
        Args:
            event_type: Type of event
            data: Event data
            
        Returns:
            Optional response/modification to the event
        """
        if event_type == "model_upgrade":
            return await self._handle_model_upgrade(data)
        
        return None
    
    async def on_agent_outcome(self, outcome: AgentOutcomeEvent) -> Optional[CorrectionPatch]:
        """
        Process an agent outcome and optionally return a patch.
        
        This is the core SCAK logic:
        1. Detect give-up signals
        2. Verify with CMVK if correction needed
        3. Generate patch if laziness/issue detected
        
        Args:
            outcome: The agent's execution outcome
            
        Returns:
            CorrectionPatch if correction is needed
        """
        self._outcomes_processed += 1
        
        # Step 1: Check for give-up signals
        give_up_detected = self._detect_give_up(outcome.response)
        
        if not give_up_detected and outcome.success:
            # No issues detected
            return None
        
        # Step 2: Verify with CMVK
        verification = await self._verifier.verify(
            claim=outcome.response,
            context={
                "prompt": outcome.prompt,
                "agent_id": outcome.agent_id,
                "success": outcome.success,
            },
            verification_type="completeness"
        )
        
        self.telemetry.emit_event(
            event_type=EventType.AUDIT_COMPLETED,
            data={
                "agent_id": outcome.agent_id,
                "give_up_detected": give_up_detected,
                "verification_valid": verification.is_valid,
                "verification_confidence": verification.confidence,
            }
        )
        
        # Step 3: Generate patch if needed
        if not verification.is_valid and verification.confidence >= self.verification_threshold:
            self._laziness_detected += 1
            
            self.telemetry.emit_event(
                event_type=EventType.LAZINESS_DETECTED,
                data={
                    "agent_id": outcome.agent_id,
                    "prompt_preview": outcome.prompt[:100],
                    "response_preview": outcome.response[:100],
                    "confidence": verification.confidence,
                }
            )
            
            patch = self._generate_patch(outcome, verification)
            self._patches_generated += 1
            
            return patch
        
        return None
    
    def _detect_give_up(self, response: str) -> bool:
        """Detect if agent gave up based on response."""
        response_lower = response.lower()
        return any(signal in response_lower for signal in self.give_up_signals)
    
    def _generate_patch(
        self,
        outcome: AgentOutcomeEvent,
        verification: VerificationOutcome
    ) -> CorrectionPatch:
        """
        Generate a correction patch based on outcome and verification.
        
        Args:
            outcome: The agent's outcome
            verification: CMVK verification result
            
        Returns:
            CorrectionPatch to apply
        """
        # Analyze the failure to generate appropriate instruction
        prompt_context = outcome.prompt.lower()
        
        # Generate context-aware instruction
        if "log" in prompt_context or "error" in prompt_context:
            instruction = (
                "When searching for logs or errors, check archived partitions "
                "and historical data stores before reporting 'not found'. "
                f"Previous failure context: {outcome.prompt[:50]}..."
            )
        elif "project" in prompt_context or "resource" in prompt_context:
            instruction = (
                "When looking up projects or resources, always check both "
                "active and archived registries. Resources may be archived "
                "but still accessible. "
                f"Previous failure context: {outcome.prompt[:50]}..."
            )
        elif "user" in prompt_context or "customer" in prompt_context:
            instruction = (
                "When querying user or customer data, ensure proper time windows "
                "and consider data partitioning. Empty results may indicate "
                "incorrect query parameters. "
                f"Previous failure context: {outcome.prompt[:50]}..."
            )
        else:
            instruction = (
                "Before reporting 'not found' or giving up, verify all data sources "
                "have been checked including archived, historical, and backup stores. "
                f"Previous failure context: {outcome.prompt[:50]}..."
            )
        
        patch = CorrectionPatch(
            agent_id=outcome.agent_id,
            instruction=instruction,
            patch_type="competence",
            confidence=verification.confidence,
            decay_type="TYPE_A",  # Can be purged on model upgrade
            source="scak-laziness-detector",
            metadata={
                "verification_details": verification.details,
                "give_up_signal": True,
            }
        )
        
        self.telemetry.emit_event(
            event_type=EventType.PATCH_CREATED,
            data={
                "patch_id": patch.patch_id,
                "agent_id": patch.agent_id,
                "patch_type": patch.patch_type,
                "decay_type": patch.decay_type,
                "confidence": patch.confidence,
            }
        )
        
        return patch
    
    async def _handle_model_upgrade(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle model upgrade event - trigger semantic purge.
        
        Args:
            data: Event data with model version info
            
        Returns:
            Purge statistics
        """
        old_version = data.get("old_version", "unknown")
        new_version = data.get("new_version", "unknown")
        
        self.telemetry.emit_event(
            event_type=EventType.MODEL_UPGRADE,
            data={
                "old_version": old_version,
                "new_version": new_version,
                "action": "semantic_purge_triggered",
            }
        )
        
        # In production, this would trigger SemanticPurge
        # For now, return metadata
        return {
            "purge_triggered": True,
            "old_version": old_version,
            "new_version": new_version,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get extension statistics."""
        return {
            "extension_id": self._extension_id,
            "outcomes_processed": self._outcomes_processed,
            "patches_generated": self._patches_generated,
            "laziness_detected": self._laziness_detected,
            "laziness_rate": (
                self._laziness_detected / max(self._outcomes_processed, 1)
            ),
        }


# =============================================================================
# Production Control Plane Adapter
# =============================================================================

class ProductionControlPlaneAdapter:
    """
    Production adapter for real Control Plane integration.
    
    Usage:
        from agent_control_plane import ControlPlane
        from scak.integrations import ProductionControlPlaneAdapter
        
        cp = ControlPlane()
        adapter = ProductionControlPlaneAdapter(control_plane=cp)
        adapter.register_scak()
    """
    
    def __init__(
        self,
        control_plane: Any = None,
        verifier: Optional[CMVKVerifier] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize production adapter.
        
        Args:
            control_plane: The actual Control Plane instance
            verifier: CMVK verifier
            config: Configuration
        """
        self._control_plane = control_plane
        self._verifier = verifier
        self.config = config or {}
        self._scak_extension: Optional[SCAKExtension] = None
        
        if self._control_plane is None:
            logger.warning(
                "ProductionControlPlaneAdapter initialized without control_plane. "
                "Install with: pip install agent-control-plane"
            )
    
    def register_scak(self) -> SCAKExtension:
        """
        Register SCAK extension with the Control Plane.
        
        Returns:
            The registered SCAKExtension
        """
        self._scak_extension = SCAKExtension(
            verifier=self._verifier,
            config=self.config
        )
        
        if self._control_plane:
            self._control_plane.register_extension(self._scak_extension)
        else:
            logger.warning("No control plane available - SCAK running standalone")
        
        return self._scak_extension
    
    def get_extension(self) -> Optional[SCAKExtension]:
        """Get the registered SCAK extension."""
        return self._scak_extension


# =============================================================================
# Factory Functions
# =============================================================================

def create_control_plane(
    use_production: bool = False,
    control_plane_client: Any = None,
    telemetry: Optional[TelemetryEmitter] = None
) -> ControlPlaneKernel:
    """
    Factory function to create appropriate control plane.
    
    Args:
        use_production: Whether to use production control plane
        control_plane_client: Control plane client instance
        telemetry: Telemetry emitter
        
    Returns:
        ControlPlaneKernel instance
    """
    if use_production and control_plane_client:
        return control_plane_client
    else:
        return MockControlPlane(telemetry=telemetry)


def create_scak_extension(
    verifier: Optional[CMVKVerifier] = None,
    config: Optional[Dict[str, Any]] = None
) -> SCAKExtension:
    """
    Factory function to create SCAK extension.
    
    Args:
        verifier: CMVK verifier (uses mock if None)
        config: Configuration options
        
    Returns:
        SCAKExtension instance
    """
    return SCAKExtension(verifier=verifier, config=config)


__all__ = [
    # Data Models
    "AgentOutcome",
    "CorrectionPatch",
    
    # Mock Implementation
    "MockControlPlane",
    
    # SCAK Extension
    "SCAKExtension",
    
    # Production Adapter
    "ProductionControlPlaneAdapter",
    
    # Factory Functions
    "create_control_plane",
    "create_scak_extension",
]
