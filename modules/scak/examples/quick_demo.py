"""
Quick demo of the Self-Correcting Agent Kernel.

This demonstrates the exact scenario from the problem statement:
"Your agent fails in production (blocked by agent-control-plane).
Instead of you fixing it manually, this engine wakes up, analyzes 
the failure, simulates a better path, and patches the agent."
"""

from agent_kernel import SelfCorrectingAgentKernel

def main():
    print("\n" + "="*80)
    print("🤖 SELF-CORRECTING AGENT KERNEL - DEMO")
    print("="*80 + "\n")
    
    # Scenario: Agent fails in production (blocked by agent-control-plane)
    print("📌 SCENARIO: Agent blocked by control plane in production\n")
    
    # Initialize the kernel
    kernel = SelfCorrectingAgentKernel()
    
    # Agent failure details
    agent_id = "production-agent-42"
    error = "Action blocked by agent-control-plane: Unauthorized resource access"
    context = {
        "action": "modify_system_config",
        "resource": "/etc/system.conf",
        "user": "agent-service-account"
    }
    
    print(f"❌ FAILURE DETECTED:")
    print(f"   Agent: {agent_id}")
    print(f"   Error: {error}\n")
    
    # The engine wakes up, analyzes, simulates, and patches
    print("🔄 Kernel waking up to fix the issue...\n")
    
    result = kernel.wake_up_and_fix(
        agent_id=agent_id,
        error_message=error,
        context=context
    )
    
    # Display results
    print("\n" + "="*80)
    print("✅ SELF-CORRECTION RESULTS")
    print("="*80 + "\n")
    
    analysis = result['analysis']
    simulation = result['simulation']
    patch = result['patch']
    
    print(f"🔍 Analysis:")
    print(f"   Root Cause: {analysis.root_cause}")
    print(f"   Confidence: {analysis.confidence_score:.1%}")
    print(f"   Suggested Fixes: {len(analysis.suggested_fixes)}")
    
    print(f"\n🎯 Simulation:")
    print(f"   Success Rate: {simulation.estimated_success_rate:.1%}")
    print(f"   Risk Score: {simulation.risk_score:.1%}")
    print(f"   Alternative Path: {len(simulation.alternative_path)} steps")
    
    print(f"\n🔧 Patch:")
    print(f"   Patch ID: {patch.patch_id}")
    print(f"   Type: {patch.patch_type}")
    print(f"   Applied: {patch.applied}")
    
    print(f"\n📊 Agent Status:")
    status = kernel.get_agent_status(agent_id)
    print(f"   Status: {status.status}")
    print(f"   Patches Applied: {len(status.patches_applied)}")
    
    print("\n" + "="*80)
    print("🎉 Agent is now fixed and running! No manual intervention needed.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
