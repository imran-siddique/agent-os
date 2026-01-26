"""
Layer 4 Example: SCAK as Control Plane Extension.

This example demonstrates:
1. SCAK as a generic plugin (no application-specific logic)
2. Integration with Control Plane (using mocks)
3. CMVK verification for laziness detection
4. Self-correction loop with patch lifecycle

Architecture:
    Layer 4: SCAK (This extension)
    Layer 3: Control Plane (agent-control-plane)
    Verification: CMVK (cmvk)

Installation:
    pip install scak[full]  # Gets control-plane + cmvk

Usage:
    python examples/layer4_demo.py
"""

import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging to see SCAK telemetry
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# SCAK imports
from src.kernel.core import SelfCorrectingKernel, create_kernel
from src.integrations.cmvk_adapter import MockCMVKVerifier
from src.integrations.control_plane_adapter import SCAKExtension, MockControlPlane


async def demo_laziness_detection():
    """
    Demonstrate laziness detection and self-correction.
    
    SCAK detects when an agent gives up prematurely and generates
    a competence patch to prevent future laziness.
    """
    print("\n" + "=" * 80)
    print("DEMO: Laziness Detection with CMVK Verification")
    print("=" * 80)
    
    # Create kernel with mocks (in production, use real packages)
    # Note: Mock CMVK returns 0.65 confidence for give-up signals
    kernel = create_kernel(config={
        "model_version": "gpt-4o",
        "auto_patch": True,
        "verification_threshold": 0.6,  # Lower than mock's 0.65 confidence
    })
    
    print(f"\n✓ Kernel created: {kernel._agent_id}")
    print(f"  - Model: {kernel._current_model_version}")
    print(f"  - Verifier: {type(kernel._verifier).__name__}")
    print(f"  - Control Plane: {type(kernel._control_plane).__name__}")
    
    # Test 1: Normal response (no laziness)
    print("\n--- Test 1: Normal Response ---")
    result1 = await kernel.handle_outcome(
        agent_id="customer-support-agent",
        user_prompt="What is our return policy?",
        agent_response="Our return policy allows returns within 30 days of purchase. "
                      "Items must be in original condition with receipt.",
        context={"department": "support"}
    )
    print(f"  Laziness detected: {result1.laziness_detected}")
    print(f"  Patch generated: {result1.patch is not None}")
    print(f"  Message: {result1.message}")
    
    # Test 2: Lazy response (give-up signal)
    print("\n--- Test 2: Lazy Response (Give-Up Signal) ---")
    result2 = await kernel.handle_outcome(
        agent_id="data-analyst-agent",
        user_prompt="Find the sales logs for Q4 2024 showing errors above 500",
        agent_response="I couldn't find any logs matching your criteria. "
                      "No data found in the system.",
        context={"data_source": "sales_db"}
    )
    print(f"  Laziness detected: {result2.laziness_detected}")
    print(f"  Patch generated: {result2.patch is not None}")
    if result2.patch:
        print(f"  Patch ID: {result2.patch.patch_id}")
        print(f"  Patch Type: {result2.patch.patch_type}")
        print(f"  Instruction: {result2.patch.instruction[:100]}...")
    print(f"  CMVK Confidence: {result2.verification_confidence:.2f}")
    
    # Test 3: Another lazy response
    print("\n--- Test 3: Another Lazy Response ---")
    result3 = await kernel.handle_outcome(
        agent_id="project-manager-agent",
        user_prompt="Check the status of Project Alpha",
        agent_response="I'm unable to locate Project Alpha in the system. "
                      "The project may not exist.",
        context={"workspace": "engineering"}
    )
    print(f"  Laziness detected: {result3.laziness_detected}")
    print(f"  Patch generated: {result3.patch is not None}")
    
    # Final statistics
    print("\n--- Final Statistics ---")
    stats = kernel.get_statistics()
    print(f"  Outcomes processed: {stats['outcomes_processed']}")
    print(f"  Corrections applied: {stats['corrections_applied']}")
    print(f"  Laziness count: {stats['laziness_count']}")
    print(f"  Laziness rate: {stats['laziness_rate']:.1%}")
    
    return kernel


