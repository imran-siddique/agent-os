"""
Worker - Standard Agent Wrapper.

This module provides a production-grade wrapper for standard agents,
implementing best practices for:
1. Type safety (Pydantic models)
2. Async/await for I/O operations
3. Structured telemetry (no print statements)
4. Proper error handling (no silent failures)

The Worker is the "Standard Agent" that the Kernel corrects when failures occur.
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# Import models from agent_kernel for backward compatibility
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from agent_kernel.models import AgentState, AgentOutcome, GiveUpSignal, OutcomeType


class AgentStatus(Enum):
    """Status of an agent."""
    IDLE = "idle"
    ACTIVE = "active"
    FAILED = "failed"
    PATCHED = "patched"
    BLOCKED = "blocked"


class AgentWorker:
    """
    Standard agent wrapper implementing production best practices.
    
    This is the "Worker Agent" that:
    1. Executes user tasks
    2. Reports outcomes with structured telemetry
    3. Gets corrected by the Kernel on failures
    4. Applies patches to improve performance
    
    Philosophy: No Silent Failures
    - Every try/except emits structured AuditLog event
    - Never just "pass" on errors
    """
    
    def __init__(
        self,
        agent_id: str,
        model: str = "gpt-4o",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agent worker.
        
        Args:
            agent_id: Unique identifier for this agent
            model: LLM model to use
            config: Optional configuration
        """
        self.agent_id = agent_id
        self.model = model
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.patches: List[Dict[str, Any]] = []
        self.execution_count = 0
        self.failure_count = 0
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"🤖 Agent {agent_id} initialized with model {model}")
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt with any applied patches.
        
        Returns:
            str: Complete system prompt
        """
        base_prompt = """You are a helpful AI assistant.
        
