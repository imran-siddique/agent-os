<div align="center">

# Agent OS

**A kernel architecture for governing autonomous AI agents**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)

</div>

---

## What is Agent OS?

Agent OS applies operating system concepts to AI agent governance. Instead of relying on prompts to enforce safety ("please don't do dangerous things"), it provides kernel-level enforcement where policy violations are blocked before execution.

```
┌─────────────────────────────────────────────────────────┐
│              USER SPACE (Agent Code)                    │
│   Your agent code runs here. The kernel intercepts      │
│   actions before they execute.                          │
├─────────────────────────────────────────────────────────┤
│              KERNEL SPACE                               │
│   Policy Engine │ Flight Recorder │ Signal Dispatch     │
│   Actions are checked against policies before execution │
└─────────────────────────────────────────────────────────┘
```

## The Idea

**Prompt-based safety** asks the LLM to follow rules. The LLM decides whether to comply.

**Kernel-based safety** intercepts actions before execution. The policy engine decides, not the LLM.

This is the same principle operating systems use: applications request resources, the kernel grants or denies access based on permissions.

---

## Architecture

```
agent-os/
├── modules/                  # OS Modules (like Linux kernel modules)
│   ├── primitives/           # Layer 1: Base types and failures
│   ├── cmvk/                 # Layer 2: Cross-model verification
│   ├── amb/                  # Layer 2: Agent message bus
│   ├── iatp/                 # Layer 2: Inter-agent trust protocol
│   ├── emk/                  # Layer 2: Episodic memory kernel
│   ├── control-plane/        # Layer 3: THE KERNEL
│   ├── observability/        # Layer 3: Prometheus + OpenTelemetry
│   ├── scak/                 # Layer 4: Self-correcting agent kernel
│   ├── mute-agent/           # Layer 4: Face/Hands agent architecture
│   ├── atr/                  # Layer 4: Agent tool registry
│   ├── caas/                 # Layer 4: Context-as-a-Service
│   └── mcp-kernel-server/    # Integration: MCP for Claude Desktop
├── extensions/               # IDE & CLI Extensions
│   ├── vscode/               # VS Code extension
│   ├── cursor/               # Cursor IDE extension
│   ├── copilot/              # GitHub Copilot integration
│   └── github-cli/           # gh CLI extension
├── src/                      # Core Python package (agent_os)
├── examples/                 # Working demos with observability
├── docs/                     # Documentation
└── papers/                   # Research papers
```

---

## Core Modules

| Module | Layer | Description |
|--------|-------|-------------|
| [`primitives`](modules/primitives/) | 1 | Base types and failure modes |
| [`cmvk`](modules/cmvk/) | 2 | Cross-model verification (consensus across LLMs) |
| [`amb`](modules/amb/) | 2 | Agent message bus (decoupled communication) |
| [`iatp`](modules/iatp/) | 2 | Inter-agent trust protocol (sidecar-based) |
| [`emk`](modules/emk/) | 2 | Episodic memory kernel (append-only ledger) |
| [`control-plane`](modules/control-plane/) | 3 | **THE KERNEL** - Policy engine, signals, VFS |
| [`observability`](modules/observability/) | 3 | Prometheus metrics + OpenTelemetry tracing |
| [`scak`](modules/scak/) | 4 | Self-correcting agent kernel |
| [`mute-agent`](modules/mute-agent/) | 4 | Decoupled reasoning/execution architecture |
| [`atr`](modules/atr/) | 4 | Agent tool registry (runtime discovery) |
| [`caas`](modules/caas/) | 4 | Context-as-a-Service (RAG routing) |
| [`mcp-kernel-server`](modules/mcp-kernel-server/) | Int | MCP server for Claude Desktop |

---

## IDE & CLI Extensions

| Extension | Description |
|-----------|-------------|
| [`vscode`](extensions/vscode/) | VS Code extension with real-time policy checks |
| [`jetbrains`](extensions/jetbrains/) | IntelliJ, PyCharm, WebStorm plugin |
| [`cursor`](extensions/cursor/) | Cursor IDE extension (Composer integration) |
| [`copilot`](extensions/copilot/) | GitHub Copilot safety layer |
| [`github-cli`](extensions/github-cli/) | `gh agent-os` CLI extension |

---

## Install

```bash
pip install agent-os
```

Or with optional components:

```bash
pip install agent-os[cmvk]           # + cross-model verification
pip install agent-os[iatp]           # + inter-agent trust
pip install agent-os[observability]  # + Prometheus/OpenTelemetry
pip install agent-os[full]           # Everything
```

### One-Command Quickstart

