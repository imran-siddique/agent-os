"""
Agent Control Plane

A governance and management layer for autonomous AI agents.
"""

from .agent_kernel import (
    AgentKernel,
    AgentContext,
    ExecutionRequest,
    ExecutionResult,
    ActionType,
    PermissionLevel,
    ExecutionStatus,
    PolicyRule,
)

from .policy_engine import (
    PolicyEngine,
    ResourceQuota,
    RiskPolicy,
    Condition,
    ConditionalPermission,
    create_default_policies,
)

from .flight_recorder import (
    FlightRecorder,
)

from .execution_engine import (
    ExecutionEngine,
    ExecutionContext,
    SandboxLevel,
    ExecutionMetrics,
)

from .control_plane import (
    AgentControlPlane,
    create_read_only_agent,
    create_standard_agent,
    create_admin_agent,
)

from .adapter import (
    ControlPlaneAdapter,
    create_governed_client,
    DEFAULT_TOOL_MAPPING,
)

from .langchain_adapter import (
    LangChainAdapter,
    create_governed_langchain_client,
    DEFAULT_LANGCHAIN_TOOL_MAPPING,
)

from .mcp_adapter import (
    MCPAdapter,
    MCPServer,
    create_governed_mcp_server,
)

from .a2a_adapter import (
    A2AAdapter,
    A2AAgent,
    create_governed_a2a_agent,
)

from .tool_registry import (
    ToolRegistry,
    Tool,
    ToolType,
    ToolSchema,
    create_standard_tool_registry,
)

from .orchestrator import (
    AgentOrchestrator,
    AgentNode,
    AgentRole,
    Message,
    MessageType,
    OrchestrationType,
    WorkflowState,
    create_rag_pipeline,
)

from .governance_layer import (
    GovernanceLayer,
    AlignmentPrinciple,
    AlignmentRule,
    BiasType,
    BiasDetectionResult,
    PrivacyLevel,
    PrivacyAnalysis,
    create_default_governance,
)

__version__ = "0.1.0"
__author__ = "Agent Control Plane Contributors"

__all__ = [
    # Main interface
    "AgentControlPlane",
    "create_read_only_agent",
    "create_standard_agent",
    "create_admin_agent",
    
    # OpenAI Adapter (Drop-in Middleware)
    "ControlPlaneAdapter",
    "create_governed_client",
    "DEFAULT_TOOL_MAPPING",
    
    # LangChain Adapter
    "LangChainAdapter",
    "create_governed_langchain_client",
    "DEFAULT_LANGCHAIN_TOOL_MAPPING",
    
    # MCP (Model Context Protocol) Adapter
    "MCPAdapter",
    "MCPServer",
    "create_governed_mcp_server",
    
    # A2A (Agent-to-Agent) Adapter
    "A2AAdapter",
    "A2AAgent",
    "create_governed_a2a_agent",
    
    # Tool Registry (Dynamic Tool Management)
    "ToolRegistry",
    "Tool",
    "ToolType",
    "ToolSchema",
    "create_standard_tool_registry",
    
    # Multi-Agent Orchestration
    "AgentOrchestrator",
    "AgentNode",
    "AgentRole",
    "Message",
    "MessageType",
    "OrchestrationType",
    "WorkflowState",
    "create_rag_pipeline",
    
    # Governance Layer (Ethical Alignment & Advanced Safety)
    "GovernanceLayer",
    "AlignmentPrinciple",
    "AlignmentRule",
    "BiasType",
    "BiasDetectionResult",
    "PrivacyLevel",
    "PrivacyAnalysis",
    "create_default_governance",
    
    # Kernel
    "AgentKernel",
    "AgentContext",
    "ExecutionRequest",
    "ExecutionResult",
    "PolicyRule",
    
    # Enums
    "ActionType",
    "PermissionLevel",
    "ExecutionStatus",
    "SandboxLevel",
    
    # Policy
    "PolicyEngine",
    "ResourceQuota",
    "RiskPolicy",
    "Condition",
    "ConditionalPermission",
    "create_default_policies",
    
    # Audit
    "FlightRecorder",
    
    # Execution
    "ExecutionEngine",
    "ExecutionContext",
    "ExecutionMetrics",
]
