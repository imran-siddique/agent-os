"""
CMVK Integration — Behavioral Verification and Drift-Triggered Slashing

Bridges the CMVK (Cross-Model Verification Kernel) to the Hypervisor.
When CMVK detects behavioral drift above a threshold, the adapter
triggers slashing via the Hypervisor's liability engine.

Flow:
  Agent output → CMVK verify_embeddings() → drift_score
  If drift_score > threshold → slash agent + notify Nexus
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional, Protocol


# ---------------------------------------------------------------------------
# Protocol: CMVK API contract
# ---------------------------------------------------------------------------


class CMVKVerifier(Protocol):
    """Protocol matching CMVK verify_embeddings interface."""

    def verify_embeddings(
        self,
        embedding_a: Any,
        embedding_b: Any,
        metric: str = "cosine",
        weights: Any = None,
        threshold_profile: Optional[str] = None,
        explain: bool = False,
    ) -> Any: ...


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class DriftSeverity(str, Enum):
    """Severity levels for behavioral drift."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DriftCheckResult:
    """Result of a CMVK behavioral verification check."""

    agent_did: str
    session_id: str
    drift_score: float
    severity: DriftSeverity
    passed: bool
    explanation: Optional[str] = None
    action_id: Optional[str] = None
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def should_slash(self) -> bool:
        return self.severity in (DriftSeverity.HIGH, DriftSeverity.CRITICAL)

    @property
    def should_demote(self) -> bool:
        return self.severity == DriftSeverity.MEDIUM


@dataclass
class DriftThresholds:
    """Configurable thresholds for drift severity classification."""

    low: float = 0.15
    medium: float = 0.30
    high: float = 0.50
    critical: float = 0.75


# ---------------------------------------------------------------------------
# Adapter: CMVK → Hypervisor
# ---------------------------------------------------------------------------


class CMVKAdapter:
    """
    Integrates CMVK behavioral verification into Hypervisor sessions.

    Usage:
        cmvk = CMVKAdapter(verifier=cmvk_engine)

        # After each agent action, verify behavioral alignment
        result = cmvk.check_behavioral_drift(
            agent_did="did:mesh:agent-1",
            session_id="session-123",
            claimed_embedding=claim_vec,
            observed_embedding=output_vec,
        )

        if result.should_slash:
            # Trigger slashing via hypervisor
            hv.slashing.slash(...)
    """

    def __init__(
        self,
        verifier: Optional[CMVKVerifier] = None,
        thresholds: Optional[DriftThresholds] = None,
        on_drift_detected: Optional[Callable[[DriftCheckResult], None]] = None,
    ) -> None:
        self._verifier = verifier
        self.thresholds = thresholds or DriftThresholds()
        self._on_drift_detected = on_drift_detected
        self._check_history: list[DriftCheckResult] = []

    def check_behavioral_drift(
        self,
        agent_did: str,
        session_id: str,
        claimed_embedding: Any,
        observed_embedding: Any,
        action_id: Optional[str] = None,
        metric: str = "cosine",
        threshold_profile: Optional[str] = None,
    ) -> DriftCheckResult:
        """
        Verify an agent's output matches its claimed behavior.

        Args:
            agent_did: Agent whose behavior to verify
            session_id: Session context
            claimed_embedding: Expected behavior vector (from manifest)
            observed_embedding: Actual output vector
            action_id: Optional action identifier
            metric: Distance metric for comparison
            threshold_profile: CMVK threshold profile name

        Returns:
            DriftCheckResult with severity classification
        """
        if self._verifier is None:
            # No verifier — assume no drift
            result = DriftCheckResult(
                agent_did=agent_did,
                session_id=session_id,
                drift_score=0.0,
                severity=DriftSeverity.NONE,
                passed=True,
                action_id=action_id,
            )
            self._check_history.append(result)
            return result

        score = self._verifier.verify_embeddings(
            embedding_a=claimed_embedding,
            embedding_b=observed_embedding,
            metric=metric,
            threshold_profile=threshold_profile,
            explain=True,
        )

        drift_score = getattr(score, "drift_score", 0.0)
        explanation = None
        if hasattr(score, "explanation") and score.explanation:
            explanation = str(score.explanation)

        severity = self._classify_severity(drift_score)
        passed = severity in (DriftSeverity.NONE, DriftSeverity.LOW)

        result = DriftCheckResult(
            agent_did=agent_did,
            session_id=session_id,
            drift_score=drift_score,
            severity=severity,
            passed=passed,
            explanation=explanation,
            action_id=action_id,
        )
        self._check_history.append(result)

        if not passed and self._on_drift_detected:
            self._on_drift_detected(result)

        return result

    def get_agent_drift_history(
        self,
        agent_did: str,
        session_id: Optional[str] = None,
    ) -> list[DriftCheckResult]:
        """Get drift check history for an agent."""
        return [
            r for r in self._check_history
            if r.agent_did == agent_did
            and (session_id is None or r.session_id == session_id)
        ]

    def get_drift_rate(
        self,
        agent_did: str,
        session_id: Optional[str] = None,
    ) -> float:
        """
        Calculate the drift failure rate for an agent.

        Returns:
            Ratio of failed checks to total checks (0.0–1.0).
        """
        history = self.get_agent_drift_history(agent_did, session_id)
        if not history:
            return 0.0
        failed = sum(1 for r in history if not r.passed)
        return failed / len(history)

    def get_mean_drift_score(
        self,
        agent_did: str,
        session_id: Optional[str] = None,
    ) -> float:
        """Calculate mean drift score for an agent."""
        history = self.get_agent_drift_history(agent_did, session_id)
        if not history:
            return 0.0
        return sum(r.drift_score for r in history) / len(history)

    @property
    def total_checks(self) -> int:
        return len(self._check_history)

    @property
    def total_violations(self) -> int:
        return sum(1 for r in self._check_history if not r.passed)

    def _classify_severity(self, drift_score: float) -> DriftSeverity:
        if drift_score >= self.thresholds.critical:
            return DriftSeverity.CRITICAL
        elif drift_score >= self.thresholds.high:
            return DriftSeverity.HIGH
        elif drift_score >= self.thresholds.medium:
            return DriftSeverity.MEDIUM
        elif drift_score >= self.thresholds.low:
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NONE
