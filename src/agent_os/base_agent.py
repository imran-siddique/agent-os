"""
Base Agent Module - Reusable base classes for Agent OS agents.

Provides a consistent pattern for building agents that run under
the Agent OS kernel with policy governance, audit logging, and
tool integration.

Example:
    >>> from agent_os.base_agent import BaseAgent, AgentConfig
    >>> 
    >>> class MyAgent(BaseAgent):
    ...     async def run(self, task: str) -> ExecutionResult:
    ...         return await self._execute("process", {"task": task})
    >>> 
    >>> agent = MyAgent(AgentConfig(agent_id="my-agent", policies=["read_only"]))
    >>> result = await agent.run("hello")
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from uuid import uuid4

from agent_os.stateless import (
    StatelessKernel,
    ExecutionContext,
    ExecutionResult,
    MemoryBackend,
    StateBackend,
)


class PolicyDecision(Enum):
    """Result of policy evaluation."""
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"  # Allow but log for review
    # TODO: Add ESCALATE decision for human-in-the-loop scenarios
    # TODO: Add DEFER decision for async policy evaluation


@dataclass
class AgentConfig:
    """Configuration for an agent instance.
    
    Attributes:
        agent_id: Unique identifier for this agent instance
        policies: List of policy names to apply (e.g., ["read_only", "no_pii"])
        metadata: Additional metadata for the agent
        state_backend: Optional custom state backend (defaults to in-memory)
    """
    agent_id: str
    policies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    state_backend: Optional[StateBackend] = None
    # FIXME: Add validation for agent_id format (should be alphanumeric with dashes)
    # TODO: Support loading config from YAML/JSON file

    def __repr__(self) -> str:
        return f"AgentConfig(agent_id={self.agent_id!r}, policies={self.policies!r})"


@dataclass
class AuditEntry:
    """An entry in the agent's audit log."""
    timestamp: datetime
    agent_id: str
    request_id: str
    action: str
    params: Dict[str, Any]
    decision: PolicyDecision
    result_success: Optional[bool] = None
    error: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f"AuditEntry(agent_id={self.agent_id!r}, action={self.action!r}, "
            f"decision={self.decision!r})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "request_id": self.request_id,
            "action": self.action,
            "params_keys": list(self.params.keys()),  # Don't log full params
            "decision": self.decision.value,
            "result_success": self.result_success,
            "error": self.error,
        }


