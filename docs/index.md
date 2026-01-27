# Agent OS Documentation

Welcome to the Agent OS documentation. Agent OS is a kernel architecture for governing autonomous AI agents with deterministic policy enforcement.

## Quick Navigation

### 🚀 Getting Started

| Guide | Time | Description |
|-------|------|-------------|
| [5-Minute Quickstart](tutorials/getting-started.md) | 5 min | Get running immediately |
| [First Governed Agent](tutorials/first-governed-agent.md) | 15 min | Build a complete agent |
| [Cheatsheet](cheatsheet.md) | - | Quick reference card |

### 📚 Tutorials

- [Using Message Bus Adapters](tutorials/message-bus-adapters.md) - Connect agents with Redis, Kafka, NATS
- [Creating Custom Tools](tutorials/custom-tools.md) - Build safe tools for agents

### 🏗️ Architecture

- [Architecture Overview](architecture.md) - System design and concepts
- [Kernel Internals](kernel-internals.md) - How the kernel works
- [CMVK Algorithm](cmvk-algorithm.md) - Cross-model verification

### 🔧 Reference

- [Framework Integrations](integrations.md) - LangChain, OpenAI, CrewAI
- [Dependencies](dependencies.md) - Package dependencies
- [Security Specification](security-spec.md) - Security model

### 📋 RFCs

- [RFC-003: Agent Signals](rfcs/RFC-003-Agent-Signals.md) - POSIX-style signals
- [RFC-004: Agent Primitives](rfcs/RFC-004-Agent-Primitives.md) - Core primitives

### 🎯 Case Studies

- [Carbon Auditor](case-studies/) - Fraud detection example
- [DeFi Sentinel](case-studies/) - Attack detection
- [Grid Balancing](case-studies/) - Multi-agent coordination

---

## Installation

```bash
# Core package
pip install agent-os

# With all features
pip install agent-os[full]
```

## One-Command Quickstart

**macOS/Linux:**
```bash
curl -sSL https://get.agent-os.dev | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://get.agent-os.dev/win | iex
```

## Hello World

```python
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str):
    return f"Processed: {task}"

# Run with kernel governance
result = await kernel.execute(my_agent, "analyze data")
```

## Key Concepts

### Kernel vs User Space

```
┌─────────────────────────────────────────────────────────┐
│              USER SPACE (Agent Code)                    │
│   Your agent code runs here. Can crash, hallucinate.   │
├─────────────────────────────────────────────────────────┤
│              KERNEL SPACE (Agent OS)                    │
│   Policy Engine checks every action before execution    │
│   If policy violated → SIGKILL (non-catchable)         │
└─────────────────────────────────────────────────────────┘
```

### Signals

Agent OS uses POSIX-style signals for control:

| Signal | Description |
|--------|-------------|
| `SIGKILL` | Terminate immediately (cannot be caught) |
| `SIGSTOP` | Pause for human review |
| `SIGCONT` | Resume execution |

### Policies

Policies define what agents can and cannot do:

```yaml
policies:
  - name: read_only
    deny:
      - action: file_write
      - action: database_write
```

## IDE Extensions

| IDE | Status | Link |
|-----|--------|------|
| VS Code | ✅ Available | [Marketplace](extensions/vscode/) |
| JetBrains | ✅ Available | [Plugin](extensions/jetbrains/) |
| Cursor | ✅ Available | [Extension](extensions/cursor/) |
| GitHub Copilot | ✅ Available | [Extension](extensions/copilot/) |

## Policy Templates

Pre-built templates for common use cases:

| Template | Use Case |
|----------|----------|
| [secure-coding](../templates/policies/secure-coding.yaml) | General development |
| [data-protection](../templates/policies/data-protection.yaml) | PII handling |
| [enterprise](../templates/policies/enterprise.yaml) | Production deployments |

```bash
# Use a template
agentos init my-project --template secure-coding
```

## Support

- [GitHub Issues](https://github.com/imran-siddique/agent-os/issues)
- [Discussions](https://github.com/imran-siddique/agent-os/discussions)
- [Contributing Guide](../CONTRIBUTING.md)

---

<div align="center">

**Kernel-level safety for AI agents.**

[GitHub](https://github.com/imran-siddique/agent-os) · [Examples](../examples/)

</div>
