"""
OpenAI Assistants Integration

Wraps OpenAI Assistants API with Agent OS governance.

Usage:
    from agent_os.integrations import OpenAIKernel
    from openai import OpenAI
    
    client = OpenAI()
    kernel = OpenAIKernel(policy="strict")
    
    # Create assistant as normal
    assistant = client.beta.assistants.create(
        name="Trading Bot",
        instructions="You analyze market data",
        model="gpt-4-turbo"
    )
    
    # Wrap for governance
    governed_assistant = kernel.wrap_assistant(assistant, client)
    
    # All runs are now governed!
    thread = governed_assistant.create_thread()
    governed_assistant.add_message(thread.id, "Analyze AAPL")
    run = governed_assistant.run(thread.id)  # Governed execution

Features:
- Pre-execution policy checks
- Tool call interception and validation
- Real-time run monitoring
- SIGKILL support (cancel run on violation)
- Full audit trail
"""

from typing import Any, Optional, Callable, Generator
from dataclasses import dataclass, field
from datetime import datetime
import time

from .base import BaseIntegration, GovernancePolicy, ExecutionContext


@dataclass
class AssistantContext(ExecutionContext):
    """Extended context for OpenAI Assistants"""
    assistant_id: str = ""
    thread_ids: list[str] = field(default_factory=list)
    run_ids: list[str] = field(default_factory=list)
    function_calls: list[dict] = field(default_factory=list)
    
    # Token tracking
    prompt_tokens: int = 0
    completion_tokens: int = 0


class OpenAIKernel(BaseIntegration):
    """
    OpenAI Assistants adapter for Agent OS.
    
    Provides governance for:
    - Assistant creation/modification
    - Thread management
    - Run execution
    - Tool/function calls
    - File operations
    
    Example:
        kernel = OpenAIKernel(policy=GovernancePolicy(
            max_tokens=10000,
            allowed_tools=["code_interpreter", "retrieval"],
            blocked_patterns=["password", "api_key", "secret"]
        ))
        
        governed = kernel.wrap_assistant(assistant, client)
        result = governed.run(thread_id)
    """
    
    def __init__(self, policy: Optional[GovernancePolicy] = None):
        super().__init__(policy)
        self._wrapped_assistants: dict[str, Any] = {}  # assistant_id -> original
        self._clients: dict[str, Any] = {}  # assistant_id -> client
        self._cancelled_runs: set[str] = set()
    
    def wrap(self, agent: Any) -> Any:
        """
        Generic wrap - routes to wrap_assistant.
        For API compatibility with other integrations.
        """
        raise NotImplementedError(
            "Use wrap_assistant(assistant, client) for OpenAI Assistants"
        )
    
    def wrap_assistant(self, assistant: Any, client: Any) -> "GovernedAssistant":
        """
        Wrap an OpenAI Assistant with governance.
        
        Args:
            assistant: OpenAI Assistant object
            client: OpenAI client instance
            
        Returns:
            GovernedAssistant with full governance
        """
        assistant_id = assistant.id
        ctx = AssistantContext(
            agent_id=assistant_id,
            session_id=f"oai-{int(time.time())}",
            policy=self.policy,
            assistant_id=assistant_id
        )
        self.contexts[assistant_id] = ctx
        self._wrapped_assistants[assistant_id] = assistant
        self._clients[assistant_id] = client
        
        return GovernedAssistant(
            assistant=assistant,
            client=client,
            kernel=self,
            ctx=ctx
        )
    
    def unwrap(self, governed_agent: Any) -> Any:
        """Get original assistant from wrapped version"""
        if isinstance(governed_agent, GovernedAssistant):
            return governed_agent._assistant
        return governed_agent
    
    def cancel_run(self, thread_id: str, run_id: str, client: Any):
        """Cancel a run (SIGKILL equivalent)"""
        self._cancelled_runs.add(run_id)
        try:
            client.beta.threads.runs.cancel(
                thread_id=thread_id,
                run_id=run_id
            )
        except Exception:
            pass  # Run may already be complete
    
    def is_cancelled(self, run_id: str) -> bool:
        """Check if a run was cancelled"""
        return run_id in self._cancelled_runs