**macOS/Linux:**
```bash
curl -sSL https://raw.githubusercontent.com/imran-siddique/agent-os/main/scripts/quickstart.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/imran-siddique/agent-os/main/scripts/quickstart.ps1 | iex
```

---

## Quick Example

```python
from agent_os import KernelSpace

# Create kernel with policy
kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str):
    # Your LLM code here
    return llm.generate(task)

# Actions are checked against policies
result = await kernel.execute(my_agent, "analyze this data")
```

---

## POSIX-Inspired Primitives

Agent OS borrows concepts from POSIX operating systems:

| Concept | POSIX | Agent OS |
|---------|-------|----------|
| Process control | `SIGKILL`, `SIGSTOP` | `AgentSignal.SIGKILL`, `AgentSignal.SIGSTOP` |
| Filesystem | `/proc`, `/tmp` | VFS with `/mem/working`, `/mem/episodic` |
| IPC | Pipes (`\|`) | Typed IPC pipes between agents |
| Syscalls | `open()`, `read()` | `kernel.execute()` |

### Signals

```python
from agent_os import SignalDispatcher, AgentSignal

dispatcher.signal(agent_id, AgentSignal.SIGSTOP)  # Pause
dispatcher.signal(agent_id, AgentSignal.SIGCONT)  # Resume
dispatcher.signal(agent_id, AgentSignal.SIGKILL)  # Terminate
```

### VFS (Virtual File System)

```python
from agent_os import AgentVFS

vfs = AgentVFS(agent_id="agent-001")
vfs.write("/mem/working/task.txt", "Current task")
vfs.read("/policy/rules.yaml")  # Read-only from user space
```

---

## Framework Integrations

Wrap existing frameworks with Agent OS governance:

```python
# LangChain
from agent_os.integrations import LangChainKernel
governed = LangChainKernel().wrap(my_chain)

# OpenAI Assistants
from agent_os.integrations import OpenAIKernel
governed = OpenAIKernel().wrap_assistant(assistant, client)

# Semantic Kernel
from agent_os.integrations import SemanticKernelWrapper
governed = SemanticKernelWrapper().wrap(sk_kernel)

# CrewAI
from agent_os.integrations import CrewAIKernel
governed = CrewAIKernel().wrap(my_crew)
```

See [integrations documentation](docs/integrations.md) for full details.

---

## How It Differs from LangChain/CrewAI

LangChain and CrewAI are frameworks for building agents. Agent OS is infrastructure for governing them.

| | LangChain/CrewAI | Agent OS |
|---|------------------|----------|
| **Purpose** | Build agents | Govern agents |
| **Layer** | Application | Infrastructure |
| **Safety** | Prompt-based | Kernel-enforced |

You can use them together:

```python
from langchain.agents import AgentExecutor
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

@kernel.govern
async def my_langchain_agent(task: str):
    return agent_executor.invoke({"input": task})
```

---

## Examples

The `examples/` directory contains working demos:

### Getting Started

| Demo | Description | Command |
|------|-------------|---------|
| [hello-world](examples/hello-world/) | Simplest example (15 lines) | `cd examples/hello-world && python agent.py` |
| [chat-agent](examples/chat-agent/) | Interactive chatbot with memory | `cd examples/chat-agent && python chat.py` |
| [tool-using-agent](examples/tool-using-agent/) | Agent with safe tools | `cd examples/tool-using-agent && python agent.py` |

### Production Demos (with Observability)

| Demo | Description | Command |
|------|-------------|---------|
| [carbon-auditor](examples/carbon-auditor/) | Multi-model verification | `cd examples/carbon-auditor && docker-compose up` |
| [grid-balancing](examples/grid-balancing/) | Multi-agent coordination (100 agents) | `cd examples/grid-balancing && docker-compose up` |
| [defi-sentinel](examples/defi-sentinel/) | Real-time attack detection | `cd examples/defi-sentinel && docker-compose up` |
| [pharma-compliance](examples/pharma-compliance/) | Document analysis | `cd examples/pharma-compliance && docker-compose up` |

Each production demo includes:
- **Grafana dashboard** on port 300X
- **Prometheus metrics** on port 909X  
- **Jaeger tracing** on port 1668X

```bash
# Run carbon auditor with full observability
cd examples/carbon-auditor
cp .env.example .env  # Optional: add API keys
docker-compose up

# Open dashboards
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:16686 # Jaeger traces
```

---

## Safe Tool Plugins

Agent OS includes pre-built safe tools for agents:

