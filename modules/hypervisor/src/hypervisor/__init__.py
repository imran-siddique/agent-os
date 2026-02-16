"""
Agent Hypervisor v1.0

Runtime supervisor for multi-agent Shared Sessions. Enforces a strict security
model based on Verified Intent, Joint Liability scoring, hardware-inspired
Execution Rings, and delta-based forensic audit trails.

The Hypervisor composes existing Agent-OS modules (IATP, CMVK, Nexus, CaaS, SCAK)
into a unified governance runtime for multi-agent collaboration.

Core Components:
    - SessionManager: Shared Session Object (SSO) lifecycle
    - LiabilityEngine: Vouching, bonding, and collateral slashing
    - RingEnforcer: 4-ring privilege model (Ring 0-3)
    - ReversibilityRegistry: Execute/Undo API mapping
    - SagaOrchestrator: Semantic saga with reverse-order compensation
    - DeltaAuditEngine: Merkle-chained semantic diffs

Usage:
    >>> from hypervisor import Hypervisor, SessionConfig, ConsistencyMode
    >>> hv = Hypervisor()
    >>> session = await hv.create_session(
    ...     config=SessionConfig(consistency_mode=ConsistencyMode.EVENTUAL)
    ... )

Version: 1.0.0
"""

__version__ = "1.0.0"

# Core models
from hypervisor.models import (
    ConsistencyMode,
    ExecutionRing,
    ReversibilityLevel,
    SessionConfig,
    SessionState,
)

# Session management
from hypervisor.session import SharedSessionObject

# Liability engine
from hypervisor.liability.vouching import VouchRecord, VouchingEngine
from hypervisor.liability.slashing import SlashingEngine
from hypervisor.liability import LiabilityMatrix

# Execution rings
from hypervisor.rings.enforcer import RingEnforcer
from hypervisor.rings.classifier import ActionClassifier

# Reversibility
from hypervisor.reversibility.registry import ReversibilityRegistry

# Saga
from hypervisor.saga.orchestrator import SagaOrchestrator
from hypervisor.saga.state_machine import SagaState, StepState

# Audit
from hypervisor.audit.delta import DeltaEngine
from hypervisor.audit.commitment import CommitmentEngine
from hypervisor.audit.gc import EphemeralGC

# Verification
from hypervisor.verification.history import TransactionHistoryVerifier

# Top-level orchestrator
from hypervisor.core import Hypervisor

__all__ = [
    # Version
    "__version__",
    # Core
    "Hypervisor",
    # Models
    "ConsistencyMode",
    "ExecutionRing",
    "ReversibilityLevel",
    "SessionConfig",
    "SessionState",
    # Session
    "SharedSessionObject",
    # Liability
    "VouchRecord",
    "VouchingEngine",
    "SlashingEngine",
    "LiabilityMatrix",
    # Rings
    "RingEnforcer",
    "ActionClassifier",
    # Reversibility
    "ReversibilityRegistry",
    # Saga
    "SagaOrchestrator",
    "SagaState",
    "StepState",
    # Audit
    "DeltaEngine",
    "CommitmentEngine",
    "EphemeralGC",
    # Verification
    "TransactionHistoryVerifier",
]