class GovernedAssistant:
    """
    OpenAI Assistant wrapped with Agent OS governance.
    
    All API calls are intercepted for policy enforcement.
    """
    
    def __init__(
        self,
        assistant: Any,
        client: Any,
        kernel: OpenAIKernel,
        ctx: AssistantContext
    ):
        self._assistant = assistant
        self._client = client
        self._kernel = kernel
        self._ctx = ctx
    
    @property
    def id(self) -> str:
        """Assistant ID"""
        return self._assistant.id
    
    @property
    def name(self) -> str:
        """Assistant name"""
        return self._assistant.name
    
    # =========================================================================
    # Thread Management
    # =========================================================================
    
    def create_thread(self, **kwargs) -> Any:
        """Create a new thread for conversation"""
        thread = self._client.beta.threads.create(**kwargs)
        self._ctx.thread_ids.append(thread.id)
        return thread
    
    def get_thread(self, thread_id: str) -> Any:
        """Retrieve a thread"""
        return self._client.beta.threads.retrieve(thread_id)
    
    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread"""
        result = self._client.beta.threads.delete(thread_id)
        if thread_id in self._ctx.thread_ids:
            self._ctx.thread_ids.remove(thread_id)
        return result.deleted
    
    # =========================================================================
    # Message Management
    # =========================================================================
    
    def add_message(
        self,
        thread_id: str,
        content: str,
        role: str = "user",
        **kwargs
    ) -> Any:
        """
        Add a message to thread (with policy check).
        """
        # Pre-check: blocked patterns
        allowed, reason = self._kernel.pre_execute(self._ctx, content)
        if not allowed:
            raise PolicyViolationError(f"Message blocked: {reason}")
        
        message = self._client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content,
            **kwargs
        )
        return message
    
    def list_messages(self, thread_id: str, **kwargs) -> list:
        """List messages in a thread"""
        return self._client.beta.threads.messages.list(
            thread_id=thread_id,
            **kwargs
        )
    
    # =========================================================================
    # Run Execution (Core Governance)
    # =========================================================================
    
    def run(
        self,
        thread_id: str,
        instructions: Optional[str] = None,
        tools: Optional[list] = None,
        poll_interval: float = 1.0,
        **kwargs
    ) -> Any:
        """
        Execute a governed run.
        
        This is the primary method for executing the assistant.
        All tool calls and outputs are validated against policy.
        
        Args:
            thread_id: Thread to run on
            instructions: Optional override instructions
            tools: Optional tools to enable
            poll_interval: How often to check run status
            **kwargs: Additional run parameters
            
        Returns:
            Completed run object
            
        Raises:
            PolicyViolationError: If policy is violated
            RunCancelledException: If run was SIGKILL'd
        """
        # Pre-check
        if instructions:
            allowed, reason = self._kernel.pre_execute(self._ctx, instructions)
            if not allowed:
                raise PolicyViolationError(f"Instructions blocked: {reason}")
        
        # Validate tools against policy
        if tools:
            self._validate_tools(tools)
        
        # Create run
        run_kwargs = {
            "thread_id": thread_id,
            "assistant_id": self._assistant.id,
            **kwargs
        }
        if instructions:
            run_kwargs["instructions"] = instructions
        if tools:
            run_kwargs["tools"] = tools
        
        run = self._client.beta.threads.runs.create(**run_kwargs)
        self._ctx.run_ids.append(run.id)
        
        # Poll until complete (with governance checks)
        return self._poll_run(thread_id, run.id, poll_interval)
    
    def run_stream(
        self,
        thread_id: str,
        instructions: Optional[str] = None,
        **kwargs
    ) -> Generator:
        """
        Stream a governed run.
        
        Yields events as they arrive, with real-time policy checks.
        """
        # Pre-check
        if instructions:
            allowed, reason = self._kernel.pre_execute(self._ctx, instructions)
            if not allowed:
                raise PolicyViolationError(f"Instructions blocked: {reason}")
        
        # Create streaming run
        with self._client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=self._assistant.id,
            instructions=instructions,
            **kwargs
        ) as stream:
            for event in stream:
                # Check for cancellation
                if hasattr(event, 'data') and hasattr(event.data, 'id'):
                    if self._kernel.is_cancelled(event.data.id):
                        raise RunCancelledException("Run was cancelled (SIGKILL)")
                
                # Yield event
                yield event
    
    def _poll_run(
        self,
        thread_id: str,
        run_id: str,
        poll_interval: float
    ) -> Any:
        """
        Poll run status with governance checks.
        """
        while True:
            # Check for SIGKILL
            if self._kernel.is_cancelled(run_id):
                raise RunCancelledException("Run was cancelled (SIGKILL)")
            
            run = self._client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            # Update token counts
            if hasattr(run, 'usage') and run.usage:
                self._ctx.prompt_tokens += run.usage.prompt_tokens or 0
                self._ctx.completion_tokens += run.usage.completion_tokens or 0
                
                # Check token limit
                total = self._ctx.prompt_tokens + self._ctx.completion_tokens
                if total > self._kernel.policy.max_tokens:
                    self._kernel.cancel_run(thread_id, run_id, self._client)
                    raise PolicyViolationError(
                        f"Token limit exceeded: {total} > {self._kernel.policy.max_tokens}"
                    )
            
            # Handle different statuses
            if run.status == "completed":
                self._kernel.post_execute(self._ctx, run)
                return run
            
            elif run.status == "requires_action":
                # Tool calls need approval
                run = self._handle_tool_calls(thread_id, run)
            
            elif run.status in ["failed", "cancelled", "expired"]:
                return run
            
            elif run.status in ["queued", "in_progress"]:
                time.sleep(poll_interval)
            
            else:
                # Unknown status
                time.sleep(poll_interval)
    
    def _handle_tool_calls(self, thread_id: str, run: Any) -> Any:
        """
        Handle tool calls with policy validation.
        """
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        
        for tool_call in tool_calls:
            # Record tool call
            call_info = {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": tool_call.function.name if hasattr(tool_call, 'function') else None,
                "arguments": tool_call.function.arguments if hasattr(tool_call, 'function') else None,
                "timestamp": datetime.now().isoformat()
            }
            self._ctx.function_calls.append(call_info)
            self._ctx.tool_calls.append(call_info)
            
            # Check tool call count
            if len(self._ctx.tool_calls) > self._kernel.policy.max_tool_calls:
                self._kernel.cancel_run(thread_id, run.id, self._client)
                raise PolicyViolationError(
                    f"Tool call limit exceeded: {len(self._ctx.tool_calls)} > {self._kernel.policy.max_tool_calls}"
                )
            
            # Validate function name
            if hasattr(tool_call, 'function'):
                func_name = tool_call.function.name
                if self._kernel.policy.allowed_tools:
                    if func_name not in self._kernel.policy.allowed_tools:
                        self._kernel.cancel_run(thread_id, run.id, self._client)
                        raise PolicyViolationError(
                            f"Tool not allowed: {func_name}"
                        )
            
            # For now, we don't auto-execute - return placeholder
            # In production, you'd integrate with your tool execution
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": '{"status": "governed", "message": "Tool execution requires approval"}'
            })
        
        # Submit outputs
        return self._client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    
    def _validate_tools(self, tools: list):
        """Validate tools against policy"""
        if not self._kernel.policy.allowed_tools:
            return  # No restrictions
        
        for tool in tools:
            tool_type = tool.get("type") if isinstance(tool, dict) else getattr(tool, "type", None)
            if tool_type and tool_type not in self._kernel.policy.allowed_tools:
                raise PolicyViolationError(f"Tool type not allowed: {tool_type}")
    
    # =========================================================================
    # Signal Handling
    # =========================================================================
    
    def sigkill(self, thread_id: str, run_id: str):
        """
        Send SIGKILL to a running assistant.
        
        Immediately cancels the run.
        """
        self._kernel.cancel_run(thread_id, run_id, self._client)
    
    def sigstop(self, thread_id: str, run_id: str):
        """
        Send SIGSTOP to a running assistant.
        
        Note: OpenAI API doesn't support pause, so this cancels.
        """
        self._kernel.cancel_run(thread_id, run_id, self._client)
    
    # =========================================================================
    # Utility
    # =========================================================================
    
    def get_context(self) -> AssistantContext:
        """Get execution context with audit info"""
        return self._ctx
    
    def get_token_usage(self) -> dict:
        """Get token usage statistics"""
        return {
            "prompt_tokens": self._ctx.prompt_tokens,
            "completion_tokens": self._ctx.completion_tokens,
            "total_tokens": self._ctx.prompt_tokens + self._ctx.completion_tokens,
            "limit": self._kernel.policy.max_tokens
        }
    
    def __getattr__(self, name):
        """Passthrough for other assistant attributes"""
        return getattr(self._assistant, name)


class PolicyViolationError(Exception):
    """Raised when an assistant violates governance policy"""
    pass


class RunCancelledException(Exception):
    """Raised when a run is cancelled (SIGKILL)"""
    pass


# ============================================================================
# Convenience Functions
# ============================================================================

def wrap_assistant(
    assistant: Any,
    client: Any,
    policy: Optional[GovernancePolicy] = None
) -> GovernedAssistant:
    """
    Quick wrapper for OpenAI Assistants.
    
    Example:
        from agent_os.integrations.openai_adapter import wrap_assistant
        
        governed = wrap_assistant(my_assistant, openai_client)
        result = governed.run(thread_id)
    """
    return OpenAIKernel(policy).wrap_assistant(assistant, client)