```python
from atr.tools.safe import create_safe_toolkit

toolkit = create_safe_toolkit("standard")

# Available tools
http = toolkit["http"]        # Rate-limited HTTP with domain whitelisting
files = toolkit["files"]      # Sandboxed file reader
calc = toolkit["calculator"]  # Safe math (no eval)
json = toolkit["json"]        # Safe JSON/YAML parsing
dt = toolkit["datetime"]      # Timezone-aware datetime
text = toolkit["text"]        # Text processing

# Use a tool
result = await http.get("https://api.github.com/users/octocat")
```

See [Creating Custom Tools](docs/tutorials/custom-tools.md) for more.

---

## Message Bus Adapters

Connect agents using various message brokers:

```python
from amb_core.adapters import RedisBroker, KafkaBroker, NATSBroker

# Redis (low latency)
broker = RedisBroker(url="redis://localhost:6379")

# Kafka (high throughput)
broker = KafkaBroker(bootstrap_servers="localhost:9092")

# NATS (cloud-native)
broker = NATSBroker(servers=["nats://localhost:4222"])

# Also: AzureServiceBusBroker, AWSSQSBroker
```

See [Message Bus Adapters Guide](docs/tutorials/message-bus-adapters.md) for details.

---

## CLI Tool

Agent OS includes a CLI for terminal workflows:

```bash
# Check files for safety violations
agentos check src/app.py

# Check staged git files (pre-commit)
agentos check --staged

# Multi-model code review
agentos review src/app.py --cmvk

# Install git pre-commit hook
agentos install-hooks

# Initialize Agent OS in project
agentos init
```

---

## MCP Integration (Claude Desktop)

Agent OS provides an MCP server for Claude Desktop integration:

```bash
# Install
pip install agent-os[mcp]

# Run MCP server
mcp-kernel-server --stdio

# Or add to claude_desktop_config.json:
{
  "mcpServers": {
    "agent-os": {
      "command": "mcp-kernel-server",
      "args": ["--stdio"]
    }
  }
}
```

Exposes tools: `cmvk_verify`, `kernel_execute`, `iatp_sign`, `iatp_verify`

See [MCP server documentation](modules/mcp-kernel-server/README.md).

---

## Documentation

### Tutorials
- [5-Minute Getting Started](docs/tutorials/getting-started.md) - Get running fast
- [Building Your First Governed Agent](docs/tutorials/first-governed-agent.md) - Complete walkthrough
- [Using Message Bus Adapters](docs/tutorials/message-bus-adapters.md) - Connect agents
- [Creating Custom Tools](docs/tutorials/custom-tools.md) - Build safe tools
- [Cheatsheet](docs/cheatsheet.md) - Quick reference

### Reference
- [Quickstart Guide](docs/quickstart.md) - 60 seconds to first agent
- [Framework Integrations](docs/integrations.md) - LangChain, OpenAI, etc.
- [Kernel Internals](docs/kernel-internals.md) - How the kernel works
- [Architecture Overview](docs/architecture.md) - System design
- [CMVK Algorithm](docs/cmvk-algorithm.md) - Cross-model verification
- [RFC-003: Agent Signals](docs/rfcs/RFC-003-Agent-Signals.md) - POSIX-style signals
- [RFC-004: Agent Primitives](docs/rfcs/RFC-004-Agent-Primitives.md) - Core primitives

---

## Status

This is a research project exploring kernel concepts for AI agent governance. The code is functional but evolving.

**What works:**
- Policy engine with signal-based enforcement (SIGKILL, SIGSTOP, SIGCONT)
- VFS for structured agent memory
- Cross-model verification (CMVK) with drift detection
- Inter-agent trust protocol (IATP) with cryptographic signing
- MCP server integration (Claude Desktop compatible)
- Prometheus/OpenTelemetry observability with pre-built dashboards
- Framework integrations: LangChain, CrewAI, AutoGen, OpenAI Assistants, Semantic Kernel
- IDE extensions: VS Code, Cursor, GitHub Copilot
- CLI tool with pre-commit hooks
- Stateless architecture (MCP June 2026 compliant)
- AGENTS.md compatibility (OpenAI/Anthropic standard)
- **Message bus adapters: Redis, Kafka, RabbitMQ, NATS, Azure Service Bus, AWS SQS**
- **Safe tool plugins: HTTP client, file reader, calculator, JSON parser, datetime, text**

**What's experimental:**
- The "0% violation" claim needs formal verification
- Benchmark numbers need independent reproduction
- Some integrations are basic wrappers

---

## Contributing

```bash
git clone https://github.com/imran-siddique/agent-os.git
cd agent-os
pip install -e ".[dev]"
pytest
```

---

## License

MIT - See [LICENSE](LICENSE)

---

<div align="center">

**Exploring kernel concepts for AI agent safety.**

[GitHub](https://github.com/imran-siddique/agent-os) · [Docs](docs/)

</div>
