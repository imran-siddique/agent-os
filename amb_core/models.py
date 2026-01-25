"""Core message models for AMB."""

from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class MessagePriority(str, Enum):
    """Message priority levels."""
    BACKGROUND = "background"  # Low-priority background tasks (e.g., memory consolidation)
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"  # Highest priority (e.g., security, governance)


class Message(BaseModel):
    """
    Core message model for the Agent Message Bus.
    
    This model represents a message that can be sent through the bus.
    It includes metadata for routing, tracking, and handling.
    """
    
    id: str = Field(..., description="Unique message identifier")
    topic: str = Field(..., description="Message topic/channel")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="Message priority")
    
    # Metadata
    sender: Optional[str] = Field(None, description="Sender identifier")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for request-response patterns")
    reply_to: Optional[str] = Field(None, description="Topic to reply to")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Message timestamp")
    
    # TTL and expiration
    ttl: Optional[int] = Field(None, description="Time to live in seconds")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
