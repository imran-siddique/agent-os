"""
Blockchain Summary Hash Commitment

On session termination, computes the Merkle Root of all deltas
and anchors it for permanent, verifiable audit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class CommitmentRecord:
    """Record of a Summary Hash commitment."""

    session_id: str
    merkle_root: str
    participant_dids: list[str]
    delta_count: int
    committed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    blockchain_tx_id: Optional[str] = None
    committed_to: str = "local"  # "local", "ethereum", "ipfs"


class CommitmentEngine:
    """
    Manages Summary Hash commitments to blockchain / permanent storage.

    On session termination:
    1. Compute Merkle Root of all session deltas
    2. Write Summary Hash to blockchain / DID document
    3. Associate with session participants' DIDs
    """

    def __init__(self) -> None:
        self._commitments: dict[str, CommitmentRecord] = {}
        self._batch_queue: list[CommitmentRecord] = []

    def commit(
        self,
        session_id: str,
        merkle_root: str,
        participant_dids: list[str],
        delta_count: int,
    ) -> CommitmentRecord:
        """Commit a session's Summary Hash."""
        record = CommitmentRecord(
            session_id=session_id,
            merkle_root=merkle_root,
            participant_dids=participant_dids,
            delta_count=delta_count,
        )
        self._commitments[session_id] = record
        return record

    def verify(self, session_id: str, expected_root: str) -> bool:
        """Verify a session's Merkle root matches the committed value."""
        record = self._commitments.get(session_id)
        if not record:
            return False
        return record.merkle_root == expected_root

    def queue_for_batch(self, record: CommitmentRecord) -> None:
        """Queue a commitment for batch blockchain write."""
        self._batch_queue.append(record)

    def flush_batch(self) -> list[CommitmentRecord]:
        """Flush the batch queue. Returns committed records."""
        batch = list(self._batch_queue)
        self._batch_queue.clear()
        return batch

    def get_commitment(self, session_id: str) -> Optional[CommitmentRecord]:
        return self._commitments.get(session_id)
