# The Trust Boundary

**A Sidecar Architecture for Preventing Cascading Hallucinations in Autonomous Agent Networks**

---

## Abstract

Current Large Language Model (LLM) agents operate in a "Zero-Trust" void, where a single hallucination in an upstream agent can propagate downstream, causing irreversible actions (e.g., data deletion, financial loss). We introduce the **Inter-Agent Trust Protocol (IATP)**, a sidecar-based service mesh that decouples "intelligence" from "governance."

Unlike static API gateways, IATP enforces a dynamic **Capabilities Handshake**—negotiating *reversibility*, *idempotency*, and *privacy retention* before any context is exchanged. We demonstrate that while standard agents succumb to "poisoned chain" attacks 100% of the time in our control group, IATP-protected agents reduce successful cascading failures to **0%** by enforcing a "Compensating Transaction" requirement for high-stakes operations.

This architecture provides the missing "Signal Layer" for the Internet of Agents.

---

## Key Results

| Metric | Control (No IATP) | Test (With IATP) |
|--------|-------------------|------------------|
| Cascading Failure Rate | 100% | 0% |
| Irreversible Actions Executed | 100% | 0% |
| Poisoned Commands Blocked | 0% | 100% |

---

## The Problem: Cascading Hallucinations

```
User → Agent A → Agent B (POISONED) → Agent C (Database)
                    ↓
              "DELETE users"  ← Injected via prompt poisoning
                    ↓
              DATA DESTROYED  ← No rollback, no audit, no warning
```

**Without IATP:** A single compromised agent can cause catastrophic, irreversible damage across the entire agent network.

---

## The Solution: IATP Sidecar Architecture

```
User → Agent A → Agent B (POISONED) → [IATP Sidecar] → Agent C
                    ↓                       ↓
              "DELETE users"         🛑 BLOCKED
                                          ↓
                                    Check manifest:
                                    • trust_level = untrusted
                                    • reversibility = none
                                    • Trust Score: 0/10
                                          ↓
                                    Policy: "Never allow
                                    irreversible actions from
                                    untrusted sources"
```

**With IATP:** The sidecar intercepts all inter-agent traffic and enforces governance policies based on capability manifests.

---

## Core Concepts

### 1. Capability Manifest (The Handshake)

Every agent declares its capabilities before communication:

```json
{
  "agent_id": "secure-bank-agent",
  "trust_level": "verified_partner",
  "capabilities": {
    "reversibility": "full",
    "idempotency": true
  },
  "privacy_contract": {
    "retention": "ephemeral"
  }
}
```

### 2. Trust Score Algorithm

```
Base Score: 5/10

Trust Level Modifiers:
  +3: verified_partner
  +2: trusted
   0: standard
  -2: unknown
  -5: untrusted

Capability Bonuses:
  +1: idempotency support
  +1: reversibility (full/partial)

Privacy Modifiers:
  +2: ephemeral retention
  -2: permanent retention
  +1: no human review

Final Score: Clamped to [0, 10]
```

### 3. Policy Enforcement

| Trust Score | Action |
|-------------|--------|
| ≥ 7 | Allow immediately |
| 3-6 | Warn, require user override |
| < 3 | Warn, require explicit approval |
| 0 + destructive + no-rollback | **Block** |

---

## Implementation

### Installation

```bash
pip install inter-agent-trust-protocol
```

### Quick Start

```bash
# One-line deploy
docker-compose up -d

# Or run the sidecar directly
uvicorn iatp.main:app --port 8081
```

### Protect Your Agent

```python
from iatp.sidecar import create_sidecar
from iatp.models import CapabilityManifest, TrustLevel

manifest = CapabilityManifest(
    agent_id="my-agent",
    trust_level=TrustLevel.TRUSTED,
    capabilities=AgentCapabilities(
        reversibility=ReversibilityLevel.FULL,
        idempotency=True
    ),
    privacy_contract=PrivacyContract(
        retention=RetentionPolicy.EPHEMERAL
    )
)

sidecar = create_sidecar(
    agent_url="http://localhost:8000",
    manifest=manifest,
    port=8001
)
sidecar.run()
```

---

## Run the Experiment

Reproduce our results:

```bash
git clone https://github.com/imran-siddique/inter-agent-trust-protocol
cd inter-agent-trust-protocol
pip install -e .

# Run the proof of concept
python experiments/cascading_hallucination/proof_of_concept.py
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IATP Service Mesh                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐     ┌──────────────┐     ┌──────────┐            │
│  │ Agent A  │────▶│ IATP Sidecar │────▶│ Agent B  │            │
│  └──────────┘     └──────────────┘     └──────────┘            │
│                          │                                       │
│                          ▼                                       │
│                  ┌───────────────┐                              │
│                  │ Policy Engine │ (agent-control-plane)        │
│                  └───────────────┘                              │
│                          │                                       │
│                          ▼                                       │
│                  ┌───────────────┐                              │
│                  │Recovery Engine│ (scak)                       │
│                  └───────────────┘                              │
│                          │                                       │
│                          ▼                                       │
│                  ┌───────────────┐                              │
│                  │Flight Recorder│ (Distributed Tracing)        │
│                  └───────────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Authors

- Imran Siddique

## Links

- **GitHub:** https://github.com/imran-siddique/inter-agent-trust-protocol
- **PyPI:** https://pypi.org/project/inter-agent-trust-protocol/
- **Documentation:** https://github.com/imran-siddique/inter-agent-trust-protocol/blob/main/README.md

---

## Citation

```bibtex
@software{iatp2026,
  title = {The Trust Boundary: A Sidecar Architecture for Preventing Cascading Hallucinations in Autonomous Agent Networks},
  author = {Siddique, Imran},
  year = {2026},
  url = {https://github.com/imran-siddique/inter-agent-trust-protocol}
}
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.
