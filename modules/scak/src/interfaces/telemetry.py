"""
Telemetry - JSON Structured Logs for Offline Analysis.

This module implements production-grade telemetry following the principle:
"Telemetry over Logging" - emit JSON blobs that can be parsed, not text.

Key Features:
1. Structured JSON output for log aggregation systems
2. No print() statements - use structured logging
3. Audit trail for compliance
4. Offline analysis support
5. Performance metrics

This is the "interfaces" layer - how the Kernel communicates results.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of telemetry events."""
    FAILURE_DETECTED = "failure_detected"
    FAILURE_ANALYZED = "failure_analyzed"
    PATCH_CREATED = "patch_created"
    PATCH_APPLIED = "patch_applied"
    AUDIT_TRIGGERED = "audit_triggered"
    AUDIT_COMPLETED = "audit_completed"
    LAZINESS_DETECTED = "laziness_detected"
    SEMANTIC_PURGE = "semantic_purge"
    MODEL_UPGRADE = "model_upgrade"
    AGENT_EXECUTION = "agent_execution"
    TRIAGE_DECISION = "triage_decision"


class AuditLog:
    """
    Structured audit log event.
    
    Every try/except block MUST emit an AuditLog event.
    No silent failures allowed.
    """
    
    def __init__(
        self,
        event_type: EventType,
        agent_id: str,
        data: Dict[str, Any],
        severity: str = "INFO"
    ):
        """
        Create audit log event.
        
        Args:
            event_type: Type of event
            agent_id: Agent identifier
            data: Event-specific data
            severity: Log severity (INFO, WARNING, ERROR)
        """
        self.event_type = event_type
        self.agent_id = agent_id
        self.data = data
        self.severity = severity
        self.timestamp = datetime.now().isoformat()
        self.event_id = f"{event_type.value}-{datetime.now().timestamp()}"
    
    def to_json(self) -> str:
        """Serialize to JSON for log aggregation."""
        return json.dumps({
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "data": self.data
        }, indent=None)  # Single-line JSON for log parsing
    
    def emit(self) -> None:
        """
        Emit the log event to structured logging system.
        
        In production, this goes to:
        - stdout/stderr for container log aggregation
        - CloudWatch, Datadog, Splunk, etc.
        - Local file for debugging
        """
        json_str = self.to_json()
        
        # Map severity to logging level
        if self.severity == "ERROR":
            logger.error(json_str)
        elif self.severity == "WARNING":
            logger.warning(json_str)
        else:
            logger.info(json_str)


