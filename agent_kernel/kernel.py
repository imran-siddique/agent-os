"""
Self-Correcting Agent Kernel - Main orchestrator.
"""

import logging
from typing import Optional, Dict, Any, List

from .models import AgentFailure, FailureAnalysis, SimulationResult, CorrectionPatch, AgentState
from .detector import FailureDetector
from .analyzer import FailureAnalyzer
from .simulator import PathSimulator
from .patcher import AgentPatcher

logger = logging.getLogger(__name__)


class SelfCorrectingAgentKernel:
    """
    Main kernel that orchestrates the self-correcting agent system.
    
    When an agent fails in production (e.g., blocked by agent-control-plane),
    this kernel:
    1. Detects and classifies the failure
    2. Analyzes the failure to identify root causes
    3. Simulates alternative paths
    4. Automatically patches the agent
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the self-correcting agent kernel.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize components
        self.detector = FailureDetector()
        self.analyzer = FailureAnalyzer()
        self.simulator = PathSimulator()
        self.patcher = AgentPatcher()
        
        # Configure logging
        self._setup_logging()
        
        logger.info("Self-Correcting Agent Kernel initialized")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def handle_failure(
        self,
        agent_id: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
        auto_patch: bool = True
    ) -> Dict[str, Any]:
        """
        Handle an agent failure through the full self-correction pipeline.
        
        This is the main entry point when an agent fails in production.
        
        Args:
            agent_id: Identifier of the failed agent
            error_message: Error message from the failure
            context: Additional context about the failure
            stack_trace: Optional stack trace
            auto_patch: Whether to automatically apply the patch (default: True)
            
        Returns:
            Dictionary containing the results of the self-correction process
        """
        logger.info(f"=" * 80)
        logger.info(f"AGENT FAILURE DETECTED - Starting self-correction process")
        logger.info(f"Agent ID: {agent_id}")
        logger.info(f"Error: {error_message}")
        logger.info(f"=" * 80)
        
        # Step 1: Detect and classify failure
        logger.info("[1/4] Detecting and classifying failure...")
        failure = self.detector.detect_failure(
            agent_id=agent_id,
            error_message=error_message,
            context=context,
            stack_trace=stack_trace
        )
        
        # Step 2: Analyze failure
        logger.info("[2/4] Analyzing failure to identify root cause...")
        failure_history = self.detector.get_failure_history(agent_id=agent_id)
        similar_failures = self.analyzer.find_similar_failures(failure, failure_history)
        analysis = self.analyzer.analyze(failure, similar_failures)
        
        # Step 3: Simulate alternative path
        logger.info("[3/4] Simulating alternative path...")
        simulation = self.simulator.simulate(analysis)
        
        if not simulation.success:
            logger.warning("Simulation did not produce a viable alternative path")
            return {
                "success": False,
                "failure": failure,
                "analysis": analysis,
                "simulation": simulation,
                "patch": None,
                "message": "Could not find a viable alternative path"
            }
        
        # Step 4: Create and optionally apply patch
        logger.info("[4/4] Creating correction patch...")
        patch = self.patcher.create_patch(agent_id, analysis, simulation)
        
        patch_applied = False
        if auto_patch:
            logger.info("Auto-patching enabled, applying patch...")
            patch_applied = self.patcher.apply_patch(patch)
        else:
            logger.info("Auto-patching disabled, patch created but not applied")
        
        logger.info(f"=" * 80)
        logger.info(f"SELF-CORRECTION COMPLETE")
        logger.info(f"Patch ID: {patch.patch_id}")
        logger.info(f"Patch Applied: {patch_applied}")
        logger.info(f"Expected Success Rate: {simulation.estimated_success_rate:.2%}")
        logger.info(f"=" * 80)
        
        return {
            "success": True,
            "failure": failure,
            "analysis": analysis,
            "simulation": simulation,
            "patch": patch,
            "patch_applied": patch_applied,
            "message": "Agent successfully patched" if patch_applied else "Patch created, awaiting manual approval"
        }
    
    def get_agent_status(self, agent_id: str) -> AgentState:
        """
        Get the current status of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            AgentState object with current status
        """
        return self.patcher.get_agent_state(agent_id)
    
    def rollback_patch(self, patch_id: str) -> bool:
        """
        Rollback a previously applied patch.
        
        Args:
            patch_id: ID of the patch to rollback
            
        Returns:
            True if rollback was successful
        """
        return self.patcher.rollback_patch(patch_id)
    
    def get_failure_history(self, agent_id: Optional[str] = None, limit: int = 100) -> List[AgentFailure]:
        """
        Get failure history.
        
        Args:
            agent_id: Optional filter by agent ID
            limit: Maximum number of failures to return
            
        Returns:
            List of AgentFailure objects
        """
        return self.detector.get_failure_history(agent_id, limit)
    
    def get_patch_history(self, agent_id: Optional[str] = None) -> List[CorrectionPatch]:
        """
        Get patch history.
        
        Args:
            agent_id: Optional filter by agent ID
            
        Returns:
            List of CorrectionPatch objects
        """
        return self.patcher.get_patch_history(agent_id)
    
    def wake_up_and_fix(self, agent_id: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """
        Convenience method that wakes up the kernel, analyzes the failure,
        simulates a better path, and patches the agent.
        
        This is the main method referenced in the problem statement.
        
        Args:
            agent_id: ID of the failed agent
            error_message: Error message from the failure
            context: Additional context
        """
        logger.info("🚀 Kernel waking up to fix agent failure...")
        result = self.handle_failure(agent_id, error_message, context, auto_patch=True)
        
        if result["success"] and result["patch_applied"]:
            logger.info("✅ Agent fixed and patched successfully!")
        else:
            logger.warning("⚠️ Agent fix incomplete, manual intervention may be required")
        
        return result