class BaseAgent(ABC):
    """Abstract base class for Agent OS agents.
    
    Provides:
    - Kernel integration with policy enforcement
    - Execution context management
    - Audit logging
    - Common helper methods
    
    Subclasses must implement the `run` method which defines
    the agent's main task.
    
    Example:
        >>> class GreeterAgent(BaseAgent):
        ...     async def run(self, name: str) -> ExecutionResult:
        ...         result = await self._execute(
        ...             action="greet",
        ...             params={"name": name, "output": f"Hello, {name}!"}
        ...         )
        ...         return result
        >>> 
        >>> agent = GreeterAgent(AgentConfig(agent_id="greeter"))
        >>> result = await agent.run("World")
        >>> print(result.data)  # "Hello, World!"
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the agent.
        
        Args:
            config: Agent configuration including ID, policies, and backend
        """
        self._config = config
        self._kernel = StatelessKernel(
            backend=config.state_backend or MemoryBackend()
        )
        self._audit_log: List[AuditEntry] = []
        # HACK: Hardcoded max audit log size - should be configurable
        self._max_audit_entries = 10000
    
    @property
    def agent_id(self) -> str:
        """Get the agent's unique identifier."""
        return self._config.agent_id
    
    @property
    def policies(self) -> List[str]:
        """Get the agent's active policies."""
        return self._config.policies.copy()
    
    def _new_context(self, **extra_metadata) -> ExecutionContext:
        """Create a new execution context for a request.
        
        Args:
            **extra_metadata: Additional metadata to include
            
        Returns:
            Fresh ExecutionContext with agent's default settings
        """
        # XXX: Potential memory leak if metadata contains large objects
        metadata = {**self._config.metadata, **extra_metadata}
        return ExecutionContext(
            agent_id=self._config.agent_id,
            policies=self._config.policies.copy(),
            metadata=metadata,
        )
    
    async def _execute(
        self,
        action: str,
        params: Dict[str, Any],
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        """Execute an action through the kernel with policy checks.
        
        This is the primary method for agents to perform actions.
        All actions are:
        1. Checked against configured policies
        2. Logged for audit
        3. Executed through the kernel
        
        Args:
            action: Name of the action to execute
            params: Parameters for the action
            context: Optional custom context (uses default if None)
            
        Returns:
            ExecutionResult with success status, data, and any errors
        """
        ctx = context or self._new_context()
        request_id = str(uuid4())[:16]
        
        # Create audit entry
        audit = AuditEntry(
            timestamp=datetime.now(timezone.utc),
            agent_id=self._config.agent_id,
            request_id=request_id,
            action=action,
            params=params,
            decision=PolicyDecision.ALLOW,  # Will be updated
        )
        
        # Execute through kernel
        result = await self._kernel.execute(action, params, ctx)
        
        # Update audit entry with result
        if result.signal == "SIGKILL":
            audit.decision = PolicyDecision.DENY
        audit.result_success = result.success
        audit.error = result.error
        
        self._audit_log.append(audit)
        
        return result
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the agent's audit log.
        
        Returns:
            List of audit entries as dictionaries
        """
        return [entry.to_dict() for entry in self._audit_log]
    
    def clear_audit_log(self) -> None:
        """Clear the agent's audit log."""
        self._audit_log.clear()
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> ExecutionResult:
        """Run the agent's main task.
        
        Subclasses must implement this method to define the agent's
        primary functionality.
        
        Returns:
            ExecutionResult with the outcome of the task
        """
        pass


class ToolUsingAgent(BaseAgent):
    """Base class for agents that use registered tools from ATR.
    
    Extends BaseAgent with tool discovery and execution capabilities.
    Tools are executed through the kernel for policy enforcement.
    
    Example:
        >>> class AnalysisAgent(ToolUsingAgent):
        ...     async def run(self, data: str) -> ExecutionResult:
        ...         # Use registered tools
        ...         parsed = await self._use_tool("json_parser", {"text": data})
        ...         return parsed
    """
    
    def __init__(self, config: AgentConfig, tools: Optional[List[str]] = None):
        """Initialize the tool-using agent.
        
        Args:
            config: Agent configuration
            tools: Optional list of tool names this agent is allowed to use
        """
        super().__init__(config)
        self._allowed_tools = set(tools) if tools else None
    
    async def _use_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
    ) -> ExecutionResult:
        """Use a registered tool through the kernel.
        
        Args:
            tool_name: Name of the tool to use
            params: Parameters to pass to the tool
            
        Returns:
            ExecutionResult from tool execution
        """
        # Check tool allowlist if configured
        if self._allowed_tools and tool_name not in self._allowed_tools:
            return ExecutionResult(
                success=False,
                data=None,
                error=f"Tool '{tool_name}' not in allowed tools list",
            )
        
        # Execute through kernel
        return await self._execute(
            action=f"tool:{tool_name}",
            params=params,
        )
    
    def list_allowed_tools(self) -> Optional[List[str]]:
        """Get list of allowed tools, or None if all tools allowed."""
        return list(self._allowed_tools) if self._allowed_tools else None


# Type variable for generic agent results
T = TypeVar("T")


@dataclass
class TypedResult(Generic[T]):
    """A typed wrapper for execution results.
    
    Useful when you want type hints on the result data.
    """
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def from_execution_result(
        cls,
        result: ExecutionResult,
        transform: Optional[Callable[[Any], T]] = None,
    ) -> "TypedResult[T]":
        """Create from an ExecutionResult with optional transformation."""
        data = None
        if result.success and result.data is not None:
            data = transform(result.data) if transform else result.data
        return cls(
            success=result.success,
            data=data,
            error=result.error,
        )
