"""
Data models for the self-correcting agent kernel.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class FailureType(str, Enum):
    """Types of agent failures."""
    BLOCKED_BY_CONTROL_PLANE = "blocked_by_control_plane"
    TIMEOUT = "timeout"
    INVALID_ACTION = "invalid_action"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    LOGIC_ERROR = "logic_error"
    UNKNOWN = "unknown"


class FailureSeverity(str, Enum):
    """Severity levels for failures."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentFailure(BaseModel):
    """Represents a failure detected in an agent."""
    
    agent_id: str = Field(..., description="Unique identifier for the agent")
    failure_type: FailureType = Field(..., description="Type of failure")
    severity: FailureSeverity = Field(default=FailureSeverity.MEDIUM)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_message: str = Field(..., description="Error message from the failure")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "agent_id": "agent-123",
                "failure_type": "blocked_by_control_plane",
                "severity": "high",
                "error_message": "Agent action blocked by control plane policy",
                "context": {"action": "delete_file", "resource": "/etc/passwd"}
            }
        }
    )


class FailureAnalysis(BaseModel):
    """Analysis of an agent failure."""
    
    failure: AgentFailure
    root_cause: str = Field(..., description="Identified root cause")
    contributing_factors: List[str] = Field(default_factory=list)
    suggested_fixes: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in analysis")
    similar_failures: List[str] = Field(default_factory=list, description="IDs of similar past failures")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "root_cause": "Agent attempted unauthorized file access",
                "contributing_factors": ["Missing permission check", "Inadequate input validation"],
                "suggested_fixes": ["Add permission validation", "Implement safe file access patterns"],
                "confidence_score": 0.85
            }
        }
    )


class SimulationResult(BaseModel):
    """Result of simulating an alternative path."""
    
    simulation_id: str
    success: bool
    alternative_path: List[Dict[str, Any]] = Field(description="Steps in the alternative path")
    expected_outcome: str
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk of the alternative")
    estimated_success_rate: float = Field(..., ge=0.0, le=1.0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "simulation_id": "sim-456",
                "success": True,
                "alternative_path": [
                    {"action": "validate_permissions", "params": {}},
                    {"action": "safe_file_access", "params": {"file": "/tmp/safe.txt"}}
                ],
                "expected_outcome": "Safe file operation completed",
                "risk_score": 0.15,
                "estimated_success_rate": 0.92
            }
        }
    )


class CorrectionPatch(BaseModel):
    """A patch to correct an agent's behavior."""
    
    patch_id: str
    agent_id: str
    failure_analysis: FailureAnalysis
    simulation_result: SimulationResult
    patch_type: str = Field(..., description="Type of patch (code, config, rule)")
    patch_content: Dict[str, Any] = Field(..., description="The actual patch content")
    applied: bool = Field(default=False)
    applied_at: Optional[datetime] = None
    rollback_available: bool = Field(default=True)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patch_id": "patch-789",
                "agent_id": "agent-123",
                "patch_type": "code",
                "patch_content": {
                    "module": "file_handler",
                    "changes": [
                        {"type": "add_validation", "code": "if not has_permission(file): return"}
                    ]
                },
                "applied": True
            }
        }
    )


class AgentState(BaseModel):
    """Current state of an agent."""
    
    agent_id: str
    status: str = Field(..., description="Current status (running, failed, patched, etc.)")
    last_failure: Optional[AgentFailure] = None
    patches_applied: List[str] = Field(default_factory=list, description="List of patch IDs")
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    total_runs: int = Field(default=0)
    failed_runs: int = Field(default=0)
