"""
Agent OS - A Safety-First Kernel for Autonomous AI Agents

Agent OS provides POSIX-inspired primitives for AI agent systems with
a 0% policy violation guarantee through kernel-level enforcement.

Architecture Layers:
    Layer 1 - Primitives: Base models, verification, context, memory
    Layer 2 - Infrastructure: Trust protocol, message bus, tool registry
    Layer 3 - Framework: Control plane, signals, VFS, kernel space
    Layer 4 - Intelligence: Self-correction, reasoning/execution split

Quick Start:
    >>> from agent_os import KernelSpace, AgentSignal, AgentVFS
    >>> kernel = KernelSpace()
    >>> ctx = kernel.create_agent_context("agent-001")
    >>> await ctx.write("/mem/working/task.txt", "Hello World")

Stateless API (MCP June 2026):
    >>> from agent_os import stateless_execute
    >>> result = await stateless_execute(
    ...     action="database_query",
    ...     params={"query": "SELECT * FROM users"},
    ...     agent_id="analyst-001",
    ...     policies=["read_only"]
    ... )

Installation:
    pip install agent-os-kernel[full]  # Everything
    pip install agent-os-kernel        # Core
"""

__version__ = "1.3.1"
__author__ = "Imran Siddique"
__license__ = "MIT"

# ============================================================================
# Layer 1: Primitives
# ============================================================================

# Agent Primitives - Base failure models
try:
    from agent_primitives import (
        AgentFailure,
        FailureType,
        FailureSeverity,
    )
    _PRIMITIVES_AVAILABLE = True
except ImportError:
    _PRIMITIVES_AVAILABLE = False

# CMVK - Cross-Model Verification Kernel
try:
    from cmvk import (
        DriftDetector,
        SemanticDrift,
        verify_outputs,
    )
    _CMVK_AVAILABLE = True
except ImportError:
    _CMVK_AVAILABLE = False

# CaaS - Context as a Service
try:
    from caas import (
        ContextPipeline,
        RAGContext,
    )
    _CAAS_AVAILABLE = True
except ImportError:
    _CAAS_AVAILABLE = False

# EMK - Episodic Memory Kernel
try:
    from emk import (
        EpisodicMemory,
        Episode,
        MemoryStore,
    )
    _EMK_AVAILABLE = True
except ImportError:
    _EMK_AVAILABLE = False

# ============================================================================
# Layer 2: Infrastructure
# ============================================================================

# IATP - Inter-Agent Trust Protocol
try:
    from iatp import (
        CapabilityManifest,
        TrustLevel,
        SidecarProxy,
        TypedPipe,
        Pipeline,
        PipeMessage,
        PolicyCheckPipe,
    )
    _IATP_AVAILABLE = True
except ImportError:
    _IATP_AVAILABLE = False

# AMB - Agent Message Bus
try:
    from amb_core import (
        MessageBus,
        Message,
        Topic,
    )
    _AMB_AVAILABLE = True
except ImportError:
    _AMB_AVAILABLE = False

# ATR - Agent Tool Registry
try:
    from atr import (
        ToolRegistry,
        Tool,
        ToolExecutor,
    )
    _ATR_AVAILABLE = True
except ImportError:
    _ATR_AVAILABLE = False

# ============================================================================
# Layer 3: Framework (Control Plane)
# ============================================================================

try:
    from agent_control_plane import (
        # Main Interface
        AgentControlPlane,
        create_control_plane,
        
        # Kernel Architecture (v0.3.0)
        AgentSignal,
        SignalDispatcher,
        AgentKernelPanic,
        SignalAwareAgent,
        kill_agent,
        pause_agent,
        resume_agent,
        policy_violation,
        
        # Agent VFS
        AgentVFS,
        VFSBackend,
        MemoryBackend,
        FileMode,
        create_agent_vfs,
        
        # Kernel/User Space
        KernelSpace,
        AgentContext,
        ProtectionRing,
        SyscallType,
        SyscallRequest,
        SyscallResult,
        KernelState,
        user_space_execution,
        create_kernel,
        
        # Policy Engine
        PolicyEngine,
        PolicyRule,
        
        # Flight Recorder
        FlightRecorder,
        
        # Execution
        ExecutionEngine,
        ExecutionStatus,
    )
    _CONTROL_PLANE_AVAILABLE = True
except ImportError:
    _CONTROL_PLANE_AVAILABLE = False

# ============================================================================
# Layer 4: Intelligence
# ============================================================================

# SCAK - Self-Correcting Agent Kernel
try:
    from agent_kernel import (
        SelfCorrectingKernel,
        LazinessDetector,
        DifferentialAuditor,
    )
    _SCAK_AVAILABLE = True
except ImportError:
    _SCAK_AVAILABLE = False

# Mute Agent
try:
    from mute_agent import (
        MuteAgent,
        ReasoningAgent,
        ExecutionAgent,
    )
    _MUTE_AGENT_AVAILABLE = True
