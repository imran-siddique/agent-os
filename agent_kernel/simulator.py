"""
Path simulation system to test alternative solutions.
"""

import logging
import uuid
from typing import List, Dict, Any

from .models import FailureAnalysis, SimulationResult

logger = logging.getLogger(__name__)


class PathSimulator:
    """Simulates alternative paths to avoid failures."""
    
    def __init__(self):
        self.simulation_history: List[SimulationResult] = []
    
    def simulate(self, analysis: FailureAnalysis) -> SimulationResult:
        """
        Simulate an alternative path based on failure analysis.
        
        Args:
            analysis: The failure analysis containing suggested fixes
            
        Returns:
            SimulationResult with the alternative path and predicted outcome
        """
        logger.info(f"Simulating alternative path for agent {analysis.failure.agent_id}")
        
        # Generate simulation ID
        simulation_id = str(uuid.uuid4())
        
        # Build alternative path from suggested fixes
        alternative_path = self._build_alternative_path(analysis)
        
        # Predict outcome
        expected_outcome = self._predict_outcome(analysis, alternative_path)
        
        # Calculate risk score
        risk_score = self._calculate_risk(analysis, alternative_path)
        
        # Estimate success rate
        estimated_success_rate = self._estimate_success_rate(analysis, risk_score)
        
        # Determine if simulation is successful
        success = risk_score < 0.5 and estimated_success_rate > 0.7
        
        result = SimulationResult(
            simulation_id=simulation_id,
            success=success,
            alternative_path=alternative_path,
            expected_outcome=expected_outcome,
            risk_score=risk_score,
            estimated_success_rate=estimated_success_rate
        )
        
        self.simulation_history.append(result)
        
        if success:
            logger.info(f"Simulation successful. Success rate: {estimated_success_rate:.2f}, Risk: {risk_score:.2f}")
        else:
            logger.warning(f"Simulation failed. Success rate: {estimated_success_rate:.2f}, Risk: {risk_score:.2f}")
        
        return result
    
    def _build_alternative_path(self, analysis: FailureAnalysis) -> List[Dict[str, Any]]:
        """Build an alternative execution path from suggested fixes."""
        path = []
        failure = analysis.failure
        
        # Add validation step for control plane blocks
        if failure.failure_type.value == "blocked_by_control_plane":
            path.append({
                "step": 1,
                "action": "validate_permissions",
                "description": "Check permissions before attempting action",
                "params": {
                    "resource": failure.context.get("resource", "unknown"),
                    "action": failure.context.get("action", "unknown")
                }
            })
            
            path.append({
                "step": 2,
                "action": "request_authorization",
                "description": "Request proper authorization if needed",
                "params": {
                    "required_permission": "resource_access"
                }
            })
            
            path.append({
                "step": 3,
                "action": "safe_execute",
                "description": "Execute action with safety checks",
                "params": {
                    "original_action": failure.context.get("action", "unknown"),
                    "safety_mode": "enabled"
                }
            })
        
        # Add timeout handling for timeout failures
        elif failure.failure_type.value == "timeout":
            path.append({
                "step": 1,
                "action": "set_timeout",
                "description": "Configure appropriate timeout",
                "params": {"timeout_seconds": 30}
            })
            
            path.append({
                "step": 2,
                "action": "add_progress_monitoring",
                "description": "Add progress monitoring",
                "params": {"check_interval_seconds": 5}
            })
            
            path.append({
                "step": 3,
                "action": "execute_with_timeout",
                "description": "Execute with timeout handling",
                "params": {"allow_partial_results": True}
            })
        
        # Generic alternative path for other failures
        else:
            for i, fix in enumerate(analysis.suggested_fixes[:3], 1):
                path.append({
                    "step": i,
                    "action": "apply_fix",
                    "description": fix,
                    "params": {"fix": fix}
                })
        
        return path
    
    def _predict_outcome(self, analysis: FailureAnalysis, alternative_path: List[Dict[str, Any]]) -> str:
        """Predict the outcome of executing the alternative path."""
        failure = analysis.failure
        
        if failure.failure_type.value == "blocked_by_control_plane":
            return "Action will be executed with proper authorization and safety checks"
        elif failure.failure_type.value == "timeout":
            return "Operation will complete within timeout with progress monitoring"
        else:
            return f"Failure {failure.failure_type.value} will be prevented by applying suggested fixes"
    
    def _calculate_risk(self, analysis: FailureAnalysis, alternative_path: List[Dict[str, Any]]) -> float:
        """Calculate risk score for the alternative path."""
        risk = 0.3  # Base risk
        
        # Lower risk if confidence is high
        risk -= (analysis.confidence_score * 0.2)
        
        # Lower risk if we have multiple steps (more thorough)
        if len(alternative_path) >= 3:
            risk -= 0.1
        
        # Higher risk for unknown failure types
        if analysis.failure.failure_type.value == "unknown":
            risk += 0.2
        
        return max(0.0, min(1.0, risk))
    
    def _estimate_success_rate(self, analysis: FailureAnalysis, risk_score: float) -> float:
        """Estimate success rate of the alternative path."""
        # Base success rate from confidence
        success_rate = analysis.confidence_score
        
        # Adjust based on risk
        success_rate = success_rate * (1.0 - risk_score * 0.5)
        
        # Bonus for having similar failures (we've seen this before)
        if len(analysis.similar_failures) > 0:
            success_rate += 0.1
        
        return max(0.0, min(1.0, success_rate))
    
    def get_best_simulation(self, simulations: List[SimulationResult]) -> SimulationResult:
        """Get the best simulation from a list based on success rate and risk."""
        if not simulations:
            raise ValueError("No simulations provided")
        
        # Sort by estimated success rate (desc) and risk score (asc)
        sorted_sims = sorted(
            simulations,
            key=lambda s: (s.estimated_success_rate, -s.risk_score),
            reverse=True
        )
        
        return sorted_sims[0]
