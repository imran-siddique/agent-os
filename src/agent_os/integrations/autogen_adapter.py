"""
AutoGen Integration

Wraps Microsoft AutoGen agents with Agent OS governance.

Usage:
    from agent_os.integrations import AutoGenKernel
    
    kernel = AutoGenKernel()
    kernel.govern(agent1, agent2, agent3)
    
    # Now all conversations are governed
    agent1.initiate_chat(agent2, message="...")
"""

from typing import Any, Optional, List

from .base import BaseIntegration, GovernancePolicy, ExecutionContext
from .langchain_adapter import PolicyViolationError


class AutoGenKernel(BaseIntegration):
    """
    AutoGen adapter for Agent OS.
    
    Supports:
    - AssistantAgent
    - UserProxyAgent
    - GroupChat
    - Conversation flows
    """
    
    def __init__(self, policy: Optional[GovernancePolicy] = None):
        """Initialise the AutoGen governance kernel.

        Args:
            policy: Governance policy to enforce. When ``None`` the default
                ``GovernancePolicy`` is used.
        """
        super().__init__(policy)
        self._governed_agents: dict[str, Any] = {}
        self._original_methods: dict[str, dict[str, Any]] = {}
        self._stopped: dict[str, bool] = {}

    def wrap(self, agent: Any) -> Any:
        """Wrap a single AutoGen agent with governance.

        Convenience method that delegates to :meth:`govern` for a single
        agent.

        Args:
            agent: An AutoGen agent (``AssistantAgent``, ``UserProxyAgent``,
                etc.).

        Returns:
            The same agent object with its key methods monkey-patched for
            governance.
        """
        return self.govern(agent)[0]

    def govern(self, *agents: Any) -> List[Any]:
        """Add governance to one or more AutoGen agents.

        Monkey-patches ``initiate_chat``, ``generate_reply``, and
        ``receive`` on each agent so that every message exchange is
        validated against the active policy.

        The original methods are stored internally so they can be restored
        later via :meth:`unwrap`.

        Args:
            *agents: AutoGen agents to govern.

        Returns:
            The same agent objects (in-place patched) as a list.

        Example:
            >>> kernel = AutoGenKernel(policy=GovernancePolicy(
            ...     blocked_patterns=["password"]
            ... ))
            >>> kernel.govern(assistant, user_proxy)
            >>> assistant.initiate_chat(user_proxy, message="hello")
        """
        governed = []
        
        for agent in agents:
            agent_id = getattr(agent, 'name', f"autogen-{id(agent)}")
            ctx = self.create_context(agent_id)
            
            # Store reference
            self._governed_agents[agent_id] = agent
            self._stopped[agent_id] = False
            
            # Store original methods before wrapping
            self._original_methods[agent_id] = {}
            for method_name in ('initiate_chat', 'generate_reply', 'receive'):
                if hasattr(agent, method_name):
                    self._original_methods[agent_id][method_name] = getattr(agent, method_name)
            
            # Wrap key methods
            self._wrap_initiate_chat(agent, ctx, agent_id)
            self._wrap_generate_reply(agent, ctx, agent_id)
            self._wrap_receive(agent, ctx, agent_id)
            
            governed.append(agent)
        
        return governed
    
    def _wrap_initiate_chat(self, agent: Any, ctx: ExecutionContext, agent_id: str):
        """Wrap ``initiate_chat`` with pre-/post-execution governance.

        Args:
            agent: The AutoGen agent to patch.
            ctx: Execution context for this agent.
            agent_id: Unique identifier for audit logging.
        """
        if not hasattr(agent, 'initiate_chat'):
            return
        
        original = agent.initiate_chat
        kernel = self
        
        def governed_initiate_chat(recipient, message=None, **kwargs):
            if kernel._stopped.get(agent_id):
                raise PolicyViolationError(f"Agent '{agent_id}' is stopped (SIGSTOP)")
            
            allowed, reason = kernel.pre_execute(ctx, {"recipient": str(recipient), "message": message})
            if not allowed:
                raise PolicyViolationError(reason)
            
            result = original(recipient, message=message, **kwargs)
            
            kernel.post_execute(ctx, result)
            return result
        
        agent.initiate_chat = governed_initiate_chat
    
    def _wrap_generate_reply(self, agent: Any, ctx: ExecutionContext, agent_id: str):
        """Wrap ``generate_reply`` with message interception and governance.

        Unlike ``initiate_chat``, violations in ``generate_reply`` return a
        ``[BLOCKED: ...]`` string rather than raising an exception, so that
        multi-agent conversations can continue with the violation visible
        in the message stream.

        Args:
            agent: The AutoGen agent to patch.
            ctx: Execution context for this agent.
            agent_id: Unique identifier for audit logging.
        """
        if not hasattr(agent, 'generate_reply'):
            return
        
        original = agent.generate_reply
        kernel = self
        
        def governed_generate_reply(messages=None, sender=None, **kwargs):
            if kernel._stopped.get(agent_id):
                return f"[BLOCKED: Agent '{agent_id}' is stopped (SIGSTOP)]"
            
            allowed, reason = kernel.pre_execute(ctx, {"messages": messages, "sender": str(sender)})
            if not allowed:
                return f"[BLOCKED: {reason}]"
            
            result = original(messages=messages, sender=sender, **kwargs)
            
            valid, reason = kernel.post_execute(ctx, result)
            if not valid:
                return f"[BLOCKED: {reason}]"
            
            return result
        
        agent.generate_reply = governed_generate_reply
    
    def _wrap_receive(self, agent: Any, ctx: ExecutionContext, agent_id: str):
        """Wrap ``receive`` with inbound message governance.

        Intercepts messages arriving at this agent and validates them
        against the active policy before forwarding to the original
        ``receive`` implementation.

        Args:
            agent: The AutoGen agent to patch.
            ctx: Execution context for this agent.
            agent_id: Unique identifier for audit logging.
        """
        if not hasattr(agent, 'receive'):
            return
        
        original = agent.receive
        kernel = self
        
        def governed_receive(message, sender, **kwargs):
            if kernel._stopped.get(agent_id):
                raise PolicyViolationError(f"Agent '{agent_id}' is stopped (SIGSTOP)")
            
            allowed, reason = kernel.pre_execute(ctx, {"message": message, "sender": str(sender)})
            if not allowed:
                raise PolicyViolationError(reason)
            
            result = original(message, sender, **kwargs)
            
            kernel.post_execute(ctx, result)
            return result
        
        agent.receive = governed_receive
    
    def unwrap(self, governed_agent: Any) -> Any:
        """Restore original methods on a governed AutoGen agent.

        Removes all monkey-patches applied by :meth:`govern` and clears
        the agent from internal tracking.

        Args:
            governed_agent: A previously governed AutoGen agent.

        Returns:
            The agent with its original, un-governed methods restored.
        """
        agent_id = getattr(governed_agent, 'name', f"autogen-{id(governed_agent)}")
        originals = self._original_methods.get(agent_id, {})
        
        for method_name, original_method in originals.items():
            setattr(governed_agent, method_name, original_method)
        
        self._governed_agents.pop(agent_id, None)
        self._original_methods.pop(agent_id, None)
        self._stopped.pop(agent_id, None)
        
        return governed_agent
    
    def signal(self, agent_id: str, signal: str):
        """Send a POSIX-style signal to a governed agent.

        Supported signals:

        * ``SIGSTOP`` — pause the agent; all intercepted methods will
          raise ``PolicyViolationError`` or return a blocked message.
        * ``SIGCONT`` — resume a previously stopped agent.
        * ``SIGKILL`` — permanently remove governance (calls
          :meth:`unwrap`).

        Args:
            agent_id: Identifier of the target agent.
            signal: One of ``"SIGSTOP"``, ``"SIGCONT"``, or ``"SIGKILL"``.
        """
        if signal == "SIGSTOP":
            self._stopped[agent_id] = True
        elif signal == "SIGCONT":
            self._stopped[agent_id] = False
        elif signal == "SIGKILL":
            if agent_id in self._governed_agents:
                agent = self._governed_agents[agent_id]
                self.unwrap(agent)
        
        super().signal(agent_id, signal)


# Convenience function
def govern(*agents: Any, policy: Optional[GovernancePolicy] = None) -> List[Any]:
    """Convenience function to add governance to AutoGen agents.

    Args:
        *agents: AutoGen agents to govern.
        policy: Optional governance policy (uses defaults when ``None``).

    Returns:
        The governed agents as a list.

    Example:
        >>> from agent_os.integrations.autogen_adapter import govern
        >>> governed_agents = govern(assistant, user_proxy)
    """
    return AutoGenKernel(policy).govern(*agents)
