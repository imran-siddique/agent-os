"""
Self-Correcting Agent Kernel

A Dual-Loop Architecture for Enterprise Agents:
- Loop 1 (Runtime): Constraint Engine (Safety)
- Loop 2 (Offline): Alignment Engine (Quality & Efficiency)
  - Completeness Auditor (detects laziness)
  - Semantic Purge (scales by subtraction)

Reference Implementations:
- auditor.py: Simplified soft failure detection
- teacher.py: Shadow Teacher diagnosis
- memory_manager.py: Lesson lifecycle management
"""

__version__ = "0.2.0"

from .kernel import SelfCorrectingAgentKernel
from .models import (
    AgentFailure, FailureAnalysis, CorrectionPatch,
    AgentOutcome, CompletenessAudit, ClassifiedPatch,
    OutcomeType, GiveUpSignal, PatchDecayType
)
from .outcome_analyzer import OutcomeAnalyzer
from .completeness_auditor import CompletenessAuditor
from .semantic_purge import SemanticPurge, PatchClassifier

# Reference implementations (simplified examples)
from .auditor import CompletenessAuditor as SimpleCompletenessAuditor
from .teacher import diagnose_failure
from .memory_manager import MemoryManager, LessonType

__all__ = [
    "SelfCorrectingAgentKernel",
    "AgentFailure",
    "FailureAnalysis",
    "CorrectionPatch",
    "AgentOutcome",
    "CompletenessAudit",
    "ClassifiedPatch",
    "OutcomeType",
    "GiveUpSignal",
    "PatchDecayType",
    "OutcomeAnalyzer",
    "CompletenessAuditor",
    "SemanticPurge",
    "PatchClassifier",
    # Reference implementations
    "SimpleCompletenessAuditor",
    "diagnose_failure",
    "MemoryManager",
    "LessonType",
]
