"""
Agent OS Integrations

Adapters to wrap existing agent frameworks with Agent OS governance.

Supported Frameworks:
- LangChain: Chains, Agents, Runnables
- CrewAI: Crews and Agents
- AutoGen: Multi-agent conversations
- OpenAI Assistants: Assistants API with tools
- Semantic Kernel: Microsoft's AI orchestration framework

Usage:
    # LangChain
    from agent_os.integrations import LangChainKernel
    kernel = LangChainKernel()
    governed_chain = kernel.wrap(my_chain)
    
    # OpenAI Assistants
    from agent_os.integrations import OpenAIKernel
    kernel = OpenAIKernel()
    governed = kernel.wrap_assistant(assistant, client)
    
    # Semantic Kernel
    from agent_os.integrations import SemanticKernelWrapper
    governed = SemanticKernelWrapper().wrap(sk_kernel)
"""

from .langchain_adapter import LangChainKernel
from .crewai_adapter import CrewAIKernel
from .autogen_adapter import AutoGenKernel
from .openai_adapter import OpenAIKernel, GovernedAssistant
from .semantic_kernel_adapter import SemanticKernelWrapper, GovernedSemanticKernel
from .base import BaseIntegration, GovernancePolicy

__all__ = [
    # Base
    "BaseIntegration",
    "GovernancePolicy",
    # LangChain
    "LangChainKernel",
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
