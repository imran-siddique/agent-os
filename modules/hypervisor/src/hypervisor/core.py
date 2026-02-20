"""
Hypervisor — Top-level orchestrator for multi-agent Shared Sessions.

Composes all submodules (Session, Liability, Rings, Reversibility,
Saga, Audit, Verification) into a unified governance runtime.

Optionally integrates with Nexus (trust scoring), CMVK (behavioral
verification), and IATP (capability manifests) when adapters are provided.
"""

from __future__ import annotations

import logging
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

logger = logging.getLogger(__name__)


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

    Usage (basic — sigma_raw passed directly):
        hv = Hypervisor()
        session = await hv.create_session(config, creator_did="did:mesh:admin")
        await hv.join_session(session.sso.session_id, "did:mesh:agent-1", sigma_raw=0.85)

    Usage (enriched — adapters resolve sigma and parse manifests):
        from hypervisor.integrations.nexus_adapter import NexusAdapter
        from hypervisor.integrations.cmvk_adapter import CMVKAdapter
        from hypervisor.integrations.iatp_adapter import IATPAdapter

        hv = Hypervisor(
            nexus=NexusAdapter(scorer=reputation_engine),
            cmvk=CMVKAdapter(verifier=cmvk_engine),
            iatp=IATPAdapter(),
        )
        # join_session will auto-resolve sigma from Nexus when sigma_raw is not provided
    """

    def __init__(
        self,
        retention_policy: Optional[RetentionPolicy] = None,
        max_exposure: Optional[float] = None,
        nexus: Optional[Any] = None,
        cmvk: Optional[Any] = None,
        iatp: Optional[Any] = None,
    ) -> None:
        # Shared engines
        self.vouching = VouchingEngine(max_exposure=max_exposure)
        self.slashing = SlashingEngine(self.vouching)
        self.ring_enforcer = RingEnforcer()
        self.classifier = ActionClassifier()
        self.verifier = TransactionHistoryVerifier()
        self.commitment = CommitmentEngine()
        self.gc = EphemeralGC(retention_policy)

        # Integration adapters (optional)
        self.nexus = nexus
        self.cmvk = cmvk
        self.iatp = iatp

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
        manifest: Optional[Any] = None,
        agent_history: Optional[Any] = None,
    ) -> ExecutionRing:
        """
        Join an agent to a session via extended IATP handshake.

        Steps:
        1. Parse IATP manifest (if adapter + manifest provided)
        2. Register actions in Reversibility Registry
        3. Force Strong mode if non-reversible actions exist
        4. Verify DID transaction history
        5. Resolve σ_eff (Nexus adapter or raw fallback) and assign ring
        """
        managed = self._get_session(session_id)

        # Step 1: IATP manifest enrichment
        if self.iatp and manifest:
            if isinstance(manifest, dict):
                analysis = self.iatp.analyze_manifest_dict(manifest)
            else:
                analysis = self.iatp.analyze_manifest(manifest)
            # Use manifest actions if none explicitly provided
            if not actions:
                actions = analysis.actions
            # Use IATP sigma hint as fallback
            if sigma_raw == 0.0:
                sigma_raw = analysis.sigma_hint
            logger.debug("IATP manifest parsed for %s: ring_hint=%s", agent_did, analysis.ring_hint)

        # Step 2: Register actions
        if actions:
            managed.reversibility.register_from_manifest(actions)

        # Step 3: Mode negotiation
        if managed.reversibility.has_non_reversible_actions():
            managed.sso.force_consistency_mode(ConsistencyMode.STRONG)

        # Step 4: Verify history
        verification = self.verifier.verify(agent_did)

        # Step 5: Resolve effective score
        sigma_eff = sigma_raw

        # Nexus enrichment: if adapter is available and no explicit sigma given
        if self.nexus and sigma_raw == 0.0:
            sigma_eff = self.nexus.resolve_sigma(
                agent_did,
                history=agent_history,
            )
            logger.debug("Nexus resolved sigma=%.3f for %s", sigma_eff, agent_did)
        elif self.nexus and agent_history:
            # Even with explicit sigma, Nexus can verify/enrich
            nexus_sigma = self.nexus.resolve_sigma(
                agent_did,
                history=agent_history,
            )
            # Use the lower of provided vs Nexus (conservative)
            sigma_eff = min(sigma_raw, nexus_sigma)

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

        # GC — actually purge VFS data
        self.gc.collect(
            session_id=session_id,
            vfs=managed.sso.vfs if hasattr(managed.sso, "vfs") else None,
            delta_engine=managed.delta_engine,
            delta_count=managed.delta_engine.turn_count,
        )

        # Archive
        managed.sso.archive()

        return merkle_root

    def get_session(self, session_id: str) -> Optional[ManagedSession]:
        return self._sessions.get(session_id)

    async def verify_behavior(
        self,
        session_id: str,
        agent_did: str,
        claimed_embedding: Any,
        observed_embedding: Any,
        action_id: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Verify agent behavior via CMVK adapter.

        If drift exceeds threshold, automatically slashes the agent and
        reports to Nexus (if adapter is available).

        Returns:
            DriftCheckResult if CMVK adapter is configured, else None.
        """
        if not self.cmvk:
            return None

        result = self.cmvk.check_behavioral_drift(
            agent_did=agent_did,
            session_id=session_id,
            claimed_embedding=claimed_embedding,
            observed_embedding=observed_embedding,
            action_id=action_id,
        )

        if result.should_slash:
            managed = self._get_session(session_id)
            participant = managed.sso.get_participant(agent_did)
            agent_scores = {
                p.agent_did: p.sigma_eff
                for p in managed.sso.participants
            }
            self.slashing.slash(
                vouchee_did=agent_did,
                session_id=session_id,
                vouchee_sigma=participant.sigma_eff,
                risk_weight=0.95,
                reason=f"CMVK drift: {result.drift_score:.3f} ({result.severity.value})",
                agent_scores=agent_scores,
            )
            # Propagate to Nexus
            if self.nexus:
                severity = "critical" if result.drift_score >= 0.75 else "high"
                self.nexus.report_slash(
                    agent_did=agent_did,
                    reason=f"Behavioral drift: {result.drift_score:.3f}",
                    severity=severity,
                )
            logger.warning("Agent %s slashed: drift=%.3f", agent_did, result.drift_score)

        return result

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
