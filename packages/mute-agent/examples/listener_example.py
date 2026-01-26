"""
Layer 5 Listener Agent - Reference Implementation Example

This example demonstrates the Listener Agent pattern:
1. Passive observation of graph states
2. Threshold-based intervention
3. Integration with the full stack (mocked)

The Listener is the capstone of the 5-layer architecture, consolidating:
- agent-control-plane (base orchestration)
- scak (intelligence/knowledge)
- iatp (security/trust)
- caas (context-as-a-service)

Usage:
    python examples/listener_example.py
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mute_agent import (
    # Core components
    MultidimensionalKnowledgeGraph,
    HandshakeProtocol,
    SuperSystemRouter,
    ReasoningAgent,
    ExecutionAgent,
    # Layer 5: Listener
    ListenerAgent,
    ListenerState,
    InterventionEvent,
    ThresholdConfig,
    ThresholdType,
    InterventionLevel,
    DEFAULT_THRESHOLDS,
)
from mute_agent.knowledge_graph.graph_elements import Node, Edge, NodeType, EdgeType
from mute_agent.knowledge_graph.subgraph import Dimension


def create_sample_graph() -> MultidimensionalKnowledgeGraph:
    """Create a sample knowledge graph for demonstration."""
    kg = MultidimensionalKnowledgeGraph()
    
    # Add dimensions
    security_dim = Dimension(
        name="security",
        description="Security constraints",
        priority=10,
    )
    operations_dim = Dimension(
        name="operations",
        description="Operational actions",
        priority=8,
    )
    
    kg.add_dimension(security_dim)
    kg.add_dimension(operations_dim)
    
    # Add action nodes
    actions = [
        ("read_data", "Read data from storage"),
        ("write_data", "Write data to storage"),
        ("delete_data", "Delete data from storage"),
        ("restart_service", "Restart a service"),
    ]
    
    for action_id, description in actions:
        node = Node(
            id=action_id,
            node_type=NodeType.ACTION,
            attributes={"description": description},
        )
        kg.add_node_to_dimension("operations", node)
    
    # Add constraint nodes
    auth_constraint = Node(
        id="require_auth",
        node_type=NodeType.CONSTRAINT,
        attributes={"type": "authentication"},
    )
    kg.add_node_to_dimension("security", auth_constraint)
    
    # Add constraint edges
    for action_id in ["write_data", "delete_data", "restart_service"]:
        edge = Edge(
            source_id=action_id,
            target_id="require_auth",
            edge_type=EdgeType.REQUIRES,
            attributes={"reason": "sensitive_operation"},
        )
        kg.add_edge_to_dimension("security", edge)
    
    return kg


def on_intervention(event: InterventionEvent):
    """Callback for intervention events."""
    print(f"\n🚨 INTERVENTION EVENT")
    print(f"   ID: {event.event_id}")
    print(f"   Level: {event.intervention_level.value}")
    print(f"   Action: {event.action_taken}")
    print(f"   Triggered Rules: {len(event.triggered_rules)}")
    for rule in event.triggered_rules:
        print(f"      - {rule.description}")
    print(f"   Outcome: {event.outcome}")
    print(f"   Duration: {event.duration_ms:.2f}ms")


def on_state_change(old_state: ListenerState, new_state: ListenerState):
    """Callback for state changes."""
    print(f"   📊 Listener state: {old_state.value} → {new_state.value}")


def main():
    print("=" * 60)
    print("Layer 5: Listener Agent - Reference Implementation")
    print("=" * 60)
    
    # === Step 1: Create core components ===
    print("\n1️⃣  Creating core components...")
    
    kg = create_sample_graph()
    protocol = HandshakeProtocol()
    router = SuperSystemRouter(kg)
    
    print(f"   ✅ Knowledge graph: {len(kg.dimensions)} dimensions")
    print(f"   ✅ Handshake protocol initialized")
    print(f"   ✅ Super system router ready")
    
    # === Step 2: Configure thresholds ===
    print("\n2️⃣  Configuring intervention thresholds...")
    
    # Use default thresholds with some customization
    threshold_config = ThresholdConfig(
        rules=DEFAULT_THRESHOLDS.rules.copy(),
        global_intervention_level=InterventionLevel.OBSERVE,
        window_size_seconds=60.0,
    )
    
    # Add a custom threshold for demo
    from mute_agent.listener.threshold_config import ThresholdRule
    threshold_config.add_rule(ThresholdRule(
        threshold_type=ThresholdType.ACTION_REJECTION_RATE,
        value=0.3,  # Lower threshold for demo
        intervention_level=InterventionLevel.WARN,
        description="Demo: Warn when rejection rate exceeds 30%",
    ))
    
    print(f"   ✅ {len(threshold_config.rules)} threshold rules configured")
    
    # === Step 3: Create Listener Agent ===
    print("\n3️⃣  Creating Listener Agent...")
    
    from mute_agent.listener import ListenerConfig
    listener_config = ListenerConfig(
        thresholds=threshold_config,
        observation_interval_seconds=0.5,
        auto_intervention=True,
    )
    
    listener = ListenerAgent(
        knowledge_graph=kg,
        protocol=protocol,
        router=router,
        config=listener_config,
    )
    
    # Register callbacks
    listener.register_intervention_callback(on_intervention)
    listener.register_state_change_callback(on_state_change)
    
    print(f"   ✅ Listener agent created")
    print(f"   📊 Initial state: {listener.state.value}")
    
    # === Step 4: Demonstrate passive observation ===
    print("\n4️⃣  Demonstrating passive observation...")
    
    # Import MetricType for accessing metrics
    from mute_agent.listener.state_observer import MetricType
    
    # Perform a few manual observations
    for i in range(3):
        observation = listener.observe_once()
        print(f"   📊 Observation {i+1}:")
        print(f"      - Dimensions: {int(observation.metrics.get(MetricType.DIMENSION_COUNT, 0))}")
        print(f"      - Nodes: {int(observation.metrics.get(MetricType.NODE_COUNT, 0))}")
        print(f"      - Edges: {int(observation.metrics.get(MetricType.EDGE_COUNT, 0))}")
        print(f"      - Rejection rate: {observation.derived_metrics.get('action_rejection_rate', 0):.2%}")
        time.sleep(0.2)
    
    # === Step 5: Simulate activity that triggers thresholds ===
    print("\n5️⃣  Simulating protocol activity...")
    
    # Create some handshake sessions (some will be rejected)
    from mute_agent.core.handshake_protocol import ActionProposal, ValidationResult
    
    for i in range(5):
        proposal = ActionProposal(
            action_id=f"test_action_{i}",
            parameters={"target": f"resource_{i}"},
            context={"user": "test_user"},
            justification=f"Test action {i}",
        )
        session = protocol.initiate_handshake(proposal)
        
        # Reject some to increase rejection rate
        if i % 2 == 0:
            validation = ValidationResult(
                is_valid=False,
                errors=["Simulated rejection for demo"],
            )
            protocol.validate_proposal(session.session_id, validation)
            print(f"   ❌ Session {session.session_id}: REJECTED")
        else:
            validation = ValidationResult(is_valid=True)
            protocol.validate_proposal(session.session_id, validation)
            protocol.accept_proposal(session.session_id)
            print(f"   ✅ Session {session.session_id}: ACCEPTED")
    
    # === Step 6: Start the Listener ===
    print("\n6️⃣  Starting Listener Agent (background observation)...")
    
    listener.start()
    print(f"   📊 Listener state: {listener.state.value}")
    
    # Let it run for a bit
    print("   ⏳ Observing for 3 seconds...")
    time.sleep(3)
    
    # === Step 7: Check statistics ===
    print("\n7️⃣  Checking Listener statistics...")
    
    stats = listener.get_statistics()
    print(f"   📊 State: {stats['state']}")
    print(f"   📊 Total observations: {stats['total_observations']}")
    print(f"   📊 Total interventions: {stats['total_interventions']}")
    print(f"   📊 Active thresholds: {stats['active_thresholds']}")
    
    # === Step 8: Stop the Listener ===
    print("\n8️⃣  Stopping Listener Agent...")
    
    listener.stop()
    print(f"   📊 Final state: {listener.state.value}")
    
    # === Summary ===
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"""
The Listener Agent demonstrates Layer 5 of the architecture:

1. PASSIVE OBSERVATION
   - Monitors graph state without interfering
   - Collects metrics from protocol and router
   - Calculates derived metrics for analysis

2. THRESHOLD-BASED INTERVENTION
   - Configurable rules for when to intervene
   - Multiple intervention levels (WARN → EMERGENCY)
   - Rate limiting to prevent over-intervention

3. CONSOLIDATED STACK
   - Wires together: agent-control-plane, scak, iatp, caas
   - Adapters provide clean interfaces to each layer
   - No logic reimplementation - pure delegation

4. AUDIT TRAIL
   - Every intervention is logged with full context
   - Callbacks for external integration
   - Statistics for monitoring

This reference implementation is designed for:
- GitHub: As a reference repo showing the pattern
- PyPI: As a reusable library (when dependencies are published)
""")
    
    # Show intervention history
    interventions = listener.get_intervention_history()
    if interventions:
        print(f"Intervention History ({len(interventions)} events):")
        for event in interventions:
            print(f"  - {event.timestamp.isoformat()}: {event.action_taken} ({event.intervention_level.value})")
    else:
        print("No interventions occurred (system was stable).")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()
