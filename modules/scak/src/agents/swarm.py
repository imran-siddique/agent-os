"""
Evolvable Orchestrator - Dynamic agent hot-swapping based on performance.

This extends the base Orchestrator with evolutionary capabilities:
- Real-time performance monitoring
- Hot-swapping of underperforming agents
- Agent pool management
- Context handover between agents

Architecture Pattern:
- Pool: Multiple agent profiles with different capabilities
- Monitor: Track performance metrics (reward, success rate, latency)
- Swap: Replace underperforming agents mid-flight
- Handover: Transfer context seamlessly to new agent

This implements "Evolvable Teams" from DEPS research - agents are not
fixed roles, but dynamic assignments based on performance.

Integration with v2:
- RewardShaper provides performance scores
- EmergenceMonitor flags problematic agents
- MemoryController stores swap history
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime
from uuid import uuid4

from src.agents.orchestrator import (
    Orchestrator, AgentSpec, AgentRole, OrchestratedTask, TaskStatus
)
from src.kernel.schemas import (
    AgentPerformance, AgentSwapDecision, Rubric
)

logger = logging.getLogger(__name__)


class AgentPool:
    """
    Pool of agent profiles available for hot-swapping.
    
    This maintains a registry of agents with different:
    - Models (gpt-4o vs o1-preview)
    - System prompts (analyst vs senior-analyst)
    - Tool access (basic vs advanced)
    
    The pool allows the orchestrator to upgrade/downgrade agents
    based on performance.
    """
    
    def __init__(self):
        """Initialize empty agent pool."""
        self.agents: Dict[str, AgentSpec] = {}
        self.performance: Dict[str, AgentPerformance] = {}
        
        # Agent tiers (for upgrade/downgrade)
        self.tiers: Dict[str, int] = {}  # agent_id → tier (1=basic, 2=standard, 3=senior)
        
        logger.info("AgentPool initialized")
    
    def register_agent(
        self,
        agent: AgentSpec,
        tier: int = 2,
        initial_performance: Optional[AgentPerformance] = None
    ):
        """
        Register an agent in the pool.
        
        Args:
            agent: Agent specification
            tier: Agent tier (1=basic, 2=standard, 3=senior)
            initial_performance: Initial performance metrics
        """
        self.agents[agent.agent_id] = agent
        self.tiers[agent.agent_id] = tier
        
        if initial_performance:
            self.performance[agent.agent_id] = initial_performance
        else:
            # Initialize with neutral performance
            self.performance[agent.agent_id] = AgentPerformance(
                agent_id=agent.agent_id,
                role=agent.role.value,
                reward_score=0.5,
                success_rate=0.5
            )
        
        logger.info(
            f"Registered agent {agent.agent_id} (tier {tier}, role {agent.role.value})"
        )
    
    def update_performance(
        self,
        agent_id: str,
        reward_score: Optional[float] = None,
        task_success: Optional[bool] = None,
        latency_ms: Optional[float] = None
    ):
        """
        Update agent performance metrics.
        
        Args:
            agent_id: Agent to update
            reward_score: New reward score (if available)
            task_success: Whether task succeeded
            latency_ms: Task latency
        """
        if agent_id not in self.performance:
            logger.warning(f"Agent {agent_id} not in pool")
            return
        
        perf = self.performance[agent_id]
        
        if reward_score is not None:
            # Update with exponential moving average
            alpha = 0.3  # Weighting for new value
            perf.reward_score = alpha * reward_score + (1 - alpha) * perf.reward_score
        
        if task_success is not None:
            if task_success:
                perf.tasks_completed += 1
            else:
                perf.tasks_failed += 1
            
            total_tasks = perf.tasks_completed + perf.tasks_failed
            perf.success_rate = perf.tasks_completed / total_tasks if total_tasks > 0 else 0.5
        
        if latency_ms is not None:
            # Update with exponential moving average
            alpha = 0.3
            if perf.avg_latency_ms == 0:
                perf.avg_latency_ms = latency_ms
            else:
                perf.avg_latency_ms = alpha * latency_ms + (1 - alpha) * perf.avg_latency_ms
        
        perf.last_updated = datetime.now()
        
        logger.debug(
            f"Updated {agent_id}: reward={perf.reward_score:.2f}, "
            f"success_rate={perf.success_rate:.2f}"
        )
    
    def get_performance(self, agent_id: str) -> Optional[AgentPerformance]:
        """Get agent performance."""
        return self.performance.get(agent_id)
    
    def find_replacement(
        self,
        current_agent_id: str,
        role: AgentRole,
        min_tier_increase: int = 1
    ) -> Optional[AgentSpec]:
        """
        Find a replacement agent (upgrade).
        
        This implements the "hot-swap" logic - find a better agent
        with the same role but higher tier.
        
        Args:
            current_agent_id: Agent to replace
            role: Required role
            min_tier_increase: Minimum tier increase (1=next tier up)
            
        Returns:
            AgentSpec: Replacement agent or None
        """
        current_tier = self.tiers.get(current_agent_id, 2)
        target_tier = current_tier + min_tier_increase
        
        # Find agents with matching role and higher tier
        candidates = [
            agent for agent_id, agent in self.agents.items()
            if agent.role == role
            and self.tiers.get(agent_id, 2) >= target_tier
            and agent_id != current_agent_id
        ]
        
        if not candidates:
            logger.warning(
                f"No replacement found for {current_agent_id} (role {role.value}, tier {current_tier})"
            )
            return None
        
        # Return highest tier candidate
        best_candidate = max(candidates, key=lambda a: self.tiers.get(a.agent_id, 2))
        
        logger.info(
            f"Found replacement: {best_candidate.agent_id} "
            f"(tier {self.tiers.get(best_candidate.agent_id, 2)}) "
            f"for {current_agent_id} (tier {current_tier})"
        )
        
        return best_candidate
    
    def get_agents_by_role(self, role: AgentRole) -> List[AgentSpec]:
        """Get all agents with specific role."""
        return [
            agent for agent in self.agents.values()
            if agent.role == role
        ]


class EvolvableOrchestrator(Orchestrator):
    """
    Orchestrator with dynamic agent hot-swapping.
    
    Extends base Orchestrator with evolutionary capabilities:
    1. Performance monitoring (via RewardShaper)
    2. Hot-swapping underperforming agents
    3. Context handover between agents
    4. Evolution history tracking
    
    Example Use Case:
    - Analyst agent has success_rate < 0.70
    - Orchestrator swaps to Senior Analyst (o1-preview)
    - Context is transferred seamlessly
    - Task continues without user interruption
    
    This implements "Self-Improving Teams" - the swarm evolves its
    composition based on performance feedback.
    """
    
    def __init__(
        self,
        agents: List[AgentSpec],
        agent_pool: Optional[AgentPool] = None,
        performance_threshold: float = 0.70,
        swap_enabled: bool = True,
        **kwargs
    ):
        """
        Initialize evolvable orchestrator.
        
        Args:
            agents: Initial agent specifications
            agent_pool: Agent pool for hot-swapping (auto-created if None)
            performance_threshold: Min performance before swap (0.0-1.0)
            swap_enabled: Whether to enable hot-swapping
            **kwargs: Additional args for base Orchestrator
        """
        super().__init__(agents, **kwargs)
        
        self.agent_pool = agent_pool or AgentPool()
        self.performance_threshold = performance_threshold
        self.swap_enabled = swap_enabled
        
        # Register initial agents in pool
        for agent in agents:
            if agent.agent_id not in self.agent_pool.agents:
                # Infer tier from agent_id or model
                tier = self._infer_tier(agent)
                self.agent_pool.register_agent(agent, tier=tier)
        
        # Evolution history
        self.swap_history: List[AgentSwapDecision] = []
        
        logger.info(
            f"EvolvableOrchestrator initialized (swap_enabled={swap_enabled}, "
            f"threshold={performance_threshold})"
        )
    
    def _infer_tier(self, agent: AgentSpec) -> int:
        """
        Infer agent tier from agent_id or model.
        
        This is a heuristic:
        - basic/junior → tier 1
        - standard/analyst → tier 2
        - senior/advanced/o1 → tier 3
        
        Args:
            agent: Agent specification
            
        Returns:
            int: Tier (1-3)
        """
        agent_id_lower = agent.agent_id.lower()
        model_lower = agent.model.lower()
        
        if "senior" in agent_id_lower or "advanced" in agent_id_lower or "o1" in model_lower:
            return 3
        elif "basic" in agent_id_lower or "junior" in agent_id_lower:
            return 1
        else:
            return 2
    
    async def submit_task_with_monitoring(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        rubric: Optional[Rubric] = None
    ) -> str:
        """
        Submit task with performance monitoring.
        
        This extends submit_task() with:
        - Performance tracking
        - Automatic swap on low performance
        - Reward computation
        
        Args:
            description: Task description
            context: Additional context
            rubric: Reward rubric for scoring
            
        Returns:
            str: task_id for tracking
        """
        task_id = await self.submit_task(description, context)
        
        # Start monitoring in background
        asyncio.create_task(
            self._monitor_and_swap(task_id, rubric)
        )
        
        return task_id
    
    async def _monitor_and_swap(
        self,
        task_id: str,
        rubric: Optional[Rubric]
    ):
        """
        Monitor task execution and swap agent if needed.
        
        This is the core "evolutionary" logic:
        1. Wait for task to complete
        2. Check agent performance
        3. If below threshold, swap for next task
        
        Args:
            task_id: Task to monitor
            rubric: Reward rubric for scoring
        """
        # Wait for task completion
        await asyncio.sleep(0.5)  # Initial wait
        
        max_wait = 60  # Max 60 seconds
        wait_time = 0
        
        while wait_time < max_wait:
            task = await self.get_task_status(task_id)
            
            if not task:
                break
            
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                # Task done - update performance
                await self._update_agent_performance(task, rubric)
                
                # Check if swap needed
                if task.assigned_to and self.swap_enabled:
                    await self._check_and_swap(task.assigned_to)
                
                break
            
            await asyncio.sleep(1)
            wait_time += 1
    
    async def _update_agent_performance(
        self,
        task: OrchestratedTask,
        rubric: Optional[Rubric]
    ):
        """
        Update agent performance after task completion.
        
        Args:
            task: Completed task
            rubric: Reward rubric for scoring
        """
        if not task.assigned_to:
            return
        
        task_success = task.status == TaskStatus.COMPLETED
        
        # Compute latency
        latency_ms = None
        if task.started_at and task.completed_at:
            latency_ms = (task.completed_at - task.started_at).total_seconds() * 1000
        
        # Compute reward score (simplified)
        # In production, would use actual RewardShaper
        reward_score = None
        if task_success and rubric:
            # Mock: Use success as proxy for reward
            reward_score = 0.8
        elif task_success:
            reward_score = 0.7
        else:
            reward_score = 0.3
        
        self.agent_pool.update_performance(
            agent_id=task.assigned_to,
            reward_score=reward_score,
            task_success=task_success,
            latency_ms=latency_ms
        )
        
        logger.info(
            f"Updated performance for {task.assigned_to}: "
            f"reward={reward_score:.2f}, success={task_success}"
        )
    
    async def _check_and_swap(self, agent_id: str):
        """
        Check if agent should be swapped and perform swap.
        
        Args:
            agent_id: Agent to check
        """
        perf = self.agent_pool.get_performance(agent_id)
        
        if not perf:
            return
        
        # Need minimum task count before swapping
        total_tasks = perf.tasks_completed + perf.tasks_failed
        if total_tasks < 3:
            # Not enough data yet
            return
        
        # Check if performance below threshold
        if perf.reward_score >= self.performance_threshold:
            # Performance acceptable
            return
        
        logger.warning(
            f"Agent {agent_id} performance below threshold: "
            f"{perf.reward_score:.2f} < {self.performance_threshold:.2f}"
        )
        
        # Find replacement
        agent_spec = self.agents.get(agent_id)
        if not agent_spec:
            return
        
        replacement = self.agent_pool.find_replacement(
            current_agent_id=agent_id,
            role=agent_spec.role,
            min_tier_increase=1
        )
        
        if not replacement:
            logger.warning(f"No replacement found for {agent_id}")
            return
        
        # Perform swap
        await self._perform_swap(agent_id, replacement, perf)
    
    async def _perform_swap(
        self,
        old_agent_id: str,
        new_agent: AgentSpec,
        performance_before: AgentPerformance
    ):
        """
        Perform hot-swap of agents.
        
        This is the critical "context handover" - we need to:
        1. Pause execution (if possible)
        2. Transfer context/memory to new agent
        3. Update orchestrator state
        4. Resume execution
        
        Args:
            old_agent_id: Agent to replace
            new_agent: Replacement agent
            performance_before: Performance metrics before swap
        """
        logger.info(
            f"🔄 Performing hot-swap: {old_agent_id} → {new_agent.agent_id}"
        )
        
        # Step 1: Update orchestrator state
        self.agents[new_agent.agent_id] = new_agent
        
        # Step 2: Transfer executor (if exists)
        if old_agent_id in self.agent_executors:
            executor = self.agent_executors[old_agent_id]
            self.agent_executors[new_agent.agent_id] = executor
            logger.info(f"Transferred executor from {old_agent_id} to {new_agent.agent_id}")
        
        # Step 3: Register in pool (if not already)
        if new_agent.agent_id not in self.agent_pool.agents:
            tier = self._infer_tier(new_agent)
            self.agent_pool.register_agent(new_agent, tier=tier)
        
        # Step 4: Record swap decision
        decision = AgentSwapDecision(
            old_agent_id=old_agent_id,
            new_agent_id=new_agent.agent_id,
            reason=(
                f"Performance below threshold ({performance_before.reward_score:.2f} < "
                f"{self.performance_threshold:.2f})"
            ),
            performance_before=performance_before,
            expected_improvement=0.15  # Heuristic
        )
        
        self.swap_history.append(decision)
        
        logger.info(
            f"✅ Swap complete: {old_agent_id} → {new_agent.agent_id} "
            f"(expected +{decision.expected_improvement:.2f} reward)"
        )
        
        # Note: In production, would also:
        # - Transfer conversation history
        # - Update system prompt with context
        # - Notify monitoring systems
        # - Possibly retry failed tasks
    
    def get_swap_history(self, limit: int = 100) -> List[AgentSwapDecision]:
        """Get agent swap history."""
        return self.swap_history[-limit:]
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """
        Get evolution statistics.
        
        Returns:
            dict: Statistics about swarms and swaps
        """
        base_stats = self.get_orchestrator_stats()
        
        # Add evolution-specific stats
        base_stats.update({
            "swap_enabled": self.swap_enabled,
            "performance_threshold": self.performance_threshold,
            "total_swaps": len(self.swap_history),
            "agents_in_pool": len(self.agent_pool.agents),
            "agent_performances": {
                agent_id: {
                    "reward_score": perf.reward_score,
                    "success_rate": perf.success_rate,
                    "tasks_completed": perf.tasks_completed
                }
                for agent_id, perf in self.agent_pool.performance.items()
            }
        })
        
        return base_stats
    
    async def force_swap(
        self,
        old_agent_id: str,
        new_agent_id: str,
        reason: str = "Manual swap"
    ) -> bool:
        """
        Force a swap between two agents.
        
        This is for manual intervention or testing.
        
        Args:
            old_agent_id: Agent to replace
            new_agent_id: Replacement agent
            reason: Reason for swap
            
        Returns:
            bool: True if swap succeeded
        """
        if new_agent_id not in self.agent_pool.agents:
            logger.error(f"New agent {new_agent_id} not in pool")
            return False
        
        new_agent = self.agent_pool.agents[new_agent_id]
        perf = self.agent_pool.get_performance(old_agent_id)
        
        if not perf:
            # Create dummy performance
            perf = AgentPerformance(
                agent_id=old_agent_id,
                role="unknown",
                reward_score=0.5,
                success_rate=0.5
            )
        
        await self._perform_swap(old_agent_id, new_agent, perf)
        
        # Update reason in history
        if self.swap_history:
            self.swap_history[-1].reason = reason
        
        return True


# Example usage
async def example_evolutionary_swarm():
    """
    Example: Evolutionary fraud detection swarm.
    
    Demonstrates hot-swapping:
    - Basic analyst starts with low performance
    - System automatically upgrades to senior analyst
    - Performance improves without user intervention
    """
    # Define agent pool with tiers
    agents = [
        AgentSpec(
            agent_id="analyst-basic",
            role=AgentRole.ANALYST,
            capabilities=["analyze", "investigate"],
            model="gpt-4o-mini"
        ),
        AgentSpec(
            agent_id="analyst-senior",
            role=AgentRole.ANALYST,
            capabilities=["analyze", "investigate", "advanced"],
            model="o1-preview"
        )
    ]
    
    # Create pool
    pool = AgentPool()
    pool.register_agent(agents[0], tier=1)
    pool.register_agent(agents[1], tier=3)
    
    # Create orchestrator
    orchestrator = EvolvableOrchestrator(
        agents=[agents[0]],  # Start with basic
        agent_pool=pool,
        performance_threshold=0.70,
        swap_enabled=True
    )
    
    # Register executors
    async def basic_executor(task: str, context: dict) -> dict:
        # Simulate low performance
        return {"analysis": "Basic analysis", "confidence": 0.60}
    
    async def senior_executor(task: str, context: dict) -> dict:
        # Simulate high performance
        return {"analysis": "Advanced analysis", "confidence": 0.95}
    
    orchestrator.register_executor("analyst-basic", basic_executor)
    orchestrator.register_executor("analyst-senior", senior_executor)
    
    # Submit tasks
    for i in range(5):
        await orchestrator.submit_task_with_monitoring(
            f"Analyze transaction T-{i}",
            context={"transaction_id": f"T-{i}"}
        )
    
    # Wait for completion
    await asyncio.sleep(3)
    
    # Check stats
    stats = orchestrator.get_evolution_stats()
    print(f"Evolution stats: {stats}")
    print(f"Swaps performed: {len(orchestrator.get_swap_history())}")


if __name__ == "__main__":
    asyncio.run(example_evolutionary_swarm())
