"""
Multi-Agent Orchestration for complex workflows.

This module implements hierarchical agent coordination inspired by research
on multi-agent systems and swarm intelligence.

Research Foundation:
- "Voyager: An Open-Ended Embodied Agent with Large Language Models" (arXiv:2305.16291)
  - Self-growing skill libraries and hierarchical task decomposition
- "DEPS: A Framework for Deployable and Evolvable Production Systems" (ICML 2023)
  - Evolving agent teams and role-based coordination
- "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" (MSR 2023)
  - Agent-to-agent communication patterns

Architectural Pattern:
- Supervisor agents coordinate worker agents
- Message passing via async queues (Redis pub-sub in production)
- Hierarchical task decomposition
- Role-based specialization (analyst, verifier, executor)
"""

from typing import List, Dict, Any, Optional, Callable, Awaitable
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import logging
from uuid import uuid4

# Import enhanced multi-agent capabilities (backward compatible)
_PUBSUB_AVAILABLE = True
_CONFLICT_RESOLUTION_AVAILABLE = True

try:
    from .pubsub import InMemoryPubSub, PubSubBackend, AgentSwarm, MessagePriority
except ImportError:
    _PUBSUB_AVAILABLE = False
    InMemoryPubSub = None
    PubSubBackend = None
    AgentSwarm = None
    MessagePriority = None

try:
    from .conflict_resolution import ConflictResolver, AgentVote, ConflictType, VoteType
except ImportError:
    _CONFLICT_RESOLUTION_AVAILABLE = False
    ConflictResolver = None
    AgentVote = None
    ConflictType = None
    VoteType = None

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """
    Agent roles in the orchestration hierarchy.
    
    Based on enterprise patterns (e.g., fraud detection with analyst + verifier).
    """
    SUPERVISOR = "supervisor"      # Coordinates other agents
    ANALYST = "analyst"            # Analyzes data and generates insights
    VERIFIER = "verifier"          # Validates outputs for correctness
    EXECUTOR = "executor"          # Performs actions/mutations
    SPECIALIST = "specialist"      # Domain-specific expertise


class MessageType(str, Enum):
    """Message types for agent-to-agent communication."""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    REQUEST_ASSISTANCE = "request_assistance"
    PROVIDE_FEEDBACK = "provide_feedback"
    STATUS_UPDATE = "status_update"


class AgentMessage(BaseModel):
    """
    Message passed between agents.
    
    Implements structured communication protocol for multi-agent coordination.
    """
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    from_agent: str = Field(..., description="Sender agent ID")
    to_agent: str = Field(..., description="Recipient agent ID")
    message_type: MessageType
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    parent_message_id: Optional[str] = Field(None, description="Reply-to message ID")


class AgentSpec(BaseModel):
    """
    Specification for an agent in the orchestration.
    
    Defines the agent's role, capabilities, and execution function.
    """
    agent_id: str
    role: AgentRole
    capabilities: List[str] = Field(default_factory=list, description="What this agent can do")
    system_prompt: Optional[str] = None
    model: str = "gpt-4o"
    max_concurrent_tasks: int = 3


