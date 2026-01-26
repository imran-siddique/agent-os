"""
Lazy Evaluation Hooks for Self-Correcting Agent Kernel.

The Fix: Allow the kernel to defer thinking. "I don't need to solve this now. 
I will create a TODO token and return."

Scale by Subtraction: Defer expensive computations until actually needed.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from src.interfaces.telemetry import TelemetryEmitter, EventType


class DeferralReason(str, Enum):
    """Reasons for deferring computation."""
    NOT_NEEDED_NOW = "not_needed_now"  # Not required for current task
    TOO_EXPENSIVE = "too_expensive"  # Computation too costly right now
    MISSING_CONTEXT = "missing_context"  # Need more info before computing
    LOW_PRIORITY = "low_priority"  # Can be done later
    SPECULATIVE = "speculative"  # Might not be needed at all


class TODOToken(BaseModel):
    """
    A TODO token representing deferred computation.
    
    This is the atomic unit of lazy evaluation. Instead of computing
    something immediately, we create a TODO token that can be resolved later.
    """
    
    token_id: str = Field(default_factory=lambda: f"todo-{uuid4().hex[:8]}")
    description: str = Field(..., description="What needs to be computed")
    reason: DeferralReason = Field(..., description="Why deferred")
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10 (10=highest)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context for resolution")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved: bool = Field(default=False)
    result: Optional[Any] = None
    
    # Metadata for tracking
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    estimated_cost_ms: Optional[int] = None  # Estimated computation time
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "token_id": "todo-abc123",
                "description": "Fetch historical logs from archived partition",
                "reason": "not_needed_now",
                "priority": 3,
                "context": {
                    "time_range": "2023-01-01 to 2023-12-31",
                    "partition": "archive_2023"
                },
                "estimated_cost_ms": 5000
            }
        }
    }


class DeferredTask(BaseModel):
    """
    A deferred task that can be executed later.
    
    More complex than a TODO token - includes the actual computation logic.
    """
    
    task_id: str = Field(default_factory=lambda: f"task-{uuid4().hex[:8]}")
    todo_token: TODOToken
    execution_function: Optional[str] = Field(
        None,
        description="Name/reference to function to execute"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Token IDs this task depends on"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "task-xyz789",
                "todo_token": {
                    "token_id": "todo-abc123",
                    "description": "Analyze user behavior patterns"
                },
                "execution_function": "analyze_user_behavior",
                "dependencies": ["todo-def456", "todo-ghi789"]
            }
        }
    }


class LazyEvaluationDecision(BaseModel):
    """
    Decision about whether to defer a computation.
    
    This encapsulates the decision-making logic for lazy evaluation.
    """
    
    should_defer: bool = Field(..., description="Whether to defer this computation")
    reason: DeferralReason = Field(..., description="Why defer (or not)")
    estimated_savings_ms: int = Field(default=0, description="Estimated time saved by deferring")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in decision")
    explanation: str = Field(default="", description="Human-readable explanation")


class LazyEvaluator:
    """
    Lazy Evaluation Engine for the Self-Correcting Agent Kernel.
    
    Implements "Scale by Subtraction" by deferring computations that:
    1. Are not needed immediately
    2. Are expensive and might not be needed at all
    3. Are speculative (exploratory queries)
    4. Require context that isn't available yet
    
    Architecture:
    - Decides what to defer based on heuristics
    - Creates TODO tokens for deferred work
    - Tracks deferred tasks for later resolution
    - Emits structured telemetry for all deferral decisions
    """
    
    def __init__(
        self,
        agent_id: str,
        enable_lazy_eval: bool = True,
        max_deferred_tasks: int = 100,
        telemetry: Optional[TelemetryEmitter] = None
    ):
        """
        Initialize lazy evaluator.
        
        Args:
            agent_id: Agent identifier
            enable_lazy_eval: Whether lazy evaluation is enabled (default: True)
            max_deferred_tasks: Maximum number of deferred tasks to track
            telemetry: Telemetry emitter for structured logging
        """
        self.agent_id = agent_id
        self.enable_lazy_eval = enable_lazy_eval
        self.max_deferred_tasks = max_deferred_tasks
        self.telemetry = telemetry or TelemetryEmitter(agent_id=agent_id)
        
        # Track TODO tokens and deferred tasks
        self.todo_tokens: Dict[str, TODOToken] = {}
        self.deferred_tasks: Dict[str, DeferredTask] = {}
        
        # Statistics
        self.total_deferrals = 0
        self.total_resolutions = 0
        self.total_savings_ms = 0
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "action": "lazy_evaluator_initialized",
                "agent_id": agent_id,
                "enable_lazy_eval": enable_lazy_eval,
                "max_deferred_tasks": max_deferred_tasks
            }
        )
    
    def should_defer(
        self,
        description: str,
        context: Dict[str, Any],
        estimated_cost_ms: Optional[int] = None
    ) -> LazyEvaluationDecision:
        """
        Decide whether a computation should be deferred.
        
        Args:
            description: Description of the computation
            context: Context for making the decision
            estimated_cost_ms: Estimated cost in milliseconds
            
        Returns:
            LazyEvaluationDecision with the verdict
        """
        if not self.enable_lazy_eval:
            return LazyEvaluationDecision(
                should_defer=False,
                reason=DeferralReason.NOT_NEEDED_NOW,  # Dummy reason
                confidence=1.0,
                explanation="Lazy evaluation disabled"
            )
        
        # Heuristics for deferral decision
        
        # Heuristic 1: High-cost operations (>2 seconds)
        if estimated_cost_ms and estimated_cost_ms > 2000:
            return LazyEvaluationDecision(
                should_defer=True,
                reason=DeferralReason.TOO_EXPENSIVE,
                estimated_savings_ms=estimated_cost_ms,
                confidence=0.9,
                explanation=f"Operation too expensive ({estimated_cost_ms}ms > 2000ms threshold)"
            )
        
        # Heuristic 2: Speculative queries (keywords: "might", "could", "possibly")
        desc_lower = description.lower()
        speculative_keywords = ["might", "could", "possibly", "maybe", "optional", "if needed"]
        if any(kw in desc_lower for kw in speculative_keywords):
            return LazyEvaluationDecision(
                should_defer=True,
                reason=DeferralReason.SPECULATIVE,
                estimated_savings_ms=estimated_cost_ms or 1000,
                confidence=0.8,
                explanation="Speculative computation detected"
            )
        
        # Heuristic 3: Missing context (keywords: "need", "require", "depends on")
        missing_context_keywords = ["need more", "require", "depends on", "waiting for"]
        if any(kw in desc_lower for kw in missing_context_keywords):
            return LazyEvaluationDecision(
                should_defer=True,
                reason=DeferralReason.MISSING_CONTEXT,
                estimated_savings_ms=estimated_cost_ms or 500,
                confidence=0.85,
                explanation="Missing required context for computation"
            )
        
        # Heuristic 4: Context flags (explicit deferral hints)
        if context.get("defer", False) or context.get("low_priority", False):
            priority = context.get("priority", 5)
            if priority < 5:  # Low priority (1-4)
                return LazyEvaluationDecision(
                    should_defer=True,
                    reason=DeferralReason.LOW_PRIORITY,
                    estimated_savings_ms=estimated_cost_ms or 500,
                    confidence=0.95,
                    explanation=f"Low priority task (priority={priority})"
                )
        
        # Heuristic 5: Archive/historical data queries (can be deferred)
        archive_keywords = ["archive", "historical", "old", "backup", "past"]
        if any(kw in desc_lower for kw in archive_keywords):
            # Only defer if not explicitly requested
            if not context.get("immediate", False):
                return LazyEvaluationDecision(
                    should_defer=True,
                    reason=DeferralReason.NOT_NEEDED_NOW,
                    estimated_savings_ms=estimated_cost_ms or 3000,
                    confidence=0.75,
                    explanation="Archive/historical query - can be deferred"
                )
        
        # Default: Don't defer
        return LazyEvaluationDecision(
            should_defer=False,
            reason=DeferralReason.NOT_NEEDED_NOW,
            confidence=0.6,
            explanation="No strong reason to defer"
        )
    
    def defer(
        self,
        description: str,
        reason: DeferralReason,
        context: Dict[str, Any],
        priority: int = 5,
        estimated_cost_ms: Optional[int] = None,
        task_id: Optional[str] = None
    ) -> TODOToken:
        """
        Defer a computation and create a TODO token.
        
        Args:
            description: What needs to be computed
            reason: Why it's being deferred
            context: Context for later resolution
            priority: Priority 1-10 (10=highest)
            estimated_cost_ms: Estimated computation time
            task_id: Optional task identifier
            
        Returns:
            TODOToken representing the deferred work
        """
        # Check if we're at capacity
        if len(self.todo_tokens) >= self.max_deferred_tasks:
            # Remove lowest priority completed token
            self._evict_lowest_priority_token()
        
        # Create TODO token
        token = TODOToken(
            description=description,
            reason=reason,
            priority=priority,
            context=context,
            agent_id=self.agent_id,
            task_id=task_id,
            estimated_cost_ms=estimated_cost_ms
        )
        
        # Store token
        self.todo_tokens[token.token_id] = token
        
        # Update statistics
        self.total_deferrals += 1
        if estimated_cost_ms:
            self.total_savings_ms += estimated_cost_ms
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "action": "computation_deferred",
                "agent_id": self.agent_id,
                "token_id": token.token_id,
                "description": description[:100],
                "reason": reason.value,
                "priority": priority,
                "estimated_cost_ms": estimated_cost_ms
            }
        )
        
        return token
    
    def resolve(
        self,
        token_id: str,
        result: Any
    ) -> bool:
        """
        Resolve a TODO token with actual result.
        
        Args:
            token_id: ID of the token to resolve
            result: Computed result
            
        Returns:
            True if resolved successfully, False if token not found
        """
        if token_id not in self.todo_tokens:
            return False
        
        token = self.todo_tokens[token_id]
        token.resolved = True
        token.resolved_at = datetime.utcnow()
        token.result = result
        
        # Update statistics
        self.total_resolutions += 1
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "action": "todo_token_resolved",
                "agent_id": self.agent_id,
                "token_id": token_id,
                "description": token.description[:100],
                "resolution_time_ms": (
                    (token.resolved_at - token.created_at).total_seconds() * 1000
                    if token.resolved_at else 0
                )
            }
        )
        
        return True
    
    def get_pending_tokens(self) -> List[TODOToken]:
        """Get all unresolved TODO tokens, sorted by priority."""
        pending = [t for t in self.todo_tokens.values() if not t.resolved]
        return sorted(pending, key=lambda t: t.priority, reverse=True)
    
    def get_resolved_tokens(self) -> List[TODOToken]:
        """Get all resolved TODO tokens."""
        return [t for t in self.todo_tokens.values() if t.resolved]
    
    def _evict_lowest_priority_token(self):
        """Remove lowest priority completed token to make room."""
        completed = [t for t in self.todo_tokens.values() if t.resolved]
        if completed:
            # Remove lowest priority completed token
            to_remove = min(completed, key=lambda t: t.priority)
            del self.todo_tokens[to_remove.token_id]
        else:
            # If no completed tokens, remove oldest pending low-priority token
            pending = [t for t in self.todo_tokens.values() if not t.resolved]
            low_priority = [t for t in pending if t.priority < 5]
            if low_priority:
                to_remove = min(low_priority, key=lambda t: t.created_at)
                del self.todo_tokens[to_remove.token_id]
    
    def clear_resolved(self):
        """Clear all resolved TODO tokens."""
        resolved_ids = [tid for tid, token in self.todo_tokens.items() if token.resolved]
        for tid in resolved_ids:
            del self.todo_tokens[tid]
        
        self.telemetry.emit_event(
            event_type=EventType.AGENT_EXECUTION,
            data={
                "action": "resolved_tokens_cleared",
                "agent_id": self.agent_id,
                "cleared_count": len(resolved_ids)
            }
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get lazy evaluation statistics."""
        pending = len([t for t in self.todo_tokens.values() if not t.resolved])
        resolved = len([t for t in self.todo_tokens.values() if t.resolved])
        
        return {
            "agent_id": self.agent_id,
            "enable_lazy_eval": self.enable_lazy_eval,
            "total_deferrals": self.total_deferrals,
            "total_resolutions": self.total_resolutions,
            "pending_tokens": pending,
            "resolved_tokens": resolved,
            "total_savings_ms": self.total_savings_ms,
            "total_savings_seconds": self.total_savings_ms / 1000,
            "resolution_rate": (
                self.total_resolutions / max(self.total_deferrals, 1)
            )
        }


