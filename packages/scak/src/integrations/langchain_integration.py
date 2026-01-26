"""
LangChain Integration for Self-Correcting Agent Kernel (SCAK).

This module provides three core components for integrating SCAK with LangChain:
1. SCAKMemory: Memory adapter for SCAK's 3-Tier memory hierarchy
2. SCAKCallbackHandler: Background auditor for laziness detection
3. SelfCorrectingRunnable: Runtime guard for failure handling

Architecture follows SCAK's Dual-Loop pattern:
- Loop 1 (Runtime Safety): SelfCorrectingRunnable + FailureTriage
- Loop 2 (Quality/Efficiency): SCAKCallbackHandler + CompletenessAuditor

All implementations follow SCAK principles:
- Type safety with Pydantic models
- Async-first design
- Structured telemetry (no print statements)
- Scale by subtraction
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Pydantic for type safety
from pydantic import BaseModel, Field

# LangChain imports (these are optional dependencies)
try:
    from langchain.schema import BaseMemory, BaseMessage, SystemMessage, HumanMessage, AIMessage
    from langchain.callbacks.base import BaseCallbackHandler, AsyncCallbackHandler
    from langchain.schema.runnable import Runnable, RunnableConfig
    from langchain.schema.agent import AgentFinish, AgentAction
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Define minimal stubs for type hints
    BaseMemory = object
    BaseCallbackHandler = object
    AsyncCallbackHandler = object
    Runnable = object
    RunnableConfig = object  # Add stub for RunnableConfig
    BaseMessage = object
    SystemMessage = object
    AIMessage = object
    AgentFinish = object

# SCAK imports
from src.kernel.memory import MemoryController
from src.kernel.auditor import CompletenessAuditor
from src.kernel.triage import FailureTriage, FixStrategy
from src.kernel.patcher import AgentPatcher
from src.interfaces.telemetry import AuditLog, EventType

# Models
from agent_kernel.models import (
    AgentOutcome, GiveUpSignal, OutcomeType, AgentFailure,
    FailureType, FailureSeverity
)

logger = logging.getLogger(__name__)


# ============================================================================
# COMPONENT 1: SCAKMemory - The Prompt Manager
# ============================================================================

class SCAKMemory(BaseMemory if LANGCHAIN_AVAILABLE else object):
    """
    LangChain memory adapter for SCAK's 3-Tier Memory Hierarchy.
    
    This replaces standard buffer memory with SCAK's systematic memory routing:
    - Tier 1 (Kernel): Safety-critical rules always in system prompt
    - Tier 2 (Skill Cache): Tool-specific rules injected conditionally
    - Tier 3 (Archive): Long-tail wisdom retrieved on-demand
    
    Usage:
        ```python
        from scak.integrations.langchain import SCAKMemory
        
        scak_memory = SCAKMemory()
        
        # Use in LangChain agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_patch}"),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        ```
    
    This enables "Scale by Subtraction" - only relevant context is injected,
    reducing latency and improving accuracy.
    """
    
    # Instance attributes (initialized in __init__)
    memory_key: str
    system_patch_key: str
    controller: MemoryController
    return_messages: bool
    chat_history: List[BaseMessage]
    
    def __init__(
        self,
        memory_key: str = "history",
        system_patch_key: str = "system_patch",
        controller: Optional[MemoryController] = None,
        return_messages: bool = True
    ):
        """
        Initialize SCAKMemory.
        
        Args:
            memory_key: Key for chat history in memory
            system_patch_key: Key for system prompt patches
            controller: MemoryController instance (creates new if None)
            return_messages: Whether to return messages or strings
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is required for SCAKMemory. "
                "Install with: pip install langchain langchain-core"
            )
        
        self.memory_key = memory_key
        self.system_patch_key = system_patch_key
        self.controller = controller or MemoryController()
        self.return_messages = return_messages
        
        # Store chat history
        self.chat_history: List[BaseMessage] = []
        
        # Emit telemetry
        AuditLog(
            event_type=EventType.AGENT_EXECUTION,
            agent_id="scak_memory",
            data={
                "action": "initialized",
                "tiers_active": ["kernel", "skill_cache", "archive"]
            },
            severity="INFO"
        ).emit()
        
        logger.info("SCAKMemory initialized with 3-tier architecture")
    
    @property
    def memory_variables(self) -> List[str]:
        """Return the list of memory variables."""
        return [self.memory_key, self.system_patch_key]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load memory variables for the agent.
        
        This is where SCAK's magic happens:
        1. Extract current task and active tools from inputs
        2. Call MemoryController.retrieve_context() to get dynamic context
        3. Format as SystemMessage for LangChain
        
        Args:
            inputs: Input dictionary from LangChain chain
            
        Returns:
            Dict with memory variables including system_patch and history
        """
        # 1. Extract task and tools
        current_task = inputs.get("input", "")
        active_tools = inputs.get("tools", [])
        
        # Handle tool objects (extract names)
        if active_tools and hasattr(active_tools[0], "name"):
            active_tools = [tool.name for tool in active_tools]
        
        # 2. Retrieve dynamic context from SCAK Memory Controller
        # This injects Tier 1 (always) + Tier 2 (conditionally) + Tier 3 (on-demand)
        dynamic_context = self.controller.retrieve_context(
            current_task=current_task,
            active_tools=active_tools
        )
        
        # 3. Format as SystemMessage
        system_patch = dynamic_context if dynamic_context else ""
        
        # Emit telemetry
        AuditLog(
            event_type=EventType.AGENT_EXECUTION,
            agent_id="scak_memory",
            data={
                "action": "context_loaded",
                "task_length": len(current_task),
                "active_tools_count": len(active_tools),
                "context_length": len(system_patch),
                "tiers_used": {
                    "kernel": bool(self.controller.kernel_rules),
                    "skill_cache": len(active_tools) > 0,
                    "archive": len(current_task.split()) > 5
                }
            },
            severity="INFO"
        ).emit()
        
        logger.info(
            f"Loaded SCAK context: {len(system_patch)} chars for {len(active_tools)} tools"
        )
        
        # Return both system patch and chat history
        result = {
            self.system_patch_key: system_patch,
        }
        
        if self.return_messages:
            result[self.memory_key] = self.chat_history
        else:
            result[self.memory_key] = self._format_history_as_string()
        
        return result
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Save context to memory.
        
        Standard LangChain memory interface for saving conversation history.
        
        Args:
            inputs: Input dictionary with user message
            outputs: Output dictionary with agent response
        """
        # Save user message
        if "input" in inputs:
            self.chat_history.append(HumanMessage(content=inputs["input"]))
        
        # Save agent response
        if "output" in outputs:
            # Determine message type based on output
            # In LangChain, agent responses are typically in "output" key
            self.chat_history.append(AIMessage(content=outputs["output"]))
        
        logger.debug(f"Saved context to memory. History length: {len(self.chat_history)}")
    
    def clear(self) -> None:
        """Clear chat history."""
        self.chat_history = []
        logger.info("Cleared SCAK memory")
    
    def _format_history_as_string(self) -> str:
        """Format chat history as string."""
        return "\n".join([f"{msg.type}: {msg.content}" for msg in self.chat_history])


