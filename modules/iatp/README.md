# Inter-Agent Trust Protocol (IATP)

> **Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents

[![PyPI version](https://badge.fury.io/py/inter-agent-trust-protocol.svg)](https://pypi.org/project/inter-agent-trust-protocol/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/imran-siddique/inter-agent-trust-protocol/test.yml?branch=main)](https://github.com/imran-siddique/inter-agent-trust-protocol/actions)

**Sidecar-based trust protocol for agent-to-agent communication.** Part of the Agent OS ecosystem.

---

## Why IATP?

Multi-agent systems fail because agents are forced to embed trust logic, security validation, and audit trails directly into their code. This creates tight coupling, makes agents fragile, and prevents interoperability.

**We built IATP because hard-coding trust into every agent is the wrong abstraction.** By extracting trust, policy enforcement, and governance into a sidecar proxy—similar to how Envoy extracts networking concerns from microservices—we subtract complexity from agents while adding scalability to the system.

**Scale by Subtraction:** Remove trust logic from agents. Remove policy checks from agents. Remove audit logging from agents. Put it all in the sidecar. Agents become simple functions. The infrastructure handles reliability.

---

## 🔒 Removing Implicit Trust

IATP eliminates implicit trust through two key features:

### 1. **Agent Attestation (Verifiable Credentials)**

**The Problem:** How do we know an agent running on a different server is running the verified code and not a hacked version?

**The Fix:** Attestation Handshake. Agents exchange a hash of their codebase/configuration signed by the Control Plane before talking.

- Cryptographic proof that agents run verified code
- Signed by trusted Control Plane
- Prevents running modified/hacked agent versions
- No need for complex firewalls—security is in the protocol

### 2. **Reputation Slashing**

**The Problem:** Agents that hallucinate or misbehave continue to be trusted by the network.

**The Fix:** If cmvk (Context Memory Verification Kit) catches an agent hallucinating, IATP automatically lowers that agent's trust score across the network. Other agents stop listening to it.

- Network-wide reputation tracking
- Automatic slashing when misbehavior detected
- cmvk integration for hallucination detection
- Conservative reputation propagation across nodes

---

## Installation

```bash
pip install inter-agent-trust-protocol
```

---

## Quick Start

```python
from iatp import create_sidecar, CapabilityManifest, AgentCapabilities, PrivacyContract, RetentionPolicy

manifest = CapabilityManifest(agent_id="my-agent", capabilities=AgentCapabilities(), privacy_contract=PrivacyContract(retention=RetentionPolicy.EPHEMERAL))
sidecar = create_sidecar(agent_url="http://localhost:8000", manifest=manifest, port=8001)
sidecar.run()
```

Your agent is now protected by IATP. Requests are validated, policies enforced, and all actions logged.

### Using Attestation and Reputation

```python
from iatp import create_sidecar, CapabilityManifest, AgentCapabilities, PrivacyContract, RetentionPolicy
from iatp.attestation import AttestationValidator, ReputationManager

# Create attestation for your agent (done by Control Plane)
validator = AttestationValidator()
validator.add_trusted_key("control-plane-key", "-----BEGIN PUBLIC KEY-----...")

attestation = validator.create_attestation(
    agent_id="my-agent",
    codebase_hash="sha256_of_codebase",
    config_hash="sha256_of_config",
    signing_key_id="control-plane-key",
    expires_in_hours=24
)

# Create sidecar with attestation
manifest = CapabilityManifest(...)
sidecar = create_sidecar(
    agent_url="http://localhost:8000",
    manifest=manifest,
    port=8001,
    attestation=attestation  # Proves you're running verified code
)

# Track reputation
reputation = ReputationManager()

# Record hallucination (called by cmvk)
reputation.record_hallucination(
    agent_id="misbehaving-agent",
    severity="high",
    details={"reason": "fabricated data"}
)

# Get reputation score
score = reputation.get_score("misbehaving-agent")
print(f"Trust score: {score.score}/10")
print(f"Trust level: {score.get_trust_level()}")
```

Run the demo:
```bash
python examples/demo_attestation_reputation.py
```

---

## Architecture

IATP sits in **Layer 2 (Infrastructure)** of the Agent OS. It acts as a sidecar proxy that intercepts agent-to-agent communication and enforces trust policies before forwarding requests.

```
Layer 3: Framework       [agent-control-plane, scak]
Layer 2: Infrastructure  [iatp, amb, atr]        ← IATP lives here
Layer 1: Primitives      [caas, cmvk, emk]
```

IATP receives requests from other agents or clients, validates the requester's capabilities against the target agent's requirements, enforces privacy and security policies, logs all transactions for auditability, and forwards approved requests to the backend agent.

The protocol defines a standard `.well-known/agent-manifest` endpoint that publishes trust levels, reversibility guarantees, privacy contracts, and SLA commitments. Trust scores are calculated automatically based on these attributes, and policies can block, warn, or allow operations accordingly.

---

## The Ecosystem Map

IATP is part of a modular Agent OS built on the "Scale by Subtraction" philosophy:

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Primitives** | `caas` | Context as a Service – Shared context management |
| | `cmvk` | Context Memory Verification Kit – Verify context integrity |
| | `emk` | Episodic Memory Kit – Long-term memory storage |
| **Infrastructure** | **`iatp`** | **Inter-Agent Trust Protocol – Trust and security sidecar** |
| | `amb` | Agent Message Bus – Reliable message transport |
| | `atr` | Agent Tool Registry – Discover and invoke agent tools |
| **Framework** | `agent-control-plane` | Agent Control Plane – Orchestration and lifecycle management |
| | `scak` | Self-Correction Autonomy Kit – Automated error recovery |

**Explore the ecosystem:**
- [Context as a Service (caas)](https://github.com/imran-siddique/caas)
- [Agent Message Bus (amb)](https://github.com/imran-siddique/amb)
- [Agent Control Plane](https://github.com/imran-siddique/agent-control-plane)

---

## Citation

If you use IATP in your research or production systems, please cite:

```bibtex
@software{iatp2024,
  author = {Siddique, Imran},
  title = {Inter-Agent Trust Protocol: Sidecar-Based Trust for Multi-Agent Systems},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/imran-siddique/inter-agent-trust-protocol}},
  version = {0.3.1}
}
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

