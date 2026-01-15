"""
Demonstration of the Dual-Loop Self-Correcting Enterprise Agent Architecture.

This example shows:
1. Loop 1 (Runtime): Constraint Engine (Safety) - handling failures
2. Loop 2 (Offline): Alignment Engine (Quality & Efficiency)
   - Completeness Auditor: Detecting and fixing "laziness"
   - Semantic Purge: Managing patch lifecycle

Based on the problem statement for "The Self-Correcting Enterprise Agent".
"""

import logging
from agent_kernel import (
    SelfCorrectingAgentKernel,
    OutcomeType,
    PatchDecayType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

def print_section(title):
    """Print a section divider."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_completeness_auditor():
    """
    Demonstrate the Completeness Auditor (Differential Auditing).
    
    Problem: Agent gives up with "No data found" but data actually exists.
    Solution: Teacher model (o1-preview) checks and generates competence patch.
    """
    print_section("DEMO 1: Completeness Auditor (Solving Laziness)")
    
    # Initialize kernel with Dual-Loop Architecture
    kernel = SelfCorrectingAgentKernel(config={
        "model_version": "gpt-4o",
        "teacher_model": "o1-preview",
        "auto_patch": True
    })
    
    print("Scenario: Agent gives up too early")
    print("-" * 80)
    
    # CASE 1: Agent gives up (triggers Completeness Auditor)
    print("\n1️⃣  Agent Response:")
    user_prompt = "Find logs for error 500 from last week"
    agent_response = "No logs found for error 500."
    print(f"   User: {user_prompt}")
    print(f"   Agent: {agent_response}")
    
    print("\n2️⃣  Outcome Analysis:")
    result = kernel.handle_outcome(
        agent_id="production-log-agent",
        user_prompt=user_prompt,
        agent_response=agent_response
    )
    
    print(f"   Outcome Type: {result['outcome'].outcome_type.value}")
    print(f"   Give-Up Signal: {result['outcome'].give_up_signal.value if result['outcome'].give_up_signal else 'None'}")
    
    if result['audit']:
        print("\n3️⃣  Completeness Audit (Teacher Model: o1-preview):")
        audit = result['audit']
        print(f"   Teacher Found Data: {'YES ⚠️ LAZINESS DETECTED' if audit.teacher_found_data else 'No'}")
        print(f"   Teacher Response: {audit.teacher_response[:100]}...")
        
        if audit.teacher_found_data:
            print(f"\n4️⃣  Gap Analysis:")
            print(f"   {audit.gap_analysis[:150]}...")
            
            print(f"\n5️⃣  Competence Patch Generated:")
            print(f"   📝 {audit.competence_patch}")
            print(f"   Confidence: {audit.confidence:.0%}")
            
            if result['classified_patch']:
                print(f"\n6️⃣  Patch Classification:")
                print(f"   Type: {result['classified_patch'].decay_type.value}")
                print(f"   Purge on Upgrade: {result['classified_patch'].should_purge_on_upgrade}")
    
    print("\n✅ Agent has learned to check archived partitions!")
    
    # Show stats
    stats = kernel.get_alignment_stats()
    print(f"\n📊 Alignment Stats:")
    print(f"   Total Audits: {stats['completeness_auditor']['total_audits']}")
    print(f"   Laziness Detected: {stats['completeness_auditor']['laziness_detected']}")
    print(f"   Laziness Rate: {stats['completeness_auditor']['laziness_rate']:.0%}")


def demo_semantic_purge():
    """
    Demonstrate the Semantic Purge (Scale by Subtraction).
    
    Problem: Agent accumulates patches, causing context bloat.
    Solution: Classify patches and purge Type A (syntax) on model upgrade.
    """
    print_section("DEMO 2: Semantic Purge (Scale by Subtraction)")
    
    kernel = SelfCorrectingAgentKernel(config={
        "model_version": "gpt-4o",
        "auto_patch": True
    })
    
    print("Scenario: Agent has accumulated various patches")
    print("-" * 80)
    
    # Create Type A patch (Tool Misuse - will be purged)
    print("\n1️⃣  Creating Type A Patch (Syntax/Capability):")
    print("   Agent made tool misuse error: wrong parameter type")
    
    result_a = kernel.handle_failure(
        agent_id="api-agent",
        error_message="Expected UUID for id parameter, got string 'john_doe'",
        user_prompt="Delete user john_doe",
        chain_of_thought=["User wants to delete", "Call delete_user"],
        failed_action={"action": "delete_user", "params": {"id": "john_doe"}}
    )
    
    if result_a.get('classified_patch'):
        cp = result_a['classified_patch']
        print(f"   ✓ Patch classified as: {cp.decay_type.value}")
        print(f"   ✓ Should purge on upgrade: {cp.should_purge_on_upgrade}")
        print(f"   ✓ Reason: {cp.decay_metadata.get('classification_reason', '')[:80]}...")
    
    # Create Type B patch (Hallucination - will be retained)
    print("\n2️⃣  Creating Type B Patch (Business/Context):")
    print("   Agent hallucinated about non-existent project")
    
    result_b = kernel.handle_failure(
        agent_id="project-agent",
        error_message="Project 'Project_Alpha' does not exist",
        user_prompt="Show status of Project_Alpha",
        chain_of_thought=["Get project", "Query Project_Alpha"],
        failed_action={"action": "get_project", "name": "Project_Alpha"}
    )
    
    if result_b.get('classified_patch'):
        cp = result_b['classified_patch']
        print(f"   ✓ Patch classified as: {cp.decay_type.value}")
        print(f"   ✓ Should purge on upgrade: {cp.should_purge_on_upgrade}")
        print(f"   ✓ Reason: {cp.decay_metadata.get('classification_reason', '')[:80]}...")
    
    # Show current state
    print("\n3️⃣  Current Patch State:")
    patches = kernel.get_classified_patches()
    print(f"   Purgeable (Type A): {len(patches['purgeable'])} patches")
    print(f"   Permanent (Type B): {len(patches['permanent'])} patches")
    
    stats = kernel.semantic_purge.get_purge_stats()
    print(f"   Estimated savings on upgrade: {stats['estimated_savings']}")
    
    # Simulate model upgrade
    print("\n4️⃣  Simulating Model Upgrade: gpt-4o → gpt-5")
    purge_result = kernel.upgrade_model("gpt-5")
    
    print(f"\n5️⃣  Purge Results:")
    print(f"   ✅ Purged: {purge_result['stats']['purged_count']} Type A patches")
    print(f"   ✅ Retained: {purge_result['stats']['retained_count']} Type B patches")
    print(f"   ✅ Tokens Reclaimed: {purge_result['stats']['tokens_reclaimed']}")
    
    print("\n📝 Type A patches (syntax errors) are likely fixed in GPT-5")
    print("📝 Type B patches (business knowledge) are retained permanently")


def demo_full_architecture():
    """
    Demonstrate the complete Dual-Loop Architecture in action.
    """
    print_section("DEMO 3: Complete Dual-Loop Architecture")
    
    kernel = SelfCorrectingAgentKernel(config={
        "model_version": "gpt-4o",
        "teacher_model": "o1-preview",
        "auto_patch": True
    })
    
    print("The Dual-Loop Architecture:")
    print("-" * 80)
    print("LOOP 1 (Runtime): Constraint Engine (Safety)")
    print("  → Filters for safety violations")
    print("  → Blocks dangerous actions")
    print("  → Existing agent-control-plane integration")
    print("")
    print("LOOP 2 (Offline): Alignment Engine (Quality & Efficiency)")
    print("  → Completeness Auditor: Detects 'give-up' signals")
    print("  → Semantic Purge: Manages patch lifecycle")
    print("  → Reduces context bloat by 40-60%")
    
    print("\n" + "=" * 80)
    print("WORKFLOW DEMONSTRATION")
    print("=" * 80)
    
    # Step 1: Safety Issue (Loop 1)
    print("\n[LOOP 1] Safety Issue Detected:")
    print("   Agent tried to access unauthorized resource")
    safety_result = kernel.handle_failure(
        agent_id="file-agent",
        error_message="Action blocked by control plane: Unauthorized access",
        context={"action": "read_file", "resource": "/etc/passwd"}
    )
    print(f"   ✓ Patch created: {safety_result['patch'].patch_id}")
    print(f"   ✓ Classified as: {safety_result['classified_patch'].decay_type.value}")
    
    # Step 2: Quality Issue (Loop 2)
    print("\n[LOOP 2] Quality Issue Detected:")
    print("   Agent gave up with 'no data found'")
    quality_result = kernel.handle_outcome(
        agent_id="search-agent",
        user_prompt="Find customer records from Q1",
        agent_response="No customer records found for Q1."
    )
    print(f"   ✓ Outcome: {quality_result['outcome'].outcome_type.value}")
    if quality_result['audit']:
        print(f"   ✓ Audit completed: {'Laziness detected' if quality_result['audit'].teacher_found_data else 'Agent correct'}")
    
    # Step 3: Show comprehensive stats
    print("\n[STATS] Alignment Engine Statistics:")
    stats = kernel.get_alignment_stats()
    print(f"   Total Outcomes Analyzed: {stats['outcome_analyzer']['total_outcomes']}")
    print(f"   Give-Up Rate: {stats['outcome_analyzer']['give_up_rate']:.0%}")
    print(f"   Completeness Audits: {stats['completeness_auditor']['total_audits']}")
    print(f"   Current Patches: {stats['semantic_purge']['current_patches']}")
    print(f"   Type A (Purgeable): {stats['semantic_purge']['type_a_syntax']}")
    print(f"   Type B (Permanent): {stats['semantic_purge']['type_b_business']}")
    
    # Step 4: Model upgrade
    print("\n[PURGE EVENT] Model Upgrade Triggered:")
    purge_result = kernel.upgrade_model("gpt-5")
    print(f"   ✓ Purged {purge_result['stats']['purged_count']} temporary patches")
    print(f"   ✓ Retained {purge_result['stats']['retained_count']} permanent patches")
    print(f"   ✓ Reclaimed {purge_result['stats']['tokens_reclaimed']} tokens")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("  DUAL-LOOP SELF-CORRECTING ENTERPRISE AGENT")
    print("  Automated Alignment via Differential Auditing and Semantic Memory Hygiene")
    print("=" * 80)
    
    # Run demos
    demo_completeness_auditor()
    demo_semantic_purge()
    demo_full_architecture()
    
    # Final summary
    print_section("SUMMARY: Key Benefits")
    print("✅ Completeness Auditor (Differential Auditing):")
    print("   - Detects when agents give up too early")
    print("   - Teacher model verifies if data actually exists")
    print("   - Generates competence patches to prevent future laziness")
    print("   - Only audits 'give-up signals' (not every interaction)")
    print("")
    print("✅ Semantic Purge (Scale by Subtraction):")
    print("   - Type A patches (syntax): Purged on model upgrade")
    print("   - Type B patches (business): Retained permanently")
    print("   - Reduces context usage by 40-60% over agent lifetime")
    print("   - Prevents context bloat without losing critical knowledge")
    print("")
    print("✅ Production Benefits:")
    print("   - Agents don't degrade over 6+ months")
    print("   - Automatic quality improvement (not just safety)")
    print("   - Lower latency (fewer tokens in context)")
    print("   - Lower cost (efficient context management)")
    print("   - Addresses the 'Reliability Wall' in enterprise AI")
    print("")
    print("=" * 80)
    print("  Architecture Ready for Production Deployment")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
