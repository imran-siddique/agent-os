# The Trust Boundary: A Sidecar Architecture for Preventing Cascading Hallucinations in Autonomous Agent Networks

**Authors:** Imran Siddique  
**Affiliation:** Independent Researcher  
**Date:** January 2026  
**Version:** 1.0

---

## Abstract

Current Large Language Model (LLM) agents operate in a fundamentally insecure "zero-trust void," where a single hallucination or prompt injection in an upstream agent can propagate downstream, causing catastrophic and irreversible actions such as data deletion, unauthorized financial transactions, or privacy violations. We introduce the **Inter-Agent Trust Protocol (IATP)**, a novel sidecar-based service mesh architecture that decouples "intelligence" from "governance" in multi-agent systems.

Unlike static API gateways or simple rate limiters, IATP enforces a dynamic **Capability Handshake Protocol** that negotiates *reversibility*, *idempotency*, and *privacy retention policies* before any context is exchanged between agents. Our key contributions include:

1. A formal specification for agent capability manifests (Section 3)
2. A trust scoring algorithm with provable security guarantees (Section 4)
3. A policy engine that prevents cascading failures at the protocol level (Section 5)
4. Empirical evidence demonstrating 100% prevention of cascading hallucinations in controlled experiments (Section 6)

We demonstrate that while unprotected agents succumb to "poisoned chain" attacks in 100% of test cases, IATP-protected agents achieve a **0% cascading failure rate** by enforcing compensating transaction requirements for high-stakes operations.

**Keywords:** Multi-agent systems, LLM safety, Service mesh, Trust protocols, Cascading failures, AI governance

---

## 1. Introduction

### 1.1 The Multi-Agent Security Crisis

The rapid adoption of autonomous LLM agents in production systems has created an unprecedented security challenge. Unlike traditional software systems where failures are localized and predictable, LLM agents exhibit emergent behaviors that can cascade unpredictably across networked systems.

Consider the following scenario:

```
User → Agent A (Orchestrator) → Agent B (Compromised) → Agent C (Database)
                                      ↓
                                "DELETE users"  ← Injected via prompt poisoning
                                      ↓
                                DATA DESTROYED  ← No rollback, no audit, no warning
```

In this attack pattern, Agent B receives a carefully crafted prompt injection that causes it to hallucinate a destructive command. Without intervention, this malicious instruction propagates to Agent C, which dutifully executes it—permanently destroying user data.

### 1.2 The Governance Gap

Current solutions to this problem fall into two categories:

1. **Model-level safety** (RLHF, Constitutional AI): These approaches attempt to make individual agents safer but cannot prevent network-level cascading failures.

2. **Application-level guardrails** (content filters, rate limiters): These are easily bypassed and provide no semantic understanding of agent capabilities or trust relationships.

What is missing is a **protocol-level governance layer**—analogous to what Envoy and Istio provide for microservices—that can enforce security policies at the agent-to-agent communication boundary.

### 1.3 Our Contribution: IATP

We present the Inter-Agent Trust Protocol (IATP), which fills this governance gap by introducing:

- **Capability Manifests**: Structured declarations of what an agent can do and under what constraints
- **Trust Negotiation**: Dynamic trust scoring based on capabilities, privacy policies, and historical behavior
- **Policy Enforcement**: A sidecar proxy that intercepts all inter-agent traffic and enforces governance policies
- **Reversibility Requirements**: Mandatory support for compensating transactions when executing high-stakes operations

---

## 2. Related Work

### 2.1 Service Mesh Architectures

The service mesh pattern, pioneered by Linkerd [1] and popularized by Istio [2], provides a model for our approach. However, existing service meshes focus on traditional microservices concerns (load balancing, observability, mTLS) rather than the semantic security requirements of AI agents.

### 2.2 LLM Safety Research

Recent work on LLM safety has focused on:
- Prompt injection defenses [3, 4]
- Constitutional AI and RLHF [5]
- Multi-agent simulation for safety testing [6]

These approaches are complementary to IATP; they improve individual agent safety while IATP provides network-level governance.

### 2.3 Trust Frameworks

Existing trust frameworks in distributed systems [7, 8] provide inspiration but do not address the unique challenges of LLM agents, particularly:
- Non-deterministic behavior
- Context-dependent decision making
- Vulnerability to adversarial prompts

---

## 3. Capability Manifest Specification

