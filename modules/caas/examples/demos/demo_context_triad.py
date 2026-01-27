"""
Demo: Context Triad (Hot, Warm, Cold) - The Engineering Reality

This demo showcases the Context Triad system, which treats context like
a tiered storage system defined by intimacy, not just speed.
"""

from caas.triad import ContextTriadManager


def demo_context_triad():
    """Demonstrate the Context Triad system."""
    
    print("=" * 70)
    print("Context Triad Demo: Hot, Warm, Cold")
    print("=" * 70)
    
    manager = ContextTriadManager()
    
    # ========================================
    # Step 1: Add Hot Context (The Situation)
    # ========================================
    print("\n📍 Step 1: Adding Hot Context (The Situation)")
    print("-" * 70)
    print("Hot Context = What is happening RIGHT NOW?")
    print("Policy: 'Attention Head' - Overrides everything\n")
    
    manager.add_hot_context(
        "User is debugging: NullPointerException in AuthenticationService.login() at line 145",
        metadata={"source": "error_log", "severity": "error"},
        priority=3.0
    )
    print("✓ Added: Error log streaming in real-time")
    
    manager.add_hot_context(
        "Currently viewing: auth_service.py (lines 140-160)",
        metadata={"source": "vscode", "file": "auth_service.py"},
        priority=2.5
    )
    print("✓ Added: Open VS Code tab")
    
    manager.add_hot_context(
        "Current conversation: 'How do I fix this authentication error?'",
        metadata={"source": "chat", "user": "developer"},
        priority=3.0
    )
    print("✓ Added: Active conversation message")
    
    # ========================================
    # Step 2: Add Warm Context (The Persona)
    # ========================================
    print("\n👤 Step 2: Adding Warm Context (The Persona)")
    print("-" * 70)
    print("Warm Context = Who am I?")
    print("Policy: 'Always On Filter' - Colors how AI speaks to you\n")
    
    manager.add_warm_context(
        "Senior Backend Engineer specializing in Python and distributed systems",
        metadata={"category": "Profile", "source": "linkedin"},
        priority=2.0
    )
    print("✓ Added: Professional profile")
    
    manager.add_warm_context(
        "Coding Style: Prefers type hints, comprehensive docstrings, and pytest for testing",
        metadata={"category": "Preferences", "source": "settings"},
        priority=2.5
    )
    print("✓ Added: Coding style preferences")
    
    manager.add_warm_context(
        "Tech Stack: FastAPI, PostgreSQL, Redis, Docker, Kubernetes",
        metadata={"category": "Tech Stack", "source": "resume"},
        priority=1.8
    )
    print("✓ Added: Technology preferences")
    
    manager.add_warm_context(
        "Communication: Prefers detailed technical explanations with code examples",
        metadata={"category": "Communication", "source": "preferences"},
        priority=2.0
    )
    print("✓ Added: Communication style")
    
    # ========================================
    # Step 3: Add Cold Context (The Archive)
    # ========================================
    print("\n📦 Step 3: Adding Cold Context (The Archive)")
    print("-" * 70)
    print("Cold Context = What happened last year?")
    print("Policy: 'On Demand Only' - Never automatically included\n")
    
    manager.add_cold_context(
        "Ticket #1234 (2023-06-15): Fixed similar NullPointerException in UserService. "
        "Solution: Added null check before calling user.getEmail()",
        metadata={"date": "2023-06-15", "type": "ticket", "status": "closed"},
        priority=1.2
    )
    print("✓ Added: Old ticket from last year")
    
    manager.add_cold_context(
        "PR #567 (2023-08-20): Refactored authentication module to use dependency injection. "
        "Improved testability and fixed several edge cases.",
        metadata={"date": "2023-08-20", "type": "pr", "status": "merged"},
        priority=1.5
    )
    print("✓ Added: Closed PR from history")
    
    manager.add_cold_context(
        "Design Doc (2022-01-10): Legacy Authentication Flow. "
        "Describes the old token-based auth system before JWT migration.",
        metadata={"date": "2022-01-10", "type": "design_doc"},
        priority=0.8
    )
    print("✓ Added: Historical design document")
    
    # ========================================
    # Scenario 1: Default Behavior (Hot + Warm only)
    # ========================================
    print("\n\n" + "=" * 70)
    print("📋 Scenario 1: Default Behavior (Hot + Warm)")
    print("=" * 70)
    print("The Naive Approach: 'Stuff everything into the Context Window'")
    print("The Engineering Reality: Use intimacy-based tiers\n")
    
    result = manager.get_full_context(
        include_hot=True,
        include_warm=True,
        include_cold=False  # Cold is OFF by default
    )
    
    print(f"Layers Included: {result['layers_included']}")
    print(f"Total Tokens: ~{result['total_tokens']}")
    print(f"\nMetadata: {result['metadata']}")
    
    print("\n" + "-" * 70)
    print("HOT CONTEXT (Current Situation):")
    print("-" * 70)
    print(result['hot_context'][:500] + "..." if len(result['hot_context']) > 500 else result['hot_context'])
    
    print("\n" + "-" * 70)
    print("WARM CONTEXT (User Persona):")
    print("-" * 70)
    print(result['warm_context'][:500] + "..." if len(result['warm_context']) > 500 else result['warm_context'])
    
    print("\n" + "-" * 70)
    print("COLD CONTEXT (Archive):")
    print("-" * 70)
    print("❌ NOT INCLUDED (Policy: On Demand Only)")
    
    # ========================================
    # Scenario 2: With Cold Context (Explicit Query)
    # ========================================
    print("\n\n" + "=" * 70)
    print("📋 Scenario 2: Explicit Historical Query (Hot + Warm + Cold)")
    print("=" * 70)
    print("User asks: 'Have we seen this error before?'")
    print("Action: Fetch cold context with query='NullPointerException'\n")
    
    result = manager.get_full_context(
        include_hot=True,
        include_warm=True,
        include_cold=True,
        cold_query="NullPointerException"  # Explicit query for archive
    )
    
    print(f"Layers Included: {result['layers_included']}")
    print(f"Total Tokens: ~{result['total_tokens']}")
    
    print("\n" + "-" * 70)
    print("COLD CONTEXT (Archive - Query: 'NullPointerException'):")
    print("-" * 70)
    print(result['cold_context'])
    
    # ========================================
    # Scenario 3: Only Warm Context (System Prompt)
    # ========================================
    print("\n\n" + "=" * 70)
    print("📋 Scenario 3: System Prompt Setup (Warm Only)")
    print("=" * 70)
    print("Use Case: Initialize AI assistant with user persona")
    print("Warm context should be 'Always On' in system prompt\n")
    
    result = manager.get_full_context(
        include_hot=False,
        include_warm=True,
        include_cold=False
    )
    
    print(f"Layers Included: {result['layers_included']}")
    print("\n" + "-" * 70)
    print("WARM CONTEXT for System Prompt:")
    print("-" * 70)
    print(result['warm_context'])
    
    # ========================================
    # Key Insights
    # ========================================
    print("\n\n" + "=" * 70)
    print("🎯 Key Insights: The Context Triad")
    print("=" * 70)
    
    print("\n1. Hot Context (The Situation):")
    print("   - What: Current conversation, open files, streaming errors")
    print("   - Policy: 'Attention Head' - Overrides everything")
    print("   - Priority: Highest (always included)")
    
    print("\n2. Warm Context (The Persona):")
    print("   - What: User profile, coding preferences, communication style")
    print("   - Policy: 'Always On Filter' - Colors AI responses")
    print("   - Priority: Medium (persistent, part of system prompt)")
    
    print("\n3. Cold Context (The Archive):")
    print("   - What: Old tickets, closed PRs, historical docs")
    print("   - Policy: 'On Demand Only' - Requires explicit query")
    print("   - Priority: Low (never pollutes hot window)")
    
    print("\n" + "=" * 70)
    print("✅ The Context Triad solves the 'Flat Context Fallacy'")
    print("   by treating context as intimacy-based tiers, not just speed.")
    print("=" * 70)


if __name__ == "__main__":
    demo_context_triad()
