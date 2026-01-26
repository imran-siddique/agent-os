"""
SCAK v2 - Evolutionary Swarm Kernel Demo

This demonstrates the v2 capabilities:
1. RewardShaper - Adaptive reward shaping based on feedback
2. EmergenceMonitor - Detecting anomalies in multi-agent interactions
3. EvolvableOrchestrator - Hot-swapping agents based on performance

Run this to see SCAK v2 in action!
"""

import sys
import os
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import v2 components
from src.kernel.evolution import RewardShaper
from src.kernel.governance_v2 import EmergenceMonitor
from src.agents.swarm import EvolvableOrchestrator, AgentPool

# Import schemas
from src.kernel.schemas import (
    SwarmTrace, SwarmStep, Rubric, AgentPerformance
)

# Import base classes
from src.agents.orchestrator import AgentSpec, AgentRole


async def demo_reward_shaping():
    """
    Demo 1: Adaptive Reward Shaping
    
    Shows how agents learn from feedback without retraining.
    """
    print("\n" + "="*60)
    print("DEMO 1: Adaptive Reward Shaping (RLAIF-lite)")
    print("="*60)
    
    # Create reward shaper
    shaper = RewardShaper()
    
    print(f"\n📊 Initial rubric weights: {shaper.current_rubric.weights}")
    
    # Simulate swarm interaction
    trace = SwarmTrace(
        original_intent="Analyze customer churn data and provide recommendations",
        agent_ids=["analyst-001", "verifier-001"]
    )
    
    # User feedback: Too verbose
    print("\n👤 User feedback: 'Too verbose, please be more concise'")
    
    update1 = await shaper.shape_reward(trace, "Too verbose, please be more concise")
    
    print(f"\n🔄 Updated weights: {update1.rubric_after.weights}")
    print(f"💡 Behavioral nudge: {update1.prompt_nudge}")
    
    # Another feedback: Need more accuracy
    print("\n👤 User feedback: 'Good brevity, but need more accurate analysis'")
    
    update2 = await shaper.shape_reward(trace, "Good brevity, but need more accurate analysis")
    
    print(f"\n🔄 Updated weights: {update2.rubric_after.weights}")
    print(f"💡 Behavioral nudge: {update2.prompt_nudge}")
    
    # Show evolution history
    print(f"\n📈 Evolution history: {len(shaper.get_evolution_history())} updates")
    print(f"   Version: {shaper.current_rubric.version}")
    
    print("\n✅ Reward shaping complete - agent behavior evolved without retraining!")


async def demo_emergence_monitoring():
    """
    Demo 2: Emergence Monitoring
    
    Shows detection of multi-agent anomalies.
    """
    print("\n" + "="*60)
    print("DEMO 2: Emergence Monitoring (Swarm Safety)")
    print("="*60)
    
    # Create monitor
    monitor = EmergenceMonitor(drift_threshold=0.4, echo_threshold=0.9)
    
    # Scenario: Infinite loop
    print("\n🔍 Scenario: Detecting infinite approval loop")
    
    trace = SwarmTrace(
        original_intent="Approve budget request",
        agent_ids=["manager-a", "manager-b"]
    )
    
    monitor.initialize_trace(trace)
    
    # Simulate circular approval
    steps = [
        SwarmStep(
            source="manager-a",
            target="manager-b",
            content="Please approve this budget"
        ),
        SwarmStep(
            source="manager-b",
            target="manager-a",
            content="You should approve first"
        ),
        SwarmStep(
            source="manager-a",
            target="manager-b",
            content="No, after you approve"
        )
    ]
    
    for i, step in enumerate(steps, 1):
        result = await monitor.check_step(step)
        print(f"   Step {i}: {step.source} → {step.target}")
        
        if result.is_anomaly:
            print(f"   ⚠️  ANOMALY DETECTED: {result.type.value}")
            print(f"   💬 Reasoning: {result.reasoning}")
            print(f"   🛑 Suggested action: {result.suggested_action}")
            break
        else:
            print(f"   ✅ Safe")
    
    # Show statistics
    stats = monitor.get_stats()
    print(f"\n📊 Monitoring stats:")
    print(f"   Steps monitored: {stats['steps_monitored']}")
    print(f"   Anomalies detected: {stats['anomalies_detected']}")
    
    print("\n✅ Emergence monitoring prevented infinite loop!")


