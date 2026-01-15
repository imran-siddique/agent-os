"""
Reference Implementation Demo

This demonstrates the three core components from the problem statement:
1. Completeness Auditor (auditor.py) - Detects soft failures
2. Shadow Teacher (teacher.py) - Diagnoses failures  
3. Memory Manager (memory_manager.py) - Manages lesson lifecycle

These are simplified reference implementations that show the core concepts.
For production use, see the full implementations in:
- completeness_auditor.py
- semantic_purge.py
- analyzer.py
"""

import asyncio
from agent_kernel import (
    SimpleCompletenessAuditor,
    diagnose_failure,
    MemoryManager,
    LessonType
)


def demo_completeness_auditor():
    """
    Demo 1: The Completeness Auditor
    
    Problem: Agent says "No logs found." - Is this laziness or truth?
    Solution: Use heuristic engine to flag "Low Information" responses.
    """
    print("=" * 80)
    print("DEMO 1: Completeness Auditor - Detecting Soft Failures")
    print("=" * 80)
    
    auditor = SimpleCompletenessAuditor()
    
    # Test Case 1: Agent gives up (LAZINESS)
    print("\n📋 Test Case 1: Agent gives up early")
    agent_response = "I cannot find any logs for that error."
    tool_output = None
    
    needs_intervention = auditor.audit_response(agent_response, tool_output)
    print(f"  Agent response: '{agent_response}'")
    print(f"  Needs intervention: {needs_intervention}")
    print(f"  ⚠️  Soft failure detected - agent gave up!")
    
    # Test Case 2: Tool returns empty (EMPTY SUCCESS)
    print("\n📋 Test Case 2: Tool returns empty results")
    agent_response = "Here are the logs:"
    tool_output = "[]"
    
    needs_intervention = auditor.audit_response(agent_response, tool_output)
    print(f"  Agent response: '{agent_response}'")
    print(f"  Tool output: '{tool_output}'")
    print(f"  Needs intervention: {needs_intervention}")
    print(f"  ⚠️  Empty success detected - tool returned nothing!")
    
    # Test Case 3: Agent succeeds (NORMAL)
    print("\n📋 Test Case 3: Agent succeeds properly")
    agent_response = "Found 247 error logs in the system."
    tool_output = '[{"timestamp": "2024-01-15", "level": "error"}]'
    
    needs_intervention = auditor.audit_response(agent_response, tool_output)
    print(f"  Agent response: '{agent_response}'")
    print(f"  Tool output length: {len(tool_output)} chars")
    print(f"  Needs intervention: {needs_intervention}")
    print(f"  ✓ Success - agent performed correctly!")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT: Auditor catches 'soft failures' that don't throw exceptions")
    print("=" * 80 + "\n")


async def demo_shadow_teacher():
    """
    Demo 2: The Shadow Teacher
    
    Problem: Agent failed. We need a "Patch," not just a retry.
    Solution: A stronger model (Teacher) debugs the weaker model (Student).
    """
    print("=" * 80)
    print("DEMO 2: Shadow Teacher - Counterfactual Engine")
    print("=" * 80)
    
    # Test Case: Agent failed to find logs
    print("\n📋 Failure Scenario: Agent couldn't find logs")
    prompt = "Find logs for error 500 from last week"
    failed_response = "No logs found for error 500."
    tool_trace = "search_logs(error_code='500', time_range='7d', location='recent')"
    
    print(f"  Original prompt: '{prompt}'")
    print(f"  Agent response: '{failed_response}'")
    print(f"  Tool trace: {tool_trace}")
    
    print("\n🧠 Calling Teacher Model (o1-preview) for diagnosis...")
    diagnosis = await diagnose_failure(prompt, failed_response, tool_trace)
    
    print(f"\n📊 Diagnosis Results:")
    print(f"  Root cause: {diagnosis['cause']}")
    print(f"  Lesson patch: {diagnosis['lesson_patch']}")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT: Teacher model identifies WHY it failed, not just THAT it failed")
    print("=" * 80 + "\n")
    
    return diagnosis


