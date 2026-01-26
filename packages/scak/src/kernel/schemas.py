"""
Data contracts (schemas) for self-correcting agent kernel.

This module defines the rigorous data contracts between Auditor and Patcher.
These schemas use Pydantic to enforce type safety and can be exported
directly into Fine-Tuning datasets (RLAIF).

The "Spine" of the self-correcting system:
1. Lesson - The atomic unit of learning (what we learned)
2. FailureTrace - The evidence (what happened)
3. PatchRequest - The prescription (how to fix it)

v2 Extensions (Evolutionary Swarm):
4. SwarmTrace - Multi-agent interaction trace
5. RubricUpdate - Reward shaping changes
6. AnomalyDecision - Emergence detection results
7. Rubric - Reward scoring rubric
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from uuid import uuid4
from enum import Enum


class MemoryTier(str, Enum):
    """
    Three-tier memory hierarchy for deterministic lesson routing.
    
    This implements "Scale by Subtraction" by injecting only relevant context:
    - Tier 1: Always active (safety-critical)
    - Tier 2: Conditionally injected (tool-specific)
    - Tier 3: Retrieved on-demand (long-tail edge cases)
    """
    TIER_1_KERNEL = "kernel"           # Permanent System Prompt
    TIER_2_SKILL_CACHE = "skill_cache" # Injected based on active Tool
    TIER_3_ARCHIVE = "rag_archive"     # Semantic Search


# 1. The Atomic Lesson (What we learned)
class Lesson(BaseModel):
    """
    An atomic lesson learned from a failure.
    
    This represents a single, specific piece of knowledge that should
    be added to the agent's system prompt or memory to prevent future failures.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    trigger_pattern: str = Field(..., description="The context/keywords that triggered this failure")
    rule_text: str = Field(..., description="The actual instruction to add to System Prompt")
    lesson_type: Literal["syntax", "business", "security"] = Field(
        ...,
        description="Type of lesson: syntax (model capability), business (domain knowledge), security (safety rule)"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Teacher's confidence in this fix (0.0-1.0)"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Tiering metadata
    tier: Optional[MemoryTier] = Field(
        None,
        description="The memory tier where this lesson is stored"
    )
    retrieval_count: int = Field(
        default=0,
        description="Number of times this lesson was retrieved (for promotion logic)"
    )
    last_retrieved_at: Optional[datetime] = Field(
        None,
        description="Last time this lesson was retrieved from Tier 3"
    )
    last_triggered_at: Optional[datetime] = Field(
        None,
        description="Last time this lesson triggered a block/correction (for demotion logic)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "lesson-abc123",
                "trigger_pattern": "search logs, empty result, archived partition",
                "rule_text": "When searching logs, always check archived partitions if recent logs are empty",
                "lesson_type": "business",
                "confidence_score": 0.92,
                "created_at": "2026-01-15T23:00:00"
            }
        }
    }


# 2. The Failure Trace (The Evidence)
class FailureTrace(BaseModel):
    """
    Complete trace of a failure including evidence.
    
    This captures everything about what went wrong, including the user prompt,
    agent reasoning, tool execution, and the specific failure that occurred.
    """
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    user_prompt: str = Field(..., description="The user's original request")
    agent_reasoning: str = Field(..., description="The agent's reasoning/response")
    tool_call: Optional[Dict[str, Any]] = Field(
        None,
        description="The tool call that was made (if any)"
    )
    tool_output: Optional[str] = Field(
        None,
        description="The output from the tool execution"
    )
    failure_type: Literal["omission_laziness", "commission_safety", "hallucination"] = Field(
        ...,
        description="Type of failure: omission (gave up too early), commission (unsafe action), hallucination (invented facts)"
    )
    severity: Literal["critical", "non_critical"] = Field(
        ...,
        description="Severity of the failure"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "trace_id": "trace-xyz789",
                "user_prompt": "Find the Q3 report",
                "agent_reasoning": "I searched for 'Q3 report' but found no exact matches.",
                "tool_call": {"tool": "search_files", "query": "Q3 report"},
                "tool_output": "[]",
                "failure_type": "omission_laziness",
                "severity": "non_critical",
                "timestamp": "2026-01-15T23:00:00"
            }
        }
    }


# 3. The Patch (The Prescription)
class PatchRequest(BaseModel):
    """
    A request to patch an agent with a lesson.
    
    This combines the failure evidence (trace_id) with the diagnosis
    and proposed fix (lesson). It also specifies the application strategy
    (hotfix now vs batch later).
    """
    trace_id: str = Field(..., description="Reference to the FailureTrace that triggered this patch")
    diagnosis: str = Field(..., description="Why did it fail? Root cause analysis.")
    proposed_lesson: Lesson = Field(..., description="The lesson to apply")
    apply_strategy: Literal["hotfix_now", "batch_later"] = Field(
        ...,
        description="When to apply: hotfix_now (critical, sync) or batch_later (non-critical, async)"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the patch"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "trace_id": "trace-xyz789",
                "diagnosis": "Agent gave up after finding no exact match for 'Q3 report' without trying alternative search terms like 'Quarter 3' or 'Q3-2024'",
                "proposed_lesson": {
                    "id": "lesson-abc123",
                    "trigger_pattern": "search failure, no exact matches",
                    "rule_text": "When search returns no results, try alternative terms and synonyms before giving up",
                    "lesson_type": "business",
                    "confidence_score": 0.88
                },
                "apply_strategy": "batch_later",
                "context": {"priority": "medium"}
            }
        }
    }


# ========================================
# v2 SCHEMAS: Evolutionary Swarm Kernel
# ========================================

