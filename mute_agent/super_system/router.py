"""
Super System Router - Routes context to specific dimensional subgraphs.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ..knowledge_graph.multidimensional_graph import MultidimensionalKnowledgeGraph
from ..knowledge_graph.graph_elements import Node


@dataclass
class RoutingResult:
    """Result of routing a context through the Super System."""
    selected_dimensions: List[str]
    pruned_action_space: List[Node]
    routing_metadata: Dict[str, Any]


class SuperSystemRouter:
    """
    The Super System Router analyzes context and routes it to specific
    dimensional subgraphs, effectively pruning the action space before
    the agent acts.
    """
    
    def __init__(self, knowledge_graph: MultidimensionalKnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.routing_history: List[RoutingResult] = []
    
    def route(self, context: Dict[str, Any]) -> RoutingResult:
        """
        Route the context to appropriate dimensional subgraphs.
        This is the core routing mechanism that implements the
        "Forest of Trees" approach.
        """
        # Step 1: Find relevant dimensions based on context
        relevant_dimensions = self.knowledge_graph.find_relevant_dimensions(context)
        
        if not relevant_dimensions:
            # If no specific dimensions match, use all dimensions
            relevant_dimensions = list(self.knowledge_graph.dimensions.keys())
        
        # Step 2: Get pruned action spaces from each dimension
        action_spaces = {}
        for dim_name in relevant_dimensions:
            action_space = self.knowledge_graph.get_pruned_action_space(
                dim_name, context
            )
            action_spaces[dim_name] = action_space
        
        # Step 3: Intersect action spaces to find valid actions across dimensions
        pruned_action_space = self._intersect_action_spaces(
            action_spaces,
            relevant_dimensions
        )
        
        # Step 4: Create routing result
        result = RoutingResult(
            selected_dimensions=relevant_dimensions,
            pruned_action_space=pruned_action_space,
            routing_metadata={
                "context": context,
                "action_count_by_dimension": {
                    dim: len(actions) for dim, actions in action_spaces.items()
                },
                "final_action_count": len(pruned_action_space)
            }
        )
        
        # Store in history
        self.routing_history.append(result)
        
        return result
    
    def _intersect_action_spaces(
        self,
        action_spaces: Dict[str, List[Node]],
        dimension_names: List[str]
    ) -> List[Node]:
        """
        Intersect action spaces from multiple dimensions to find
        actions that are valid across all dimensions.
        """
        if not action_spaces or not dimension_names:
            return []
        
        # Start with the first dimension's action space
        first_dim = dimension_names[0]
        common_actions = {node.id: node for node in action_spaces.get(first_dim, [])}
        
        # Intersect with other dimensions
        for dim_name in dimension_names[1:]:
            dim_actions = {node.id for node in action_spaces.get(dim_name, [])}
            common_actions = {
                action_id: node
                for action_id, node in common_actions.items()
                if action_id in dim_actions
            }
        
        return list(common_actions.values())
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get statistics about routing operations."""
        if not self.routing_history:
            return {
                "total_routings": 0,
                "avg_dimensions_per_routing": 0,
                "avg_actions_per_routing": 0
            }
        
        total_routings = len(self.routing_history)
        total_dimensions = sum(
            len(result.selected_dimensions) for result in self.routing_history
        )
        total_actions = sum(
            len(result.pruned_action_space) for result in self.routing_history
        )
        
        return {
            "total_routings": total_routings,
            "avg_dimensions_per_routing": total_dimensions / total_routings,
            "avg_actions_per_routing": total_actions / total_routings,
            "dimension_usage": self._get_dimension_usage_stats()
        }
    
    def _get_dimension_usage_stats(self) -> Dict[str, int]:
        """Get statistics on how often each dimension is used."""
        usage = {}
        for result in self.routing_history:
            for dim_name in result.selected_dimensions:
                usage[dim_name] = usage.get(dim_name, 0) + 1
        return usage
