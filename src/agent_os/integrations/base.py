"""
Base Integration Interface

All framework adapters inherit from this base class.
"""

import fnmatch
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Union
from datetime import datetime


class PatternType(Enum):
    """Type of pattern matching for blocked_patterns."""
    SUBSTRING = "substring"
    REGEX = "regex"
    GLOB = "glob"


class GovernanceEventType(Enum):
    """Event types emitted by the governance layer."""
    POLICY_CHECK = "policy_check"
    POLICY_VIOLATION = "policy_violation"
    TOOL_CALL_BLOCKED = "tool_call_blocked"
    CHECKPOINT_CREATED = "checkpoint_created"
    DRIFT_DETECTED = "drift_detected"


@dataclass
class GovernancePolicy:
    """Policy configuration for governed agents"""
    max_tokens: int = 4096
    max_tool_calls: int = 10
    allowed_tools: list[str] = field(default_factory=list)
    blocked_patterns: list[Union[str, tuple[str, PatternType]]] = field(default_factory=list)
    require_human_approval: bool = False
    timeout_seconds: int = 300
    
    # Safety thresholds
    confidence_threshold: float = 0.8
    drift_threshold: float = 0.15
    
    # Audit settings
    log_all_calls: bool = True
    checkpoint_frequency: int = 5  # Every N calls
    
    # Concurrency limits
    max_concurrent: int = 10
    backpressure_threshold: int = 8  # Start slowing down at this level

    def __repr__(self) -> str:
        return (
            f"GovernancePolicy(max_tokens={self.max_tokens!r}, "
            f"max_tool_calls={self.max_tool_calls!r}, "
            f"require_human_approval={self.require_human_approval!r})"
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.max_tokens,
                self.max_tool_calls,
                tuple(self.allowed_tools),
                tuple(self.blocked_patterns),
                self.require_human_approval,
                self.timeout_seconds,
                self.confidence_threshold,
                self.drift_threshold,
                self.log_all_calls,
                self.checkpoint_frequency,
                self.max_concurrent,
                self.backpressure_threshold,
            )
        )

    def __post_init__(self):
        """Validate policy fields on construction."""
        self.validate()

    def validate(self):
        """Validate all policy fields and raise ValueError for invalid inputs."""
        # Validate positive integers (must be > 0)
        for field_name in (
            "max_tokens", "timeout_seconds",
            "max_concurrent", "backpressure_threshold", "checkpoint_frequency",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value <= 0:
                raise ValueError(
                    f"{field_name} must be a positive integer, got {value!r}"
                )

        # Validate non-negative integers (>= 0 allowed)
        for field_name in ("max_tool_calls",):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"{field_name} must be a non-negative integer, got {value!r}"
                )

        # Validate float thresholds are in [0.0, 1.0]
        for field_name in ("confidence_threshold", "drift_threshold"):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"{field_name} must be a float between 0.0 and 1.0, got {value!r}"
                )

        # Validate allowed_tools entries are strings
        if not isinstance(self.allowed_tools, list):
            raise ValueError(
                f"allowed_tools must be a list, got {type(self.allowed_tools).__name__}"
            )
        for i, tool in enumerate(self.allowed_tools):
            if not isinstance(tool, str):
                raise ValueError(
                    f"allowed_tools[{i}] must be a string, got {type(tool).__name__}: {tool!r}"
                )

        # Validate blocked_patterns entries and precompile regex/glob patterns
        if not isinstance(self.blocked_patterns, list):
            raise ValueError(
                f"blocked_patterns must be a list, got {type(self.blocked_patterns).__name__}"
            )
        self._compiled_patterns: list[tuple[str, PatternType, Optional[re.Pattern]]] = []
        for i, pattern in enumerate(self.blocked_patterns):
            if isinstance(pattern, str):
                self._compiled_patterns.append((pattern, PatternType.SUBSTRING, None))
            elif isinstance(pattern, tuple) and len(pattern) == 2:
                pat_str, pat_type = pattern
                if not isinstance(pat_str, str):
                    raise ValueError(
                        f"blocked_patterns[{i}][0] must be a string, got {type(pat_str).__name__}: {pat_str!r}"
                    )
                if not isinstance(pat_type, PatternType):
                    raise ValueError(
                        f"blocked_patterns[{i}][1] must be a PatternType, got {type(pat_type).__name__}: {pat_type!r}"
                    )
                compiled = None
                if pat_type == PatternType.REGEX:
                    try:
                        compiled = re.compile(pat_str, re.IGNORECASE)
                    except re.error as e:
                        raise ValueError(
                            f"blocked_patterns[{i}] has invalid regex '{pat_str}': {e}"
                        )
                elif pat_type == PatternType.GLOB:
                    try:
                        compiled = re.compile(fnmatch.translate(pat_str), re.IGNORECASE)
                    except re.error as e:
                        raise ValueError(
                            f"blocked_patterns[{i}] has invalid glob '{pat_str}': {e}"
                        )
                self._compiled_patterns.append((pat_str, pat_type, compiled))
            else:
                raise ValueError(
                    f"blocked_patterns[{i}] must be a string or (string, PatternType) tuple, got {type(pattern).__name__}: {pattern!r}"
                )

    def detect_conflicts(self) -> list[str]:
        """
        Detect conflicting or contradictory policy settings.

        Returns:
            A list of human-readable warning strings describing each conflict.
        """
        warnings: list[str] = []

        # Backpressure will never trigger if threshold is >= max_concurrent
        if self.backpressure_threshold >= self.max_concurrent:
            warnings.append(
                f"backpressure_threshold ({self.backpressure_threshold}) >= "
                f"max_concurrent ({self.max_concurrent}): backpressure will never trigger"
            )

        # Tools are allowed but max_tool_calls blocks any tool calls
        if self.max_tool_calls == 0 and self.allowed_tools:
            warnings.append(
                f"max_tool_calls is 0 but allowed_tools is non-empty "
                f"({self.allowed_tools}): tools are allowed but no calls permitted"
            )

        # Confidence checks effectively disabled
        if self.confidence_threshold == 0.0:
            warnings.append(
                "confidence_threshold is 0.0: effectively disables confidence checking"
            )

        # timeout_seconds is too low for reasonable execution (< 5s warning)
        if self.timeout_seconds < 5:
            warnings.append(
                f"timeout_seconds ({self.timeout_seconds}) is very low (under 5s), "
                f"may not allow reasonable execution time"
            )

        return warnings

    def matches_pattern(self, text: str) -> list[str]:
        """Return all blocked patterns that match the given text."""
        matches = []
        for pat_str, pat_type, compiled in self._compiled_patterns:
            if pat_type == PatternType.SUBSTRING:
                if pat_str.lower() in text.lower():
                    matches.append(pat_str)
            elif compiled is not None and compiled.search(text):
                matches.append(pat_str)
        return matches

    def to_yaml(self) -> str:
        """Serialize policy to YAML string."""
        import yaml

        data = {
            "max_tokens": self.max_tokens,
            "max_tool_calls": self.max_tool_calls,
            "allowed_tools": self.allowed_tools,
            "blocked_patterns": [
                {"pattern": p, "type": t.value} if t != PatternType.SUBSTRING
                else p
                for p, t, _ in self._compiled_patterns
            ],
            "require_human_approval": self.require_human_approval,
            "timeout_seconds": self.timeout_seconds,
            "confidence_threshold": self.confidence_threshold,
            "drift_threshold": self.drift_threshold,
            "log_all_calls": self.log_all_calls,
            "checkpoint_frequency": self.checkpoint_frequency,
            "max_concurrent": self.max_concurrent,
            "backpressure_threshold": self.backpressure_threshold,
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "GovernancePolicy":
        """Deserialize policy from YAML string."""
        import yaml

        data = yaml.safe_load(yaml_str)
        if not isinstance(data, dict):
            raise ValueError(f"Expected a YAML mapping, got {type(data).__name__}")

        # Convert blocked_patterns back to tuples where needed
        raw_patterns = data.get("blocked_patterns", [])
        patterns: list[Union[str, tuple[str, PatternType]]] = []
        for p in raw_patterns:
            if isinstance(p, str):
                patterns.append(p)
            elif isinstance(p, dict) and "pattern" in p and "type" in p:
                try:
                    pt = PatternType(p["type"])
                except ValueError:
                    raise ValueError(f"Unknown pattern type: {p['type']!r}")
                patterns.append((p["pattern"], pt))
            else:
                raise ValueError(f"Invalid blocked_pattern entry: {p!r}")
        data["blocked_patterns"] = patterns

        # Remove unknown keys
        valid_fields = {
            "max_tokens", "max_tool_calls", "allowed_tools", "blocked_patterns",
            "require_human_approval", "timeout_seconds", "confidence_threshold",
            "drift_threshold", "log_all_calls", "checkpoint_frequency",
            "max_concurrent", "backpressure_threshold",
        }
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    def save(self, filepath: str) -> None:
        """Save policy to a YAML file."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())

    @classmethod
    def load(cls, filepath: str) -> "GovernancePolicy":
        """Load policy from a YAML file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_yaml(f.read())

    def diff(self, other: "GovernancePolicy") -> dict[str, tuple[Any, Any]]:
        """Compare this policy with another, returning changed fields.

        Returns a dict mapping field names to (self_value, other_value) tuples
        for fields that differ between the two policies.
        """
        changes: dict[str, tuple[Any, Any]] = {}
        fields = [
            "max_tokens", "max_tool_calls", "allowed_tools", "blocked_patterns",
            "require_human_approval", "timeout_seconds", "confidence_threshold",
            "drift_threshold", "log_all_calls", "checkpoint_frequency",
            "max_concurrent", "backpressure_threshold",
        ]
        for f in fields:
            v_self = getattr(self, f)
            v_other = getattr(other, f)
            if v_self != v_other:
                changes[f] = (v_self, v_other)
        return changes

    def is_stricter_than(self, other: "GovernancePolicy") -> bool:
        """Return True if this policy is more restrictive than other.

        Stricter means: lower limits, higher thresholds, more blocked patterns,
        fewer allowed tools, and human approval required.
        """
        checks = [
            self.max_tokens <= other.max_tokens,
            self.max_tool_calls <= other.max_tool_calls,
            self.timeout_seconds <= other.timeout_seconds,
            self.max_concurrent <= other.max_concurrent,
            self.backpressure_threshold <= other.backpressure_threshold,
            self.confidence_threshold >= other.confidence_threshold,
            self.checkpoint_frequency <= other.checkpoint_frequency,
            len(self.blocked_patterns) >= len(other.blocked_patterns),
            (not other.require_human_approval) or self.require_human_approval,
        ]
        # allowed_tools: fewer allowed tools is stricter (unless both empty)
        if self.allowed_tools or other.allowed_tools:
            checks.append(
                len(self.allowed_tools) <= len(other.allowed_tools)
                if other.allowed_tools else True
            )
        # Must be at least one actual difference to be considered stricter
        has_difference = any([
            self.max_tokens < other.max_tokens,
            self.max_tool_calls < other.max_tool_calls,
            self.timeout_seconds < other.timeout_seconds,
            self.confidence_threshold > other.confidence_threshold,
            self.require_human_approval and not other.require_human_approval,
            len(self.blocked_patterns) > len(other.blocked_patterns),
            len(self.allowed_tools) < len(other.allowed_tools) if other.allowed_tools else False,
        ])
        return all(checks) and has_difference

    def format_diff(self, other: "GovernancePolicy") -> str:
        """Return a human-readable diff between this policy and other."""
        changes = self.diff(other)
        if not changes:
            return "Policies are identical."
        lines = ["Policy Diff:", "-" * 50]
        for field_name, (old, new) in changes.items():
            lines.append(f"  {field_name}: {old!r} -> {new!r}")
        lines.append("-" * 50)
        return "\n".join(lines)


_AGENT_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


@dataclass
class ExecutionContext:
    """Context passed through the governance layer"""
    agent_id: str
    session_id: str
    policy: GovernancePolicy
    start_time: datetime = field(default_factory=datetime.now)
    call_count: int = 0
    total_tokens: int = 0
    tool_calls: list[dict] = field(default_factory=list)
    checkpoints: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"ExecutionContext(agent_id={self.agent_id!r}, session_id={self.session_id!r})"

    def __post_init__(self):
        """Validate context fields on construction."""
        self.validate()

    def validate(self):
        """Validate all context fields and raise ValueError for invalid inputs."""
        # Validate agent_id is a non-empty string matching allowed pattern
        if not isinstance(self.agent_id, str) or not self.agent_id:
            raise ValueError(
                f"agent_id must be a non-empty string, got {self.agent_id!r}"
            )
        if not _AGENT_ID_RE.match(self.agent_id):
            raise ValueError(
                f"agent_id must match ^[a-zA-Z0-9_-]+$, got {self.agent_id!r}"
            )

        # Validate session_id is a non-empty string
        if not isinstance(self.session_id, str) or not self.session_id:
            raise ValueError(
                f"session_id must be a non-empty string, got {self.session_id!r}"
            )

        # Validate policy is a GovernancePolicy instance
        if not isinstance(self.policy, GovernancePolicy):
            raise ValueError(
                f"policy must be a GovernancePolicy instance, got {type(self.policy).__name__}"
            )

        # Validate non-negative integers
        for field_name in ("call_count", "total_tokens"):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"{field_name} must be a non-negative integer, got {value!r}"
                )

        # Validate checkpoints is a list of strings
        if not isinstance(self.checkpoints, list):
            raise ValueError(
                f"checkpoints must be a list, got {type(self.checkpoints).__name__}"
            )
        for i, cp in enumerate(self.checkpoints):
            if not isinstance(cp, str):
                raise ValueError(
                    f"checkpoints[{i}] must be a string, got {type(cp).__name__}: {cp!r}"
                )