class TelemetryEmitter:
    """
    Central telemetry emitter for the Kernel.
    
    This is the "observability layer" that makes the self-correcting
    process transparent and analyzable.
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        enable_console: bool = True,
        enable_file: bool = False
    ):
        """
        Initialize telemetry emitter.
        
        Args:
            agent_id: Default agent ID for events
            enable_console: Emit to console (stdout/stderr)
            enable_file: Emit to file (optional)
        """
        self.default_agent_id = agent_id or "scak-kernel"
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.events: List[AuditLog] = []
        
        if enable_file:
            # Set up file handler for JSON logs
            self._setup_file_logging()
    
    def _setup_file_logging(self) -> None:
        """Setup file logging for telemetry."""
        # In production, configure file rotation, compression, etc.
        file_handler = logging.FileHandler("kernel_telemetry.jsonl")
        file_handler.setFormatter(logging.Formatter('%(message)s'))  # Raw JSON
        logger.addHandler(file_handler)
    
    def emit_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        agent_id: Optional[str] = None,
        severity: str = "INFO"
    ) -> None:
        """
        Generic event emitter for Layer 4 components.
        
        Args:
            event_type: Type of event to emit
            data: Event data dictionary
            agent_id: Agent ID (uses default if not provided)
            severity: Log severity (INFO, WARNING, ERROR)
        """
        event = AuditLog(
            event_type=event_type,
            agent_id=agent_id or self.default_agent_id,
            data=data,
            severity=severity
        )
        event.emit()
        self.events.append(event)
    
    def emit_failure_detected(
        self,
        agent_id: str,
        failure_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit failure detection event."""
        event = AuditLog(
            event_type=EventType.FAILURE_DETECTED,
            agent_id=agent_id,
            data={
                "failure_type": failure_type,
                "error_message": error_message,
                "context": context or {}
            },
            severity="WARNING"
        )
        event.emit()
        self.events.append(event)
    
    def emit_failure_analyzed(
        self,
        agent_id: str,
        root_cause: str,
        cognitive_glitch: Optional[str],
        confidence: float
    ) -> None:
        """Emit failure analysis event."""
        event = AuditLog(
            event_type=EventType.FAILURE_ANALYZED,
            agent_id=agent_id,
            data={
                "root_cause": root_cause,
                "cognitive_glitch": cognitive_glitch,
                "confidence": confidence
            },
            severity="INFO"
        )
        event.emit()
        self.events.append(event)
    
    def emit_patch_created(
        self,
        agent_id: str,
        patch_id: str,
        patch_type: str,
        decay_type: str,
        estimated_success_rate: float
    ) -> None:
        """Emit patch creation event."""
        event = AuditLog(
            event_type=EventType.PATCH_CREATED,
            agent_id=agent_id,
            data={
                "patch_id": patch_id,
                "patch_type": patch_type,
                "decay_type": decay_type,
                "estimated_success_rate": estimated_success_rate
            },
            severity="INFO"
        )
        event.emit()
        self.events.append(event)
    
    def emit_patch_applied(
        self,
        agent_id: str,
        patch_id: str,
        application_strategy: str
    ) -> None:
        """Emit patch application event."""
        event = AuditLog(
            event_type=EventType.PATCH_APPLIED,
            agent_id=agent_id,
            data={
                "patch_id": patch_id,
                "application_strategy": application_strategy
            },
            severity="INFO"
        )
        event.emit()
        self.events.append(event)
    
    def emit_audit_triggered(
        self,
        agent_id: str,
        trigger_signal: str,
        user_prompt: str
    ) -> None:
        """Emit Completeness Audit trigger event."""
        event = AuditLog(
            event_type=EventType.AUDIT_TRIGGERED,
            agent_id=agent_id,
            data={
                "trigger_signal": trigger_signal,
                "user_prompt": user_prompt[:200]  # Truncate for privacy
            },
            severity="INFO"
        )
        event.emit()
        self.events.append(event)
    
    def emit_laziness_detected(
        self,
        agent_id: str,
        audit_id: str,
        teacher_response: str,
        gap_analysis: str,
        competence_patch: str
    ) -> None:
        """Emit laziness detection event (HIGH VALUE METRIC)."""
        event = AuditLog(
            event_type=EventType.LAZINESS_DETECTED,
            agent_id=agent_id,
            data={
                "audit_id": audit_id,
                "teacher_response": teacher_response[:200],
                "gap_analysis": gap_analysis[:200],
                "competence_patch": competence_patch[:200]
            },
            severity="WARNING"
        )
        event.emit()
        self.events.append(event)
    
    def emit_semantic_purge(
        self,
        old_model_version: str,
        new_model_version: str,
        purged_count: int,
        retained_count: int,
        tokens_reclaimed: int
    ) -> None:
        """Emit semantic purge event (EFFICIENCY METRIC)."""
        event = AuditLog(
            event_type=EventType.SEMANTIC_PURGE,
            agent_id="system",
            data={
                "old_model_version": old_model_version,
                "new_model_version": new_model_version,
                "purged_count": purged_count,
                "retained_count": retained_count,
                "tokens_reclaimed": tokens_reclaimed,
                "reduction_percentage": (
                    purged_count / (purged_count + retained_count) * 100
                    if (purged_count + retained_count) > 0 else 0
                )
            },
            severity="INFO"
        )
        event.emit()
        self.events.append(event)
    
    def emit_triage_decision(
        self,
        agent_id: str,
        strategy: str,
        reason: str,
        is_critical: bool,
        user_tier: Optional[str] = None
    ) -> None:
        """Emit triage routing decision."""
        event = AuditLog(
            event_type=EventType.TRIAGE_DECISION,
            agent_id=agent_id,
            data={
                "strategy": strategy,
                "reason": reason,
                "is_critical": is_critical,
                "user_tier": user_tier
            },
            severity="INFO"
        )
        event.emit()
        self.events.append(event)
    
    def get_events(self, event_type: Optional[EventType] = None) -> List[AuditLog]:
        """
        Get telemetry events for analysis.
        
        Args:
            event_type: Filter by event type (optional)
            
        Returns:
            List of audit log events
        """
        if event_type:
            return [e for e in self.events if e.event_type == event_type]
        return self.events
    
    def get_stats(self) -> Dict[str, Any]:
        """Get telemetry statistics."""
        return {
            "total_events": len(self.events),
            "events_by_type": {
                et.value: len([e for e in self.events if e.event_type == et])
                for et in EventType
            },
            "laziness_detected": len([
                e for e in self.events 
                if e.event_type == EventType.LAZINESS_DETECTED
            ]),
            "patches_created": len([
                e for e in self.events 
                if e.event_type == EventType.PATCH_CREATED
            ]),
            "semantic_purges": len([
                e for e in self.events 
                if e.event_type == EventType.SEMANTIC_PURGE
            ])
        }


