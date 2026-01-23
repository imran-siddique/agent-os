"""
Inter-Agent Trust Protocol (IATP)

A Zero-Config Sidecar for Agent Communication that provides:
- Discovery: Capability manifest exchange
- Trust: Security validation and privacy checks
- Reversibility: Transaction tracking and audit logging
"""

__version__ = "0.1.0"

from iatp.models import (
    CapabilityManifest,
    AgentCapabilities,
    PrivacyContract,
    TrustLevel,
    ReversibilityLevel,
    RetentionPolicy,
    QuarantineSession,
    TracingContext,
)

from iatp.sidecar import SidecarProxy, create_sidecar
from iatp.security import SecurityValidator, PrivacyScrubber
from iatp.telemetry import FlightRecorder, TraceIDGenerator

__all__ = [
    # Models
    "CapabilityManifest",
    "AgentCapabilities",
    "PrivacyContract",
    "TrustLevel",
    "ReversibilityLevel",
    "RetentionPolicy",
    "QuarantineSession",
    "TracingContext",
    # Sidecar
    "SidecarProxy",
    "create_sidecar",
    # Security
    "SecurityValidator",
    "PrivacyScrubber",
    # Telemetry
    "FlightRecorder",
    "TraceIDGenerator",
]
