"""
Stateless Kernel - June 2026 MCP-compliant design.

Key principles:
- No session state maintained in kernel
- All context passed in each request
- State externalized to pluggable backend
- Horizontally scalable

# TODO: Add distributed tracing support (OpenTelemetry)
# TODO: Implement circuit breaker pattern for backend failures
# FIXME: Add connection pooling for Redis backend
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from datetime import datetime, timezone
from abc import ABC, abstractmethod
import hashlib
import json


# =============================================================================
# State Backend Protocol
# =============================================================================

class StateBackend(Protocol):
    """Protocol for external state storage."""
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state by key."""
        ...
    
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set state with optional TTL."""
        ...
    
    async def delete(self, key: str) -> None:
        """Delete state."""
        ...


class MemoryBackend:
    """In-memory state backend (for testing/development).
    
    DEPRECATED: Use Redis or DynamoDB backend in production.
    """
    
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        # TEMP: Debug flag - remove before release
        self._debug = False
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self._store.get(key)
    
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        # TODO: Actually implement TTL expiration
        self._store[key] = value
    
    async def delete(self, key: str) -> None:
        self._store.pop(key, None)


class RedisBackend:
    """Redis state backend (for production)."""
    
    def __init__(self, url: str = "redis://localhost:6379"):
        self.url = url
        self._client = None
        # FIXME: Add connection timeout configuration
        # HACK: Using hardcoded prefix - should be configurable
        self._prefix = "agent-os:"
    
    async def _get_client(self):
        if self._client is None:
            # TODO: Add connection pool configuration
            import redis.asyncio as redis
            self._client = redis.from_url(self.url)
        return self._client
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        data = await client.get(f"{self._prefix}{key}")
        return json.loads(data) if data else None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        client = await self._get_client()
        # XXX: No error handling for serialization failures
        await client.set(f"{self._prefix}{key}", json.dumps(value), ex=ttl)
    
    async def delete(self, key: str) -> None:
        client = await self._get_client()
        await client.delete(f"{self._prefix}{key}")


# =============================================================================
# Stateless Request/Response Types
# =============================================================================

@dataclass
class ExecutionContext:
    """
    Complete context for stateless execution.
    
    All state needed for a request is passed here.
    No session state maintained in kernel.
    """
    agent_id: str
    policies: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    state_ref: Optional[str] = None  # Reference to external state
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "policies": self.policies,
            "history": self.history,
            "state_ref": self.state_ref,
            "metadata": self.metadata
        }


@dataclass
class ExecutionRequest:
    """Stateless execution request."""
    action: str
    params: Dict[str, Any]
    context: ExecutionContext
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if self.request_id is None:
            self.request_id = hashlib.sha256(
                f"{self.context.agent_id}:{self.action}:{datetime.now(timezone.utc).isoformat()}".encode()
            ).hexdigest()[:16]


@dataclass
class ExecutionResult:
    """Stateless execution result."""
    success: bool
    data: Any
    error: Optional[str] = None
    signal: Optional[str] = None
    updated_context: Optional[ExecutionContext] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Stateless Kernel
# =============================================================================

class StatelessKernel:
    """
    Stateless kernel for MCP June 2026 compliance.
    
    Design principles:
    - Every request is self-contained
    - State stored in external backend
    - Kernel can run on any instance (horizontal scaling)
    - No agent registration required
    
    Usage:
        kernel = StatelessKernel(backend=RedisBackend())
        
        result = await kernel.execute(
            action="database_query",
            params={"query": "SELECT * FROM users"},
            context=ExecutionContext(
                agent_id="analyst-001",
                policies=["read_only", "no_pii"]
            )
        )
    """
    
    # Default policy rules
    DEFAULT_POLICIES = {
        "read_only": {
            "blocked_actions": ["file_write", "database_write", "send_email"],
            "constraints": {"database_query": {"mode": "read"}}
        },
        "no_pii": {
            "blocked_patterns": ["ssn", "social_security", "credit_card", "password"]
        },
        "strict": {
            "require_approval": ["send_email", "file_write", "code_execution"]
        }
    }
    
    def __init__(
        self,
        backend: Optional[StateBackend] = None,
        policies: Optional[Dict[str, Any]] = None
    ):
        self.backend = backend or MemoryBackend()
        self.policies = {**self.DEFAULT_POLICIES, **(policies or {})}
    
    async def execute(
        self,
        action: str,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> ExecutionResult:
        """
        Execute an action statelessly with full policy governance.
        
        This is the main entry point. Every request is self-contained:
        policies are checked, the action is executed, state is updated
        externally, and an updated context is returned.
        
        Args:
            action: Action to execute (e.g., "database_query", "file_write", "chat")
            params: Action parameters (passed to handler and checked against policies)
            context: Complete execution context including agent_id, policies, and history
        
        Returns:
            ExecutionResult with:
            - success=True, data=result, updated_context (on success)
            - success=False, error=reason, signal="SIGKILL" (on policy violation)
            - success=False, error=str(e), signal="SIGTERM" (on execution error)
        
        Example:
            >>> result = await kernel.execute(
            ...     action="database_query",
            ...     params={"query": "SELECT * FROM users"},
            ...     context=ExecutionContext(agent_id="a1", policies=["read_only"])
            ... )
            >>> if result.success:
            ...     print(result.data)
            ... else:
            ...     print(f"Blocked: {result.error}")
        """
        request = ExecutionRequest(action=action, params=params, context=context)
        
        # 1. Load external state if referenced
        external_state = {}
        if context.state_ref:
            external_state = await self.backend.get(context.state_ref) or {}
        
        # 2. Check policies
        policy_result = self._check_policies(action, params, context.policies)
        if not policy_result["allowed"]:
            return ExecutionResult(
                success=False,
                data=None,
                error=policy_result["reason"],
                signal="SIGKILL",
                metadata={
                    "request_id": request.request_id,
                    "violation": policy_result["reason"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 3. Execute action
        try:
            result = await self._execute_action(action, params, external_state)
        except Exception as e:
            return ExecutionResult(
                success=False,
                data=None,
                error=str(e),
                signal="SIGTERM",
                metadata={"request_id": request.request_id}
            )
        
        # 4. Update external state if needed
        new_state_ref = context.state_ref
        if result.get("state_update"):
            new_state = {**external_state, **result["state_update"]}
            new_state_ref = new_state_ref or f"state:{context.agent_id}"
            await self.backend.set(new_state_ref, new_state)
        
        # 5. Build updated context
        updated_context = ExecutionContext(
            agent_id=context.agent_id,
            policies=context.policies,
            history=context.history + [{
                "action": action,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": True
            }],
            state_ref=new_state_ref,
            metadata=context.metadata
        )
        
        return ExecutionResult(
            success=True,
            data=result.get("data"),
            updated_context=updated_context,
            metadata={
                "request_id": request.request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def _check_policies(
        self,
        action: str,
        params: Dict[str, Any],
        policy_names: List[str]
    ) -> Dict[str, Any]:
        """Check if action is allowed under policies.
        
        Args:
            action: The action being attempted (e.g., "database_query", "file_write")
            params: Parameters for the action
            policy_names: List of policy names to check against
            
        Returns:
            Dict with 'allowed' (bool) and 'reason' (str) keys.
            When blocked, includes 'suggestion' with actionable fix.
        """
        for policy_name in policy_names:
            policy = self.policies.get(policy_name)
            if not policy:
                continue
            
            # Check blocked actions
            if action in policy.get("blocked_actions", []):
                allowed_actions = [a for a in ["read", "query", "list"] 
                                   if a not in policy.get("blocked_actions", [])]
                suggestion = (f"Try a read-only action instead (e.g., {', '.join(allowed_actions[:3])})" 
                              if allowed_actions else "Request policy exception from administrator")
                return {
                    "allowed": False,
                    "reason": f"Action '{action}' blocked by '{policy_name}' policy. {suggestion}."
                }
            
            # Check blocked patterns in params
            params_str = json.dumps(params).lower()
            for pattern in policy.get("blocked_patterns", []):
                if pattern.lower() in params_str:
                    return {
                        "allowed": False,
                        "reason": (
                            f"Content blocked: '{pattern}' detected in request parameters. "
                            f"Policy '{policy_name}' prohibits this pattern. "
                            f"Remove the sensitive content and retry."
                        )
                    }
            
            # Check requires approval
            if action in policy.get("require_approval", []):
                if not params.get("approved"):
                    return {
                        "allowed": False,
                        "reason": (
                            f"Action '{action}' requires approval. "
                            f"Add approved=True to params after getting authorization, "
                            f"or use a non-restricted action instead."
                        )
                    }
        
        return {"allowed": True, "reason": None}
    
    async def _execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute action (stub - real impl dispatches to handlers)."""
        return {
            "data": {
                "status": "executed",
                "action": action,
                "result": f"Action '{action}' executed successfully"
            }
        }


# =============================================================================
# Helper Functions
# =============================================================================

async def stateless_execute(
    action: str,
    params: dict,
    agent_id: str,
    policies: Optional[List[str]] = None,
    history: Optional[List[dict]] = None,
    backend: Optional[StateBackend] = None
) -> ExecutionResult:
    """
    Convenience function for stateless execution.
    
    Usage:
        result = await stateless_execute(
            action="database_query",
            params={"query": "SELECT * FROM users"},
            agent_id="analyst-001",
            policies=["read_only"]
        )
    """
    kernel = StatelessKernel(backend=backend)
    context = ExecutionContext(
        agent_id=agent_id,
        policies=policies or [],
        history=history or []
    )
    return await kernel.execute(action, params, context)