# ── Abstract Tool Call Interceptor ────────────────────────────

@dataclass
class ToolCallRequest:
    """Vendor-neutral representation of a tool/function call."""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = ""
    agent_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"ToolCallRequest(tool_name={self.tool_name!r}, call_id={self.call_id!r})"


@dataclass
class ToolCallResult:
    """Result of intercepting a tool call."""
    allowed: bool
    reason: Optional[str] = None
    modified_arguments: Optional[Dict[str, Any]] = None  # For argument sanitization
    audit_entry: Optional[Dict[str, Any]] = None

    def __repr__(self) -> str:
        return f"ToolCallResult(allowed={self.allowed!r}, reason={self.reason!r})"


class ToolCallInterceptor(Protocol):
    """
    Abstract protocol for intercepting tool/function calls.

    Implement this to add custom governance logic across any framework.
    The same interceptor works with OpenAI, LangChain, CrewAI, etc.

    Example:
        class PIIInterceptor:
            def intercept(self, request: ToolCallRequest) -> ToolCallResult:
                if any(p in str(request.arguments) for p in ["ssn", "password"]):
                    return ToolCallResult(allowed=False, reason="PII detected")
                return ToolCallResult(allowed=True)
    """

    def intercept(self, request: ToolCallRequest) -> ToolCallResult:
        """Intercept a tool call and return allow/deny decision."""
        ...


