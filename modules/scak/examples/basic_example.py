"""
Example usage of the Self-Correcting Agent Kernel.

This demonstrates how the kernel automatically fixes an agent that fails
due to being blocked by the agent control plane.
"""

import logging
from agent_kernel import SelfCorrectingAgentKernel

# Setup logging to see the kernel in action
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def example_control_plane_blocking():
    """
    Example: Agent blocked by control plane when trying to access a file.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE: Agent Blocked by Control Plane")
    print("=" * 80 + "\n")
    
    # Initialize the kernel
    kernel = SelfCorrectingAgentKernel()
    
    # Simulate an agent failure - blocked by control plane
    agent_id = "agent-file-processor-001"
    error_message = "Action blocked by control plane: Unauthorized file access"
    context = {
        "action": "delete_file",
        "resource": "/etc/passwd",
        "reason": "Permission denied"
    }
    
    # The kernel wakes up, analyzes, simulates, and patches
    result = kernel.wake_up_and_fix(
        agent_id=agent_id,
        error_message=error_message,
        context=context
    )
    
    # Display results
    print("\n" + "-" * 80)
    print("RESULTS:")
    print("-" * 80)
    print(f"Success: {result['success']}")
    print(f"Patch Applied: {result['patch_applied']}")
    print(f"Failure Type: {result['failure'].failure_type}")
    print(f"Root Cause: {result['analysis'].root_cause}")
    print(f"Confidence: {result['analysis'].confidence_score:.2%}")
    print(f"Expected Success Rate: {result['simulation'].estimated_success_rate:.2%}")
    print(f"Risk Score: {result['simulation'].risk_score:.2%}")
    print(f"\nSuggested Fixes:")
    for i, fix in enumerate(result['analysis'].suggested_fixes, 1):
        print(f"  {i}. {fix}")
    print(f"\nAlternative Path ({len(result['simulation'].alternative_path)} steps):")
    for step in result['simulation'].alternative_path:
        print(f"  Step {step['step']}: {step['description']}")
    print(f"\nPatch ID: {result['patch'].patch_id}")
    print(f"Patch Type: {result['patch'].patch_type}")
    print("-" * 80 + "\n")
    
    # Check agent status
    status = kernel.get_agent_status(agent_id)
    print(f"Agent Status: {status.status}")
    print(f"Patches Applied: {len(status.patches_applied)}")
    print()


def example_timeout_failure():
    """
    Example: Agent timeout failure.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE: Agent Timeout Failure")
    print("=" * 80 + "\n")
    
    kernel = SelfCorrectingAgentKernel()
    
    agent_id = "agent-data-processor-002"
    error_message = "Operation timed out after 10 seconds"
    context = {
        "action": "process_large_dataset",
        "dataset_size": "10GB",
        "timeout": "10s"
    }
    
    result = kernel.handle_failure(
        agent_id=agent_id,
        error_message=error_message,
        context=context,
        auto_patch=True
    )
    
    print(f"\nTimeout Failure Handled:")
    print(f"  Root Cause: {result['analysis'].root_cause}")
    print(f"  Alternative Path: {len(result['simulation'].alternative_path)} steps")
    print(f"  Patch Applied: {result['patch_applied']}")
    print()


def example_multiple_failures():
    """
    Example: Multiple failures from the same agent showing learning.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE: Multiple Failures - Learning from History")
    print("=" * 80 + "\n")
    
    kernel = SelfCorrectingAgentKernel()
    agent_id = "agent-api-caller-003"
    
    # First failure
    print("First failure...")
    kernel.handle_failure(
        agent_id=agent_id,
        error_message="Action blocked: Invalid API endpoint access",
        context={"endpoint": "/admin/users", "method": "DELETE"}
    )
    
    # Second similar failure - should have higher confidence
    print("\nSecond similar failure...")
    result = kernel.handle_failure(
        agent_id=agent_id,
        error_message="Action blocked: Invalid API endpoint access",
        context={"endpoint": "/admin/settings", "method": "DELETE"}
    )
    
    print(f"\nLearning from history:")
    print(f"  Similar failures found: {len(result['analysis'].similar_failures)}")
    print(f"  Confidence improved to: {result['analysis'].confidence_score:.2%}")
    
    # Show failure history
    history = kernel.get_failure_history(agent_id=agent_id)
    print(f"  Total failures for agent: {len(history)}")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SELF-CORRECTING AGENT KERNEL" + " " * 30 + "║")
    print("║" + " " * 30 + "Examples" + " " * 40 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Run examples
    example_control_plane_blocking()
    example_timeout_failure()
    example_multiple_failures()
    
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80 + "\n")
