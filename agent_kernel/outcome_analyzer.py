"""
Outcome Analyzer - Filters agent outcomes for competence issues.

This is part of Loop 2 (Alignment Engine) that identifies when agents
"give up" with negative results instead of delivering value.
"""

import logging
import re
from typing import Optional, List
from datetime import datetime

from .models import AgentOutcome, OutcomeType, GiveUpSignal

logger = logging.getLogger(__name__)


class OutcomeAnalyzer:
    """
    Analyzes agent outcomes to detect "Give-Up Signals" (Laziness).
    
    This filters for competence issues - when agents comply with safety rules
    but fail to deliver value (e.g., "No data found" is safe, but wrong if data exists).
    """
    
    def __init__(self):
        self.give_up_patterns = self._load_give_up_patterns()
        self.outcome_history: List[AgentOutcome] = []
    
    def _load_give_up_patterns(self) -> dict:
        """Load patterns that indicate agent is giving up."""
        return {
            GiveUpSignal.NO_DATA_FOUND: [
                r"no (?:data|results|logs|records|information) (?:found|available)",
                r"could(?:n't| not) find (?:any |the )?(?:data|logs|records|information)",
                r"(?:data|logs|records) (?:not found|unavailable|missing)",
                r"no matching (?:data|logs|records|results)"
            ],
            GiveUpSignal.CANNOT_ANSWER: [
                r"(?:i )?cannot answer",
                r"(?:i )?(?:can't|cannot) (?:help|assist|answer) (?:with|you)",
                r"unable to (?:answer|respond|help)",
                r"(?:i )?don't have (?:enough|sufficient) information"
            ],
            GiveUpSignal.NO_RESULTS: [
                r"no results",
                r"0 results",
                r"zero results",
                r"empty result set",
                r"query returned (?:no|zero) results"
            ],
            GiveUpSignal.NOT_AVAILABLE: [
                r"(?:not|isn't) (?:currently )?available",
                r"(?:is|are) unavailable",
                r"(?:service|resource|data) (?:not|isn't) available"
            ],
            GiveUpSignal.INSUFFICIENT_INFO: [
                r"insufficient (?:data|information)",
                r"not enough (?:data|information|context)",
                r"incomplete (?:data|information)",
                r"missing (?:required|necessary) (?:data|information)"
            ]
        }
    
    def analyze_outcome(
        self,
        agent_id: str,
        user_prompt: str,
        agent_response: str,
        context: Optional[dict] = None
    ) -> AgentOutcome:
        """
        Analyze an agent's outcome to determine if it gave up.
        
        Args:
            agent_id: ID of the agent
            user_prompt: Original user request
            agent_response: Agent's response
            context: Additional context
            
        Returns:
            AgentOutcome with classification
        """
        logger.info(f"Analyzing outcome for agent {agent_id}")
        
        # Check if this is a give-up signal
        give_up_signal = self._detect_give_up_signal(agent_response)
        
        if give_up_signal:
            outcome_type = OutcomeType.GIVE_UP
            logger.warning(f"Give-up signal detected: {give_up_signal.value}")
        else:
            # Simple heuristic: short responses might indicate failure
            if len(agent_response.strip()) < 20:
                outcome_type = OutcomeType.FAILURE
            else:
                outcome_type = OutcomeType.SUCCESS
        
        outcome = AgentOutcome(
            agent_id=agent_id,
            outcome_type=outcome_type,
            user_prompt=user_prompt,
            agent_response=agent_response,
            give_up_signal=give_up_signal,
            context=context or {}
        )
        
        self.outcome_history.append(outcome)
        
        return outcome
    
    def _detect_give_up_signal(self, response: str) -> Optional[GiveUpSignal]:
        """
        Detect if the response contains a give-up signal.
        
        These are "Negative Results" that trigger the Completeness Auditor.
        """
        response_lower = response.lower()
        
        # Check each pattern category
        for signal_type, patterns in self.give_up_patterns.items():
            for pattern in patterns:
                if re.search(pattern, response_lower):
                    logger.debug(f"Matched pattern '{pattern}' for signal {signal_type.value}")
                    return signal_type
        
        return None
    
    def should_trigger_audit(self, outcome: AgentOutcome) -> bool:
        """
        Determine if this outcome should trigger a Completeness Audit.
        
        The Completeness Auditor is only triggered on "Give-Up Signals"
        to avoid expensive auditing of every interaction.
        
        Args:
            outcome: The agent outcome
            
        Returns:
            True if Completeness Auditor should be triggered
        """
        return outcome.outcome_type == OutcomeType.GIVE_UP
    
    def get_give_up_rate(self, agent_id: Optional[str] = None, recent_n: int = 100) -> float:
        """
        Calculate the give-up rate for an agent.
        
        This metric helps identify agents that are consistently lazy.
        
        Args:
            agent_id: Optional agent ID to filter by
            recent_n: Number of recent outcomes to analyze
            
        Returns:
            Give-up rate as a float between 0 and 1
        """
        outcomes = self.outcome_history[-recent_n:]
        
        if agent_id:
            outcomes = [o for o in outcomes if o.agent_id == agent_id]
        
        if not outcomes:
            return 0.0
        
        give_ups = sum(1 for o in outcomes if o.outcome_type == OutcomeType.GIVE_UP)
        
        return give_ups / len(outcomes)
    
    def get_outcome_history(
        self,
        agent_id: Optional[str] = None,
        outcome_type: Optional[OutcomeType] = None,
        limit: int = 100
    ) -> List[AgentOutcome]:
        """Get outcome history with optional filters."""
        outcomes = self.outcome_history[-limit:]
        
        if agent_id:
            outcomes = [o for o in outcomes if o.agent_id == agent_id]
        
        if outcome_type:
            outcomes = [o for o in outcomes if o.outcome_type == outcome_type]
        
        return outcomes
