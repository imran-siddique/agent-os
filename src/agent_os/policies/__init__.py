"""
Declarative policy language for Agent-OS governance.

Separates policy rules (YAML/JSON data) from evaluation logic,
enabling policies to be authored, versioned, and shared as plain files.
"""

from .bridge import document_to_governance, governance_to_document
from .evaluator import PolicyDecision, PolicyEvaluator
from .schema import (
    PolicyAction,
    PolicyCondition,
    PolicyDefaults,
    PolicyDocument,
    PolicyOperator,
    PolicyRule,
)

__all__ = [
    "PolicyAction",
    "PolicyCondition",
    "PolicyDecision",
    "PolicyDefaults",
    "PolicyDocument",
    "PolicyEvaluator",
    "PolicyOperator",
    "PolicyRule",
    "document_to_governance",
    "governance_to_document",
]
