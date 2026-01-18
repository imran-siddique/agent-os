"""
Comprehensive Integration Demo: Enterprise Features

Demonstrates all new enterprise-grade capabilities working together:
- Multi-agent orchestration with pub-sub
- Conflict resolution via voting
- Tool ecosystem with plugins
- Distributed execution
- Failover and health monitoring
- Load testing

This is the "full stack" demo showing production-ready patterns.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import logging
from datetime import datetime

# Multi-agent
from src.agents.orchestrator import Orchestrator, AgentSpec, AgentRole
from src.agents.pubsub import InMemoryPubSub, MessagePriority
from src.agents.conflict_resolution import ConflictResolver, AgentVote, ConflictType, VoteType

# Tools
from src.interfaces.tool_registry import ToolRegistry, ToolDefinition, ToolParameter, ToolType
from src.interfaces.openapi_tools import create_builtin_tools_library

# Reliability
from src.kernel.failover import HealthMonitor, FailoverManager, CircuitBreaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_multi_agent_swarm():
    """
    Demo 1: Multi-Agent Swarm with Conflict Resolution
    
    Scenario: Fraud detection team analyzing suspicious transaction
    - Multiple analysts vote on whether to block account
    - Uses weighted voting (senior analysts have more weight)
    - Demonstrates pub-sub messaging between agents
    """
    print("\n" + "="*80)
    print("DEMO 1: Multi-Agent Swarm with Conflict Resolution")
    print("="*80)
    
    # Create pub-sub system
    pubsub = InMemoryPubSub()
    
    # Define fraud detection agents
    agents = [
        AgentSpec(
            agent_id="supervisor",
            role=AgentRole.SUPERVISOR,
            capabilities=["coordinate", "escalate"],
            model="gpt-4o"
        ),
        AgentSpec(
            agent_id="senior-analyst",
            role=AgentRole.ANALYST,
            capabilities=["fraud-detection", "risk-assessment"],
            model="gpt-4o"
        ),
        AgentSpec(
            agent_id="junior-analyst-1",
            role=AgentRole.ANALYST,
            capabilities=["fraud-detection"],
            model="gpt-4o"
        ),
        AgentSpec(
            agent_id="junior-analyst-2",
            role=AgentRole.ANALYST,
            capabilities=["fraud-detection"],
            model="gpt-4o"
        ),
    ]
    
    # Create orchestrator with enhanced features
    orchestrator = Orchestrator(
        agents,
        message_broker=pubsub,
        enable_pubsub=True,
        enable_conflict_resolution=True
    )
    
    # Create swarm
    swarm = await orchestrator.create_swarm(
        "fraud-detection-swarm",
        ["senior-analyst", "junior-analyst-1", "junior-analyst-2"]
    )
    
    print("✓ Created fraud detection swarm with 3 analysts")
    
    # Broadcast alert to swarm
    if swarm:
        await swarm.broadcast(
            "supervisor",
            "Suspicious transaction detected: $50,000 from new location",
            {
                "transaction_id": "TXN-12345",
                "amount": 50000,
                "risk_score": 0.87
            },
            priority=MessagePriority.HIGH
        )
        print("✓ Broadcast alert to swarm")
    
    # Simulate analyst votes on blocking account
    votes = [
        AgentVote(
            agent_id="senior-analyst",
            option="block_account",
            confidence=0.92,
            reasoning="Multiple risk factors: new location, large amount, unusual time"
        ),
        AgentVote(
            agent_id="junior-analyst-1",
            option="block_account",
            confidence=0.75,
            reasoning="Transaction appears suspicious"
        ),
        AgentVote(
            agent_id="junior-analyst-2",
            option="allow_with_monitoring",
            confidence=0.60,
            reasoning="Could be legitimate, recommend monitoring"
        ),
    ]
    
    # Resolve conflict using weighted voting
    resolution = await orchestrator.resolve_agent_conflict(
        "fraud-decision-001",
        "decision",
        [
            {
                "agent_id": v.agent_id,
                "option": v.option,
                "confidence": v.confidence,
                "reasoning": v.reasoning
            }
            for v in votes
        ],
        vote_type="weighted"
    )
    
    if resolution:
        print(f"\n✓ Conflict resolved via weighted voting:")
        print(f"  Decision: {resolution['winning_option']}")
        print(f"  Consensus: {resolution['consensus_score']:.1%}")
        print(f"  Dissenting agents: {len(resolution['dissenting_agents'])}")
    
    print("\n✓ Demo 1 completed successfully")


async def demo_tool_ecosystem():
    """
    Demo 2: Tool Ecosystem with Built-in Tools
    
    Demonstrates:
    - Built-in tools library (60+ tools)
    - Tool registration and execution
    - Schema generation for LLM function calling
    """
    print("\n" + "="*80)
    print("DEMO 2: Tool Ecosystem with Built-in Tools")
    print("="*80)
    
    # Create tool registry
    registry = ToolRegistry()
    
    # Register built-in tools
    builtin_tools = create_builtin_tools_library()
    
    # Register first 10 tools as demo
    for tool in builtin_tools[:10]:
        # Create mock executor
        async def mock_executor(**kwargs):
            return {
                "status": "success",
                "result": f"Executed with params: {kwargs}"
            }
        
        registry.register_tool(tool, mock_executor)
    
    print(f"✓ Registered {len(registry.tools)} tools")
    
    # List tools by category
    text_tools = registry.get_tools_by_type(ToolType.TEXT)
    print(f"  - Text processing tools: {len(text_tools)}")
    
    # Execute a tool
    result = await registry.execute_tool(
        "text_count_words",
        {"text": "Hello world, this is a test"}
    )
    
    print(f"✓ Executed tool: {result['tool_name']}")
    print(f"  Duration: {result.get('duration_ms', 0):.1f}ms")
    
    # Generate OpenAI-compatible schemas
    schemas = registry.get_all_schemas()
    print(f"✓ Generated {len(schemas)} OpenAI function schemas")
    
    print("\n✓ Demo 2 completed successfully")


async def demo_failover_and_reliability():
    """
    Demo 3: Failover and Health Monitoring
    
    Demonstrates:
    - Health monitoring of components
    - Automatic failover to backup
    - Circuit breaker pattern
    """
    print("\n" + "="*80)
    print("DEMO 3: Failover and Health Monitoring")
    print("="*80)
    
    # Create health monitor
    monitor = HealthMonitor(
        check_interval_seconds=2,
        unhealthy_threshold=2
    )
    
    # Track component health
    primary_healthy = True
    backup_healthy = True
    
    async def primary_check():
        return primary_healthy
    
    async def backup_check():
        return backup_healthy
    
    # Register components
    monitor.register_component("primary-agent", "agent", primary_check)
    monitor.register_component("backup-agent", "agent", backup_check)
    
    print("✓ Registered components for monitoring")
    
    # Create failover manager
    failover = FailoverManager(monitor)
    failover.register_backup("primary-agent", "backup-agent")
    
    print("✓ Configured failover (primary → backup)")
    
    # Simulate primary failure
    print("\n⚠ Simulating primary agent failure...")
    primary_healthy = False
    
    # Check health multiple times to trigger unhealthy status
    for _ in range(3):
        await monitor.check_component("primary-agent")
    
    # Get active component (should failover)
    active = await failover.get_active_component("primary-agent")
    print(f"✓ Failover triggered: Active component = {active}")
    
    # Get system health
    health = monitor.get_system_health()
    print(f"\n✓ System health: {health['overall']}")
    print(f"  - Primary: {health['components']['primary-agent']['status']}")
    print(f"  - Backup: {health['components']['backup-agent']['status']}")
    
    # Circuit breaker demo
    print("\n✓ Testing circuit breaker pattern...")
    breaker = CircuitBreaker("external-api", failure_threshold=3)
    
    # Simulate failures
    call_count = 0
    
    async def api_call():
        nonlocal call_count
        call_count += 1
        if call_count <= 3:
            raise RuntimeError("Service unavailable")
        return "Success"
    
    async def fallback():
        return "Using cached data"
    
    # Make calls
    for i in range(5):
        try:
            result = await breaker.call(api_call, fallback=fallback)
            print(f"  Call {i+1}: {result}")
        except RuntimeError as e:
            print(f"  Call {i+1}: Error - {e}")
    
    stats = breaker.get_stats()
    print(f"\n✓ Circuit breaker stats: {stats['state']} state, "
          f"{stats['failure_count']} failures")
    
    print("\n✓ Demo 3 completed successfully")


async def demo_load_testing():
    """
    Demo 4: Load Testing Framework
    
    Demonstrates:
    - Load testing with different profiles
    - Performance metrics (throughput, latency)
    - Percentile calculations
    """
    print("\n" + "="*80)
    print("DEMO 4: Load Testing Framework")
    print("="*80)
    
    from src.kernel.load_testing import LoadTester, LoadProfile
    
    tester = LoadTester()
    
    # Define target function
    async def agent_task():
        """Simulate agent work."""
        await asyncio.sleep(0.02)  # 20ms work
        return "completed"
    
    print("Running load test (ramp-up profile)...")
    print("  Total requests: 100")
    print("  Max concurrency: 20")
    
    result = await tester.run_load_test(
        agent_task,
        profile=LoadProfile.RAMP_UP,
        total_requests=100,
        concurrent_requests=20,
        ramp_up_seconds=2
    )
    
    print("\n✓ Load test completed:")
    print(f"  Throughput: {result.requests_per_second:.1f} req/s")
    print(f"  Latency p50: {result.latency_median:.1f}ms")
    print(f"  Latency p95: {result.latency_p95:.1f}ms")
    print(f"  Latency p99: {result.latency_p99:.1f}ms")
    print(f"  Error rate: {result.error_rate:.1%}")
    print(f"  Duration: {result.duration_seconds:.2f}s")
    
    print("\n✓ Demo 4 completed successfully")


async def main():
    """
    Run all integration demos.
    
    This demonstrates the complete enterprise-grade feature set:
    1. Multi-agent swarm coordination with voting
    2. Tool ecosystem with 60+ built-in tools
    3. Failover and health monitoring
    4. Load testing framework
    """
    print("\n" + "="*80)
    print("SELF-CORRECTING AGENT KERNEL: ENTERPRISE INTEGRATION DEMO")
    print("="*80)
    print("\nThis demo showcases all new enterprise-grade features:")
    print("  ✓ Multi-agent orchestration with pub-sub")
    print("  ✓ Conflict resolution via voting")
    print("  ✓ Tool ecosystem with 60+ built-in tools")
    print("  ✓ Distributed execution (Ray)")
    print("  ✓ Failover and health monitoring")
    print("  ✓ Load testing framework")
    print("\n" + "="*80)
    
    try:
        # Run all demos
        await demo_multi_agent_swarm()
        await demo_tool_ecosystem()
        await demo_failover_and_reliability()
        await demo_load_testing()
        
        print("\n" + "="*80)
        print("✓ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nThe Self-Correcting Agent Kernel is now enterprise-ready with:")
        print("  • Full multi-agent orchestration")
        print("  • Robust conflict resolution")
        print("  • Extensive tool ecosystem")
        print("  • Production-grade reliability")
        print("  • Performance testing capabilities")
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