except ImportError:
    _MUTE_AGENT_AVAILABLE = False

# ============================================================================
# Local Components (Always Available)
# ============================================================================

# Stateless Kernel (MCP June 2026)
from agent_os.stateless import (
    StatelessKernel,
    ExecutionContext,
    ExecutionRequest,
    ExecutionResult,
    MemoryBackend as StatelessMemoryBackend,
    stateless_execute,
)

# AGENTS.md Compatibility
from agent_os.agents_compat import (
    AgentsParser,
    AgentConfig as AgentsConfig,  # Renamed to avoid conflict
    AgentSkill,
    discover_agents,
)

# Base Agent Classes
from agent_os.base_agent import (
    BaseAgent,
    ToolUsingAgent,
    AgentConfig,
    AuditEntry,
    PolicyDecision,
    TypedResult,
)

# ============================================================================
# Availability Flags
# ============================================================================

AVAILABLE_PACKAGES = {
    "primitives": _PRIMITIVES_AVAILABLE if '_PRIMITIVES_AVAILABLE' in dir() else False,
    "cmvk": _CMVK_AVAILABLE if '_CMVK_AVAILABLE' in dir() else False,
    "caas": _CAAS_AVAILABLE if '_CAAS_AVAILABLE' in dir() else False,
    "emk": _EMK_AVAILABLE if '_EMK_AVAILABLE' in dir() else False,
    "iatp": _IATP_AVAILABLE if '_IATP_AVAILABLE' in dir() else False,
    "amb": _AMB_AVAILABLE if '_AMB_AVAILABLE' in dir() else False,
    "atr": _ATR_AVAILABLE if '_ATR_AVAILABLE' in dir() else False,
    "control_plane": _CONTROL_PLANE_AVAILABLE if '_CONTROL_PLANE_AVAILABLE' in dir() else False,
    "scak": _SCAK_AVAILABLE if '_SCAK_AVAILABLE' in dir() else False,
    "mute_agent": _MUTE_AGENT_AVAILABLE if '_MUTE_AGENT_AVAILABLE' in dir() else False,
}


def check_installation():
    """Check which Agent OS packages are installed."""
    print("Agent OS Installation Status:")
    print("=" * 40)
    for pkg, available in AVAILABLE_PACKAGES.items():
        status = "✓ Installed" if available else "✗ Not installed"
        print(f"  {pkg:15} {status}")
    print("=" * 40)
    print(f"\nInstall missing packages with:")
    print("  pip install agent-os-kernel[full]")


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "AVAILABLE_PACKAGES",
    "check_installation",
    
    # Layer 1: Primitives
    "AgentFailure",
    "FailureType",
    "FailureSeverity",
    "DriftDetector",
    "SemanticDrift",
    "verify_outputs",
    "ContextPipeline",
    "RAGContext",
    "EpisodicMemory",
    "Episode",
    "MemoryStore",
    
    # Layer 2: Infrastructure
    "CapabilityManifest",
    "TrustLevel",
    "SidecarProxy",
    "TypedPipe",
    "Pipeline",
    "PipeMessage",
    "PolicyCheckPipe",
    "MessageBus",
    "Message",
    "Topic",
    "ToolRegistry",
    "Tool",
    "ToolExecutor",
    
    # Layer 3: Framework
    "AgentControlPlane",
    "create_control_plane",
    "AgentSignal",
    "SignalDispatcher",
    "AgentKernelPanic",
    "SignalAwareAgent",
    "kill_agent",
    "pause_agent",
    "resume_agent",
    "policy_violation",
    "AgentVFS",
    "VFSBackend",
    "MemoryBackend",
    "FileMode",
    "create_agent_vfs",
    "KernelSpace",
    "AgentContext",
    "ProtectionRing",
    "SyscallType",
    "SyscallRequest",
    "SyscallResult",
    "KernelState",
    "user_space_execution",
    "create_kernel",
    "PolicyEngine",
    "PolicyRule",
    "FlightRecorder",
    "ExecutionEngine",
    "ExecutionStatus",
    
    # Layer 4: Intelligence
    "SelfCorrectingKernel",
    "LazinessDetector",
    "DifferentialAuditor",
    "MuteAgent",
    "ReasoningAgent",
    "ExecutionAgent",
    
    # Stateless API (MCP June 2026)
    "StatelessKernel",
    "ExecutionContext",
    "ExecutionRequest",
    "ExecutionResult",
    "StatelessMemoryBackend",
    "stateless_execute",
    
    # Base Agent Classes
    "BaseAgent",
    "ToolUsingAgent",
    "AgentConfig",
    "AuditEntry",
    "PolicyDecision",
    "TypedResult",
    
    # AGENTS.md Compatibility
    "AgentsParser",
    "AgentsConfig",
    "AgentSkill",
    "discover_agents",
]
