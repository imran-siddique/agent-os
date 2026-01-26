"""
Flight Recorder - Black Box Audit Logger for Agent Control Plane

This module provides SQLite-based audit logging for all agent actions,
capturing the exact state for forensic analysis and compliance.
"""

import sqlite3
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import logging


class FlightRecorder:
    """
    The Black Box Recorder for AI Agents.

    Logs every action attempt with full context for forensic analysis.
    Similar to an aircraft's flight data recorder, this captures:
    - Timestamp: When the action was attempted
    - AgentID: Which agent attempted it
    - InputPrompt: The original user/agent intent
    - IntendedAction: What the agent tried to do
    - PolicyVerdict: Whether it was allowed or blocked
    - Result: What actually happened
    """

    def __init__(self, db_path: str = "flight_recorder.db"):
        """
        Initialize the Flight Recorder.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger("FlightRecorder")
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create the main audit log table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                tool_args TEXT,
                input_prompt TEXT,
                policy_verdict TEXT NOT NULL,
                violation_reason TEXT,
                result TEXT,
                execution_time_ms REAL,
                metadata TEXT
            )
        """
        )

        # Create indexes for common queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_agent_id ON audit_log(agent_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_policy_verdict ON audit_log(policy_verdict)
        """
        )

        conn.commit()
        conn.close()

        self.logger.info(f"Flight Recorder initialized: {self.db_path}")

    def start_trace(
        self,
        agent_id: str,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        input_prompt: Optional[str] = None,
    ) -> str:
        """
        Start a new trace for an agent action.

        Args:
            agent_id: ID of the agent
            tool_name: Name of the tool being called
            tool_args: Arguments passed to the tool
            input_prompt: The original user/agent prompt (optional)

        Returns:
            trace_id: Unique identifier for this trace
        """
        trace_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO audit_log 
            (trace_id, timestamp, agent_id, tool_name, tool_args, input_prompt, policy_verdict)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """,
            (
                trace_id,
                timestamp,
                agent_id,
                tool_name,
                json.dumps(tool_args) if tool_args else None,
                input_prompt,
            ),
        )

        conn.commit()
        conn.close()

        return trace_id

    def log_violation(self, trace_id: str, violation_reason: str):
        """
        Log a policy violation for a trace.

        Args:
            trace_id: The trace ID from start_trace
            violation_reason: Why the action was blocked
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE audit_log 
            SET policy_verdict = 'blocked', 
                violation_reason = ?
            WHERE trace_id = ?
        """,
            (violation_reason, trace_id),
        )

        conn.commit()
        conn.close()

        self.logger.warning(f"BLOCKED: {trace_id} - {violation_reason}")

    def log_shadow_exec(self, trace_id: str, simulated_result: Optional[str] = None):
        """
        Log a shadow mode execution (simulated, not real).

        Args:
            trace_id: The trace ID from start_trace
            simulated_result: The simulated result returned to the agent
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE audit_log 
            SET policy_verdict = 'shadow', 
                result = ?
            WHERE trace_id = ?
        """,
            (simulated_result or "Simulated success", trace_id),
        )

        conn.commit()
        conn.close()

        self.logger.info(f"SHADOW: {trace_id}")

    def log_success(
        self, trace_id: str, result: Optional[Any] = None, execution_time_ms: Optional[float] = None
    ):
        """
        Log a successful execution.

        Args:
            trace_id: The trace ID from start_trace
            result: The result of the execution
            execution_time_ms: How long the execution took
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        result_str = (
            json.dumps(result)
            if result and not isinstance(result, str)
            else str(result) if result else None
        )

        cursor.execute(
            """
            UPDATE audit_log 
            SET policy_verdict = 'allowed', 
                result = ?,
                execution_time_ms = ?
            WHERE trace_id = ?
        """,
            (result_str, execution_time_ms, trace_id),
        )

        conn.commit()
        conn.close()

        self.logger.info(f"ALLOWED: {trace_id}")

    def log_error(self, trace_id: str, error: str):
        """
        Log an execution error.

        Args:
            trace_id: The trace ID from start_trace
            error: The error message
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE audit_log 
            SET policy_verdict = 'error', 
                violation_reason = ?
            WHERE trace_id = ?
        """,
            (error, trace_id),
        )

        conn.commit()
        conn.close()

        self.logger.error(f"ERROR: {trace_id} - {error}")

    def query_logs(
        self,
        agent_id: Optional[str] = None,
        policy_verdict: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list:
        """
        Query the audit logs with filters.

        Args:
            agent_id: Filter by agent ID
            policy_verdict: Filter by verdict (allowed, blocked, shadow, error)
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            limit: Maximum number of results

        Returns:
            List of audit log entries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if policy_verdict:
            query += " AND policy_verdict = ?"
            params.append(policy_verdict)

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the audit log.

        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total actions
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        total = cursor.fetchone()[0]

        # By verdict
        cursor.execute(
            """
            SELECT policy_verdict, COUNT(*) as count 
            FROM audit_log 
            GROUP BY policy_verdict
        """
        )
        by_verdict = {row[0]: row[1] for row in cursor.fetchall()}

        # By agent
        cursor.execute(
            """
            SELECT agent_id, COUNT(*) as count 
            FROM audit_log 
            GROUP BY agent_id
            ORDER BY count DESC
            LIMIT 10
        """
        )
        top_agents = [{"agent_id": row[0], "count": row[1]} for row in cursor.fetchall()]

        # Average execution time
        cursor.execute(
            """
            SELECT AVG(execution_time_ms) 
            FROM audit_log 
            WHERE execution_time_ms IS NOT NULL
        """
        )
        avg_exec_time = cursor.fetchone()[0]

        conn.close()

        return {
            "total_actions": total,
            "by_verdict": by_verdict,
            "top_agents": top_agents,
            "avg_execution_time_ms": avg_exec_time,
        }

    def close(self):
        """Clean up resources"""
        pass  # SQLite connections are opened/closed per operation
    
    # ===== Time-Travel Debugging Support =====
    
    def get_log(self) -> list:
        """
        Get the complete audit log for time-travel debugging.
        
        Returns:
            List of all audit log entries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT * FROM audit_log 
            ORDER BY timestamp ASC
            """
        )
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return results
    
    def get_events_in_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        agent_id: Optional[str] = None
    ) -> list:
        """
        Get events within a specific time range for time-travel replay.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            agent_id: Optional agent ID filter
            
        Returns:
            List of audit log entries in the time range
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM audit_log 
            WHERE timestamp >= ? AND timestamp <= ?
        """
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return results

