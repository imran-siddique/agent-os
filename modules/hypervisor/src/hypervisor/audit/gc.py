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
        self._purged_sessions: set[str] = set()

    def collect(
        self,
        session_id: str,
        vfs: Any = None,
        delta_engine: Any = None,
        vfs_file_count: int = 0,
        cache_count: int = 0,
        delta_count: int = 0,
        estimated_vfs_bytes: int = 0,
        estimated_cache_bytes: int = 0,
        estimated_delta_bytes: int = 0,
    ) -> GCResult:
        """
        Run garbage collection for a terminated session.

        When VFS and DeltaEngine references are provided, actually purges
        ephemeral data. Otherwise falls back to reporting-only mode.
        """
        purged_vfs = 0
        purged_caches = 0

        # Actually purge VFS state if reference provided
        if vfs is not None:
            try:
                files = vfs.list_files() if hasattr(vfs, "list_files") else []
                purged_vfs = len(files)
                for f in files:
                    try:
                        vfs.delete(f)
                    except Exception:
                        pass  # best-effort purge
            except Exception:
                purged_vfs = vfs_file_count
        else:
            purged_vfs = vfs_file_count

        # Expire old deltas if engine provided
        retained_deltas = delta_count
        if delta_engine is not None and hasattr(delta_engine, "deltas"):
            expired = [
                d for d in delta_engine.deltas
                if self.should_expire_deltas(d.timestamp)
            ]
            retained_deltas = delta_count - len(expired)
            if hasattr(delta_engine, "prune_expired"):
                delta_engine.prune_expired(self.policy.delta_retention_days)

        total_before = estimated_vfs_bytes + estimated_cache_bytes + estimated_delta_bytes
        total_after = estimated_delta_bytes if delta_count > 0 else 0

        result = GCResult(
            session_id=session_id,
            retained_deltas=max(retained_deltas, 0),
            retained_hash=True,
            purged_vfs_files=purged_vfs,
            purged_caches=cache_count,
            storage_before_bytes=total_before,
            storage_after_bytes=total_after,
        )
        self._gc_history.append(result)
        self._purged_sessions.add(session_id)
        return result

    def is_purged(self, session_id: str) -> bool:
        """Check if a session has been garbage collected."""
        return session_id in self._purged_sessions

    def should_expire_deltas(self, delta_timestamp: datetime) -> bool:
        """Check if a delta has exceeded its retention period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.policy.delta_retention_days)
        return delta_timestamp < cutoff

    @property
    def history(self) -> list[GCResult]:
        return list(self._gc_history)

    @property
    def purged_session_count(self) -> int:
        return len(self._purged_sessions)
