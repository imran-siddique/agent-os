"""Kernel components for SCAK Layer 4.

Core Components:
- core.py: SelfCorrectingKernel - Main orchestrator with CMVK integration
- triage.py: FailureTriage - Sync/Async decision engine
- memory.py: SemanticPurge, MemoryManager - Patch lifecycle management
- auditor.py: CompletenessAuditor - Laziness detection (via agent_kernel)
- patcher.py: AgentPatcher - Patch application (via agent_kernel)

Layer 4 Architecture:
    SCAK implements self-correction as a Control Plane extension,
    using CMVK for verification. No application-specific logic.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Layer 4 Core Kernel
from .core import SelfCorrectingKernel, CorrectionResult, create_kernel

# Triage Engine
from .triage import FailureTriage, FixStrategy

# Memory & Patch Lifecycle
from .memory import (
    MemoryManager, PatchClassifier, SemanticPurge, LessonType,
    MemoryController, MockRedisCache, MockVectorStore
)

# Skill Mapping
from .skill_mapper import SkillMapper, ToolSignature

# Lesson Rubric
from .rubric import LessonRubric

# Circuit Breaker (Loop Detection)
from .circuit_breaker import (
    CircuitBreaker, CircuitBreakerRegistry, LoopDetectedError,
    LoopDetectionStrategy, ActionResultPair, CircuitBreakerState
)

# Lazy Evaluation Hooks
from .lazy_evaluator import (
    LazyEvaluator, LazyEvaluatorRegistry, TODOToken, DeferredTask,
    DeferralReason, LazyEvaluationDecision
)

# Backward compatibility: auditor and patcher from agent_kernel
from agent_kernel.completeness_auditor import CompletenessAuditor
from agent_kernel.patcher import AgentPatcher

__all__ = [
    # Layer 4 Core
    "SelfCorrectingKernel",
    "CorrectionResult",
    "create_kernel",
    
    # Triage
    "FailureTriage",
    "FixStrategy",
    
    # Memory
    "MemoryManager",
    "PatchClassifier",
    "SemanticPurge",
    "LessonType",
    "MemoryController",
    "MockRedisCache",
    "MockVectorStore",
    
    # Skill Mapping
    "SkillMapper",
    "ToolSignature",
    
    # Rubric
    "LessonRubric",
    
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerRegistry",
    "LoopDetectedError",
    "LoopDetectionStrategy",
    "ActionResultPair",
    "CircuitBreakerState",
    
    # Lazy Evaluation
    "LazyEvaluator",
    "LazyEvaluatorRegistry",
    "TODOToken",
    "DeferredTask",
    "DeferralReason",
    "LazyEvaluationDecision",
    
    # Legacy (backward compat)
    "CompletenessAuditor",
    "AgentPatcher",
]
