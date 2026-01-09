# Mute Agent

**Decoupling Reasoning from Execution using a Dynamic Semantic Handshake Protocol**

## Overview

The Mute Agent is an advanced agent architecture that decouples reasoning (The Face) from execution (The Hands) using a Dynamic Semantic Handshake Protocol. Instead of free-text tool invocation, the Reasoning Agent must negotiate actions against a Multidimensional Knowledge Graph.

## Key Components

### 1. The Face (Reasoning Agent)
The thinking component responsible for:
- Analyzing context
- Reasoning about available actions
- Proposing actions based on graph constraints
- Validating action proposals against the knowledge graph

### 2. The Hands (Execution Agent)
The action component responsible for:
- Executing validated actions
- Managing action handlers
- Tracking execution results
- Reporting execution statistics

### 3. Dynamic Semantic Handshake Protocol
The negotiation mechanism that:
- Manages the communication between reasoning and execution
- Enforces strict validation before execution
- Tracks the complete lifecycle of action proposals
- Provides session-based negotiation

### 4. Multidimensional Knowledge Graph
A dynamic constraint layer that:
- Organizes knowledge into multiple dimensions
- Acts as a "Forest of Trees" with dimensional subgraphs
- Provides graph-based constraint validation
- Enables fine-grained action space pruning

### 5. Super System Router
The routing component that:
- Analyzes context to select relevant dimensions
- Prunes the action space before the agent acts
- Implements the "Forest of Trees" approach
- Provides efficient action space management

## Architecture

```
Context → Super System Router → Dimensional Subgraphs → Pruned Action Space
                                        ↓
                                Knowledge Graph
                                        ↓
The Face (Reasoning) ←→ Handshake Protocol ←→ The Hands (Execution)
```

## Installation

```bash
pip install -e .
```

For development with testing tools:
```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from mute_agent import (
    ReasoningAgent,
    ExecutionAgent,
    HandshakeProtocol,
    MultidimensionalKnowledgeGraph,
    SuperSystemRouter,
)
from mute_agent.knowledge_graph.graph_elements import Node, NodeType, Edge, EdgeType
from mute_agent.knowledge_graph.subgraph import Dimension

# 1. Create a knowledge graph
kg = MultidimensionalKnowledgeGraph()

# 2. Define dimensions
security_dim = Dimension(
    name="security",
    description="Security constraints",
    priority=10
)
kg.add_dimension(security_dim)

# 3. Add actions and constraints
action = Node(
    id="read_file",
    node_type=NodeType.ACTION,
    attributes={"operation": "read"}
)
kg.add_node_to_dimension("security", action)

# 4. Initialize components
router = SuperSystemRouter(kg)
protocol = HandshakeProtocol()
reasoning_agent = ReasoningAgent(kg, router, protocol)
execution_agent = ExecutionAgent(protocol)

# 5. Register action handlers
def read_handler(params):
    return {"content": "file content"}

execution_agent.register_action_handler("read_file", read_handler)

# 6. Reason and execute
context = {"user": "admin", "authenticated": True}
session = reasoning_agent.propose_action(
    action_id="read_file",
    parameters={"path": "/data/file.txt"},
    context=context,
    justification="User requested file read"
)

if session.validation_result.is_valid:
    protocol.accept_proposal(session.session_id)
    result = execution_agent.execute(session.session_id)
    print(result.execution_result)
```

## Examples

Run the included example:
```bash
python examples/simple_example.py
```

## Core Concepts

### Forest of Trees Approach
The knowledge graph organizes constraints into multiple dimensional subgraphs. Each dimension represents a different constraint layer (e.g., security, resources, workflow). The Super System Router selects relevant dimensions based on context, effectively pruning the action space.

### Graph-Based Constraints
Instead of free-text invocation, all actions must exist as nodes in the knowledge graph and satisfy the constraints (edges) defined in relevant dimensions. This provides:
- Type safety through graph structure
- Explicit constraint validation
- Traceable action authorization
- Fine-grained control over action spaces

### Semantic Handshake
The protocol enforces a strict negotiation process:
1. **Initiated**: Reasoning agent proposes an action
2. **Validated**: Action is checked against graph constraints
3. **Accepted/Rejected**: Based on validation results
4. **Executing**: Execution agent begins work
5. **Completed/Failed**: Final state with results

## Benefits

1. **Separation of Concerns**: Reasoning and execution are completely decoupled
2. **Safety**: All actions must pass graph-based validation
3. **Transparency**: Complete audit trail through session tracking
4. **Flexibility**: Dynamic constraint management through dimensions
5. **Scalability**: Efficient action space pruning reduces complexity

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.