class SwarmStep(BaseModel):
    """
    A single step in multi-agent swarm interaction.
    
    Captures the message flow between agents for emergence detection.
    """
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    source: str = Field(..., description="Source agent ID")
    target: str = Field(..., description="Target agent ID")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    semantic_embedding: Optional[List[float]] = Field(
        None,
        description="Vector embedding for semantic drift detection"
    )


class SwarmTrace(BaseModel):
    """
    Complete trace of multi-agent swarm interaction.
    
    Used by EmergenceMonitor to detect anomalies across agent interactions.
    """
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    original_intent: str = Field(..., description="Original user prompt/goal")
    steps: List[SwarmStep] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    agent_ids: List[str] = Field(default_factory=list, description="All agents involved")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "trace_id": "swarm-abc123",
                "original_intent": "Analyze customer churn data",
                "steps": [
                    {
                        "source": "analyst-001",
                        "target": "verifier-001",
                        "content": "Found 15% churn rate"
                    }
                ],
                "agent_ids": ["analyst-001", "verifier-001"]
            }
        }
    }


class AnomalyType(str, Enum):
    """Types of emergent anomalies in swarm behavior."""
    INFINITE_LOOP = "infinite_loop"          # Circular approval
    GOAL_DRIFT = "goal_drift"                # Semantic divergence from original intent
    ECHO_CHAMBER = "echo_chamber"            # Repetitive similar content
    ESCALATION_SPIRAL = "escalation_spiral"  # Agents keep deferring to each other
    SAFE = "safe"                            # No anomaly detected


class AnomalyDecision(BaseModel):
    """
    Decision from EmergenceMonitor about swarm safety.
    
    Determines whether swarm execution should continue or be terminated.
    """
    is_anomaly: bool = Field(..., description="Whether an anomaly was detected")
    type: AnomalyType = Field(default=AnomalyType.SAFE)
    is_safe: bool = Field(default=True, description="Inverse of is_anomaly for clarity")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: Optional[str] = Field(None, description="Why this decision was made")
    suggested_action: Optional[str] = Field(None, description="Circuit breaker, retry, etc.")
    drift_score: Optional[float] = Field(None, description="Semantic distance from original intent")
    cycle_detected: bool = Field(default=False, description="Whether a graph cycle was found")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "is_anomaly": True,
                "type": "infinite_loop",
                "is_safe": False,
                "confidence": 0.95,
                "reasoning": "Agents A and B are in circular approval pattern (3 iterations)",
                "suggested_action": "CIRCUIT_BREAK"
            }
        }
    }


class Rubric(BaseModel):
    """
    Reward scoring rubric for agent behavior.
    
    Defines weights for different evaluation criteria.
    This is the dynamic part that RewardShaper adjusts.
    """
    rubric_id: str = Field(default_factory=lambda: str(uuid4()))
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "conciseness": 0.3,
            "accuracy": 0.5,
            "thoroughness": 0.2
        },
        description="Weights for different scoring criteria"
    )
    version: int = Field(default=1, description="Rubric version for tracking evolution")
    created_at: datetime = Field(default_factory=datetime.now)
    parent_rubric_id: Optional[str] = Field(None, description="Previous version if evolved")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "rubric_id": "rubric-v1",
                "weights": {
                    "conciseness": 0.4,  # Increased from 0.3 - user prefers brevity
                    "accuracy": 0.5,
                    "thoroughness": 0.1  # Decreased from 0.2
                },
                "version": 2
            }
        }
    }


class RubricUpdate(BaseModel):
    """
    An update to the reward rubric based on feedback.
    
    Generated by RewardShaper when adapting agent behavior.
    """
    update_id: str = Field(default_factory=lambda: str(uuid4()))
    rubric_before: Rubric = Field(..., description="Original rubric")
    rubric_after: Rubric = Field(..., description="Updated rubric")
    prompt_nudge: str = Field(..., description="Natural language instruction for agent")
    feedback_signal: str = Field(..., description="What triggered this update")
    correction_vector: Dict[str, float] = Field(
        ...,
        description="Delta for each weight (e.g., {'conciseness': +0.1})"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "update_id": "update-xyz",
                "feedback_signal": "User feedback: 'Too verbose'",
                "correction_vector": {
                    "conciseness": 0.1,     # Increase
                    "thoroughness": -0.1    # Decrease
                },
                "prompt_nudge": "Current Policy Update: Prioritize conciseness +15%. Reduce verbosity."
            }
        }
    }


class AgentPerformance(BaseModel):
    """
    Performance metrics for an agent in the swarm.
    
    Used by EvolvableOrchestrator to decide on hot-swapping.
    """
    agent_id: str
    role: str
    reward_score: float = Field(ge=0.0, description="Cumulative reward based on rubric")
    tasks_completed: int = Field(default=0)
    tasks_failed: int = Field(default=0)
    avg_latency_ms: float = Field(default=0.0)
    success_rate: float = Field(ge=0.0, le=1.0, description="tasks_completed / total_tasks")
    last_updated: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "agent_id": "analyst-001",
                "role": "analyst",
                "reward_score": 0.72,
                "tasks_completed": 45,
                "tasks_failed": 5,
                "success_rate": 0.9
            }
        }
    }


class AgentSwapDecision(BaseModel):
    """
    Decision to hot-swap an underperforming agent.
    
    Generated by EvolvableOrchestrator.
    """
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    old_agent_id: str
    new_agent_id: str
    reason: str = Field(..., description="Why the swap is needed")
    performance_before: AgentPerformance
    expected_improvement: Optional[float] = Field(None, description="Expected reward delta")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "old_agent_id": "analyst-basic",
                "new_agent_id": "analyst-senior",
                "reason": "Performance below threshold (0.65 < 0.70), swapping to stronger model",
                "expected_improvement": 0.15
            }
        }
    }
