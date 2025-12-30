"""
Telemetry and Event Stream System

This module provides event tracking and streaming capabilities
for decoupling execution from learning.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class TelemetryEvent:
    """Represents a single execution event."""
    
    event_type: str  # "task_start", "task_complete", "user_feedback"
    timestamp: str
    query: str
    agent_response: Optional[str] = None
    success: Optional[bool] = None
    user_feedback: Optional[str] = None
    instructions_version: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TelemetryEvent':
        """Create event from dictionary."""
        return cls(**data)


class EventStream:
    """
    Manages the event stream for telemetry.
    Uses a simple file-based append-only log.
    """
    
    def __init__(self, stream_file: str = "telemetry_events.jsonl"):
        self.stream_file = stream_file
    
    def emit(self, event: TelemetryEvent) -> None:
        """Emit an event to the stream."""
        with open(self.stream_file, 'a') as f:
            f.write(json.dumps(event.to_dict()) + '\n')
    
    def read_all(self) -> List[TelemetryEvent]:
        """Read all events from the stream."""
        if not os.path.exists(self.stream_file):
            return []
        
        events = []
        with open(self.stream_file, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    events.append(TelemetryEvent.from_dict(data))
        return events
    
    def read_unprocessed(self, last_processed_timestamp: Optional[str] = None) -> List[TelemetryEvent]:
        """
        Read events that haven't been processed yet.
        If last_processed_timestamp is None, returns all events.
        """
        all_events = self.read_all()
        if last_processed_timestamp is None:
            return all_events
        
        # Return events after the last processed timestamp
        unprocessed = []
        for event in all_events:
            if event.timestamp > last_processed_timestamp:
                unprocessed.append(event)
        return unprocessed
    
    def clear(self) -> None:
        """Clear all events from the stream (for testing)."""
        if os.path.exists(self.stream_file):
            os.remove(self.stream_file)
    
    def get_last_timestamp(self) -> Optional[str]:
        """Get the timestamp of the last event in the stream."""
        events = self.read_all()
        if events:
            return events[-1].timestamp
        return None
