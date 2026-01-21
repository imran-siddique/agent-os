"""
Graph Memory: The "Graph of Truth" implementation.
This module manages a persistent state machine that prevents deadlocks and caches proven truths.
"""
from typing import Dict, List, Optional, Set
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
        logger.info("Cleared graph memory")
    
    @staticmethod
    def _generate_node_id(content: str) -> str:
        """Generate a unique ID for a node based on its content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @staticmethod
    def generate_state_hash(task: str, solution: str, iteration: int) -> str:
        """Generate a hash representing the current state."""
        state_str = f"{task}|{solution}|{iteration}"
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def get_stats(self) -> Dict:
        """Get statistics about the graph state."""
        return {
            "total_nodes": len(self.nodes),
            "verified_nodes": len(self.get_verified_nodes()),
            "failed_nodes": len(self.get_failed_nodes()),
            "visited_states": len(self.visited_states),
            "cached_solutions": len(self.verified_cache)
        }