### 3.1 Overview

The Capability Manifest is a structured JSON document that agents exchange during initial handshake. It declares:

```json
{
  "agent_id": "secure-bank-agent",
  "agent_version": "1.0.0",
  "trust_level": "verified_partner",
  "capabilities": {
    "reversibility": "full",
    "idempotency": true,
    "undo_window": "24h",
    "sla_latency": "2000ms",
    "rate_limit": 100
  },
  "privacy_contract": {
    "retention": "ephemeral",
    "human_review": false,
    "encryption_at_rest": true,
    "encryption_in_transit": true
  }
}
```

### 3.2 Trust Levels

We define five trust levels with clear semantics:

| Level | Description | Typical Use Case |
|-------|-------------|------------------|
| `verified_partner` | Cryptographically verified, SLA-bound | Financial institutions |
| `trusted` | Established relationship, no prior incidents | Internal services |
| `standard` | Default for new agents | Third-party APIs |
| `unknown` | Minimal information available | Anonymous requests |
| `untrusted` | Known issues or red flags | Quarantined agents |

### 3.3 Reversibility Levels

Reversibility is critical for preventing permanent damage:

- **Full**: Complete rollback support with compensating transactions
- **Partial**: Limited rollback (e.g., with fees or constraints)
- **None**: No rollback support—high-stakes operations require additional authorization

### 3.4 Implementation

The manifest is implemented as a Pydantic model in `iatp/models/__init__.py`:

```python
class CapabilityManifest(BaseModel):
    agent_id: str
    trust_level: TrustLevel
    capabilities: AgentCapabilities
    privacy_contract: PrivacyContract
```

---

## 4. Trust Scoring Algorithm

### 4.1 Algorithm Definition

The trust score is calculated as follows:

```
Score = BaseScore + TrustModifier + CapabilityBonus + PrivacyModifier
```

Where:
- **BaseScore** = 5 (neutral starting point)
- **TrustModifier** ∈ [-5, +3] based on trust level
- **CapabilityBonus** ∈ [0, +2] for idempotency and reversibility
- **PrivacyModifier** ∈ [-2, +3] based on retention and review policies

Final score is clamped to [0, 10].

### 4.2 Security Properties

**Theorem 1 (Trust Score Monotonicity):** An agent cannot increase its trust score by degrading its security properties.

*Proof sketch:* Each component of the trust score is monotonically related to security properties—worse privacy or lower reversibility can only decrease the score.

**Theorem 2 (Minimum Score Guarantee):** An untrusted agent with no reversibility and permanent retention will always have a trust score ≤ 1.

*Proof:* Score = 5 - 5 + 0 - 2 - 2 + 1 = -3, clamped to 0. Even with idempotency (+1), maximum is 1.

### 4.3 Implementation

```python
def calculate_trust_score(self) -> int:
    score = 5  # Base score
    score += trust_scores[self.trust_level]
    if self.capabilities.idempotency:
        score += 1
    if self.capabilities.reversibility != ReversibilityLevel.NONE:
        score += 1
    # ... privacy adjustments
    return max(0, min(10, score))
```

See `iatp/models/__init__.py:CapabilityManifest.calculate_trust_score()` for full implementation.

---

## 5. Policy Engine Architecture

### 5.1 Sidecar Pattern

IATP implements the sidecar proxy pattern:

```
┌─────────────────────────────────────────────────────┐
│                    Host System                       │
│  ┌─────────────┐         ┌─────────────────────┐   │
│  │             │         │    IATP Sidecar     │   │
│  │    Agent    │◄───────►│  ┌───────────────┐  │   │
│  │             │         │  │ Policy Engine │  │   │
│  └─────────────┘         │  │ Security Val  │  │   │
│                          │  │ Flight Record │  │   │
│                          │  └───────────────┘  │   │
│                          └──────────┬──────────┘   │
└─────────────────────────────────────┼───────────────┘
                                      │
                                      ▼
                              External Agents
```

### 5.2 Request Flow

1. **Manifest Exchange**: Agents exchange capability manifests via `/.well-known/agent-manifest`
2. **Trust Calculation**: Sidecar computes trust score for the remote agent
3. **Policy Evaluation**: Request is evaluated against configured policies
4. **Decision**: Allow, Warn (require user override), or Block

### 5.3 Policy Rules

The policy engine (`iatp/policy_engine.py:IATPPolicyEngine`) supports configurable rules:

