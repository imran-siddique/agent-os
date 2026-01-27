"""
Integration test for Auditor-Patcher communication using schemas.

This test verifies that the data contracts (schemas) enable strict
communication between the Auditor and Patcher components.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.kernel.schemas import Lesson, FailureTrace, PatchRequest
from src.kernel.auditor import CompletenessAuditor
from agent_kernel.patcher import AgentPatcher
from agent_kernel.models import (
    AgentOutcome, OutcomeType, GiveUpSignal,
    AgentFailure, FailureType, FailureSeverity,
    FailureAnalysis, SimulationResult
)
from datetime import datetime


def test_schema_creation():
    """Test that schemas can be created and validated."""
    print("=" * 70)
    print("Test 1: Schema Creation and Validation")
    print("=" * 70)
    
    # Create a Lesson
    lesson = Lesson(
        trigger_pattern="search logs, empty result",
        rule_text="When searching logs, always check archived partitions if recent logs are empty",
        lesson_type="business",
        confidence_score=0.92
    )
    print(f"✅ Created Lesson: {lesson.id}")
    print(f"   Rule: {lesson.rule_text}")
    print()
    
    # Create a FailureTrace
    trace = FailureTrace(
        user_prompt="Find error 500 in logs",
        agent_reasoning="I searched for error 500 but found no matches.",
        tool_call={"tool": "search_logs", "query": "error 500"},
        tool_output="[]",
        failure_type="omission_laziness",
        severity="non_critical"
    )
    print(f"✅ Created FailureTrace: {trace.trace_id}")
    print(f"   Failure Type: {trace.failure_type}")
    print()
    
    # Create a PatchRequest
    patch_request = PatchRequest(
        trace_id=trace.trace_id,
        diagnosis="Agent gave up after empty search without trying archived logs",
        proposed_lesson=lesson,
        apply_strategy="batch_later"
    )
    print(f"✅ Created PatchRequest")
    print(f"   Trace ID: {patch_request.trace_id}")
    print(f"   Strategy: {patch_request.apply_strategy}")
    print(f"   Diagnosis: {patch_request.diagnosis}")
    print()
    
    return True


def test_auditor_patcher_flow():
    """Test the complete Auditor -> Patcher flow."""
    print("=" * 70)
    print("Test 2: Auditor-Patcher Integration Flow")
    print("=" * 70)
    
    # Step 1: Auditor detects laziness
    auditor = CompletenessAuditor()
    
    # Create an agent outcome that represents a lazy response
    outcome = AgentOutcome(
        agent_id="test-agent-001",
        outcome_type=OutcomeType.GIVE_UP,
        user_prompt="Find error 500 in logs",
        agent_response="I searched for error 500 but found no matches.",
        give_up_signal=GiveUpSignal.NO_DATA_FOUND,
        context={"tool_output": "[]"}
    )
    
    print("Step 1: Auditor detects laziness")
    print(f"   User Prompt: {outcome.user_prompt}")
    print(f"   Agent Response: {outcome.agent_response}")
    
    # Run audit
    audit_result = auditor.audit_give_up(outcome)
    print(f"   Laziness Detected: {audit_result.teacher_found_data}")
    print(f"   Competence Patch: {audit_result.competence_patch[:80]}...")
    print()
    
    if not audit_result.teacher_found_data:
        print("❌ Expected laziness to be detected, but it wasn't")
        return False
    
    # Step 2: Create schemas from audit result
    print("Step 2: Create structured schemas from audit result")
    
    # Create Lesson from competence patch
    lesson = Lesson(
        trigger_pattern="search logs, empty result, archived partition",
        rule_text=audit_result.competence_patch,
        lesson_type="business",
        confidence_score=audit_result.confidence
    )
    print(f"   Created Lesson: {lesson.id}")
    
    # Create FailureTrace
    trace = FailureTrace(
        user_prompt=outcome.user_prompt,
        agent_reasoning=outcome.agent_response,
        tool_call={"tool": "search_logs", "query": "error 500"},
        tool_output=outcome.context.get("tool_output"),
        failure_type="omission_laziness",
        severity="non_critical"
    )
    print(f"   Created FailureTrace: {trace.trace_id}")
    
    # Create PatchRequest
    patch_request = PatchRequest(
        trace_id=trace.trace_id,
        diagnosis=audit_result.gap_analysis,
        proposed_lesson=lesson,
        apply_strategy="batch_later"
    )
    print(f"   Created PatchRequest with strategy: {patch_request.apply_strategy}")
    print()
    
    # Step 3: Patcher applies the patch
    print("Step 3: Patcher applies the patch")
    
    patcher = AgentPatcher()
    
    # Create a failure analysis for the patcher
    failure = AgentFailure(
        agent_id=outcome.agent_id,
        failure_type=FailureType.LOGIC_ERROR,
        severity=FailureSeverity.MEDIUM,
        error_message="Agent gave up without exhaustive search",
        context={"audit_id": audit_result.audit_id}
    )
    
    analysis = FailureAnalysis(
        failure=failure,
        root_cause=patch_request.diagnosis,
        suggested_fixes=[lesson.rule_text],
        confidence_score=lesson.confidence_score
    )
    
    simulation = SimulationResult(
        simulation_id="sim-001",
        success=True,
        alternative_path=[{"action": "check_archived_logs"}],
        expected_outcome="Found logs in archived partition",
        risk_score=0.1,
        estimated_success_rate=0.9
    )
    
    # Create and apply patch
    patch = patcher.create_patch(
        agent_id=outcome.agent_id,
        analysis=analysis,
        simulation=simulation
    )
    
    print(f"   Created Patch: {patch.patch_id}")
    print(f"   Patch Type: {patch.patch_type}")
    
    # Apply the patch
    success = patcher.apply_patch(patch)
    
    if success:
        print(f"   ✅ Patch applied successfully")
        print(f"   Patch Content: {str(patch.patch_content)[:100]}...")
    else:
        print(f"   ❌ Patch failed to apply")
        return False
    
    print()
    
    # Step 4: Verify the patch was applied
    print("Step 4: Verify patch application")
    agent_state = patcher.get_agent_state(outcome.agent_id)
    print(f"   Agent Status: {agent_state.status}")
    print(f"   Patches Applied: {len(agent_state.patches_applied)}")
    print(f"   Latest Patch ID: {agent_state.patches_applied[-1] if agent_state.patches_applied else 'None'}")
    print()
    
    return True


def main():
    """Run all integration tests."""
    print()
    print("🔗 AUDITOR-PATCHER COMMUNICATION TEST")
    print("Testing the data contract 'spine' between Auditor and Patcher")
    print()
    
    results = []
    
    # Test 1: Schema creation
    try:
        result1 = test_schema_creation()
        results.append(("Schema Creation", result1))
    except Exception as e:
        print(f"❌ Test 1 failed with error: {e}")
        results.append(("Schema Creation", False))
    
    # Test 2: Integration flow
    try:
        result2 = test_auditor_patcher_flow()
        results.append(("Auditor-Patcher Flow", result2))
    except Exception as e:
        print(f"❌ Test 2 failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Auditor-Patcher Flow", False))
    
    # Print summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print()
        print("🎉 ALL TESTS PASSED!")
        print("The Auditor and Patcher can communicate using the data contracts.")
        return 0
    else:
        print()
        print("❌ SOME TESTS FAILED")
        print("Review the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