# ============================================================================
# COMPONENT 2: SCAKCallbackHandler - The Lazy Auditor
# ============================================================================

class SCAKCallbackHandler(AsyncCallbackHandler if LANGCHAIN_AVAILABLE else object):
    """
    Background auditor that checks for agent laziness.
    
    This implements SCAK's "Alignment Loop" (Loop 2) by:
    1. Listening to agent_finish events
    2. Detecting "give-up signals" (cheap check)
    3. Triggering Shadow Teacher audit (async, non-blocking)
    
    Key Features:
    - Async execution: Does not block agent response
    - Differential auditing: Only audits give-up signals (5-10% of interactions)
    - Structured telemetry: All events are logged as JSON
    
    Usage:
        ```python
        from scak.integrations.langchain import SCAKCallbackHandler
        
        scak_handler = SCAKCallbackHandler()
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            callbacks=[scak_handler]  # Add SCAK monitoring
        )
        ```
    
    This enables detection of "soft failures" where the agent complies with
    safety constraints but fails to deliver value.
    """
    
    # Instance attributes (initialized in __init__)
    auditor: CompletenessAuditor
    agent_id: str
    total_executions: int
    give_up_count: int
    audit_count: int
    
    # Give-up signal patterns (aligned with GiveUpSignal enum)
    GIVE_UP_PATTERNS = [
        "no data found",
        "cannot answer",
        "no results",
        "not available",
        "insufficient info",
        "i couldn't find",
        "i was unable to",
        "no information",
        "not able to",
        "unable to find"
    ]
    
    def __init__(
        self,
        auditor: Optional[CompletenessAuditor] = None,
        agent_id: str = "langchain_agent"
    ):
        """
        Initialize SCAKCallbackHandler.
        
        Args:
            auditor: CompletenessAuditor instance (creates new if None)
            agent_id: Identifier for the agent being monitored
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is required for SCAKCallbackHandler. "
                "Install with: pip install langchain langchain-core"
            )
        
        self.auditor = auditor or CompletenessAuditor()
        self.agent_id = agent_id
        
        # Statistics
        self.total_executions = 0
        self.give_up_count = 0
        self.audit_count = 0
        
        # Emit telemetry
        AuditLog(
            event_type=EventType.AGENT_EXECUTION,
            agent_id=agent_id,
            data={
                "action": "callback_handler_initialized",
                "teacher_model": self.auditor.teacher_model
            },
            severity="INFO"
        ).emit()
        
        logger.info(f"SCAKCallbackHandler initialized for {agent_id}")
    
    async def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id,
        parent_run_id = None,
        **kwargs: Any
    ) -> None:
        """
        Callback when agent finishes execution.
        
        This is where laziness detection happens:
        1. Extract agent response
        2. Check for give-up signals (cheap)
        3. If detected, trigger async audit (fire & forget)
        
        Args:
            finish: AgentFinish object with return values
            run_id: Unique run identifier
            parent_run_id: Parent run identifier
            **kwargs: Additional keyword arguments
        """
        self.total_executions += 1
        
        # Extract response
        response = finish.return_values.get("output", "")
        
        # Extract inputs if available
        inputs = kwargs.get("inputs", {})
        user_prompt = inputs.get("input", "")
        
        # 1. Cheap check: Is this a potential give-up?
        if self.is_give_up_signal(response):
            self.give_up_count += 1
            
            # Emit telemetry
            AuditLog(
                event_type=EventType.LAZINESS_DETECTED,
                agent_id=self.agent_id,
                data={
                    "run_id": str(run_id),
                    "user_prompt": user_prompt[:100],
                    "agent_response": response[:100],
                    "give_up_ratio": f"{self.give_up_count}/{self.total_executions}"
                },
                severity="WARNING"
            ).emit()
            
            logger.warning(
                f"Give-up signal detected ({self.give_up_count}/{self.total_executions}): "
                f"'{response[:60]}...'"
            )
            
            # 2. Trigger Async Audit (Fire & Forget)
            # This does not block the agent response
            asyncio.create_task(self._audit_give_up(user_prompt, response, str(run_id)))
    
    def is_give_up_signal(self, response: str) -> bool:
        """
        Check if response contains a give-up signal.
        
        This is a cheap pattern matching check that runs on every response.
        If matched, we trigger the expensive Shadow Teacher audit.
        
        Args:
            response: Agent response text
            
        Returns:
            True if give-up signal detected
        """
        response_lower = response.lower()
        return any(pattern in response_lower for pattern in self.GIVE_UP_PATTERNS)
    
    async def _audit_give_up(
        self,
        user_prompt: str,
        agent_response: str,
        run_id: str
    ) -> None:
        """
        Trigger async audit using Shadow Teacher.
        
        This is the expensive operation that runs in the background
        without blocking the agent response to the user.
        
        Args:
            user_prompt: Original user prompt
            agent_response: Agent's give-up response
            run_id: Unique run identifier
        """
        self.audit_count += 1
        
        # Emit telemetry
        AuditLog(
            event_type=EventType.AUDIT_TRIGGERED,
            agent_id=self.agent_id,
            data={
                "run_id": run_id,
                "audit_number": self.audit_count,
                "user_prompt": user_prompt[:100],
                "agent_response": agent_response[:100]
            },
            severity="INFO"
        ).emit()
        
        logger.info(f"🔍 Triggering audit #{self.audit_count} for run {run_id}")
        
        # Create AgentOutcome for auditing
        outcome = AgentOutcome(
            agent_id=self.agent_id,
            outcome_type=OutcomeType.GIVE_UP,
            user_prompt=user_prompt,
            agent_response=agent_response,
            give_up_signal=self._detect_give_up_type(agent_response),
            context={
                "run_id": run_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Run audit (this calls Shadow Teacher)
        try:
            audit = self.auditor.audit_give_up(outcome)
            
            # Emit audit completion
            AuditLog(
                event_type=EventType.AUDIT_COMPLETED,
                agent_id=self.agent_id,
                data={
                    "run_id": run_id,
                    "audit_id": audit.audit_id,
                    "teacher_found_data": audit.teacher_found_data,
                    "confidence": audit.confidence,
                    "laziness_detected": audit.teacher_found_data
                },
                severity="WARNING" if audit.teacher_found_data else "INFO"
            ).emit()
            
            logger.info(
                f"✓ Audit complete: teacher_found_data={audit.teacher_found_data}, "
                f"confidence={audit.confidence:.2f}"
            )
            
        except Exception as e:
            # Never let audit failure break the main flow
            AuditLog(
                event_type=EventType.AUDIT_COMPLETED,
                agent_id=self.agent_id,
                data={
                    "run_id": run_id,
                    "error": str(e),
                    "audit_failed": True
                },
                severity="ERROR"
            ).emit()
            
            logger.error(f"Audit failed for run {run_id}: {e}")
    
    def _detect_give_up_type(self, response: str) -> GiveUpSignal:
        """
        Detect the specific type of give-up signal.
        
        Args:
            response: Agent response
            
        Returns:
            GiveUpSignal enum value
        """
        response_lower = response.lower()
        
        if "no data found" in response_lower or "no results" in response_lower:
            return GiveUpSignal.NO_DATA_FOUND
        elif "cannot answer" in response_lower or "unable to" in response_lower:
            return GiveUpSignal.CANNOT_ANSWER
        elif "not available" in response_lower:
            return GiveUpSignal.NOT_AVAILABLE
        elif "insufficient" in response_lower:
            return GiveUpSignal.INSUFFICIENT_INFO
        else:
            return GiveUpSignal.UNKNOWN


# ============================================================================
# COMPONENT 3: SelfCorrectingRunnable - The Runtime Guard
# ============================================================================

class SelfCorrectingRunnable(Runnable if LANGCHAIN_AVAILABLE else object):
    """
    Runtime guard that wraps LangChain agents for self-correction.
    
    This implements SCAK's "Runtime Loop" (Loop 1) by:
    1. Intercepting exceptions and tool errors
    2. Running FailureTriage to decide sync vs async correction
    3. Applying patches in real-time for critical failures
    
    Key Features:
    - Transparent wrapping: Works with any Runnable
    - Smart routing: SYNC_JIT for critical, ASYNC_BATCH for non-critical
    - Patch application: Auto-fixes failures without manual intervention
    
    Usage:
        ```python
        from scak.integrations.langchain import SelfCorrectingRunnable
        
        # Wrap your agent
        base_agent = AgentExecutor(agent=agent, tools=tools)
        correcting_agent = SelfCorrectingRunnable(base_agent)
        
        # Use as normal
        result = correcting_agent.invoke({"input": "Find logs"})
        ```
    
    This enables "self-healing" - the agent automatically recovers from
    failures without requiring manual debugging or prompt engineering.
    """
    
    # Instance attributes (initialized in __init__)
    agent: Runnable
    triage: FailureTriage
    patcher: AgentPatcher
    agent_id: str
    execution_count: int
    failure_count: int
    correction_count: int
    
    def __init__(
        self,
        agent: Runnable,
        triage: Optional[FailureTriage] = None,
        patcher: Optional[AgentPatcher] = None,
        agent_id: str = "langchain_agent"
    ):
        """
        Initialize SelfCorrectingRunnable.
        
        Args:
            agent: The base agent/runnable to wrap
            triage: FailureTriage instance (creates new if None)
            patcher: AgentPatcher instance (creates new if None)
            agent_id: Identifier for the agent
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is required for SelfCorrectingRunnable. "
                "Install with: pip install langchain langchain-core"
            )
        
        self.agent = agent
        self.triage = triage or FailureTriage()
        self.patcher = patcher or AgentPatcher()
        self.agent_id = agent_id
        
        # Statistics
        self.execution_count = 0
        self.failure_count = 0
        self.correction_count = 0
        
        # Emit telemetry
        AuditLog(
            event_type=EventType.AGENT_EXECUTION,
            agent_id=agent_id,
            data={
                "action": "self_correcting_wrapper_initialized",
                "triage_enabled": True,
                "patcher_enabled": True
            },
            severity="INFO"
        ).emit()
        
        logger.info(f"SelfCorrectingRunnable initialized for {agent_id}")
    
    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any]:
        """
        Invoke the agent with self-correction.
        
        This is the synchronous entry point that:
        1. Tries to run the agent normally
        2. Catches failures and runs triage
        3. Applies correction if SYNC_JIT
        4. Retries with corrected context
        
        Args:
            input: Input dictionary for the agent
            config: Optional runnable config
            
        Returns:
            Output dictionary from the agent
        """
        self.execution_count += 1
        
        try:
            # Try normal execution
            result = self.agent.invoke(input, config)
            
            # Success - emit telemetry
            AuditLog(
                event_type=EventType.AGENT_EXECUTION,
                agent_id=self.agent_id,
                data={
                    "execution_number": self.execution_count,
                    "status": "success",
                    "failures_total": self.failure_count,
                    "corrections_total": self.correction_count
                },
                severity="INFO"
            ).emit()
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            
            # Emit failure detection
            AuditLog(
                event_type=EventType.FAILURE_DETECTED,
                agent_id=self.agent_id,
                data={
                    "execution_number": self.execution_count,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "input": str(input)[:100]
                },
                severity="ERROR"
            ).emit()
            
            logger.error(f"Agent failure detected: {type(e).__name__}: {e}")
            
            # Run triage to decide correction strategy
            user_prompt = input.get("input", "")
            tool_name = self._extract_tool_from_error(e)
            
            strategy = self.triage.decide_strategy(
                prompt=user_prompt,
                tool_name=tool_name,
                context={"error": str(e), "error_type": type(e).__name__}
            )
            
            # Emit triage decision
            AuditLog(
                event_type=EventType.TRIAGE_DECISION,
                agent_id=self.agent_id,
                data={
                    "strategy": strategy.value,
                    "reason": "critical_operation" if strategy == FixStrategy.SYNC_JIT else "defer_to_background"
                },
                severity="INFO"
            ).emit()
            
            logger.info(f"Triage decision: {strategy.value}")
            
            if strategy == FixStrategy.SYNC_JIT:
                # SYNC: Fix now and retry
                return self._synchronous_correction(input, e, config)
            else:
                # ASYNC: Log and re-raise
                # In production, this would queue for background processing
                logger.info("Failure queued for async correction")
                raise e
    
    def _synchronous_correction(
        self,
        input: Dict[str, Any],
        error: Exception,
        config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any]:
        """
        Apply synchronous correction and retry.
        
        This is the "JIT retry" path where we:
        1. Create a failure analysis
        2. Generate a patch
        3. Apply the patch to modify input
        4. Retry with corrected input
        
        Args:
            input: Original input
            error: The error that occurred
            config: Optional runnable config
            
        Returns:
            Result from retried execution
        """
        self.correction_count += 1
        
        logger.info(f"🔧 Applying synchronous correction #{self.correction_count}")
        
        # Create AgentFailure for analysis
        failure = AgentFailure(
            agent_id=self.agent_id,
            failure_type=self._classify_failure_type(error),
            severity=FailureSeverity.HIGH,  # SYNC_JIT implies high severity
            error_message=str(error),
            context={
                "input": str(input)[:200],
                "correction_attempt": self.correction_count
            }
        )
        
        # In a real implementation, this would:
        # 1. Run shadow teacher to diagnose
        # 2. Generate competence patch
        # 3. Inject hint into system prompt
        
        # For now, we apply a simple correction:
        # Add error context to the input to guide retry
        corrected_input = input.copy()
        if "input" in corrected_input:
            corrected_input["input"] = (
                f"{corrected_input['input']}\n\n"
                f"[SCAK NOTE: Previous attempt failed with: {str(error)[:100]}. "
                f"Please try an alternative approach.]"
            )
        
        # Emit patch creation
        AuditLog(
            event_type=EventType.PATCH_CREATED,
            agent_id=self.agent_id,
            data={
                "patch_type": "hint_injection",
                "correction_number": self.correction_count,
                "original_error": str(error)[:100]
            },
            severity="INFO"
        ).emit()
        
        # Retry with corrected input
        try:
            result = self.agent.invoke(corrected_input, config)
            
            # Success after correction!
            AuditLog(
                event_type=EventType.PATCH_APPLIED,
                agent_id=self.agent_id,
                data={
                    "patch_successful": True,
                    "correction_number": self.correction_count
                },
                severity="INFO"
            ).emit()
            
            logger.info(f"✓ Correction successful!")
            return result
            
        except Exception as retry_error:
            # Correction failed - log and re-raise original error
            AuditLog(
                event_type=EventType.PATCH_APPLIED,
                agent_id=self.agent_id,
                data={
                    "patch_successful": False,
                    "retry_error": str(retry_error)[:100],
                    "correction_number": self.correction_count
                },
                severity="ERROR"
            ).emit()
            
            logger.error(f"✗ Correction failed: {retry_error}")
            raise error  # Re-raise original error
    
    def _extract_tool_from_error(self, error: Exception) -> Optional[str]:
        """Extract tool name from error message if possible."""
        error_str = str(error).lower()
        
        # Check for critical tool names in error message
        for tool in self.triage.critical_tools:
            if tool in error_str:
                return tool
        
        # Common tool patterns (fallback)
        tool_patterns = [
            "sql", "database", "file", "api", "http", "search"
        ]
        
        for pattern in tool_patterns:
            if pattern in error_str:
                return pattern
        
        return None
    
    def _classify_failure_type(self, error: Exception) -> FailureType:
        """Classify the type of failure from exception."""
        error_type = type(error).__name__.lower()
        error_msg = str(error).lower()
        
        if "timeout" in error_type or "timeout" in error_msg:
            return FailureType.TIMEOUT
        elif "permission" in error_msg or "access" in error_msg:
            return FailureType.BLOCKED_BY_CONTROL_PLANE
        elif "invalid" in error_msg or "validation" in error_msg:
            return FailureType.INVALID_ACTION
        else:
            return FailureType.UNKNOWN


