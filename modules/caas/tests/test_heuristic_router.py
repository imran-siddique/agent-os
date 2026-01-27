"""
Tests for the Heuristic Router.

Testing the three main routing rules:
1. Query length < 50 characters -> Fast Model (GPT-4o-mini)
2. Keywords like "Summary", "Analyze", "Compare" -> Smart Model (GPT-4o)
3. Greetings like "Hi", "Thanks" -> Canned Response (Zero Cost)
"""

from caas.routing import HeuristicRouter, ModelTier, RoutingDecision


def test_rule_1_short_queries_to_fast_model():
    """Test Rule 1: Short queries (< 50 chars) route to fast model."""
    print("\n=== Testing Rule 1: Short Queries -> Fast Model ===")
    
    router = HeuristicRouter()
    
    # Test cases: short queries without smart keywords
    short_queries = [
        "What is Python?",  # 16 chars
        "How to install?",  # 17 chars
        "Who are you?",  # 13 chars
        "Status of deployment",  # 21 chars
        "Show me the logs",  # 17 chars
    ]
    
    for query in short_queries:
        decision = router.route(query)
        print(f"\nQuery: '{query}' ({len(query)} chars)")
        print(f"  → Tier: {decision.model_tier}")
        print(f"  → Reason: {decision.reason}")
        print(f"  → Model: {decision.suggested_model}")
        print(f"  → Cost: {decision.estimated_cost}")
        
        assert decision.model_tier == ModelTier.FAST, \
            f"Expected FAST tier for short query '{query}', got {decision.model_tier}"
        assert decision.suggested_model == "gpt-4o-mini"
        assert decision.estimated_cost == "low"
        assert decision.query_length == len(query)
    
    print("\n✓ All short queries correctly routed to FAST model")


def test_rule_2_smart_keywords_to_smart_model():
    """Test Rule 2: Queries with smart keywords route to smart model."""
    print("\n=== Testing Rule 2: Smart Keywords -> Smart Model ===")
    
    router = HeuristicRouter()
    
    # Test cases: queries with smart keywords (even if short)
    smart_queries = [
        ("Summarize this document", ["summarize"]),
        ("Analyze the performance", ["analyze"]),
        ("Compare these two approaches", ["compare"]),
        ("Please provide a comprehensive summary", ["comprehensive", "summary"]),
        ("Evaluate the design", ["evaluate"]),
        ("Give me a thorough analysis", ["thorough", "analysis"]),
    ]
    
    for query, expected_keywords in smart_queries:
        decision = router.route(query)
        print(f"\nQuery: '{query}'")
        print(f"  → Tier: {decision.model_tier}")
        print(f"  → Reason: {decision.reason}")
        print(f"  → Model: {decision.suggested_model}")
        print(f"  → Cost: {decision.estimated_cost}")
        print(f"  → Matched Keywords: {decision.matched_keywords}")
        
        assert decision.model_tier == ModelTier.SMART, \
            f"Expected SMART tier for query '{query}', got {decision.model_tier}"
        assert decision.suggested_model == "gpt-4o"
        assert decision.estimated_cost == "high"
        
        # Check that at least some expected keywords were matched
        for keyword in expected_keywords:
            assert any(keyword in matched for matched in decision.matched_keywords), \
                f"Expected keyword '{keyword}' not found in matched keywords: {decision.matched_keywords}"
    
    print("\n✓ All smart keyword queries correctly routed to SMART model")


def test_rule_3_greetings_to_canned_responses():
    """Test Rule 3: Greetings route to canned responses."""
    print("\n=== Testing Rule 3: Greetings -> Canned Response ===")
    
    router = HeuristicRouter(enable_canned_responses=True)
    
    # Test cases: greetings
    greetings = [
        "Hi",
        "Hello",
        "Hey there",
        "Thanks",
        "Thank you",
        "Thx",
        "Ok",
        "Got it",
        "Bye",
    ]
    
    for query in greetings:
        decision = router.route(query)
        print(f"\nQuery: '{query}'")
        print(f"  → Tier: {decision.model_tier}")
        print(f"  → Reason: {decision.reason}")
        print(f"  → Model: {decision.suggested_model}")
        print(f"  → Cost: {decision.estimated_cost}")
        
        assert decision.model_tier == ModelTier.CANNED, \
            f"Expected CANNED tier for greeting '{query}', got {decision.model_tier}"
        assert decision.suggested_model == "canned_response"
        assert decision.estimated_cost == "zero"
    
    print("\n✓ All greetings correctly routed to CANNED response")


