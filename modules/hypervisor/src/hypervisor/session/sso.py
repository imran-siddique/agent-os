"""Session-scoped VFS integration with copy-on-write snapshots."""

from __future__ import annotations

import copy
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class VFSEdit:
    """A tracked edit to the session VFS."""

    path: str
    operation: str  # "create", "update", "delete", "permission", "restore"
    agent_did: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: Optional[str] = None
    previous_hash: Optional[str] = None


class VFSPermissionError(Exception):
    """Raised when an agent lacks permission to access a VFS path."""


class SessionVFS:
    """
    Session-scoped Virtual File System wrapper.

    Provides copy-on-write isolation per session, agent write attribution,
    permission enforcement, and snapshot/restore for saga rollback.
    """

    def __init__(self, session_id: str, namespace: Optional[str] = None):
        self.session_id = session_id
        self.namespace = namespace or f"/sessions/{session_id}"

        # In-memory file store: path → content
        self._files: dict[str, str] = {}
        # Path-level permissions: path → set of allowed agent DIDs
        # If a path has no entry, all agents can access it (open by default).
        self._permissions: dict[str, set[str]] = {}
        self._edit_log: list[VFSEdit] = []
        self._snapshots: dict[str, dict[str, str]] = {}

    def write(self, path: str, content: str, agent_did: str) -> VFSEdit:
        """Write a file, tracking agent attribution.

        Raises:
            VFSPermissionError: If the path has explicit permissions and
                the agent is not in the allowed set.
        """
        full_path = self._resolve(path)
        self._check_permission(full_path, agent_did)
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

    def read(self, path: str, agent_did: Optional[str] = None) -> Optional[str]:
        """Read a file from the session VFS.

        Args:
            path: File path (relative or absolute).
            agent_did: If provided, permission is checked before reading.
        """
        full_path = self._resolve(path)
        if agent_did is not None:
            self._check_permission(full_path, agent_did)
        return self._files.get(full_path)

    def delete(self, path: str, agent_did: str) -> VFSEdit:
        """Delete a file, tracking agent attribution."""
        full_path = self._resolve(path)
        if full_path not in self._files:
            raise FileNotFoundError(f"{full_path} not found in session VFS")
        self._check_permission(full_path, agent_did)
        previous_hash = _hash(self._files.pop(full_path))
        # Clean up permissions for deleted path
        self._permissions.pop(full_path, None)
        edit = VFSEdit(
            path=full_path,
            operation="delete",
            agent_did=agent_did,
            previous_hash=previous_hash,
        )
        self._edit_log.append(edit)
        return edit

    def list_files(self) -> list[str]:
        """List all files in the session VFS (returns relative paths)."""
        prefix = self.namespace
        return [p.removeprefix(prefix) for p in self._files if p.startswith(prefix)]

    # ── Permission management ─────────────────────────────────

    def set_permissions(
        self, path: str, allowed_agents: set[str], agent_did: str
    ) -> VFSEdit:
        """Set path-level permissions, restricting access to specific agents.

        Args:
            path: The file path to restrict.
            allowed_agents: Set of agent DIDs that may access this path.
            agent_did: The agent setting the permission (recorded in audit log).
        """
        full_path = self._resolve(path)
        self._permissions[full_path] = set(allowed_agents)
        edit = VFSEdit(
            path=full_path,
            operation="permission",
            agent_did=agent_did,
        )
        self._edit_log.append(edit)
        return edit

    def clear_permissions(self, path: str) -> None:
        """Remove path-level permissions (revert to open access)."""
        full_path = self._resolve(path)
        self._permissions.pop(full_path, None)

    def get_permissions(self, path: str) -> Optional[set[str]]:
        """Get the permission set for a path, or None if open."""
        return self._permissions.get(self._resolve(path))

    # ── Snapshot management ───────────────────────────────────

    def create_snapshot(self, snapshot_id: Optional[str] = None) -> str:
        """Snapshot current state for rollback (copy-on-write).

        Captures both files and path-level permissions so the full
        VFS state can be restored atomically.
        """
        sid = snapshot_id or f"snap:{uuid.uuid4()}"
        self._snapshots[sid] = {
            "files": copy.deepcopy(self._files),
            "permissions": copy.deepcopy(self._permissions),
        }
        return sid

    def restore_snapshot(self, snapshot_id: str, agent_did: str) -> None:
        """Restore VFS to a previous snapshot (files + permissions)."""
        if snapshot_id not in self._snapshots:
            raise KeyError(f"Snapshot {snapshot_id} not found")
        snapshot = self._snapshots[snapshot_id]
        self._files = copy.deepcopy(snapshot["files"])
        self._permissions = copy.deepcopy(snapshot["permissions"])
        self._edit_log.append(VFSEdit(
            path=self.namespace,
            operation="restore",
            agent_did=agent_did,
        ))

    def list_snapshots(self) -> list[str]:
        """List all snapshot IDs."""
        return list(self._snapshots.keys())

    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete a snapshot to free memory."""
        if snapshot_id not in self._snapshots:
            raise KeyError(f"Snapshot {snapshot_id} not found")
        del self._snapshots[snapshot_id]

    # ── Query APIs ────────────────────────────────────────────

    @property
    def edit_log(self) -> list[VFSEdit]:
        """Immutable view of the edit log."""
        return list(self._edit_log)

    def edits_by_agent(self, agent_did: str) -> list[VFSEdit]:
        """Return all edits attributed to a specific agent."""
        return [e for e in self._edit_log if e.agent_did == agent_did]

    @property
    def file_count(self) -> int:
        """Number of files currently in the VFS."""
        return len(self._files)

    @property
    def snapshot_count(self) -> int:
        """Number of snapshots currently stored."""
        return len(self._snapshots)

    # ── Internals ─────────────────────────────────────────────

    def _resolve(self, path: str) -> str:
        """Resolve a relative path to session namespace."""
        if path.startswith(self.namespace):
            return path
        clean = path.lstrip("/")
        return f"{self.namespace}/{clean}"

    def _check_permission(self, full_path: str, agent_did: str) -> None:
        """Raise VFSPermissionError if path is restricted and agent is not allowed."""
        allowed = self._permissions.get(full_path)
        if allowed is not None and agent_did not in allowed:
            raise VFSPermissionError(
                f"Agent {agent_did} not permitted to access {full_path}"
            )


def _hash(content: str) -> str:
    """SHA-256 hash of content."""
    return hashlib.sha256(content.encode()).hexdigest()
