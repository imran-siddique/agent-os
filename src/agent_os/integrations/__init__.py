"""
Agent OS Integrations

Adapters to wrap existing agent frameworks with Agent OS governance.

Supported Frameworks:
- LangChain: Chains, Agents, Runnables
- LlamaIndex: Query Engines, Chat Engines, Agents
- CrewAI: Crews and Agents
- AutoGen: Multi-agent conversations
- OpenAI Assistants: Assistants API with tools
- Anthropic Claude: Messages API with tool use
- Google Gemini: GenerativeModel with function calling
- Mistral AI: Chat API with tool calls
- Semantic Kernel: Microsoft's AI orchestration framework
- PydanticAI: Model-agnostic agents with tool governance

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
    governed = kernel.wrap(assistant, client)
    
    # Semantic Kernel
    from agent_os.integrations import SemanticKernelWrapper
    governed = SemanticKernelWrapper().wrap(sk_kernel)
"""

from agent_os.integrations.langchain_adapter import LangChainKernel
from agent_os.integrations.llamaindex_adapter import LlamaIndexKernel
from agent_os.integrations.crewai_adapter import CrewAIKernel
from agent_os.integrations.autogen_adapter import AutoGenKernel
from agent_os.integrations.openai_adapter import OpenAIKernel, GovernedAssistant
from agent_os.integrations.anthropic_adapter import AnthropicKernel, GovernedAnthropicClient
from agent_os.integrations.gemini_adapter import GeminiKernel, GovernedGeminiModel
from agent_os.integrations.mistral_adapter import MistralKernel, GovernedMistralClient
from agent_os.integrations.semantic_kernel_adapter import (
    SemanticKernelWrapper,
    GovernedSemanticKernel,
)
from agent_os.integrations.guardrails_adapter import GuardrailsKernel
from agent_os.integrations.google_adk_adapter import GoogleADKKernel
from agent_os.integrations.a2a_adapter import A2AGovernanceAdapter, A2APolicy, A2AEvaluation
from agent_os.integrations.pydantic_ai_adapter import PydanticAIKernel
from .base import (
    AsyncGovernedWrapper,
    BaseIntegration,
    DriftResult,
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
from .logging import GovernanceLogger, JSONFormatter, get_logger
from .config import AgentOSConfig, get_config, reset_config
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
    "DriftResult",
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
    # Anthropic Claude
    "AnthropicKernel",
    "GovernedAnthropicClient",
    # Google Gemini
    "GeminiKernel",
    "GovernedGeminiModel",
    # Mistral AI
    "MistralKernel",
    "GovernedMistralClient",
    # Semantic Kernel
    "SemanticKernelWrapper",
    "GovernedSemanticKernel",
    # Guardrails
    "GuardrailsKernel",
    # Google ADK
    "GoogleADKKernel",
    # A2A (Agent-to-Agent)
    "A2AGovernanceAdapter",
    "A2APolicy",
    "A2AEvaluation",
    # PydanticAI
    "PydanticAIKernel",
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
    # Structured Logging
    "GovernanceLogger",
    "JSONFormatter",
    "get_logger",
    # Environment Configuration
    "AgentOSConfig",
    "get_config",
    "reset_config",
]
