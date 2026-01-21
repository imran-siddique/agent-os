"""
The Kernel: The Brain of the Cross-Model Verification System.
This is the deterministic logic that manages the Generator -> Verifier -> Graph loop.

Core Philosophy: "Trust, but Verify (with a different brain)."
"""
import logging
from typing import Optional, Dict, Any
import yaml
from pathlib import Path

from .types import (
    KernelState, GenerationResult, VerificationResult,
    VerificationOutcome, NodeStatus
)
from .graph_memory import GraphMemory
from ..agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class VerificationKernel:
    """
    The Arbiter - manages the adversarial verification loop.
    
    This kernel:
    1. Accepts a task from the user
    2. Calls the Generator to produce a solution
    3. Calls the Verifier to check the solution
    4. Updates the Graph of Truth
    5. Decides whether to accept, reject, or iterate
    6. Prevents infinite loops and caches successful results
    """
    
    def __init__(
        self,
        generator: BaseAgent,
        verifier: BaseAgent,
        config_path: Optional[str] = None
    ):
        """
        Initialize the kernel.
        
        Args:
            generator: The Generator agent (e.g., GPT-4o)
            verifier: The Verifier agent (e.g., Gemini 1.5 Pro)
            config_path: Path to configuration file
        """
        self.generator = generator
        self.verifier = verifier
        self.graph = GraphMemory()
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.max_loops = self.config.get("kernel", {}).get("max_loops", 5)
        self.confidence_threshold = self.config.get("kernel", {}).get("confidence_threshold", 0.85)
        
        logger.info("VerificationKernel initialized")
        logger.info(f"Max loops: {self.max_loops}, Confidence threshold: {self.confidence_threshold}")
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> KernelState:
        """
        Execute the verification loop for a given task.
        
        Args:
            task: The problem statement or task description
            context: Optional additional context for the task
            
        Returns:
            KernelState containing the final result and execution history
        """
        logger.info(f"Starting kernel execution for task: {task[:100]}...")
        
        # Initialize kernel state
        state = KernelState(
            task_description=task,
            current_loop=0,
            max_loops=self.max_loops,
            metadata=context or {}
        )
        
        # Feature 3: Add task to conversation trace
        self.graph.add_conversation_entry({
            "type": "task_start",
            "task": task,
            "max_loops": self.max_loops,
            "context": context or {}
        })
        
        # Check cache first
        problem_hash = GraphMemory.generate_state_hash(task, "", 0)
        cached_solution = self.graph.get_cached_solution(problem_hash)
        if cached_solution:
            logger.info("Found cached solution")
            state.final_result = cached_solution
            state.is_complete = True
            return state
        
        # Main verification loop
        while state.current_loop < self.max_loops and not state.is_complete:
            state.current_loop += 1
            logger.info(f"Starting loop {state.current_loop}/{self.max_loops}")
            
            # Step 1: Generate solution
            generation_result = self._generate_solution(task, state)
            state.current_solution = generation_result
            
            # Create a node in the graph
            node = self.graph.create_node(
                content=generation_result.solution,
                parent_id=None
            )
            
            # Step 2: Verify solution
            verification_result = self._verify_solution(generation_result, task)
            state.verification_history.append(verification_result)
            self.graph.add_verification_result(node.id, verification_result)
            
            # Feature 3: Add to conversation trace
            self.graph.add_conversation_entry({
                "type": "verification",
                "loop": state.current_loop,
                "outcome": verification_result.outcome.value,
                "confidence": verification_result.confidence,
                "critical_issues": verification_result.critical_issues,
                "hostile_tests_count": len(verification_result.hostile_tests) if verification_result.hostile_tests else 0
            })
            
            # Step 3: Check for infinite loops
            state_hash = GraphMemory.generate_state_hash(
                task, generation_result.solution, state.current_loop
            )
            if self.graph.has_visited_state(state_hash):
                logger.warning("Detected loop - same state visited before")
                state.is_complete = True
                state.final_result = self._handle_loop_detection(state)
                break
            
            self.graph.mark_state_visited(state_hash)
            
            # Step 4: Decide outcome
            if self._should_accept_solution(verification_result):
                logger.info("Solution accepted")
                state.is_complete = True
                state.final_result = generation_result.solution
                self.graph.cache_solution(problem_hash, generation_result.solution)
                self.graph.update_node_status(node.id, NodeStatus.VERIFIED)
                break
            elif state.current_loop >= self.max_loops:
                logger.warning("Max loops reached without verification")
                state.is_complete = True
                state.final_result = self._handle_max_loops_reached(state)
                self.graph.update_node_status(node.id, NodeStatus.FAILED)
            else:
                logger.info("Solution rejected, iterating...")
                
                # Feature 2: Record approach failure for lateral thinking
                self.graph.record_approach_failure(generation_result.solution, task)
                
                # Provide feedback to generator for next iteration
                state.metadata["last_verification"] = verification_result
                
                # Feature 2: Check if we need to branch to a different approach
                if self.graph.should_branch(generation_result.solution, task):
                    forbidden_approaches = self.graph.get_forbidden_approaches(task)
                    state.metadata["forbidden_approaches"] = forbidden_approaches
                    logger.info(f"Branching required - forbidden approaches: {forbidden_approaches}")
                
                self.graph.update_node_status(node.id, NodeStatus.FAILED)
        
        logger.info(f"Kernel execution complete. Success: {state.is_complete}")
        return state
    
    def _generate_solution(self, task: str, state: KernelState) -> GenerationResult:
        """
        Call the Generator to produce a solution.
        
        Args:
            task: The problem statement
            state: Current kernel state (for context)
            
        Returns:
            GenerationResult containing the solution
        """
        logger.debug("Calling generator...")
        
        # Build context from previous iterations
        context = {
            "iteration": state.current_loop,
            "previous_feedback": None
        }
        
        if state.verification_history:
            last_verification = state.verification_history[-1]
            context["previous_feedback"] = {
                "outcome": last_verification.outcome.value,
                "critical_issues": last_verification.critical_issues,
                "logic_flaws": last_verification.logic_flaws,
                "missing_edge_cases": last_verification.missing_edge_cases
            }
        
        # Feature 2: Add forbidden approaches to context
        if "forbidden_approaches" in state.metadata:
            forbidden = state.metadata["forbidden_approaches"]
            if forbidden:
                context["forbidden_approaches"] = forbidden
                context["branching_instruction"] = (
                    f"IMPORTANT: The following approaches have FAILED multiple times and are FORBIDDEN: {', '.join(forbidden)}. "
                    f"You MUST use a completely different approach. "
                    f"For example, if 'recursive' is forbidden, use an iterative solution instead."
                )
        
        result = self.generator.generate(task, context)
        
        # Feature 3: Add generation to conversation trace
        self.graph.add_conversation_entry({
            "type": "generation",
            "loop": state.current_loop,
            "approach": self.graph.detect_approach(result.solution),
            "solution_length": len(result.solution),
            "forbidden_approaches": state.metadata.get("forbidden_approaches", [])
        })
        
        return result
    
    def _verify_solution(self, solution: GenerationResult, task: str) -> VerificationResult:
        """
        Call the Verifier to check the solution.
        
        Args:
            solution: The generated solution
            task: The original problem statement
            
        Returns:
            VerificationResult containing the verification outcome
        """
        logger.debug("Calling verifier...")
        
        context = {
            "task": task,
            "solution": solution.solution,
            "explanation": solution.explanation,
            "test_cases": solution.test_cases
        }
        
        result = self.verifier.verify(context)
        return result
    
    def _should_accept_solution(self, verification: VerificationResult) -> bool:
        """
        Decide whether to accept a solution based on verification results.
        
        Args:
            verification: The verification result
            
        Returns:
            True if solution should be accepted, False otherwise
        """
        # Must pass verification
        if verification.outcome != VerificationOutcome.PASS:
            return False
        
        # Must meet confidence threshold
        if verification.confidence < self.confidence_threshold:
            logger.info(f"Confidence {verification.confidence} below threshold {self.confidence_threshold}")
            return False
        
        # Must not have critical issues
        if verification.has_critical_issues():
            logger.info("Critical issues found, rejecting")
            return False
        
        return True
    
    def _handle_loop_detection(self, state: KernelState) -> str:
        """Handle the case where an infinite loop is detected."""
        logger.warning("Loop detected - returning best attempt so far")
        if state.current_solution:
            return f"[LOOP DETECTED] Best attempt:\n{state.current_solution.solution}"
        return "[LOOP DETECTED] No valid solution found"
    
    def _handle_max_loops_reached(self, state: KernelState) -> str:
        """Handle the case where max loops are reached without success."""
        logger.warning("Max loops reached - returning last solution")
        if state.current_solution:
            return f"[MAX ITERATIONS] Last attempt:\n{state.current_solution.solution}"
        return "[MAX ITERATIONS] No solution found"
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            # Default to config/settings.yaml relative to this file
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        
        config_path = Path(config_path)
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML config file {config_path}: {e}. Using defaults.")
            return {}
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {e}. Using defaults.")
            return {}
        
        logger.info(f"Loaded configuration from {config_path}")
        return config or {}
    
    def get_graph_stats(self) -> Dict:
        """Get statistics about the graph state."""
        return self.graph.get_stats()
    
    def reset(self) -> None:
        """Reset the kernel state (for testing or new sessions)."""
        self.graph.clear()
        logger.info("Kernel reset complete")
    
    def export_conversation_trace(self, filepath: str) -> None:
        """
        Export the conversation trace to a JSON file.
        
        Args:
            filepath: Path to save the trace
        """
        self.graph.export_conversation_trace(filepath)
        logger.info(f"Exported conversation trace to {filepath}")
