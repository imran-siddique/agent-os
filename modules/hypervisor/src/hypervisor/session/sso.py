"""Session-scoped VFS integration with copy-on-write snapshots."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class VFSEdit:
    """A tracked edit to the session VFS."""

    path: str
    operation: str  # "create", "update", "delete", "permission"
    agent_did: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: Optional[str] = None
    previous_hash: Optional[str] = None


class SessionVFS:
    """
    Session-scoped Virtual File System wrapper.

    Provides copy-on-write isolation per session, agent write attribution,
    and snapshot/restore for saga rollback.
    """

    def __init__(self, session_id: str, namespace: Optional[str] = None):
        self.session_id = session_id
        self.namespace = namespace or f"/sessions/{session_id}"

        # In-memory file store: path → content
        self._files: dict[str, str] = {}
        self._permissions: dict[str, set[str]] = {}  # path → set of allowed agent DIDs
        self._edit_log: list[VFSEdit] = []
        self._snapshots: dict[str, dict[str, str]] = {}

    def write(self, path: str, content: str, agent_did: str) -> VFSEdit:
        """Write a file, tracking agent attribution."""
        full_path = self._resolve(path)
        operation = "update" if full_path in self._files else "create"
        previous_hash = _hash(self._files.get(full_path, ""))
        self._files[full_path] = content
        edit = VFSEdit(
            path=full_path,
            operation=operation,
            agent_did=agent_did,
            content_hash=_hash(content),
            previous_hash=previous_hash if operation == "update" else None,
        )
        self._edit_log.append(edit)
        return edit

    def read(self, path: str) -> Optional[str]:
        """Read a file from the session VFS."""
        return self._files.get(self._resolve(path))

    def delete(self, path: str, agent_did: str) -> VFSEdit:
        """Delete a file, tracking agent attribution."""
        full_path = self._resolve(path)
        if full_path not in self._files:
            raise FileNotFoundError(f"{full_path} not found in session VFS")
        previous_hash = _hash(self._files.pop(full_path))
        edit = VFSEdit(
            path=full_path,
            operation="delete",
            agent_did=agent_did,
            previous_hash=previous_hash,
        )
        self._edit_log.append(edit)
        return edit

    def list_files(self) -> list[str]:
        """List all files in the session VFS."""
        prefix = self.namespace
        return [p.removeprefix(prefix) for p in self._files if p.startswith(prefix)]

    def create_snapshot(self, snapshot_id: Optional[str] = None) -> str:
        """Snapshot current state for rollback."""
        sid = snapshot_id or f"snap:{uuid.uuid4()}"
        self._snapshots[sid] = copy.deepcopy(self._files)
        return sid

    def restore_snapshot(self, snapshot_id: str, agent_did: str) -> None:
        """Restore VFS to a previous snapshot."""
        if snapshot_id not in self._snapshots:
            raise KeyError(f"Snapshot {snapshot_id} not found")
        self._files = copy.deepcopy(self._snapshots[snapshot_id])
        self._edit_log.append(VFSEdit(
            path=self.namespace,
            operation="restore",
            agent_did=agent_did,
        ))

    @property
    def edit_log(self) -> list[VFSEdit]:
        """Immutable view of the edit log."""
        return list(self._edit_log)

    def _resolve(self, path: str) -> str:
        """Resolve a relative path to session namespace."""
        if path.startswith(self.namespace):
            return path
        clean = path.lstrip("/")
        return f"{self.namespace}/{clean}"


def _hash(content: str) -> str:
    """SHA-256 hash of content."""
    import hashlib
    return hashlib.sha256(content.encode()).hexdigest()