class PolicyInterceptor:
    """
    Default interceptor that enforces GovernancePolicy rules.

    Checks:
    - Tool is in allowed_tools (if specified)
    - Arguments don't contain blocked patterns
    - Call count within limits
    """

    def __init__(self, policy: GovernancePolicy, context: Optional[ExecutionContext] = None):
        self.policy = policy
        self.context = context

    def intercept(self, request: ToolCallRequest) -> ToolCallResult:
        # Check allowed tools
        if self.policy.allowed_tools and request.tool_name not in self.policy.allowed_tools:
            return ToolCallResult(
                allowed=False,
                reason=f"Tool '{request.tool_name}' not in allowed list: {self.policy.allowed_tools}",
            )

        # Check blocked patterns
        args_str = str(request.arguments)
        matched = self.policy.matches_pattern(args_str)
        if matched:
            return ToolCallResult(
                allowed=False,
                reason=f"Blocked pattern '{matched[0]}' detected in tool arguments",
            )

        # Check call count
        if self.context and self.context.call_count >= self.policy.max_tool_calls:
            return ToolCallResult(
                allowed=False,
                reason=f"Max tool calls exceeded ({self.policy.max_tool_calls})",
            )

        return ToolCallResult(allowed=True)


class CompositeInterceptor:
    """Chain multiple interceptors. All must allow for the call to proceed."""

    def __init__(self, interceptors: Optional[List[Any]] = None):
        self.interceptors: List[Any] = interceptors or []

    def add(self, interceptor: Any) -> "CompositeInterceptor":
        self.interceptors.append(interceptor)
        return self

    def intercept(self, request: ToolCallRequest) -> ToolCallResult:
        for interceptor in self.interceptors:
            result = interceptor.intercept(request)
            if not result.allowed:
                return result
        return ToolCallResult(allowed=True)


