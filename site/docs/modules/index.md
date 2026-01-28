---
layout: default
title: Modules
parent: Documentation
nav_order: 4
has_children: true
permalink: /docs/modules/
description: "Agent OS module documentation: CMVK, EMK, IATP, AMB, and more."
---

# Modules

Agent OS is built from modular components. Each module solves a specific problem and can be used independently.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Applications                                  │
│  ├─ SCAK (Self-Correcting Agent Kernel)                │
│  ├─ MUTE-Agent (Face/Hands Architecture)               │
│  └─ ATR (Agent Tool Registry)                          │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Framework (THE KERNEL)                        │
│  ├─ Control Plane (Policy Engine, Signals, VFS)        │
│  └─ Observability (Prometheus, OpenTelemetry)          │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Infrastructure                                │
│  ├─ CMVK (Cross-Model Verification)                    │
│  ├─ IATP (Inter-Agent Trust Protocol)                  │
│  ├─ EMK (Episodic Memory Kernel)                       │
│  └─ AMB (Agent Message Bus)                            │
├─────────────────────────────────────────────────────────┤
│  Layer 1: Primitives                                    │
│  └─ Base types, failures, core abstractions            │
└─────────────────────────────────────────────────────────┘
```

---

## Core Modules

### [CMVK - Cross-Model Verification Kernel](/docs/modules/cmvk/)

Detect hallucinations by comparing outputs across multiple LLMs.

```python
from cmvk import verify

score = verify("The capital of France is Paris.", 
               "Paris is the capital city of France.")
print(f"Drift: {score.drift_score}")  # 0.0 = identical
```

**Key Features**:
- Semantic drift detection
- Multi-model consensus verification
- Batch verification
- Hallucination detection

[Read CMVK Documentation →](/docs/modules/cmvk/)

---

### [EMK - Episodic Memory Kernel](/docs/modules/emk/)

Immutable, append-only ledger of agent experiences.

```python
from emk import Episode, FileAdapter

store = FileAdapter("memory.jsonl")
episode = Episode(
    goal="Query user data",
    action="SELECT * FROM users",
    result="200 rows",
    reflection="Query was fast"
)
store.store(episode)
```

**Key Features**:
- Immutable episodes
- Semantic search/retrieval
- Memory compression (sleep cycle)
- Negative memory (anti-patterns)

[Read EMK Documentation →](/docs/modules/emk/)

---

### [IATP - Inter-Agent Trust Protocol](/docs/modules/iatp/)

Cryptographic signing and verification for multi-agent systems.

```python
from iatp import AgentIdentity, SignedMessage, TrustRegistry

agent = AgentIdentity.create("agent-001", "My Agent", ["capabilities"])
message = SignedMessage.create(sender=agent, recipient_id="agent-002", content={...})

registry = TrustRegistry()
registry.register(agent, TrustLevel.HIGH)
result = registry.verify(message)
```

**Key Features**:
- Agent identity management
- Message signing/verification
- Trust levels and revocation
- Secure multi-agent communication

[Read IATP Documentation →](/docs/modules/iatp/)

---

### [AMB - Agent Message Bus](/docs/modules/amb/)

Decoupled communication between agents.

```python
from amb_core import MessageBus
from amb_core.adapters import RedisBroker

broker = RedisBroker(url="redis://localhost:6379")
bus = MessageBus(broker)

await bus.publish("agent.tasks", message)
await bus.subscribe("agent.results", handler)
```

**Key Features**:
- Multiple backends (Redis, Kafka, NATS, SQS)
- Pub/sub messaging
- Request/reply patterns
- Message routing

[Read AMB Documentation →](/docs/modules/amb/)

---

### [Control Plane](/docs/modules/control-plane/)

The kernel itself—policy engine, signals, VFS.

```python
from agent_os import KernelSpace, AgentSignal

kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task): ...

# Signal control
dispatcher.signal(agent_id, AgentSignal.SIGSTOP)
```

**Key Features**:
- Policy enforcement
- Signal dispatch (SIGKILL, SIGSTOP, SIGCONT)
- Virtual file system (VFS)
- Audit logging

[Read Control Plane Documentation →](/docs/modules/control-plane/)

---

### [Observability](/docs/modules/observability/)

Prometheus metrics and OpenTelemetry tracing.

```python
from agent_os.observability import enable_metrics, enable_tracing

enable_metrics(port=9090)
enable_tracing()
```

**Key Features**:
- Prometheus metrics export
- OpenTelemetry tracing
- Pre-built Grafana dashboards
- Jaeger integration

[Read Observability Documentation →](/docs/modules/observability/)

---

## Application Modules

### [SCAK - Self-Correcting Agent Kernel](/docs/modules/scak/)
Verification-driven correction loops for agents.

### [ATR - Agent Tool Registry](/docs/modules/atr/)
Runtime tool discovery and safe tool plugins.

### [CAAS - Context-as-a-Service](/docs/modules/caas/)
RAG routing and context management.

### [MCP Kernel Server](/docs/modules/mcp/)
MCP server for Claude Desktop integration.

---

## Module Independence

Each module is designed to be:
- **Independent**: Can be used standalone
- **Composable**: Works well with other modules
- **Zero cross-dependencies**: Primitives don't depend on each other

Install only what you need:
```bash
pip install agent-os[cmvk]    # Just CMVK
pip install agent-os[iatp]    # Just IATP
pip install agent-os[full]    # Everything
```

---

## Next Steps

- [5-Minute Quickstart](/docs/tutorials/quickstart/) — Get started
- [Architecture Overview](/docs/concepts/) — Understand the design
- [API Reference](/docs/api/) — Detailed API docs
