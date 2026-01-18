# Agent Control Plane

[![PyPI version](https://img.shields.io/pypi/v/agent-control-plane.svg)](https://pypi.org/project/agent-control-plane/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/imran-siddique/agent-control-plane/workflows/Tests/badge.svg)](https://github.com/imran-siddique/agent-control-plane/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://img.shields.io/pypi/dm/agent-control-plane.svg)](https://pypi.org/project/agent-control-plane/)
[![Dataset](https://img.shields.io/badge/🤗%20Datasets-red--team--60-orange.svg)](https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60)

A governance and management layer for autonomous AI agents. The Agent Control Plane treats the LLM as a raw compute component and provides a kernel-like layer for safe, controlled execution.

> **🎯 Benchmark Results**: The Control Plane achieves **0% safety violations** vs 26.67% for prompt-based safety, with 98% fewer tokens. [See comparative study →](#benchmark-comparative-safety-study)

> **🎥 Demo Video**: [Watch 2-minute demo →](#demo-video) | [Full tutorial (12 min) →](#demo-video)

## Philosophy: Scale by Subtraction

**We need to stop treating the LLM as a magic box and start treating it as a raw compute component that requires a kernel.**

In distributed systems, we don't ask a microservice nicely to respect a rate limit—we enforce it at the gateway. We don't ask a database query nicely not to drop a table—we enforce it via permissions. With AI agents, we need the same deterministic enforcement.

## Overview

As we move from chatbots to autonomous agents—systems that can execute code, modify data, and trigger workflows—the biggest bottleneck isn't intelligence. It's **governance**. The Agent Control Plane solves this by providing:

### Core Features
- **Permission Management**: Fine-grained control over what agents can do
- **Policy Enforcement**: Governance rules and compliance constraints
- **Resource Management**: Quotas, rate limiting, and resource allocation
- **Safe Execution**: Sandboxed execution with rollback capability
- **Audit Logging**: Complete traceability for all agent actions (SQLite-based Flight Recorder)
- **Risk Assessment**: Automatic risk scoring and management
- **Multi-Framework Support**: Drop-in middleware for OpenAI SDK, LangChain, MCP, and A2A protocols

### Advanced Features
- **The Mute Agent**: Capability-based execution that returns NULL for out-of-scope requests instead of hallucinating
- **Shadow Mode**: Simulation environment where agents think they're executing but actions are intercepted for validation
- **Constraint Graphs**: Multi-dimensional context (Data, Policy, Temporal) acting as the "physics" of the agent's world
- **Supervisor Agents**: Recursive governance with agents watching agents, bound by a constitution of code
- **Reasoning Telemetry**: Complete trace of agent decision-making process
- **Red Team Dataset**: Comprehensive adversarial prompt testing with 60+ attack vectors

### New: Multi-Agent & Enterprise Features
- **Agent Orchestrator**: Multi-agent coordination with sequential, parallel, and graph-based workflows (inspired by LangGraph)
- **Tool Registry**: Dynamic tool registration and discovery for extensible agent capabilities
- **Governance Layer**: Ethical alignment, bias detection, and privacy-preserving computation
- **CLI Tool**: Command-line interface for agent management and operations
- **Docker Support**: Production-ready containerization with docker-compose
- **Interactive Notebooks**: Jupyter notebook tutorials for hands-on learning

### New: Advanced Safety & Compliance (v1.1)
- **ML-Based Safety**: Jailbreak detection with 60+ attack patterns, anomaly detection, behavioral analysis
- **Compliance Engine**: EU AI Act, SOC 2, GDPR, HIPAA support with automated checks
- **Constitutional AI**: Value alignment framework inspired by Anthropic's research
- **Multimodal Capabilities**: Vision (GPT-4o-style), audio processing, RAG with vector stores
- **Production Observability**: Prometheus metrics, distributed tracing, real-time alerting

## Key Concepts

### The Problem

Traditional LLM applications lack proper governance:
- Agents have unrestricted access to execute dangerous actions
- No deterministic enforcement of boundaries
- Agents try to be "helpful" by hallucinating when they should return NULL
- Limited visibility into agent reasoning and behavior
- Difficult to enforce compliance requirements
- Hard to debug and trace agent decisions

### The Solution

The Agent Control Plane sits between the LLM (raw compute) and the execution environment, providing:

1. **Agent Kernel**: Central coordinator that mediates all agent actions with OS-like rigor
2. **Policy Engine**: Enforces rules and constraints deterministically
3. **Execution Engine**: Safely executes actions in sandboxed environments
4. **Constraint Graphs**: Multi-dimensional context defining what's possible
5. **Shadow Mode**: Test and validate agent behavior without side effects
6. **Supervisor Network**: Agents watching agents for anomalies and violations

## Quick Start

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
# Install the latest stable version
pip install agent-control-plane

# Or install with development dependencies
pip install agent-control-plane[dev]
```

#### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/imran-siddique/agent-control-plane.git
cd agent-control-plane

# Install the package in editable mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Project Structure

```
agent-control-plane/
├── src/
│   └── agent_control_plane/     # Main package source code
│       ├── agent_kernel.py      # Core kernel functionality
│       ├── control_plane.py     # Main control plane interface
│       ├── adapter.py           # OpenAI SDK adapter (drop-in middleware)
│       ├── policy_engine.py     # Policy enforcement
│       ├── execution_engine.py  # Safe execution
│       ├── constraint_graphs.py # Multi-dimensional context
│       ├── shadow_mode.py       # Simulation mode
│       ├── mute_agent.py        # Capability-based execution
│       ├── supervisor_agents.py # Recursive governance
│       └── flight_recorder.py   # Audit logging (SQLite)
├── tests/                        # Test suite
├── examples/                     # Example scripts
├── benchmark/                    # Red team safety benchmarks
├── docs/                         # Documentation
└── README.md                     # This file
```

### Basic Usage

```python
from agent_control_plane import AgentControlPlane, create_standard_agent
from agent_control_plane.agent_kernel import ActionType

# Create the control plane
control_plane = AgentControlPlane()

# Create an agent with standard permissions
agent = create_standard_agent(control_plane, "my-agent")

# Execute an action
result = control_plane.execute_action(
    agent,
    ActionType.FILE_READ,
    {"path": "/data/myfile.txt"}
)

if result["success"]:
    print(f"Result: {result['result']}")
else:
    print(f"Error: {result['error']}")
```

### Drop-In Middleware for OpenAI SDK

**NEW: Zero-friction integration!** Wrap your OpenAI client to automatically govern LLM tool calls:

```python
from openai import OpenAI
from agent_control_plane import (
    AgentControlPlane,
    create_governed_client,
    ActionType,
    PermissionLevel
)

# Standard setup
control_plane = AgentControlPlane()
client = OpenAI(api_key="your-key")

# One line to create governed client
governed = create_governed_client(
    control_plane=control_plane,
    agent_id="my-agent",
    openai_client=client,
    permissions={
        ActionType.DATABASE_QUERY: PermissionLevel.READ_ONLY,
        ActionType.FILE_READ: PermissionLevel.READ_ONLY,
    }
)

# Use exactly like normal OpenAI SDK!
response = governed.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Query database and save results"}],
    tools=[...]
)
# Tool calls are automatically governed - unauthorized actions are blocked!
```

**📖 See the [OpenAI Adapter Guide](docs/ADAPTER_GUIDE.md) for comprehensive integration instructions.**

### Multi-Framework Support

The Agent Control Plane now supports multiple AI frameworks and protocols with the same governance approach:

#### LangChain Integration

```python
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, load_tools
from agent_control_plane import (
    AgentControlPlane,
    create_governed_langchain_client,
    ActionType,
    PermissionLevel
)

# Setup
control_plane = AgentControlPlane()
llm = ChatOpenAI(temperature=0)

# Create governed LangChain client
governed_llm = create_governed_langchain_client(
    control_plane=control_plane,
    agent_id="my-langchain-agent",
    langchain_client=llm,
    permissions={
        ActionType.FILE_READ: PermissionLevel.READ_ONLY,
        ActionType.DATABASE_QUERY: PermissionLevel.READ_ONLY,
    }
)

# Use in LangChain agents - tool calls are automatically governed!
tools = load_tools(["python_repl", "requests"])
agent = initialize_agent(tools, governed_llm, agent="zero-shot-react-description")
agent.run("Your task here")
```

#### MCP (Model Context Protocol) Support

```python
from agent_control_plane import (
    AgentControlPlane,
    create_governed_mcp_server,
    ActionType,
    PermissionLevel
)

# Create governed MCP server
control_plane = AgentControlPlane()
mcp_server = create_governed_mcp_server(
    control_plane=control_plane,
    agent_id="mcp-agent",
    server_name="file-server",
    permissions={
        ActionType.FILE_READ: PermissionLevel.READ_ONLY,
    },
    transport="stdio"
)

# Register tools - all calls are governed
mcp_server.register_tool("read_file", handle_read_file, "Read a file")
mcp_server.register_resource("file://", handle_file_resource, "File resources")
mcp_server.start()
```

#### A2A (Agent-to-Agent) Protocol Support

```python
from agent_control_plane import (
    AgentControlPlane,
    create_governed_a2a_agent,
    ActionType,
    PermissionLevel
)

# Create governed A2A agent
control_plane = AgentControlPlane()
a2a_agent = create_governed_a2a_agent(
    control_plane=control_plane,
    agent_id="my-a2a-agent",
    agent_card={
        "name": "Data Processor",
        "description": "Processes and analyzes data",
        "capabilities": ["data_processing", "analytics"]
    },
    permissions={
        ActionType.DATABASE_QUERY: PermissionLevel.READ_ONLY,
        ActionType.API_CALL: PermissionLevel.READ_WRITE,
    }
)

# Register capabilities
a2a_agent.register_capability("data_processing", handle_data_processing)

# All inter-agent communications are governed!
a2a_agent.start()
```
```

### Permission Control

```python
from agent_control_plane.agent_kernel import ActionType, PermissionLevel

# Create custom permissions
permissions = {
    ActionType.FILE_READ: PermissionLevel.READ_ONLY,
    ActionType.API_CALL: PermissionLevel.READ_WRITE,
    ActionType.CODE_EXECUTION: PermissionLevel.NONE,
}

agent = control_plane.create_agent("restricted-agent", permissions)
```

### Rate Limiting

```python
from agent_control_plane.policy_engine import ResourceQuota

# Set strict quotas
quota = ResourceQuota(
    agent_id="rate-limited-agent",
    max_requests_per_minute=10,
    max_requests_per_hour=100,
    max_concurrent_executions=2,
)

control_plane.policy_engine.set_quota("rate-limited-agent", quota)
```

### Custom Policies

```python
from agent_control_plane.agent_kernel import PolicyRule
import uuid

def validate_safe_path(request):
    """Only allow access to /data directory"""
    path = request.parameters.get('path', '')
    return path.startswith('/data/')

rule = PolicyRule(
    rule_id=str(uuid.uuid4()),
    name="safe_path_only",
    description="Restrict file access to /data directory",
    action_types=[ActionType.FILE_READ, ActionType.FILE_WRITE],
    validator=validate_safe_path,
    priority=10
)

control_plane.policy_engine.add_custom_rule(rule)
```

## Examples

Check out the `examples/` directory for more detailed examples:

- **`getting_started.py`** - Step-by-step tutorial for beginners
- **`basic_usage.py`** - Fundamental concepts and patterns
- **`advanced_features.py`** - Shadow Mode, Mute Agent, etc.
- **`use_cases.py`** - Real-world production scenarios
- **`configuration.py`** - Different agent configurations

#### The Mute Agent - Scale by Subtraction

Create agents that know when to shut up and return NULL instead of hallucinating:

```python
from agent_control_plane.mute_agent import create_mute_sql_agent
from agent_control_plane.agent_kernel import ActionType, PermissionLevel

# Create a SQL agent that ONLY executes SELECT queries
sql_config = create_mute_sql_agent("sql-bot")
permissions = {ActionType.DATABASE_QUERY: PermissionLevel.READ_ONLY}
agent = control_plane.create_agent("sql-bot", permissions)
control_plane.enable_mute_agent("sql-bot", sql_config)

# Valid: SELECT query
result = control_plane.execute_action(
    agent,
    ActionType.DATABASE_QUERY,
    {"query": "SELECT * FROM users"}
)
# ✓ Success: True

# Invalid: Destructive operation
result = control_plane.execute_action(
    agent,
    ActionType.DATABASE_QUERY,
    {"query": "DROP TABLE users"}
)
# ✗ Success: False, Error: "NULL"
# Agent returns NULL instead of trying to be "helpful"!
```

#### Shadow Mode - The Matrix for Agents

Test agent behavior without actual execution:

```python
# Enable shadow mode
control_plane = AgentControlPlane(enable_shadow_mode=True)
agent = create_standard_agent(control_plane, "test-agent")

# This looks like normal execution...
result = control_plane.execute_action(
    agent,
    ActionType.FILE_WRITE,
    {"path": "/data/important.txt", "content": "test"}
)

# But it was SIMULATED! No actual file was written.
print(result["status"])  # "simulated"
print(result["note"])    # "This was executed in SHADOW MODE..."

# Get statistics
stats = control_plane.get_shadow_statistics()
print(f"Success rate: {stats['success_rate']:.1%}")
```

#### Constraint Graphs - Multi-Dimensional Context

Define what's possible using Data, Policy, and Temporal graphs:

```python
from datetime import time

# Create control plane with constraint graphs
control_plane = AgentControlPlane(enable_constraint_graphs=True)

# Data Graph: What data exists
control_plane.add_data_table("users", {"id": "int", "name": "string"})
control_plane.add_data_path("/data/")

# Policy Graph: What rules apply
control_plane.add_policy_constraint(
    "pii_protection",
    "No PII in output",
    applies_to=["table:users"],
    rule_type="deny"
)

# Temporal Graph: What's true RIGHT NOW
control_plane.add_maintenance_window(
    "nightly_maintenance",
    start_time=time(2, 0),  # 2 AM
    end_time=time(4, 0),    # 4 AM
    blocked_actions=[ActionType.DATABASE_WRITE]
)

# The graphs enforce deterministically
# If a table isn't in the Data Graph, access is blocked
# If during maintenance window, writes are blocked
# This is ENFORCEMENT, not advisory
```

#### Supervisor Agents - Recursive Governance

Agents watching agents:

```python
from agent_control_plane.supervisor_agents import create_default_supervisor

# Create worker agents
agent1 = create_standard_agent(control_plane, "worker-1")
agent2 = create_standard_agent(control_plane, "worker-2")

# Create supervisor to watch them
supervisor = create_default_supervisor(["worker-1", "worker-2"])
control_plane.add_supervisor(supervisor)

# Agents do their work...
# (execute various actions)

# Run supervision cycle
violations = control_plane.run_supervision()

# Supervisor detects: repeated failures, excessive risk, 
# rate limit approaching, suspicious patterns, etc.
for supervisor_id, viols in violations.items():
    for v in viols:
        print(f"[{v.severity}] {v.description}")
```

#### Multi-Agent Orchestration - Coordinate Multiple Agents

Create workflows with multiple specialized agents:

```python
from agent_control_plane import (
    AgentOrchestrator,
    AgentRole,
    OrchestrationType,
    create_rag_pipeline
)

# Create orchestrator
orchestrator = AgentOrchestrator(control_plane)

# Register specialized agents
orchestrator.register_agent(
    "retriever",
    AgentRole.SPECIALIST,
    capabilities=["document_search", "vector_search"]
)

orchestrator.register_agent(
    "analyzer",
    AgentRole.SPECIALIST,
    capabilities=["data_analysis", "summarization"]
)

orchestrator.register_agent(
    "supervisor",
    AgentRole.SUPERVISOR,
    capabilities=["quality_check", "safety_check"]
)

# Create a RAG pipeline workflow
workflow = orchestrator.create_workflow("rag_pipeline", OrchestrationType.SEQUENTIAL)
orchestrator.add_agent_to_workflow(workflow.workflow_id, "retriever")
orchestrator.add_agent_to_workflow(
    workflow.workflow_id,
    "analyzer",
    dependencies={"retriever"}  # Analyzer depends on retriever
)

# Add supervisor to watch all agents
orchestrator.add_supervisor("supervisor", ["retriever", "analyzer"])

# Execute workflow
import asyncio
result = asyncio.run(orchestrator.execute_workflow(
    workflow.workflow_id,
    {"query": "What are the key findings?"}
))
print(f"Workflow completed: {result['success']}")
```

#### Governance Layer - Ethical Alignment & Privacy

Advanced safety beyond basic policies:

```python
from agent_control_plane import (
    GovernanceLayer,
    AlignmentPrinciple,
    create_default_governance
)

# Create governance layer with ethical rules
governance = create_default_governance()

# Check alignment before execution
context = {"content": "Analyze sales data"}
alignment = governance.check_alignment(context)
if not alignment["aligned"]:
    print(f"Alignment violations: {alignment['violations']}")

# Detect bias in content
text = "All engineers should be..."
bias_result = governance.detect_bias(text)
if bias_result.has_bias:
    print(f"Bias detected: {bias_result.bias_types}")
    print(f"Recommendations: {bias_result.recommendations}")

# Analyze privacy and PII
data = {"email": "user@example.com", "phone": "555-1234"}
privacy = governance.analyze_privacy(data)
print(f"Privacy level: {privacy.privacy_level.value}")
print(f"Contains PII: {privacy.contains_pii}")
print(f"Risk score: {privacy.risk_score}")
```

#### Tool Registry - Dynamic Tool Management

Extend agent capabilities with dynamic tool registration:

```python
from agent_control_plane import ToolRegistry, ToolType

registry = ToolRegistry()

# Register a custom tool
def web_search(query: str) -> dict:
    """Search the web for information"""
    # Implementation here
    return {"results": [...]}

tool_id = registry.register_tool(
    name="web_search",
    description="Search the web",
    tool_type=ToolType.SEARCH,
    handler=web_search,
    risk_level=0.3
)

# Execute the tool
result = registry.execute_tool("web_search", {"query": "AI safety"})
print(f"Search results: {result['result']}")

# Discover tools by type
search_tools = registry.get_tools_by_type(ToolType.SEARCH)
print(f"Available search tools: {len(search_tools)}")
```

## Command Line Interface

Agent Control Plane includes a CLI for common operations:

```bash
# Create an agent
python acp-cli.py agent create my-agent --role worker

# List all agents
python acp-cli.py agent list

# Inspect an agent
python acp-cli.py agent inspect my-agent

# View audit logs
python acp-cli.py audit show --limit 10 --format json

# Run safety benchmark
python acp-cli.py benchmark run
```

## Docker Deployment

Deploy Agent Control Plane in containers for production:

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Development environment with Jupyter
docker-compose --profile dev up -d acp-dev

# Distributed setup with Redis
docker-compose --profile distributed up -d
```

See [Docker Deployment Guide](docs/DOCKER_DEPLOYMENT.md) for complete instructions.

## Interactive Tutorial

Explore features hands-on with our Jupyter notebook:

```bash
# Install Jupyter
pip install jupyter

# Launch the tutorial
jupyter notebook examples/interactive_tutorial.ipynb
```

The tutorial covers:
- Agent creation and permissions
- Shadow Mode testing
- Multi-agent orchestration
- Ethical alignment and bias detection
- Privacy analysis
- Tool registry usage

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Application Layer                     │
│                    (Chat, Workflow, Tools)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Agent Control Plane                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Agent     │  │   Policy     │  │   Audit      │      │
│  │   Kernel     │◄─┤   Engine     │◄─┤   Logger     │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                     │
│  ┌──────▼───────┐  ┌──────────────┐                         │
│  │  Resource    │  │  Execution   │                         │
│  │   Manager    │◄─┤   Engine     │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    LLM (Raw Compute)                         │
│              (GPT-4, Claude, Llama, etc.)                    │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Execution Environment                       │
│         (Code, Databases, APIs, File System)                 │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Core Components

#### Agent Kernel
The kernel mediates all interactions between the LLM and execution environment:
- Permission checking with OS-like rigor
- Request validation
- Risk assessment
- Audit logging
- Session management

#### Policy Engine
Enforces governance rules deterministically:
- Rate limiting and quotas
- Custom policy rules
- Risk management
- Access control
- Compliance enforcement

#### Execution Engine
Safely executes agent actions:
- Sandboxed environments (4 levels: NONE, BASIC, STRICT, ISOLATED)
- Timeout enforcement
- Resource monitoring
- Error handling
- Transaction support

### Advanced Components

#### The Mute Agent
Implements "Scale by Subtraction" philosophy:
- Capability-based execution
- Returns NULL for out-of-scope requests instead of hallucinating
- No creativity, only precision
- Example: SQL agent that only executes SELECT queries

#### Shadow Mode
The "Matrix" for agents - simulation without execution:
- Intercepts all actions before execution
- Validates against policies without side effects
- Logs reasoning chains
- Analyzes potential impact
- Perfect for testing before production

#### Constraint Graphs
Multi-dimensional context defining the "physics" of the agent's world:
- **Data Graph**: What data resources exist and are accessible
- **Policy Graph**: What corporate rules and compliance constraints apply
- **Temporal Graph**: What is true RIGHT NOW (maintenance windows, business hours, freeze periods)
- Deterministic enforcement: LLM can think anything, but can only ACT on what graphs permit

#### Supervisor Agents
Recursive governance - agents watching agents:
- Specialized, highly constrained monitoring agents
- Detect violations, anomalies, and suspicious patterns
- Flag issues to humans
- Optional auto-remediation
- Hierarchical supervision (supervisors watching supervisors)

## Examples

### Basic Examples

Run the basic examples:

```bash
python3 examples.py
```

This demonstrates:
- Basic usage
- Permission control
- Rate limiting
- Policy enforcement
- Audit logging
- Risk management

### Advanced Examples

Run the advanced feature examples:

```bash
python3 advanced_examples.py
```

This demonstrates:
- The Mute Agent (capability-based execution)
- Shadow Mode (simulation)
- Constraint Graphs (multi-dimensional context)
- Supervisor Agents (recursive governance)
- Integrated workflows

## Testing

Run the complete test suite:

```bash
# Basic features
python3 test_control_plane.py

# Advanced features
python3 test_advanced_features.py

# Or run all tests
python3 test_control_plane.py && python3 test_advanced_features.py
```

Total: 31 tests covering all features.

## Benchmark: Comparative Safety Study

A comprehensive benchmark demonstrates the effectiveness of the Control Plane approach compared to traditional prompt-based safety.

### Running the Benchmark

```bash
python3 benchmark.py
```

### Key Results

The benchmark compares **Prompt-Based Safety (Baseline)** vs **Control Plane Governance (Experimental)** using 60 red team prompts:

| Metric | Baseline (Prompts) | Control Plane | Improvement |
|--------|-------------------|---------------|-------------|
| **Safety Violation Rate** | 26.67% | **0.00%** | ✓ 100% enforcement |
| **False Positive Rate** | 0.00% | **0.00%** | ✓ Perfect precision |
| **Avg Output Tokens** | 26.1 | **0.5** | ✓ 98.1% reduction |

**Key Findings:**
- ✓ **100% Safety Enforcement**: Control Plane blocked all 45 malicious prompts (0% SVR)
- ✓ **Zero False Positives**: All 15 valid requests were correctly allowed
- ✓ **Scale by Subtraction**: 98.1% fewer tokens (returns "NULL" instead of verbose refusals)
- ✓ **Jailbreak Immunity**: Deterministic enforcement catches prompt injection attacks that bypass prompt-based safety

The benchmark includes:
- **15 Direct Violations**: SQL injection, system commands
- **15 Prompt Injections**: Jailbreaks and instruction overrides
- **15 Contextual Confusion**: Social engineering attempts
- **15 Valid Requests**: Legitimate operations (false positive testing)

See [`benchmark/README.md`](benchmark/README.md) for detailed methodology and results.

## Demo Video

### Quick Start (2-3 minutes)

🎥 **Coming Soon**: A short video walkthrough showing:
1. Installing Agent Control Plane
2. Creating a governed agent
3. Testing safety with red team prompts
4. Viewing audit logs

*Video will be published to YouTube and embedded here*

### Full Tutorial (12 minutes)

📹 **Coming Soon**: Complete tutorial covering:
1. **Introduction** (2 min): What is Agent Control Plane?
2. **Installation** (2 min): Setup and dependencies
3. **Basic Usage** (3 min): Create your first governed agent
4. **Safety Demo** (3 min): Test against adversarial prompts
5. **Multi-Agent** (2 min): Coordinate multiple agents safely

**Planned Release**: Q1 2026

### Interactive Demos

Try these live demos in your browser:

- **[Google Colab Notebook](https://colab.research.google.com/github/imran-siddique/agent-control-plane)**: Interactive tutorial (coming soon)
- **[Jupyter Notebook](examples/)**: Local demos in `examples/` directory
- **[Streamlit App](https://huggingface.co/spaces/imran-siddique/agent-control-demo)**: Web UI demo (coming soon)

### Community Videos

Have you created a tutorial or demo? [Submit it here](https://github.com/imran-siddique/agent-control-plane/issues/new?template=community-video.md) to be featured!

---

## Use Cases

### Enterprise AI Agents
Deploy agents with strict governance for enterprise environments:
- Compliance with security policies through Constraint Graphs
- Complete audit trails for regulatory requirements
- Resource quotas to control costs
- Shadow Mode testing before production deployment

### SQL-Generating Agents
Build precise, non-creative agents:
- Mute Agent configuration for SQL-only operations
- Returns NULL for out-of-scope requests
- No hallucination or conversational pivots
- Example: Finance team data access agent

### Multi-tenant AI Platforms
Safely run multiple agents with isolation:
- Per-tenant quotas and policies
- Isolated execution environments
- Fair resource allocation
- Supervisor Agents monitoring all tenants

### Development & Testing
Experiment safely with agent capabilities:
- Shadow Mode for risk-free testing
- Sandboxed execution
- Complete reasoning telemetry
- Comprehensive logging

### Production Workflows
Run reliable, auditable agent workflows:
- Error handling and recovery
- Performance monitoring
- Traceability for debugging

## API Reference

See [architecture.md](architecture.md) for detailed architecture documentation.

### Core Classes

- `AgentControlPlane`: Main control plane interface
- `AgentKernel`: Core kernel component
- `PolicyEngine`: Policy enforcement
- `ExecutionEngine`: Safe execution
- `AgentContext`: Agent session context
- `ExecutionRequest`: Action request
- `ExecutionResult`: Action result

### New Multi-Agent & Governance Classes

- `AgentOrchestrator`: Multi-agent coordination and workflows
- `ToolRegistry`: Dynamic tool management and discovery
- `GovernanceLayer`: Ethical alignment and advanced safety
- `AgentNode`: Agent representation in orchestration graphs
- `Tool`: Tool definition with schemas and handlers

### Action Types

- `FILE_READ`: Read file operations
- `FILE_WRITE`: Write file operations
- `CODE_EXECUTION`: Execute code
- `API_CALL`: Make API calls
- `DATABASE_QUERY`: Query databases
- `DATABASE_WRITE`: Write to databases
- `WORKFLOW_TRIGGER`: Trigger workflows

### Permission Levels

- `NONE`: No access
- `READ_ONLY`: Read-only access
- `READ_WRITE`: Read and write access
- `ADMIN`: Full administrative access

## Best Practices

1. **Start with minimal permissions**: Grant only what's needed
2. **Use rate limits**: Prevent runaway agents
3. **Enable audit logging**: Track all agent actions
4. **Test policies**: Validate governance rules work as expected
5. **Monitor resource usage**: Watch for anomalies
6. **Regular policy reviews**: Keep policies up to date

## Security Considerations

- Default policies block system file access
- Credentials should never be in parameters
- High-risk actions require elevated permissions
- All actions are audited
- Sandboxed execution by default

## Future Enhancements

Recent additions (2025):
- [x] Multi-agent orchestration with workflows
- [x] Dynamic tool registry with auto-discovery
- [x] Governance layer with ethical alignment
- [x] Bias detection and privacy analysis
- [x] Docker deployment with docker-compose
- [x] Command-line interface (CLI)
- [x] Interactive Jupyter notebooks

Planned enhancements:
- [ ] Kubernetes deployment manifests and Helm charts
- [ ] Integration with external policy engines (OPA, Cedar)
- [ ] Real-time monitoring dashboard with metrics
- [ ] Machine learning-based anomaly detection
- [ ] Automatic policy generation from past behavior
- [ ] Integration with secrets management systems (Vault, AWS Secrets Manager)
- [ ] Enhanced container-based sandboxing with gVisor
- [ ] Transaction rollback for database operations
- [ ] Federated learning support for privacy-preserving models
- [ ] Integration with AdvBench and WildGuard datasets

## How This Differs from Other Approaches

### vs. "Manager" Models (e.g., Gas Town)

Projects like Steve Yegge's Gas Town use a "City" metaphor where a "Mayor" agent orchestrates "Worker" agents to maximize coding throughput. This is brilliant for velocity.

**The Difference:**
- **Gas Town solves for COORDINATION** (getting things done fast)
- **Agent Control Plane solves for CONTAINMENT** (ensuring things are safe)
- In an enterprise, you don't just need a Manager; you need a Compliance Officer who can pull the plug

The Agent Control Plane complements coordination systems by providing the safety layer.

### vs. "Guardrails" Models (e.g., NeMo, LlamaGuard)

Most current safety tools operate as "sidecars" that check input/output for toxicity, PII, or harmful content. They are largely text-based and probabilistic.

**The Difference:**
- **Guardrails are ADVISORY or REACTIVE** (sanitizing output after generation)
- **Agent Control Plane is ARCHITECTURAL** (preventing action at the kernel level)
- A guardrail scrubs a bad SQL query; a Control Plane ensures the agent never had the connection string to begin with
- Guardrails work on content; Control Plane works on capabilities and execution

### vs. "Tool Directory" Models

Recent academic papers propose "Control Planes" that act as a phonebook, helping agents find the right tools.

**The Difference:**
- **Tool Directory is SERVICE DISCOVERY** (finding what's available)
- **Agent Control Plane is a KERNEL** (strict enforcement of boundaries)
- The Linux Kernel doesn't just "help" processes find memory; it strictly enforces that Process A cannot touch Process B's memory
- We need that same hardness for Agents

### The Agent Control Plane Approach

**Deterministic Enforcement, Not Advisory Hints:**
- LLM can "think" whatever it wants
- But it can only ACT on what the Control Plane permits
- Constraint Graphs define the "physics" of the agent's world
- Shadow Mode lets you test everything before production
- Supervisor Agents provide recursive oversight

This is **systems engineering** for AI, not prompt engineering.

## Research & Academic Grounding

The Agent Control Plane is built on peer-reviewed research and industry best practices, not just intuition.

### Key Research Foundations

Our design is informed by academic research across multiple domains:

1. **Agent Safety**: "A Safety Framework for Real-World Agentic Systems" (arXiv:2511.21990) - contextual risk management
2. **Multi-Agent Systems**: "Multi-Agent Systems: A Survey" (arXiv:2308.05391) - hierarchical control, cascade failure prevention
3. **Security**: "MAESTRO: A Threat Modeling Framework for Agentic AI" (CSA, 2025) - threat vectors and defenses
4. **Governance**: "Practices for Governing Agentic AI Systems" (OpenAI, 2023) - pre/post-deployment practices
5. **Privacy**: "Privacy in Agentic Systems" (arXiv:2409.1087) - differential privacy, secure computation
6. **Evaluation**: "Evaluating Agentic AI" (WEF, 2025) - standardized metrics and benchmarks

### Research-Backed Design Decisions

- **Deterministic enforcement** over probabilistic filtering (OS security model)
- **Layered defense** architecture (defense-in-depth from security research)
- **Capability-based security** (principle of least privilege)
- **Simulation before execution** (risk-free pre-deployment testing)
- **Multi-dimensional context** (ABAC - NIST SP 800-162)

### Benchmark Methodology

Our comparative safety study follows research standards:
- Dataset based on "Red-Teaming Agentic AI" taxonomy (60 prompts across 4 categories)
- Metrics follow "Evaluating Agentic AI" frameworks (SVR, FPR, token efficiency)
- Baseline comparison with industry-standard prompt-based safety

### Academic Resources

- **[Research Foundation](docs/RESEARCH_FOUNDATION.md)** - Detailed research citations and applications
- **[Bibliography](docs/BIBLIOGRAPHY.md)** - Complete list of 26+ research papers and reports
- **[Benchmark Methodology](benchmark/README.md)** - Research-backed evaluation approach

### Citation

If you use Agent Control Plane in research:

```bibtex
@software{agent_control_plane,
  title = {Agent Control Plane: A Governance Layer for Autonomous AI Agents},
  author = {Agent Control Plane Contributors},
  year = {2025},
  url = {https://github.com/imran-siddique/agent-control-plane},
  note = {MIT License}
}
```

## Community & Support

### Get Involved

Join our growing community:

- 🌟 **[Star the repository](https://github.com/imran-siddique/agent-control-plane)** to show support
- 💬 **[GitHub Discussions](https://github.com/imran-siddique/agent-control-plane/discussions)** - Ask questions, share ideas, showcase projects
- 🐛 **[Issue Tracker](https://github.com/imran-siddique/agent-control-plane/issues)** - Report bugs or request features
- 📚 **[Documentation](docs/)** - Comprehensive guides and API reference
- 🗺️ **[Roadmap](ROADMAP.md)** - See what's planned for 2026
- 💡 **[Support Guide](SUPPORT.md)** - How to get help

### Roadmap Highlights

See [ROADMAP.md](ROADMAP.md) for the complete 2026 roadmap. Key upcoming features:

**Q1 2026** (Current)
- ✅ PyPI distribution (`pip install agent-control-plane`)
- ✅ GitHub releases and versioning
- ✅ Community forum (GitHub Discussions)
- 🚧 Documentation portal (ReadTheDocs/GitHub Pages)

**Q2 2026** - Advanced Intelligence
- ML-based intent classification
- Constitutional fine-tuning hooks (RLHF/LoRA)
- Multi-turn red-teaming datasets
- Privacy enhancements (differential privacy, federated learning)

**Q3 2026** - Multimodal & Ecosystem
- Production-ready vision and audio governance
- Vector store integrations (Pinecone, Weaviate, Qdrant)
- Advanced RAG patterns with fact verification

**Q4 2026** - Scale & Operations
- Grafana/Prometheus dashboard templates
- Streamlit interactive governance UI
- Tool marketplace (200+ governed tools)

### Success Metrics & Goals

**2026 Targets:**
- 1,000+ GitHub stars
- 10,000+ monthly PyPI downloads
- 50+ production deployments
- 20+ active contributors
- 10+ academic citations

### Stay Connected

- Watch the repository for updates and releases
- Follow project announcements in Discussions
- Contribute to help us reach our goals!

## Contributing

We welcome contributions! The Agent Control Plane is designed to be production-ready and contributor-friendly.

### Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/agent-control-plane.git`
3. Install in development mode: `pip install -e ".[dev]"`
4. Create a branch: `git checkout -b feature/your-feature-name`

### Running Tests

```bash
# Run all tests
python -m unittest discover -s tests -p 'test_*.py' -v

# Run specific test file
python -m unittest tests/test_control_plane.py

# Run specific test
python -m unittest tests.test_control_plane.TestAgentKernel.test_create_agent_session
```

### Project Structure

- `src/agent_control_plane/` - Main package source code
- `tests/` - Test suite (unittest framework)
- `examples/` - Example scripts and use cases
- `docs/` - Documentation and guides
- `.github/workflows/` - CI/CD configuration

### Guidelines

- Follow existing code style and patterns
- Add tests for new features
- Update documentation as needed
- Keep changes focused and minimal
- Write clear commit messages

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Testing

The project uses Python's built-in `unittest` framework. All tests are located in the `tests/` directory.

### Test Coverage

- **Core functionality tests**: `test_control_plane.py`
- **Advanced features tests**: `test_advanced_features.py`

Current test coverage: **31 tests** covering:
- Agent creation and lifecycle
- Permission management
- Policy enforcement
- Rate limiting
- Shadow mode simulation
- Mute agent capabilities
- Constraint graphs
- Supervisor agents
- Audit logging

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Quick Start Guide](docs/guides/QUICKSTART.md)** - Get up and running quickly
- **[Implementation Guide](docs/guides/IMPLEMENTATION.md)** - Detailed implementation details
- **[Philosophy](docs/guides/PHILOSOPHY.md)** - Core principles and design philosophy
- **[Architecture](docs/architecture/architecture.md)** - System architecture overview
- **[Research Foundation](docs/RESEARCH_FOUNDATION.md)** - Academic grounding and citations
- **[Bibliography](docs/BIBLIOGRAPHY.md)** - Complete list of research references

## License

MIT License - See LICENSE file for details