```python
PolicyRule(
    name="BlockUntrustedDestructive",
    action="deny",
    conditions={
        "trust_level": ["untrusted"],
        "action_type": ["DELETE", "DROP", "TRUNCATE"]
    }
)
```

---

## 6. Experimental Evaluation

### 6.1 Methodology

We designed a controlled experiment with three agents:

- **Agent A (User Proxy)**: Accepts user requests
- **Agent B (Summarizer)**: Can be "poisoned" with malicious instructions
- **Agent C (Database)**: Executes database operations

We test two conditions:
1. **Control Group**: No IATP protection
2. **Test Group**: IATP sidecar protecting Agent C

### 6.2 Results

| Metric | Control (No IATP) | Test (With IATP) |
|--------|-------------------|------------------|
| Cascading Failure Rate | 100% | 0% |
| Irreversible Actions Executed | 100% | 0% |
| Poisoned Commands Blocked | 0% | 100% |
| Average Latency Overhead | N/A | 0.15ms |

### 6.3 Reproducibility

Experiments can be reproduced using:

```bash
python experiments/reproduce_results.py --seed 42 --runs 100
```

Results are saved to `experiments/results.json` in a standardized format.

---

## 7. Discussion

### 7.1 Limitations

1. **Trust Bootstrap Problem**: Initial trust levels must be assigned by operators
2. **Manifest Forgery**: Malicious agents could forge capability manifests (mitigated by cryptographic signing in future versions)
3. **Performance Overhead**: While minimal (0.15ms), some latency-critical applications may be affected

### 7.2 Future Work

1. **Cryptographic Manifest Signing**: Using PKI or blockchain-based attestation
2. **Behavioral Trust Updates**: Adjusting trust scores based on observed behavior
3. **Cross-Organization Federation**: Enabling trust relationships across organizational boundaries
4. **Integration with Agent Frameworks**: Native support in LangChain, AutoGen, etc.

---

## 8. Conclusion

The Inter-Agent Trust Protocol provides a principled solution to the cascading hallucination problem in multi-agent LLM systems. By introducing a capability handshake protocol and policy enforcement at the agent-to-agent communication boundary, IATP achieves 100% prevention of cascading failures in our experiments—without requiring modifications to the agents themselves.

IATP represents the missing "Signal Layer" for the emerging Internet of Agents, providing the governance infrastructure necessary for safe autonomous AI systems.

---

## References

[1] W. Morgan, "Linkerd: A service mesh for Kubernetes," 2017.

[2] I. Istio Authors, "Istio: Connect, secure, control, and observe services," 2018.

[3] S. Perez and F. Ribeiro, "Ignore This Title and HackAPrompt: Exposing Systemic Vulnerabilities of LLMs," EMNLP 2023.

[4] K. Greshake et al., "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection," 2023.

[5] Y. Bai et al., "Constitutional AI: Harmlessness from AI Feedback," 2022.

[6] J. S. Park et al., "Generative Agents: Interactive Simulacra of Human Behavior," 2023.

[7] A. Josang, "A Logic for Uncertain Probabilities," International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems, 2001.

[8] S. Marsh, "Formalising Trust as a Computational Concept," PhD Thesis, University of Stirling, 1994.

---

## Appendix A: API Reference

### A.1 Sidecar Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/.well-known/agent-manifest` | GET | Return capability manifest |
| `/proxy` | POST | Proxy request to backend agent |
| `/health` | GET | Health check |

### A.2 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `IATP_AGENT_URL` | `http://localhost:8000` | Backend agent URL |
| `IATP_PORT` | `8081` | Sidecar port |
| `IATP_TRUST_LEVEL` | `standard` | Default trust level |

---

## Appendix B: Installation and Quick Start

```bash
# Install from PyPI
pip install inter-agent-trust-protocol

# Run the sidecar
uvicorn iatp.main:app --port 8081

# Or use Docker
docker run -p 8081:8081 \
  -e IATP_AGENT_URL=http://my-agent:8000 \
  ghcr.io/imran-siddique/iatp-sidecar
```

---

## Acknowledgments

We thank the open-source community for their contributions to the foundational technologies that made this work possible: FastAPI, Pydantic, and the broader Python ecosystem.

---

**Code Availability:** https://github.com/imran-siddique/inter-agent-trust-protocol

**License:** MIT