Follow these guidelines:
1. Be thorough in your searches
2. Check all available data sources
3. Validate parameters before tool calls
4. Never give up prematurely
5. Report errors with context
"""
        
        # Append patches
        if self.patches:
            patch_section = "\n\n## Learned Corrections:\n"
            for patch in self.patches:
                patch_section += f"- {patch['content']}\n"
            base_prompt += patch_section
        
        return base_prompt
    
    async def execute(
        self,
        user_prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentOutcome:
        """
        Execute a user task asynchronously.
        
        This is the main execution path. In production, this would:
        1. Call LLM API with system prompt + user prompt
        2. Execute any tool calls
        3. Capture complete execution trace
        4. Return structured outcome
        
        Args:
            user_prompt: User's task
            context: Optional context
            
        Returns:
            AgentOutcome with result and metadata
        """
        self.execution_count += 1
        self.status = AgentStatus.ACTIVE
        
        logger.info(f"▶️  Agent {self.agent_id} executing: {user_prompt[:60]}...")
        
        try:
            # Simulate execution (in production, this would be actual LLM call)
            response = await self._simulate_execution(user_prompt, context)
            
            # Detect give-up signals
            give_up_signal = self._detect_give_up_signal(response)
            
            # Determine outcome type
            if give_up_signal:
                outcome_type = OutcomeType.GIVE_UP
            else:
                outcome_type = OutcomeType.SUCCESS
            
            outcome = AgentOutcome(
                agent_id=self.agent_id,
                outcome_type=outcome_type,
                user_prompt=user_prompt,
                agent_response=response,
                give_up_signal=give_up_signal,
                context=context or {}
            )
            
            self.status = AgentStatus.IDLE
            
            if give_up_signal:
                logger.warning(f"⚠️  Agent gave up: {give_up_signal.value}")
            else:
                logger.info(f"✅ Agent completed successfully")
            
            return outcome
            
        except Exception as e:
            # No Silent Failures: Always emit structured log
            self.failure_count += 1
            self.status = AgentStatus.FAILED
            
            logger.error(f"❌ Agent {self.agent_id} failed: {str(e)}")
            
            # Emit structured telemetry (not just print)
            self._emit_failure_telemetry(user_prompt, str(e), context)
            
            # Re-raise for kernel to handle
            raise
    
    async def _simulate_execution(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Simulate agent execution.
        
        In production, this would:
        1. Call LLM API (OpenAI, Anthropic, etc.)
        2. Execute any tool calls
        3. Return final response
        
        For demonstration, we simulate based on patterns.
        """
        prompt_lower = prompt.lower()
        
        # Simulate different outcomes based on prompt
        if "error 500" in prompt_lower and "log" in prompt_lower:
            # Simulate giving up (will trigger Completeness Auditor)
            return "No logs found for error 500 in the recent logs directory."
        
        if "project alpha" in prompt_lower:
            # Simulate hallucination (entity doesn't exist)
            return "Project Alpha does not exist in the system."
        
        if "delete" in prompt_lower and "/etc/" in prompt_lower:
            # Simulate blocked action
            raise Exception("Action blocked by control plane: Unauthorized file access")
        
        # Default: Successful completion
        return f"Successfully completed the task: {prompt[:50]}"
    
    def _detect_give_up_signal(self, response: str) -> Optional[GiveUpSignal]:
        """
        Detect if agent gave up with negative result.
        
        This triggers Differential Auditing via Completeness Auditor.
        
        Args:
            response: Agent's response
            
        Returns:
            GiveUpSignal if detected, None otherwise
        """
        response_lower = response.lower()
        
        # Pattern matching for give-up signals
        if any(phrase in response_lower for phrase in ["no data found", "no logs found", "not found"]):
            return GiveUpSignal.NO_DATA_FOUND
        
        if any(phrase in response_lower for phrase in ["cannot answer", "insufficient", "don't have enough"]):
            return GiveUpSignal.INSUFFICIENT_INFO
        
        if any(phrase in response_lower for phrase in ["unable to", "cannot access", "cannot complete"]):
            return GiveUpSignal.CAPABILITY_LIMIT
        
        if any(phrase in response_lower for phrase in ["i'm sorry", "unfortunately"]):
            return GiveUpSignal.APOLOGETIC_REFUSAL
        
        return None
    
    def apply_patch(self, patch: Dict[str, Any]) -> None:
        """
        Apply a correction patch to this agent.
        
        Patches modify the agent's system prompt to prevent future failures.
        
        Args:
            patch: Patch to apply
        """
        self.patches.append({
            "patch_id": patch.get("patch_id", str(uuid.uuid4())),
            "content": patch.get("content", ""),
            "applied_at": datetime.now(),
            "decay_type": patch.get("decay_type", "unknown")
        })
        
        # Rebuild system prompt with new patch
        self.system_prompt = self._build_system_prompt()
        self.status = AgentStatus.PATCHED
        
        logger.info(f"🔧 Patch applied to {self.agent_id}: {patch.get('content', '')[:60]}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status with telemetry.
        
        Returns:
            dict: Structured status information
        """
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "model": self.model,
            "execution_count": self.execution_count,
            "failure_count": self.failure_count,
            "patches_applied": len(self.patches),
            "success_rate": (
                (self.execution_count - self.failure_count) / self.execution_count
                if self.execution_count > 0 else 0.0
            )
        }
    
    def _emit_failure_telemetry(
        self,
        prompt: str,
        error: str,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """
        Emit structured telemetry for offline analysis.
        
        NO print statements - only JSON structured logs.
        
        Args:
            prompt: User prompt
            error: Error message
            context: Execution context
        """
        telemetry = {
            "event_type": "agent_failure",
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "model": self.model,
            "prompt": prompt[:200],  # Truncate for privacy
            "error": error,
            "context": context,
            "execution_count": self.execution_count,
            "failure_count": self.failure_count
        }
        
        # In production, this would go to structured logging system
        # (e.g., JSON to stdout/stderr for log aggregation)
        logger.error(f"TELEMETRY: {telemetry}")


class WorkerPool:
    """
    Manages a pool of agent workers.
    
    Provides:
    1. Load balancing across multiple agents
    2. Failure isolation
    3. Coordinated patch application
    """
    
    def __init__(self):
        self.workers: Dict[str, AgentWorker] = {}
    
    def create_worker(
        self,
        agent_id: str,
        model: str = "gpt-4o",
        config: Optional[Dict[str, Any]] = None
    ) -> AgentWorker:
        """Create a new worker agent."""
        worker = AgentWorker(agent_id, model, config)
        self.workers[agent_id] = worker
        return worker
    
    def get_worker(self, agent_id: str) -> Optional[AgentWorker]:
        """Get worker by ID."""
        return self.workers.get(agent_id)
    
    def apply_patch_to_all(self, patch: Dict[str, Any]) -> None:
        """Apply patch to all workers in the pool."""
        for worker in self.workers.values():
            worker.apply_patch(patch)
        
        logger.info(f"📡 Patch broadcast to {len(self.workers)} workers")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get statistics for the entire pool."""
        return {
            "total_workers": len(self.workers),
            "active_workers": sum(1 for w in self.workers.values() if w.status == AgentStatus.ACTIVE),
            "failed_workers": sum(1 for w in self.workers.values() if w.status == AgentStatus.FAILED),
            "total_executions": sum(w.execution_count for w in self.workers.values()),
            "total_failures": sum(w.failure_count for w in self.workers.values())
        }
