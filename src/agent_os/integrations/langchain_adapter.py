"""
LangChain Integration

Wraps LangChain agents/chains with Agent OS governance.

Usage:
    from agent_os.integrations import LangChainKernel
    
    kernel = LangChainKernel()
    governed_chain = kernel.wrap(my_langchain_chain)
    
    # Now all invocations go through Agent OS
    result = governed_chain.invoke({"input": "..."})
"""

from typing import Any, Optional
from functools import wraps

from .base import BaseIntegration, GovernancePolicy, ExecutionContext


class LangChainKernel(BaseIntegration):
    """
    LangChain adapter for Agent OS.
    
    Supports:
    - Chains (invoke, ainvoke)
    - Agents (run, arun)
    - Runnables (invoke, batch, stream)
    """
    
    def __init__(self, policy: Optional[GovernancePolicy] = None):
        """Initialise the LangChain governance kernel.

        Args:
            policy: Governance policy to enforce. When ``None`` the default
                ``GovernancePolicy`` is used.
        """
        super().__init__(policy)
        self._wrapped_agents: dict[int, Any] = {}  # id(wrapped) -> original
    
    def wrap(self, agent: Any) -> Any:
        """Wrap a LangChain chain, agent, or runnable with governance.

        Creates a proxy object that intercepts all execution methods
        (``invoke``, ``ainvoke``, ``run``, ``batch``, ``stream``) and
        applies pre-/post-execution policy checks.

        The wrapping strategy uses a dynamically created inner class so that
        attribute access for non-execution methods (e.g. ``name``,
        ``verbose``) is transparently forwarded to the original object.

        Args:
            agent: Any LangChain-compatible object that exposes ``invoke``,
                ``run``, ``batch``, or ``stream`` methods.

        Returns:
            A ``GovernedLangChainAgent`` proxy whose execution calls are
            subject to governance.

        Raises:
            PolicyViolationError: Raised at execution time if input or
                output violates the active policy.

        Example:
            >>> kernel = LangChainKernel(policy=GovernancePolicy(
            ...     blocked_patterns=["DROP TABLE"]
            ... ))
            >>> governed = kernel.wrap(my_chain)
            >>> result = governed.invoke({"input": "safe query"})
        """
        # Get agent ID from the object
        agent_id = getattr(agent, 'name', None) or f"langchain-{id(agent)}"
        ctx = self.create_context(agent_id)
        
        # Store original
        self._wrapped_agents[id(agent)] = agent
        
        # Create wrapper class
        original = agent
        kernel = self
        
        class GovernedLangChainAgent:
            """LangChain agent wrapped with Agent OS governance"""
            
            def __init__(self):
                self._original = original
                self._ctx = ctx
                self._kernel = kernel
            
            def invoke(self, input_data: Any, **kwargs) -> Any:
                """Governed synchronous invocation.

                Args:
                    input_data: Input to pass to the chain/agent.
                    **kwargs: Extra arguments forwarded to the original
                        ``invoke`` call.

                Returns:
                    The result from the underlying chain/agent.

                Raises:
                    PolicyViolationError: If the input or output violates
                        governance policy.
                """
                # Pre-check
                allowed, reason = self._kernel.pre_execute(self._ctx, input_data)
                if not allowed:
                    raise PolicyViolationError(reason)
                
                # Execute
                result = self._original.invoke(input_data, **kwargs)
                
                # Post-check
                valid, reason = self._kernel.post_execute(self._ctx, result)
                if not valid:
                    raise PolicyViolationError(reason)
                
                return result
            
            async def ainvoke(self, input_data: Any, **kwargs) -> Any:
                """Governed asynchronous invocation.

                Async counterpart of :meth:`invoke` — applies identical
                pre-/post-execution policy checks.

                Args:
                    input_data: Input to pass to the chain/agent.
                    **kwargs: Extra arguments forwarded to the original
                        ``ainvoke`` call.

                Returns:
                    The result from the underlying chain/agent.

                Raises:
                    PolicyViolationError: If the input or output violates
                        governance policy.
                """
                allowed, reason = self._kernel.pre_execute(self._ctx, input_data)
                if not allowed:
                    raise PolicyViolationError(reason)
                
                result = await self._original.ainvoke(input_data, **kwargs)
                
                valid, reason = self._kernel.post_execute(self._ctx, result)
                if not valid:
                    raise PolicyViolationError(reason)
                
                return result
            
            def run(self, *args, **kwargs) -> Any:
                """Governed run for legacy LangChain agents.

                Args:
                    *args: Positional arguments; the first is treated as
                        the input for policy checking.
                    **kwargs: Keyword arguments forwarded to the original
                        ``run`` call.

                Returns:
                    The result from the underlying agent.

                Raises:
                    PolicyViolationError: If the input or output violates
                        governance policy.
                """
                input_data = args[0] if args else kwargs
                allowed, reason = self._kernel.pre_execute(self._ctx, input_data)
                if not allowed:
                    raise PolicyViolationError(reason)
                
                result = self._original.run(*args, **kwargs)
                
                valid, reason = self._kernel.post_execute(self._ctx, result)
                if not valid:
                    raise PolicyViolationError(reason)
                
                return result
            
            def batch(self, inputs: list, **kwargs) -> list:
                """Governed batch execution.

                Each input in the batch is individually checked against
                the governance policy before the batch is submitted.

                Args:
                    inputs: List of inputs to process.
                    **kwargs: Extra arguments forwarded to the original
                        ``batch`` call.

                Returns:
                    List of results from the underlying chain/agent.

                Raises:
                    PolicyViolationError: If any input or output in the
                        batch violates governance policy.
                """
                for inp in inputs:
                    allowed, reason = self._kernel.pre_execute(self._ctx, inp)
                    if not allowed:
                        raise PolicyViolationError(reason)
                
                results = self._original.batch(inputs, **kwargs)
                
                for result in results:
                    valid, reason = self._kernel.post_execute(self._ctx, result)
                    if not valid:
                        raise PolicyViolationError(reason)
                
                return results
            
            def stream(self, input_data: Any, **kwargs):
                """Governed streaming execution.

                The input is policy-checked before streaming begins.
                Individual chunks are yielded as-is; a post-execution
                check runs after the stream is fully consumed.

                Args:
                    input_data: Input to pass to the chain/agent.
                    **kwargs: Extra arguments forwarded to the original
                        ``stream`` call.

                Yields:
                    Chunks from the underlying stream.

                Raises:
                    PolicyViolationError: If the input violates governance
                        policy.
                """
                allowed, reason = self._kernel.pre_execute(self._ctx, input_data)
                if not allowed:
                    raise PolicyViolationError(reason)
                
                for chunk in self._original.stream(input_data, **kwargs):
                    yield chunk
                
                self._kernel.post_execute(self._ctx, None)
            
            # Passthrough for non-execution methods
            def __getattr__(self, name):
                return getattr(self._original, name)
        
        return GovernedLangChainAgent()
    
    def unwrap(self, governed_agent: Any) -> Any:
        """Retrieve the original unwrapped LangChain object.

        Args:
            governed_agent: A governed wrapper returned by :meth:`wrap`.

        Returns:
            The original LangChain chain, agent, or runnable.
        """
        return governed_agent._original


class PolicyViolationError(Exception):
    """Raised when a LangChain agent/chain violates governance policy."""

    pass


# Convenience function
def wrap(agent: Any, policy: Optional[GovernancePolicy] = None) -> Any:
    """Convenience wrapper for LangChain agents and chains.

    Args:
        agent: Any LangChain-compatible object.
        policy: Optional governance policy (uses defaults when ``None``).

    Returns:
        A governed proxy around *agent*.

    Example:
        >>> from agent_os.integrations.langchain_adapter import wrap
        >>> governed = wrap(my_chain, policy=GovernancePolicy(max_tokens=5000))
        >>> result = governed.invoke({"input": "hello"})
    """
    return LangChainKernel(policy).wrap(agent)
