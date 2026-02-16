"""
Ephemeral Session Data Garbage Collection

After session archival, garbage-collects ephemeral data while
retaining forensic artifacts for the SRE "Black Box."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional


@dataclass
class GCResult:
    """Result of a garbage collection run."""

    session_id: str
    retained_deltas: int
    retained_hash: bool
    purged_vfs_files: int
    purged_caches: int
    storage_before_bytes: int
    storage_after_bytes: int
    gc_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def storage_saved_bytes(self) -> int:
        return self.storage_before_bytes - self.storage_after_bytes

    @property
    def savings_pct(self) -> float:
        if self.storage_before_bytes == 0:
            return 0.0
        return (self.storage_saved_bytes / self.storage_before_bytes) * 100


@dataclass
class RetentionPolicy:
    """Configuration for what to retain after GC."""

    delta_retention_days: int = 90
    hash_retention: str = "permanent"  # "permanent" or days
    liability_snapshot: bool = True


class EphemeralGC:
    """
    Garbage collector for session ephemeral data.

    Retention rules:
    - Retain: Summary Hash (permanent), Deltas (configurable), LiabilityMatrix snapshot
    - Purge: VFS state, in-memory caches, temporary agent contexts
    - Compact: Delta chains into optimized storage
    """

    def __init__(self, policy: Optional[RetentionPolicy] = None) -> None:
        self.policy = policy or RetentionPolicy()
        self._gc_history: list[GCResult] = []

    def collect(
        self,
        session_id: str,
        vfs_file_count: int = 0,
        cache_count: int = 0,
        delta_count: int = 0,
        estimated_vfs_bytes: int = 0,
        estimated_cache_bytes: int = 0,
        estimated_delta_bytes: int = 0,
    ) -> GCResult:
        """
        Run garbage collection for a terminated session.

        In production, this would actually delete VFS state and caches.
        Here we track what would be purged for reporting.
        """
        total_before = estimated_vfs_bytes + estimated_cache_bytes + estimated_delta_bytes
        total_after = estimated_delta_bytes  # only deltas retained

        result = GCResult(
            session_id=session_id,
            retained_deltas=delta_count,
            retained_hash=True,
            purged_vfs_files=vfs_file_count,
            purged_caches=cache_count,
            storage_before_bytes=total_before,
            storage_after_bytes=total_after,
        )
        self._gc_history.append(result)
        return result

    def should_expire_deltas(self, delta_timestamp: datetime) -> bool:
        """Check if a delta has exceeded its retention period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.policy.delta_retention_days)
        return delta_timestamp < cutoff

    @property
    def history(self) -> list[GCResult]:
        return list(self._gc_history)
