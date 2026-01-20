"""
LangChain Integration for Self-Correcting Agent Kernel (SCAK).

This module provides LangChain-compatible components that enable:
1. Automatic laziness detection and correction
2. Dynamic memory management with 3-Tier hierarchy
3. Runtime failure handling with self-correction

Usage:
    from scak.integrations.langchain import SCAKMemory, SCAKCallbackHandler, SelfCorrectingRunnable
"""

from .langchain_integration import (
    SCAKMemory,
    SCAKCallbackHandler,
    SelfCorrectingRunnable,
    create_scak_agent,
)

__all__ = [
    "SCAKMemory",
    "SCAKCallbackHandler",
    "SelfCorrectingRunnable",
    "create_scak_agent",
]