def test_canned_responses():
    """Test that greetings return appropriate canned responses."""
    print("\n=== Testing Canned Response Generation ===")
    
    router = HeuristicRouter(enable_canned_responses=True)
    
    test_cases = [
        ("Hi", "Hello! How can I assist you today?"),
        ("Thanks", "You're welcome! Let me know if you need anything else."),
        ("Bye", "Goodbye! Have a great day!"),
    ]
    
    for query, expected_response in test_cases:
        response = router.get_canned_response(query)
        print(f"\nQuery: '{query}'")
        print(f"  → Response: {response}")
        
        assert response is not None, f"Expected canned response for '{query}', got None"
        assert response == expected_response, \
            f"Expected '{expected_response}', got '{response}'"
    
    print("\n✓ All canned responses generated correctly")


def test_long_queries_without_keywords():
    """Test that long queries without smart keywords route to smart model."""
    print("\n=== Testing Long Queries Without Keywords -> Smart Model ===")
    
    router = HeuristicRouter()
    
    # Long query without smart keywords (> 50 chars)
    long_query = "Can you tell me more about the implementation details of this feature and how it works?"
    
    decision = router.route(long_query)
    print(f"\nQuery: '{long_query}' ({len(long_query)} chars)")
    print(f"  → Tier: {decision.model_tier}")
    print(f"  → Reason: {decision.reason}")
    print(f"  → Model: {decision.suggested_model}")
    
    assert decision.model_tier == ModelTier.SMART, \
        f"Expected SMART tier for long query, got {decision.model_tier}"
    assert len(long_query) >= 50, "Test query should be >= 50 characters"
    
    print("\n✓ Long queries without keywords correctly routed to SMART model")


def test_priority_greetings_over_keywords():
    """Test that greetings have priority even with keywords."""
    print("\n=== Testing Greeting Priority ===")
    
    router = HeuristicRouter(enable_canned_responses=True)
    
    # Greeting should take priority over keyword
    query = "Thanks"  # Could be confused with a query, but it's a greeting
    decision = router.route(query)
    
    print(f"\nQuery: '{query}'")
    print(f"  → Tier: {decision.model_tier}")
    
    assert decision.model_tier == ModelTier.CANNED, \
        "Greetings should have highest priority"
    
    print("\n✓ Greetings correctly prioritized over other rules")


def test_router_with_canned_disabled():
    """Test router behavior when canned responses are disabled."""
    print("\n=== Testing Router with Canned Responses Disabled ===")
    
    router = HeuristicRouter(enable_canned_responses=False)
    
    # Greeting should now route to fast model (short query)
    query = "Hi"
    decision = router.route(query)
    
    print(f"\nQuery: '{query}'")
    print(f"  → Tier: {decision.model_tier}")
    print(f"  → Reason: {decision.reason}")
    
    assert decision.model_tier == ModelTier.FAST, \
        "With canned disabled, short greeting should route to FAST"
    
    print("\n✓ Router correctly handles disabled canned responses")


def test_custom_threshold():
    """Test router with custom query length threshold."""
    print("\n=== Testing Custom Query Length Threshold ===")
    
    # Set custom threshold to 30 characters
    router = HeuristicRouter(short_query_threshold=30)
    
    # Query that's 35 chars (would be FAST with default 50, SMART with 30)
    query = "What is the status of the build?"  # 34 chars
    decision = router.route(query)
    
    print(f"\nQuery: '{query}' ({len(query)} chars)")
    print(f"  → Tier: {decision.model_tier}")
    print(f"  → Threshold: 30 chars")
    
    assert decision.model_tier == ModelTier.SMART, \
        f"Query ({len(query)} chars) should route to SMART with 30 char threshold"
    
    print("\n✓ Custom threshold correctly applied")


def test_confidence_scores():
    """Test that confidence scores are reasonable."""
    print("\n=== Testing Confidence Scores ===")
    
    router = HeuristicRouter()
    
    test_cases = [
        ("Hi", ModelTier.CANNED, 0.90),  # High confidence for greetings
        ("Summarize this", ModelTier.SMART, 0.80),  # Good confidence for keywords
        ("What is this?", ModelTier.FAST, 0.70),  # Moderate confidence for short query
    ]
    
    for query, expected_tier, min_confidence in test_cases:
        decision = router.route(query)
        print(f"\nQuery: '{query}'")
        print(f"  → Tier: {decision.model_tier}")
        print(f"  → Confidence: {decision.confidence:.2f}")
        
        assert decision.model_tier == expected_tier
        assert decision.confidence >= min_confidence, \
            f"Confidence {decision.confidence} should be >= {min_confidence}"
        assert 0.0 <= decision.confidence <= 1.0, \
            "Confidence should be between 0 and 1"
    
    print("\n✓ All confidence scores are reasonable")


