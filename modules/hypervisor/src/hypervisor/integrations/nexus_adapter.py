"""
Nexus Integration — Real Trust Scoring for Ring Assignment

Bridges the Nexus ReputationEngine to the Hypervisor, replacing
stub sigma_raw values with computed trust scores from agent history.

Nexus score range: 0–1000 → normalized to 0.0–1.0 for Hypervisor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, Protocol


# ---------------------------------------------------------------------------
# Protocol: Nexus API contract (avoids hard dependency)
# ---------------------------------------------------------------------------


class NexusTrustScorer(Protocol):
    """Protocol matching Nexus ReputationEngine interface."""

    def calculate_trust_score(
        self,
        verification_level: str,
        history: Any,
        capabilities: Optional[dict] = None,
        privacy: Optional[dict] = None,
    ) -> Any: ...

    def slash_reputation(
        self,
        agent_did: str,
        reason: str,
        severity: str,
        evidence_hash: Optional[str] = None,
        trace_id: Optional[str] = None,
        broadcast: bool = True,
    ) -> Any: ...

    def record_task_outcome(
        self,
        agent_did: str,
        outcome: str,
    ) -> Any: ...


class NexusAgentVerifier(Protocol):
    """Protocol matching Nexus AgentRegistry.verify_peer interface."""

    async def verify_peer(
        self,
        peer_did: str,
        min_score: int = 700,
        required_capabilities: Optional[list[str]] = None,
    ) -> Any: ...


# ---------------------------------------------------------------------------
# Adapter: Nexus → Hypervisor
# ---------------------------------------------------------------------------


NEXUS_SCORE_SCALE = 1000.0

# Mapping from Nexus TrustTier to Hypervisor ring thresholds
TIER_TO_SIGMA = {
    "verified_partner": 0.95,
    "trusted": 0.80,
    "standard": 0.60,
    "probationary": 0.35,
    "untrusted": 0.10,
}


@dataclass
class NexusScoreResult:
    """Result of a Nexus trust score lookup."""

    agent_did: str
    raw_nexus_score: int
    normalized_sigma: float
    tier: str
    successful_tasks: int = 0
    failed_tasks: int = 0
    times_slashed: int = 0
    resolved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class NexusAdapter:
    """
    Integrates Nexus trust scoring into Hypervisor ring assignment.

    Usage:
        nexus = NexusAdapter(reputation_engine)
        sigma = nexus.resolve_sigma("did:mesh:agent-1")
        ring = await hv.join_session(session_id, "did:mesh:agent-1", sigma_raw=sigma)
    """

    def __init__(
        self,
        scorer: Optional[NexusTrustScorer] = None,
        verifier: Optional[NexusAgentVerifier] = None,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self._scorer = scorer
        self._verifier = verifier
        self._cache: dict[str, NexusScoreResult] = {}
        self._cache_ttl = cache_ttl_seconds

    def resolve_sigma(
        self,
        agent_did: str,
        verification_level: str = "standard",
        history: Optional[Any] = None,
        capabilities: Optional[dict] = None,
    ) -> float:
        """
        Resolve an agent's effective sigma from Nexus trust scoring.

        Returns:
            Normalized sigma (0.0–1.0) for Hypervisor ring assignment.
        """
        # Check cache
        cached = self._cache.get(agent_did)
        if cached and self._is_cache_valid(cached):
            return cached.normalized_sigma

        if self._scorer is None:
            return 0.50  # default if no scorer configured

        score = self._scorer.calculate_trust_score(
            verification_level=verification_level,
            history=history,
            capabilities=capabilities,
        )

        # Nexus returns TrustScore with total_score (0–1000)
        raw_score = getattr(score, "total_score", 500)
        tier = self._score_to_tier(raw_score)
        normalized = raw_score / NEXUS_SCORE_SCALE

        result = NexusScoreResult(
            agent_did=agent_did,
            raw_nexus_score=raw_score,
            normalized_sigma=normalized,
            tier=tier,
            successful_tasks=getattr(score, "successful_tasks", 0),
            failed_tasks=getattr(score, "failed_tasks", 0),
        )
        self._cache[agent_did] = result
        return normalized

    def report_task_outcome(
        self,
        agent_did: str,
        outcome: str,
    ) -> None:
        """Report a task outcome back to Nexus for reputation tracking."""
        if self._scorer:
            self._scorer.record_task_outcome(agent_did, outcome)
            # Invalidate cache
            self._cache.pop(agent_did, None)

    def report_slash(
        self,
        agent_did: str,
        reason: str,
        severity: str = "medium",
        evidence_hash: Optional[str] = None,
    ) -> None:
        """Report a slashing event to Nexus."""
        if self._scorer:
            self._scorer.slash_reputation(
                agent_did=agent_did,
                reason=reason,
                severity=severity,
                evidence_hash=evidence_hash,
            )
            self._cache.pop(agent_did, None)

    async def verify_agent(
        self,
        agent_did: str,
        min_score: int = 500,
    ) -> bool:
        """Verify an agent meets minimum requirements via Nexus registry."""
        if self._verifier is None:
            return True  # permissive if no verifier
        result = await self._verifier.verify_peer(agent_did, min_score=min_score)
        return getattr(result, "is_verified", False)

    def get_cached_result(self, agent_did: str) -> Optional[NexusScoreResult]:
        """Get the last cached score result for an agent."""
        return self._cache.get(agent_did)

    def invalidate_cache(self, agent_did: Optional[str] = None) -> None:
        """Invalidate cache for an agent or all agents."""
        if agent_did:
            self._cache.pop(agent_did, None)
        else:
            self._cache.clear()

    def _score_to_tier(self, score: int) -> str:
        if score >= 900:
            return "verified_partner"
        elif score >= 700:
            return "trusted"
        elif score >= 500:
            return "standard"
        elif score >= 300:
            return "probationary"
        else:
            return "untrusted"

    def _is_cache_valid(self, result: NexusScoreResult) -> bool:
        age = (datetime.now(timezone.utc) - result.resolved_at).total_seconds()
        return age < self._cache_ttl
