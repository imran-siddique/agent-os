"""
Hypervisor — Top-level orchestrator for multi-agent Shared Sessions.

Composes all submodules (Session, Liability, Rings, Reversibility,
Saga, Audit, Verification) into a unified governance runtime.
"""

from __future__ import annotations

from typing import Any, Optional

from hypervisor.audit.commitment import CommitmentEngine
from hypervisor.audit.delta import DeltaEngine, VFSChange
from hypervisor.audit.gc import EphemeralGC, RetentionPolicy
from hypervisor.liability.slashing import SlashingEngine
from hypervisor.liability.vouching import VouchingEngine
from hypervisor.models import (
    ActionDescriptor,
    ConsistencyMode,
    ExecutionRing,
    SessionConfig,
)
from hypervisor.reversibility.registry import ReversibilityRegistry
from hypervisor.rings.classifier import ActionClassifier
from hypervisor.rings.enforcer import RingEnforcer
from hypervisor.saga.orchestrator import SagaOrchestrator
from hypervisor.session import SharedSessionObject
from hypervisor.verification.history import TransactionHistoryVerifier


class ManagedSession:
    """A session with all its associated engines wired together."""

    def __init__(self, sso: SharedSessionObject) -> None:
        self.sso = sso
        self.reversibility = ReversibilityRegistry(sso.session_id)
        self.delta_engine = DeltaEngine(sso.session_id)
        self.saga = SagaOrchestrator()


class Hypervisor:
    """
    Top-level orchestrator for the Agent Hypervisor.

    Usage:
        hv = Hypervisor()
        session = await hv.create_session(config, creator_did="did:mesh:admin")
        await hv.join_session(session.sso.session_id, "did:mesh:agent-1", manifest)
        # ... execute actions ...
        await hv.terminate_session(session.sso.session_id)
    """

    def __init__(
        self,
        retention_policy: Optional[RetentionPolicy] = None,
    ) -> None:
        # Shared engines
        self.vouching = VouchingEngine()
        self.slashing = SlashingEngine(self.vouching)
        self.ring_enforcer = RingEnforcer()
        self.classifier = ActionClassifier()
        self.verifier = TransactionHistoryVerifier()
        self.commitment = CommitmentEngine()
        self.gc = EphemeralGC(retention_policy)

        # Active sessions
        self._sessions: dict[str, ManagedSession] = {}

    async def create_session(
        self,
        config: SessionConfig,
        creator_did: str,
    ) -> ManagedSession:
        """Create a new Shared Session."""
        sso = SharedSessionObject(config=config, creator_did=creator_did)
        sso.begin_handshake()
        managed = ManagedSession(sso)
        self._sessions[sso.session_id] = managed
        return managed

    async def join_session(
        self,
        session_id: str,
        agent_did: str,
        actions: Optional[list[ActionDescriptor]] = None,
        sigma_raw: float = 0.0,
    ) -> ExecutionRing:
        """
        Join an agent to a session via extended IATP handshake.

        Steps:
        1. Register actions in Reversibility Registry
        2. Force Strong mode if non-reversible actions exist
        3. Verify DID transaction history
        4. Compute σ_eff and assign ring
        """
        managed = self._get_session(session_id)

        # Step 1: Register actions
        if actions:
            managed.reversibility.register_from_manifest(actions)

        # Step 2: Mode negotiation
        if managed.reversibility.has_non_reversible_actions():
            managed.sso.force_consistency_mode(ConsistencyMode.STRONG)

        # Step 3: Verify history
        verification = self.verifier.verify(agent_did)

        # Step 4: Compute effective score
        # For now, use raw score; vouching adjusts later
        sigma_eff = sigma_raw
        ring = self.ring_enforcer.compute_ring(sigma_eff)

        # Probationary agents get sandbox
        if not verification.is_trustworthy:
            ring = ExecutionRing.RING_3_SANDBOX

        # Join the session
        managed.sso.join(
            agent_did=agent_did,
            sigma_raw=sigma_raw,
            sigma_eff=sigma_eff,
            ring=ring,
        )

        return ring

    async def activate_session(self, session_id: str) -> None:
        """Activate a session after handshaking is complete."""
        managed = self._get_session(session_id)
        managed.sso.activate()

    async def terminate_session(self, session_id: str) -> Optional[str]:
        """
        Terminate a session and commit audit trail.

        Returns:
            Merkle root Summary Hash, or None if audit disabled
        """
        managed = self._get_session(session_id)
        managed.sso.terminate()

        merkle_root = None
        if managed.sso.config.enable_audit:
            merkle_root = managed.delta_engine.compute_merkle_root()
            if merkle_root:
                self.commitment.commit(
                    session_id=session_id,
                    merkle_root=merkle_root,
                    participant_dids=[p.agent_did for p in managed.sso.participants],
                    delta_count=managed.delta_engine.turn_count,
                )

        # Release all bonds
        self.vouching.release_session_bonds(session_id)

        # GC
        self.gc.collect(
            session_id=session_id,
            delta_count=managed.delta_engine.turn_count,
        )

        # Archive
        managed.sso.archive()

        return merkle_root

    def get_session(self, session_id: str) -> Optional[ManagedSession]:
        return self._sessions.get(session_id)

    @property
    def active_sessions(self) -> list[ManagedSession]:
        return [
            m for m in self._sessions.values()
            if m.sso.state.value not in ("archived", "terminating")
        ]

    def _get_session(self, session_id: str) -> ManagedSession:
        managed = self._sessions.get(session_id)
        if not managed:
            raise ValueError(f"Session {session_id} not found")
        return managed
