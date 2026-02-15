"""
Tests for Google ADK (Agent Development Kit) governance adapter.

No real ADK dependency required — uses mock ToolContext/CallbackContext objects.

Run with: python -m pytest tests/test_google_adk_adapter.py -v --tb=short
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

from agent_os.integrations.google_adk_adapter import (
    AuditEvent,
    GoogleADKKernel,
    PolicyConfig,
    PolicyViolationError,
)


# =============================================================================
# Fake ADK context objects (no real google.adk dependency)
# =============================================================================


@dataclass
class FakeToolContext:
    tool_name: str = "my_tool"
    tool_args: Dict[str, Any] = field(default_factory=dict)
    agent_name: str = "test-agent"


@dataclass
class FakeCallbackContext:
    agent_name: str = "test-agent"


# =============================================================================
# PolicyConfig tests
# =============================================================================


class TestPolicyConfig:
    def test_defaults(self):
        p = PolicyConfig()
        assert p.max_tool_calls == 50
        assert p.max_agent_calls == 20
        assert p.timeout_seconds == 300
        assert p.allowed_tools == []
        assert p.blocked_tools == []
        assert p.blocked_patterns == []
        assert p.pii_detection is True
        assert p.log_all_calls is True

    def test_custom(self):
        p = PolicyConfig(max_tool_calls=5, blocked_tools=["exec"])
        assert p.max_tool_calls == 5
        assert p.blocked_tools == ["exec"]


# =============================================================================
# Kernel init
# =============================================================================


class TestGoogleADKKernelInit:
    def test_default_policy(self):
        k = GoogleADKKernel()
        assert k.policy.max_tool_calls == 50

    def test_explicit_policy(self):
        p = PolicyConfig(max_tool_calls=3)
        k = GoogleADKKernel(policy=p)
        assert k.policy.max_tool_calls == 3

    def test_convenience_kwargs(self):
        k = GoogleADKKernel(
            max_tool_calls=7,
            blocked_tools=["shell"],
            blocked_patterns=["DROP TABLE"],
        )
        assert k.policy.max_tool_calls == 7
        assert k.policy.blocked_tools == ["shell"]
        assert k.policy.blocked_patterns == ["DROP TABLE"]

    def test_custom_violation_handler(self):
        captured = []
        k = GoogleADKKernel(on_violation=lambda e: captured.append(e))
        k.before_tool_callback(FakeToolContext(tool_name="blocked"), blocked_tools=None)
        # No violation yet, should be empty
        assert captured == []


# =============================================================================
# before_tool_callback
# =============================================================================


class TestBeforeToolCallback:
    def test_allowed_tool(self):
        k = GoogleADKKernel()
        result = k.before_tool_callback(FakeToolContext(tool_name="search"))
        assert result is None  # None = allow

    def test_blocked_tool(self):
        k = GoogleADKKernel(blocked_tools=["exec_code", "shell"])
        result = k.before_tool_callback(FakeToolContext(tool_name="exec_code"))
        assert result is not None
        assert "error" in result
        assert "blocked" in result["error"].lower()

    def test_allowed_list_accepts(self):
        k = GoogleADKKernel(allowed_tools=["search", "calculator"])
        result = k.before_tool_callback(FakeToolContext(tool_name="search"))
        assert result is None

    def test_allowed_list_rejects(self):
        k = GoogleADKKernel(allowed_tools=["search", "calculator"])
        result = k.before_tool_callback(FakeToolContext(tool_name="exec_code"))
        assert result is not None
        assert "error" in result

    def test_tool_call_limit(self):
        k = GoogleADKKernel(max_tool_calls=3)
        for _ in range(3):
            assert k.before_tool_callback(FakeToolContext()) is None
        result = k.before_tool_callback(FakeToolContext())
        assert result is not None
        assert "limit" in result["error"].lower()

    def test_content_filter_in_args(self):
        k = GoogleADKKernel(blocked_patterns=["DROP TABLE"])
        ctx = FakeToolContext(tool_args={"query": "DROP TABLE users"})
        result = k.before_tool_callback(ctx)
        assert result is not None
        assert "error" in result

    def test_content_filter_case_insensitive(self):
        k = GoogleADKKernel(blocked_patterns=["rm -rf"])
        ctx = FakeToolContext(tool_args={"cmd": "RM -RF /"})
        result = k.before_tool_callback(ctx)
        assert result is not None

    def test_increments_counter(self):
        k = GoogleADKKernel()
        k.before_tool_callback(FakeToolContext())
        k.before_tool_callback(FakeToolContext())
        assert k._tool_call_count == 2

    def test_timeout(self):
        k = GoogleADKKernel(timeout_seconds=0)
        k._start_time = time.time() - 1  # force expired
        result = k.before_tool_callback(FakeToolContext())
        assert result is not None
        assert "timeout" in result["error"].lower()

    def test_kwargs_fallback_when_no_context(self):
        k = GoogleADKKernel(blocked_tools=["shell"])
        result = k.before_tool_callback(tool_name="shell", tool_args={})
        assert result is not None
        assert "blocked" in result["error"].lower()

    def test_records_violation(self):
        k = GoogleADKKernel(blocked_tools=["danger"])
        k.before_tool_callback(FakeToolContext(tool_name="danger"))
        assert len(k.get_violations()) == 1
        assert k.get_violations()[0].policy_name == "tool_filter"


# =============================================================================
# after_tool_callback
# =============================================================================


class TestAfterToolCallback:
    def test_passes_result_through(self):
        k = GoogleADKKernel()
        result = k.after_tool_callback(FakeToolContext(), tool_result={"data": 42})
        assert result == {"data": 42}

    def test_blocks_string_output(self):
        k = GoogleADKKernel(blocked_patterns=["SECRET_TOKEN"])
        result = k.after_tool_callback(FakeToolContext(), tool_result="key=SECRET_TOKEN_123")
        assert "error" in result

    def test_blocks_dict_output(self):
        k = GoogleADKKernel(blocked_patterns=["password"])
        result = k.after_tool_callback(
            FakeToolContext(), tool_result={"msg": "your password is 1234"}
        )
        assert "error" in result

    def test_allows_safe_output(self):
        k = GoogleADKKernel(blocked_patterns=["DROP TABLE"])
        result = k.after_tool_callback(FakeToolContext(), tool_result="query succeeded")
        assert result == "query succeeded"

    def test_none_result(self):
        k = GoogleADKKernel()
        result = k.after_tool_callback(FakeToolContext(), tool_result=None)
        assert result is None


# =============================================================================
# before_agent_callback
# =============================================================================


class TestBeforeAgentCallback:
    def test_allows_agent(self):
        k = GoogleADKKernel()
        result = k.before_agent_callback(FakeCallbackContext())
        assert result is None

    def test_agent_call_limit(self):
        k = GoogleADKKernel(max_agent_calls=2)
        assert k.before_agent_callback(FakeCallbackContext()) is None
        assert k.before_agent_callback(FakeCallbackContext()) is None
        result = k.before_agent_callback(FakeCallbackContext())
        assert result is not None
        assert "error" in result

    def test_timeout(self):
        k = GoogleADKKernel(timeout_seconds=0)
        k._start_time = time.time() - 1
        result = k.before_agent_callback(FakeCallbackContext())
        assert result is not None
        assert "timeout" in result["error"].lower()

    def test_increments_counter(self):
        k = GoogleADKKernel()
        k.before_agent_callback(FakeCallbackContext())
        k.before_agent_callback(FakeCallbackContext())
        assert k._agent_call_count == 2


# =============================================================================
# after_agent_callback
# =============================================================================


class TestAfterAgentCallback:
    def test_passes_content_through(self):
        k = GoogleADKKernel()
        result = k.after_agent_callback(FakeCallbackContext(), content="Hello world")
        assert result == "Hello world"

    def test_blocks_string_content(self):
        k = GoogleADKKernel(blocked_patterns=["rm -rf"])
        result = k.after_agent_callback(FakeCallbackContext(), content="run rm -rf /")
        assert "error" in result

    def test_allows_safe_content(self):
        k = GoogleADKKernel(blocked_patterns=["DROP"])
        result = k.after_agent_callback(FakeCallbackContext(), content="All good")
        assert result == "All good"

    def test_none_content(self):
        k = GoogleADKKernel()
        result = k.after_agent_callback(FakeCallbackContext(), content=None)
        assert result is None


# =============================================================================
# Audit & Stats
# =============================================================================


class TestAuditAndStats:
    def test_audit_log_records_events(self):
        k = GoogleADKKernel()
        k.before_tool_callback(FakeToolContext(tool_name="search", agent_name="a1"))
        k.after_tool_callback(FakeToolContext(tool_name="search", agent_name="a1"), tool_result="ok")
        k.before_agent_callback(FakeCallbackContext(agent_name="a1"))
        k.after_agent_callback(FakeCallbackContext(agent_name="a1"), content="done")

        log = k.get_audit_log()
        assert len(log) == 4
        assert log[0].event_type == "before_tool"
        assert log[1].event_type == "after_tool"
        assert log[2].event_type == "before_agent"
        assert log[3].event_type == "after_agent"

    def test_audit_log_disabled(self):
        p = PolicyConfig(log_all_calls=False)
        k = GoogleADKKernel(policy=p)
        k.before_tool_callback(FakeToolContext())
        assert len(k.get_audit_log()) == 0

    def test_audit_event_fields(self):
        k = GoogleADKKernel()
        k.before_tool_callback(FakeToolContext(tool_name="calc", agent_name="bot"))
        event = k.get_audit_log()[0]
        assert isinstance(event, AuditEvent)
        assert event.agent_name == "bot"
        assert event.details["tool"] == "calc"
        assert event.timestamp > 0

    def test_stats(self):
        k = GoogleADKKernel(max_tool_calls=10, blocked_tools=["shell"])
        k.before_tool_callback(FakeToolContext(tool_name="search"))
        k.before_tool_callback(FakeToolContext(tool_name="shell"))  # violation
        k.before_agent_callback(FakeCallbackContext())

        stats = k.get_stats()
        assert stats["tool_calls"] == 2
        assert stats["agent_calls"] == 1
        assert stats["violations"] == 1
        assert stats["audit_events"] == 3
        assert stats["elapsed_seconds"] >= 0

    def test_reset(self):
        k = GoogleADKKernel(max_tool_calls=2)
        k.before_tool_callback(FakeToolContext())
        k.before_tool_callback(FakeToolContext())
        # Limit reached
        result = k.before_tool_callback(FakeToolContext())
        assert result is not None

        k.reset()
        # After reset, counter is fresh
        result = k.before_tool_callback(FakeToolContext())
        assert result is None
        assert k._tool_call_count == 1

    def test_violations_list(self):
        k = GoogleADKKernel(blocked_tools=["exec", "shell"])
        k.before_tool_callback(FakeToolContext(tool_name="exec"))
        k.before_tool_callback(FakeToolContext(tool_name="shell"))
        v = k.get_violations()
        assert len(v) == 2
        assert all(isinstance(e, PolicyViolationError) for e in v)


# =============================================================================
# get_callbacks()
# =============================================================================


class TestGetCallbacks:
    def test_returns_four_callbacks(self):
        k = GoogleADKKernel()
        cbs = k.get_callbacks()
        assert "before_tool_callback" in cbs
        assert "after_tool_callback" in cbs
        assert "before_agent_callback" in cbs
        assert "after_agent_callback" in cbs

    def test_callbacks_are_callable(self):
        k = GoogleADKKernel()
        cbs = k.get_callbacks()
        for name, cb in cbs.items():
            assert callable(cb), f"{name} is not callable"

    def test_unpack_into_agent(self):
        """Simulate **kernel.get_callbacks() usage for LlmAgent constructor."""
        k = GoogleADKKernel(blocked_tools=["danger"])
        cbs = k.get_callbacks()

        # Simulate ADK calling the callbacks
        result = cbs["before_tool_callback"](FakeToolContext(tool_name="danger"))
        assert result is not None
        assert "error" in result


# =============================================================================
# Integration: full lifecycle
# =============================================================================


class TestIntegration:
    def test_full_lifecycle(self):
        """Simulate a complete agent run with multiple tool calls."""
        violations = []
        k = GoogleADKKernel(
            max_tool_calls=5,
            blocked_tools=["shell"],
            blocked_patterns=["SECRET"],
            on_violation=lambda e: violations.append(e),
        )

        # Agent starts
        assert k.before_agent_callback(FakeCallbackContext(agent_name="assistant")) is None

        # Tool 1: allowed
        assert k.before_tool_callback(
            FakeToolContext(tool_name="search", tool_args={"q": "weather"}, agent_name="assistant")
        ) is None
        assert k.after_tool_callback(
            FakeToolContext(tool_name="search", agent_name="assistant"),
            tool_result="Sunny, 72°F",
        ) == "Sunny, 72°F"

        # Tool 2: blocked tool
        result = k.before_tool_callback(
            FakeToolContext(tool_name="shell", tool_args={"cmd": "ls"}, agent_name="assistant")
        )
        assert result is not None

        # Tool 3: blocked content in args
        result = k.before_tool_callback(
            FakeToolContext(
                tool_name="search",
                tool_args={"q": "find SECRET key"},
                agent_name="assistant",
            )
        )
        assert result is not None

        # Tool 4: allowed tool but blocked output
        assert k.before_tool_callback(
            FakeToolContext(tool_name="db_query", tool_args={"q": "SELECT *"}, agent_name="assistant")
        ) is None
        result = k.after_tool_callback(
            FakeToolContext(tool_name="db_query", agent_name="assistant"),
            tool_result="SECRET_API_KEY=abc123",
        )
        assert "error" in result

        # Agent finishes
        final = k.after_agent_callback(
            FakeCallbackContext(agent_name="assistant"),
            content="The weather is sunny.",
        )
        assert final == "The weather is sunny."

        # Verify stats
        assert k._tool_call_count == 4
        assert k._agent_call_count == 1
        assert len(violations) == 3  # blocked tool + content in args + output filter
        assert len(k.get_audit_log()) >= 6

    def test_policy_violation_error(self):
        e = PolicyViolationError("test_policy", "something bad", severity="critical")
        assert e.policy_name == "test_policy"
        assert e.description == "something bad"
        assert e.severity == "critical"
        assert "test_policy" in str(e)
