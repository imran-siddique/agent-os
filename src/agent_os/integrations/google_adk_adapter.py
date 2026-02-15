"""
Google ADK (Agent Development Kit) Integration for Agent-OS
============================================================

Provides kernel-level governance for Google ADK agent workflows.

Features:
- Policy enforcement via ADK's native callback hooks
- before_tool_callback / after_tool_callback for tool governance
- before_agent_callback / after_agent_callback for agent lifecycle
- Content filtering with blocked patterns
- Tool allow/block lists
- Full audit trail of tool calls and agent runs
- Compatible with LlmAgent, SequentialAgent, ParallelAgent, LoopAgent

Example:
    >>> from agent_os.integrations.google_adk_adapter import GoogleADKKernel
    >>> from google.adk.agents import LlmAgent
    >>>
    >>> kernel = GoogleADKKernel(
    ...     max_tool_calls=10,
    ...     blocked_tools=["exec_code", "shell"],
    ...     blocked_patterns=["DROP TABLE", "rm -rf"],
    ... )
    >>>
    >>> agent = LlmAgent(
    ...     model="gemini-2.5-flash",
    ...     name="assistant",
    ...     tools=[my_tool],
    ...     before_tool_callback=kernel.before_tool_callback,
    ...     after_tool_callback=kernel.after_tool_callback,
    ...     before_agent_callback=kernel.before_agent_callback,
    ...     after_agent_callback=kernel.after_agent_callback,
    ... )
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PolicyConfig:
    """Policy configuration for Google ADK governance."""

    max_tool_calls: int = 50
    max_agent_calls: int = 20
    timeout_seconds: int = 300

    allowed_tools: List[str] = field(default_factory=list)
    blocked_tools: List[str] = field(default_factory=list)

    blocked_patterns: List[str] = field(default_factory=list)
    pii_detection: bool = True

    log_all_calls: bool = True


class PolicyViolationError(Exception):
    """Raised when a governance policy is violated."""

    def __init__(self, policy_name: str, description: str, severity: str = "high"):
        self.policy_name = policy_name
        self.description = description
        self.severity = severity
        super().__init__(f"Policy violation ({policy_name}): {description}")


@dataclass
class AuditEvent:
    """Single audit trail entry."""

    timestamp: float
    event_type: str
    agent_name: str
    details: Dict[str, Any]


class GoogleADKKernel:
    """
    Governance kernel for Google ADK.

    Provides callback functions that plug directly into ADK's
    before_tool_callback, after_tool_callback, before_agent_callback,
    and after_agent_callback hooks.
    """

    def __init__(
        self,
        policy: Optional[PolicyConfig] = None,
        on_violation: Optional[Callable[[PolicyViolationError], None]] = None,
        *,
        # Convenience kwargs (create PolicyConfig automatically)
        max_tool_calls: int = 50,
        max_agent_calls: int = 20,
        timeout_seconds: int = 300,
        allowed_tools: Optional[List[str]] = None,
        blocked_tools: Optional[List[str]] = None,
        blocked_patterns: Optional[List[str]] = None,
    ):
        if policy is not None:
            self.policy = policy
        else:
            self.policy = PolicyConfig(
                max_tool_calls=max_tool_calls,
                max_agent_calls=max_agent_calls,
                timeout_seconds=timeout_seconds,
                allowed_tools=allowed_tools or [],
                blocked_tools=blocked_tools or [],
                blocked_patterns=blocked_patterns or [],
            )
        self.on_violation = on_violation or self._default_violation_handler

        # Counters
        self._tool_call_count: int = 0
        self._agent_call_count: int = 0
        self._start_time: float = time.time()

        # Audit trail
        self._audit_log: List[AuditEvent] = []

        # Violations collected
        self._violations: List[PolicyViolationError] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_violation_handler(self, error: PolicyViolationError) -> None:
        logger.error(f"Policy violation: {error}")

    def _record(self, event_type: str, agent_name: str, details: Dict[str, Any]) -> None:
        if self.policy.log_all_calls:
            self._audit_log.append(
                AuditEvent(
                    timestamp=time.time(),
                    event_type=event_type,
                    agent_name=agent_name,
                    details=details,
                )
            )

    def _check_tool_allowed(self, tool_name: str) -> tuple[bool, str]:
        if tool_name in self.policy.blocked_tools:
            return False, f"Tool '{tool_name}' is blocked by policy"
        if self.policy.allowed_tools and tool_name not in self.policy.allowed_tools:
            return False, f"Tool '{tool_name}' not in allowed list"
        return True, ""

    def _check_content(self, content: str) -> tuple[bool, str]:
        content_lower = content.lower()
        for pattern in self.policy.blocked_patterns:
            if pattern.lower() in content_lower:
                return False, f"Content matches blocked pattern: '{pattern}'"
        return True, ""

    def _check_timeout(self) -> tuple[bool, str]:
        elapsed = time.time() - self._start_time
        if elapsed > self.policy.timeout_seconds:
            return False, f"Execution timeout ({elapsed:.0f}s > {self.policy.timeout_seconds}s)"
        return True, ""

    def _raise_violation(self, policy_name: str, description: str) -> PolicyViolationError:
        error = PolicyViolationError(policy_name, description)
        self._violations.append(error)
        self.on_violation(error)
        return error

    # ------------------------------------------------------------------
    # ADK Callback Hooks
    # ------------------------------------------------------------------

    def before_tool_callback(self, tool_context: Any = None, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        ADK before_tool_callback — called before each tool execution.

        Compatible with ADK's ToolContext. If tool_context is not an ADK
        ToolContext (e.g., in tests), falls back to kwargs for tool_name/tool_args.

        Returns:
            None to allow execution, or a dict with an error to block it.
        """
        tool_name = getattr(tool_context, "tool_name", kwargs.get("tool_name", "unknown"))
        tool_args = getattr(tool_context, "tool_args", kwargs.get("tool_args", {}))
        agent_name = getattr(tool_context, "agent_name", kwargs.get("agent_name", "unknown"))

        self._record("before_tool", agent_name, {"tool": tool_name, "args": tool_args})

        # Check timeout
        ok, reason = self._check_timeout()
        if not ok:
            error = self._raise_violation("timeout", reason)
            return {"error": str(error)}

        # Check tool count
        self._tool_call_count += 1
        if self._tool_call_count > self.policy.max_tool_calls:
            error = self._raise_violation(
                "tool_limit",
                f"Tool call count ({self._tool_call_count}) exceeds limit ({self.policy.max_tool_calls})",
            )
            return {"error": str(error)}

        # Check tool allowed
        ok, reason = self._check_tool_allowed(tool_name)
        if not ok:
            error = self._raise_violation("tool_filter", reason)
            return {"error": str(error)}

        # Check content in arguments
        if isinstance(tool_args, dict):
            for value in tool_args.values():
                if isinstance(value, str):
                    ok, reason = self._check_content(value)
                    if not ok:
                        error = self._raise_violation("content_filter", reason)
                        return {"error": str(error)}

        return None  # Allow execution

    def after_tool_callback(
        self,
        tool_context: Any = None,
        tool_result: Any = None,
        **kwargs: Any,
    ) -> Any:
        """
        ADK after_tool_callback — called after each tool execution.

        Inspects tool output for blocked patterns.

        Returns:
            The (possibly modified) tool_result, or a dict with error if blocked.
        """
        tool_name = getattr(tool_context, "tool_name", kwargs.get("tool_name", "unknown"))
        agent_name = getattr(tool_context, "agent_name", kwargs.get("agent_name", "unknown"))

        self._record("after_tool", agent_name, {"tool": tool_name, "result_type": type(tool_result).__name__})

        # Check output content
        if isinstance(tool_result, str):
            ok, reason = self._check_content(tool_result)
            if not ok:
                error = self._raise_violation("output_filter", reason)
                return {"error": str(error)}

        if isinstance(tool_result, dict):
            for value in tool_result.values():
                if isinstance(value, str):
                    ok, reason = self._check_content(value)
                    if not ok:
                        error = self._raise_violation("output_filter", reason)
                        return {"error": str(error)}

        return tool_result

    def before_agent_callback(self, callback_context: Any = None, **kwargs: Any) -> Any:
        """
        ADK before_agent_callback — called before agent starts processing.

        Returns:
            None to allow, or a Content-like object to skip the agent.
        """
        agent_name = getattr(callback_context, "agent_name", kwargs.get("agent_name", "unknown"))

        self._record("before_agent", agent_name, {})

        # Check timeout
        ok, reason = self._check_timeout()
        if not ok:
            error = self._raise_violation("timeout", reason)
            return {"error": str(error)}

        # Check agent call count
        self._agent_call_count += 1
        if self._agent_call_count > self.policy.max_agent_calls:
            error = self._raise_violation(
                "agent_limit",
                f"Agent call count ({self._agent_call_count}) exceeds limit ({self.policy.max_agent_calls})",
            )
            return {"error": str(error)}

        return None

    def after_agent_callback(
        self,
        callback_context: Any = None,
        content: Any = None,
        **kwargs: Any,
    ) -> Any:
        """
        ADK after_agent_callback — called after agent finishes.

        Checks agent output for blocked content.

        Returns:
            The content (possibly modified), or a dict with error if blocked.
        """
        agent_name = getattr(callback_context, "agent_name", kwargs.get("agent_name", "unknown"))

        self._record("after_agent", agent_name, {"has_content": content is not None})

        # Check output content if it's a string
        if isinstance(content, str):
            ok, reason = self._check_content(content)
            if not ok:
                error = self._raise_violation("output_filter", reason)
                return {"error": str(error)}

        return content

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset counters and start time (for new execution runs)."""
        self._tool_call_count = 0
        self._agent_call_count = 0
        self._start_time = time.time()

    def get_audit_log(self) -> List[AuditEvent]:
        """Return the full audit trail."""
        return list(self._audit_log)

    def get_violations(self) -> List[PolicyViolationError]:
        """Return all collected violations."""
        return list(self._violations)

    def get_stats(self) -> Dict[str, Any]:
        """Get governance statistics."""
        return {
            "tool_calls": self._tool_call_count,
            "agent_calls": self._agent_call_count,
            "violations": len(self._violations),
            "audit_events": len(self._audit_log),
            "elapsed_seconds": round(time.time() - self._start_time, 2),
            "policy": {
                "max_tool_calls": self.policy.max_tool_calls,
                "max_agent_calls": self.policy.max_agent_calls,
                "blocked_tools": self.policy.blocked_tools,
                "allowed_tools": self.policy.allowed_tools,
            },
        }

    def get_callbacks(self) -> Dict[str, Any]:
        """
        Return a dict of all callbacks suitable for unpacking into LlmAgent.

        Usage:
            agent = LlmAgent(..., **kernel.get_callbacks())
        """
        return {
            "before_tool_callback": self.before_tool_callback,
            "after_tool_callback": self.after_tool_callback,
            "before_agent_callback": self.before_agent_callback,
            "after_agent_callback": self.after_agent_callback,
        }


__all__ = [
    "GoogleADKKernel",
    "PolicyConfig",
    "PolicyViolationError",
    "AuditEvent",
]