# ── Bounded Concurrency ──────────────────────────────────────

class BoundedSemaphore:
    """
    Async-compatible bounded semaphore with backpressure.

    When concurrency exceeds backpressure_threshold, callers must wait.
    When it exceeds max_concurrent, requests are rejected.
    """

    def __init__(self, max_concurrent: int = 10, backpressure_threshold: int = 8):
        self.max_concurrent = max_concurrent
        self.backpressure_threshold = backpressure_threshold
        self._active = 0
        self._total_acquired = 0
        self._total_rejected = 0

    def try_acquire(self) -> tuple[bool, Optional[str]]:
        """
        Try to acquire a slot.

        Returns (acquired, reason).
        """
        if self._active >= self.max_concurrent:
            self._total_rejected += 1
            return False, f"Max concurrency reached ({self.max_concurrent})"
        self._active += 1
        self._total_acquired += 1
        return True, None

    def release(self) -> None:
        """Release a slot."""
        if self._active > 0:
            self._active -= 1

    @property
    def is_under_pressure(self) -> bool:
        """Check if backpressure threshold is reached."""
        return self._active >= self.backpressure_threshold

    @property
    def active(self) -> int:
        return self._active

    @property
    def available(self) -> int:
        return max(0, self.max_concurrent - self._active)

    def stats(self) -> Dict[str, Any]:
        return {
            "active": self._active,
            "max_concurrent": self.max_concurrent,
            "available": self.available,
            "under_pressure": self.is_under_pressure,
            "total_acquired": self._total_acquired,
            "total_rejected": self._total_rejected,
        }


