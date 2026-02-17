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
from .token_budget import TokenBudgetTracker, TokenBudgetStatus
from .dry_run import DryRunPolicy, DryRunResult, DryRunDecision, DryRunCollector
from .rate_limiter import RateLimiter, RateLimitStatus
from .templates import PolicyTemplates
from .webhooks import WebhookConfig, WebhookEvent, WebhookNotifier, DeliveryRecord
from .policy_compose import compose_policies, PolicyHierarchy, override_policy
from .health import HealthChecker, HealthReport, HealthStatus, ComponentHealth
from agent_os.exceptions import (
    AgentOSError,
    PolicyError,
    PolicyViolationError,
    PolicyDeniedError,
    PolicyTimeoutError,
    BudgetError,
    BudgetExceededError,
    BudgetWarningError,
    IdentityError,
    IdentityVerificationError,
    CredentialExpiredError,
    IntegrationError,
    AdapterNotFoundError,
    AdapterTimeoutError,
    ConfigurationError,
    InvalidPolicyError,
    MissingConfigError,
    RateLimitError,
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
    # Token Budget Tracking
    "TokenBudgetTracker",
    "TokenBudgetStatus",
    # Dry Run
    "DryRunPolicy",
    "DryRunResult",
    "DryRunDecision",
    "DryRunCollector",
    # Rate Limiting
    "RateLimiter",
    "RateLimitStatus",
    # Policy Templates
    "PolicyTemplates",
    # Webhooks
    "WebhookConfig",
    "WebhookEvent",
    "WebhookNotifier",
    "DeliveryRecord",
    # Policy Composition
    "compose_policies",
    "PolicyHierarchy",
    "override_policy",
    # Exceptions
    "AgentOSError",
    "PolicyError",
    "PolicyViolationError",
    "PolicyDeniedError",
    "PolicyTimeoutError",
    "BudgetError",
    "BudgetExceededError",
    "BudgetWarningError",
    "IdentityError",
    "IdentityVerificationError",
    "CredentialExpiredError",
    "IntegrationError",
    "AdapterNotFoundError",
    "AdapterTimeoutError",
    "ConfigurationError",
    "InvalidPolicyError",
    "MissingConfigError",
    "RateLimitError",
    # Health Checks
    "HealthChecker",
    "HealthReport",
    "HealthStatus",
    "ComponentHealth",
]
