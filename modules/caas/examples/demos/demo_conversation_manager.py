"""
Demonstration of the Sliding Window (FIFO) Conversation Management.

The Brutal Squeeze Philosophy:
"Chopping > Summarizing"

This demo shows why FIFO sliding window is better than summarization
for managing conversation history in a frugal architecture.
"""

from caas.conversation import ConversationManager


def demo_basic_sliding_window():
    """Demonstrate basic sliding window functionality."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Sliding Window (FIFO)")
    print("="*70)
    
    # Create manager with small window for demonstration
    manager = ConversationManager(max_turns=5)
    
    print(f"\n📊 Configuration: Keeping last {manager.state.max_turns} turns")
    print("   Policy: FIFO (First In First Out)")
    print("   Philosophy: Chopping > Summarizing\n")
    
    # Simulate a conversation
    conversations = [
        ("How do I install Python?", "You can download it from python.org"),
        ("What about pip?", "pip comes bundled with Python 3.4+"),
        ("How do I create a virtual environment?", "Use: python -m venv myenv"),
        ("How do I activate it?", "On Windows: myenv\\Scripts\\activate, On Unix: source myenv/bin/activate"),
        ("What is requirements.txt?", "A file listing all dependencies for your project"),
        # These next turns will trigger FIFO deletions
        ("How do I install from requirements.txt?", "Use: pip install -r requirements.txt"),
        ("What about freezing dependencies?", "Use: pip freeze > requirements.txt"),
    ]
    
    for i, (user_msg, ai_msg) in enumerate(conversations, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {user_msg[:50]}...")
        manager.add_turn(user_msg, ai_msg)
        
        stats = manager.get_statistics()
        print(f"📈 Current: {stats['current_turns']} turns | Total ever: {stats['total_turns_ever']} | Deleted: {stats['deleted_turns']}")
    
    print("\n" + "-"*70)
    print("FINAL STATE:")
    print("-"*70)
    
    history = manager.get_conversation_history(format_as_text=False)
    print(f"\n✅ Kept {len(history)} most recent turns:")
    for i, turn in enumerate(history, 1):
        print(f"\n  Turn {i}:")
        print(f"    User: {turn.user_message[:60]}...")
        print(f"    AI: {turn.ai_response[:60]}...")
    
    stats = manager.get_statistics()
    print(f"\n🗑️  Deleted {stats['deleted_turns']} old turns")
    print(f"💾 Total turns processed: {stats['total_turns_ever']}")


def demo_no_information_loss():
    """Demonstrate that no information is lost through summarization."""
    print("\n\n" + "="*70)
    print("DEMO 2: No Information Loss (vs. Summarization)")
    print("="*70)
    
    manager = ConversationManager(max_turns=3)
    
    # Add a turn with specific details
    specific_message = """I'm getting error code 500 when calling the API endpoint /api/users/123. 
The exact error is: 'Internal Server Error: Connection timeout to database at db.example.com:5432'.
The logs show timestamp: 2024-01-03 14:23:45 UTC"""
    
    specific_response = """That's a database connection issue. Here's how to fix it:
