"""
Agent OS Integrations

Adapters to wrap existing agent frameworks with Agent OS governance.

Supported Frameworks:
- LangChain: Chains, Agents, Runnables
- LlamaIndex: Query Engines, Chat Engines, Agents
- CrewAI: Crews and Agents
- AutoGen: Multi-agent conversations
- OpenAI Assistants: Assistants API with tools
- Semantic Kernel: Microsoft's AI orchestration framework

Usage:
    # LangChain
    from agent_os.integrations import LangChainKernel
    kernel = LangChainKernel()
    governed_chain = kernel.wrap(my_chain)
    
    # LlamaIndex
    from agent_os.integrations import LlamaIndexKernel
    kernel = LlamaIndexKernel()
    governed_engine = kernel.wrap(my_query_engine)
    
    # OpenAI Assistants
    from agent_os.integrations import OpenAIKernel
    kernel = OpenAIKernel()
    governed = kernel.wrap_assistant(assistant, client)
    
    # Semantic Kernel
    from agent_os.integrations import SemanticKernelWrapper
    governed = SemanticKernelWrapper().wrap(sk_kernel)
"""

from .langchain_adapter import LangChainKernel
from .llamaindex_adapter import LlamaIndexKernel
from .crewai_adapter import CrewAIKernel
from .autogen_adapter import AutoGenKernel
from .openai_adapter import OpenAIKernel, GovernedAssistant
from .semantic_kernel_adapter import SemanticKernelWrapper, GovernedSemanticKernel
from .base import (
    AsyncGovernedWrapper,
    BaseIntegration,
    GovernancePolicy,
    ToolCallInterceptor,
    ToolCallRequest,
    ToolCallResult,
    PolicyInterceptor,
    CompositeInterceptor,
    BoundedSemaphore,
)

__all__ = [
    # Base
    "AsyncGovernedWrapper",
    "BaseIntegration",
    "GovernancePolicy",
    # Tool Call Interceptor (vendor-neutral)
    "ToolCallInterceptor",
    "ToolCallRequest",
    "ToolCallResult",
    "PolicyInterceptor",
    "CompositeInterceptor",
    # Backpressure / Concurrency
    "BoundedSemaphore",
    # LangChain
    "LangChainKernel",
    # LlamaIndex
    "LlamaIndexKernel",
    # CrewAI
    "CrewAIKernel", 
    # AutoGen
    "AutoGenKernel",
    # OpenAI Assistants
    "OpenAIKernel",
    "GovernedAssistant",
    # Semantic Kernel
    "SemanticKernelWrapper",
    "GovernedSemanticKernel",
]