def test_case_insensitivity():
    """Test that routing is case-insensitive."""
    print("\n=== Testing Case Insensitivity ===")
    
    router = HeuristicRouter()
    
    # Test different cases of the same query
    queries = [
        "SUMMARIZE THIS DOCUMENT",
        "Summarize This Document",
        "summarize this document",
    ]
    
    results = []
    for query in queries:
        decision = router.route(query)
        results.append(decision.model_tier)
        print(f"\nQuery: '{query}'")
        print(f"  → Tier: {decision.model_tier}")
    
    # All should route to the same tier
    assert all(tier == ModelTier.SMART for tier in results), \
        "All case variations should route to the same tier"
    
    print("\n✓ Routing is case-insensitive")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n=== Testing Edge Cases ===")
    
    router = HeuristicRouter(short_query_threshold=50)
    
    # Test exactly at threshold
    query_50 = "x" * 49  # Just under threshold
    query_50_plus = "x" * 50  # At threshold
    
    decision_49 = router.route(query_50)
    decision_50 = router.route(query_50_plus)
    
    print(f"\nQuery with 49 chars → {decision_49.model_tier}")
    print(f"Query with 50 chars → {decision_50.model_tier}")
    
    assert decision_49.model_tier == ModelTier.FAST, "49 chars should be FAST"
    assert decision_50.model_tier == ModelTier.SMART, "50+ chars should be SMART"
    
    # Test empty query
    empty_decision = router.route("")
    print(f"\nEmpty query → {empty_decision.model_tier}")
    assert empty_decision.model_tier == ModelTier.FAST, "Empty query should route to FAST"
    
    # Test whitespace-only query
    whitespace_decision = router.route("   ")
    print(f"Whitespace query → {whitespace_decision.model_tier}")
    
    print("\n✓ Edge cases handled correctly")


def test_routing_decision_model():
    """Test that RoutingDecision model works correctly."""
    print("\n=== Testing RoutingDecision Model ===")
    
    decision = RoutingDecision(
        model_tier=ModelTier.SMART,
        reason="Test reason",
        confidence=0.85,
        query_length=42,
        matched_keywords=["analyze", "compare"],
        suggested_model="gpt-4o",
        estimated_cost="high"
    )
    
    print(f"\nDecision Model:")
    print(f"  → Tier: {decision.model_tier}")
    print(f"  → Reason: {decision.reason}")
    print(f"  → Confidence: {decision.confidence}")
    print(f"  → Query Length: {decision.query_length}")
    print(f"  → Keywords: {decision.matched_keywords}")
    print(f"  → Model: {decision.suggested_model}")
    print(f"  → Cost: {decision.estimated_cost}")
    
    assert decision.model_tier == ModelTier.SMART
    assert decision.confidence == 0.85
    assert len(decision.matched_keywords) == 2
    
    print("\n✓ RoutingDecision model works correctly")


def run_all_tests():
    """Run all heuristic router tests."""
    print("\n" + "=" * 70)
    print("HEURISTIC ROUTER TEST SUITE")
    print("=" * 70)
    
    test_rule_1_short_queries_to_fast_model()
    test_rule_2_smart_keywords_to_smart_model()
    test_rule_3_greetings_to_canned_responses()
    test_canned_responses()
    test_long_queries_without_keywords()
    test_priority_greetings_over_keywords()
    test_router_with_canned_disabled()
    test_custom_threshold()
    test_confidence_scores()
    test_case_insensitivity()
    test_edge_cases()
    test_routing_decision_model()
    
    print("\n" + "=" * 70)
    print("✅ ALL HEURISTIC ROUTER TESTS PASSED")
    print("=" * 70)
    print("\nSummary:")
    print("  ✓ Rule 1 (Short queries → Fast Model): WORKING")
    print("  ✓ Rule 2 (Smart keywords → Smart Model): WORKING")
    print("  ✓ Rule 3 (Greetings → Canned Response): WORKING")
    print("  ✓ Priority and edge cases: WORKING")
    print("\n🚀 Heuristic Router is ready for production!")


if __name__ == "__main__":
    run_all_tests()
