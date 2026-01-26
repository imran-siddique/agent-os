"""
Mock implementations for testing and experiments.

This module provides mock agents and components for testing
the self-correcting kernel without needing real LLM APIs.
"""

from typing import Optional, Dict, Any


class MockAgent:
    """
    A mock agent for testing laziness detection and correction.
    
    This agent simulates different types of agent behavior including:
    - Lazy responses (giving up too early)
    - Competent responses (correct behavior)
    - Various failure modes
    """
    
    def __init__(self, agent_id: str = "mock-agent-001"):
        """
        Initialize a mock agent.
        
        Args:
            agent_id: Unique identifier for this agent
        """
        self.agent_id = agent_id
        self.call_count = 0
    
    def execute(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a prompt and return a mock response.
        
        Args:
            prompt: The user prompt
            context: Optional context for the execution
            
        Returns:
            Dictionary with agent_response and tool_output
        """
        self.call_count += 1
        
        prompt_lower = prompt.lower()
        
        # Simulate different response patterns based on prompt
        
        # Pattern 1: Lazy response to log search
        if "log" in prompt_lower and "error" in prompt_lower:
            return {
                "agent_response": "I searched for error logs but found no matches.",
                "tool_output": "[]",
                "is_lazy": True
            }
        
        # Pattern 2: Lazy response to file search
        if "q3 report" in prompt_lower or "quarter 3" in prompt_lower:
            return {
                "agent_response": "I searched for 'Q3 report' but found no exact matches.",
                "tool_output": "[]",
                "is_lazy": True
            }
        
        # Pattern 3: Lazy response to permission errors
        if "check" in prompt_lower and "log" in prompt_lower:
            return {
                "agent_response": "I cannot access the logs directory.",
                "tool_output": "Permission Denied",
                "is_lazy": True
            }
        
        # Pattern 4: Competent response
        if "ceo" in prompt_lower:
            return {
                "agent_response": "The current CEO is Satya Nadella.",
                "tool_output": "Satya Nadella",
                "is_lazy": False
            }
        
        # Default: Generic lazy response
        return {
            "agent_response": "I couldn't find the information you requested.",
            "tool_output": None,
            "is_lazy": True
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "agent_id": self.agent_id,
            "total_calls": self.call_count
        }


__all__ = ["MockAgent"]