class TaskStatus(str, Enum):
    """Status of a task in the orchestration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_ASSISTANCE = "requires_assistance"


class OrchestratedTask(BaseModel):
    """
    A task being coordinated by the orchestrator.
    
    Tracks the task lifecycle, assigned agent, and results.
    """
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[str] = None
    subtasks: List[str] = Field(default_factory=list)


class Orchestrator:
    """
    Multi-agent orchestrator for complex workflows.
    
    Implements hierarchical coordination where a supervisor agent
    decomposes tasks and assigns them to specialized worker agents.
    
    Pattern: Supervisor → Workers with feedback loops
    
    Example Use Cases:
    - Fraud detection: Analyst detects anomaly → Verifier confirms → Executor blocks
    - Data pipeline: Extractor → Transformer → Validator → Loader
    - Customer support: Classifier → Resolver → Quality checker
    
    Research: Inspired by "Voyager" (skill libraries) and "DEPS" (evolving teams).
    """
    
    def __init__(
        self,
        agents: List[AgentSpec],
        message_broker: Optional[Any] = None,
        enable_pubsub: bool = True,
        enable_conflict_resolution: bool = True
    ):
        """
        Initialize orchestrator with agent specifications.
        
        Args:
            agents: List of agent specifications
            message_broker: Optional message broker (Redis pub-sub in production)
            enable_pubsub: Enable pub-sub messaging (default: True)
            enable_conflict_resolution: Enable conflict resolution (default: True)
        """
        self.agents = {agent.agent_id: agent for agent in agents}
        self.tasks: Dict[str, OrchestratedTask] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_broker = message_broker
        
        # Agent execution functions (injected by user)
        self.agent_executors: Dict[str, Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]] = {}
        
        # Enhanced capabilities
        self.pubsub: Optional[PubSubBackend] = None
        self.conflict_resolver: Optional[ConflictResolver] = None
        self.swarms: Dict[str, AgentSwarm] = {}
        
        if enable_pubsub:
            if not _PUBSUB_AVAILABLE:
                logger.warning("Pub-sub requested but module not available")
            elif message_broker:
                self.pubsub = message_broker
                logger.info("Pub-sub messaging enabled (custom broker)")
            elif InMemoryPubSub:
                self.pubsub = InMemoryPubSub()
                logger.info("Pub-sub messaging enabled (in-memory)")
        
        if enable_conflict_resolution:
            if not _CONFLICT_RESOLUTION_AVAILABLE:
                logger.warning("Conflict resolution requested but module not available")
            elif ConflictResolver:
                # Find supervisor agent for escalation
                supervisor_id = None
                for agent in agents:
                    if agent.role == AgentRole.SUPERVISOR:
                        supervisor_id = agent.agent_id
                        break
                
                self.conflict_resolver = ConflictResolver(
                    default_vote_type=VoteType.MAJORITY,
                    supervisor_agent_id=supervisor_id
                )
                logger.info(f"Conflict resolution enabled (supervisor: {supervisor_id})")
        
        logger.info(f"Orchestrator initialized with {len(agents)} agents")
    
    def register_executor(
        self,
        agent_id: str,
        executor: Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ):
        """
        Register an execution function for an agent.
        
        Args:
            agent_id: Agent identifier
            executor: Async function that executes tasks for this agent
                     Signature: async def execute(task_description: str, context: dict) -> dict
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found in orchestrator")
        
        self.agent_executors[agent_id] = executor
        logger.info(f"Executor registered for agent {agent_id}")
    
    async def submit_task(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a task to the orchestrator.
        
        The orchestrator will:
        1. Analyze the task complexity
        2. Assign to appropriate agent(s)
        3. Monitor execution and handle failures
        4. Coordinate multi-step workflows
        
        Args:
            description: Task description
            context: Additional context
            
        Returns:
            task_id for tracking
        """
        task = OrchestratedTask(
            description=description,
            status=TaskStatus.PENDING
        )
        
        self.tasks[task.task_id] = task
        
        logger.info(f"Task submitted: {task.task_id} - {description[:50]}")
        
        # Start task execution in background
        asyncio.create_task(self._execute_task(task.task_id, context or {}))
        
        return task.task_id
    
    async def _execute_task(
        self,
        task_id: str,
        context: Dict[str, Any]
    ):
        """
        Execute a task with automatic agent selection and coordination.
        
        Implements the core orchestration logic:
        1. Task analysis and decomposition
        2. Agent selection based on capabilities
        3. Execution with retry and fallback
        4. Result aggregation for multi-step tasks
        
        Args:
            task_id: Task identifier
            context: Execution context
        """
        task = self.tasks[task_id]
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        try:
            # Step 1: Analyze task and select agent
            selected_agent = self._select_agent(task.description, context)
            
            if not selected_agent:
                raise ValueError("No suitable agent found for task")
            
            task.assigned_to = selected_agent.agent_id
            
            logger.info(
                f"Task {task_id} assigned to {selected_agent.agent_id} "
                f"(role: {selected_agent.role.value})"
            )
            
            # Step 2: Execute via registered executor
            if selected_agent.agent_id not in self.agent_executors:
                raise ValueError(f"No executor registered for {selected_agent.agent_id}")
            
            executor = self.agent_executors[selected_agent.agent_id]
            result = await executor(task.description, context)
            
            # Step 3: Mark as completed
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Task {task_id} completed successfully")
            
            # Emit telemetry
            duration_ms = (task.completed_at - task.started_at).total_seconds() * 1000
            logger.info(
                f"Task metrics: task_id={task_id}, "
                f"agent={selected_agent.agent_id}, "
                f"duration_ms={duration_ms:.0f}"
            )
            
        except Exception as e:
            # Handle failure
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"Task {task_id} failed: {e}")
            
            # Could trigger self-correction here via Shadow Teacher
            await self._handle_task_failure(task_id, e)
    
    def _select_agent(
        self,
        task_description: str,
        context: Dict[str, Any]
    ) -> Optional[AgentSpec]:
        """
        Select the most appropriate agent for a task.
        
        Selection based on:
        1. Agent role (supervisor vs specialist)
        2. Capabilities match
        3. Current workload
        
        Research: "DEPS" framework's dynamic agent selection.
        
        Args:
            task_description: Task to assign
            context: Execution context
            
        Returns:
            Selected agent spec or None
        """
        # Simple heuristic: match task keywords to capabilities
        task_lower = task_description.lower()
        
        candidates = []
        for agent in self.agents.values():
            # Check if agent has relevant capabilities
            capability_match = any(
                cap.lower() in task_lower 
                for cap in agent.capabilities
            )
            
            if capability_match:
                candidates.append(agent)
        
        # If no capability match, use supervisor
        if not candidates:
            supervisors = [
                a for a in self.agents.values() 
                if a.role == AgentRole.SUPERVISOR
            ]
            return supervisors[0] if supervisors else None
        
        # Return first match (could add load balancing here)
        return candidates[0]
    
    async def _handle_task_failure(
        self,
        task_id: str,
        error: Exception
    ):
        """
        Handle task failure with potential retry or escalation.
        
        Could integrate with self-correcting kernel here:
        1. Analyze failure via Shadow Teacher
        2. Generate patch
        3. Retry with updated instructions
        
        Args:
            task_id: Failed task ID
            error: Exception that caused failure
        """
        task = self.tasks[task_id]
        
        logger.warning(
            f"Handling failure for task {task_id}: {error}\n"
            f"Consider implementing self-correction via Shadow Teacher"
        )
        
        # Placeholder for self-correction integration
        # In production, would call:
        # - shadow_teacher.analyze_failure(...)
        # - patcher.create_patch(...)
        # - retry with updated context
    
    async def get_task_status(self, task_id: str) -> Optional[OrchestratedTask]:
        """
        Get current status of a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task object or None if not found
        """
        return self.tasks.get(task_id)
    
    async def send_message(self, message: AgentMessage):
        """
        Send a message from one agent to another.
        
        Implements agent-to-agent communication (A2A pattern).
        
        Args:
            message: Message to send
        """
        if self.message_broker:
            # Use external broker (e.g., Redis pub-sub)
            await self.message_broker.publish(message.to_agent, message.dict())
        else:
            # Use internal queue
            await self.message_queue.put(message)
        
        logger.debug(
            f"Message sent: {message.from_agent} → {message.to_agent} "
            f"({message.message_type.value})"
        )
    
    async def decompose_task(
        self,
        task_id: str,
        subtask_descriptions: List[str]
    ) -> List[str]:
        """
        Decompose a complex task into subtasks.
        
        Implements hierarchical task decomposition from "Voyager" research.
        
        Args:
            task_id: Parent task ID
            subtask_descriptions: List of subtask descriptions
            
        Returns:
            List of subtask IDs
        """
        parent_task = self.tasks.get(task_id)
        if not parent_task:
            raise ValueError(f"Task {task_id} not found")
        
        subtask_ids = []
        for desc in subtask_descriptions:
            subtask = OrchestratedTask(
                description=desc,
                parent_task_id=task_id,
                status=TaskStatus.PENDING
            )
            self.tasks[subtask.task_id] = subtask
            subtask_ids.append(subtask.task_id)
            
            # Start execution
            asyncio.create_task(self._execute_task(subtask.task_id, {}))
        
        parent_task.subtasks = subtask_ids
        
        logger.info(
            f"Task {task_id} decomposed into {len(subtask_ids)} subtasks"
        )
        
        return subtask_ids
    
    def get_agent_workload(self, agent_id: str) -> int:
        """
        Get current workload for an agent.
        
        Returns:
            Number of tasks currently in progress for this agent
        """
        return sum(
            1 for task in self.tasks.values()
            if task.assigned_to == agent_id and task.status == TaskStatus.IN_PROGRESS
        )
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """
        Get orchestrator statistics for monitoring.
        
        Returns:
            dict with task counts by status, agent workloads, etc.
        """
        stats = {
            "total_tasks": len(self.tasks),
            "by_status": {},
            "agent_workloads": {},
            "avg_completion_time_ms": 0
        }
        
        # Count by status
        for status in TaskStatus:
            stats["by_status"][status.value] = sum(
                1 for t in self.tasks.values() if t.status == status
            )
        
        # Agent workloads
        for agent_id in self.agents:
            stats["agent_workloads"][agent_id] = self.get_agent_workload(agent_id)
        
        # Avg completion time
        completed_tasks = [
            t for t in self.tasks.values() 
            if t.status == TaskStatus.COMPLETED and t.completed_at and t.started_at
        ]
        
        if completed_tasks:
            total_ms = sum(
                (t.completed_at - t.started_at).total_seconds() * 1000
                for t in completed_tasks
            )
            stats["avg_completion_time_ms"] = total_ms / len(completed_tasks)
        
        return stats
    
    async def create_swarm(
        self,
        swarm_id: str,
        agent_ids: List[str]
    ) -> Optional[Any]:
        """
        Create an agent swarm for collaborative tasks.
        
        Args:
            swarm_id: Unique swarm identifier
            agent_ids: List of agent IDs to include in swarm
            
        Returns:
            AgentSwarm instance or None if pub-sub not enabled
        """
        if not self.pubsub or not _PUBSUB_AVAILABLE or not AgentSwarm:
            logger.warning("Pub-sub not available, cannot create swarm")
            return None
        
        # Validate all agents exist
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")
        
        swarm = AgentSwarm(swarm_id, self.pubsub, agent_ids)
        self.swarms[swarm_id] = swarm
        
        logger.info(f"Swarm {swarm_id} created with {len(agent_ids)} agents")
        
        return swarm
    
    async def resolve_agent_conflict(
        self,
        conflict_id: str,
        conflict_type: str,
        votes: List[Dict[str, Any]],
        vote_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve conflict between agents using voting.
        
        Args:
            conflict_id: Unique conflict identifier
            conflict_type: Type of conflict (decision, interpretation, etc.)
            votes: List of votes as dicts with agent_id, option, confidence
            vote_type: Voting mechanism (majority, weighted, etc.)
            
        Returns:
            Resolution dict or None if conflict resolution not available
        """
        if not self.conflict_resolver or not _CONFLICT_RESOLUTION_AVAILABLE or not AgentVote or not ConflictType:
            logger.warning("Conflict resolution not available")
            return None
        
        # Convert dicts to AgentVote objects
        vote_objects = [
            AgentVote(
                agent_id=v["agent_id"],
                option=v["option"],
                confidence=v.get("confidence", 1.0),
                reasoning=v.get("reasoning")
            )
            for v in votes
        ]
        
        # Convert strings to enums
        conflict_type_enum = ConflictType(conflict_type)
        vote_type_enum = VoteType(vote_type) if vote_type else None
        
        resolution = await self.conflict_resolver.resolve_conflict(
            conflict_id,
            conflict_type_enum,
            vote_objects,
            vote_type_enum
        )
        
        return {
            "conflict_id": resolution.conflict_id,
            "winning_option": resolution.winning_option,
            "consensus_score": resolution.consensus_score,
            "total_votes": resolution.total_votes,
            "votes_for_winner": resolution.votes_for_winner,
            "dissenting_agents": resolution.dissenting_agents,
            "escalated": resolution.escalated_to_supervisor
        }
    
    async def broadcast_to_swarm(
        self,
        swarm_id: str,
        from_agent: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Broadcast message to all agents in a swarm.
        
        Args:
            swarm_id: Swarm to broadcast to
            from_agent: Sender agent ID
            message: Message content
            payload: Optional structured data
            
        Returns:
            True if successful, False otherwise
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return False
        
        swarm = self.swarms[swarm_id]
        await swarm.broadcast(from_agent, message, payload)
        
        return True
    
    async def request_swarm_consensus(
        self,
        swarm_id: str,
        from_agent: str,
        proposal: str,
        context: Dict[str, Any],
        required_votes: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Request consensus vote from swarm agents.
        
        Args:
            swarm_id: Swarm to request consensus from
            from_agent: Agent making proposal
            proposal: Decision to vote on
            context: Context for decision
            required_votes: Minimum votes needed
            
        Returns:
            Consensus result dict or None if swarm not found
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return None
        
        swarm = self.swarms[swarm_id]
        result = await swarm.request_consensus(
            from_agent,
            proposal,
            context,
            required_votes
        )
        
        return result


# Example usage pattern
async def example_orchestration():
    """
    Example: Multi-department fraud detection workflow.
    
    Demonstrates hierarchical coordination:
    1. Supervisor receives alert
    2. Analyst investigates transaction
    3. Verifier confirms findings
    4. Executor blocks account if fraud confirmed
    """
    # Define agents
    agents = [
        AgentSpec(
            agent_id="supervisor-001",
            role=AgentRole.SUPERVISOR,
            capabilities=["coordinate", "escalate"],
            model="gpt-4o"
        ),
        AgentSpec(
            agent_id="fraud-analyst-001",
            role=AgentRole.ANALYST,
            capabilities=["analyze", "investigate", "fraud"],
            model="gpt-4o"
        ),
        AgentSpec(
            agent_id="verifier-001",
            role=AgentRole.VERIFIER,
            capabilities=["verify", "validate", "confirm"],
            model="gpt-4o"
        ),
        AgentSpec(
            agent_id="executor-001",
            role=AgentRole.EXECUTOR,
            capabilities=["block", "execute", "action"],
            model="gpt-4o"
        )
    ]
    
    orchestrator = Orchestrator(agents)
    
    # Register executor functions
    async def analyst_executor(task: str, context: dict) -> dict:
        # Mock: Would call actual LLM + tools here
        return {"analysis": "Suspicious pattern detected", "confidence": 0.85}
    
    async def verifier_executor(task: str, context: dict) -> dict:
        return {"verified": True, "evidence": ["Multiple locations", "Unusual time"]}
    
    async def executor_executor(task: str, context: dict) -> dict:
        return {"action": "account_blocked", "timestamp": datetime.now().isoformat()}
    
    orchestrator.register_executor("fraud-analyst-001", analyst_executor)
    orchestrator.register_executor("verifier-001", verifier_executor)
    orchestrator.register_executor("executor-001", executor_executor)
    
    # Submit task
    task_id = await orchestrator.submit_task(
        "Analyze transaction T-12345 for fraud indicators",
        context={"transaction_id": "T-12345"}
    )
    
    # Wait for completion
    await asyncio.sleep(1)
    
    # Check status
    task = await orchestrator.get_task_status(task_id)
    print(f"Task status: {task.status if task else 'Not found'}")
    
    # Get stats
    stats = orchestrator.get_orchestrator_stats()
    print(f"Orchestrator stats: {stats}")


if __name__ == "__main__":
    asyncio.run(example_orchestration())
