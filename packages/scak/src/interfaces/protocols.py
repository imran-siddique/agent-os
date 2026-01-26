"""
Protocols - Abstract Interfaces for Control Plane and CMVK Integration.

Layer 4 (Extension/Plugin) requires well-defined interfaces to integrate
with the Control Plane (Layer 3) and CMVK (verification layer).

This module defines the contracts that SCAK uses to:
1. Register as a Control Plane extension
2. Delegate verification to CMVK
3. Remain generic (no application-specific logic)

Key Principle: SCAK is a "brain" that can power ANY agent, not just specific ones.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from datetime import datetime
from pydantic import BaseModel, Field


# =============================================================================
# CMVK Integration Protocols
# =============================================================================

@runtime_checkable
class VerificationResult(Protocol):
    """Protocol for CMVK verification results."""
    
    is_valid: bool
    confidence: float
    verification_type: str
    details: Dict[str, Any]


class CMVKVerificationRequest(BaseModel):
    """Request model for CMVK verification."""
    
    claim: str = Field(..., description="The claim or output to verify")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context for verification")
    verification_type: str = Field(default="completeness", description="Type of verification")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CMVKVerificationResponse(BaseModel):
    """Response model from CMVK verification."""
    
    is_valid: bool = Field(..., description="Whether the claim passed verification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    verification_type: str = Field(..., description="Type of verification performed")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed findings")
    corrections: Optional[List[str]] = Field(None, description="Suggested corrections if invalid")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


@runtime_checkable
class CMVKVerifier(Protocol):
    """
    Protocol for CMVK integration.
    
    CMVK (Claim-based Model Verification Kernel) provides verification
    services that SCAK uses to determine if correction is needed.
    
    In production, this would be:
        from cmvk import Verifier
        verifier = Verifier()
    """
    
    async def verify(
        self,
        claim: str,
        context: Dict[str, Any],
        verification_type: str = "completeness"
    ) -> VerificationResult:
        """
        Verify a claim using CMVK.
        
        Args:
            claim: The claim/output to verify
            context: Context for verification (prompt, tools, etc.)
            verification_type: Type of verification to perform
            
        Returns:
            VerificationResult with validity and confidence
        """
        ...
    
    async def verify_completeness(
        self,
        agent_output: str,
        expected_coverage: List[str],
        context: Dict[str, Any]
    ) -> VerificationResult:
        """
        Verify that agent output covers expected information.
        
        Used by Completeness Auditor to detect laziness.
        
        Args:
            agent_output: The agent's response
            expected_coverage: Topics/data that should be covered
            context: Execution context
            
        Returns:
            VerificationResult indicating completeness
        """
        ...
    
    async def verify_correctness(
        self,
        agent_output: str,
        ground_truth: Optional[str],
        context: Dict[str, Any]
    ) -> VerificationResult:
        """
        Verify that agent output is factually correct.
        
        Args:
            agent_output: The agent's response
            ground_truth: Known correct answer (if available)
            context: Execution context
            
        Returns:
            VerificationResult indicating correctness
        """
        ...


# =============================================================================
# Control Plane Integration Protocols
# =============================================================================

@runtime_checkable
class AgentOutcomeEvent(Protocol):
    """Protocol for agent outcome events from Control Plane."""
    
    agent_id: str
    prompt: str
    response: str
    success: bool
    execution_time_ms: int
    context: Dict[str, Any]


@runtime_checkable
class PatchInstruction(Protocol):
    """Protocol for patch instructions to be applied."""
    
    patch_id: str
    agent_id: str
    instruction: str
    patch_type: str


@runtime_checkable
class ControlPlaneKernel(Protocol):
    """
    Protocol for Control Plane Kernel that SCAK extends.
    
    SCAK inherits from or wraps the Control Plane's base Kernel/Agent class
    to add self-correction capabilities.
    
    In production, this would be:
        from agent_control_plane import BaseKernel
        class SelfCorrectingKernel(BaseKernel):
            ...
    """
    
    def register_extension(self, extension: "KernelExtension") -> None:
        """Register an extension with the control plane."""
        ...
    
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to the control plane."""
        ...
    
    async def handle_outcome(self, outcome: AgentOutcomeEvent) -> None:
        """Handle an agent outcome event."""
        ...
    
    def apply_patch(self, patch: PatchInstruction) -> bool:
        """Apply a patch instruction to an agent."""
        ...


@runtime_checkable
class KernelExtension(Protocol):
    """
    Protocol for kernel extensions (like SCAK).
    
    Extensions can:
    1. Subscribe to specific events
    2. Intercept and modify outcomes
    3. Apply corrections to agents
    """
    
    @property
    def extension_id(self) -> str:
        """Unique identifier for this extension."""
        ...
    
    @property
    def subscribed_events(self) -> List[str]:
        """List of event types this extension handles."""
        ...
    
    async def on_event(self, event_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle an event from the control plane.
        
        Args:
            event_type: Type of event
            data: Event data
            
        Returns:
            Optional response/modification to the event
        """
        ...
    
    async def on_agent_outcome(self, outcome: AgentOutcomeEvent) -> Optional[PatchInstruction]:
        """
        Process an agent outcome and optionally return a patch.
        
        Args:
            outcome: The agent's execution outcome
            
        Returns:
            Optional patch instruction if correction is needed
        """
        ...


# =============================================================================
# Abstract Base Classes (for inheritance-based integration)
# =============================================================================

class AbstractCorrectionEngine(ABC):
    """
    Abstract base for self-correction engines.
    
    This is what SCAK implements - the "brain" that decides
    when and how to correct agent behavior.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def generate_correction(
        self,
        outcome: AgentOutcomeEvent,
        verification_result: VerificationResult
    ) -> Optional[PatchInstruction]:
        """
        Generate a correction patch for the agent.
        
        Args:
            outcome: Agent execution outcome
            verification_result: CMVK verification result
            
        Returns:
            Patch instruction if correction is possible
        """
        pass
    
    @abstractmethod
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
        pass


class AbstractLazinessDetector(ABC):
    """
    Abstract base for laziness detection.
    
    Laziness = Agent gives up when it could have succeeded.
    This is detected by comparing agent output with CMVK verification.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_give_up_signals(self) -> List[str]:
        """Get the list of phrases that indicate agent gave up."""
        pass


# =============================================================================
# Type Aliases for Cleaner Signatures
# =============================================================================

VerificationContext = Dict[str, Any]
AgentContext = Dict[str, Any]
PatchMetadata = Dict[str, Any]


__all__ = [
    # CMVK Protocols
    "VerificationResult",
    "CMVKVerificationRequest",
    "CMVKVerificationResponse",
    "CMVKVerifier",
    
    # Control Plane Protocols
    "AgentOutcomeEvent",
    "PatchInstruction",
    "ControlPlaneKernel",
    "KernelExtension",
    
    # Abstract Base Classes
    "AbstractCorrectionEngine",
    "AbstractLazinessDetector",
    
    # Type Aliases
    "VerificationContext",
    "AgentContext",
    "PatchMetadata",
]
