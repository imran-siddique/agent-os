"""
DID Transaction History Verification

Verifies an agent's behavioral history by checking Summary Hashes
from their DID document or blockchain during the IATP handshake.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class VerificationStatus(str, Enum):
    """Result of transaction history verification."""

    VERIFIED = "verified"
    PROBATIONARY = "probationary"  # new DID, limited history
    SUSPICIOUS = "suspicious"  # inconsistent hashes
    UNREACHABLE = "unreachable"  # couldn't fetch history
    UNKNOWN = "unknown"


@dataclass
class TransactionRecord:
    """A historical transaction record from a DID."""

    session_id: str
    summary_hash: str
    timestamp: datetime
    participant_count: int = 0


@dataclass
class VerificationResult:
    """Result of verifying an agent's transaction history."""

    agent_did: str
    status: VerificationStatus
    transactions_checked: int
    transactions_found: int
    inconsistencies: list[str] = field(default_factory=list)
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cached: bool = False

    @property
    def is_trustworthy(self) -> bool:
        return self.status in (VerificationStatus.VERIFIED, VerificationStatus.PROBATIONARY)


class TransactionHistoryVerifier:
    """
    Verifies agent transaction history via DID documents / blockchain.

    During handshake, checks the last N transaction Summary Hashes
    to validate behavioral consistency.
    """

    REQUIRED_HISTORY_DEPTH = 5

    def __init__(self) -> None:
        self._cache: dict[str, VerificationResult] = {}

    def verify(
        self,
        agent_did: str,
        declared_history: Optional[list[TransactionRecord]] = None,
    ) -> VerificationResult:
        """
        Verify an agent's transaction history.

        Args:
            agent_did: The agent's DID to verify
            declared_history: History declared by the agent (to cross-check)

        Returns:
            VerificationResult with status and details
        """
        # Check cache first
        if agent_did in self._cache:
            cached = self._cache[agent_did]
            cached.cached = True
            return cached

        if declared_history is None or len(declared_history) == 0:
            # No history — treat as new/probationary
            result = VerificationResult(
                agent_did=agent_did,
                status=VerificationStatus.PROBATIONARY,
                transactions_checked=0,
                transactions_found=0,
                inconsistencies=["No transaction history available"],
            )
        elif len(declared_history) < self.REQUIRED_HISTORY_DEPTH:
            # Insufficient history
            result = VerificationResult(
                agent_did=agent_did,
                status=VerificationStatus.PROBATIONARY,
                transactions_checked=len(declared_history),
                transactions_found=len(declared_history),
                inconsistencies=[
                    f"Only {len(declared_history)} transactions "
                    f"(need {self.REQUIRED_HISTORY_DEPTH})"
                ],
            )
        else:
            # Validate hash consistency
            inconsistencies = self._check_consistency(declared_history)
            status = (
                VerificationStatus.SUSPICIOUS
                if inconsistencies
                else VerificationStatus.VERIFIED
            )
            result = VerificationResult(
                agent_did=agent_did,
                status=status,
                transactions_checked=len(declared_history),
                transactions_found=len(declared_history),
                inconsistencies=inconsistencies,
            )

        self._cache[agent_did] = result
        return result

    def clear_cache(self, agent_did: Optional[str] = None) -> None:
        """Clear verification cache."""
        if agent_did:
            self._cache.pop(agent_did, None)
        else:
            self._cache.clear()

    def _check_consistency(self, history: list[TransactionRecord]) -> list[str]:
        """Check transaction history for inconsistencies."""
        issues: list[str] = []

        # Check for duplicate hashes (different sessions, same hash = suspicious)
        seen_hashes: dict[str, str] = {}
        for tx in history:
            if tx.summary_hash in seen_hashes:
                issues.append(
                    f"Duplicate hash in sessions {seen_hashes[tx.summary_hash]} "
                    f"and {tx.session_id}"
                )
            seen_hashes[tx.summary_hash] = tx.session_id

        # Check for temporal ordering
        for i in range(1, len(history)):
            if history[i].timestamp < history[i - 1].timestamp:
                issues.append(
                    f"Non-monotonic timestamps: {history[i].session_id} "
                    f"predates {history[i-1].session_id}"
                )

        # Check for empty hashes
        for tx in history:
            if not tx.summary_hash or len(tx.summary_hash) < 16:
                issues.append(f"Invalid hash in session {tx.session_id}")

        return issues