class OutcomeAnalyzer:
    """
    Offline analyzer for telemetry data.
    
    Parses JSON logs to generate insights about:
    1. Correction Rate (how many failures fixed)
    2. Laziness Rate (how often agent gives up)
    3. Token Reduction (context efficiency)
    4. MTTR (Mean Time To Recovery)
    
    This is for the "experiments" - proving value delivery.
    """
    
    def __init__(self, telemetry_file: str):
        """
        Initialize outcome analyzer.
        
        Args:
            telemetry_file: Path to JSONL telemetry file
        """
        self.telemetry_file = telemetry_file
        self.events: List[Dict[str, Any]] = []
    
    def load_events(self) -> None:
        """Load events from JSONL file."""
        try:
            with open(self.telemetry_file, 'r') as f:
                for line in f:
                    if line.strip():
                        self.events.append(json.loads(line))
        except FileNotFoundError:
            logger.warning(f"Telemetry file not found: {self.telemetry_file}")
    
    def calculate_correction_rate(self) -> float:
        """
        Calculate percentage of failures successfully corrected.
        
        Returns:
            float: Correction rate (0.0 to 1.0)
        """
        failures = [e for e in self.events if e.get("event_type") == "failure_detected"]
        patches = [e for e in self.events if e.get("event_type") == "patch_applied"]
        
        if not failures:
            return 0.0
        
        return len(patches) / len(failures)
    
    def calculate_laziness_rate(self) -> float:
        """
        Calculate percentage of audits that found laziness.
        
        Returns:
            float: Laziness rate (0.0 to 1.0)
        """
        audits = [e for e in self.events if e.get("event_type") == "audit_triggered"]
        laziness = [e for e in self.events if e.get("event_type") == "laziness_detected"]
        
        if not audits:
            return 0.0
        
        return len(laziness) / len(audits)
    
    def calculate_token_reduction(self) -> Dict[str, float]:
        """
        Calculate token reduction from semantic purges.
        
        Returns:
            dict: Token reduction statistics
        """
        purges = [e for e in self.events if e.get("event_type") == "semantic_purge"]
        
        if not purges:
            return {"total_tokens_reclaimed": 0, "average_reduction_percentage": 0.0}
        
        total_reclaimed = sum(e.get("data", {}).get("tokens_reclaimed", 0) for e in purges)
        avg_reduction = sum(
            e.get("data", {}).get("reduction_percentage", 0) for e in purges
        ) / len(purges)
        
        return {
            "total_tokens_reclaimed": total_reclaimed,
            "average_reduction_percentage": avg_reduction,
            "purge_count": len(purges)
        }