class BaseIntegration(ABC):
    """
    Base class for framework integrations.
    
    Wraps any agent framework with Agent OS governance:
    - Pre-execution policy checks
    - Post-execution validation
    - Flight recording
    - Signal handling
    """
    
    def __init__(self, policy: Optional[GovernancePolicy] = None):
        self.policy = policy or GovernancePolicy()
        self.contexts: dict[str, ExecutionContext] = {}
        self._signal_handlers: dict[str, Callable] = {}
        self._event_listeners: dict[GovernanceEventType, list[Callable]] = {}
    
    @abstractmethod
    def wrap(self, agent: Any) -> Any:
        """
        Wrap an agent with governance.
        
        Returns a governed version of the agent that:
        - Enforces policy on all operations
        - Records execution to flight recorder
        - Responds to signals (SIGSTOP, SIGKILL, etc.)
        """
        pass
    
    @abstractmethod
    def unwrap(self, governed_agent: Any) -> Any:
        """Remove governance wrapper and return original agent"""
        pass
    
    def create_context(self, agent_id: str) -> ExecutionContext:
        """Create execution context for an agent"""
        from uuid import uuid4
        ctx = ExecutionContext(
            agent_id=agent_id,
            session_id=str(uuid4())[:8],
            policy=self.policy
        )
        self.contexts[agent_id] = ctx
        return ctx

    def on(self, event_type: GovernanceEventType, callback: Callable) -> None:
        """Register a callback for a governance event type."""
        self._event_listeners.setdefault(event_type, []).append(callback)

    def emit(self, event_type: GovernanceEventType, data: dict) -> None:
        """Fire all registered callbacks for an event type."""
        for cb in self._event_listeners.get(event_type, []):
            try:
                cb(data)
            except Exception:
                pass  # Don't let listener errors break governance flow
    
    def pre_execute(self, ctx: ExecutionContext, input_data: Any) -> tuple[bool, Optional[str]]:
        """
        Pre-execution policy check.
        
        Returns (allowed, reason) tuple.
        """
        event_base = {"agent_id": ctx.agent_id, "timestamp": datetime.now().isoformat()}

        self.emit(GovernanceEventType.POLICY_CHECK, {**event_base, "phase": "pre_execute"})

        # Check call count
        if ctx.call_count >= self.policy.max_tool_calls:
            reason = f"Max tool calls exceeded ({self.policy.max_tool_calls})"
            self.emit(GovernanceEventType.POLICY_VIOLATION, {**event_base, "reason": reason})
            return False, reason
        
        # Check timeout
        elapsed = (datetime.now() - ctx.start_time).total_seconds()
        if elapsed > self.policy.timeout_seconds:
            reason = f"Timeout exceeded ({self.policy.timeout_seconds}s)"
            self.emit(GovernanceEventType.POLICY_VIOLATION, {**event_base, "reason": reason})
            return False, reason
        
        # Check blocked patterns
        input_str = str(input_data)
        matched = self.policy.matches_pattern(input_str)
        if matched:
            reason = f"Blocked pattern detected: {matched[0]}"
            self.emit(GovernanceEventType.TOOL_CALL_BLOCKED, {**event_base, "reason": reason, "pattern": matched[0]})
            return False, reason
        
        return True, None
    
    def post_execute(self, ctx: ExecutionContext, output_data: Any) -> tuple[bool, Optional[str]]:
        """
        Post-execution validation.
        
        Returns (valid, reason) tuple.
        """
        ctx.call_count += 1
        
        # Checkpoint if needed
        if ctx.call_count % self.policy.checkpoint_frequency == 0:
            checkpoint_id = f"checkpoint-{ctx.call_count}"
            ctx.checkpoints.append(checkpoint_id)
            self.emit(GovernanceEventType.CHECKPOINT_CREATED, {
                "agent_id": ctx.agent_id,
                "timestamp": datetime.now().isoformat(),
                "checkpoint_id": checkpoint_id,
                "call_count": ctx.call_count,
            })
        
        return True, None
    
    def on_signal(self, signal: str, handler: Callable):
        """Register a signal handler"""
        self._signal_handlers[signal] = handler
    
    def signal(self, agent_id: str, signal: str):
        """Send signal to agent"""
        if signal in self._signal_handlers:
            self._signal_handlers[signal](agent_id)
