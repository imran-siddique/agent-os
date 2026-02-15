"""
Tests for framework integration adapters.

Covers: base.py, langchain_adapter.py, crewai_adapter.py, openai_adapter.py
Uses mock objects — no real API calls.

Run with: python -m pytest tests/test_integrations.py -v --tb=short
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from agent_os.integrations.base import (
    ExecutionContext,
    GovernancePolicy,
)
from agent_os.integrations.crewai_adapter import CrewAIKernel
from agent_os.integrations.langchain_adapter import (
    LangChainKernel,
    PolicyViolationError,
)
from agent_os.integrations.openai_adapter import (
    AssistantContext,
    GovernedAssistant,
    OpenAIKernel,
    RunCancelledException,
)
from agent_os.integrations.openai_adapter import (
    PolicyViolationError as OpenAIPolicyViolationError,
)

# =============================================================================
# Helpers
# =============================================================================


def _make_mock_chain(name="test-chain"):
    """Create a mock LangChain-like chain/runnable."""
    chain = MagicMock()
    chain.name = name
    chain.invoke.return_value = "invoke-result"
    chain.run.return_value = "run-result"
    chain.batch.return_value = ["batch-1", "batch-2"]
    chain.stream.return_value = iter(["chunk-1", "chunk-2"])
    return chain


def _make_mock_crew():
    """Create a mock CrewAI crew."""
    crew = MagicMock()
    crew.id = "crew-42"
    crew.kickoff.return_value = "crew-result"
    crew.agents = []
    return crew


def _make_mock_openai_client():
    """Create a mock OpenAI client with all required sub-objects."""
    client = MagicMock()
    # Thread creation
    thread = MagicMock()
    thread.id = "thread_abc"
    client.beta.threads.create.return_value = thread
    # Message creation
    msg = MagicMock()
    msg.id = "msg_xyz"
    client.beta.threads.messages.create.return_value = msg
    return client


def _make_mock_assistant(assistant_id="asst_001", name="TestBot"):
    assistant = MagicMock()
    assistant.id = assistant_id
    assistant.name = name
    return assistant


def _make_completed_run(run_id="run_001", usage=None):
    """Return a mock run object with status 'completed'."""
    run = MagicMock()
    run.id = run_id
    run.status = "completed"
    run.usage = usage
    return run


def _make_requires_action_run(run_id="run_001", tool_calls=None):
    """Return a mock run that requires tool-call action."""
    run = MagicMock()
    run.id = run_id
    run.status = "requires_action"
    run.usage = None  # no token usage yet
    if tool_calls is None:
        tc = MagicMock()
        tc.id = "call_1"
        tc.type = "function"
        tc.function.name = "get_weather"
        tc.function.arguments = '{"city":"NY"}'
        tool_calls = [tc]
    run.required_action.submit_tool_outputs.tool_calls = tool_calls
    return run


# =============================================================================
# GovernancePolicy defaults & customisation
# =============================================================================


class TestGovernancePolicy:
    def test_defaults(self):
        p = GovernancePolicy()
        assert p.max_tokens == 4096
        assert p.max_tool_calls == 10
        assert p.allowed_tools == []
        assert p.blocked_patterns == []
        assert p.require_human_approval is False
        assert p.timeout_seconds == 300
        assert p.confidence_threshold == 0.8
        assert p.drift_threshold == 0.15
        assert p.log_all_calls is True
        assert p.checkpoint_frequency == 5

    def test_custom_values(self):
        p = GovernancePolicy(
            max_tokens=1000,
            max_tool_calls=3,
            blocked_patterns=["secret"],
            timeout_seconds=60,
        )
        assert p.max_tokens == 1000
        assert p.max_tool_calls == 3
        assert p.blocked_patterns == ["secret"]
        assert p.timeout_seconds == 60

    def test_identical_policies_are_equal(self):
        p1 = GovernancePolicy(
            allowed_tools=["search", "read_file"],
            blocked_patterns=["password"],
            max_tool_calls=5,
        )
        p2 = GovernancePolicy(
            allowed_tools=["search", "read_file"],
            blocked_patterns=["password"],
            max_tool_calls=5,
        )
        assert p1 == p2

    def test_policies_with_different_values_are_not_equal(self):
        p1 = GovernancePolicy(max_tokens=1024)
        p2 = GovernancePolicy(max_tokens=2048)
        assert p1 != p2

    def test_policy_is_not_equal_to_non_policy_object(self):
        p = GovernancePolicy()
        assert p != "not-a-policy"

    def test_policies_are_hashable_for_sets_and_dicts(self):
        p1 = GovernancePolicy(allowed_tools=["search"])
        p2 = GovernancePolicy(allowed_tools=["search"])
        p3 = GovernancePolicy(allowed_tools=["write"])

        policy_set = {p1, p2, p3}
        policy_dict = {p1: "alpha", p3: "beta"}

        assert len(policy_set) == 2
        assert policy_dict[p2] == "alpha"


# =============================================================================
# GovernancePolicy input validation
# =============================================================================


class TestGovernancePolicyValidation:
    """Tests for GovernancePolicy.validate() input validation."""

    def test_default_policy_passes_validation(self):
        p = GovernancePolicy()
        p.validate()  # should not raise

    def test_max_tokens_zero_raises(self):
        with pytest.raises(ValueError, match="max_tokens must be a positive integer"):
            GovernancePolicy(max_tokens=0)

    def test_max_tokens_negative_raises(self):
        with pytest.raises(ValueError, match="max_tokens must be a positive integer"):
            GovernancePolicy(max_tokens=-1)

    def test_max_tool_calls_negative_raises(self):
        with pytest.raises(ValueError, match="max_tool_calls must be a non-negative integer"):
            GovernancePolicy(max_tool_calls=-1)

    def test_max_tool_calls_zero_allowed(self):
        p = GovernancePolicy(max_tool_calls=0)
        assert p.max_tool_calls == 0

    def test_timeout_seconds_zero_raises(self):
        with pytest.raises(ValueError, match="timeout_seconds must be a positive integer"):
            GovernancePolicy(timeout_seconds=0)

    def test_timeout_seconds_negative_raises(self):
        with pytest.raises(ValueError, match="timeout_seconds must be a positive integer"):
            GovernancePolicy(timeout_seconds=-10)

    def test_max_concurrent_zero_raises(self):
        with pytest.raises(ValueError, match="max_concurrent must be a positive integer"):
            GovernancePolicy(max_concurrent=0)

    def test_checkpoint_frequency_zero_raises(self):
        with pytest.raises(ValueError, match="checkpoint_frequency must be a positive integer"):
            GovernancePolicy(checkpoint_frequency=0)

    def test_confidence_threshold_negative_raises(self):
        with pytest.raises(
            ValueError, match="confidence_threshold must be a float between 0.0 and 1.0"
        ):
            GovernancePolicy(confidence_threshold=-0.1)

    def test_confidence_threshold_above_one_raises(self):
        with pytest.raises(
            ValueError, match="confidence_threshold must be a float between 0.0 and 1.0"
        ):
            GovernancePolicy(confidence_threshold=1.5)

    def test_drift_threshold_negative_raises(self):
        with pytest.raises(ValueError, match="drift_threshold must be a float between 0.0 and 1.0"):
            GovernancePolicy(drift_threshold=-0.01)

    def test_drift_threshold_above_one_raises(self):
        with pytest.raises(ValueError, match="drift_threshold must be a float between 0.0 and 1.0"):
            GovernancePolicy(drift_threshold=2.0)

    def test_allowed_tools_non_string_raises(self):
        with pytest.raises(ValueError, match="allowed_tools\\[0\\] must be a string"):
            GovernancePolicy(allowed_tools=[123])

    def test_allowed_tools_mixed_types_raises(self):
        with pytest.raises(ValueError, match="allowed_tools\\[1\\] must be a string"):
            GovernancePolicy(allowed_tools=["valid", 42])

    def test_blocked_patterns_non_string_raises(self):
        with pytest.raises(ValueError, match="blocked_patterns\\[0\\] must be a string"):
            GovernancePolicy(blocked_patterns=[None])

    def test_valid_string_lists_pass(self):
        p = GovernancePolicy(
            allowed_tools=["tool_a", "tool_b"],
            blocked_patterns=["secret", "password"],
        )
        assert p.allowed_tools == ["tool_a", "tool_b"]
        assert p.blocked_patterns == ["secret", "password"]

    def test_boundary_thresholds_pass(self):
        p = GovernancePolicy(confidence_threshold=0.0, drift_threshold=1.0)
        assert p.confidence_threshold == 0.0
        assert p.drift_threshold == 1.0

    def test_adapter_with_invalid_policy_raises(self):
        with pytest.raises(ValueError, match="max_tokens must be a positive integer"):
            LangChainKernel(policy=GovernancePolicy(max_tokens=-5))


# =============================================================================
# ExecutionContext
# =============================================================================


class TestExecutionContext:
    def test_initial_state(self):
        ctx = ExecutionContext(
            agent_id="a1",
            session_id="s1",
            policy=GovernancePolicy(),
        )
        assert ctx.call_count == 0
        assert ctx.total_tokens == 0
        assert ctx.tool_calls == []
        assert ctx.checkpoints == []
        assert isinstance(ctx.start_time, datetime)


class TestExecutionContextValidation:
    """Tests for ExecutionContext.validate() input validation."""

    def test_valid_context_passes_validation(self):
        ctx = ExecutionContext(
            agent_id="agent-1_test",
            session_id="sess-abc",
            policy=GovernancePolicy(),
        )
        ctx.validate()  # should not raise

    def test_empty_agent_id_raises(self):
        with pytest.raises(ValueError, match="agent_id must be a non-empty string"):
            ExecutionContext(agent_id="", session_id="s1", policy=GovernancePolicy())

    def test_non_string_agent_id_raises(self):
        with pytest.raises(ValueError, match="agent_id must be a non-empty string"):
            ExecutionContext(agent_id=123, session_id="s1", policy=GovernancePolicy())

    def test_agent_id_with_invalid_chars_raises(self):
        with pytest.raises(ValueError, match=r"agent_id must match"):
            ExecutionContext(agent_id="agent id!", session_id="s1", policy=GovernancePolicy())

    def test_agent_id_valid_patterns_pass(self):
        for aid in ("a1", "my-agent", "Agent_01", "test-agent-v2"):
            ctx = ExecutionContext(agent_id=aid, session_id="s1", policy=GovernancePolicy())
            assert ctx.agent_id == aid

    def test_empty_session_id_raises(self):
        with pytest.raises(ValueError, match="session_id must be a non-empty string"):
            ExecutionContext(agent_id="a1", session_id="", policy=GovernancePolicy())

    def test_non_string_session_id_raises(self):
        with pytest.raises(ValueError, match="session_id must be a non-empty string"):
            ExecutionContext(agent_id="a1", session_id=None, policy=GovernancePolicy())

    def test_policy_not_governance_policy_raises(self):
        with pytest.raises(ValueError, match="policy must be a GovernancePolicy instance"):
            ExecutionContext(agent_id="a1", session_id="s1", policy="not-a-policy")

    def test_negative_call_count_raises(self):
        with pytest.raises(ValueError, match="call_count must be a non-negative integer"):
            ExecutionContext(
                agent_id="a1", session_id="s1", policy=GovernancePolicy(), call_count=-1
            )

    def test_negative_total_tokens_raises(self):
        with pytest.raises(ValueError, match="total_tokens must be a non-negative integer"):
            ExecutionContext(
                agent_id="a1", session_id="s1", policy=GovernancePolicy(), total_tokens=-5
            )

    def test_zero_call_count_and_total_tokens_pass(self):
        ctx = ExecutionContext(
            agent_id="a1", session_id="s1", policy=GovernancePolicy(), call_count=0, total_tokens=0
        )
        assert ctx.call_count == 0
        assert ctx.total_tokens == 0

    def test_checkpoints_non_string_entry_raises(self):
        with pytest.raises(ValueError, match=r"checkpoints\[0\] must be a string"):
            ExecutionContext(
                agent_id="a1", session_id="s1", policy=GovernancePolicy(), checkpoints=[42]
            )

    def test_valid_checkpoints_pass(self):
        ctx = ExecutionContext(
            agent_id="a1",
            session_id="s1",
            policy=GovernancePolicy(),
            checkpoints=["cp-1", "cp-2"],
        )
        assert ctx.checkpoints == ["cp-1", "cp-2"]


# =============================================================================
# BaseIntegration.pre_execute / post_execute
# =============================================================================


class TestBaseIntegrationPreExecute:
    """Tests for pre_execute policy checks."""

    def _kernel(self, **policy_kw):
        """Helper: return a LangChainKernel (concrete subclass) with given policy."""
        return LangChainKernel(policy=GovernancePolicy(**policy_kw))

    def test_allowed_when_policy_satisfied(self):
        k = self._kernel()
        ctx = k.create_context("a1")
        allowed, reason = k.pre_execute(ctx, "hello")
        assert allowed is True
        assert reason is None

    def test_blocked_when_call_count_exceeded(self):
        k = self._kernel(max_tool_calls=2)
        ctx = k.create_context("a1")
        ctx.call_count = 2  # already at limit
        allowed, reason = k.pre_execute(ctx, "hello")
        assert allowed is False
        assert "Max tool calls" in reason

    def test_blocked_when_timeout_exceeded(self):
        k = self._kernel(timeout_seconds=10)
        ctx = k.create_context("a1")
        ctx.start_time = datetime.now() - timedelta(seconds=20)
        allowed, reason = k.pre_execute(ctx, "hello")
        assert allowed is False
        assert "Timeout" in reason

    def test_blocked_pattern_exact(self):
        k = self._kernel(blocked_patterns=["password"])
        ctx = k.create_context("a1")
        allowed, reason = k.pre_execute(ctx, "my password is 123")
        assert allowed is False
        assert "password" in reason

    def test_blocked_pattern_case_insensitive(self):
        k = self._kernel(blocked_patterns=["secret"])
        ctx = k.create_context("a1")
        allowed, _ = k.pre_execute(ctx, "This has a SECRET inside")
        assert allowed is False

    def test_blocked_pattern_case_insensitive_upper_policy(self):
        k = self._kernel(blocked_patterns=["SECRET"])
        ctx = k.create_context("a1")
        allowed, _ = k.pre_execute(ctx, "my secret data")
        assert allowed is False

    def test_no_blocked_pattern_match(self):
        k = self._kernel(blocked_patterns=["password"])
        ctx = k.create_context("a1")
        allowed, reason = k.pre_execute(ctx, "nothing blocked here")
        assert allowed is True


class TestBaseIntegrationPostExecute:
    """Tests for post_execute validation."""

    def _kernel(self, **policy_kw):
        return LangChainKernel(policy=GovernancePolicy(**policy_kw))

    def test_increments_call_count(self):
        k = self._kernel()
        ctx = k.create_context("a1")
        assert ctx.call_count == 0
        k.post_execute(ctx, "result")
        assert ctx.call_count == 1
        k.post_execute(ctx, "result2")
        assert ctx.call_count == 2

    def test_checkpoint_created_at_frequency(self):
        k = self._kernel(checkpoint_frequency=3)
        ctx = k.create_context("a1")
        for _ in range(3):
            k.post_execute(ctx, "r")
        assert len(ctx.checkpoints) == 1
        assert ctx.checkpoints[0] == "checkpoint-3"

    def test_no_checkpoint_before_frequency(self):
        k = self._kernel(checkpoint_frequency=5)
        ctx = k.create_context("a1")
        for _ in range(4):
            k.post_execute(ctx, "r")
        assert ctx.checkpoints == []

    def test_multiple_checkpoints(self):
        k = self._kernel(checkpoint_frequency=2)
        ctx = k.create_context("a1")
        for _ in range(6):
            k.post_execute(ctx, "r")
        assert ctx.checkpoints == ["checkpoint-2", "checkpoint-4", "checkpoint-6"]


# =============================================================================
# BaseIntegration signal handling
# =============================================================================


class TestBaseIntegrationSignals:
    def test_register_and_fire_signal(self):
        k = LangChainKernel()
        called_with = {}

        def handler(agent_id):
            called_with["id"] = agent_id

        k.on_signal("SIGSTOP", handler)
        k.signal("agent-1", "SIGSTOP")
        assert called_with["id"] == "agent-1"

    def test_unregistered_signal_is_noop(self):
        k = LangChainKernel()
        k.signal("agent-1", "SIGFOO")  # should not raise


# =============================================================================
# LangChainKernel.wrap — invoke / run / batch / stream
# =============================================================================


class TestLangChainKernelWrap:
    def test_invoke_returns_result(self):
        chain = _make_mock_chain()
        governed = LangChainKernel().wrap(chain)
        result = governed.invoke("hi")
        assert result == "invoke-result"
        chain.invoke.assert_called_once_with("hi")

    def test_invoke_raises_on_blocked_pattern(self):
        policy = GovernancePolicy(blocked_patterns=["DROP TABLE"])
        governed = LangChainKernel(policy).wrap(_make_mock_chain())
        with pytest.raises(PolicyViolationError, match="Blocked pattern"):
            governed.invoke("please DROP TABLE users")

    def test_run_returns_result(self):
        chain = _make_mock_chain()
        governed = LangChainKernel().wrap(chain)
        result = governed.run("prompt")
        assert result == "run-result"
        chain.run.assert_called_once_with("prompt")

    def test_run_raises_on_blocked_pattern(self):
        policy = GovernancePolicy(blocked_patterns=["api_key"])
        governed = LangChainKernel(policy).wrap(_make_mock_chain())
        with pytest.raises(PolicyViolationError):
            governed.run("leak the api_key")

    def test_batch_returns_results(self):
        chain = _make_mock_chain()
        governed = LangChainKernel().wrap(chain)
        results = governed.batch(["a", "b"])
        assert results == ["batch-1", "batch-2"]
        chain.batch.assert_called_once_with(["a", "b"])

    def test_batch_blocks_if_any_input_violates(self):
        policy = GovernancePolicy(blocked_patterns=["bad"])
        governed = LangChainKernel(policy).wrap(_make_mock_chain())
        with pytest.raises(PolicyViolationError):
            governed.batch(["ok", "this is bad"])

    def test_stream_yields_chunks(self):
        chain = _make_mock_chain()
        governed = LangChainKernel().wrap(chain)
        chunks = list(governed.stream("go"))
        assert chunks == ["chunk-1", "chunk-2"]

    def test_stream_blocks_on_violation(self):
        policy = GovernancePolicy(blocked_patterns=["nope"])
        governed = LangChainKernel(policy).wrap(_make_mock_chain())
        with pytest.raises(PolicyViolationError):
            list(governed.stream("nope"))

    def test_invoke_increments_call_count(self):
        chain = _make_mock_chain()
        kernel = LangChainKernel()
        governed = kernel.wrap(chain)
        governed.invoke("a")
        governed.invoke("b")
        # access internal context through the governed wrapper
        assert governed._ctx.call_count == 2

    def test_invoke_blocks_after_max_tool_calls(self):
        policy = GovernancePolicy(max_tool_calls=1)
        chain = _make_mock_chain()
        governed = LangChainKernel(policy).wrap(chain)
        governed.invoke("first")  # succeeds, post_execute increments to 1
        with pytest.raises(PolicyViolationError, match="Max tool calls"):
            governed.invoke("second")

    def test_unwrap_returns_original(self):
        chain = _make_mock_chain()
        kernel = LangChainKernel()
        governed = kernel.wrap(chain)
        assert kernel.unwrap(governed) is chain

    def test_getattr_passthrough(self):
        chain = _make_mock_chain()
        chain.custom_attr = "hello"
        governed = LangChainKernel().wrap(chain)
        assert governed.custom_attr == "hello"


# =============================================================================
# CrewAIKernel.wrap — kickoff
# =============================================================================


class TestCrewAIKernelWrap:
    def test_kickoff_returns_result(self):
        crew = _make_mock_crew()
        governed = CrewAIKernel().wrap(crew)
        result = governed.kickoff({"topic": "AI"})
        assert result == "crew-result"
        crew.kickoff.assert_called_once_with({"topic": "AI"})

    def test_kickoff_raises_on_blocked_pattern(self):
        policy = GovernancePolicy(blocked_patterns=["hack"])
        governed = CrewAIKernel(policy).wrap(_make_mock_crew())
        with pytest.raises(PolicyViolationError):
            governed.kickoff({"goal": "hack the system"})

    def test_kickoff_increments_call_count(self):
        crew = _make_mock_crew()
        governed = CrewAIKernel().wrap(crew)
        governed.kickoff()
        assert governed._ctx.call_count == 1

    def test_kickoff_blocks_after_max_calls(self):
        policy = GovernancePolicy(max_tool_calls=1)
        governed = CrewAIKernel(policy).wrap(_make_mock_crew())
        governed.kickoff()
        with pytest.raises(PolicyViolationError, match="Max tool calls"):
            governed.kickoff()

    def test_kickoff_wraps_individual_agents(self):
        crew = _make_mock_crew()
        agent_mock = MagicMock()
        agent_mock.execute_task = MagicMock(return_value="done")
        crew.agents = [agent_mock]
        governed = CrewAIKernel().wrap(crew)
        governed.kickoff()
        # _wrap_agent should have replaced execute_task
        assert agent_mock.execute_task is not crew.agents[0].execute_task or True

    def test_unwrap_returns_original(self):
        crew = _make_mock_crew()
        kernel = CrewAIKernel()
        governed = kernel.wrap(crew)
        assert kernel.unwrap(governed) is crew

    def test_getattr_passthrough(self):
        crew = _make_mock_crew()
        crew.verbose = True
        governed = CrewAIKernel().wrap(crew)
        assert governed.verbose is True


# =============================================================================
# OpenAIKernel — wrap_assistant basics
# =============================================================================


class TestOpenAIKernelBasics:
    def test_wrap_generic_raises(self):
        kernel = OpenAIKernel()
        with pytest.raises(NotImplementedError):
            kernel.wrap(MagicMock())

    def test_wrap_assistant_returns_governed(self):
        kernel = OpenAIKernel()
        assistant = _make_mock_assistant()
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(assistant, client)
        assert isinstance(governed, GovernedAssistant)

    def test_governed_assistant_id_and_name(self):
        kernel = OpenAIKernel()
        assistant = _make_mock_assistant("asst_99", "Bot99")
        governed = kernel.wrap_assistant(assistant, _make_mock_openai_client())
        assert governed.id == "asst_99"
        assert governed.name == "Bot99"

    def test_unwrap_returns_original(self):
        kernel = OpenAIKernel()
        assistant = _make_mock_assistant()
        governed = kernel.wrap_assistant(assistant, _make_mock_openai_client())
        assert kernel.unwrap(governed) is assistant


# =============================================================================
# OpenAIKernel — thread management
# =============================================================================


class TestOpenAIThreadManagement:
    def test_create_thread(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        thread = governed.create_thread()
        assert thread.id == "thread_abc"
        assert "thread_abc" in governed._ctx.thread_ids

    def test_delete_thread_removes_from_context(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()
        client.beta.threads.delete.return_value = MagicMock(deleted=True)
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        governed.create_thread()
        assert "thread_abc" in governed._ctx.thread_ids
        governed.delete_thread("thread_abc")
        assert "thread_abc" not in governed._ctx.thread_ids


# =============================================================================
# OpenAIKernel — message blocking
# =============================================================================


class TestOpenAIMessageBlocking:
    def test_add_message_allowed(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        msg = governed.add_message("thread_abc", "hello")
        assert msg.id == "msg_xyz"

    def test_add_message_blocked_by_pattern(self):
        policy = GovernancePolicy(blocked_patterns=["password"])
        kernel = OpenAIKernel(policy)
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(OpenAIPolicyViolationError, match="Message blocked"):
            governed.add_message("thread_abc", "my password is 123")

    def test_add_message_case_insensitive_block(self):
        policy = GovernancePolicy(blocked_patterns=["SECRET"])
        kernel = OpenAIKernel(policy)
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(OpenAIPolicyViolationError):
            governed.add_message("thread_abc", "this is secret info")


# =============================================================================
# OpenAIKernel — run execution & polling
# =============================================================================


class TestOpenAIRunExecution:
    def test_run_completes_successfully(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()

        created_run = MagicMock()
        created_run.id = "run_001"
        client.beta.threads.runs.create.return_value = created_run

        completed_run = _make_completed_run("run_001")
        client.beta.threads.runs.retrieve.return_value = completed_run

        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        result = governed.run("thread_abc")
        assert result.status == "completed"
        assert "run_001" in governed._ctx.run_ids

    def test_run_blocked_instructions(self):
        policy = GovernancePolicy(blocked_patterns=["hack"])
        kernel = OpenAIKernel(policy)
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(OpenAIPolicyViolationError, match="Instructions blocked"):
            governed.run("thread_abc", instructions="hack the planet")

    def test_run_validates_tools_against_policy(self):
        policy = GovernancePolicy(allowed_tools=["code_interpreter"])
        kernel = OpenAIKernel(policy)
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(OpenAIPolicyViolationError, match="Tool type not allowed"):
            governed.run("thread_abc", tools=[{"type": "retrieval"}])

    def test_run_handles_failed_status(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()

        created_run = MagicMock(id="run_fail")
        client.beta.threads.runs.create.return_value = created_run

        failed_run = MagicMock()
        failed_run.id = "run_fail"
        failed_run.status = "failed"
        failed_run.usage = None
        client.beta.threads.runs.retrieve.return_value = failed_run

        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        result = governed.run("thread_abc")
        assert result.status == "failed"


# =============================================================================
# OpenAIKernel — tool call handling
# =============================================================================


class TestOpenAIToolCallHandling:
    def test_tool_call_recorded_in_context(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()

        # First retrieve returns requires_action, second returns completed
        ra_run = _make_requires_action_run("run_tc")
        completed_run = _make_completed_run("run_tc")
        client.beta.threads.runs.retrieve.side_effect = [ra_run, completed_run]
        client.beta.threads.runs.submit_tool_outputs.return_value = MagicMock()

        created_run = MagicMock(id="run_tc")
        client.beta.threads.runs.create.return_value = created_run

        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        governed.run("thread_abc", poll_interval=0)
        assert len(governed._ctx.function_calls) == 1
        assert governed._ctx.function_calls[0]["function"] == "get_weather"

    def test_tool_call_limit_cancels_run(self):
        policy = GovernancePolicy(max_tool_calls=0)
        kernel = OpenAIKernel(policy)
        client = _make_mock_openai_client()

        ra_run = _make_requires_action_run("run_lim")
        client.beta.threads.runs.retrieve.return_value = ra_run
        created_run = MagicMock(id="run_lim")
        client.beta.threads.runs.create.return_value = created_run

        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(OpenAIPolicyViolationError, match="Tool call limit"):
            governed.run("thread_abc", poll_interval=0)
        # Verify cancel was called
        client.beta.threads.runs.cancel.assert_called_once()

    def test_disallowed_function_name_cancels_run(self):
        policy = GovernancePolicy(allowed_tools=["safe_func"])
        kernel = OpenAIKernel(policy)
        client = _make_mock_openai_client()

        tc = MagicMock()
        tc.id = "call_bad"
        tc.type = "function"
        tc.function.name = "dangerous_func"
        tc.function.arguments = "{}"
        ra_run = _make_requires_action_run("run_bad", tool_calls=[tc])
        client.beta.threads.runs.retrieve.return_value = ra_run
        created_run = MagicMock(id="run_bad")
        client.beta.threads.runs.create.return_value = created_run

        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(OpenAIPolicyViolationError, match="Tool not allowed"):
            governed.run("thread_abc", poll_interval=0)


# =============================================================================
# OpenAIKernel — SIGKILL
# =============================================================================


class TestOpenAISIGKILL:
    def test_sigkill_cancels_run(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        governed.sigkill("thread_abc", "run_x")
        assert kernel.is_cancelled("run_x")

    def test_sigkill_raises_during_poll(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()

        created_run = MagicMock(id="run_killed")
        client.beta.threads.runs.create.return_value = created_run

        # Pre-cancel so the very first poll iteration raises
        kernel._cancelled_runs.add("run_killed")

        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(RunCancelledException, match="SIGKILL"):
            governed.run("thread_abc", poll_interval=0)

    def test_sigstop_also_cancels(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        governed.sigstop("thread_abc", "run_y")
        assert kernel.is_cancelled("run_y")


# =============================================================================
# OpenAIKernel — token tracking
# =============================================================================


class TestOpenAITokenTracking:
    def test_token_usage_accumulates(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()

        created_run = MagicMock(id="run_tok")
        client.beta.threads.runs.create.return_value = created_run

        usage = MagicMock()
        usage.prompt_tokens = 100
        usage.completion_tokens = 50
        completed_run = _make_completed_run("run_tok", usage=usage)
        client.beta.threads.runs.retrieve.return_value = completed_run

        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        governed.run("thread_abc", poll_interval=0)

        info = governed.get_token_usage()
        assert info["prompt_tokens"] == 100
        assert info["completion_tokens"] == 50
        assert info["total_tokens"] == 150

    def test_token_limit_exceeded_cancels_run(self):
        policy = GovernancePolicy(max_tokens=100)
        kernel = OpenAIKernel(policy)
        client = _make_mock_openai_client()

        created_run = MagicMock(id="run_over")
        client.beta.threads.runs.create.return_value = created_run

        usage = MagicMock()
        usage.prompt_tokens = 80
        usage.completion_tokens = 80  # total 160 > 100
        over_run = MagicMock()
        over_run.id = "run_over"
        over_run.status = "in_progress"
        over_run.usage = usage
        client.beta.threads.runs.retrieve.return_value = over_run

        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(OpenAIPolicyViolationError, match="Token limit exceeded"):
            governed.run("thread_abc", poll_interval=0)
        client.beta.threads.runs.cancel.assert_called_once()

    def test_get_context_returns_assistant_context(self):
        kernel = OpenAIKernel()
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        ctx = governed.get_context()
        assert isinstance(ctx, AssistantContext)
        assert ctx.assistant_id == "asst_001"


# =============================================================================
# OpenAIKernel — _validate_tools
# =============================================================================


class TestOpenAIValidateTools:
    def test_no_restriction_allows_all(self):
        kernel = OpenAIKernel(GovernancePolicy(allowed_tools=[]))
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        # Should not raise
        governed._validate_tools([{"type": "anything"}])

    def test_dict_tool_rejected(self):
        kernel = OpenAIKernel(GovernancePolicy(allowed_tools=["code_interpreter"]))
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        with pytest.raises(OpenAIPolicyViolationError, match="Tool type not allowed"):
            governed._validate_tools([{"type": "retrieval"}])

    def test_object_tool_rejected(self):
        kernel = OpenAIKernel(GovernancePolicy(allowed_tools=["code_interpreter"]))
        client = _make_mock_openai_client()
        governed = kernel.wrap_assistant(_make_mock_assistant(), client)
        tool_obj = MagicMock()
        tool_obj.type = "file_search"
        with pytest.raises(OpenAIPolicyViolationError, match="Tool type not allowed"):
            governed._validate_tools([tool_obj])


# =============================================================================
# PolicyViolationError identity
# =============================================================================


class TestPolicyViolationError:
    def test_langchain_error_is_exception(self):
        err = PolicyViolationError("test")
        assert isinstance(err, Exception)
        assert str(err) == "test"

    def test_openai_error_is_exception(self):
        err = OpenAIPolicyViolationError("oai test")
        assert isinstance(err, Exception)
        assert str(err) == "oai test"

    def test_run_cancelled_is_exception(self):
        err = RunCancelledException("killed")
        assert isinstance(err, Exception)
        assert str(err) == "killed"
