# AMB - Agent Message Bus

[![PyPI version](https://badge.fury.io/py/amb-core.svg)](https://badge.fury.io/py/amb-core)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/imran-siddique/amb/actions/workflows/ci.yml/badge.svg)](https://github.com/imran-siddique/amb/actions/workflows/ci.yml)

**Broker-agnostic message transport for decoupled agent communication. Part of the Agent OS ecosystem.**

## Why AMB?

In multi-agent systems, tight coupling between agents creates dependency graphs that scale exponentially with system size. When Agent A must know about Agent B, C, and D to communicate, the system becomes rigid and unmaintainable.

We built `amb` because **direct agent coupling creates spaghetti code**. The solution: **Scale by Subtraction**. By removing the requirement for agents to know about each other, we eliminate O(n²) dependencies and replace them with O(1) broadcast semantics. Agents emit signals (`"I am thinking"`, `"I need verification"`) without knowing who listens. The bus stays dumb and fast—it just transports the envelope.



## Installation

```bash
pip install amb-core
```

For production deployments with Redis, RabbitMQ, or Kafka:
```bash
pip install amb-core[redis]      # Redis support
pip install amb-core[rabbitmq]   # RabbitMQ support  
pip install amb-core[kafka]      # Kafka support
pip install amb-core[all]        # All adapters
```

## Quick Start

```python
import asyncio
from amb_core import MessageBus

async def main():
    async with MessageBus() as bus:
        async def handler(msg): print(msg.payload)
        await bus.subscribe("agent.events", handler)
        await bus.publish("agent.events", {"status": "ready"})
        await asyncio.sleep(0.1)

asyncio.run(main())
```

## Architecture

`amb` sits in **Layer 2 (Infrastructure)** of the Agent OS stack. It transports message envelopes without inspecting content or enforcing policy.

```
┌──────────────────────────────────────┐
│  Layer 3: Framework                  │  agent-control-plane, scak
│  (Orchestration & Self-Correction)   │
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│  Layer 2: Infrastructure    ← AMB    │  iatp (Trust), atr (Registry)
│  (Transport & Discovery)             │
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│  Layer 1: Primitives                 │  caas (Context), cmvk (Verification),
│  (State & Identity)                  │  emk (Memory)
└──────────────────────────────────────┘
```

**Design Principles:**
- **No Business Logic:** The bus never decides routing based on message content.
- **Broker Agnostic:** Swap Redis for RabbitMQ without changing application code.
- **Local-First:** Works on a laptop with InMemoryBroker—no Docker required.
- **Separation of Concerns:** The bus transports. The receiver validates trust (via `iatp`), not the bus.

## The Agent OS Ecosystem

`amb` is one component of a modular Agent Operating System. Each layer solves a specific problem.

### Layer 1: Primitives (State & Identity)
- **[caas](https://github.com/imran-siddique/caas)** - Context as a Service: Manages agent context and state
- **[cmvk](https://github.com/imran-siddique/cmvk)** - Context Merkle Verification Kit: Cryptographic verification of context
- **[emk](https://github.com/imran-siddique/emk)** - Episodic Memory Kit: Persistent memory for agents

### Layer 2: Infrastructure (Transport & Discovery)
- **[iatp](https://github.com/imran-siddique/iatp)** - Inter-Agent Trust Protocol: Trust verification for agent messages
- **[amb](https://github.com/imran-siddique/amb)** - Agent Message Bus: Broker-agnostic transport *(you are here)*
- **[atr](https://github.com/imran-siddique/atr)** - Agent Tool Registry: Decentralized tool discovery

### Layer 3: Framework (Orchestration & Self-Correction)
- **[agent-control-plane](https://github.com/imran-siddique/agent-control-plane)** - The orchestration core
- **[scak](https://github.com/imran-siddique/scak)** - Self-Correction & Alignment Kit: Runtime safety and alignment

## Citation

If you use AMB in research, please cite:

```bibtex
@software{amb2026,
  author = {Siddique, Imran},
  title = {AMB: Agent Message Bus for Decoupled Multi-Agent Systems},
  year = {2026},
  url = {https://github.com/imran-siddique/amb},
  version = {0.1.0}
}
```

---

**License:** MIT | **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md) | **Changelog:** [CHANGELOG.md](CHANGELOG.md)
