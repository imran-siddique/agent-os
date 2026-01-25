"""
Circuit Breaker Pattern for Agent Loop Detection.

The Problem: Agents often get stuck in "I'm sorry, I can't do that" loops.
The Fix: A hard-coded heuristic in the kernel. If Action A is repeated 3x 
with same Result B, force a StopIteration exception or switch strategies.
Scale by Subtraction: Removes wasted tokens on stuck loops.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import deque
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, Field

from src.interfaces.telemetry import TelemetryEmitter, EventType


class LoopDetectionStrategy(str, Enum):
    """Strategy for handling detected loops."""
    STOP_ITERATION = "stop_iteration"  # Raise StopIteration exception
    SWITCH_STRATEGY = "switch_strategy"  # Switch to alternative strategy
    ESCALATE = "escalate"  # Escalate to supervisor/human


@dataclass
class ActionResultPair:
    """Represents an action and its result."""
    action: str
    action_params: Dict[str, Any]
    result: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def signature(self) -> str:
        """Create a signature for comparison (ignoring timestamp)."""
        # Create hashable representation of action + params
        params_str = str(sorted(self.action_params.items()))
        return f"{self.action}::{params_str}::{self.result}"


class LoopDetectedError(Exception):
    """Exception raised when a loop is detected."""
    
    def __init__(
        self,
        message: str,
        agent_id: str,
        loop_count: int,
        repeated_action: str,
        repeated_result: str,
        history: List[ActionResultPair]
    ):
        super().__init__(message)
        self.agent_id = agent_id
        self.loop_count = loop_count
        self.repeated_action = repeated_action
        self.repeated_result = repeated_result
        self.history = history


class CircuitBreakerState(BaseModel):
    """State of the circuit breaker for an agent."""
    
    agent_id: str
    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recent action-result pairs"
    )
    loop_detected: bool = Field(default=False)
    loop_count: int = Field(default=0)
    last_action_signature: Optional[str] = None
    consecutive_repetitions: int = Field(default=0)
    total_loops_detected: int = Field(default=0)
    strategy: LoopDetectionStrategy = Field(default=LoopDetectionStrategy.STOP_ITERATION)


class CircuitBreaker:
    """
    Circuit Breaker for detecting and breaking agent loops.
    
    Implements the pattern:
    If Action A is repeated 3x with same Result B → Break the loop.
    
    This prevents wasted tokens on stuck agents repeating the same
    failed action over and over.
    
    Architecture:
    - Tracks recent action-result pairs per agent
    - Detects consecutive repetitions (same signature 3x)
    - Raises LoopDetectedError or switches strategy
    - Emits structured telemetry for all events
    """
    
    def __init__(
        self,
        agent_id: str,
        repetition_threshold: int = 3,
        history_window: int = 10,
        strategy: LoopDetectionStrategy = LoopDetectionStrategy.STOP_ITERATION,
        telemetry: Optional[TelemetryEmitter] = None
    ):
        """
        Initialize circuit breaker for an agent.
        
        Args:
            agent_id: Agent identifier
            repetition_threshold: Number of repetitions to trigger circuit break (default: 3)
            history_window: Size of rolling window for tracking history (default: 10)
            strategy: Strategy for handling loops (default: STOP_ITERATION)
            telemetry: Telemetry emitter for structured logging
        """
        self.agent_id = agent_id
        self.repetition_threshold = repetition_threshold
        self.history_window = history_window
        self.strategy = strategy
        self.telemetry = telemetry or TelemetryEmitter(agent_id=agent_id)
        
        # Rolling window of recent action-result pairs
        self.history: deque[ActionResultPair] = deque(maxlen=history_window)
        
        # Loop detection state
        self.loop_detected = False
        self.loop_count = 0
        self.consecutive_repetitions = 0
        self.last_signature: Optional[str] = None
        self.total_loops_detected = 0
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "action": "circuit_breaker_initialized",
                "agent_id": agent_id,
                "repetition_threshold": repetition_threshold,
                "history_window": history_window,
                "strategy": strategy.value
            }
        )
    
    def record_action_result(
        self,
        action: str,
        action_params: Dict[str, Any],
        result: str
    ) -> bool:
        """
        Record an action-result pair and check for loops.
        
        Args:
            action: Action name (e.g., "search_logs", "query_db")
            action_params: Action parameters
            result: Result of the action (summary or error message)
            
        Returns:
            True if loop detected, False otherwise
            
        Raises:
            LoopDetectedError: If loop is detected and strategy is STOP_ITERATION
        """
        # Create action-result pair
        pair = ActionResultPair(
            action=action,
            action_params=action_params,
            result=result
        )
        
        # Add to history
        self.history.append(pair)
        
        # Get signature for comparison
        signature = pair.signature()
        
        # Check for repetition
        if signature == self.last_signature:
            self.consecutive_repetitions += 1
            
            self.telemetry.emit_event(
                event_type=EventType.AGENT_EXECUTION,
                data={
                    "action": "repetition_detected",
                    "agent_id": self.agent_id,
                    "consecutive_repetitions": self.consecutive_repetitions,
                    "action_name": action,
                    "threshold": self.repetition_threshold
                }
            )
            
            # Check if we've hit the threshold
            if self.consecutive_repetitions >= self.repetition_threshold:
                self.loop_detected = True
                self.loop_count += 1
                self.total_loops_detected += 1
                
                self.telemetry.emit_event(
                    event_type=EventType.FAILURE_DETECTED,
                    data={
                        "action": "loop_detected",
                        "agent_id": self.agent_id,
                        "loop_count": self.loop_count,
                        "total_loops_detected": self.total_loops_detected,
                        "repeated_action": action,
                        "repeated_result": result[:200],  # Truncate for telemetry
                        "consecutive_repetitions": self.consecutive_repetitions,
                        "strategy": self.strategy.value
                    }
                )
                
                # Handle based on strategy
                if self.strategy == LoopDetectionStrategy.STOP_ITERATION:
                    raise LoopDetectedError(
                        message=f"Agent {self.agent_id} stuck in loop: "
                                f"Action '{action}' repeated {self.consecutive_repetitions}x "
                                f"with same result. Breaking loop.",
                        agent_id=self.agent_id,
                        loop_count=self.loop_count,
                        repeated_action=action,
                        repeated_result=result,
                        history=list(self.history)
                    )
                elif self.strategy == LoopDetectionStrategy.SWITCH_STRATEGY:
                    # Reset state for strategy switch
                    self._reset_detection_state()
                    return True
                elif self.strategy == LoopDetectionStrategy.ESCALATE:
                    # Just flag and continue - caller handles escalation
                    return True
        else:
            # Different action or result - reset counter
            self.consecutive_repetitions = 1
            self.last_signature = signature
        
        return self.loop_detected
    
    def _reset_detection_state(self):
        """Reset loop detection state (but keep history)."""
        self.loop_detected = False
        self.consecutive_repetitions = 0
        self.last_signature = None
    
    def reset(self):
        """
        Reset circuit breaker completely (clear history and state).
        
        Use this when starting a new task or conversation.
        """
        self.history.clear()
        self._reset_detection_state()
        self.loop_count = 0
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "action": "circuit_breaker_reset",
                "agent_id": self.agent_id,
                "total_loops_detected": self.total_loops_detected
            }
        )
    
    def get_state(self) -> CircuitBreakerState:
        """Get current state of the circuit breaker."""
        return CircuitBreakerState(
            agent_id=self.agent_id,
            history=[
                {
                    "action": pair.action,
                    "params": pair.action_params,
                    "result": pair.result,
                    "timestamp": pair.timestamp.isoformat()
                }
                for pair in self.history
            ],
            loop_detected=self.loop_detected,
            loop_count=self.loop_count,
            last_action_signature=self.last_signature,
            consecutive_repetitions=self.consecutive_repetitions,
            total_loops_detected=self.total_loops_detected,
            strategy=self.strategy
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loop detection."""
        return {
            "agent_id": self.agent_id,
            "total_loops_detected": self.total_loops_detected,
            "current_loop_detected": self.loop_detected,
            "consecutive_repetitions": self.consecutive_repetitions,
            "history_size": len(self.history),
            "history_window": self.history_window,
            "repetition_threshold": self.repetition_threshold,
            "strategy": self.strategy.value
        }
    
    def detect_recent_loops(self) -> Optional[Tuple[str, int]]:
        """
        Analyze recent history for loop patterns.
        
        Returns:
            Tuple of (action_signature, repetition_count) if pattern found, else None
        """
        if len(self.history) < 2:
            return None
        
        # Count signature frequencies in recent history
        signature_counts: Dict[str, int] = {}
        for pair in self.history:
            sig = pair.signature()
            signature_counts[sig] = signature_counts.get(sig, 0) + 1
        
        # Find most repeated signature
        max_sig = max(signature_counts.items(), key=lambda x: x[1])
        
        if max_sig[1] >= 2:  # At least 2 repetitions
            return max_sig
        
        return None


