"""
Conflict Resolution for Multi-Agent Systems.

Implements algorithms for resolving disagreements between agents:
- Voting mechanisms (majority, weighted, ranked-choice)
- Tie-breaking strategies
- Expert agent escalation
- Confidence-weighted consensus

Research Foundation:
- "Consensus Algorithms for Distributed Systems" (Raft, Paxos patterns)
- "Multi-Agent Coordination via Voting" (Social choice theory)
- "AutoGen" and "DEPS" conflict resolution patterns

Architectural Pattern:
- Decentralized decision-making with fallback to supervisor
- Weighted voting based on agent expertise/confidence
- Time-bounded resolution (no infinite debates)
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import logging
from statistics import mean, median
from collections import Counter

logger = logging.getLogger(__name__)


class VoteType(str, Enum):
    """Types of voting mechanisms."""
    MAJORITY = "majority"              # Simple majority (50% + 1)
    SUPERMAJORITY = "supermajority"    # 2/3 or 3/4 threshold
    UNANIMOUS = "unanimous"            # All agents must agree
    WEIGHTED = "weighted"              # Votes weighted by confidence/expertise
    RANKED_CHOICE = "ranked_choice"    # Agents rank preferences


class ConflictType(str, Enum):
    """Types of conflicts that can occur."""
    DECISION = "decision"          # Which action to take
    INTERPRETATION = "interpretation"  # How to interpret data
    PRIORITY = "priority"          # Which task is more important
    RESOURCE = "resource"          # Who gets limited resource


class AgentVote(BaseModel):
    """
    A single agent's vote on an issue.
    
    Supports both simple votes and weighted/ranked preferences.
    """
    agent_id: str
    option: str = Field(..., description="Option being voted for")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in vote (0.0-1.0)"
    )
    reasoning: Optional[str] = Field(None, description="Why agent voted this way")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # For ranked-choice voting
    ranked_preferences: Optional[List[str]] = Field(
        None,
        description="Ordered list of preferences (1st choice, 2nd choice, ...)"
    )


class ConflictResolution(BaseModel):
    """
    Result of conflict resolution process.
    
    Records the decision, how it was reached, and dissenting opinions.
    """
    conflict_id: str
    conflict_type: ConflictType
    resolution_method: VoteType
    winning_option: str
    votes: List[AgentVote]
    resolution_time: datetime = Field(default_factory=datetime.now)
    
    # Metadata
    total_votes: int
    votes_for_winner: int
    consensus_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How strong the consensus was (0.0-1.0)"
    )
    dissenting_agents: List[str] = Field(
        default_factory=list,
        description="Agents who voted against winning option"
    )
    tiebreaker_used: bool = False
    escalated_to_supervisor: bool = False


class ConflictResolver:
    """
    Resolves conflicts between agents using various voting mechanisms.
    
    Implements:
    1. Multiple voting algorithms
    2. Tie-breaking strategies
    3. Escalation to supervisor/expert agents
    4. Confidence-weighted consensus
    
    Research: Social choice theory applied to multi-agent AI systems.
    """
    
    def __init__(
        self,
        default_vote_type: VoteType = VoteType.MAJORITY,
        supervisor_agent_id: Optional[str] = None
    ):
        """
        Initialize conflict resolver.
        
        Args:
            default_vote_type: Default voting mechanism
            supervisor_agent_id: Optional supervisor for escalation
        """
        self.default_vote_type = default_vote_type
        self.supervisor_agent_id = supervisor_agent_id
        
        # Track resolution history
        self.resolution_history: List[ConflictResolution] = []
        
        logger.info(
            f"ConflictResolver initialized (default: {default_vote_type.value})"
        )
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        conflict_type: ConflictType,
        votes: List[AgentVote],
        vote_type: Optional[VoteType] = None,
        options: Optional[List[str]] = None
    ) -> ConflictResolution:
        """
        Resolve a conflict using specified voting mechanism.
        
        Args:
            conflict_id: Unique conflict identifier
            conflict_type: Type of conflict
            votes: List of agent votes
            vote_type: Voting mechanism (uses default if None)
            options: Valid options (for validation)
            
        Returns:
            ConflictResolution with winning option and metadata
            
        Raises:
            ValueError: If no votes or invalid vote_type
        """
        if not votes:
            raise ValueError("Cannot resolve conflict with zero votes")
        
        vote_type = vote_type or self.default_vote_type
        
        logger.info(
            f"Resolving conflict {conflict_id} ({conflict_type.value}) "
            f"with {len(votes)} votes using {vote_type.value}"
        )
        
        # Dispatch to appropriate voting algorithm
        if vote_type == VoteType.MAJORITY:
            resolution = self._resolve_majority(
                conflict_id, conflict_type, votes
            )
        elif vote_type == VoteType.SUPERMAJORITY:
            resolution = self._resolve_supermajority(
                conflict_id, conflict_type, votes, threshold=0.67
            )
        elif vote_type == VoteType.UNANIMOUS:
            resolution = self._resolve_unanimous(
                conflict_id, conflict_type, votes
            )
        elif vote_type == VoteType.WEIGHTED:
            resolution = self._resolve_weighted(
                conflict_id, conflict_type, votes
            )
        elif vote_type == VoteType.RANKED_CHOICE:
            resolution = self._resolve_ranked_choice(
                conflict_id, conflict_type, votes
            )
        else:
            raise ValueError(f"Unknown vote type: {vote_type}")
        
        # Record resolution
        self.resolution_history.append(resolution)
        
        logger.info(
            f"Conflict {conflict_id} resolved: {resolution.winning_option} "
            f"(consensus: {resolution.consensus_score:.2f})"
        )
        
        return resolution
    
    def _resolve_majority(
        self,
        conflict_id: str,
        conflict_type: ConflictType,
        votes: List[AgentVote]
    ) -> ConflictResolution:
        """
        Simple majority voting (50% + 1).
        
        Most common option wins. Ties broken by confidence.
        """
        # Count votes
        vote_counts = Counter(vote.option for vote in votes)
        
        # Find winner
        max_votes = max(vote_counts.values())
        candidates = [
            option for option, count in vote_counts.items()
            if count == max_votes
        ]
        
        # Handle tie
        tiebreaker_used = False
        if len(candidates) > 1:
            winning_option = self._tiebreaker(candidates, votes)
            tiebreaker_used = True
        else:
            winning_option = candidates[0]
        
        votes_for_winner = vote_counts[winning_option]
        
        # Calculate consensus score (% voting for winner)
        consensus_score = votes_for_winner / len(votes)
        
        # Identify dissenting agents
        dissenting = [
            vote.agent_id for vote in votes
            if vote.option != winning_option
        ]
        
        return ConflictResolution(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            resolution_method=VoteType.MAJORITY,
            winning_option=winning_option,
            votes=votes,
            total_votes=len(votes),
            votes_for_winner=votes_for_winner,
            consensus_score=consensus_score,
            dissenting_agents=dissenting,
            tiebreaker_used=tiebreaker_used
        )
    
    def _resolve_supermajority(
        self,
        conflict_id: str,
        conflict_type: ConflictType,
        votes: List[AgentVote],
        threshold: float = 0.67
    ) -> ConflictResolution:
        """
        Supermajority voting (2/3 or 3/4 threshold).
        
        Requires stronger consensus than simple majority.
        If threshold not met, escalate to supervisor.
        """
        vote_counts = Counter(vote.option for vote in votes)
        
        # Check if any option meets threshold
        required_votes = int(len(votes) * threshold)
        
        winner_option = None
        votes_for_winner = 0
        
        for option, count in vote_counts.items():
            if count >= required_votes:
                winner_option = option
                votes_for_winner = count
                break
        
        # If no supermajority, escalate or use tiebreaker
        escalated = False
        tiebreaker_used = False
        
        if winner_option is None:
            if self.supervisor_agent_id:
                # Escalate to supervisor
                logger.warning(
                    f"Supermajority not reached, escalating to {self.supervisor_agent_id}"
                )
                winner_option = self._escalate_to_supervisor(votes)
                escalated = True
            else:
                # Fallback to majority
                logger.warning("Supermajority not reached, using majority fallback")
                max_votes = max(vote_counts.values())
                candidates = [
                    opt for opt, cnt in vote_counts.items()
                    if cnt == max_votes
                ]
                winner_option = self._tiebreaker(candidates, votes)
                votes_for_winner = vote_counts[winner_option]
                tiebreaker_used = True
        
        consensus_score = votes_for_winner / len(votes)
        dissenting = [
            vote.agent_id for vote in votes
            if vote.option != winner_option
        ]
        
        return ConflictResolution(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            resolution_method=VoteType.SUPERMAJORITY,
            winning_option=winner_option,
            votes=votes,
            total_votes=len(votes),
            votes_for_winner=votes_for_winner,
            consensus_score=consensus_score,
            dissenting_agents=dissenting,
            tiebreaker_used=tiebreaker_used,
            escalated_to_supervisor=escalated
        )
    
    def _resolve_unanimous(
        self,
        conflict_id: str,
        conflict_type: ConflictType,
        votes: List[AgentVote]
    ) -> ConflictResolution:
        """
        Unanimous voting (all agents must agree).
        
        If not unanimous, escalate to supervisor.
        """
        vote_counts = Counter(vote.option for vote in votes)
        
        # Check if unanimous
        if len(vote_counts) == 1:
            # All voted for same option
            winning_option = list(vote_counts.keys())[0]
            consensus_score = 1.0
            escalated = False
        else:
            # Not unanimous, escalate
            logger.warning("Unanimous vote failed, escalating")
            winning_option = self._escalate_to_supervisor(votes)
            consensus_score = vote_counts[winning_option] / len(votes)
            escalated = True
        
        dissenting = [
            vote.agent_id for vote in votes
            if vote.option != winning_option
        ]
        
        return ConflictResolution(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            resolution_method=VoteType.UNANIMOUS,
            winning_option=winning_option,
            votes=votes,
            total_votes=len(votes),
            votes_for_winner=vote_counts[winning_option],
            consensus_score=consensus_score,
            dissenting_agents=dissenting,
            escalated_to_supervisor=escalated
        )
    
    def _resolve_weighted(
        self,
        conflict_id: str,
        conflict_type: ConflictType,
        votes: List[AgentVote]
    ) -> ConflictResolution:
        """
        Confidence-weighted voting.
        
        Each vote weighted by agent's confidence (0.0-1.0).
        Useful when some agents are more expert than others.
        
        Research: "Weighted voting in multi-agent systems" patterns.
        """
        # Calculate weighted votes for each option
        weighted_votes: Dict[str, float] = {}
        
        for vote in votes:
            option = vote.option
            weight = vote.confidence
            
            if option not in weighted_votes:
                weighted_votes[option] = 0.0
            
            weighted_votes[option] += weight
        
        # Find winner (highest weighted score)
        winning_option = max(weighted_votes, key=weighted_votes.get)
        winner_score = weighted_votes[winning_option]
        
        # Calculate consensus score (winner weight / total weight)
        total_weight = sum(weighted_votes.values())
        consensus_score = winner_score / total_weight if total_weight > 0 else 0.0
        
        # Count actual votes (not weighted)
        vote_counts = Counter(vote.option for vote in votes)
        votes_for_winner = vote_counts[winning_option]
        
        dissenting = [
            vote.agent_id for vote in votes
            if vote.option != winning_option
        ]
        
        logger.info(
            f"Weighted vote: {winning_option} with score {winner_score:.2f} "
            f"(consensus: {consensus_score:.2f})"
        )
        
        return ConflictResolution(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            resolution_method=VoteType.WEIGHTED,
            winning_option=winning_option,
            votes=votes,
            total_votes=len(votes),
            votes_for_winner=votes_for_winner,
            consensus_score=consensus_score,
            dissenting_agents=dissenting
        )
    
    def _resolve_ranked_choice(
        self,
        conflict_id: str,
        conflict_type: ConflictType,
        votes: List[AgentVote]
    ) -> ConflictResolution:
        """
        Ranked-choice voting (instant runoff).
        
        Agents rank options in preference order.
        Eliminates lowest-vote option each round until winner found.
        
        Research: "Instant-runoff voting" applied to AI agents.
        """
        # Validate all votes have ranked preferences
        for vote in votes:
            if not vote.ranked_preferences:
                raise ValueError(
                    f"Ranked-choice voting requires ranked_preferences in all votes"
                )
        
        # Start with all options from first-choice votes
        remaining_options = set()
        for vote in votes:
            if vote.ranked_preferences:
                remaining_options.update(vote.ranked_preferences)
        
        round_num = 0
        
        while len(remaining_options) > 1:
            round_num += 1
            
            # Count first-choice votes for remaining options
            first_choice_counts: Dict[str, int] = {}
            
            for vote in votes:
                if not vote.ranked_preferences:
                    continue
                
                # Find first remaining option in preferences
                for pref in vote.ranked_preferences:
                    if pref in remaining_options:
                        first_choice_counts[pref] = first_choice_counts.get(pref, 0) + 1
                        break
            
            # Check if any option has majority
            majority_threshold = len(votes) / 2
            for option, count in first_choice_counts.items():
                if count > majority_threshold:
                    # Winner found
                    winning_option = option
                    votes_for_winner = count
                    consensus_score = count / len(votes)
                    
                    dissenting = [
                        vote.agent_id for vote in votes
                        if not vote.ranked_preferences or
                        vote.ranked_preferences[0] != winning_option
                    ]
                    
                    logger.info(
                        f"Ranked-choice winner found in round {round_num}: "
                        f"{winning_option} ({votes_for_winner} votes)"
                    )
                    
                    return ConflictResolution(
                        conflict_id=conflict_id,
                        conflict_type=conflict_type,
                        resolution_method=VoteType.RANKED_CHOICE,
                        winning_option=winning_option,
                        votes=votes,
                        total_votes=len(votes),
                        votes_for_winner=votes_for_winner,
                        consensus_score=consensus_score,
                        dissenting_agents=dissenting
                    )
            
            # No majority, eliminate lowest
            min_count = min(first_choice_counts.values())
            eliminated = [
                opt for opt, cnt in first_choice_counts.items()
                if cnt == min_count
            ]
            
            # Remove eliminated option
            for opt in eliminated:
                remaining_options.discard(opt)
            
            logger.debug(f"Round {round_num}: eliminated {eliminated}")
        
        # Last remaining option wins
        winning_option = remaining_options.pop()
        
        # Count final votes
        vote_counts = Counter(vote.option for vote in votes)
        votes_for_winner = vote_counts.get(winning_option, 0)
        consensus_score = votes_for_winner / len(votes)
        
        dissenting = [
            vote.agent_id for vote in votes
            if vote.option != winning_option
        ]
        
        return ConflictResolution(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            resolution_method=VoteType.RANKED_CHOICE,
            winning_option=winning_option,
            votes=votes,
            total_votes=len(votes),
            votes_for_winner=votes_for_winner,
            consensus_score=consensus_score,
            dissenting_agents=dissenting
        )
    
    def _tiebreaker(
        self,
        tied_options: List[str],
        votes: List[AgentVote]
    ) -> str:
        """
        Break tie between options.
        
        Strategy: Use confidence scores to break tie.
        Option with highest average confidence wins.
        
        Args:
            tied_options: Options with same vote count
            votes: All votes
            
        Returns:
            Winning option
        """
        avg_confidence = {}
        
        for option in tied_options:
            confidences = [
                vote.confidence for vote in votes
                if vote.option == option
            ]
            avg_confidence[option] = mean(confidences) if confidences else 0.0
        
        winner = max(avg_confidence, key=avg_confidence.get)
        
        logger.info(
            f"Tiebreaker applied: {winner} "
            f"(avg confidence: {avg_confidence[winner]:.2f})"
        )
        
        return winner
    
    def _escalate_to_supervisor(self, votes: List[AgentVote]) -> str:
        """
        Escalate decision to supervisor agent.
        
        In production, would call actual supervisor agent.
        For now, returns most common option.
        
        Args:
            votes: Agent votes
            
        Returns:
            Supervisor's decision
        """
        if not self.supervisor_agent_id:
            # Fallback to majority
            vote_counts = Counter(vote.option for vote in votes)
            return vote_counts.most_common(1)[0][0]
        
        logger.warning(
            f"Escalating to supervisor {self.supervisor_agent_id}"
        )
        
        # TODO: Call actual supervisor agent
        # For now, return most common vote
        vote_counts = Counter(vote.option for vote in votes)
        return vote_counts.most_common(1)[0][0]
    
    def get_resolution_stats(self) -> Dict[str, Any]:
        """
        Get statistics on conflict resolutions.
        
        Returns:
            dict with resolution counts, avg consensus, etc.
        """
        if not self.resolution_history:
            return {
                "total_resolutions": 0,
                "avg_consensus_score": 0.0,
                "escalation_rate": 0.0,
                "tiebreaker_rate": 0.0
            }
        
        total = len(self.resolution_history)
        avg_consensus = mean(r.consensus_score for r in self.resolution_history)
        escalated = sum(1 for r in self.resolution_history if r.escalated_to_supervisor)
        tiebreakers = sum(1 for r in self.resolution_history if r.tiebreaker_used)
        
        return {
            "total_resolutions": total,
            "avg_consensus_score": avg_consensus,
            "escalation_rate": escalated / total,
            "tiebreaker_rate": tiebreakers / total,
            "by_method": Counter(r.resolution_method.value for r in self.resolution_history)
        }


# Example usage
async def example_conflict_resolution():
    """Demonstrate conflict resolution patterns."""
    resolver = ConflictResolver(
        default_vote_type=VoteType.MAJORITY,
        supervisor_agent_id="supervisor-001"
    )
    
    # Scenario 1: Simple majority vote
    votes = [
        AgentVote(agent_id="agent-001", option="approve", confidence=0.9),
        AgentVote(agent_id="agent-002", option="approve", confidence=0.8),
        AgentVote(agent_id="agent-003", option="reject", confidence=0.7),
    ]
    
    resolution = await resolver.resolve_conflict(
        "conflict-001",
        ConflictType.DECISION,
        votes,
        vote_type=VoteType.MAJORITY
    )
    
    print(f"Majority vote: {resolution.winning_option} "
          f"(consensus: {resolution.consensus_score:.2f})")
    
    # Scenario 2: Weighted voting (expertise matters)
    votes_weighted = [
        AgentVote(
            agent_id="expert-001",
            option="option_a",
            confidence=0.95,  # High expertise
            reasoning="Deep analysis shows option A is optimal"
        ),
        AgentVote(
            agent_id="novice-001",
            option="option_b",
            confidence=0.3,  # Low confidence
            reasoning="Intuition suggests option B"
        ),
        AgentVote(
            agent_id="novice-002",
            option="option_b",
            confidence=0.4
        ),
    ]
    
    resolution_weighted = await resolver.resolve_conflict(
        "conflict-002",
        ConflictType.INTERPRETATION,
        votes_weighted,
        vote_type=VoteType.WEIGHTED
    )
    
    print(f"Weighted vote: {resolution_weighted.winning_option} "
          f"(consensus: {resolution_weighted.consensus_score:.2f})")
    
    # Scenario 3: Ranked-choice voting
    votes_ranked = [
        AgentVote(
            agent_id="agent-001",
            option="option_a",
            ranked_preferences=["option_a", "option_b", "option_c"]
        ),
        AgentVote(
            agent_id="agent-002",
            option="option_b",
            ranked_preferences=["option_b", "option_a", "option_c"]
        ),
        AgentVote(
            agent_id="agent-003",
            option="option_c",
            ranked_preferences=["option_c", "option_a", "option_b"]
        ),
    ]
    
    resolution_ranked = await resolver.resolve_conflict(
        "conflict-003",
        ConflictType.PRIORITY,
        votes_ranked,
        vote_type=VoteType.RANKED_CHOICE
    )
    
    print(f"Ranked-choice: {resolution_ranked.winning_option}")
    
    # Get resolution stats
    stats = resolver.get_resolution_stats()
    print(f"Resolution stats: {stats}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_conflict_resolution())