1. Check if the database server is running on db.example.com:5432
2. Verify your connection string in config.py line 45
3. Check the firewall rules for port 5432
4. Look at the database logs at /var/log/postgresql/postgresql.log"""
    
    print("\n📝 Adding turn with SPECIFIC details:")
    print(f"   - Error code: 500")
    print(f"   - Endpoint: /api/users/123")
    print(f"   - Database: db.example.com:5432")
    print(f"   - Timestamp: 2024-01-03 14:23:45 UTC")
    print(f"   - Config file: config.py line 45")
    print(f"   - Log file: /var/log/postgresql/postgresql.log")
    
    manager.add_turn(specific_message, specific_response)
    
    # Verify exact retrieval
    history = manager.get_conversation_history(format_as_text=False)
    retrieved = history[0]
    
    print("\n✅ RETRIEVED (No Summarization):")
    print(f"   ALL details preserved:")
    assert "500" in retrieved.user_message
    assert "/api/users/123" in retrieved.user_message
    assert "db.example.com:5432" in retrieved.user_message
    assert "2024-01-03 14:23:45" in retrieved.user_message
    assert "config.py line 45" in retrieved.ai_response
    assert "/var/log/postgresql/postgresql.log" in retrieved.ai_response
    print("   ✓ Error code: 500")
    print("   ✓ Endpoint: /api/users/123")
    print("   ✓ Database: db.example.com:5432")
    print("   ✓ Timestamp: 2024-01-03 14:23:45 UTC")
    print("   ✓ Config file: config.py line 45")
    print("   ✓ Log file: /var/log/postgresql/postgresql.log")
    
    print("\n❌ WITH SUMMARIZATION (Hypothetical):")
    print("   'User encountered API error. System provided troubleshooting steps.'")
    print("   LOST: Error code, endpoint, database host, timestamp, file paths!")
    
    print("\n🎯 Conclusion: Sliding Window = LOSSLESS")


def demo_recent_precision():
    """Demonstrate that recent turns are what matter most."""
    print("\n\n" + "="*70)
    print("DEMO 3: Recent Precision > Vague History")
    print("="*70)
    
    manager = ConversationManager(max_turns=5)
    
    print("\n📖 Simulating a debugging session...\n")
    
    # Simulate debugging session
    debug_session = [
        ("I'm debugging a function", "Let me help you with that"),
        ("Here's my code: def process_data(items):", "I see the function signature"),
        ("    for item in items:", "You're iterating over items"),
        ("        result = item.value * 2", "You're doubling the value"),
        ("        print(result)", "You're printing the result"),
        # Critical recent interaction
        ("Wait, I just realized the bug! Line 4 should be item.value * 3 not * 2", 
         "Ah! So the multiplication factor is wrong. Change line 4 to multiply by 3."),
        ("Yes! That fixed it. The output is now correct.", "Great! The bug is fixed."),
    ]
    
    for user_msg, ai_msg in debug_session:
        manager.add_turn(user_msg, ai_msg)
    
    print("💡 KEY INSIGHT:")
    print("   User just discovered the bug is on line 4: multiply by 3 not 2")
    print("   They need to see this EXACT detail in the next turn\n")
    
    # Get recent turns
    recent = manager.get_recent_turns(n=3)
    
    print("📊 Last 3 turns (perfectly preserved):")
    for i, turn in enumerate(recent, 1):
        print(f"\n  Turn {i}:")
        print(f"    User: {turn.user_message}")
        print(f"    AI: {turn.ai_response}")
    
    # Verify critical detail is preserved (check if any of the recent turns has the detail)
    has_line4_detail = any("line 4" in turn.user_message.lower() for turn in recent)
    has_multiply3_detail = any("multiply by 3" in turn.user_message.lower() or "* 3" in turn.user_message for turn in recent)
    
    assert has_line4_detail, "Expected 'line 4' detail to be preserved in recent turns"
    assert has_multiply3_detail, "Expected '* 3' or 'multiply by 3' detail to be preserved in recent turns"
    
    print("\n✅ User can see EXACT fix: 'line 4 should be item.value * 3 not * 2'")
    print("   No vague summary like: 'User identified a calculation issue'")
    
    stats = manager.get_statistics()
    print(f"\n📈 Stats:")
    print(f"   Current turns: {stats['current_turns']}")
    print(f"   Total processed: {stats['total_turns_ever']}")
    print(f"   Deleted old turns: {stats['deleted_turns']}")


def demo_cost_comparison():
    """Compare cost of sliding window vs. summarization."""
    print("\n\n" + "="*70)
    print("DEMO 4: Cost Comparison (Sliding Window vs. Summarization)")
    print("="*70)
    
    print("\n💰 COST ANALYSIS:")
    print("\n   Scenario: 1000 conversations, 20 turns each\n")
    
    print("   ❌ SUMMARIZATION APPROACH:")
    print("      - Summarize every 10 turns")
    print("      - Cost per summary: $0.01 (GPT-4o call)")
    print("      - Summaries needed: 1000 conversations × 2 summaries = 2,000")
    print("      - Total cost: 2,000 × $0.01 = $20.00")
    print("      - Information loss: ⚠️  HIGH (loses error codes, exact wording)")
    
    print("\n   ✅ SLIDING WINDOW APPROACH:")
    print("      - Keep last 10 turns intact")
    print("      - Delete older turns (FIFO)")
    print("      - Cost per conversation: $0.00 (no AI calls)")
    print("      - Total cost: $0.00")
    print("      - Information loss: ✅ ZERO (what's kept is perfect)")
    
    print("\n   💡 SAVINGS:")
    print("      - Monthly cost reduction: $20.00")
    print("      - Annual cost reduction: $240.00")
    print("      - Per 10K conversations: $200.00")
    
    print("\n   🎯 KEY INSIGHT:")
    print("      Users rarely reference turns from 20 minutes ago")
    print("      They constantly reference code from 30 seconds ago")
    print("      → Recent Precision > Vague History")


def demo_fifo_behavior():
    """Demonstrate FIFO deletion behavior."""
    print("\n\n" + "="*70)
    print("DEMO 5: FIFO Deletion Behavior")
    print("="*70)
    
    manager = ConversationManager(max_turns=3)
    
    print(f"\n📦 Window size: {manager.state.max_turns} turns")
    print("   Policy: First In, First Out (FIFO)\n")
    
    turns_data = [
        ("Turn 1: Old question", "Old answer 1"),
        ("Turn 2: Another old question", "Old answer 2"),
        ("Turn 3: Getting recent", "Recent answer 3"),
        ("Turn 4: Very recent", "Recent answer 4"),
        ("Turn 5: Most recent", "Most recent answer 5"),
    ]
    
    for i, (user_msg, ai_msg) in enumerate(turns_data, 1):
        print(f"\n{'='*50}")
        print(f"Adding: {user_msg}")
        manager.add_turn(user_msg, ai_msg)
        
        current = manager.get_conversation_history(format_as_text=False)
        stats = manager.get_statistics()
        
        print(f"\n  Current window ({len(current)} turns):")
        for j, turn in enumerate(current, 1):
            print(f"    {j}. {turn.user_message}")
        
        if stats['deleted_turns'] > 0:
            print(f"\n  🗑️  Deleted: {stats['deleted_turns']} old turn(s)")
    
    print("\n" + "="*50)
    print("\n✅ FINAL STATE:")
    final = manager.get_conversation_history(format_as_text=False)
    print(f"   Kept last {len(final)} turns:")
    for i, turn in enumerate(final, 1):
        print(f"   {i}. {turn.user_message}")
    
    print("\n   Notice: Turns 1 and 2 are gone (FIFO)")
    print("   But turns 3, 4, and 5 are PERFECTLY intact!")


def run_all_demos():
    """Run all demonstration scenarios."""
    print("\n" + "="*70)
    print("SLIDING WINDOW CONVERSATION MANAGEMENT DEMO")
    print("The Brutal Squeeze: Chopping > Summarizing")
    print("="*70)
    
    demo_basic_sliding_window()
    demo_no_information_loss()
    demo_recent_precision()
    demo_cost_comparison()
    demo_fifo_behavior()
    
    print("\n\n" + "="*70)
    print("✅ ALL DEMOS COMPLETED!")
    print("="*70)
    
    print("\n🎯 KEY TAKEAWAYS:")
    print("   1. Sliding Window keeps recent turns PERFECTLY intact")
    print("   2. No AI cost for context management")
    print("   3. No information loss (what's kept is lossless)")
    print("   4. Users care about recent details, not old summaries")
    print("   5. Recent Precision > Vague History")
    
    print("\n💡 THE BRUTAL SQUEEZE PHILOSOPHY:")
    print("   Summarization = Lossy Compression (loses error codes, exact wording)")
    print("   Chopping (FIFO) = Lossless Compression (of the recent past)")
    print("   In a frugal architecture: Chopping > Summarizing")
    print("\n")


if __name__ == "__main__":
    run_all_demos()
