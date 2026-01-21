"""
Graph Memory: The "Graph of Truth" implementation.
This module manages a persistent state machine that prevents deadlocks and caches proven truths.
"""
from typing import Dict, List, Optional, Set, Any
import logging
from datetime import datetime
import hashlib

from .types import Node, NodeStatus, VerificationResult, VerificationOutcome

logger = logging.getLogger(__name__)


class GraphMemory:
    """
    The Graph of Truth - a multi-dimensional state machine that:
    1. Prevents infinite loops by detecting repeated states
    2. Caches proven truths to speed up future reasoning
    3. Maintains relationships between verified solutions
    """
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.visited_states: Set[str] = set()
        self.verified_cache: Dict[str, str] = {}  # Problem hash -> Solution
        
        # Feature 2: Lateral Thinking - Track approach failures
        self.approach_failures: Dict[str, int] = {}  # Approach hash -> failure count
        self.forbidden_approaches: Set[str] = set()  # Approaches to avoid
        self.conversation_trace: List[Dict[str, Any]] = []  # Feature 3: Full trace
        
    def create_node(self, content: str, parent_id: Optional[str] = None) -> Node:
        """Create a new node in the graph."""
        node_id = self._generate_node_id(content)
        
        node = Node(
            id=node_id,
            content=content,
            status=NodeStatus.PENDING,
            parent_id=parent_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.nodes[node_id] = node
        
        # Update parent's children
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].children_ids.append(node_id)
            
        logger.info(f"Created node {node_id} with parent {parent_id}")
        return node
    
    def update_node_status(self, node_id: str, status: NodeStatus) -> None:
        """Update the status of a node."""
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self.nodes[node_id].updated_at = datetime.now()
            logger.info(f"Updated node {node_id} status to {status}")
        else:
            logger.warning(f"Attempted to update non-existent node {node_id}")
    
    def add_verification_result(self, node_id: str, result: VerificationResult) -> None:
        """Add a verification result to a node."""
        if node_id in self.nodes:
            self.nodes[node_id].verification_results.append(result)
            self.nodes[node_id].updated_at = datetime.now()
            
            # Update status based on verification result
            if result.outcome == VerificationOutcome.PASS:
                self.update_node_status(node_id, NodeStatus.VERIFIED)
            elif result.outcome == VerificationOutcome.FAIL:
                self.update_node_status(node_id, NodeStatus.FAILED)
                
            logger.info(f"Added verification result to node {node_id}: {result.outcome}")
        else:
            logger.warning(f"Attempted to add verification to non-existent node {node_id}")
    
    def has_visited_state(self, state_hash: str) -> bool:
        """Check if we've seen this state before (loop detection)."""
        return state_hash in self.visited_states
    
    def mark_state_visited(self, state_hash: str) -> None:
        """Mark a state as visited to prevent infinite loops."""
        self.visited_states.add(state_hash)
        logger.debug(f"Marked state as visited: {state_hash}")
    
    def get_cached_solution(self, problem_hash: str) -> Optional[str]:
        """Retrieve a cached solution for a problem."""
        return self.verified_cache.get(problem_hash)
    
    def cache_solution(self, problem_hash: str, solution: str) -> None:
        """Cache a verified solution for future use."""
        self.verified_cache[problem_hash] = solution
        logger.info(f"Cached solution for problem {problem_hash}")
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by ID."""
        return self.nodes.get(node_id)
    
    def get_verified_nodes(self) -> List[Node]:
        """Get all verified nodes."""
        return [node for node in self.nodes.values() if node.is_verified()]
    
    def get_failed_nodes(self) -> List[Node]:
        """Get all failed nodes."""
        return [node for node in self.nodes.values() if node.status == NodeStatus.FAILED]
    
    def clear(self) -> None:
        """Clear all graph state (for testing or reset)."""
        self.nodes.clear()
        self.visited_states.clear()
        self.verified_cache.clear()
        self.approach_failures.clear()
        self.forbidden_approaches.clear()
        self.conversation_trace.clear()
        logger.info("Cleared graph memory")
    
    @staticmethod
    def _generate_node_id(content: str) -> str:
        """Generate a unique ID for a node based on its content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @staticmethod
    def generate_state_hash(task: str, solution: str, iteration: int) -> str:
        """Generate a hash representing the current state.

        Note: The iteration parameter is accepted for backward compatibility
        but is not included in the hash to ensure identical task/solution
        pairs are treated as the same state for loop detection.
        """
        state_str = f"{task}|{solution}"
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def get_stats(self) -> Dict:
        """Get statistics about the graph state."""
        return {
            "total_nodes": len(self.nodes),
            "verified_nodes": len(self.get_verified_nodes()),
            "failed_nodes": len(self.get_failed_nodes()),
            "visited_states": len(self.visited_states),
            "cached_solutions": len(self.verified_cache),
            "approach_failures": len(self.approach_failures),
            "forbidden_approaches": len(self.forbidden_approaches),
            "conversation_entries": len(self.conversation_trace)
        }
    
    # Feature 2: Lateral Thinking Methods
    
    @staticmethod
    def detect_approach(solution: str) -> str:
        """
        Detect the approach used in a solution.
        
        This uses simple heuristics to identify patterns like:
        - Recursion vs Iteration
        - Dynamic Programming
        - Greedy algorithms
        - Divide and Conquer
        
        Args:
            solution: The solution code
            
        Returns:
            A string identifying the approach
        """
        solution_lower = solution.lower()
        
        # Check for recursion
        import re
        function_match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', solution)
        if function_match:
            function_name = function_match.group(1)
            # Check if function calls itself
            if function_name in solution[function_match.end():]:
                return "recursive"
        
        # Check for iteration
        if any(keyword in solution_lower for keyword in ['for ', 'while ']):
            # Check for dynamic programming patterns
            if any(pattern in solution_lower for pattern in ['dp[', 'memo', 'cache', '@lru_cache']):
                return "dynamic_programming"
            return "iterative"
        
        # Check for greedy patterns
        if any(pattern in solution_lower for pattern in ['max(', 'min(', 'sorted(', 'sort(']):
            return "greedy"
        
        # Default
        return "unknown"
    
    def record_approach_failure(self, solution: str, task: str) -> None:
        """
        Record that an approach failed for a task.
        
        Args:
            solution: The failed solution
            task: The task being attempted
        """
        approach = self.detect_approach(solution)
        approach_key = f"{task[:50]}|{approach}"  # Use first 50 chars of task + approach
        
        self.approach_failures[approach_key] = self.approach_failures.get(approach_key, 0) + 1
        
        # If approach has failed twice, mark it as forbidden
        if self.approach_failures[approach_key] >= 2:
            self.forbidden_approaches.add(approach_key)
            logger.info(f"Approach '{approach}' marked as forbidden after {self.approach_failures[approach_key]} failures")
    
    def get_forbidden_approaches(self, task: str) -> List[str]:
        """
        Get the list of approaches that should be forbidden for a task.
        
        Args:
            task: The task being attempted
            
        Returns:
            List of approach names that are forbidden
        """
        task_prefix = task[:50]
        forbidden = []
        
        for approach_key in self.forbidden_approaches:
            if approach_key.startswith(task_prefix):
                # Extract approach name
                approach = approach_key.split('|')[1]
                forbidden.append(approach)
        
        return forbidden
    
    def should_branch(self, solution: str, task: str) -> bool:
        """
        Determine if we should branch to a different approach.
        
        Args:
            solution: The current solution
            task: The task being attempted
            
        Returns:
            True if we should try a different approach
        """
        approach = self.detect_approach(solution)
        approach_key = f"{task[:50]}|{approach}"
        
        return approach_key in self.forbidden_approaches
    
    # Feature 3: Witness (Traceability) Methods
    
    def add_conversation_entry(self, entry: Dict[str, Any]) -> None:
        """
        Add an entry to the conversation trace.
        
        Args:
            entry: Dictionary containing conversation details
        """
        from datetime import datetime
        entry["timestamp"] = datetime.now().isoformat()
        self.conversation_trace.append(entry)
        logger.debug(f"Added conversation entry: {entry.get('type', 'unknown')}")
    
    def export_conversation_trace(self, filepath: str) -> None:
        """
        Export the conversation trace to a JSON file.
        
        Args:
            filepath: Path to save the trace
        """
        import json
        from pathlib import Path
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "trace": self.conversation_trace,
                "stats": self.get_stats(),
                "nodes": [
                    {
                        "id": node.id,
                        "content": node.content[:200],  # Truncate for readability
                        "status": node.status.value,
                        "verification_count": len(node.verification_results)
                    }
                    for node in self.nodes.values()
                ]
            }, f, indent=2)
        
        logger.info(f"Exported conversation trace to {filepath}")
    
    def get_conversation_trace(self) -> List[Dict[str, Any]]:
        """
        Get the full conversation trace.
        
        Returns:
            List of conversation entries
        """
        return self.conversation_trace.copy()
