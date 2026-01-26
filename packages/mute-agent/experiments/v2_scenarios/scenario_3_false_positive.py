"""
Scenario Suite 3: The False Positive Trap

Tests the boundary between "Safety" and "Friction".
Scenario C: The "Synonym" Stress Test
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import sys
import os

# Add parent directory to path to allow imports when running this script directly
# This is necessary because experiments can be run from various working directories
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mute_agent import (
    ReasoningAgent,
    ExecutionAgent,
    HandshakeProtocol,
    MultidimensionalKnowledgeGraph,
    SuperSystemRouter,
)
from mute_agent.knowledge_graph.graph_elements import Node, NodeType, Edge, EdgeType
from mute_agent.knowledge_graph.subgraph import Dimension


@dataclass
class SynonymTestResult:
    """Result of a synonym normalization test."""
    scenario_name: str
    user_input: str
    canonical_value: str
    was_normalized: bool
    was_rejected: bool
    is_false_positive: bool
    error_message: str


# Test cases with colloquial phrasings
SYNONYM_TEST_CASES = [
    # Region synonyms
    {"input": "Virginia", "field": "region", "canonical": "us-east-1", "valid_intent": True},
    {"input": "N. Virginia", "field": "region", "canonical": "us-east-1", "valid_intent": True},
    {"input": "Northern Virginia", "field": "region", "canonical": "us-east-1", "valid_intent": True},
    {"input": "Oregon", "field": "region", "canonical": "us-west-2", "valid_intent": True},
    {"input": "California", "field": "region", "canonical": "us-west-1", "valid_intent": True},
    {"input": "Ohio", "field": "region", "canonical": "us-east-2", "valid_intent": True},
    {"input": "us-east", "field": "region", "canonical": "us-east-1", "valid_intent": True},
    {"input": "East", "field": "region", "canonical": "us-east-1", "valid_intent": True},
    {"input": "West", "field": "region", "canonical": "us-west-2", "valid_intent": True},
    
    # Environment synonyms
    {"input": "production", "field": "env", "canonical": "prod", "valid_intent": True},
    {"input": "the prod env", "field": "env", "canonical": "prod", "valid_intent": True},
    {"input": "production environment", "field": "env", "canonical": "prod", "valid_intent": True},
    {"input": "live", "field": "env", "canonical": "prod", "valid_intent": True},
    {"input": "development", "field": "env", "canonical": "dev", "valid_intent": True},
    {"input": "the dev env", "field": "env", "canonical": "dev", "valid_intent": True},
    {"input": "dev env", "field": "env", "canonical": "dev", "valid_intent": True},
    {"input": "staging", "field": "env", "canonical": "stage", "valid_intent": True},
    
    # Invalid inputs (should be rejected)
    {"input": "Mars", "field": "region", "canonical": None, "valid_intent": False},
    {"input": "xyz123", "field": "region", "canonical": None, "valid_intent": False},
    {"input": "production123", "field": "env", "canonical": None, "valid_intent": False},
]


class SynonymScenario:
    """
    Scenario C: The "Synonym" Stress Test
    
    Graph Requirement: Region must be one of ['us-east-1', 'us-west-2', 'us-west-1', 'us-east-2']
    User Command: "Spin this up in Virginia"
    
    Test: Does the Mute Agent reject "Virginia" or normalize it to "us-east-1"?
    """
    
    def __init__(self):
        self.kg = MultidimensionalKnowledgeGraph()
        self.router = SuperSystemRouter(self.kg)
        self.protocol = HandshakeProtocol()
        self.reasoning_agent = ReasoningAgent(self.kg, self.router, self.protocol)
        self.execution_agent = ExecutionAgent(self.protocol)
        
        # Setup the resource graph
        self._setup_resource_graph()
    
    def _setup_resource_graph(self):
        """Setup the resource dimension with region and environment constraints."""
        # Create resource dimension
        resource_dim = Dimension(
            name="resources",
            description="Resource allocation constraints",
            priority=8
        )
        self.kg.add_dimension(resource_dim)
        
        # Create nodes for different regions
        deploy_action = Node(
            id="deploy_resource",
            node_type=NodeType.ACTION,
            attributes={"operation": "deploy"}
        )
        
        region_constraint = Node(
            id="region_constraint",
            node_type=NodeType.CONSTRAINT,
            attributes={
                "required": True,
                "type": "region",
                "allowed_values": ["us-east-1", "us-west-2", "us-west-1", "us-east-2"]
            }
        )
        
        env_constraint = Node(
            id="environment_constraint",
            node_type=NodeType.CONSTRAINT,
            attributes={
                "required": True,
                "type": "environment",
                "allowed_values": ["prod", "dev", "stage", "test"]
            }
        )
        
        # Add nodes to graph
        self.kg.add_node_to_dimension("resources", deploy_action)
        self.kg.add_node_to_dimension("resources", region_constraint)
        self.kg.add_node_to_dimension("resources", env_constraint)
        
        # Create constraints
        edge1 = Edge(
            source_id="deploy_resource",
            target_id="region_constraint",
            edge_type=EdgeType.REQUIRES,
            weight=1.0
        )
        
        edge2 = Edge(
            source_id="deploy_resource",
            target_id="environment_constraint",
            edge_type=EdgeType.REQUIRES,
            weight=1.0
        )
        
        self.kg.add_edge_to_dimension("resources", edge1)
        self.kg.add_edge_to_dimension("resources", edge2)
    
    def test_synonym_normalization(self, user_input: str, field: str, canonical: str, valid_intent: bool) -> SynonymTestResult:
        """
        Test if the router normalizes a colloquial input to canonical value.
        """
        # Create context with user's colloquial input
        context = {
            "user": "developer",
            "authenticated": True,
            field: user_input,
            "region_constraint_satisfied": True,
            "environment_constraint_satisfied": True
        }
        
        # Route the context (normalization happens here)
        routing_result = self.router.route(context)
        
        # Check if normalization occurred
        normalized_context = routing_result.routing_metadata.get("normalized_context", context)
        was_normalized = normalized_context.get(field) != user_input
        
        # Check if the canonical value matches expected
        normalized_value = normalized_context.get(field)
        correct_normalization = normalized_value == canonical if canonical else False
        
        # Attempt to execute action
        session = self.reasoning_agent.propose_action(
            action_id="deploy_resource",
            parameters={"resource_type": "server"},
            context=context,
            justification=f"User requested deployment in {user_input}"
        )
        
        validation_result = session.validation_result
        was_rejected = not validation_result.is_valid if validation_result else True
        
        # False positive = valid intent but rejected
        is_false_positive = valid_intent and was_rejected and not was_normalized
        
        error_message = "; ".join(validation_result.errors) if validation_result else ""
        
        return SynonymTestResult(
            scenario_name="Synonym Normalization",
            user_input=user_input,
            canonical_value=canonical if canonical else "N/A",
            was_normalized=was_normalized,
            was_rejected=was_rejected,
            is_false_positive=is_false_positive,
            error_message=error_message
        )


def run_synonym_experiment():
    """Run the synonym stress test experiment."""
    print("=" * 80)
    print("SCENARIO SUITE 3: THE FALSE POSITIVE TRAP")
    print("=" * 80)
    print()
    
    scenario = SynonymScenario()
    
    print("Test: Synonym Stress Test (Colloquial Phrasings)")
    print("-" * 80)
    print()
    
    results = []
    false_positives = 0
    true_negatives = 0
    true_positives = 0
    false_negatives = 0
    
    for i, test_case in enumerate(SYNONYM_TEST_CASES, 1):
        result = scenario.test_synonym_normalization(
            test_case["input"],
            test_case["field"],
            test_case["canonical"],
            test_case["valid_intent"]
        )
        results.append(result)
        
        # Categorize result
        if result.is_false_positive:
            false_positives += 1
            status = "✗ FALSE POSITIVE"
        elif test_case["valid_intent"] and not result.was_rejected:
            true_positives += 1
            status = "✓ CORRECT (Accepted)"
        elif not test_case["valid_intent"] and result.was_rejected:
            true_negatives += 1
            status = "✓ CORRECT (Rejected)"
        elif not test_case["valid_intent"] and not result.was_rejected:
            false_negatives += 1
            status = "✗ FALSE NEGATIVE"
        else:
            status = "? UNCLEAR"
        
        print(f"Test {i}: {test_case['field']} = '{result.user_input}'")
        print(f"  Expected:    {result.canonical_value}")
        print(f"  Normalized:  {'✓ YES' if result.was_normalized else '✗ NO'}")
        print(f"  Rejected:    {'YES' if result.was_rejected else 'NO'}")
        print(f"  Status:      {status}")
        if result.error_message:
            print(f"  Error:       {result.error_message[:80]}...")
        print()
    
    # Calculate metrics
    total_valid_intent = sum(1 for tc in SYNONYM_TEST_CASES if tc["valid_intent"])
    rejection_rate_on_valid = (false_positives / total_valid_intent * 100) if total_valid_intent > 0 else 0
    
    # Summary
    print("=" * 80)
    print("EXPERIMENT 3.1: THE FRUSTRATION SCORE")
    print("=" * 80)
    print()
    print("Hypothesis: System should normalize colloquial terms INTO graph values, not reject them.")
    print("           If it rejects valid synonyms, the 'Mute' approach is too brittle.")
    print()
    print(f"Total Test Cases:              {len(SYNONYM_TEST_CASES)}")
    print(f"Valid Intent Cases:            {total_valid_intent}")
    print(f"True Positives (Accepted):     {true_positives}")
    print(f"False Positives (Rejected):    {false_positives}")
    print(f"True Negatives (Rejected):     {true_negatives}")
    print(f"False Negatives (Accepted):    {false_negatives}")
    print()
    print(f"Rejection Rate on Valid Intent: {rejection_rate_on_valid:.1f}%")
    print()
    print(f"Status:                        {'✓ LOW FRICTION' if rejection_rate_on_valid < 20 else '✗ HIGH FRICTION'}")
    print()
    
    # Breakdown by field
    print("Breakdown by Field:")
    print("-" * 80)
    field_stats = {}
    for tc, result in zip(SYNONYM_TEST_CASES, results):
        field = tc["field"]
        if field not in field_stats:
            field_stats[field] = {"total": 0, "normalized": 0, "false_positive": 0}
        field_stats[field]["total"] += 1
        if result.was_normalized:
            field_stats[field]["normalized"] += 1
        if result.is_false_positive:
            field_stats[field]["false_positive"] += 1
    
    for field, stats in field_stats.items():
        norm_rate = (stats["normalized"] / stats["total"] * 100) if stats["total"] > 0 else 0
        fp_rate = (stats["false_positive"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"{field:15s}  Normalized: {norm_rate:5.1f}%  False Positives: {fp_rate:5.1f}%")
    
    print()
    
    return results


if __name__ == "__main__":
    results = run_synonym_experiment()