class CircuitBreakerRegistry:
    """
    Registry for managing circuit breakers across multiple agents.
    
    This allows the kernel to manage circuit breakers for all agents
    from a central location.
    """
    
    def __init__(
        self,
        default_repetition_threshold: int = 3,
        default_history_window: int = 10,
        default_strategy: LoopDetectionStrategy = LoopDetectionStrategy.STOP_ITERATION,
        telemetry: Optional[TelemetryEmitter] = None
    ):
        """
        Initialize circuit breaker registry.
        
        Args:
            default_repetition_threshold: Default threshold for all breakers
            default_history_window: Default history window for all breakers
            default_strategy: Default strategy for all breakers
            telemetry: Shared telemetry emitter
        """
        self.default_repetition_threshold = default_repetition_threshold
        self.default_history_window = default_history_window
        self.default_strategy = default_strategy
        self.telemetry = telemetry or TelemetryEmitter(agent_id="circuit-breaker-registry")
        
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    def get_or_create(self, agent_id: str) -> CircuitBreaker:
        """
        Get existing circuit breaker or create new one for agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            CircuitBreaker instance for the agent
        """
        if agent_id not in self._breakers:
            self._breakers[agent_id] = CircuitBreaker(
                agent_id=agent_id,
                repetition_threshold=self.default_repetition_threshold,
                history_window=self.default_history_window,
                strategy=self.default_strategy,
                telemetry=self.telemetry
            )
        
        return self._breakers[agent_id]
    
    def reset_agent(self, agent_id: str):
        """Reset circuit breaker for specific agent."""
        if agent_id in self._breakers:
            self._breakers[agent_id].reset()
    
    def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            breaker.reset()
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {
            agent_id: breaker.get_statistics()
            for agent_id, breaker in self._breakers.items()
        }


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerRegistry",
    "LoopDetectedError",
    "LoopDetectionStrategy",
    "ActionResultPair",
    "CircuitBreakerState",
]
