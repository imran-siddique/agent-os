"""
Agent patcher that applies corrections to agents.
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import FailureAnalysis, SimulationResult, CorrectionPatch, AgentState

logger = logging.getLogger(__name__)


class AgentPatcher:
    """Patches agents to prevent future failures."""
    
    def __init__(self):
        self.patches: Dict[str, CorrectionPatch] = {}
        self.agent_states: Dict[str, AgentState] = {}
    
    def create_patch(
        self,
        agent_id: str,
        analysis: FailureAnalysis,
        simulation: SimulationResult
    ) -> CorrectionPatch:
        """
        Create a correction patch for an agent.
        
        Args:
            agent_id: ID of the agent to patch
            analysis: Failure analysis
            simulation: Successful simulation result
            
        Returns:
            CorrectionPatch object
        """
        logger.info(f"Creating patch for agent {agent_id}")
        
        # Generate patch ID
        patch_id = f"patch-{uuid.uuid4().hex[:8]}"
        
        # Determine patch type based on failure
        patch_type = self._determine_patch_type(analysis)
        
        # Generate patch content
        patch_content = self._generate_patch_content(analysis, simulation)
        
        patch = CorrectionPatch(
            patch_id=patch_id,
            agent_id=agent_id,
            failure_analysis=analysis,
            simulation_result=simulation,
            patch_type=patch_type,
            patch_content=patch_content,
            applied=False,
            rollback_available=True
        )
        
        self.patches[patch_id] = patch
        logger.info(f"Created {patch_type} patch {patch_id}")
        
        return patch
    
    def apply_patch(self, patch: CorrectionPatch) -> bool:
        """
        Apply a correction patch to an agent.
        
        Args:
            patch: The patch to apply
            
        Returns:
            True if patch was applied successfully
        """
        logger.info(f"Applying patch {patch.patch_id} to agent {patch.agent_id}")
        
        try:
            # In a real implementation, this would:
            # 1. Connect to the agent
            # 2. Apply the patch (code changes, config updates, etc.)
            # 3. Verify the patch
            # 4. Restart the agent if needed
            
            # For now, we simulate successful patching
            patch.applied = True
            patch.applied_at = datetime.utcnow()
            
            # Update agent state
            self._update_agent_state(patch.agent_id, patch)
            
            logger.info(f"Successfully applied patch {patch.patch_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply patch {patch.patch_id}: {e}")
            return False
    
    def rollback_patch(self, patch_id: str) -> bool:
        """
        Rollback a previously applied patch.
        
        Args:
            patch_id: ID of the patch to rollback
            
        Returns:
            True if rollback was successful
        """
        if patch_id not in self.patches:
            logger.error(f"Patch {patch_id} not found")
            return False
        
        patch = self.patches[patch_id]
        
        if not patch.applied:
            logger.warning(f"Patch {patch_id} is not applied, cannot rollback")
            return False
        
        if not patch.rollback_available:
            logger.error(f"Patch {patch_id} does not support rollback")
            return False
        
        logger.info(f"Rolling back patch {patch_id}")
        
        try:
            # In a real implementation, this would restore the previous state
            patch.applied = False
            patch.applied_at = None
            
            # Update agent state
            if patch.agent_id in self.agent_states:
                state = self.agent_states[patch.agent_id]
                if patch_id in state.patches_applied:
                    state.patches_applied.remove(patch_id)
            
            logger.info(f"Successfully rolled back patch {patch_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback patch {patch_id}: {e}")
            return False
    
    def get_agent_state(self, agent_id: str) -> AgentState:
        """Get the current state of an agent."""
        if agent_id not in self.agent_states:
            self.agent_states[agent_id] = AgentState(
                agent_id=agent_id,
                status="unknown"
            )
        return self.agent_states[agent_id]
    
    def _determine_patch_type(self, analysis: FailureAnalysis) -> str:
        """Determine the type of patch needed."""
        failure_type = analysis.failure.failure_type.value
        
        if failure_type == "blocked_by_control_plane":
            return "code"  # Code changes to add permission checks
        elif failure_type == "timeout":
            return "config"  # Configuration changes for timeouts
        elif failure_type == "invalid_action":
            return "rule"  # Rule changes to validate actions
        else:
            return "code"  # Default to code patches
    
    def _generate_patch_content(
        self,
        analysis: FailureAnalysis,
        simulation: SimulationResult
    ) -> Dict[str, Any]:
        """Generate the actual patch content."""
        failure_type = analysis.failure.failure_type.value
        
        if failure_type == "blocked_by_control_plane":
            return {
                "type": "permission_check",
                "changes": [
                    {
                        "location": "before_action",
                        "code": "if not validate_permissions(action, resource): raise PermissionError()",
                        "description": "Add permission validation"
                    },
                    {
                        "location": "action_handler",
                        "code": "with safe_context(): execute_action()",
                        "description": "Wrap action in safe context"
                    }
                ],
                "simulation_steps": simulation.alternative_path
            }
        elif failure_type == "timeout":
            return {
                "type": "timeout_handling",
                "config": {
                    "timeout_seconds": 30,
                    "enable_progress_monitoring": True,
                    "allow_partial_results": True
                },
                "simulation_steps": simulation.alternative_path
            }
        else:
            return {
                "type": "generic_fix",
                "suggested_fixes": analysis.suggested_fixes,
                "simulation_steps": simulation.alternative_path
            }
    
    def _update_agent_state(self, agent_id: str, patch: CorrectionPatch):
        """Update the state of an agent after patching."""
        if agent_id not in self.agent_states:
            self.agent_states[agent_id] = AgentState(
                agent_id=agent_id,
                status="running"
            )
        
        state = self.agent_states[agent_id]
        state.status = "patched"
        state.last_failure = patch.failure_analysis.failure
        
        if patch.patch_id not in state.patches_applied:
            state.patches_applied.append(patch.patch_id)
    
    def get_patch_history(self, agent_id: Optional[str] = None) -> List[CorrectionPatch]:
        """Get patch history, optionally filtered by agent_id."""
        patches = list(self.patches.values())
        
        if agent_id:
            patches = [p for p in patches if p.agent_id == agent_id]
        
        return sorted(patches, key=lambda p: p.applied_at or datetime.min, reverse=True)
