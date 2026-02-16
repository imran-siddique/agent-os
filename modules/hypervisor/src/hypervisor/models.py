"""Core data models for the Agent Hypervisor."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class ConsistencyMode(str, Enum):
    """Session consistency mode. Strong requires consensus; Eventual uses gossip."""

    STRONG = "strong"
    EVENTUAL = "eventual"


class ExecutionRing(int, Enum):
    """
    Hardware-inspired execution privilege rings.

    Ring 0 (Root): Hypervisor config & slashing — requires SRE Witness.
    Ring 1 (Privileged): Non-reversible actions — requires σ_eff > 0.95 + consensus.
    Ring 2 (Standard): Reversible actions — requires σ_eff > 0.60.
    Ring 3 (Sandbox): Read-only / research — default for unknown agents.
    """

    RING_0_ROOT = 0
    RING_1_PRIVILEGED = 1
    RING_2_STANDARD = 2
    RING_3_SANDBOX = 3

    @classmethod
    def from_sigma_eff(cls, sigma_eff: float, has_consensus: bool = False) -> ExecutionRing:
        """Derive ring level from effective reputation score."""
        if sigma_eff > 0.95 and has_consensus:
            return cls.RING_1_PRIVILEGED
        elif sigma_eff > 0.60:
            return cls.RING_2_STANDARD
        else:
            return cls.RING_3_SANDBOX


class ReversibilityLevel(str, Enum):
    """How reversible an action is."""

    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"

    @property
    def risk_weight_range(self) -> tuple[float, float]:
        """Return the (min, max) risk weight ω for this reversibility level."""
        if self == ReversibilityLevel.FULL:
            return (0.1, 0.3)
        elif self == ReversibilityLevel.PARTIAL:
            return (0.5, 0.8)
        else:
            return (0.9, 1.0)

    @property
    def default_risk_weight(self) -> float:
        """Return the default ω for this level."""
        lo, hi = self.risk_weight_range
        return (lo + hi) / 2


class SessionState(str, Enum):
    """Lifecycle state of a Shared Session."""

    CREATED = "created"
    HANDSHAKING = "handshaking"
    ACTIVE = "active"
    TERMINATING = "terminating"
    ARCHIVED = "archived"


@dataclass
class SessionConfig:
    """Configuration for a new Shared Session."""

    consistency_mode: ConsistencyMode = ConsistencyMode.EVENTUAL
    max_participants: int = 10
    max_duration_seconds: int = 3600
    min_sigma_eff: float = 0.60
    enable_audit: bool = True
    enable_blockchain_commitment: bool = False


@dataclass
class SessionParticipant:
    """An agent participating in a session."""

    agent_did: str
    ring: ExecutionRing = ExecutionRing.RING_3_SANDBOX
    sigma_raw: float = 0.0
    sigma_eff: float = 0.0
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class ActionDescriptor:
    """Describes an action from an IATP Capability Manifest."""

    action_id: str
    name: str
    execute_api: str
    undo_api: Optional[str] = None
    reversibility: ReversibilityLevel = ReversibilityLevel.NONE
    undo_window_seconds: int = 0
    compensation_method: Optional[str] = None
    is_read_only: bool = False
    is_admin: bool = False

    @property
    def risk_weight(self) -> float:
        """Compute ω from reversibility level."""
        return self.reversibility.default_risk_weight

    @property
    def required_ring(self) -> ExecutionRing:
        """Determine minimum ring required for this action."""
        if self.is_admin:
            return ExecutionRing.RING_0_ROOT
        elif self.reversibility == ReversibilityLevel.NONE and not self.is_read_only:
            return ExecutionRing.RING_1_PRIVILEGED
        elif self.is_read_only:
            return ExecutionRing.RING_3_SANDBOX
        else:
            return ExecutionRing.RING_2_STANDARD