class LazyEvaluatorRegistry:
    """
    Registry for managing lazy evaluators across multiple agents.
    
    Centralized management of lazy evaluation for all agents.
    """
    
    def __init__(
        self,
        enable_lazy_eval: bool = True,
        max_deferred_tasks: int = 100,
        telemetry: Optional[TelemetryEmitter] = None
    ):
        """
        Initialize lazy evaluator registry.
        
        Args:
            enable_lazy_eval: Global enable flag
            max_deferred_tasks: Default max deferred tasks per agent
            telemetry: Shared telemetry emitter
        """
        self.enable_lazy_eval = enable_lazy_eval
        self.max_deferred_tasks = max_deferred_tasks
        self.telemetry = telemetry or TelemetryEmitter(agent_id="lazy-evaluator-registry")
        
        self._evaluators: Dict[str, LazyEvaluator] = {}
    
    def get_or_create(self, agent_id: str) -> LazyEvaluator:
        """
        Get existing lazy evaluator or create new one for agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            LazyEvaluator instance for the agent
        """
        if agent_id not in self._evaluators:
            self._evaluators[agent_id] = LazyEvaluator(
                agent_id=agent_id,
                enable_lazy_eval=self.enable_lazy_eval,
                max_deferred_tasks=self.max_deferred_tasks,
                telemetry=self.telemetry
            )
        
        return self._evaluators[agent_id]
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all lazy evaluators."""
        return {
            agent_id: evaluator.get_statistics()
            for agent_id, evaluator in self._evaluators.items()
        }
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global statistics across all agents."""
        total_deferrals = sum(
            e.total_deferrals for e in self._evaluators.values()
        )
        total_resolutions = sum(
            e.total_resolutions for e in self._evaluators.values()
        )
        total_savings_ms = sum(
            e.total_savings_ms for e in self._evaluators.values()
        )
        
        return {
            "total_agents": len(self._evaluators),
            "total_deferrals": total_deferrals,
            "total_resolutions": total_resolutions,
            "total_savings_ms": total_savings_ms,
            "total_savings_seconds": total_savings_ms / 1000,
            "global_resolution_rate": (
                total_resolutions / max(total_deferrals, 1)
            )
        }


__all__ = [
    "LazyEvaluator",
    "LazyEvaluatorRegistry",
    "TODOToken",
    "DeferredTask",
    "DeferralReason",
    "LazyEvaluationDecision",
]