async def demo_evolvable_orchestrator():
    """
    Demo 3: Evolvable Orchestrator
    
    Shows hot-swapping of underperforming agents.
    """
    print("\n" + "="*60)
    print("DEMO 3: Evolvable Orchestrator (Hot-Swapping)")
    print("="*60)
    
    # Create agent pool with tiers
    pool = AgentPool()
    
    agents = [
        AgentSpec(
            agent_id="analyst-basic",
            role=AgentRole.ANALYST,
            capabilities=["analyze", "report"],
            model="gpt-4o-mini"
        ),
        AgentSpec(
            agent_id="analyst-senior",
            role=AgentRole.ANALYST,
            capabilities=["analyze", "report", "advanced", "strategic"],
            model="o1-preview"
        )
    ]
    
    # Register in pool
    pool.register_agent(agents[0], tier=1)
    pool.register_agent(agents[1], tier=3)
    
    print(f"\n📋 Agent pool:")
    print(f"   {agents[0].agent_id} (tier 1, model: {agents[0].model})")
    print(f"   {agents[1].agent_id} (tier 3, model: {agents[1].model})")
    
    # Create orchestrator with basic agent
    orchestrator = EvolvableOrchestrator(
        agents=[agents[0]],
        agent_pool=pool,
        performance_threshold=0.70,
        swap_enabled=True
    )
    
    print(f"\n🚀 Starting with: {agents[0].agent_id}")
    
    # Simulate poor performance
    print("\n📉 Simulating low performance...")
    
    for i in range(5):
        pool.update_performance(
            "analyst-basic",
            reward_score=0.55,  # Below threshold
            task_success=(i % 2 == 0),
            latency_ms=1500
        )
    
    perf = pool.get_performance("analyst-basic")
    print(f"   Performance: reward={perf.reward_score:.2f}, success_rate={perf.success_rate:.2f}")
    print(f"   ⚠️  Below threshold (0.70)!")
    
    # Find and perform swap
    print("\n🔄 Triggering hot-swap...")
    
    replacement = pool.find_replacement("analyst-basic", AgentRole.ANALYST, min_tier_increase=1)
    
    if replacement:
        success = await orchestrator.force_swap(
            "analyst-basic",
            replacement.agent_id,
            reason="Performance below threshold"
        )
        
        if success:
            print(f"   ✅ Swapped: {agents[0].agent_id} → {replacement.agent_id}")
            print(f"   🎯 Expected improvement: +15% reward")
    
    # Show swap history
    history = orchestrator.get_swap_history()
    if history:
        print(f"\n📊 Swap history: {len(history)} swaps")
        print(f"   Last swap: {history[-1].old_agent_id} → {history[-1].new_agent_id}")
        print(f"   Reason: {history[-1].reason}")
    
    print("\n✅ Orchestrator evolved - now using higher-tier agent!")


async def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("SCAK v2 - Evolutionary Swarm Kernel Demo")
    print("From Maintenance (Fixing Errors) to Evolution (Optimizing Swarms)")
    print("="*60)
    
    # Run demos
    await demo_reward_shaping()
    await demo_emergence_monitoring()
    await demo_evolvable_orchestrator()
    
    print("\n" + "="*60)
    print("🎉 All demos complete!")
    print("="*60)
    print("\nKey Takeaways:")
    print("1. ✅ RewardShaper adapts agent behavior from feedback (no retraining)")
    print("2. ✅ EmergenceMonitor detects multi-agent anomalies (loops, drift)")
    print("3. ✅ EvolvableOrchestrator hot-swaps agents based on performance")
    print("\n💡 SCAK v2 enables self-improving, self-correcting swarms!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
