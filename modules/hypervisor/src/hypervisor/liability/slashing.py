"""
Collateral Slashing Engine

When a vouchee violates Negotiated Intent:
- Vouchee: instantly blacklisted (σ → 0)
- Voucher: collateral clip — σ_new = σ_old × (1 - ω)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class SlashResult:
    """Result of a slashing operation."""

    slash_id: str
    vouchee_did: str
    vouchee_sigma_before: float
    vouchee_sigma_after: float  # always 0.0
    voucher_clips: list[VoucherClip]
    reason: str
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cascade_depth: int = 0


@dataclass
class VoucherClip:
    """A collateral clip applied to a voucher."""

    voucher_did: str
    sigma_before: float
    sigma_after: float
    risk_weight: float
    vouch_id: str


class SlashingEngine:
    """
    Enforces Joint Liability penalties.

    Violation flow:
    1. CMVK detects behavioral mismatch
    2. Vouchee is blacklisted (σ → 0)
    3. All vouchers suffer collateral clip: σ_new = σ_old × (1 - ω)
    4. Cascading slashing capped at MAX_CASCADE_DEPTH
    """

    MAX_CASCADE_DEPTH = 2
    SIGMA_FLOOR = 0.05  # minimum σ after slashing (prevents total wipeout)

    def __init__(self, vouching_engine: object) -> None:
        from hypervisor.liability.vouching import VouchingEngine

        self._vouching: VouchingEngine = vouching_engine  # type: ignore[assignment]
        self._slash_history: list[SlashResult] = []

    def slash(
        self,
        vouchee_did: str,
        session_id: str,
        vouchee_sigma: float,
        risk_weight: float,
        reason: str,
        agent_scores: dict[str, float],
        cascade_depth: int = 0,
    ) -> SlashResult:
        """
        Execute a slashing event.

        Args:
            vouchee_did: DID of the violating agent
            session_id: Session where violation occurred
            vouchee_sigma: Vouchee's current σ
            risk_weight: ω of the violated action
            reason: Human-readable violation reason
            agent_scores: Mutable dict of agent_did → σ (updated in-place)
            cascade_depth: Current depth of cascading slashes

        Returns:
            SlashResult with all penalties applied
        """
        # Blacklist vouchee
        agent_scores[vouchee_did] = 0.0

        # Clip all vouchers
        clips: list[VoucherClip] = []
        vouchers = self._vouching.get_vouchers_for(vouchee_did, session_id)

        for vouch in vouchers:
            voucher_sigma = agent_scores.get(vouch.voucher_did, 0.0)
            new_sigma = voucher_sigma * (1.0 - risk_weight)
            new_sigma = max(new_sigma, self.SIGMA_FLOOR)
            agent_scores[vouch.voucher_did] = new_sigma

            clips.append(VoucherClip(
                voucher_did=vouch.voucher_did,
                sigma_before=voucher_sigma,
                sigma_after=new_sigma,
                risk_weight=risk_weight,
                vouch_id=vouch.vouch_id,
            ))

            # Release the bond
            self._vouching.release_bond(vouch.vouch_id)

        result = SlashResult(
            slash_id=f"slash:{uuid.uuid4()}",
            vouchee_did=vouchee_did,
            vouchee_sigma_before=vouchee_sigma,
            vouchee_sigma_after=0.0,
            voucher_clips=clips,
            reason=reason,
            session_id=session_id,
            cascade_depth=cascade_depth,
        )
        self._slash_history.append(result)

        # Cascade: if a clipped voucher is also a vouchee, cascade the slash
        if cascade_depth < self.MAX_CASCADE_DEPTH:
            for clip in clips:
                if clip.sigma_after < self.SIGMA_FLOOR + 0.01:
                    # Voucher was effectively wiped — cascade
                    cascade_vouchers = self._vouching.get_vouchers_for(
                        clip.voucher_did, session_id
                    )
                    if cascade_vouchers:
                        self.slash(
                            vouchee_did=clip.voucher_did,
                            session_id=session_id,
                            vouchee_sigma=clip.sigma_after,
                            risk_weight=risk_weight,
                            reason=f"Cascade from {vouchee_did}: {reason}",
                            agent_scores=agent_scores,
                            cascade_depth=cascade_depth + 1,
                        )

        return result

    @property
    def history(self) -> list[SlashResult]:
        return list(self._slash_history)
