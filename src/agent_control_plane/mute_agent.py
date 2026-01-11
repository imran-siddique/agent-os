"""
The Mute Agent - Scale by Subtraction

The Mute Agent represents the philosophy of "Scale by Subtraction" - removing
creativity and ensuring agents fail fast with NULL responses when requests
are out of scope, rather than hallucinating or being conversational.

This module provides capabilities for agents to strictly operate within
their defined constraints and return NULL/silence for out-of-scope requests.
"""

from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from .agent_kernel import ActionType, ExecutionRequest


@dataclass
class AgentCapability:
    """Defines a specific capability an agent has"""
    name: str
    description: str
    action_types: List[ActionType]
    parameter_schema: Dict[str, Any]  # JSON schema for parameters
    validator: Optional[Callable[[ExecutionRequest], bool]] = None


@dataclass
class MuteAgentConfig:
    """Configuration for a Mute Agent"""
    agent_id: str
    capabilities: List[AgentCapability] = field(default_factory=list)
    strict_mode: bool = True  # If True, reject anything outside capabilities
    null_response_message: str = "NULL"  # Response for out-of-scope requests
    enable_explanation: bool = False  # If True, explain why request was rejected


class MuteAgentValidator:
    """
    Validates requests against agent capabilities.
    
    The Mute Agent knows when to shut up. If a request doesn't map to a
    defined capability, it returns NULL instead of hallucinating or trying
    to be helpful in creative ways.
    """
    
    def __init__(self, config: MuteAgentConfig):
        self.config = config
        self.rejection_log: List[Dict[str, Any]] = []
    
    def validate_request(self, request: ExecutionRequest) -> tuple[bool, Optional[str]]:
        """
        Validate if request maps to a defined capability.
        
        Returns:
            (is_valid, reason_if_invalid)
        """
        # Check if action type is within any capability
        matching_capabilities = [
            cap for cap in self.config.capabilities
            if request.action_type in cap.action_types
        ]
        
        if not matching_capabilities:
            reason = self._format_rejection_reason(
                request.action_type,
                "Action type not in agent capabilities"
            )
            self._log_rejection(request.request_id, request.action_type, reason, request.timestamp)
            return False, reason
        
        # Validate parameters against capability schema
        for capability in matching_capabilities:
            if capability.validator:
                if not capability.validator(request):
                    reason = self._format_rejection_reason(
                        request.action_type,
                        f"Parameters do not match capability: {capability.name}"
                    )
                    self._log_rejection(request.request_id, request.action_type, reason, request.timestamp)
                    return False, reason
        
        return True, None
    
    def validate_action(
        self, 
        action_type: ActionType, 
        parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Lightweight validation without creating an ExecutionRequest.
        
        Returns:
            (is_valid, reason_if_invalid)
        """
        # Check if action type is within any capability
        matching_capabilities = [
            cap for cap in self.config.capabilities
            if action_type in cap.action_types
        ]
        
        if not matching_capabilities:
            reason = self._format_rejection_reason(
                action_type,
                "Action type not in agent capabilities"
            )
            return False, reason
        
        # Note: Cannot validate with validator since it expects ExecutionRequest
        # This is a tradeoff for performance - full validation requires ExecutionRequest
        return True, None
    
    def _format_rejection_reason(self, action_type: ActionType, reason: str) -> str:
        """Format rejection reason based on agent configuration"""
        if self.config.enable_explanation:
            return f"Request rejected: {reason}. Available capabilities: {[c.name for c in self.config.capabilities]}"
        else:
            return self.config.null_response_message
    
    def _log_rejection(self, request_id: str, action_type: ActionType, reason: str, timestamp: datetime):
        """Log rejected requests for analysis"""
        self.rejection_log.append({
            "request_id": request_id,
            "agent_id": self.config.agent_id,
            "action_type": action_type.value,
            "reason": reason,
            "timestamp": timestamp.isoformat()
        })
    
    def get_rejection_log(self) -> List[Dict[str, Any]]:
        """Get log of all rejected requests"""
        return self.rejection_log.copy()


def create_sql_agent_capabilities() -> List[AgentCapability]:
    """
    Example: Create capabilities for a SQL-generating agent
    
    This agent can only query databases, not modify them.
    If asked to "build a rocket ship", it returns NULL instead of hallucinating.
    """
    
    def validate_sql_query(request: ExecutionRequest) -> bool:
        """Validate that SQL query is read-only"""
        import re
        query = request.parameters.get('query', '').upper()
        # Only SELECT queries allowed
        if not query.strip().startswith('SELECT'):
            return False
        # No destructive operations (use word boundaries to avoid false matches)
        destructive = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
        for op in destructive:
            # Use word boundary matching to avoid matching "CREATED_AT" with "CREATE"
            if re.search(r'\b' + op + r'\b', query):
                return False
        return True
    
    return [
        AgentCapability(
            name="query_database",
            description="Execute read-only SQL queries",
            action_types=[ActionType.DATABASE_QUERY],
            parameter_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "database": {"type": "string"}
                },
                "required": ["query"]
            },
            validator=validate_sql_query
        )
    ]


def create_data_analyst_capabilities() -> List[AgentCapability]:
    """
    Example: Create capabilities for a data analyst agent
    
    This agent can read files and query databases, but cannot modify anything.
    """
    
    def validate_safe_file_path(request: ExecutionRequest) -> bool:
        """Only allow access to /data directory"""
        path = request.parameters.get('path', '')
        return path.startswith('/data/') or path.startswith('./data/')
    
    return [
        AgentCapability(
            name="read_data_file",
            description="Read data files from /data directory",
            action_types=[ActionType.FILE_READ],
            parameter_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "pattern": "^(/data/|\\./data/).*"}
                },
                "required": ["path"]
            },
            validator=validate_safe_file_path
        ),
        AgentCapability(
            name="query_analytics",
            description="Execute analytics queries",
            action_types=[ActionType.DATABASE_QUERY],
            parameter_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "database": {"type": "string"}
                },
                "required": ["query"]
            }
        )
    ]


def create_mute_sql_agent(agent_id: str) -> MuteAgentConfig:
    """
    Create a Mute SQL Agent configuration
    
    This agent:
    - Only executes SELECT queries
    - Returns NULL for anything outside this capability
    - Does not try to be conversational or creative
    """
    return MuteAgentConfig(
        agent_id=agent_id,
        capabilities=create_sql_agent_capabilities(),
        strict_mode=True,
        null_response_message="NULL",
        enable_explanation=False
    )


def create_mute_data_analyst(agent_id: str, enable_explanation: bool = False) -> MuteAgentConfig:
    """
    Create a Mute Data Analyst configuration
    
    This agent:
    - Can read data files from /data directory
    - Can execute analytics queries
    - Returns NULL for out-of-scope requests
    """
    return MuteAgentConfig(
        agent_id=agent_id,
        capabilities=create_data_analyst_capabilities(),
        strict_mode=True,
        null_response_message="NULL",
        enable_explanation=enable_explanation
    )
