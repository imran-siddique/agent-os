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

| Demo | Description |
|------|-------------|
| [carbon-auditor](examples/carbon-auditor/) | Multi-model verification example |
| [grid-balancing](examples/grid-balancing/) | Multi-agent coordination |
| [defi-sentinel](examples/defi-sentinel/) | Real-time monitoring |
| [pharma-compliance](examples/pharma-compliance/) | Document analysis |

```bash
# Run a demo
python examples/carbon-auditor/demo.py
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

## Documentation

- [Quickstart Guide](docs/quickstart.md)
- [Kernel Internals](docs/kernel-internals.md)
- [Architecture Overview](docs/architecture.md)
- [RFC-001: IATP](docs/rfcs/RFC-001-IATP.md)
- [RFC-002: Agent VFS](docs/rfcs/RFC-002-Agent-VFS.md)

---

## Status

This is a research project exploring kernel concepts for AI agent governance. The code is functional but not production-hardened.

**What works:**
- Policy engine with signal-based enforcement
- VFS for structured agent memory
- Cross-model verification (CMVK)
- Inter-agent trust protocol (IATP)
- MCP server integration
- Prometheus/OpenTelemetry observability

**What's experimental:**
- The "0% violation" claim needs formal verification
- Benchmark numbers need independent reproduction
- Integration with LangChain/CrewAI is basic

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
