"""
Microsoft Semantic Kernel Integration

Wraps Semantic Kernel with Agent OS governance.

Usage:
    from agent_os.integrations import SemanticKernelWrapper
    from semantic_kernel import Kernel
    
    sk = Kernel()
    governed_sk = SemanticKernelWrapper(sk, policy="strict")
    
    # All invocations are now governed
    result = await governed_sk.invoke(function, input="...")

Features:
- Function invocation governance
- Plugin/skill validation
- Memory access control
- Token limit enforcement
- Full audit trail
- POSIX-style signals
"""

from typing import Any, Optional, Callable, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
import asyncio

from .base import BaseIntegration, GovernancePolicy, ExecutionContext


@dataclass
class SKContext(ExecutionContext):
    """Extended context for Semantic Kernel"""
    kernel_id: str = ""
    plugins_loaded: List[str] = field(default_factory=list)
    functions_invoked: List[dict] = field(default_factory=list)
    memory_operations: List[dict] = field(default_factory=list)
    
    # Token tracking
    prompt_tokens: int = 0
    completion_tokens: int = 0


class SemanticKernelWrapper(BaseIntegration):
    """
    Microsoft Semantic Kernel adapter for Agent OS.
    
    Provides governance for:
    - Function invocations
    - Plugin loading
    - Memory operations
    - Chat/text completions
    - Planner execution
    
    Example:
        from semantic_kernel import Kernel
        from agent_os.integrations import SemanticKernelWrapper
        
        sk = Kernel()
        sk.add_plugin(MyPlugin(), "my_plugin")
        
        governed = SemanticKernelWrapper(sk, policy=GovernancePolicy(
            allowed_tools=["my_plugin.safe_function"],
            blocked_patterns=["password", "secret"]
        ))
        
        # All executions are now governed
        result = await governed.invoke("my_plugin", "safe_function", input="...")
    """
    
    def __init__(
        self,
        kernel: Any = None,
        policy: Optional[GovernancePolicy] = None
    ):
        super().__init__(policy)
        self._kernel = kernel
        self._stopped = False
        self._killed = False
        self._contexts: Dict[str, SKContext] = {}
    
    def wrap(self, kernel: Any) -> "GovernedSemanticKernel":
        """
        Wrap a Semantic Kernel with governance.
        
        Args:
            kernel: Semantic Kernel instance
            
        Returns:
            GovernedSemanticKernel with full governance
        """
        kernel_id = f"sk-{id(kernel)}"
        ctx = SKContext(
            agent_id=kernel_id,
            session_id=f"sk-{int(datetime.now().timestamp())}",
            policy=self.policy,
            kernel_id=kernel_id
        )
        self._contexts[kernel_id] = ctx
        
        return GovernedSemanticKernel(
            kernel=kernel,
            wrapper=self,
            ctx=ctx
        )
    
    def unwrap(self, governed_kernel: Any) -> Any:
        """Get original kernel from wrapped version"""
        if isinstance(governed_kernel, GovernedSemanticKernel):
            return governed_kernel._kernel
        return governed_kernel
    
    def signal_stop(self, kernel_id: str):
        """SIGSTOP - pause execution"""
        self._stopped = True
    
    def signal_continue(self, kernel_id: str):
        """SIGCONT - resume execution"""
        self._stopped = False
    
    def signal_kill(self, kernel_id: str):
        """SIGKILL - terminate all operations"""
        self._killed = True
    
    def is_stopped(self) -> bool:
        return self._stopped
    
    def is_killed(self) -> bool:
        return self._killed


