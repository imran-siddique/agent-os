# Mute Agent Architecture

## System Overview

The Mute Agent implements a novel architecture that strictly separates reasoning from execution through a graph-based constraint system and a formal negotiation protocol.

## Core Principles

### 1. Separation of Concerns
- **The Face (Reasoning Agent)**: Thinks but never executes
- **The Hands (Execution Agent)**: Executes but never reasons
- **Communication**: Only through the Handshake Protocol

### 2. Graph-Based Constraints
All actions must be validated against a multidimensional knowledge graph before execution. This replaces free-text tool invocation with structured, validated action proposals.

### 3. Dynamic Action Space Pruning
The Super System Router analyzes context and selectively activates dimensional subgraphs, dramatically reducing the action space before reasoning begins.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Context Input                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Super System Router                       │
│  • Analyzes context                                          │
│  • Selects relevant dimensions                               │
│  • Prunes action space                                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            Multidimensional Knowledge Graph                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Security    │  │  Resource    │  │  Workflow    │      │
│  │  Dimension   │  │  Dimension   │  │  Dimension   │ ...  │
│  │              │  │              │  │              │      │
│  │ ┌──┐   ┌──┐ │  │ ┌──┐   ┌──┐ │  │ ┌──┐   ┌──┐ │      │
│  │ │A1├───┤C1│ │  │ │A1├───┤C2│ │  │ │A1├───┤C3│ │      │
│  │ └──┘   └──┘ │  │ └──┘   └──┘ │  │ └──┘   └──┘ │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Forest of Trees: Each dimension is a separate subgraph     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Pruned Action Space                          │
│         (Actions valid across all dimensions)                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              The Face (Reasoning Agent)                      │
│  • Reasons about available actions                           │
│  • Proposes action with justification                        │
│  • Validates against graph constraints                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           Dynamic Semantic Handshake Protocol                │
│                                                              │
│  Session States:                                             │
│  INITIATED → VALIDATED → ACCEPTED → EXECUTING → COMPLETED   │
│         ↓                    ↓                               │
│     REJECTED              FAILED                             │
│                                                              │
│  • Enforces strict validation                                │
│  • Tracks complete lifecycle                                 │
│  • Provides audit trail                                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             The Hands (Execution Agent)                      │
│  • Executes validated actions only                           │
│  • Manages action handlers                                   │
│  • Reports execution results                                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Execution Result                          │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Context Processing
```
User Context → Router → Dimension Selection → Subgraph Activation
```

### 2. Action Space Pruning
```
All Actions → Filter by Dimensions → Intersect Valid Actions → Pruned Space
```

### 3. Negotiation Protocol
```
Proposal → Validation → Accept/Reject → Execute → Result
```

## Key Classes

### Knowledge Graph Components

#### Node
- Represents entities in the graph (actions, constraints, etc.)
- Has type, attributes, and metadata
- Implements constraint matching

#### Edge
- Represents relationships between nodes
- Has type (REQUIRES, ENABLES, CONFLICTS_WITH, etc.)
- Has weight and attributes

#### Dimension
- Represents a constraint layer
- Has priority for routing decisions
- Contains metadata for matching

#### Subgraph
- Contains nodes and edges for one dimension
- Implements action validation
- Supports context-based pruning

#### MultidimensionalKnowledgeGraph
- Manages multiple dimensional subgraphs
- Coordinates cross-dimensional validation
- Provides unified query interface

### Routing Components

#### SuperSystemRouter
- Analyzes context to select dimensions
- Prunes action space efficiently
- Tracks routing statistics
- Implements "Forest of Trees" approach

### Protocol Components

#### ActionProposal
- Contains action ID, parameters, context
- Includes justification for traceability
- Has priority and timestamp

#### ValidationResult
- Reports validation status
- Lists errors and warnings
- Tracks constraint satisfaction

#### HandshakeSession
- Tracks negotiation lifecycle
- Maintains state machine
- Stores complete history

#### HandshakeProtocol
- Manages all sessions
- Enforces state transitions
- Provides session queries

### Agent Components

#### ReasoningAgent (The Face)
- Uses router for action space analysis
- Proposes actions with validation
- Selects best actions based on criteria
- Never executes directly

#### ExecutionAgent (The Hands)
- Executes validated actions only
- Manages action handler registry
- Tracks execution history
- Never reasons about actions

## Benefits of This Architecture

### 1. Safety
- All actions must pass graph validation
- No free-text tool invocation
- Explicit constraint checking
- Type safety through graph structure

### 2. Transparency
- Complete audit trail through sessions
- Explicit justifications required
- Full constraint traceability
- Clear separation of responsibilities

### 3. Scalability
- Efficient action space pruning
- Parallel dimension processing possible
- Independent dimension management
- Modular constraint addition

### 4. Flexibility
- Dynamic dimension activation
- Context-aware routing
- Pluggable action handlers
- Extensible constraint types

## Implementation Details

### Forest of Trees Approach

Instead of a single monolithic graph, the system maintains multiple dimensional subgraphs:

```python
# Each dimension is an independent tree/subgraph
security_subgraph = {
    "nodes": [action1, action2, constraint1],
    "edges": [requires_edge1, requires_edge2]
}

resource_subgraph = {
    "nodes": [action1, action2, constraint2],
    "edges": [depends_edge1, depends_edge2]
}

# Router selects relevant subgraphs based on context
relevant_subgraphs = router.route(context)

# Action must be valid in ALL selected subgraphs
valid_actions = intersect_all(relevant_subgraphs)
```

### Constraint Validation

Actions are validated at multiple levels:

1. **Existence**: Action must exist in pruned action space
2. **Dimensional**: Action must be valid in each selected dimension
3. **Constraints**: All required constraints must be satisfied
4. **Parameters**: Action parameters must meet requirements

### State Machine

The handshake protocol enforces a strict state machine:

```
INITIATED ──validate──> VALIDATED ──accept──> ACCEPTED
    │                       │                     │
    └───────────────────────┴──reject──> REJECTED
    
ACCEPTED ──execute──> EXECUTING ──success──> COMPLETED
                          │
                          └──error──> FAILED
```

## Extension Points

### Adding New Dimensions

```python
# Define dimension
new_dim = Dimension(
    name="compliance",
    description="Regulatory compliance checks",
    priority=8
)

# Add to knowledge graph
kg.add_dimension(new_dim)

# Add nodes and edges
kg.add_node_to_dimension("compliance", action_node)
kg.add_edge_to_dimension("compliance", constraint_edge)
```

### Registering Action Handlers

```python
def my_action_handler(parameters):
    # Implement action logic
    return {"result": "success"}

execution_agent.register_action_handler("my_action", my_action_handler)
```

### Custom Selection Criteria

```python
criteria = {
    "priority": "high",
    "resource_cost": "low"
}

best_action = reasoning_agent.select_best_action(context, criteria)
```

## Future Enhancements

1. **Parallel Dimension Processing**: Validate across dimensions in parallel
2. **ML-Based Action Selection**: Learn from execution history
3. **Dynamic Dimension Weighting**: Adjust priorities based on context
4. **Conflict Resolution**: Automatic resolution of constraint conflicts
5. **Temporal Constraints**: Time-based validation and scheduling
6. **Distributed Knowledge Graphs**: Multi-node graph management
