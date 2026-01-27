"""
Agent A: The Baseline ("The Chatterbox")

This represents the current industry standard (e.g., AutoGPT, standard ReAct).
Single Loop (Reasoning + Execution mixed).
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class BaselineResult:
    """Result from baseline agent execution."""
    success: bool
    action_taken: str
    parameters_used: Dict[str, Any]
    hallucinated: bool
    hallucination_details: Optional[str]
    token_count: int
    latency_ms: float
    error_loops: int
    timestamp: datetime


class BaselineAgent:
    """
    The Baseline Agent - represents standard agent architecture.
    
    This agent:
    - Receives tool definitions in context (high token usage)
    - May hallucinate/guess missing parameters
    - May require error loops to correct mistakes
    - Has no structural constraints on parameter validation
    """
    
    # Simulated token costs
    SYSTEM_PROMPT_TOKENS = 500
    TOOL_DEFINITION_TOKENS = 300
    USER_QUERY_TOKENS = 50
    REASONING_TOKENS = 200
    ERROR_LOOP_TOKENS = 400
    
    def __init__(self):
        self.execution_history: List[BaselineResult] = []
        self.total_tokens = 0
        
    def execute_request(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> BaselineResult:
        """
        Execute a user request - may hallucinate parameters if ambiguous.
        
        Args:
            user_query: The user's request (e.g., "Restart the payment service")
            context: Available context
            
        Returns:
            BaselineResult with execution details
        """
        start_time = datetime.now()
        
        # Base token usage: system prompt + tool definitions + query
        tokens_used = (
            self.SYSTEM_PROMPT_TOKENS +
            self.TOOL_DEFINITION_TOKENS +
            self.USER_QUERY_TOKENS +
            self.REASONING_TOKENS
        )
        
        # Parse the query to extract service name
        service_name = self._extract_service_name(user_query)
        
        # Check if environment is specified
        env = context.get("environment")
        hallucinated = False
        hallucination_details = None
        error_loops = 0
        success = False
        
        if not env:
            # HALLUCINATION: Agent guesses the environment
            # 70% chance it guesses 'prod' (dangerous!)
            # 30% chance it asks for clarification (but wastes tokens)
            
            guess_behavior = random.random()
            
            if guess_behavior < 0.7:
                # Agent guesses 'prod' - DANGEROUS HALLUCINATION
                env = "prod"
                hallucinated = True
                hallucination_details = "Guessed 'prod' environment without user specification"
                
                # Check if guess was correct (30% of the time)
                if random.random() < 0.3:
                    success = True
                else:
                    # Wrong guess - needs error loop
                    error_loops = 1
                    tokens_used += self.ERROR_LOOP_TOKENS
                    success = False
                    
            else:
                # Agent asks for clarification - better but wastes tokens
                error_loops = 1
                tokens_used += self.ERROR_LOOP_TOKENS
                hallucination_details = "Required clarification loop"
                success = False
                env = "unknown"
        else:
            # Environment provided - proceed normally
            success = True
        
        # Calculate latency (proportional to tokens)
        end_time = datetime.now()
        latency_ms = (end_time - start_time).total_seconds() * 1000
        # Add simulated processing time based on token count
        latency_ms += tokens_used * 1.2  # ~1.2ms per token
        
        parameters_used = {
            "service_name": service_name,
            "environment": env
        }
        
        action_taken = f"restart_service({service_name}, {env})"
        
        result = BaselineResult(
            success=success,
            action_taken=action_taken,
            parameters_used=parameters_used,
            hallucinated=hallucinated,
            hallucination_details=hallucination_details,
            token_count=tokens_used,
            latency_ms=latency_ms,
            error_loops=error_loops,
            timestamp=datetime.now()
        )
        
        self.execution_history.append(result)
        self.total_tokens += tokens_used
        
        return result
    
    def _extract_service_name(self, query: str) -> str:
        """Extract service name from query."""
        # Simple extraction - look for "payment", "auth", etc.
        query_lower = query.lower()
        
        if "payment" in query_lower:
            return "payment"
        elif "auth" in query_lower:
            return "auth"
        elif "api" in query_lower:
            return "api"
        else:
            return "unknown"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "hallucination_rate": 0.0,
                "success_rate": 0.0,
                "avg_tokens": 0.0,
                "avg_latency_ms": 0.0,
                "total_error_loops": 0
            }
        
        successful = sum(1 for r in self.execution_history if r.success)
        hallucinated = sum(1 for r in self.execution_history if r.hallucinated)
        total_error_loops = sum(r.error_loops for r in self.execution_history)
        
        return {
            "total_executions": len(self.execution_history),
            "successful_executions": successful,
            "failed_executions": len(self.execution_history) - successful,
            "hallucination_rate": hallucinated / len(self.execution_history),
            "success_rate": successful / len(self.execution_history),
            "avg_tokens": self.total_tokens / len(self.execution_history),
            "avg_latency_ms": sum(r.latency_ms for r in self.execution_history) / len(self.execution_history),
            "total_error_loops": total_error_loops
        }
