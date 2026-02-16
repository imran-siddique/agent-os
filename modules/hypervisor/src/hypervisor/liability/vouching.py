"""
Vouching & Bonding Engine

Implements the Joint Liability vouching protocol where high-score agents
vouch for low-score agents by bonding a percentage of their reputation.

Effective Score: σ_eff = σ_L + (ω × σ_H)
where ω is the risk weight of the requested action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class VouchRecord:
    """A record of one agent vouching for another within a session."""

    vouch_id: str
    voucher_did: str
    vouchee_did: str
    session_id: str
    bonded_sigma_pct: float  # percentage of voucher's σ locked (0.0–1.0)
    bonded_amount: float  # absolute σ locked
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expiry: Optional[datetime] = None
    is_active: bool = True
    released_at: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        if self.expiry is None:
            return False
        return datetime.now(timezone.utc) > self.expiry


class VouchingEngine:
    """
    Manages the vouching/bonding protocol for Joint Liability.

    When a high-score agent (A_H) vouches for a low-score agent (A_L):
    1. A_H locks a percentage of its σ into the session context
    2. The effective score for A_L becomes: σ_eff = σ_L + (ω × σ_H)
    3. If A_L violates intent, both are penalized
    """

    # Score scale: Nexus uses 0–1000, we normalize to 0.0–1.0
    SCORE_SCALE = 1000.0
    MIN_VOUCHER_SCORE = 0.50  # min normalized σ to vouch
    DEFAULT_BOND_PCT = 0.20  # lock 20% of voucher's σ by default

    def __init__(self) -> None:
        self._vouches: dict[str, VouchRecord] = {}  # vouch_id → record

    def vouch(
        self,
        voucher_did: str,
        vouchee_did: str,
        session_id: str,
        voucher_sigma: float,
        bond_pct: Optional[float] = None,
        expiry: Optional[datetime] = None,
    ) -> VouchRecord:
        """
        Create a vouching bond.

        Args:
            voucher_did: DID of the high-score vouching agent
            vouchee_did: DID of the low-score agent being vouched for
            session_id: Session scope for this bond
            voucher_sigma: Voucher's raw reputation score (normalized 0.0–1.0)
            bond_pct: Percentage of σ to lock (default: 20%)
            expiry: Optional expiry time for the bond

        Returns:
            VouchRecord with bond details

        Raises:
            VouchingError: If voucher score too low or circular vouching detected
        """
        if voucher_did == vouchee_did:
            raise VouchingError("Cannot vouch for yourself")

        if voucher_sigma < self.MIN_VOUCHER_SCORE:
            raise VouchingError(
                f"Voucher σ ({voucher_sigma:.2f}) below minimum "
                f"({self.MIN_VOUCHER_SCORE:.2f})"
            )

        # Detect circular vouching within this session
        if self._creates_cycle(voucher_did, vouchee_did, session_id):
            raise VouchingError(
                f"Circular vouching detected: {vouchee_did} already vouches for "
                f"{voucher_did} in session {session_id}"
            )

        pct = bond_pct if bond_pct is not None else self.DEFAULT_BOND_PCT
        pct = max(0.0, min(1.0, pct))
        bonded = voucher_sigma * pct

        record = VouchRecord(
            vouch_id=f"vouch:{uuid.uuid4()}",
            voucher_did=voucher_did,
            vouchee_did=vouchee_did,
            session_id=session_id,
            bonded_sigma_pct=pct,
            bonded_amount=bonded,
            expiry=expiry,
        )
        self._vouches[record.vouch_id] = record
        return record

    def compute_sigma_eff(
        self,
        vouchee_did: str,
        session_id: str,
        vouchee_sigma: float,
        risk_weight: float,
    ) -> float:
        """
        Compute effective reputation score.

        σ_eff = σ_L + (ω × σ_H)

        where σ_H is the sum of all active vouchers' bonded amounts,
        and ω is the risk weight of the action.

        Returns:
            Effective score, capped at 1.0
        """
        voucher_contribution = 0.0
        for v in self._active_vouches_for(vouchee_did, session_id):
            voucher_contribution += v.bonded_amount

        sigma_eff = vouchee_sigma + (risk_weight * voucher_contribution)
        return min(sigma_eff, 1.0)

    def get_vouchers_for(self, agent_did: str, session_id: str) -> list[VouchRecord]:
        """Get all active vouchers for an agent in a session."""
        return list(self._active_vouches_for(agent_did, session_id))

    def get_total_exposure(self, voucher_did: str, session_id: str) -> float:
        """Total σ bonded by a voucher across all vouchees in a session."""
        return sum(
            v.bonded_amount
            for v in self._vouches.values()
            if v.voucher_did == voucher_did
            and v.session_id == session_id
            and v.is_active
            and not v.is_expired
        )

    def release_bond(self, vouch_id: str) -> None:
        """Release a vouching bond (e.g., on session termination)."""
        if vouch_id not in self._vouches:
            raise VouchingError(f"Vouch {vouch_id} not found")
        record = self._vouches[vouch_id]
        record.is_active = False
        record.released_at = datetime.now(timezone.utc)

    def release_session_bonds(self, session_id: str) -> int:
        """Release all bonds for a session. Returns count of released bonds."""
        count = 0
        for v in self._vouches.values():
            if v.session_id == session_id and v.is_active:
                v.is_active = False
                v.released_at = datetime.now(timezone.utc)
                count += 1
        return count

    def _active_vouches_for(
        self, agent_did: str, session_id: str
    ) -> list[VouchRecord]:
        """Get active, non-expired vouches for an agent in a session."""
        return [
            v
            for v in self._vouches.values()
            if v.vouchee_did == agent_did
            and v.session_id == session_id
            and v.is_active
            and not v.is_expired
        ]

    def _creates_cycle(
        self, voucher_did: str, vouchee_did: str, session_id: str
    ) -> bool:
        """Check if adding this vouch creates a circular dependency."""
        # Direct cycle: vouchee already vouches for voucher
        for v in self._vouches.values():
            if (
                v.voucher_did == vouchee_did
                and v.vouchee_did == voucher_did
                and v.session_id == session_id
                and v.is_active
                and not v.is_expired
            ):
                return True
        # Indirect cycles: walk the vouch chain from vouchee
        visited = {voucher_did}
        queue = [vouchee_did]
        while queue:
            current = queue.pop(0)
            if current in visited:
                return True
            visited.add(current)
            for v in self._vouches.values():
                if (
                    v.voucher_did == current
                    and v.session_id == session_id
                    and v.is_active
                    and not v.is_expired
                    and v.vouchee_did not in visited
                ):
                    queue.append(v.vouchee_did)
        return False


class VouchingError(Exception):
    """Raised for vouching protocol violations."""