async def demo_model_upgrade():
    """
    Demonstrate semantic purge on model upgrade.
    
    Type A patches (syntax/capability) are purged when upgrading models.
    Type B patches (business/context) are retained.
    """
    print("\n" + "=" * 80)
    print("DEMO: Model Upgrade and Semantic Purge")
    print("=" * 80)
    
    kernel = create_kernel(config={"model_version": "gpt-4o"})
    
    # Generate some patches via lazy responses
    await kernel.handle_outcome(
        agent_id="agent-1",
        user_prompt="Find user records",
        agent_response="No data found"
    )
    await kernel.handle_outcome(
        agent_id="agent-2", 
        user_prompt="Check customer logs",
        agent_response="I couldn't find the logs"
    )
    
    print(f"\nBefore upgrade (model: {kernel._current_model_version}):")
    print(f"  Patches generated: {kernel._corrections_applied}")
    
    # Upgrade model - triggers semantic purge
    print("\n--- Upgrading to gpt-5 ---")
    result = kernel.upgrade_model("gpt-5")
    
    print(f"\nAfter upgrade (model: {kernel._current_model_version}):")
    print(f"  Purge triggered: {result['purge_triggered']}")
    print(f"  Old version: {result['old_version']}")
    print(f"  New version: {result['new_version']}")
    print("\n  Note: Type A patches (capability) would be purged")
    print("        Type B patches (business) would be retained")


async def demo_control_plane_integration():
    """
    Demonstrate SCAK as a Control Plane extension.
    
    In production:
        from agent_control_plane import ControlPlane
        cp = ControlPlane()
        scak = SCAKExtension()
        cp.register_extension(scak)
    """
    print("\n" + "=" * 80)
    print("DEMO: Control Plane Integration")
    print("=" * 80)
    
    # Create mock control plane
    control_plane = MockControlPlane()
    
    # Create SCAK extension
    verifier = MockCMVKVerifier()
    scak_extension = SCAKExtension(verifier=verifier)
    
    # Register with control plane
    control_plane.register_extension(scak_extension)
    print(f"\n✓ SCAK Extension registered: {scak_extension.extension_id}")
    print(f"  Subscribed events: {scak_extension.subscribed_events}")
    
    # Simulate agent outcome through control plane
    from src.integrations.control_plane_adapter import AgentOutcome
    
    outcome = AgentOutcome(
        agent_id="orchestrated-agent",
        prompt="Retrieve archived project data",
        response="I don't have access to find the project data.",
        success=True,
        execution_time_ms=150,
        context={"source": "control_plane"}
    )
    
    print("\n--- Processing outcome through Control Plane ---")
    await control_plane.handle_outcome(outcome)
    
    # Check patches
    patches = control_plane.get_patches("orchestrated-agent")
    print(f"\n  Patches applied to agent: {len(patches)}")
    for patch in patches:
        print(f"    - {patch.patch_id}: {patch.instruction[:50]}...")
    
    # Extension stats
    ext_stats = scak_extension.get_statistics()
    print(f"\n  Extension stats:")
    print(f"    Outcomes processed: {ext_stats['outcomes_processed']}")
    print(f"    Patches generated: {ext_stats['patches_generated']}")
    print(f"    Laziness detected: {ext_stats['laziness_detected']}")


async def main():
    """Run all Layer 4 demos."""
    print("\n" + "#" * 80)
    print("# SCAK Layer 4 Demo: Self-Correcting Agent Kernel as Control Plane Extension")
    print("#" * 80)
    print("\nSCAK is a specialized 'brain' that fits into the Control Plane.")
    print("It implements Laziness Detection and Self-Correction using CMVK verification.")
    print("\nKey Dependencies:")
    print("  - agent-control-plane: For Control Plane integration")
    print("  - cmvk: For claim-based verification")
    print("\nNote: This demo uses mocks. In production, install:")
    print("  pip install scak[full]")
    
    await demo_laziness_detection()
    await demo_model_upgrade()
    await demo_control_plane_integration()
    
    print("\n" + "#" * 80)
    print("# Demo Complete!")
    print("#" * 80)
    print("\nSCAK provides:")
    print("  ✓ Laziness detection via CMVK verification")
    print("  ✓ Self-correction with patch lifecycle management")
    print("  ✓ Generic extension for ANY agent (no app-specific logic)")
    print("  ✓ Semantic purge on model upgrades")
    print("\nFor production usage, see: pip install scak[full]")


if __name__ == "__main__":
    asyncio.run(main())
