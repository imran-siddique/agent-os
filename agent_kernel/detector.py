"""
Failure detection and monitoring system.
"""

import logging
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

from .models import AgentFailure, FailureType, FailureSeverity

logger = logging.getLogger(__name__)


class FailureDetector:
    """Detects and classifies agent failures."""
    
    def __init__(self):
        self.failure_handlers: Dict[str, Callable] = {}
        self.failure_history: List[AgentFailure] = []
        
    def register_handler(self, failure_type: str, handler: Callable):
        """Register a custom handler for a specific failure type."""
        self.failure_handlers[failure_type] = handler
        logger.info(f"Registered handler for failure type: {failure_type}")
    
    def detect_failure(
        self,
        agent_id: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> AgentFailure:
        """
        Detect and classify a failure.
        
        Args:
            agent_id: Identifier of the agent that failed
            error_message: Error message from the failure
            context: Additional context about the failure
            stack_trace: Stack trace if available
            
        Returns:
            AgentFailure object with classified failure
        """
        failure_type = self._classify_failure(error_message, context)
        severity = self._assess_severity(failure_type, context)
        
        failure = AgentFailure(
            agent_id=agent_id,
            failure_type=failure_type,
            severity=severity,
            error_message=error_message,
            context=context or {},
            stack_trace=stack_trace,
            timestamp=datetime.utcnow()
        )
        
        self.failure_history.append(failure)
        logger.warning(f"Detected {failure_type} failure for agent {agent_id}: {error_message}")
        
        return failure
    
    def _classify_failure(self, error_message: str, context: Optional[Dict[str, Any]]) -> FailureType:
        """Classify the type of failure based on error message and context."""
        error_lower = error_message.lower()
        
        # Check for control plane blocking
        if any(keyword in error_lower for keyword in [
            "blocked", "control plane", "policy", "unauthorized", "forbidden"
        ]):
            return FailureType.BLOCKED_BY_CONTROL_PLANE
        
        # Check for timeout
        if any(keyword in error_lower for keyword in ["timeout", "timed out", "deadline"]):
            return FailureType.TIMEOUT
        
        # Check for invalid action
        if any(keyword in error_lower for keyword in ["invalid", "not allowed", "unsupported"]):
            return FailureType.INVALID_ACTION
        
        # Check for resource exhaustion
        if any(keyword in error_lower for keyword in [
            "resource", "memory", "disk", "quota", "limit exceeded"
        ]):
            return FailureType.RESOURCE_EXHAUSTED
        
        # Check for logic errors
        if any(keyword in error_lower for keyword in [
            "assertion", "null pointer", "index out", "key error", "type error"
        ]):
            return FailureType.LOGIC_ERROR
        
        return FailureType.UNKNOWN
    
    def _assess_severity(self, failure_type: FailureType, context: Optional[Dict[str, Any]]) -> FailureSeverity:
        """Assess the severity of a failure."""
        # Control plane blocks are typically high severity
        if failure_type == FailureType.BLOCKED_BY_CONTROL_PLANE:
            return FailureSeverity.HIGH
        
        # Resource exhaustion can be critical
        if failure_type == FailureType.RESOURCE_EXHAUSTED:
            return FailureSeverity.HIGH
        
        # Timeouts are usually medium severity
        if failure_type == FailureType.TIMEOUT:
            return FailureSeverity.MEDIUM
        
        # Logic errors can vary
        if failure_type == FailureType.LOGIC_ERROR:
            return FailureSeverity.MEDIUM
        
        # Default to medium for unknown
        return FailureSeverity.MEDIUM
    
    def get_failure_history(self, agent_id: Optional[str] = None, limit: int = 100) -> List[AgentFailure]:
        """Get failure history, optionally filtered by agent_id."""
        history = self.failure_history
        
        if agent_id:
            history = [f for f in history if f.agent_id == agent_id]
        
        return history[-limit:]
