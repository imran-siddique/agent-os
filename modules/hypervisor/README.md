# Agent Hypervisor v1.0

> **The world's first runtime supervisor for multi-agent collaboration** — enforcing Verified Intent, Joint Liability, Execution Rings, and forensic audit trails at sub-millisecond latency.

[![Tests](https://img.shields.io/badge/tests-177%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-unit%20%2B%20integration%20%2B%20scenarios-blue)]()
[![Benchmark](https://img.shields.io/badge/latency-268μs%20full%20pipeline-orange)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()

## Why a Hypervisor?

Just as OS hypervisors isolate virtual machines and enforce resource boundaries, the **Agent Hypervisor** isolates AI agent sessions and enforces **governance boundaries**:

| OS Hypervisor | Agent Hypervisor |
|---------------|-----------------|
| CPU rings (Ring 0–3) | **Execution Rings** — privilege levels based on trust score (σ_eff) |
| Process isolation | **Session isolation** — VFS namespacing, DID-bound identity |
| Memory protection | **Liability protection** — bonded reputation, collateral slashing |
| System calls | **Saga transactions** — multi-step operations with automatic rollback |
| Audit logs | **Merkle-chained delta audit** — tamper-evident forensic trail |

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      AGENT HYPERVISOR                        │
│                                                              │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────────┐ │
│  │   Session    │ │    Ring      │ │   Semantic Saga        │ │
│  │   Manager    │ │   Enforcer   │ │   Orchestrator         │ │
│  │             │ │              │ │  ┌──────────────────┐  │ │
│  │  SSO + VFS  │ │  Ring 0–3    │ │  │ Timeout + Retry  │  │ │
│  │  Lifecycle  │ │  σ_eff gates │ │  │ Compensation     │  │ │
│  └──────┬──────┘ └──────┬───────┘ │  │ Escalation       │  │ │
│         │               │         │  └──────────────────┘  │ │
│  ┌──────┴──────┐ ┌──────┴───────┐ └────────────┬───────────┘ │
│  │  Liability  │ │ Reversibility│               │            │
│  │  Engine     │ │  Registry    │ ┌─────────────┴──────────┐ │
│  │             │ │              │ │   Delta Audit Engine    │ │
│  │  Vouch +    │ │  Execute/    │ │                        │ │
│  │  Bond +     │ │  Undo API    │ │  Merkle Chain + GC     │ │
│  │  Slash      │ │  Mapping     │ │  Blockchain Commit     │ │
│  └─────────────┘ └──────────────┘ └────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
         │                │                    │
┌────────┴────────────────┴────────────────────┴───────────────┐
│                   AGENT-OS KERNEL LAYER                       │
│  ┌────────┐ ┌──────┐ ┌──────┐ ┌─────┐ ┌──────────┐          │
│  │ IATP   │ │ CMVK │ │Nexus │ │CaaS │ │  SCAK    │          │
│  └────────┘ └──────┘ └──────┘ └─────┘ └──────────┘          │
└──────────────────────────────────────────────────────────────┘
```

## Key Features

### 🔐 Execution Rings (Hardware-Inspired Privilege Model)

```
Ring 0 (Root)       — Hypervisor config & slashing — requires SRE Witness
Ring 1 (Privileged) — Non-reversible actions — requires σ_eff > 0.95 + consensus
Ring 2 (Standard)   — Reversible actions — requires σ_eff > 0.60
Ring 3 (Sandbox)    — Read-only / research — default for unknown agents
```

Agents are automatically assigned to rings based on their effective trust score. Ring demotion happens in real-time if trust drops.

### 🤝 Joint Liability (Trust as Collateral)

High-trust agents can **vouch** for low-trust agents by bonding a percentage of their reputation:

```
σ_eff = σ_low + (ω × σ_high_bonded)
```

If the vouchee violates intent, **both agents are penalized** — the voucher's collateral is slashed. Max exposure limits (default: 80% of σ) prevent over-bonding.

### 🔄 Semantic Saga Orchestrator

Multi-step agent transactions with:
- **Timeout enforcement** — steps that hang are automatically cancelled
- **Retry with backoff** — transient failures retry with exponential delay
- **Reverse-order compensation** — on failure, all committed steps are undone
- **Escalation** — if compensation fails, Joint Liability slashing is triggered

### 📋 Delta Audit Engine

Forensic-grade audit trails using:
- **Semantic diffs** — captures what changed, not full snapshots
- **Merkle chaining** — each delta references its parent hash (tamper-evident)
- **Blockchain commitment** — Summary Hash anchored on-chain at session end
- **Garbage collection** — ephemeral data purged, forensic artifacts retained

## Performance

| Operation | Mean Latency | Throughput |
|-----------|-------------|------------|
| Ring computation | **0.3μs** | 3.75M ops/s |
| Delta audit capture | **27μs** | 26K ops/s |
| Session lifecycle | **54μs** | 15.7K ops/s |
| 3-step saga | **151μs** | 5.3K ops/s |
| **Full governance pipeline** | **268μs** | **2,983 ops/s** |

> Full pipeline = session create + agent join + 3 audit deltas + saga step + terminate with Merkle root

## Installation

```bash
pip install agent-hypervisor
```

## Quick Start

```python
from hypervisor import Hypervisor, SessionConfig, ConsistencyMode

hv = Hypervisor()

# Create a shared session
session = await hv.create_session(
    config=SessionConfig(
        consistency_mode=ConsistencyMode.EVENTUAL,
        max_participants=5,
        min_sigma_eff=0.60,
    ),
    creator_did="did:mesh:admin",
)

# Agents join via IATP handshake — ring assigned by trust score
ring = await hv.join_session(
    session.sso.session_id,
    agent_did="did:mesh:agent-alpha",
    sigma_raw=0.85,
)
# → ExecutionRing.RING_2_STANDARD

# Activate and execute
await hv.activate_session(session.sso.session_id)

# Multi-step saga with automatic compensation
saga = session.saga.create_saga(session.sso.session_id)
step = session.saga.add_step(
    saga.saga_id, "draft_email", "did:mesh:agent-alpha",
    execute_api="/api/draft", undo_api="/api/undo-draft",
    timeout_seconds=30, max_retries=2,
)
result = await session.saga.execute_step(
    saga.saga_id, step.step_id, executor=draft_email
)

# Terminate — returns Merkle root Summary Hash
merkle_root = await hv.terminate_session(session.sso.session_id)
```

## Modules

| Module | Description | Tests |
|--------|-------------|-------|
| `hypervisor.session` | Shared Session Object lifecycle + VFS | 52 |
| `hypervisor.rings` | 4-ring privilege model + action classification | 10 |
| `hypervisor.liability` | Vouching, bonding, slashing, liability matrix | 14 |
| `hypervisor.reversibility` | Execute/Undo API registry | 4 |
| `hypervisor.saga` | Semantic saga orchestrator + state machine | 12 |
| `hypervisor.audit` | Delta engine, Merkle chain, GC, commitment | 10 |
| `hypervisor.verification` | DID transaction history verification | 4 |
| `hypervisor.integrations` | Nexus, CMVK, IATP cross-module adapters | — |
| **Integration** | End-to-end lifecycle, edge cases, security | **24** |
| **Scenarios** | Cross-module governance pipelines (7 suites) | **18** |
| **Total** | | **177** |

## Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run benchmarks
python benchmarks/bench_hypervisor.py
```

## Cross-Module Integrations

The Hypervisor integrates with other Agent-OS modules via adapters in `hypervisor.integrations`:

### Nexus Adapter — Trust-Scored Ring Assignment

```python
from hypervisor.integrations.nexus_adapter import NexusAdapter
from nexus.reputation import ReputationEngine

nexus = NexusAdapter(scorer=ReputationEngine())
sigma = nexus.resolve_sigma("did:mesh:agent-1", history=agent_history)
# → 0.82 (Nexus 820/1000 normalized)

ring = await hv.join_session(session_id, "did:mesh:agent-1", sigma_raw=sigma)
# → RING_2_STANDARD

# Report slashing back to Nexus for persistent reputation loss
nexus.report_slash("did:mesh:agent-1", reason="Behavioral drift", severity="high")
```

### CMVK Adapter — Behavioral Drift Detection

```python
from hypervisor.integrations.cmvk_adapter import CMVKAdapter

cmvk = CMVKAdapter(verifier=cmvk_engine)
result = cmvk.check_behavioral_drift(
    agent_did="did:mesh:agent-1",
    session_id=session_id,
    claimed_embedding=manifest_vector,
    observed_embedding=output_vector,
)

if result.should_slash:
    hv.slashing.slash(...)  # Trigger liability cascade
```

### IATP Adapter — Capability Manifest Parsing

```python
from hypervisor.integrations.iatp_adapter import IATPAdapter

iatp = IATPAdapter()
analysis = iatp.analyze_manifest(manifest)  # or analyze_manifest_dict(dict)
# → ManifestAnalysis with ring_hint, sigma_hint, actions, reversibility flags

ring = await hv.join_session(
    session_id, analysis.agent_did,
    actions=analysis.actions, sigma_raw=analysis.sigma_hint,
)
```
