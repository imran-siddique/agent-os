"""
Failure analysis system that diagnoses root causes.
"""

import logging
from typing import List, Optional, Dict
from collections import Counter

from .models import AgentFailure, FailureAnalysis, FailureType

logger = logging.getLogger(__name__)


class FailureAnalyzer:
    """Analyzes failures to identify root causes and suggest fixes."""
    
    def __init__(self):
        self.analysis_history: List[FailureAnalysis] = []
        self.known_patterns: Dict[str, dict] = self._load_known_patterns()
    
    def _load_known_patterns(self) -> Dict[str, dict]:
        """Load known failure patterns and their solutions."""
        return {
            FailureType.BLOCKED_BY_CONTROL_PLANE: {
                "root_causes": [
                    "Missing permission validation",
                    "Attempting unauthorized resource access",
                    "Policy violation",
                    "Security constraint violation"
                ],
                "fixes": [
                    "Add permission checks before actions",
                    "Implement resource access validation",
                    "Use safe alternatives for restricted operations",
                    "Request proper authorization before attempting action"
                ]
            },
            FailureType.TIMEOUT: {
                "root_causes": [
                    "Operation taking too long",
                    "Infinite loop or deadlock",
                    "Network latency",
                    "Resource contention"
                ],
                "fixes": [
                    "Implement operation timeout handling",
                    "Add progress monitoring",
                    "Optimize algorithm efficiency",
                    "Add async/parallel processing"
                ]
            },
            FailureType.INVALID_ACTION: {
                "root_causes": [
                    "Invalid input parameters",
                    "Action not supported in current state",
                    "Precondition not met"
                ],
                "fixes": [
                    "Add input validation",
                    "Check state before action",
                    "Verify preconditions"
                ]
            },
            FailureType.RESOURCE_EXHAUSTED: {
                "root_causes": [
                    "Memory leak",
                    "Unbounded resource allocation",
                    "Missing cleanup"
                ],
                "fixes": [
                    "Implement resource cleanup",
                    "Add resource limits",
                    "Use resource pooling"
                ]
            },
            FailureType.LOGIC_ERROR: {
                "root_causes": [
                    "Incorrect algorithm",
                    "Edge case not handled",
                    "Type mismatch"
                ],
                "fixes": [
                    "Fix algorithm logic",
                    "Add edge case handling",
                    "Add type checking"
                ]
            }
        }
    
    def analyze(self, failure: AgentFailure, similar_failures: Optional[List[AgentFailure]] = None) -> FailureAnalysis:
        """
        Analyze a failure to identify root cause and suggest fixes.
        
        Args:
            failure: The failure to analyze
            similar_failures: Optional list of similar past failures
            
        Returns:
            FailureAnalysis with root cause and suggested fixes
        """
        logger.info(f"Analyzing failure for agent {failure.agent_id}")
        
        # Get known patterns for this failure type
        patterns = self.known_patterns.get(failure.failure_type, {})
        
        # Identify root cause
        root_cause = self._identify_root_cause(failure, patterns)
        
        # Identify contributing factors
        contributing_factors = self._identify_contributing_factors(failure, patterns)
        
        # Generate suggested fixes
        suggested_fixes = self._generate_fixes(failure, patterns)
        
        # Calculate confidence based on pattern matching and similar failures
        confidence_score = self._calculate_confidence(failure, similar_failures)
        
        # Find similar failures
        similar_failure_ids = []
        if similar_failures:
            similar_failure_ids = [f.agent_id + "_" + str(f.timestamp) for f in similar_failures[:5]]
        
        analysis = FailureAnalysis(
            failure=failure,
            root_cause=root_cause,
            contributing_factors=contributing_factors,
            suggested_fixes=suggested_fixes,
            confidence_score=confidence_score,
            similar_failures=similar_failure_ids
        )
        
        self.analysis_history.append(analysis)
        logger.info(f"Analysis complete. Root cause: {root_cause} (confidence: {confidence_score:.2f})")
        
        return analysis
    
    def _identify_root_cause(self, failure: AgentFailure, patterns: dict) -> str:
        """Identify the root cause of the failure."""
        root_causes = patterns.get("root_causes", ["Unknown root cause"])
        
        # For control plane blocks, check context for more specific cause
        if failure.failure_type == FailureType.BLOCKED_BY_CONTROL_PLANE:
            context = failure.context
            if "permission" in failure.error_message.lower():
                return "Missing or insufficient permissions for requested operation"
            elif "policy" in failure.error_message.lower():
                return "Action violates control plane policy"
            else:
                return root_causes[0]
        
        # Return the first root cause as default
        return root_causes[0]
    
    def _identify_contributing_factors(self, failure: AgentFailure, patterns: dict) -> List[str]:
        """Identify contributing factors to the failure."""
        factors = []
        
        # Check for common contributing factors
        if failure.severity.value in ["high", "critical"]:
            factors.append("High severity failure requiring immediate attention")
        
        if failure.stack_trace:
            factors.append("Stack trace available for detailed debugging")
        
        if failure.context:
            factors.append(f"Additional context available: {', '.join(failure.context.keys())}")
        
        return factors
    
    def _generate_fixes(self, failure: AgentFailure, patterns: dict) -> List[str]:
        """Generate suggested fixes for the failure."""
        fixes = patterns.get("fixes", ["Manual investigation required"])
        
        # Add specific fixes based on failure type
        if failure.failure_type == FailureType.BLOCKED_BY_CONTROL_PLANE:
            if "file" in failure.context:
                fixes.append(f"Validate access permissions for: {failure.context['file']}")
            if "action" in failure.context:
                fixes.append(f"Check if action '{failure.context['action']}' is allowed by policy")
        
        return fixes[:3]  # Return top 3 fixes
    
    def _calculate_confidence(self, failure: AgentFailure, similar_failures: Optional[List[AgentFailure]]) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if we have a known pattern
        if failure.failure_type in self.known_patterns:
            confidence += 0.2
        
        # Increase confidence if we have similar failures
        if similar_failures and len(similar_failures) > 0:
            confidence += min(0.2, len(similar_failures) * 0.05)
        
        # Increase confidence if we have detailed context
        if failure.context and len(failure.context) > 0:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def find_similar_failures(self, failure: AgentFailure, history: List[AgentFailure]) -> List[AgentFailure]:
        """Find similar failures in history."""
        similar = []
        
        for past_failure in history:
            if past_failure.failure_type == failure.failure_type:
                # Calculate similarity based on error message
                similarity = self._calculate_similarity(failure.error_message, past_failure.error_message)
                if similarity > 0.6:
                    similar.append(past_failure)
        
        return similar[:10]  # Return top 10 similar failures
    
    def _calculate_similarity(self, msg1: str, msg2: str) -> float:
        """Calculate similarity between two error messages."""
        # Simple word-based similarity
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
