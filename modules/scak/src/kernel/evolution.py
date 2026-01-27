"""
Adaptive Reward Shaping - Online RLAIF for Agent Behavior Evolution.

This implements "Scale by Addition" in the behavioral space - we don't retrain models,
we shape their behavior dynamically via context injection and rubric adjustment.

Core Principle: Reward = Outcome Quality × Behavioral Nudge
Where Behavioral Nudge is derived from real-time feedback (RLAIF-lite).

Architecture:
1. RewardShaper - Main orchestrator for reward evolution
2. FeedbackAnalyzer - Extracts correction vectors from feedback
3. RubricOptimizer - Applies gradients to rubric weights
4. NudgeGenerator - Converts weight changes to natural language instructions
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.kernel.schemas import (
    SwarmTrace, Rubric, RubricUpdate, AgentPerformance
)

logger = logging.getLogger(__name__)


class FeedbackAnalyzer:
    """
    Extracts correction vectors from user/teacher feedback.
    
    This is the "critic" that analyzes feedback like:
    - "Too verbose" → Increase conciseness weight
    - "Not thorough enough" → Increase thoroughness weight
    - "Good balance" → Keep current weights
    
    In production, this would use an LLM to parse natural language feedback
    into structured correction vectors.
    """
    
    def __init__(self, teacher_model: str = "gpt-4o"):
        """
        Initialize feedback analyzer.
        
        Args:
            teacher_model: Model to use for feedback analysis
        """
        self.teacher_model = teacher_model
    
    async def analyze_preference(self, feedback: str) -> Dict[str, Any]:
        """
        Analyze feedback and extract correction vector.
        
        Args:
            feedback: Natural language feedback (e.g., "Too verbose")
            
        Returns:
            dict: {
                "correction_vector": {"conciseness": +0.15, "thoroughness": -0.15},
                "reasoning": "User prefers brevity",
                "confidence": 0.85
            }
        """
        feedback_lower = feedback.lower()
        
        # Pattern matching for common feedback types
        # In production, use LLM to parse natural language
        
        if any(word in feedback_lower for word in ["verbose", "wordy", "too long", "brief", "concise"]):
            return {
                "correction_vector": {
                    "conciseness": 0.15,
                    "thoroughness": -0.10,
                    "accuracy": -0.05  # Slight decrease to rebalance
                },
                "reasoning": "User prefers more concise responses",
                "confidence": 0.85
            }
        
        elif any(word in feedback_lower for word in ["thorough", "detailed", "more info", "comprehensive"]):
            return {
                "correction_vector": {
                    "thoroughness": 0.15,
                    "conciseness": -0.10,
                    "accuracy": -0.05
                },
                "reasoning": "User wants more thorough analysis",
                "confidence": 0.85
            }
        
        elif any(word in feedback_lower for word in ["accurate", "correct", "precise", "wrong", "error"]):
            return {
                "correction_vector": {
                    "accuracy": 0.15,
                    "conciseness": -0.07,
                    "thoroughness": -0.08
                },
                "reasoning": "User prioritizes accuracy over other factors",
                "confidence": 0.90
            }
        
        elif any(word in feedback_lower for word in ["perfect", "good", "excellent", "great"]):
            # Positive feedback - no change
            return {
                "correction_vector": {},
                "reasoning": "User satisfied with current behavior",
                "confidence": 0.95
            }
        
        else:
            # Unknown feedback - no change
            return {
                "correction_vector": {},
                "reasoning": "Unable to parse feedback",
                "confidence": 0.50
            }


class RubricOptimizer:
    """
    Applies correction vectors to rubric weights.
    
    Implements constrained optimization:
    - Weights must sum to 1.0 (probability distribution)
    - Weights must be non-negative
    - Changes are clipped to prevent extreme swings
    
    This is inspired by online learning algorithms but simplified
    for interpretability.
    """
    
    def __init__(self, learning_rate: float = 1.0, max_delta: float = 0.2):
        """
        Initialize rubric optimizer.
        
        Args:
            learning_rate: How aggressively to apply corrections (0.0-1.0)
            max_delta: Maximum change per weight per update
        """
        self.learning_rate = learning_rate
        self.max_delta = max_delta
    
    def apply_gradient(
        self,
        current_rubric: Rubric,
        correction_vector: Dict[str, float]
    ) -> Rubric:
        """
        Apply correction vector to rubric weights.
        
        Args:
            current_rubric: Current rubric
            correction_vector: Desired changes (e.g., {"conciseness": +0.15})
            
        Returns:
            Rubric: New rubric with updated weights
        """
        if not correction_vector:
            # No changes
            return current_rubric
        
        # Copy current weights
        new_weights = dict(current_rubric.weights)
        
        # Apply corrections with clipping
        for criterion, delta in correction_vector.items():
            if criterion in new_weights:
                # Apply learning rate and clip to max_delta
                scaled_delta = delta * self.learning_rate
                clipped_delta = max(min(scaled_delta, self.max_delta), -self.max_delta)
                
                new_weights[criterion] += clipped_delta
        
        # Ensure non-negative
        for criterion in new_weights:
            new_weights[criterion] = max(new_weights[criterion], 0.0)
        
        # Normalize to sum to 1.0
        total = sum(new_weights.values())
        if total > 0:
            for criterion in new_weights:
                new_weights[criterion] /= total
        
        # Create new rubric
        new_rubric = Rubric(
            weights=new_weights,
            version=current_rubric.version + 1,
            parent_rubric_id=current_rubric.rubric_id
        )
        
        logger.info(
            f"Applied gradient: {correction_vector} "
            f"→ weights={new_weights}"
        )
        
        return new_rubric


class NudgeGenerator:
    """
    Converts rubric weight changes to natural language "behavioral nudges".
    
    These nudges are injected into the agent's system prompt to guide behavior
    without retraining.
    
    Example:
    - {"conciseness": +0.15} → "Prioritize conciseness +15%. Be more brief."
    - {"accuracy": +0.10} → "Increase accuracy focus +10%. Double-check facts."
    """
    
    def generate_nudge(
        self,
        correction_vector: Dict[str, float],
        reasoning: str
    ) -> str:
        """
        Generate natural language behavioral nudge.
        
        Args:
            correction_vector: Weight changes
            reasoning: Why this change is being made
            
        Returns:
            str: Natural language instruction
        """
        if not correction_vector:
            return "No behavioral adjustments needed. Continue current approach."
        
        nudge_parts = ["Current Policy Update:"]
        
        # Identify main changes
        increases = {k: v for k, v in correction_vector.items() if v > 0.05}
        decreases = {k: v for k, v in correction_vector.items() if v < -0.05}
        
        if increases:
            for criterion, delta in increases.items():
                percentage = int(delta * 100)
                nudge_parts.append(
                    f"Prioritize {criterion} +{percentage}%."
                )
        
        if decreases:
            for criterion, delta in decreases.items():
                percentage = int(abs(delta) * 100)
                nudge_parts.append(
                    f"Reduce {criterion} focus -{percentage}%."
                )
        
        # Add reasoning
        nudge_parts.append(f"Rationale: {reasoning}")
        
        return " ".join(nudge_parts)


class RewardShaper:
    """
    Main orchestrator for adaptive reward shaping (RLAIF-lite).
    
    Lifecycle:
    1. Observe feedback from user or teacher agent
    2. Analyze feedback to extract correction vector
    3. Apply correction to rubric weights
    4. Generate natural language nudge for system prompt
    5. Track evolution history
    
    This implements "online learning" without fine-tuning - we shape
    behavior through dynamic context injection.
    
    Integration with v1:
    - CompletenessAuditor detects laziness → negative reward signal
    - FailureTriage routes critical failures → immediate rubric update
    - MemoryController stores evolution snapshots → rollback capability
    """
    
    def __init__(
        self,
        baseline_rubric: Optional[Rubric] = None,
        teacher_model: str = "gpt-4o",
        learning_rate: float = 1.0,
        max_delta: float = 0.2
    ):
        """
        Initialize reward shaper.
        
        Args:
            baseline_rubric: Starting rubric (uses default if None)
            teacher_model: Model for feedback analysis
            learning_rate: How aggressively to apply corrections
            max_delta: Maximum change per weight per update
        """
        self.current_rubric = baseline_rubric or Rubric()
        self.feedback_analyzer = FeedbackAnalyzer(teacher_model)
        self.optimizer = RubricOptimizer(learning_rate, max_delta)
        self.nudge_generator = NudgeGenerator()
        
        # Evolution history
        self.update_history: List[RubricUpdate] = []
        
        logger.info(
            f"RewardShaper initialized with baseline rubric v{self.current_rubric.version}"
        )
    
    async def shape_reward(
        self,
        trace: SwarmTrace,
        feedback: str
    ) -> RubricUpdate:
        """
        Main entry point: shape reward based on feedback.
        
        This is the core "online learning" loop:
        1. Analyze feedback → correction vector
        2. Apply to rubric → new weights
        3. Generate nudge → system prompt update
        
        Args:
            trace: The swarm trace that generated this outcome
            feedback: User/teacher feedback (e.g., "Too verbose")
            
        Returns:
            RubricUpdate with old rubric, new rubric, and prompt nudge
        """
        logger.info(f"🎯 Shaping reward based on feedback: '{feedback[:50]}...'")
        
        # Step 1: Analyze feedback
        analysis = await self.feedback_analyzer.analyze_preference(feedback)
        correction_vector = analysis["correction_vector"]
        reasoning = analysis["reasoning"]
        
        logger.info(
            f"📊 Correction vector: {correction_vector}"
        )
        
        # Step 2: Apply to rubric
        old_rubric = self.current_rubric
        new_rubric = self.optimizer.apply_gradient(old_rubric, correction_vector)
        self.current_rubric = new_rubric
        
        # Step 3: Generate nudge
        prompt_nudge = self.nudge_generator.generate_nudge(correction_vector, reasoning)
        
        logger.info(
            f"💡 Nudge: '{prompt_nudge[:80]}...'"
        )
        
        # Step 4: Create update record
        update = RubricUpdate(
            rubric_before=old_rubric,
            rubric_after=new_rubric,
            prompt_nudge=prompt_nudge,
            feedback_signal=feedback,
            correction_vector=correction_vector
        )
        
        self.update_history.append(update)
        
        logger.info(
            f"✅ Reward shaped: v{old_rubric.version} → v{new_rubric.version}"
        )
        
        return update
    
    def compute_reward(
        self,
        performance: AgentPerformance,
        rubric: Optional[Rubric] = None
    ) -> float:
        """
        Compute reward score for agent performance using rubric.
        
        This is a simple weighted sum:
        Reward = Σ(weight_i × score_i)
        
        In production, would integrate with actual performance metrics.
        
        Args:
            performance: Agent performance metrics
            rubric: Rubric to use (uses current if None)
            
        Returns:
            float: Reward score (0.0-1.0)
        """
        rubric = rubric or self.current_rubric
        
        # Mock: In production, would compute actual scores
        # For now, use success_rate as proxy
        base_score = performance.success_rate
        
        # Apply rubric weights (simplified)
        # In reality, would have separate metrics for each criterion
        weighted_score = base_score
        
        return weighted_score
    
    def get_current_rubric(self) -> Rubric:
        """Get current rubric."""
        return self.current_rubric
    
    def get_evolution_history(self, limit: int = 100) -> List[RubricUpdate]:
        """Get evolution history."""
        return self.update_history[-limit:]
    
    def rollback(self, version: int) -> bool:
        """
        Rollback to a previous rubric version.
        
        This is the "Scale by Subtraction" safety valve - if reward shaping
        goes wrong, we can revert to a known-good state.
        
        Args:
            version: Rubric version to rollback to
            
        Returns:
            bool: True if rollback succeeded
        """
        # Find the rubric with target version
        for update in reversed(self.update_history):
            if update.rubric_before.version == version:
                self.current_rubric = update.rubric_before
                logger.info(f"🔄 Rolled back to rubric v{version}")
                return True
        
        logger.warning(f"⚠️  Cannot rollback: version {version} not found")
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reward shaping statistics."""
        return {
            "current_version": self.current_rubric.version,
            "total_updates": len(self.update_history),
            "current_weights": dict(self.current_rubric.weights),
            "last_updated": self.update_history[-1].timestamp if self.update_history else None
        }


# Integration with v1 Auditor
def auditor_to_reward_signal(lazy_detected: bool, confidence: float) -> str:
    """
    Convert v1 CompletenessAuditor output to reward signal.
    
    This bridges v1 (laziness detection) with v2 (reward shaping).
    When auditor detects laziness, we convert it to negative feedback
    that decreases the reward for the agent.
    
    Args:
        lazy_detected: Whether laziness was detected
        confidence: Auditor confidence
        
    Returns:
        str: Feedback signal for RewardShaper
    """
    if lazy_detected:
        return f"Agent gave up too early (confidence: {confidence:.2f}). Need more thoroughness."
    else:
        return "Agent performed exhaustive search. Good thoroughness."