def demo_memory_manager():
    """
    Demo 3: The Semantic Purge
    
    Problem: Your prompt is getting fat with old lessons.
    Solution: Tag lessons so you can delete useless ones later.
    """
    print("=" * 80)
    print("DEMO 3: Memory Manager - Semantic Purge")
    print("=" * 80)
    
    manager = MemoryManager()
    
    # Add various lesson types
    print("\n📝 Adding lessons to memory...")
    
    # Type A: Syntax lessons (will be purged on upgrade)
    manager.add_lesson(
        "Always output responses in JSON format",
        LessonType.SYNTAX
    )
    manager.add_lesson(
        "Use UUID type for all ID parameters",
        LessonType.SYNTAX
    )
    print("  ✓ Added 2 SYNTAX lessons (Type A - High Decay)")
    
    # Type B: Business lessons (permanent)
    manager.add_lesson(
        "Fiscal year starts in October, not January",
        LessonType.BUSINESS
    )
    manager.add_lesson(
        "Project_Alpha was deprecated in Q4 2023",
        LessonType.BUSINESS
    )
    manager.add_lesson(
        "When searching logs, always check archived partitions",
        LessonType.BUSINESS
    )
    print("  ✓ Added 3 BUSINESS lessons (Type B - Zero Decay)")
    
    # Type C: One-off lessons (delete immediately)
    manager.add_lesson(
        "Server maintenance scheduled for 2024-01-15",
        LessonType.ONE_OFF
    )
    print("  ✓ Added 1 ONE_OFF lesson (transient)")
    
    # Show initial state
    print("\n📊 Current Memory State:")
    counts = manager.get_lesson_count()
    print(f"  Total lessons: {len(manager.vector_store)}")
    for lesson_type, count in counts.items():
        print(f"    {lesson_type.value}: {count}")
    
    # Simulate model upgrade
    print("\n🔄 MODEL UPGRADE: gpt-4-0125 → gpt-5")
    print("  Triggering semantic purge...")
    
    result = manager.run_upgrade_purge("gpt-5")
    
    print(f"\n📉 Purge Results:")
    print(f"  Purged: {result['purged_count']} lessons")
    print(f"  Retained: {result['retained_count']} lessons")
    print(f"  New model: {result['new_model_version']}")
    
    # Show final state
    print("\n📊 After Purge:")
    remaining = manager.vector_store
    print(f"  Total lessons: {len(remaining)}")
    for lesson in remaining:
        print(f"    [{lesson['type'].value}] {lesson['text'][:60]}...")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT: Syntax lessons purged (likely fixed in GPT-5)")
    print("             Business lessons retained (world truths)")
    print("=" * 80 + "\n")


async def demo_full_workflow():
    """
    Demo 4: Full Integration
    
    Complete workflow showing how all three components work together.
    """
    print("=" * 80)
    print("DEMO 4: Full Integration - Complete Workflow")
    print("=" * 80)
    
    print("\n🎬 Scenario: Agent gives up finding user records")
    
    # Step 1: Auditor detects laziness
    print("\n[STEP 1] Completeness Auditor checks response...")
    auditor = SimpleCompletenessAuditor()
    agent_response = "No data found for active users."
    tool_output = None
    
    needs_intervention = auditor.audit_response(agent_response, tool_output)
    print(f"  Result: needs_intervention = {needs_intervention}")
    
    if needs_intervention:
        # Step 2: Teacher diagnoses the issue
        print("\n[STEP 2] Shadow Teacher diagnoses the failure...")
        diagnosis = await diagnose_failure(
            "Find active user records from last month",
            agent_response,
            "query_users(status='active', limit=100)"
        )
        print(f"  Cause: {diagnosis['cause']}")
        print(f"  Patch: {diagnosis['lesson_patch']}")
        
        # Step 3: Store the lesson
        print("\n[STEP 3] Memory Manager stores the lesson...")
        manager = MemoryManager()
        
        # Competence patches are always BUSINESS (domain knowledge)
        manager.add_lesson(
            diagnosis['lesson_patch'],
            LessonType.BUSINESS
        )
        print(f"  ✓ Stored as BUSINESS lesson (permanent)")
        
        # Verify
        business_lessons = manager.get_lessons_by_type(LessonType.BUSINESS)
        print(f"  ✓ Total business lessons: {len(business_lessons)}")
        
        print("\n[RESULT] Agent patched successfully!")
        print("  Next time: Agent will check all sources before giving up")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT: Complete OODA Loop - Observe → Orient → Decide → Act")
    print("             Output of Alignment Engine becomes input of next run")
    print("=" * 80 + "\n")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  REFERENCE IMPLEMENTATIONS DEMO".center(78) + "║")
    print("║" + "  Three Core Components for Deep & Difficult AI".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    # Demo 1: Completeness Auditor
    demo_completeness_auditor()
    
    # Demo 2: Shadow Teacher (async)
    asyncio.run(demo_shadow_teacher())
    
    # Demo 3: Memory Manager
    demo_memory_manager()
    
    # Demo 4: Full Integration (async)
    asyncio.run(demo_full_workflow())
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  SUMMARY: What We Built".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╠" + "=" * 78 + "╣")
    print("║  1. Completeness Auditor: Detects soft failures (laziness)" + " " * 17 + "║")
    print("║  2. Shadow Teacher: Diagnoses WHY failures happen" + " " * 25 + "║")
    print("║  3. Memory Manager: Manages lesson lifecycle (semantic purge)" + " " * 10 + "║")
    print("║" + " " * 78 + "║")
    print("║  Production implementations available in:" + " " * 33 + "║")
    print("║    - completeness_auditor.py (full differential auditing)" + " " * 15 + "║")
    print("║    - semantic_purge.py (patch classification)" + " " * 27 + "║")
    print("║    - analyzer.py (cognitive diagnosis)" + " " * 35 + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")


if __name__ == "__main__":
    main()
