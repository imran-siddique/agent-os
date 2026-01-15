"""
Self-Correcting Agent Kernel - Main orchestrator.

Implements the Dual-Loop Architecture:
- Loop 1 (Runtime): Constraint Engine (Safety)
- Loop 2 (Offline): Alignment Engine (Quality & Efficiency)
"""

import logging
from typing import Optional, Dict, Any, List

from .models import (
    AgentFailure, FailureAnalysis, SimulationResult, CorrectionPatch, AgentState,
    AgentOutcome, CompletenessAudit, ClassifiedPatch
)
from .detector import FailureDetector
from .analyzer import FailureAnalyzer
from .simulator import PathSimulator
from .patcher import AgentPatcher
from .outcome_analyzer import OutcomeAnalyzer
from .completeness_auditor import CompletenessAuditor
from .semantic_purge import SemanticPurge

logger = logging.getLogger(__name__)


class SelfCorrectingAgentKernel:
    """
    Main kernel implementing the Dual-Loop Architecture.
    
    LOOP 1 (Runtime): The Constraint Engine filters for Safety
    LOOP 2 (Offline): The Alignment Engine filters for Quality & Efficiency:
        - Completeness Auditor: Detects "laziness" (give-up signals)
        - Semantic Purge: Manages patch lifecycle (scale by subtraction)
    
    When an agent fails OR gives up:
    1. Detects and classifies the outcome
    2. Analyzes for safety (Loop 1) and competence (Loop 2)
    3. Simulates alternative paths
    4. Patches the agent with classified, lifecycle-managed fixes
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the self-correcting agent kernel with Dual-Loop Architecture.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # LOOP 1: Runtime Safety Components
        self.detector = FailureDetector()
        self.analyzer = FailureAnalyzer()
        self.simulator = PathSimulator()
        self.patcher = AgentPatcher()
        
        # LOOP 2: Offline Alignment Components
        self.outcome_analyzer = OutcomeAnalyzer()
        self.completeness_auditor = CompletenessAuditor(
            teacher_model=self.config.get("teacher_model", "o1-preview")
        )
        self.semantic_purge = SemanticPurge()
        
        # Model version tracking for semantic purge
        self.current_model_version = self.config.get("model_version", "gpt-4o")
        
        # Configure logging
        self._setup_logging()
        
        logger.info("=" * 80)
        logger.info("Self-Correcting Agent Kernel initialized (Dual-Loop Architecture)")
        logger.info(f"  Loop 1 (Runtime): Constraint Engine (Safety)")
        logger.info(f"  Loop 2 (Offline): Alignment Engine (Quality & Efficiency)")
        logger.info(f"    - Completeness Auditor: {self.completeness_auditor.teacher_model}")
        logger.info(f"    - Semantic Purge: Active")
        logger.info(f"  Model Version: {self.current_model_version}")
        logger.info("=" * 80)
    
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
        auto_patch: bool = True,
        user_prompt: Optional[str] = None,
        chain_of_thought: Optional[List[str]] = None,
        failed_action: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an agent failure through the full self-correction pipeline.
        
        Enhanced to support full trace capture and cognitive diagnosis.
        
        This is the main entry point when an agent fails in production.
        
        Args:
            agent_id: Identifier of the failed agent
            error_message: Error message from the failure
            context: Additional context about the failure
            stack_trace: Optional stack trace
            auto_patch: Whether to automatically apply the patch (default: True)
            user_prompt: Original user prompt (for full trace)
            chain_of_thought: Agent's reasoning steps (for cognitive analysis)
            failed_action: The specific action that failed
            
        Returns:
            Dictionary containing the results of the self-correction process
        """
        logger.info(f"=" * 80)
        logger.info(f"AGENT FAILURE DETECTED - Starting enhanced self-correction process")
        logger.info(f"Agent ID: {agent_id}")
        logger.info(f"Error: {error_message}")
        logger.info(f"=" * 80)
        
        # Step 1: Detect and classify failure with full trace
        logger.info("[1/5] Detecting and classifying failure (capturing full trace)...")
        failure = self.detector.detect_failure(
            agent_id=agent_id,
            error_message=error_message,
            context=context,
            stack_trace=stack_trace,
            user_prompt=user_prompt,
            chain_of_thought=chain_of_thought,
            failed_action=failed_action
        )
        
        # Step 2: Deep cognitive analysis
        logger.info("[2/5] Analyzing failure (identifying cognitive glitches)...")
        failure_history = self.detector.get_failure_history(agent_id=agent_id)
        similar_failures = self.analyzer.find_similar_failures(failure, failure_history)
        analysis = self.analyzer.analyze(failure, similar_failures)
        
        # Generate cognitive diagnosis if trace available
        diagnosis = None
        if failure.failure_trace:
            logger.info("      → Performing deep cognitive analysis...")
            diagnosis = self.analyzer.diagnose_cognitive_glitch(failure)
            logger.info(f"      → Cognitive glitch: {diagnosis.cognitive_glitch.value}")
        
        # Step 3: Simulate alternative path
        logger.info("[3/5] Simulating alternative path...")
        simulation = self.simulator.simulate(analysis)
        
        # Step 4: Counterfactual simulation with Shadow Agent
        shadow_result = None
        if diagnosis and failure.failure_trace:
            logger.info("[4/5] Running counterfactual simulation (Shadow Agent)...")
            shadow_result = self.simulator.simulate_counterfactual(diagnosis, failure)
            logger.info(f"      → Shadow agent verified: {shadow_result.verified}")
        else:
            logger.info("[4/5] Skipping Shadow Agent (no trace available)")
        
        if not simulation.success and (not shadow_result or not shadow_result.verified):
            logger.warning("Simulation did not produce a viable alternative path")
            return {
                "success": False,
                "failure": failure,
                "analysis": analysis,
                "diagnosis": diagnosis,
                "simulation": simulation,
                "shadow_result": shadow_result,
                "patch": None,
                "message": "Could not find a viable alternative path"
            }
        
        # Step 5: Create and optionally apply patch
        logger.info("[5/5] Creating correction patch (The Optimizer)...")
        patch = self.patcher.create_patch(
            agent_id, analysis, simulation, diagnosis, shadow_result
        )
        
        # Classify patch for lifecycle management (Semantic Purge integration)
        classified_patch = self.semantic_purge.register_patch(
            patch=patch,
            current_model_version=self.current_model_version
        )
        logger.info(f"      → Patch classified as: {classified_patch.decay_type.value}")
        
        patch_applied = False
        if auto_patch:
            logger.info("Auto-patching enabled, applying patch...")
            patch_applied = self.patcher.apply_patch(patch)
        else:
            logger.info("Auto-patching disabled, patch created but not applied")
        
        logger.info(f"=" * 80)
        logger.info(f"SELF-CORRECTION COMPLETE")
        logger.info(f"Patch ID: {patch.patch_id}")
        logger.info(f"Patch Type: {patch.patch_type}")
        logger.info(f"Decay Type: {classified_patch.decay_type.value}")
        logger.info(f"Purge on Upgrade: {classified_patch.should_purge_on_upgrade}")
        if diagnosis:
            logger.info(f"Cognitive Glitch: {diagnosis.cognitive_glitch.value}")
        logger.info(f"Patch Applied: {patch_applied}")
        logger.info(f"Expected Success Rate: {simulation.estimated_success_rate:.2%}")
        logger.info(f"=" * 80)
        
        return {
            "success": True,
            "failure": failure,
            "analysis": analysis,
            "diagnosis": diagnosis,
            "simulation": simulation,
            "shadow_result": shadow_result,
            "patch": patch,
            "classified_patch": classified_patch,
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
    
    # ============================================================================
    # DUAL-LOOP ARCHITECTURE: Loop 2 (Alignment Engine) Methods
    # ============================================================================
    
    def handle_outcome(
        self,
        agent_id: str,
        user_prompt: str,
        agent_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an agent outcome through the Alignment Engine (Loop 2).
        
        This is the entry point for the Completeness Auditor. Instead of waiting
        for hard failures, we proactively detect when agents "give up" with
        negative results.
        
        Args:
            agent_id: ID of the agent
            user_prompt: Original user request
            agent_response: Agent's response
            context: Additional context
            
        Returns:
            Dictionary with outcome analysis and any audit results
        """
        logger.info(f"🔄 Loop 2 (Alignment Engine): Analyzing outcome for {agent_id}")
        
        # Step 1: Analyze the outcome
        outcome = self.outcome_analyzer.analyze_outcome(
            agent_id=agent_id,
            user_prompt=user_prompt,
            agent_response=agent_response,
            context=context
        )
        
        result = {
            "outcome": outcome,
            "audit": None,
            "patch": None,
            "classified_patch": None
        }
        
        # Step 2: Check if this triggers Completeness Audit (Give-Up Signal)
        if self.outcome_analyzer.should_trigger_audit(outcome):
            logger.info(f"🔍 Give-Up Signal detected! Triggering Completeness Auditor...")
            
            # Step 3: Run Completeness Audit (Differential Auditing)
            audit = self.completeness_auditor.audit_give_up(outcome)
            result["audit"] = audit
            
            # Step 4: If teacher found data (laziness detected), create competence patch
            if audit.teacher_found_data:
                logger.info(f"⚠️  LAZINESS DETECTED: Creating competence patch...")
                
                # Create a patch from the competence lesson
                patch = self._create_competence_patch(agent_id, audit)
                result["patch"] = patch
                
                # Step 5: Classify patch for lifecycle management (Semantic Purge)
                classified_patch = self.semantic_purge.register_patch(
                    patch=patch,
                    current_model_version=self.current_model_version
                )
                result["classified_patch"] = classified_patch
                
                # Register with auditor
                self.semantic_purge.register_completeness_audit(
                    audit=audit,
                    current_model_version=self.current_model_version
                )
                
                # Apply patch
                if self.config.get("auto_patch", True):
                    self.patcher.apply_patch(patch)
                    logger.info(f"✓ Competence patch applied")
        else:
            logger.info(f"✓ No give-up signal detected - agent performing well")
        
        return result
    
    def _create_competence_patch(
        self,
        agent_id: str,
        audit: CompletenessAudit
    ) -> CorrectionPatch:
        """
        Create a patch from a completeness audit.
        
        Competence patches teach the agent to avoid giving up too early.
        """
        import uuid
        from datetime import datetime
        from .models import FailureAnalysis, SimulationResult, AgentFailure, FailureType, FailureSeverity
        
        # Create a synthetic failure for the audit
        failure = AgentFailure(
            agent_id=agent_id,
            failure_type=FailureType.LOGIC_ERROR,
            severity=FailureSeverity.MEDIUM,
            error_message=f"Agent gave up: {audit.agent_outcome.agent_response}",
            context=audit.agent_outcome.context
        )
        
        # Create analysis
        analysis = FailureAnalysis(
            failure=failure,
            root_cause="Agent gave up too early without exhaustive search",
            contributing_factors=[audit.gap_analysis],
            suggested_fixes=[audit.competence_patch],
            confidence_score=audit.confidence,
            similar_failures=[]
        )
        
        # Create simulation
        simulation = SimulationResult(
            simulation_id=f"sim-{uuid.uuid4().hex[:8]}",
            success=True,
            alternative_path=[
                {
                    "step": 1,
                    "action": "exhaustive_search",
                    "description": "Check all data sources before reporting 'not found'"
                },
                {
                    "step": 2,
                    "action": "apply_competence_lesson",
                    "description": audit.competence_patch
                }
            ],
            expected_outcome="Agent will search exhaustively before giving up",
            risk_score=0.1,
            estimated_success_rate=0.9
        )
        
        # Create patch
        patch_id = f"competence-patch-{uuid.uuid4().hex[:8]}"
        
        patch = CorrectionPatch(
            patch_id=patch_id,
            agent_id=agent_id,
            failure_analysis=analysis,
            simulation_result=simulation,
            patch_type="system_prompt",
            patch_content={
                "type": "competence_rule",
                "rule": audit.competence_patch,
                "from_audit": audit.audit_id,
                "teacher_model": audit.teacher_model
            },
            applied=False
        )
        
        return patch
    
    def upgrade_model(self, new_model_version: str) -> Dict[str, Any]:
        """
        Upgrade the model version and trigger Semantic Purge.
        
        This is the "Purge Event" that removes Type A (Syntax) patches
        that are likely fixed in the new model version.
        
        Args:
            new_model_version: New model version (e.g., "gpt-5")
            
        Returns:
            Dictionary with purge statistics
        """
        logger.info(f"=" * 80)
        logger.info(f"MODEL UPGRADE: {self.current_model_version} → {new_model_version}")
        logger.info(f"=" * 80)
        
        old_version = self.current_model_version
        
        # Trigger semantic purge
        purge_result = self.semantic_purge.purge_on_upgrade(
            old_model_version=old_version,
            new_model_version=new_model_version
        )
        
        # Update model version
        self.current_model_version = new_model_version
        
        # Update all agent states
        for agent_state in self.patcher.agent_states.values():
            agent_state.model_version = new_model_version
        
        logger.info(f"=" * 80)
        logger.info(f"MODEL UPGRADE COMPLETE")
        logger.info(f"  Purged: {purge_result['stats']['purged_count']} Type A patches")
        logger.info(f"  Retained: {purge_result['stats']['retained_count']} Type B patches")
        logger.info(f"  Tokens Reclaimed: {purge_result['stats']['tokens_reclaimed']}")
        logger.info(f"=" * 80)
        
        return purge_result
    
    def get_alignment_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Alignment Engine (Loop 2).
        
        Returns:
            Dictionary with stats about completeness audits and semantic purge
        """
        return {
            "completeness_auditor": self.completeness_auditor.get_audit_stats(),
            "semantic_purge": self.semantic_purge.get_purge_stats(),
            "outcome_analyzer": {
                "total_outcomes": len(self.outcome_analyzer.outcome_history),
                "give_up_rate": self.outcome_analyzer.get_give_up_rate()
            }
        }
    
    def get_classified_patches(self) -> Dict[str, List[ClassifiedPatch]]:
        """
        Get patches classified by type.
        
        Returns:
            Dictionary with purgeable and permanent patches
        """
        return {
            "purgeable": self.semantic_purge.get_purgeable_patches(),
            "permanent": self.semantic_purge.get_permanent_patches()
        }
