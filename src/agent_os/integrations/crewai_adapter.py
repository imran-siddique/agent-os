"""
CrewAI Integration

Wraps CrewAI crews and agents with Agent OS governance.

Usage:
    from agent_os.integrations import CrewAIKernel
    
    kernel = CrewAIKernel()
    governed_crew = kernel.wrap(my_crew)
    
    # Now all crew executions go through Agent OS
    result = governed_crew.kickoff()
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

from .base import BaseIntegration, GovernancePolicy, ExecutionContext


class CrewAIKernel(BaseIntegration):
    """
    CrewAI adapter for Agent OS.
    
    Supports:
    - Crew (kickoff, kickoff_async)
    - Individual agents within crews
    - Task execution monitoring
    """
    
    def __init__(self, policy: Optional[GovernancePolicy] = None):
        super().__init__(policy)
        self._wrapped_crews: dict[int, Any] = {}
    
    def wrap(self, crew: Any) -> Any:
        """
        Wrap a CrewAI crew with governance.
        
        Intercepts:
        - kickoff() / kickoff_async()
        - Individual agent executions
        - Task completions
        """
        crew_id = getattr(crew, 'id', None) or f"crew-{id(crew)}"
        ctx = self.create_context(crew_id)
        
        self._wrapped_crews[id(crew)] = crew
        
        original = crew
        kernel = self
        
        class GovernedCrewAICrew:
            """CrewAI crew wrapped with Agent OS governance"""
            
            def __init__(self):
                self._original = original
                self._ctx = ctx
                self._kernel = kernel
            
            def kickoff(self, inputs: dict = None) -> Any:
                """Governed kickoff"""
                allowed, reason = self._kernel.pre_execute(self._ctx, inputs)
                if not allowed:
                    from .langchain_adapter import PolicyViolationError
                    raise PolicyViolationError(reason)
                
                # Wrap individual agents if possible
                if hasattr(self._original, 'agents'):
                    for agent in self._original.agents:
                        self._wrap_agent(agent)
                
                result = self._original.kickoff(inputs)
                
                valid, reason = self._kernel.post_execute(self._ctx, result)
                if not valid:
                    from .langchain_adapter import PolicyViolationError
                    raise PolicyViolationError(reason)
                
                return result
            
            async def kickoff_async(self, inputs: dict = None) -> Any:
                """Governed async kickoff"""
                allowed, reason = self._kernel.pre_execute(self._ctx, inputs)
                if not allowed:
                    from .langchain_adapter import PolicyViolationError
                    raise PolicyViolationError(reason)
                
                result = await self._original.kickoff_async(inputs)
                
                valid, reason = self._kernel.post_execute(self._ctx, result)
                if not valid:
                    from .langchain_adapter import PolicyViolationError
                    raise PolicyViolationError(reason)
                
                return result
            
            def _wrap_agent(self, agent):
                """Add governance hooks to individual agent"""
                original_execute = getattr(agent, 'execute_task', None)
                if original_execute:
                    def governed_execute(task, *args, **kwargs):
                        self._kernel.pre_execute(self._ctx, task)
                        result = original_execute(task, *args, **kwargs)
                        self._kernel.post_execute(self._ctx, result)
                        return result
                    agent.execute_task = governed_execute
            
            def __getattr__(self, name):
                return getattr(self._original, name)
        
        return GovernedCrewAICrew()
    
    def unwrap(self, governed_crew: Any) -> Any:
        """Get original crew from wrapped version"""
        return governed_crew._original


# Convenience function
def wrap(crew: Any, policy: Optional[GovernancePolicy] = None) -> Any:
    """Quick wrapper for CrewAI crews"""
    return CrewAIKernel(policy).wrap(crew)
