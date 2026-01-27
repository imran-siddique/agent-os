"""
Heuristic Router: Speed > Smarts

The Naive Approach:
"Let's use a small LLM (like GPT-3.5) to classify the user's intent, and then route it to the right model."

The Engineering Reality:
This is "Model-on-Model" overhead. Even a small LLM takes 500ms+ to think. 
You are adding latency just to decide where to send the traffic. 
We need to be Fast, even if we are occasionally Wrong.

My Philosophy:
Use Deterministic Heuristics, not AI Classifiers. 
We can solve 80% of routing with simple logic that takes 0ms:

Rule 1: Is the query length < 50 characters? -> Send to Fast Model (GPT-4o-mini).
Rule 2: Does it contain keywords like "Summary", "Analyze", "Compare"? -> Send to Smart Model (GPT-4o).
Rule 3: Is it a greeting ("Hi", "Thanks")? -> Send to Canned Response (Zero Cost).

The goal isn't 100% routing accuracy. 
The goal is instant response time for the trivial stuff, 
preserving the "Big Brain" budget for the hard stuff.
"""

from typing import Optional, List
from caas.models import ModelTier, RoutingDecision


class HeuristicRouter:
    """
    Heuristic router using deterministic rules for instant routing decisions.
    
    This router uses simple pattern matching and heuristics to route queries
    without the overhead of calling an LLM classifier. The goal is speed over
    perfect accuracy - we accept occasional wrong classifications to achieve
    near-zero latency routing decisions.
    
    Philosophy: Fast even if occasionally wrong > Slow but always right
    """
    
    # Greeting patterns (case-insensitive) - explicit greetings and farewells
    GREETING_PATTERNS = [
        "hi", "hello", "hey", "thanks", "thank you", "thx", 
        "bye", "goodbye"
    ]
    
    # Acknowledgment patterns (case-insensitive) - positive responses
    # Note: These are kept separate to avoid false positives in complex queries
    # e.g., "That's great, now analyze this data" should not be treated as greeting
    ACKNOWLEDGMENT_PATTERNS = [
        "ok", "okay", "got it", "cool", "great", "awesome", "perfect"
    ]
    
    # Smart model keywords (case-insensitive)
    SMART_KEYWORDS = [
        "summarize", "summary", "analyze", "analysis", "compare", "comparison",
        "evaluate", "assessment", "review", "critique", "explain in detail",
        "comprehensive", "thorough", "deep dive", "investigate", "research"
    ]
    
    # Query length threshold for fast model
    SHORT_QUERY_THRESHOLD = 50  # characters
    
    def __init__(
        self,
        short_query_threshold: int = 50,
        enable_canned_responses: bool = True
    ):
        """
        Initialize the heuristic router.
        
        Args:
            short_query_threshold: Maximum query length for fast model routing
            enable_canned_responses: Whether to route greetings to canned responses
        """
        self.short_query_threshold = short_query_threshold
        self.enable_canned_responses = enable_canned_responses
    
    def route(self, query: str) -> RoutingDecision:
        """
        Route a query to the appropriate model tier using deterministic heuristics.
        
        Decision Tree:
        1. Is it a greeting? -> CANNED (if enabled)
        2. Contains smart keywords? -> SMART
        3. Query length < threshold? -> FAST
        4. Default: SMART (for longer, complex queries)
        
        Args:
            query: The user query to route
            
        Returns:
            RoutingDecision with tier, reason, and confidence
        """
        query_lower = query.lower().strip()
        query_length = len(query)
        
        # Rule 3: Check for greetings (highest priority for zero cost)
        if self.enable_canned_responses and self._is_greeting(query_lower):
            return RoutingDecision(
                model_tier=ModelTier.CANNED,
                reason="Greeting detected - using canned response for zero cost",
                confidence=0.95,
                query_length=query_length,
                matched_keywords=self._get_matched_greetings(query_lower),
                suggested_model="canned_response",
                estimated_cost="zero"
            )
        
        # Rule 2: Check for smart model keywords
        matched_smart_keywords = self._get_matched_smart_keywords(query_lower)
        if matched_smart_keywords:
            return RoutingDecision(
                model_tier=ModelTier.SMART,
                reason=f"Complex task keywords detected: {', '.join(matched_smart_keywords)}",
                confidence=0.85,
                query_length=query_length,
                matched_keywords=matched_smart_keywords,
                suggested_model="gpt-4o",
                estimated_cost="high"
            )
        
        # Rule 1: Check query length for fast model
        if query_length < self.short_query_threshold:
            return RoutingDecision(
                model_tier=ModelTier.FAST,
                reason=f"Short query ({query_length} < {self.short_query_threshold} chars) - fast model sufficient",
                confidence=0.80,
                query_length=query_length,
                matched_keywords=[],
                suggested_model="gpt-4o-mini",
                estimated_cost="low"
            )
        
        # Default: Longer queries without smart keywords -> SMART model
        # (Better safe than sorry for longer queries)
        return RoutingDecision(
            model_tier=ModelTier.SMART,
            reason=f"Long query ({query_length} chars) - routing to smart model for quality",
            confidence=0.70,
            query_length=query_length,
            matched_keywords=[],
            suggested_model="gpt-4o",
            estimated_cost="high"
        )
    
    def _is_greeting(self, query_lower: str) -> bool:
        """
        Check if the query is a greeting or acknowledgment.
        
        Args:
            query_lower: Lowercase query string
            
        Returns:
            True if query is a greeting or acknowledgment
        """
        # Combine greeting and acknowledgment patterns
        all_patterns = self.GREETING_PATTERNS + self.ACKNOWLEDGMENT_PATTERNS
        
        # Check for exact matches (for single-word greetings/acknowledgments)
        if query_lower in all_patterns:
            return True
        
        # Check if query is very short and contains a greeting as a complete word
        words = query_lower.split()
        if len(words) <= 3:  # Short phrases like "hi there", "thank you"
            for pattern in all_patterns:
                # Use word boundary matching to avoid false positives like "thinking" matching "hi"
                if pattern in words:
                    return True
                # Also check for phrases that start/end with greeting as complete word
                if len(words) == 2 and (words[0] == pattern or words[1] == pattern):
                    return True
        
        return False
    
    def _get_matched_greetings(self, query_lower: str) -> List[str]:
        """Get list of matched greeting/acknowledgment patterns."""
        matched = []
        all_patterns = self.GREETING_PATTERNS + self.ACKNOWLEDGMENT_PATTERNS
        for pattern in all_patterns:
            if pattern in query_lower:
                matched.append(pattern)
        return matched
    
    def _get_matched_smart_keywords(self, query_lower: str) -> List[str]:
        """
        Get list of matched smart model keywords.
        
        Args:
            query_lower: Lowercase query string
            
        Returns:
            List of matched keywords
        """
        matched = []
        for keyword in self.SMART_KEYWORDS:
            if keyword in query_lower:
                matched.append(keyword)
        return matched
    
    def get_canned_response(self, query: str) -> Optional[str]:
        """
        Get a canned response for common greetings.
        
        Args:
            query: The user query
            
        Returns:
            Canned response string or None if not a greeting
        """
        query_lower = query.lower().strip()
        
        # Map greetings to responses
        greeting_responses = {
            "hi": "Hello! How can I assist you today?",
            "hello": "Hello! How can I assist you today?",
            "hey": "Hey there! What can I help you with?",
            "thanks": "You're welcome! Let me know if you need anything else.",
            "thank you": "You're welcome! Let me know if you need anything else.",
            "thx": "You're welcome!",
            "ok": "Great! Let me know if you need anything else.",
            "okay": "Great! Let me know if you need anything else.",
            "got it": "Perfect! Feel free to ask if you have more questions.",
            "cool": "Glad to help! Anything else?",
            "great": "Glad to help! Anything else?",
            "awesome": "Happy to help! Let me know if you need more.",
            "perfect": "Excellent! Feel free to ask more questions.",
            "bye": "Goodbye! Have a great day!",
            "goodbye": "Goodbye! Have a great day!"
        }
        
        # Check for exact or partial matches
        for pattern, response in greeting_responses.items():
            if query_lower == pattern or query_lower.startswith(pattern + " ") or query_lower.endswith(" " + pattern):
                return response
        
        # Default greeting response if it's detected as a greeting but no exact match
        if self._is_greeting(query_lower):
            return "Hello! How can I assist you today?"
        
        return None
