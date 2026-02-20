"""
IATP Integration — Capability Manifests for Session Handshakes

Bridges IATP (Inter-Agent Trust Protocol) to the Hypervisor,
enriching session handshakes with:
- Capability manifest → reversibility classification
- Trust level → initial ring assignment hint
- Privacy contract → data access policies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Protocol

from hypervisor.models import (
    ActionDescriptor,
    ExecutionRing,
    ReversibilityLevel,
)


# ---------------------------------------------------------------------------
# Protocol: IATP API contract
# ---------------------------------------------------------------------------


class IATPManifest(Protocol):
    """Protocol matching IATP CapabilityManifest interface."""

    agent_id: str
    trust_level: Any  # TrustLevel enum
    capabilities: Any  # AgentCapabilities
    scopes: list[str]

    def calculate_trust_score(self) -> int: ...


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class IATPTrustLevel(str, Enum):
    """Mirror of IATP TrustLevel for standalone use."""

    VERIFIED_PARTNER = "verified_partner"
    TRUSTED = "trusted"
    STANDARD = "standard"
    UNKNOWN = "unknown"
    UNTRUSTED = "untrusted"


# Mapping IATP TrustLevel → Hypervisor ring hint
TRUST_LEVEL_RING_HINTS = {
    IATPTrustLevel.VERIFIED_PARTNER: ExecutionRing.RING_1_PRIVILEGED,
    IATPTrustLevel.TRUSTED: ExecutionRing.RING_2_STANDARD,
    IATPTrustLevel.STANDARD: ExecutionRing.RING_2_STANDARD,
    IATPTrustLevel.UNKNOWN: ExecutionRing.RING_3_SANDBOX,
    IATPTrustLevel.UNTRUSTED: ExecutionRing.RING_3_SANDBOX,
}

# IATP reversibility levels → Hypervisor reversibility levels
REVERSIBILITY_MAP = {
    "full": ReversibilityLevel.FULL,
    "partial": ReversibilityLevel.PARTIAL,
    "none": ReversibilityLevel.NONE,
}


@dataclass
class ManifestAnalysis:
    """Result of analyzing an IATP capability manifest."""

    agent_did: str
    trust_level: IATPTrustLevel
    ring_hint: ExecutionRing
    iatp_trust_score: int  # 0–10 scale from IATP
    sigma_hint: float  # normalized to 0.0–1.0
    actions: list[ActionDescriptor]
    scopes: list[str]
    has_reversible_actions: bool
    has_non_reversible_actions: bool
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Adapter: IATP → Hypervisor
# ---------------------------------------------------------------------------


class IATPAdapter:
    """
    Integrates IATP capability manifests into Hypervisor session handshakes.

    Usage:
        iatp = IATPAdapter()
        analysis = iatp.analyze_manifest(manifest)

        # Use analysis to enrich session join
        ring = await hv.join_session(
            session_id,
            agent_did=analysis.agent_did,
            actions=analysis.actions,
            sigma_raw=analysis.sigma_hint,
        )
    """

    def __init__(self) -> None:
        self._manifest_cache: dict[str, ManifestAnalysis] = {}

    def analyze_manifest(self, manifest: IATPManifest) -> ManifestAnalysis:
        """
        Analyze an IATP manifest and extract Hypervisor-compatible data.

        Converts:
        - IATP trust_level → ring hint
        - IATP capabilities → ActionDescriptor list
        - IATP trust_score (0–10) → normalized sigma (0.0–1.0)
        """
        agent_did = manifest.agent_id

        # Trust level
        trust_str = str(getattr(manifest.trust_level, "value", manifest.trust_level))
        try:
            trust_level = IATPTrustLevel(trust_str)
        except ValueError:
            trust_level = IATPTrustLevel.UNKNOWN

        # Ring hint from trust level
        ring_hint = TRUST_LEVEL_RING_HINTS.get(trust_level, ExecutionRing.RING_3_SANDBOX)

        # IATP trust score (0–10) → sigma (0.0–1.0)
        iatp_score = manifest.calculate_trust_score()
        sigma_hint = min(max(iatp_score / 10.0, 0.0), 1.0)

        # Extract actions from capabilities
        actions = self._extract_actions(manifest)
        scopes = list(manifest.scopes) if manifest.scopes else []

        has_reversible = any(
            a.reversibility != ReversibilityLevel.NONE for a in actions
        )
        has_non_reversible = any(
            a.reversibility == ReversibilityLevel.NONE and not a.is_read_only
            for a in actions
        )

        analysis = ManifestAnalysis(
            agent_did=agent_did,
            trust_level=trust_level,
            ring_hint=ring_hint,
            iatp_trust_score=iatp_score,
            sigma_hint=sigma_hint,
            actions=actions,
            scopes=scopes,
            has_reversible_actions=has_reversible,
            has_non_reversible_actions=has_non_reversible,
        )
        self._manifest_cache[agent_did] = analysis
        return analysis

    def analyze_manifest_dict(self, manifest_dict: dict) -> ManifestAnalysis:
        """
        Analyze a manifest provided as a dictionary (for testing or
        when IATP module is not installed).
        """
        agent_did = manifest_dict.get("agent_id", "unknown")
        trust_str = manifest_dict.get("trust_level", "unknown")
        try:
            trust_level = IATPTrustLevel(trust_str)
        except ValueError:
            trust_level = IATPTrustLevel.UNKNOWN

        ring_hint = TRUST_LEVEL_RING_HINTS.get(trust_level, ExecutionRing.RING_3_SANDBOX)
        iatp_score = manifest_dict.get("trust_score", 5)
        sigma_hint = min(max(iatp_score / 10.0, 0.0), 1.0)

        # Parse actions
        actions = []
        for cap in manifest_dict.get("actions", []):
            rev_str = cap.get("reversibility", "none")
            actions.append(ActionDescriptor(
                action_id=cap.get("action_id", "unknown"),
                name=cap.get("name", ""),
                execute_api=cap.get("execute_api", ""),
                undo_api=cap.get("undo_api"),
                reversibility=REVERSIBILITY_MAP.get(rev_str, ReversibilityLevel.NONE),
                is_read_only=cap.get("is_read_only", False),
                is_admin=cap.get("is_admin", False),
            ))

        scopes = manifest_dict.get("scopes", [])

        has_reversible = any(
            a.reversibility != ReversibilityLevel.NONE for a in actions
        )
        has_non_reversible = any(
            a.reversibility == ReversibilityLevel.NONE and not a.is_read_only
            for a in actions
        )

        analysis = ManifestAnalysis(
            agent_did=agent_did,
            trust_level=trust_level,
            ring_hint=ring_hint,
            iatp_trust_score=iatp_score,
            sigma_hint=sigma_hint,
            actions=actions,
            scopes=scopes,
            has_reversible_actions=has_reversible,
            has_non_reversible_actions=has_non_reversible,
        )
        self._manifest_cache[agent_did] = analysis
        return analysis

    def get_cached_analysis(self, agent_did: str) -> Optional[ManifestAnalysis]:
        return self._manifest_cache.get(agent_did)

    def _extract_actions(self, manifest: IATPManifest) -> list[ActionDescriptor]:
        """Extract ActionDescriptors from IATP capabilities."""
        actions: list[ActionDescriptor] = []
        caps = manifest.capabilities
        if caps is None:
            return actions

        # IATP capabilities have reversibility, idempotency, etc.
        rev_str = str(getattr(caps, "reversibility", "none"))
        if hasattr(rev_str, "value"):
            rev_str = rev_str.value
        rev_level = REVERSIBILITY_MAP.get(rev_str, ReversibilityLevel.NONE)

        # Create a single descriptor from the manifest's capabilities
        undo_window = getattr(caps, "undo_window", None)
        undo_seconds = 0
        if undo_window:
            try:
                undo_seconds = int(undo_window.rstrip("s").rstrip("m").rstrip("h"))
            except (ValueError, AttributeError):
                pass

        actions.append(ActionDescriptor(
            action_id=f"{manifest.agent_id}:default",
            name=f"Default action for {manifest.agent_id}",
            execute_api=f"/api/{manifest.agent_id}/execute",
            undo_api=f"/api/{manifest.agent_id}/undo" if rev_level != ReversibilityLevel.NONE else None,
            reversibility=rev_level,
            undo_window_seconds=undo_seconds,
        ))

        return actions