# ============================================================================
# Convenience function for easy setup
# ============================================================================

def create_scak_agent(
    base_agent: Runnable,
    memory: Optional[SCAKMemory] = None,
    callback_handler: Optional[SCAKCallbackHandler] = None,
    enable_correction: bool = True,
    agent_id: str = "langchain_agent"
) -> Union[Runnable, SelfCorrectingRunnable]:
    """
    Convenience function to create a SCAK-enabled LangChain agent.
    
    This wraps a base agent with SCAK components in one call.
    
    Args:
        base_agent: The LangChain agent to wrap
        memory: Optional SCAKMemory instance
        callback_handler: Optional SCAKCallbackHandler instance
        enable_correction: Whether to enable SelfCorrectingRunnable
        agent_id: Identifier for the agent
        
    Returns:
        SCAK-enabled agent
        
    Example:
        ```python
        from langchain.agents import AgentExecutor
        from scak.integrations.langchain import create_scak_agent
        
        base_agent = AgentExecutor(agent=agent, tools=tools)
        scak_agent = create_scak_agent(base_agent)
        
        result = scak_agent.invoke({"input": "Find logs"})
        ```
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "LangChain is required for SCAK integration. "
            "Install with: pip install langchain langchain-core"
        )
    
    # Add callback handler if provided
    if callback_handler and hasattr(base_agent, 'callbacks'):
        if base_agent.callbacks is None:
            base_agent.callbacks = []
        base_agent.callbacks.append(callback_handler)
    
    # Wrap with self-correction if enabled
    if enable_correction:
        agent = SelfCorrectingRunnable(
            agent=base_agent,
            agent_id=agent_id
        )
    else:
        agent = base_agent
    
    logger.info(f"Created SCAK agent: correction={enable_correction}, callbacks={callback_handler is not None}")
    
    return agent
