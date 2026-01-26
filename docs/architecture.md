# Agent OS Architecture

> High-level architecture overview. For implementation details, see [Kernel Internals](kernel-internals.md).

## Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture](architecture.md) | This file - layer overview, package descriptions |
| [Kernel Internals](kernel-internals.md) | Deep dive - execution model, policy engine, signals |
| [Security Spec](security-spec.md) | `.agents/security.md` format specification |
| [AAIF Proposal](AAIF_PROPOSAL.md) | Foundation membership proposal |
| [AIOS Comparison](AIOS_COMPARISON.md) | Competitive differentiation |

## Overview

Agent OS is a safety-first kernel for autonomous AI agents, providing POSIX-inspired primitives with a 0% policy violation guarantee.

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LAYER 4: INTELLIGENCE                    │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐   │
│  │  SCAK                   │  │  Mute Agent                 │   │
│  │  - Self-correction      │  │  - Reasoning/Execution      │   │
│  │  - Laziness detection   │  │  - Semantic handshake       │   │
│  │  - Differential audit   │  │  - Constraint pruning       │   │
│  └─────────────────────────┘  └─────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                         LAYER 3: FRAMEWORK                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Agent Control Plane                                      │   │
│  │  - Kernel Space (Ring 0): Policy, Flight Recorder, VFS   │   │
│  │  - User Space (Ring 3): Agent logic, LLM generation      │   │
│  │  - Signals: SIGSTOP, SIGKILL, SIGPOLICY                  │   │
│  │  - Syscalls: SYS_READ, SYS_WRITE, SYS_EXEC               │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                      LAYER 2: INFRASTRUCTURE                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐      │
│  │  IATP       │  │  AMB        │  │  ATR                │      │
│  │  - Trust    │  │  - Pub/Sub  │  │  - Tool Registry    │      │
│  │  - Sidecar  │  │  - Priority │  │  - Sandbox Exec     │      │
│  │  - IPC Pipes│  │  - Backpres │  │  - Discovery        │      │
│  └─────────────┘  └─────────────┘  └─────────────────────┘      │
├─────────────────────────────────────────────────────────────────┤
│                        LAYER 1: PRIMITIVES                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│  │Primitives│  │  CMVK    │  │  CaaS    │  │  EMK         │     │
│  │- Failures│  │- Drift   │  │- RAG     │  │- Episodic    │     │
│  │- Models  │  │- Verify  │  │- Context │  │- Memory      │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Package Descriptions

### Layer 1: Primitives

| Package | PyPI Name | Description |
|---------|-----------|-------------|
| **primitives** | `agent-primitives` | Base failure types, severity levels, agent failure models |
| **cmvk** | `cmvk` | Cross-Model Verification Kernel - drift detection, hallucination detection |
| **caas** | `caas-core` | Context-as-a-Service - RAG pipeline solving 7 RAG fallacies |
| **emk** | `emk` | Episodic Memory Kernel - immutable experience ledger |

### Layer 2: Infrastructure

| Package | PyPI Name | Description |
|---------|-----------|-------------|
| **iatp** | `inter-agent-trust-protocol` | Sidecar trust protocol, typed IPC pipes, policy enforcement |
| **amb** | `amb-core` | Agent Message Bus - broker-agnostic pub/sub with priority lanes |
| **atr** | `agent-tool-registry` | Decentralized tool registry with sandboxed Docker execution |

### Layer 3: Framework

| Package | PyPI Name | Description |
|---------|-----------|-------------|
| **control-plane** | `agent-control-plane` | Governance kernel with signals, VFS, kernel/user space separation |

### Layer 4: Intelligence

| Package | PyPI Name | Description |
|---------|-----------|-------------|
| **scak** | `scak` | Self-Correcting Agent Kernel - differential auditing, semantic memory hygiene |
| **mute-agent** | `mute-agent` | Reasoning/execution decoupling, constraint-based action pruning |

## Kernel Architecture

### Protection Rings

```
Ring 0 (Kernel Space):
  - Policy Engine - Deterministic enforcement
  - Flight Recorder - Immutable audit log
  - Signal Dispatcher - Agent lifecycle control
  - VFS Manager - Memory mount points

Ring 3 (User Space):
  - LLM Generation - Can crash/hallucinate
  - Agent Logic - Python/Node.js code
  - Tool Execution - Sandboxed
```

### Signal Handling

| Signal | Value | Description | Maskable? |
|--------|-------|-------------|-----------|
| SIGSTOP | 1 | Pause for inspection (shadow mode) | Yes |
| SIGCONT | 2 | Resume execution | Yes |
| SIGINT | 3 | Graceful interrupt | Yes |
| SIGKILL | 4 | Immediate termination | **No** |
| SIGTERM | 5 | Request shutdown | Yes |
| SIGPOLICY | 8 | Policy violation → SIGKILL | **No** |
| SIGTRUST | 9 | Trust violation → SIGKILL | **No** |

### Virtual File System (VFS)

```
/agent/[id]/
├── mem/
│   ├── working/     # Ephemeral scratchpad (MemoryBackend)
│   ├── episodic/    # Experience logs (can mount ChromaDB)
│   └── semantic/    # Knowledge (can mount Pinecone/Weaviate)
├── state/
│   └── checkpoints/ # SIGUSR1 snapshots
├── policy/          # Read-only from user space
└── ipc/             # Inter-process communication
```

### Syscall Interface

| Syscall | Description |
|---------|-------------|
| SYS_READ | Read from VFS |
| SYS_WRITE | Write to VFS |
| SYS_OPEN | Open file descriptor |
| SYS_CLOSE | Close file descriptor |
| SYS_EXEC | Execute tool (through kernel) |
| SYS_SIGNAL | Send signal to agent |
| SYS_CHECKPOLICY | Check if action allowed |
| SYS_EXIT | Request termination |

## Comparison with AIOS

| Aspect | AIOS | Agent OS |
|--------|------|----------|
| **Focus** | Efficiency (throughput) | Safety (0% violations) |
| **Failure Mode** | Graceful degradation | Kernel panic |
| **Memory Model** | Short/Long-term | VFS with mount points |
| **Signal Handling** | None | POSIX-style |
| **Crash Isolation** | Same process | Kernel/User space |
| **Policy Enforcement** | Optional | Mandatory, kernel-level |
| **Target Venue** | MLSys | ASPLOS |

## Design Philosophy

### Scale by Subtraction

- **Kernel, not SaaS**: We build Linux for Agents, not ServiceNow
- **CLI-first**: Engineers prefer `agentctl` over drag-and-drop
- **Safety over Speed**: Kernel panic on violation, not graceful degradation
- **POSIX-inspired**: Familiar primitives (signals, VFS, pipes)

### What We Don't Build

❌ Visual workflow editors  
❌ CRM connectors  
❌ Agent marketplace  
❌ Low-code builders  

### What We Build

✅ Signal handling  
✅ Virtual file systems  
✅ Typed IPC pipes  
✅ Kernel/user space separation  
✅ eBPF monitoring (future)  
