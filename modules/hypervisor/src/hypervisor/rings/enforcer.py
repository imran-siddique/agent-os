"""
Ring Enforcer — 4-ring execution privilege model.

Enforces hardware-inspired privilege levels based on σ_eff thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from hypervisor.models import ActionDescriptor, ExecutionRing


@dataclass
class RingCheckResult:
    """Result of a ring enforcement check."""

    allowed: bool
    required_ring: ExecutionRing
    agent_ring: ExecutionRing
    sigma_eff: float
    reason: str
    requires_consensus: bool = False
    requires_sre_witness: bool = False


class RingEnforcer:
    """
    Enforces 4-ring privilege levels for agent actions.

    Ring 0 (Root): Hypervisor config & slashing — SRE Witness required
    Ring 1 (Privileged): Non-reversible actions — σ_eff > 0.95 + consensus
    Ring 2 (Standard): Reversible actions — σ_eff > 0.60
    Ring 3 (Sandbox): Read-only / research — default for all
    """

    RING_1_THRESHOLD = 0.95
    RING_2_THRESHOLD = 0.60

    def __init__(self) -> None:
        self._sre_witness_callback: Optional[object] = None

    def check(
        self,
        agent_ring: ExecutionRing,
        action: ActionDescriptor,
        sigma_eff: float,
        has_consensus: bool = False,
        has_sre_witness: bool = False,
    ) -> RingCheckResult:
        """
        Check if an agent can perform an action given their ring level.

        Returns:
            RingCheckResult with allowed/denied status and reason
        """
        required = action.required_ring

        # Ring 0: always requires SRE witness
        if required == ExecutionRing.RING_0_ROOT:
            if not has_sre_witness:
                return RingCheckResult(
                    allowed=False,
                    required_ring=required,
                    agent_ring=agent_ring,
                    sigma_eff=sigma_eff,
                    reason="Ring 0 actions require SRE Witness co-sign",
                    requires_sre_witness=True,
                )

        # Ring 1: requires σ_eff > 0.95 AND consensus
        if required == ExecutionRing.RING_1_PRIVILEGED:
            if sigma_eff < self.RING_1_THRESHOLD:
                return RingCheckResult(
                    allowed=False,
                    required_ring=required,
                    agent_ring=agent_ring,
                    sigma_eff=sigma_eff,
                    reason=(
                        f"Ring 1 requires σ_eff > {self.RING_1_THRESHOLD}, "
                        f"got {sigma_eff:.3f}"
                    ),
                )
            if not has_consensus:
                return RingCheckResult(
                    allowed=False,
                    required_ring=required,
                    agent_ring=agent_ring,
                    sigma_eff=sigma_eff,
                    reason="Ring 1 non-reversible actions require consensus",
                    requires_consensus=True,
                )

        # Ring 2: requires σ_eff > 0.60
        if required == ExecutionRing.RING_2_STANDARD:
            if sigma_eff < self.RING_2_THRESHOLD:
                return RingCheckResult(
                    allowed=False,
                    required_ring=required,
                    agent_ring=agent_ring,
                    sigma_eff=sigma_eff,
                    reason=(
                        f"Ring 2 requires σ_eff > {self.RING_2_THRESHOLD}, "
                        f"got {sigma_eff:.3f}"
                    ),
                )

        # Agent's ring must be <= required ring (lower number = more privileged)
        if agent_ring.value > required.value:
            return RingCheckResult(
                allowed=False,
                required_ring=required,
                agent_ring=agent_ring,
                sigma_eff=sigma_eff,
                reason=(
                    f"Agent ring {agent_ring.value} insufficient for "
                    f"required ring {required.value}"
                ),
            )

        return RingCheckResult(
            allowed=True,
            required_ring=required,
            agent_ring=agent_ring,
            sigma_eff=sigma_eff,
            reason="Access granted",
        )

    def compute_ring(self, sigma_eff: float, has_consensus: bool = False) -> ExecutionRing:
        """Compute ring assignment from σ_eff."""
        return ExecutionRing.from_sigma_eff(sigma_eff, has_consensus)

    def should_demote(self, current_ring: ExecutionRing, sigma_eff: float) -> bool:
        """Check if an agent should be demoted based on σ_eff drop."""
        appropriate = self.compute_ring(sigma_eff)
        return appropriate.value > current_ring.value
