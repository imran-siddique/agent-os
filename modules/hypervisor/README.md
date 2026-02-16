# Agent Hypervisor v1.0

> Runtime supervisor for multi-agent Shared Sessions with Verified Intent, Joint Liability, and Execution Rings.

The Hypervisor sits above the Agent-OS kernel and AgentMesh trust layer, orchestrating their capabilities into a unified governance runtime for multi-agent collaboration.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   AGENT HYPERVISOR                   │
│  ┌───────────┐ ┌──────────┐ ┌─────────────────────┐ │
│  │  Session   │ │ Ring     │ │ Semantic Saga       │ │
│  │  Manager   │ │ Enforcer │ │ Orchestrator        │ │
│  └─────┬─────┘ └────┬─────┘ └──────────┬──────────┘ │
│        │             │                  │            │
│  ┌─────┴─────┐ ┌────┴─────┐ ┌──────────┴──────────┐ │
│  │ Liability  │ │Reversi-  │ │  Delta Audit        │ │
│  │ Engine     │ │bility    │ │  Engine             │ │
│  └─────┬─────┘ └────┬─────┘ └──────────┬──────────┘ │
└────────┼────────────┼──────────────────┼────────────┘
         │            │                  │
┌────────┴────────────┴──────────────────┴────────────┐
│              EXISTING PLATFORM LAYER                 │
│  ┌────────┐ ┌──────┐ ┌──────┐ ┌─────┐ ┌──────────┐ │
│  │ IATP   │ │ CMVK │ │Nexus │ │CaaS │ │  SCAK    │ │
│  └────────┘ └──────┘ └──────┘ └─────┘ └──────────┘ │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

- **Shared Session Object (SSO)**: Encapsulates a multi-agent interaction with DID-bound identity, consistency mode, and shared VFS state.
- **Joint Liability**: Trust as a collateralized asset — high-score agents vouch for low-score agents by bonding reputation.
- **Execution Rings**: Hardware-inspired privilege levels (Ring 0–3) enforced by σ_eff thresholds.
- **Semantic Saga**: Orchestrated multi-step transactions with automatic reverse-order compensation on failure.
- **Delta Audit Trail**: Merkle-chained semantic diffs instead of full snapshots, with blockchain-anchored Summary Hashes.

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
    )
)

# Agents join via IATP handshake
await session.join(agent_did="did:mesh:agent-alpha", manifest=alpha_manifest)
await session.join(agent_did="did:mesh:agent-beta", manifest=beta_manifest)

# Execute within the session
result = await session.execute(
    agent_did="did:mesh:agent-alpha",
    action_id="draft_email",
)
```

## Modules

| Module | Description |
|--------|-------------|
| `hypervisor.session` | Shared Session Object lifecycle |
| `hypervisor.liability` | Vouching, bonding, slashing, liability matrix |
| `hypervisor.rings` | 4-ring privilege model and action classification |
| `hypervisor.reversibility` | Execute/Undo API registry |
| `hypervisor.verification` | DID transaction history verification |
| `hypervisor.saga` | Semantic saga orchestrator and state machine |
| `hypervisor.audit` | Delta engine, blockchain commitment, GC |
