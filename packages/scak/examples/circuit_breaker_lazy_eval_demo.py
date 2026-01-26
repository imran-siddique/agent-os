"""
Example demonstrating Circuit Breaker and Lazy Evaluation features.

This example shows how the kernel prevents looping and defers expensive computations.
"""

import asyncio
from src.kernel.core import SelfCorrectingKernel


async def main():
    """Demonstrate circuit breaker and lazy evaluation."""
    
    print("=" * 80)
    print("Circuit Breaker & Lazy Evaluation Demo")
    print("=" * 80)
    print()
    
    # Initialize kernel with both features enabled
    kernel = SelfCorrectingKernel(
        config={
            "enable_circuit_breaker": True,
            "enable_lazy_eval": True,
            "loop_threshold": 3,  # Trigger after 3 repetitions
            "max_deferred_tasks": 100,
        }
    )
    
    print("✓ Kernel initialized with Circuit Breaker and Lazy Evaluation")
    print()
    
    # =========================================================================
    # Demo 1: Circuit Breaker - Detect and Break Loops
    # =========================================================================
    print("-" * 80)
    print("DEMO 1: Circuit Breaker - Preventing Agent Loops")
    print("-" * 80)
    print()
    
    agent_id = "search-agent"
    
    print("Scenario: Agent keeps searching with same query and getting no results")
    print()
    
    # Simulate agent repeating the same action 3 times
    for i in range(3):
        print(f"  Attempt {i+1}: Searching for 'error logs'...")
        
        try:
            result = await kernel.handle_outcome(
                agent_id=agent_id,
                user_prompt="Find error logs from yesterday",
                agent_response="I'm sorry, I couldn't find any error logs.",
                context={
                    "action": "search_logs",
                    "action_params": {"query": "error", "date": "yesterday"},
                    "execution_time_ms": 500
                }
            )
            
            if not result.success:
                print(f"  ✗ Loop detected! Circuit breaker triggered.")
                print(f"    Message: {result.message}")
                break
            else:
                print(f"  ✓ Outcome recorded (attempt {i+1}/3)")
        except Exception as e:
            print(f"  ✗ Exception raised: {type(e).__name__}")
            print(f"    {str(e)[:100]}")
            break
    
    print()
    
    # Get circuit breaker stats
    stats = kernel.get_statistics()
    if "circuit_breaker" in stats:
        cb_stats = stats["circuit_breaker"]["agents"].get(agent_id, {})
        print(f"Circuit Breaker Stats for {agent_id}:")
        print(f"  - Total loops detected: {cb_stats.get('total_loops_detected', 0)}")
        print(f"  - History size: {cb_stats.get('history_size', 0)}")
        print(f"  - Consecutive repetitions: {cb_stats.get('consecutive_repetitions', 0)}")
    
    print()
    
    # =========================================================================
    # Demo 2: Lazy Evaluation - Defer Expensive Computations
    # =========================================================================
    print("-" * 80)
    print("DEMO 2: Lazy Evaluation - Deferring Expensive Operations")
    print("-" * 80)
    print()
    
    agent_id_2 = "analysis-agent"
    
    print("Scenario: Agent wants to analyze historical data (expensive operation)")
    print()
    
    # Simulate expensive operation that should be deferred
    print("  Requesting: Analyze logs from 2023 archive...")
    
    result = await kernel.handle_outcome(
        agent_id=agent_id_2,
        user_prompt="Can you analyze the logs from 2023 for patterns?",
        agent_response="I've identified some potential patterns in the 2023 logs.",
        context={
            "action": "analyze_historical_data",
            "action_params": {"year": 2023, "partition": "archive"},
            "execution_time_ms": 100,
            "estimated_correction_cost_ms": 5000,  # Expensive correction
            "priority": 3  # Low priority
        }
    )
    
    if "deferred" in result.message.lower() or "TODO" in result.message:
        print(f"  ✓ Computation deferred!")
        print(f"    Message: {result.message}")
    else:
        print(f"  • Processed immediately")
        print(f"    Message: {result.message}")
    
    print()
    
    # Simulate speculative operation
    print("  Requesting: User might need detailed breakdown (speculative)...")
    
    result = await kernel.handle_outcome(
        agent_id=agent_id_2,
        user_prompt="The user might want a detailed breakdown, so let's prepare it.",
        agent_response="I've prepared a detailed breakdown just in case.",
        context={
            "action": "speculative_analysis",
            "action_params": {"detail_level": "high"},
            "execution_time_ms": 100
        }
    )
    
    if "deferred" in result.message.lower() or "TODO" in result.message:
        print(f"  ✓ Speculation deferred!")
        print(f"    Message: {result.message[:100]}...")
    else:
        print(f"  • Processed immediately")
    
    print()
    
    # Get lazy evaluation stats
    stats = kernel.get_statistics()
    if "lazy_evaluation" in stats:
        le_stats = stats["lazy_evaluation"]["global"]
        print(f"Lazy Evaluation Global Stats:")
        print(f"  - Total deferrals: {le_stats.get('total_deferrals', 0)}")
        print(f"  - Total resolutions: {le_stats.get('total_resolutions', 0)}")
        print(f"  - Total savings: {le_stats.get('total_savings_seconds', 0):.2f} seconds")
        print(f"  - Resolution rate: {le_stats.get('global_resolution_rate', 0):.2%}")
    
    print()
    
    # =========================================================================
    # Demo 3: Both Features Working Together
    # =========================================================================
    print("-" * 80)
    print("DEMO 3: Both Features Working Together")
    print("-" * 80)
    print()
    
    agent_id_3 = "combined-agent"
    
    print("Scenario: Agent repeating expensive archive queries")
    print()
    
    # This should trigger both lazy eval and circuit breaker
    for i in range(3):
        print(f"  Attempt {i+1}: Querying expensive archive...")
        
        try:
            result = await kernel.handle_outcome(
                agent_id=agent_id_3,
                user_prompt="Check if there are any archived reports from 2022",
                agent_response="I couldn't find any archived reports.",
                context={
                    "action": "query_archive",
                    "action_params": {"year": 2022},
                    "execution_time_ms": 100,
                    "estimated_correction_cost_ms": 8000  # Very expensive
                }
            )
            
            if not result.success:
                print(f"  ✗ Loop detected by circuit breaker")
                break
            elif "deferred" in result.message.lower():
                print(f"  ✓ Operation deferred by lazy evaluator")
            else:
                print(f"  • Processed normally")
        except Exception as e:
            print(f"  ✗ Loop detected by circuit breaker (exception raised)")
            break
    
    print()
    
    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 80)
    print("Summary: Scale by Subtraction")
    print("=" * 80)
    print()
    
    final_stats = kernel.get_statistics()
    
    print("Overall Kernel Statistics:")
    print(f"  - Outcomes processed: {final_stats['outcomes_processed']}")
    print(f"  - Corrections applied: {final_stats['corrections_applied']}")
    print(f"  - Laziness detected: {final_stats['laziness_count']}")
    print()
    
    if "circuit_breaker" in final_stats:
        total_loops = sum(
            agent_stats.get('total_loops_detected', 0)
            for agent_stats in final_stats['circuit_breaker']['agents'].values()
        )
        print(f"Circuit Breaker Impact:")
        print(f"  - Total loops prevented: {total_loops}")
        print(f"  - Agents monitored: {len(final_stats['circuit_breaker']['agents'])}")
        print()
    
    if "lazy_evaluation" in final_stats:
        global_stats = final_stats['lazy_evaluation']['global']
        print(f"Lazy Evaluation Impact:")
        print(f"  - Computations deferred: {global_stats['total_deferrals']}")
        print(f"  - Time saved: {global_stats['total_savings_seconds']:.2f} seconds")
        print(f"  - Agents using lazy eval: {global_stats['total_agents']}")
        print()
    
    print("✓ Both features successfully prevent wasted computation!")
    print("  • Circuit Breaker: Stops infinite loops (I'm sorry, I can't...)")
    print("  • Lazy Evaluation: Defers expensive/speculative work")
    print()
    print("Result: Scale by Subtraction - removing complexity, not adding it!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
