"""Interface components: telemetry and protocols.

This module provides:
1. Telemetry - Structured JSON logging for production systems
2. Protocols - Abstract interfaces for Control Plane and CMVK integration
"""

from .telemetry import TelemetryEmitter, OutcomeAnalyzer, AuditLog, EventType
from .protocols import (
    # CMVK Protocols
    VerificationResult,
    CMVKVerificationRequest,
    CMVKVerificationResponse,
    CMVKVerifier,
    
    # Control Plane Protocols
    AgentOutcomeEvent,
    PatchInstruction,
    ControlPlaneKernel,
    KernelExtension,
    
    # Abstract Base Classes
    AbstractCorrectionEngine,
    AbstractLazinessDetector,
    
    # Type Aliases
    VerificationContext,
    AgentContext,
    PatchMetadata,
)

__all__ = [
    # Telemetry
    "TelemetryEmitter",
    "OutcomeAnalyzer",
    "AuditLog",
    "EventType",
    
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
