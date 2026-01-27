"""
Self-Correcting Agent Kernel (SCAK) - Layer 4 Extension for Control Plane.

SCAK is a specialized "brain" that fits into the Control Plane (Layer 3).
It implements:
1. Laziness Detection - Identifies when agents give up prematurely
2. Self-Correction Loops - Generates and applies patches via CMVK verification

Architecture:
    Layer 4: SCAK (Extension/Plugin)
    Layer 3: Control Plane (agent-control-plane)
    Verification: CMVK (cmvk)

Installation:
    pip install scak                    # Core only
    pip install scak[control-plane]     # With Control Plane
    pip install scak[cmvk]              # With CMVK
    pip install scak[full]              # Full stack

Usage:
    # Standalone (with mocks for development)
    from scak import SelfCorrectingKernel
    kernel = SelfCorrectingKernel()
    result = await kernel.handle_outcome(agent_id, prompt, response)
    
    # With Control Plane
    from agent_control_plane import ControlPlane
    from scak import SelfCorrectingKernel
    kernel = SelfCorrectingKernel(control_plane=ControlPlane())
    
    # With CMVK
    from cmvk import Verifier
    from scak import SelfCorrectingKernel
    kernel = SelfCorrectingKernel(cmvk_verifier=Verifier())

Key Principle: SCAK is GENERIC - it works with ANY agent, not tied to
specific applications. No mute-agent or other application-specific logic.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

__version__ = "2.0.0"

# Core Kernel (Layer 4)
from src.kernel.core import SelfCorrectingKernel, CorrectionResult, create_kernel
from src.kernel.triage import FailureTriage, FixStrategy
from src.kernel.memory import MemoryManager, PatchClassifier, SemanticPurge, LessonType

# Integrations
from src.integrations.control_plane_adapter import (
    AgentOutcome,
    CorrectionPatch,
    SCAKExtension,
    MockControlPlane,
    create_control_plane,
)
from src.integrations.cmvk_adapter import (
    MockCMVKVerifier,
    ProductionCMVKVerifier,
    VerificationOutcome,
    create_verifier,
)

# Interfaces (Protocols)
from src.interfaces.protocols import (
    CMVKVerifier,
    KernelExtension,
    AbstractCorrectionEngine,
    AbstractLazinessDetector,
)
from src.interfaces.telemetry import TelemetryEmitter, AuditLog, EventType

# Agent Components
from src.agents.shadow_teacher import ShadowTeacher, diagnose_failure, counterfactual_run
from src.agents.worker import AgentWorker, WorkerPool, AgentStatus

__all__ = [
    # Core Kernel
    "SelfCorrectingKernel",
    "CorrectionResult",
    "create_kernel",
    "FailureTriage",
    "FixStrategy",
    "MemoryManager",
    "PatchClassifier",
    "SemanticPurge",
    "LessonType",
    
    # Control Plane Integration
    "AgentOutcome",
    "CorrectionPatch",
    "SCAKExtension",
    "MockControlPlane",
    "create_control_plane",
    
    # CMVK Integration
    "CMVKVerifier",
    "MockCMVKVerifier",
    "ProductionCMVKVerifier",
    "VerificationOutcome",
    "create_verifier",
    
    # Protocols
    "KernelExtension",
    "AbstractCorrectionEngine",
    "AbstractLazinessDetector",
    
    # Telemetry
    "TelemetryEmitter",
    "AuditLog",
    "EventType",
    
    # Agent Components
    "ShadowTeacher",
    "diagnose_failure",
    "counterfactual_run",
    "AgentWorker",
    "WorkerPool",
    "AgentStatus",
]
