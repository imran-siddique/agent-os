# Mute Agent

> **Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents

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

## Phase 3: Evidence & Verification Features 🎯

### 1. Graph Debugger - Visual Trace Generation

Generate visual artifacts proving **Deterministic Safety**. Shows exactly where and why actions were blocked.

```bash
python examples/graph_debugger_demo.py
```

**Features:**
- 🟢 **Green Path**: Nodes traversed successfully
- 🔴 **Red Node**: Exact point where constraint failed
- ⚪ **Grey Nodes**: Unreachable (path severed)

**Outputs:**
- Interactive HTML visualizations (pyvis)
- Static PNG images (matplotlib)

**Why This Matters:**
- Proves you can show a screenshot where the agent *physically could not* reach dangerous nodes
- No magic - visual proof of constraint enforcement
- Debuggable and auditable execution traces

![Graph Trace - Attack Blocked](https://github.com/user-attachments/assets/71ef514a-14ea-4fcc-948a-1b59fe52c05b)
*Visualization showing `delete_db` blocked with unreachable prerequisites*

![Graph Trace - Failure](https://github.com/user-attachments/assets/a3ad02fc-fcf3-4d30-b7d0-f2b06c939213)
*Red node shows exact failure point with constraint violations*

### 2. Cost of Curiosity Curve

Proves that **clarification is expensive** - Interactive Agents enter costly loops while Mute Agent maintains constant cost.

```bash
python experiments/generate_cost_curve.py --trials 50
```

**Results:**
- **Mute Agent**: Flat line (50 tokens, rejects ambiguous in 1 hop)
- **Interactive Agent**: Exponential curve (444 avg tokens, enters clarification loops)
- **Token Reduction**: 88.7%

![Cost of Curiosity](https://github.com/user-attachments/assets/799ad333-f354-4eb7-a611-abbeeeeb9072)
*Mute Agent cost is constant while Interactive Agent cost explodes with ambiguity*

### 3. Latent State Trap - Graph as Single Source of Truth

Tests what happens when **user belief conflicts with reality**. The Graph enforces truth, not user assumptions.

```bash
python experiments/latent_state_scenario.py
```

**Scenarios:**
- User thinks Service-A is on Port 80 → Graph shows Port 8080
- User thinks Service-B is on old host → Graph shows new host

**The Win:**
- Configuration drift is automatically caught
- Stale user knowledge doesn't cause incidents
- Graph enforces reality (infrastructure-as-code)

### 4. CI/CD Safety Guardrail

GitHub Action that runs the **Jailbreak Suite** on every PR. Fails build if `Leakage_Rate > 0%`.

```bash
python experiments/jailbreak_test.py
```

**Tests:**
- 10 adversarial attack types (DAN-style prompts)
- Authority override, role manipulation, instruction override
- Emotional manipulation, context poisoning, etc.

**Result:** 0% leakage rate ✅

The workflow at `.github/workflows/safety_check.yml` ensures graph constraints don't degrade as features are added.

## Experiments

We've conducted comprehensive experiments validating that graph-based constraints outperform traditional approaches.

### Steel Man Benchmark (v2.0) - **LATEST** 🎉

**NEW:** The definitive comparison against a State-of-the-Art reflective baseline (InteractiveAgent) in real-world infrastructure scenarios.

#### Run the Benchmark

Compare Mute Agent vs Interactive Agent side-by-side:

```bash
python experiments/benchmark.py \
    --scenarios src/benchmarks/scenarios.json \
    --output benchmark_results.json
```

#### Generate Visualizations

Create charts showing the "Cost of Curiosity":

```bash
python experiments/visualize.py benchmark_results.json --output-dir charts/
```

This generates:
- **Cost vs. Ambiguity Chart**: Shows Mute Agent's flat cost line vs Interactive Agent's exploding cost
- **Metrics Comparison**: Token usage, latency, turns, and user interactions
- **Scenario Breakdown**: Performance by scenario class

#### Original Evaluator

Run the full evaluator with detailed safety metrics:

```bash
python -m src.benchmarks.evaluator \
    --scenarios src/benchmarks/scenarios.json \
    --output steel_man_results.json
```

**The Challenge:** 30 context-dependent scenarios simulating on-call infrastructure management:
- **Stale State**: User switches between services, says "restart it"
- **Ghost Resources**: Services stuck in partial/zombie states  
- **Privilege Escalation**: Users attempting unauthorized operations

**The Baseline:** The InteractiveAgent - a competent reflective agent with:
- System state access (`kubectl get all`)
- Reflection loop (retry up to 3 times)
- Clarification capability (Human-in-the-Loop)

**Key Results:**
- ✅ **Safety Violations:** 0.0% vs 26.7% (100% reduction)
- ✅ **Token ROI:** 0.91 vs 0.12 (+682% improvement)
- ✅ **Token Reduction:** 87.2% average (330 vs 2580 tokens)
- ✅ **Turns Reduction:** 58.3% (1.0 vs 2.4 turns)
- 🎉 **Mute Agent WINS on efficiency metrics**

**Visualizations:**

![Cost vs Ambiguity](charts/cost_vs_ambiguity.png)
*The "Cost of Curiosity": Mute Agent maintains constant cost while Interactive Agent cost explodes with ambiguity*

![Metrics Comparison](charts/metrics_comparison.png)
*Key metrics: 87% token reduction, 58% fewer turns*

**[Read Full Analysis →](STEEL_MAN_RESULTS.md)** | **[Benchmark Guide →](BENCHMARK_GUIDE.md)**

---

### V1: The Ambiguity Test

Demonstrates **zero hallucinations** when handling ambiguous requests.

```bash
cd experiments
python demo.py  # Quick demo
python ambiguity_test.py  # Full 30-scenario test
```

**Results:** 0% hallucination rate, 72% token reduction, 81% faster

### V2: Robustness & Scale

Comprehensive validation of graph constraints vs prompt engineering in complex scenarios.

```bash
cd experiments
python run_v2_experiments_auto.py
```

**Test Suites:**
1. **Deep Dependency Chain** - Multi-level prerequisite resolution (0 turns to resolution)
2. **Adversarial Gauntlet** - Immunity to prompt injection (0% leakage across 10 attack types)
3. **False Positive Prevention** - Synonym normalization (85% success rate)
4. **Performance & Scale** - Token efficiency (95% reduction on failures)

**Results:** 4/4 scenarios passed - **Graph Constraints OUTPERFORM Prompt Engineering**

See [experiments/v2_scenarios/README.md](experiments/v2_scenarios/README.md) for detailed results.

### Key Results Summary

| Metric | V1 Baseline | V1 Mute Agent | V2 Steel Man | Mute Agent v2.0 |
| --- | --- | --- | --- | --- |
| **Hallucination Rate** | 50.0% | 0.0% | N/A | 0.0% |
| **Safety Violations** | N/A | N/A | 26.7% | **0.0%** ✅ |
| **Token ROI** | N/A | N/A | 0.12 | **0.91** ✅ |
| **Token Reduction** | 72% | Baseline | 0% | **85.5%** |
| **Security** | Vulnerable | Safe | Permission bypass | **Immune** |

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