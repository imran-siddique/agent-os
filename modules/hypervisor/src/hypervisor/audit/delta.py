"""
Delta Audit Engine

Captures VFS state changes as semantic deltas with Merkle chaining.
Each delta references its parent hash, forming a tamper-evident chain.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class VFSChange:
    """A single change within a delta."""

    path: str
    operation: str  # "add", "modify", "delete", "permission"
    content_hash: Optional[str] = None
    previous_hash: Optional[str] = None
    agent_did: Optional[str] = None


@dataclass
class SemanticDelta:
    """A delta capturing VFS state changes at a single turn."""

    delta_id: str
    turn_id: int
    session_id: str
    agent_did: str
    timestamp: datetime
    changes: list[VFSChange]
    parent_hash: Optional[str]  # hash of previous delta (Merkle chain)
    delta_hash: str = ""  # computed after creation

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this delta for Merkle chaining."""
        payload = json.dumps(
            {
                "delta_id": self.delta_id,
                "turn_id": self.turn_id,
                "session_id": self.session_id,
                "agent_did": self.agent_did,
                "timestamp": self.timestamp.isoformat(),
                "changes": [
                    {
                        "path": c.path,
                        "operation": c.operation,
                        "content_hash": c.content_hash,
                        "previous_hash": c.previous_hash,
                    }
                    for c in self.changes
                ],
                "parent_hash": self.parent_hash,
            },
            sort_keys=True,
        )
        self.delta_hash = hashlib.sha256(payload.encode()).hexdigest()
        return self.delta_hash


class DeltaEngine:
    """
    Captures and chains semantic deltas from VFS state changes.

    At each agent "turn," the engine diffs the VFS state and records:
    - Added files/paths
    - Modified content
    - Deleted paths
    - Permission changes

    Deltas form a Merkle chain for tamper-evidence.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self._deltas: list[SemanticDelta] = []
        self._turn_counter = 0

    def capture(
        self,
        agent_did: str,
        changes: list[VFSChange],
        delta_id: Optional[str] = None,
    ) -> SemanticDelta:
        """
        Capture a delta for a turn.

        Args:
            agent_did: The agent that made these changes
            changes: List of VFS changes in this turn

        Returns:
            The captured and hashed SemanticDelta
        """
        self._turn_counter += 1
        parent_hash = self._deltas[-1].delta_hash if self._deltas else None

        delta = SemanticDelta(
            delta_id=delta_id or f"delta:{self._turn_counter}",
            turn_id=self._turn_counter,
            session_id=self.session_id,
            agent_did=agent_did,
            timestamp=datetime.now(timezone.utc),
            changes=changes,
            parent_hash=parent_hash,
        )
        delta.compute_hash()
        self._deltas.append(delta)
        return delta

    def compute_merkle_root(self) -> Optional[str]:
        """Compute the Merkle root of all deltas in this session."""
        if not self._deltas:
            return None

        hashes = [d.delta_hash for d in self._deltas]

        # Build Merkle tree bottom-up
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i + 1] if i + 1 < len(hashes) else left
                combined = hashlib.sha256(f"{left}{right}".encode()).hexdigest()
                next_level.append(combined)
            hashes = next_level

        return hashes[0]

    def verify_chain(self) -> bool:
        """Verify the integrity of the delta chain."""
        for i, delta in enumerate(self._deltas):
            # Recompute hash
            expected = delta.compute_hash()
            if delta.delta_hash != expected:
                return False

            # Check parent chain
            if i == 0:
                if delta.parent_hash is not None:
                    return False
            else:
                if delta.parent_hash != self._deltas[i - 1].delta_hash:
                    return False

        return True

    @property
    def deltas(self) -> list[SemanticDelta]:
        return list(self._deltas)

    @property
    def turn_count(self) -> int:
        return self._turn_counter