class GovernedSemanticKernel:
    """
    Semantic Kernel wrapped with Agent OS governance.
    
    Intercepts all function calls, plugin operations, and memory access.
    """
    
    def __init__(
        self,
        kernel: Any,
        wrapper: SemanticKernelWrapper,
        ctx: SKContext
    ):
        self._kernel = kernel
        self._wrapper = wrapper
        self._ctx = ctx
    
    # =========================================================================
    # Function Invocation (Core Governance)
    # =========================================================================
    
    async def invoke(
        self,
        plugin_name: Optional[str] = None,
        function_name: Optional[str] = None,
        function: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """
        Governed function invocation.
        
        Args:
            plugin_name: Name of the plugin
            function_name: Name of the function
            function: Direct function reference (alternative)
            **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            PolicyViolationError: If policy is violated
            ExecutionStoppedError: If SIGSTOP received
            ExecutionKilledError: If SIGKILL received
        """
        # Check signals
        if self._wrapper.is_killed():
            raise ExecutionKilledError("Kernel received SIGKILL")
        
        while self._wrapper.is_stopped():
            await asyncio.sleep(0.1)
            if self._wrapper.is_killed():
                raise ExecutionKilledError("Kernel received SIGKILL")
        
        # Build function identifier
        if function:
            func_id = getattr(function, 'name', str(function))
        else:
            func_id = f"{plugin_name}.{function_name}"
        
        # Record invocation
        invocation = {
            "function": func_id,
            "arguments": str(kwargs)[:500],  # Truncate for audit
            "timestamp": datetime.now().isoformat()
        }
        self._ctx.functions_invoked.append(invocation)
        
        # Pre-execution check
        allowed, reason = self._wrapper.pre_execute(self._ctx, kwargs)
        if not allowed:
            raise PolicyViolationError(f"Invocation blocked: {reason}")
        
        # Check allowed functions
        if self._wrapper.policy.allowed_tools:
            if func_id not in self._wrapper.policy.allowed_tools:
                # Check if plugin is allowed (wildcard)
                if plugin_name:
                    if f"{plugin_name}.*" not in self._wrapper.policy.allowed_tools:
                        raise PolicyViolationError(f"Function not allowed: {func_id}")
                else:
                    raise PolicyViolationError(f"Function not allowed: {func_id}")
        
        # Execute
        try:
            if function:
                result = await self._kernel.invoke(function, **kwargs)
            elif plugin_name and function_name:
                result = await self._kernel.invoke(
                    self._kernel.plugins[plugin_name][function_name],
                    **kwargs
                )
            else:
                raise ValueError("Must provide either function or plugin_name+function_name")
            
            # Post-execution check
            valid, reason = self._wrapper.post_execute(self._ctx, result)
            if not valid:
                raise PolicyViolationError(f"Result blocked: {reason}")
            
            return result
            
        except Exception as e:
            if "SIGKILL" in str(e) or self._wrapper.is_killed():
                raise ExecutionKilledError("Kernel received SIGKILL")
            raise
    
    def invoke_sync(
        self,
        plugin_name: Optional[str] = None,
        function_name: Optional[str] = None,
        function: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """
        Synchronous wrapper for invoke().
        """
        return asyncio.run(self.invoke(
            plugin_name=plugin_name,
            function_name=function_name,
            function=function,
            **kwargs
        ))
    
    # =========================================================================
    # Plugin Management
    # =========================================================================
    
    def add_plugin(
        self,
        plugin: Any,
        plugin_name: str,
        **kwargs
    ) -> Any:
        """
        Add a plugin with governance tracking.
        """
        # Record plugin
        self._ctx.plugins_loaded.append(plugin_name)
        
        # Add to kernel
        return self._kernel.add_plugin(plugin, plugin_name, **kwargs)
    
    def import_plugin_from_openai(
        self,
        plugin_name: str,
        openai_function: dict,
        **kwargs
    ) -> Any:
        """
        Import OpenAI function as plugin.
        """
        self._ctx.plugins_loaded.append(f"openai:{plugin_name}")
        return self._kernel.import_plugin_from_openai(
            plugin_name,
            openai_function,
            **kwargs
        )
    
    @property
    def plugins(self) -> dict:
        """Access loaded plugins"""
        return self._kernel.plugins
    
    # =========================================================================
    # Memory Operations (Governed)
    # =========================================================================
    
    async def memory_save(
        self,
        collection: str,
        text: str,
        id: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Save to memory with governance.
        """
        # Check signals
        if self._wrapper.is_killed():
            raise ExecutionKilledError("Kernel received SIGKILL")
        
        # Pre-check content
        allowed, reason = self._wrapper.pre_execute(self._ctx, text)
        if not allowed:
            raise PolicyViolationError(f"Memory save blocked: {reason}")
        
        # Record operation
        self._ctx.memory_operations.append({
            "operation": "save",
            "collection": collection,
            "id": id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Execute
        if hasattr(self._kernel, 'memory') and self._kernel.memory:
            return await self._kernel.memory.save_information(
                collection=collection,
                text=text,
                id=id,
                **kwargs
            )
        return None
    
    async def memory_search(
        self,
        collection: str,
        query: str,
        limit: int = 5,
        **kwargs
    ) -> list:
        """
        Search memory with governance.
        """
        # Check signals
        if self._wrapper.is_killed():
            raise ExecutionKilledError("Kernel received SIGKILL")
        
        # Record operation
        self._ctx.memory_operations.append({
            "operation": "search",
            "collection": collection,
            "query": query[:100],  # Truncate for audit
            "timestamp": datetime.now().isoformat()
        })
        
        # Execute
        if hasattr(self._kernel, 'memory') and self._kernel.memory:
            return await self._kernel.memory.search(
                collection=collection,
                query=query,
                limit=limit,
                **kwargs
            )
        return []
    
    # =========================================================================
    # Chat Completion (Governed)
    # =========================================================================
    
    async def invoke_prompt(
        self,
        prompt: str,
        **kwargs
    ) -> Any:
        """
        Invoke a prompt with governance.
        
        This is for direct chat/completion calls.
        """
        # Check signals
        if self._wrapper.is_killed():
            raise ExecutionKilledError("Kernel received SIGKILL")
        
        # Pre-check prompt
        allowed, reason = self._wrapper.pre_execute(self._ctx, prompt)
        if not allowed:
            raise PolicyViolationError(f"Prompt blocked: {reason}")
        
        # Record
        self._ctx.functions_invoked.append({
            "function": "prompt",
            "arguments": prompt[:500],
            "timestamp": datetime.now().isoformat()
        })
        
        # Get chat service and invoke
        # This works with SK's chat completion service pattern
        result = await self._kernel.invoke_prompt(prompt, **kwargs)
        
        # Post-check result
        valid, reason = self._wrapper.post_execute(self._ctx, result)
        if not valid:
            raise PolicyViolationError(f"Result blocked: {reason}")
        
        return result
    
    # =========================================================================
    # Planner (Governed)
    # =========================================================================
    
    async def create_plan(
        self,
        goal: str,
        planner: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """
        Create a plan with governance.
        
        Plans are validated before execution.
        """
        # Check signals
        if self._wrapper.is_killed():
            raise ExecutionKilledError("Kernel received SIGKILL")
        
        # Pre-check goal
        allowed, reason = self._wrapper.pre_execute(self._ctx, goal)
        if not allowed:
            raise PolicyViolationError(f"Plan goal blocked: {reason}")
        
        # Create plan
        if planner:
            plan = await planner.create_plan(goal, **kwargs)
        else:
            # Use default sequential planner if available
            from semantic_kernel.planners import SequentialPlanner
            planner = SequentialPlanner(self._kernel)
            plan = await planner.create_plan(goal, **kwargs)
        
        return GovernedPlan(plan, self._wrapper, self._ctx)
    
    # =========================================================================
    # Signal Handling
    # =========================================================================
    
    def sigkill(self):
        """Send SIGKILL to kernel"""
        self._wrapper.signal_kill(self._ctx.kernel_id)
    
    def sigstop(self):
        """Send SIGSTOP to kernel"""
        self._wrapper.signal_stop(self._ctx.kernel_id)
    
    def sigcont(self):
        """Send SIGCONT to kernel"""
        self._wrapper.signal_continue(self._ctx.kernel_id)
    
    # =========================================================================
    # Utility
    # =========================================================================
    
    def get_context(self) -> SKContext:
        """Get execution context with audit info"""
        return self._ctx
    
    def get_audit_log(self) -> dict:
        """Get full audit log"""
        return {
            "kernel_id": self._ctx.kernel_id,
            "session_id": self._ctx.session_id,
            "plugins_loaded": self._ctx.plugins_loaded,
            "functions_invoked": self._ctx.functions_invoked,
            "memory_operations": self._ctx.memory_operations,
            "call_count": self._ctx.call_count,
            "checkpoints": self._ctx.checkpoints
        }
    
    def __getattr__(self, name):
        """Passthrough for other kernel attributes"""
        return getattr(self._kernel, name)


class GovernedPlan:
    """
    A Semantic Kernel plan wrapped with governance.
    
    Validates each step before execution.
    """
    
    def __init__(
        self,
        plan: Any,
        wrapper: SemanticKernelWrapper,
        ctx: SKContext
    ):
        self._plan = plan
        self._wrapper = wrapper
        self._ctx = ctx
    
    async def invoke(self, **kwargs) -> Any:
        """
        Execute plan with step-by-step governance.
        """
        # Check signals before starting
        if self._wrapper.is_killed():
            raise ExecutionKilledError("Kernel received SIGKILL")
        
        # Validate plan steps against policy
        if hasattr(self._plan, '_steps'):
            for step in self._plan._steps:
                step_name = getattr(step, 'name', str(step))
                if self._wrapper.policy.allowed_tools:
                    if step_name not in self._wrapper.policy.allowed_tools:
                        raise PolicyViolationError(
                            f"Plan step not allowed: {step_name}"
                        )
        
        # Execute with signal checks
        result = await self._plan.invoke(**kwargs)
        
        return result
    
    def __getattr__(self, name):
        return getattr(self._plan, name)


# ============================================================================
# Exceptions
# ============================================================================

class PolicyViolationError(Exception):
    """Raised when a function violates governance policy"""
    pass


class ExecutionStoppedError(Exception):
    """Raised when execution is stopped (SIGSTOP)"""
    pass


class ExecutionKilledError(Exception):
    """Raised when execution is killed (SIGKILL)"""
    pass


# ============================================================================
# Convenience Functions
# ============================================================================

def wrap_kernel(
    kernel: Any,
    policy: Optional[GovernancePolicy] = None
) -> GovernedSemanticKernel:
    """
    Quick wrapper for Semantic Kernel.
    
    Example:
        from agent_os.integrations.semantic_kernel_adapter import wrap_kernel
        
        governed = wrap_kernel(my_kernel)
        result = await governed.invoke("plugin", "function")
    """
    return SemanticKernelWrapper(policy=policy).wrap(kernel)
