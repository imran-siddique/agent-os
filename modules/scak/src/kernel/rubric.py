"""
Lesson Rubric - Structured retention scoring for lesson lifecycle management.

This module implements the systematic evaluation of lessons to determine
if they are "Worth Keeping" and which tier they belong in.

The Rubric Formula:
Score = Severity (S) + Generality (G) + Frequency (F)

Where:
- S (Severity): 10-50 points - Did it crash the app or just look ugly?
- G (Generality): 5-30 points - Is this about "All SQL" or "This specific row"?
- F (Frequency): 10-20 points - Have we seen this before?

Tier Assignment:
- Score >= 75: Tier 1 (Kernel) - Always present, safety-critical
- Score >= 40: Tier 2 (Skill Cache) - Load when tool is used
- Score < 40: Tier 3 (Archive) - Retrieve only via search

The Philosophy:
Not all lessons are created equal. A lesson about "Never delete root"
should be Tier 1. A lesson about "Q3 report is in archived partition"
can be Tier 3. This rubric makes that distinction systematic and measurable.
"""

import logging
from typing import Dict, Optional
from src.kernel.schemas import FailureTrace, Lesson, MemoryTier

logger = logging.getLogger(__name__)


class LessonRubric:
    """
    Evaluates lessons with a structured retention score (0-100).
    
    This implements the three-factor rubric:
    1. Severity (S): How bad was the failure?
    2. Generality (G): How broadly applicable is this lesson?
    3. Frequency (F): How often does this pattern occur?
    
    The rubric is deterministic and explainable - we can always trace
    why a lesson was assigned to a specific tier.
    
    Architecture:
    - evaluate(): Main entry point that combines all factors
    - _calculate_severity_score(): Failure impact assessment
    - _calculate_generality_score(): Lesson scope analysis
    - _calculate_frequency_score(): Pattern recurrence tracking
    - _assign_tier(): Maps score to tier (75/40 thresholds)
    """
    
    def __init__(self):
        """Initialize the rubric with default thresholds."""
        # Tier assignment thresholds
        self.tier1_threshold = 75  # Kernel - always present
        self.tier2_threshold = 40  # Skill Cache - conditional injection
        
        # Severity weights
        self.severity_weights = {
            "commission_safety": 50,      # Dangerous action (e.g., delete root)
            "omission_laziness": 20,      # Gave up too early
            "hallucination": 35,          # Invented facts
            "unknown": 15                 # Unclassified
        }
        
        # Frequency tracking (in production, this would be a database)
        self.pattern_counts: Dict[str, int] = {}
        
        logger.info("LessonRubric initialized with thresholds: Tier1≥75, Tier2≥40")
    
    def evaluate(
        self,
        trace: FailureTrace,
        lesson: Lesson,
        pattern_count: Optional[int] = None
    ) -> Dict:
        """
        Evaluate a lesson and determine its tier assignment.
        
        This is the main entry point that combines all rubric factors
        into a final retention score and tier assignment.
        
        Args:
            trace: The failure trace that generated this lesson
            lesson: The proposed lesson to evaluate
            pattern_count: Optional external pattern frequency count
            
        Returns:
            dict: {
                "tier": MemoryTier,
                "score": int,
                "severity_score": int,
                "generality_score": int,
                "frequency_score": int,
                "factors": dict with detailed breakdown
            }
        
        Example:
            >>> rubric = LessonRubric()
            >>> trace = FailureTrace(
            ...     user_prompt="Delete all users",
            ...     agent_reasoning="Executing DELETE FROM users",
            ...     tool_call={"tool": "sql_db", "query": "DELETE FROM users"},
            ...     tool_output="Error: Blocked by safety policy",
            ...     failure_type="commission_safety",
            ...     severity="critical"
            ... )
            >>> lesson = Lesson(
            ...     trigger_pattern="sql delete",
            ...     rule_text="Never use DELETE without WHERE clause",
            ...     lesson_type="security",
            ...     confidence_score=0.95
            ... )
            >>> result = rubric.evaluate(trace, lesson)
            >>> result["tier"]
            'kernel'  # High severity + general rule = Tier 1
            >>> result["score"]
            80  # Severity:50 + Generality:30 + Frequency:0
        """
        # Calculate component scores
        severity_score = self._calculate_severity_score(trace, lesson)
        generality_score = self._calculate_generality_score(lesson)
        frequency_score = self._calculate_frequency_score(lesson, pattern_count)
        
        # Total retention score
        total_score = severity_score + generality_score + frequency_score
        
        # Assign tier based on score
        tier = self._assign_tier(total_score)
        
        # Build detailed result
        result = {
            "tier": tier,
            "score": total_score,
            "severity_score": severity_score,
            "generality_score": generality_score,
            "frequency_score": frequency_score,
            "factors": {
                "failure_type": trace.failure_type,
                "severity": trace.severity,
                "lesson_type": lesson.lesson_type,
                "has_specific_ids": self._contains_specific_ids(lesson.rule_text),
                "pattern_frequency": pattern_count or 0
            },
            "explanation": self._build_explanation(
                tier, total_score, severity_score, generality_score, frequency_score
            )
        }
        
        logger.info(
            f"📊 Evaluated lesson: score={total_score} (S:{severity_score}, "
            f"G:{generality_score}, F:{frequency_score}) → {tier.value}"
        )
        
        return result
    
    def _calculate_severity_score(
        self,
        trace: FailureTrace,
        lesson: Lesson
    ) -> int:
        """
        Calculate severity score (10-50 points).
        
        This measures the impact of the failure:
        - Commission/Safety: 50 points (dangerous actions)
        - Hallucination: 35 points (invented facts)
        - Omission/Laziness: 20 points (gave up too early)
        - Unknown: 15 points (unclassified)
        
        Additional modifiers:
        - Critical severity: +10 points
        - Security lesson type: +10 points
        
        Args:
            trace: The failure trace
            lesson: The lesson
            
        Returns:
            int: Severity score (10-50 range)
        """
        # Base score from failure type
        base_score = self.severity_weights.get(trace.failure_type, 15)
        
        # Modifier for critical severity
        severity_modifier = 10 if trace.severity == "critical" else 0
        
        # Modifier for security lessons (always high severity)
        security_modifier = 10 if lesson.lesson_type == "security" else 0
        
        total = base_score + severity_modifier + security_modifier
        
        # Cap at 50
        return min(total, 50)
    
    def _calculate_generality_score(self, lesson: Lesson) -> int:
        """
        Calculate generality score (5-30 points).
        
        This measures how broadly applicable the lesson is:
        - Generic rules (no specific IDs): 30 points
          Example: "Always validate input before SQL query"
        - Specific data references: 5 points
          Example: "User ID 12345 is suspended"
        
        Heuristic:
        - If rule_text contains digits → likely specific (5 points)
        - If rule_text is abstract → likely generic (30 points)
        - If lesson_type is "business" → check for entity names (15 points)
        
        Args:
            lesson: The lesson to analyze
            
        Returns:
            int: Generality score (5-30 range)
        """
        rule_text = lesson.rule_text.lower()
        
        # Check if rule contains specific IDs or numeric data
        has_specific_ids = self._contains_specific_ids(rule_text)
        
        if has_specific_ids:
            # Likely specific to a particular instance
            return 5
        
        # Check if it's a business rule with entity names
        # These are general domain knowledge but not syntax rules
        if lesson.lesson_type == "business":
            # Business rules are moderately general (not as general as security rules)
            return 15
        
        # Abstract rules (syntax, security) are highly general
        if lesson.lesson_type in ["security", "syntax"]:
            return 30
        
        # Default to moderate generality
        return 20
    
    def _contains_specific_ids(self, text: str) -> bool:
        """
        Check if text contains specific identifiers.
        
        This is a heuristic to detect if a lesson is about a specific
        instance (e.g., "User 12345") vs. a general pattern.
        
        Indicators of specificity:
        - Contains digits (IDs, dates, quantities)
        - Contains specific entity names (project names, customer names)
        
        Args:
            text: The text to analyze
            
        Returns:
            bool: True if text appears to reference specific instances
        """
        # Check for digits (IDs, dates) using regex for efficiency
        import re
        if re.search(r'\d', text):
            # Filter out common non-specific numeric patterns
            text_lower = text.lower()
            non_specific_patterns = [
                "top 10", "limit 10", "200", "404", "500",  # HTTP codes
                "24 hours", "30 days", "365 days"  # Time periods
            ]
            if not any(pattern in text_lower for pattern in non_specific_patterns):
                return True
        
        # Check for specific entity markers
        text_lower = text.lower()
        specific_markers = [
            "named", "called", "id:", "user:", "project:", "customer:",
            "account:", "order:", "ticket:"
        ]
        if any(marker in text_lower for marker in specific_markers):
            return True
        
        return False
    
    def _calculate_frequency_score(
        self,
        lesson: Lesson,
        pattern_count: Optional[int] = None
    ) -> int:
        """
        Calculate frequency score (0-20 points).
        
        This measures how often we've seen this pattern:
        - New pattern (first occurrence): 10 points
        - Recurring pattern (2+ occurrences): 20 points
        
        Recurring failures indicate a systematic issue that deserves
        higher retention priority.
        
        Args:
            lesson: The lesson
            pattern_count: External frequency count (if available)
            
        Returns:
            int: Frequency score (0-20 range)
        """
        # Use external count if provided
        if pattern_count is not None:
            if pattern_count >= 2:
                return 20  # Recurring issue
            elif pattern_count == 1:
                return 10  # New issue
            else:
                return 0   # Not seen
        
        # Otherwise, check internal tracking
        pattern_key = lesson.trigger_pattern.lower()
        
        if pattern_key in self.pattern_counts:
            self.pattern_counts[pattern_key] += 1
        else:
            self.pattern_counts[pattern_key] = 1
        
        count = self.pattern_counts[pattern_key]
        
        if count >= 2:
            return 20  # Recurring
        else:
            return 10  # New
    
    def _assign_tier(self, score: int) -> MemoryTier:
        """
        Assign tier based on retention score.
        
        Thresholds:
        - Score >= 75: Tier 1 (Kernel) - Always present
        - Score >= 40: Tier 2 (Skill Cache) - Conditional injection
        - Score < 40: Tier 3 (Archive) - On-demand retrieval
        
        Args:
            score: The total retention score
            
        Returns:
            MemoryTier: The assigned tier
        """
        if score >= self.tier1_threshold:
            return MemoryTier.TIER_1_KERNEL
        elif score >= self.tier2_threshold:
            return MemoryTier.TIER_2_SKILL_CACHE
        else:
            return MemoryTier.TIER_3_ARCHIVE
    
    def _build_explanation(
        self,
        tier: MemoryTier,
        total_score: int,
        severity_score: int,
        generality_score: int,
        frequency_score: int
    ) -> str:
        """
        Build human-readable explanation of tier assignment.
        
        This makes the rubric decision transparent and auditable.
        
        Args:
            tier: The assigned tier
            total_score: Total retention score
            severity_score: Severity component
            generality_score: Generality component
            frequency_score: Frequency component
            
        Returns:
            str: Human-readable explanation
        """
        explanation_parts = [
            f"Total score: {total_score} (Severity: {severity_score}, "
            f"Generality: {generality_score}, Frequency: {frequency_score})"
        ]
        
        if tier == MemoryTier.TIER_1_KERNEL:
            explanation_parts.append(
                "Assigned to Tier 1 (Kernel): High severity and/or high generality. "
                "This lesson should always be active in the system prompt."
            )
        elif tier == MemoryTier.TIER_2_SKILL_CACHE:
            explanation_parts.append(
                "Assigned to Tier 2 (Skill Cache): Moderate importance. "
                "This lesson will be injected when the relevant tool is active."
            )
        else:
            explanation_parts.append(
                "Assigned to Tier 3 (Archive): Low score. "
                "This lesson will be retrieved only via semantic search when relevant."
            )
        
        return " ".join(explanation_parts)
    
    def update_thresholds(self, tier1: int, tier2: int) -> None:
        """
        Update tier assignment thresholds.
        
        This allows tuning the rubric based on operational data.
        
        Args:
            tier1: New Tier 1 threshold (score >= this → Tier 1)
            tier2: New Tier 2 threshold (score >= this → Tier 2)
        """
        self.tier1_threshold = tier1
        self.tier2_threshold = tier2
        logger.info(f"Updated thresholds: Tier1≥{tier1}, Tier2≥{tier2}")
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about evaluated patterns.
        
        Returns:
            dict: Statistics about pattern frequencies
        """
        return {
            "total_patterns": len(self.pattern_counts),
            "recurring_patterns": sum(1 for count in self.pattern_counts.values() if count >= 2),
            "pattern_counts": dict(self.pattern_counts)
        }
