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

## Core Components

| Package | Description |
|---------|-------------|
| [`control-plane`](packages/control-plane/) | Kernel with policy engine, signals, VFS |
| [`iatp`](packages/iatp/) | Inter-Agent Trust Protocol for multi-agent |
| [`cmvk`](packages/cmvk/) | Cross-Model Verification (consensus across LLMs) |
| [`amb`](packages/amb/) | Agent Message Bus |
| [`observability`](packages/observability/) | Prometheus metrics + OpenTelemetry |
| [`mcp-kernel-server`](packages/mcp-kernel-server/) | MCP server integration |

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

The `examples/` directory contains working demos with full observability:

| Demo | Description | Command |
|------|-------------|---------|
| [carbon-auditor](examples/carbon-auditor/) | Multi-model verification | `cd examples/carbon-auditor && docker-compose up` |
| [grid-balancing](examples/grid-balancing/) | Multi-agent coordination (100 agents) | `cd examples/grid-balancing && docker-compose up` |
| [defi-sentinel](examples/defi-sentinel/) | Real-time attack detection | `cd examples/defi-sentinel && docker-compose up` |
| [pharma-compliance](examples/pharma-compliance/) | Document analysis | `cd examples/pharma-compliance && docker-compose up` |

Each demo includes:
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

## Architecture

```
agent-os/
├── packages/
│   ├── primitives/          # Base types
│   ├── cmvk/                 # Cross-model verification  
│   ├── iatp/                 # Inter-agent trust
│   ├── amb/                  # Message bus
│   ├── control-plane/        # THE KERNEL
│   ├── scak/                 # Self-correction
│   ├── mcp-kernel-server/    # MCP integration
│   └── observability/        # Prometheus + OTel
├── examples/                 # Working demos
├── papers/                   # Research papers
└── docs/                     # Documentation
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

See [MCP server documentation](packages/mcp-kernel-server/README.md).

---

## Documentation

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
- Stateless architecture (MCP June 2026 compliant)
- AGENTS.md compatibility (OpenAI/Anthropic standard)

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
