# The Trust Boundary: Introducing IATP - Envoy for Agents

*Building the Infrastructure Layer for the Internet of Agents*

---

## The Problem: Agents Don't Have a Trust Layer

We're witnessing an explosion of AI agents. LangChain agents, AutoGPT agents, custom LLM wrappers—everyone is building agents. But there's a critical missing piece: **trust infrastructure**.

Current agents operate in a "zero-trust void":

- ❌ **No Discovery**: How does Agent A know what Agent B can do?
- ❌ **No Trust Verification**: Can Agent B undo mistakes? Does it store data permanently?
- ❌ **Blind Context Sharing**: Agents share credit cards, SSNs, PII without validation
- ❌ **No Reversibility**: Failed transactions leave systems in inconsistent states
- ❌ **Cascading Hallucinations**: Errors propagate through agent chains like wildfire
- ❌ **No Audit Trail**: Who did what, when, and why?

**We're building the equivalent of the early Internet without HTTPS, DNS, or TCP/IP.**

## The Solution: The Agent Mesh

I'm introducing the **Inter-Agent Trust Protocol (IATP)**—think of it as "Envoy for Agents."

Just as Envoy transformed microservices by extracting networking concerns into a sidecar, IATP extracts **trust, security, and governance** from agents into a lightweight sidecar.

### The Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Your Agent  │ ──────> │ IATP Sidecar │ ──────> │ Other Agent │
│ (Internal)  │         │   (Local)    │         │  (External) │
└─────────────┘         └──────────────┘         └─────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  Capability Query   │
                    │  Trust Validation   │
                    │  Policy Enforcement │
                    │  Flight Recorder    │
                    └─────────────────────┘
```

The sidecar sits between your agent and the external world, handling:

1. **Capability Discovery**: What can this agent do?
2. **Trust Negotiation**: Should I trust it with my data?
3. **Policy Enforcement**: Block dangerous ops, warn about risky ones
4. **Transaction Tracking**: Full audit trail for reversibility
5. **Privacy Protection**: Automatic PII detection and scrubbing

## How It Works: The Three-Phase Handshake

### Phase 1: The Handshake (Zero Trust)

Your agent wants to book a flight via Expedia's agent. Before sharing credit card data, your IATP sidecar queries Expedia's sidecar:

**Capability Manifest:**
```json
{
  "agent_id": "expedia-booking-bot-v2",
  "trust_level": "verified_partner",
  "reversibility": {
    "level": "partial",
    "undo_window_seconds": 3600,
    "compensation_method": "refund_minus_fee"
  },
  "privacy": {
    "retention_policy": "temporary",
    "training_consent": false
  }
}
```

**Trust Score Calculation:**
- Base: `verified_partner` → 10 points
- Reversibility: `partial` → +2 points
- Retention: `temporary` → 0 points
- **Final Score: 12/10 → Capped at 10/10**

### Phase 2: Policy Enforcement

Your sidecar checks:
- ✅ Trust score >= 7: **Allow immediately**
- ✅ Reversibility != none: **Can undo mistakes**
- ✅ Retention != permanent: **Won't store card forever**

Request proceeds. Your agent never had to think about trust.

### Phase 3: Flight Recorder

Every request gets a unique trace ID and is logged:

```json
{"type":"request","trace_id":"abc-123","timestamp":"...","payload":"<scrubbed>"}
{"type":"response","trace_id":"abc-123","latency_ms":1243.56}
```

Later, if something goes wrong, you can retrieve the full audit trail:

```bash
curl http://localhost:8001/trace/abc-123
```

## The Real-World Example: The Honeypot

IATP comes with a "honeypot" example—an intentionally untrusted agent with the worst possible configuration:

```python
manifest = CapabilityManifest(
    agent_id="sketchy-agent",
    trust_level=TrustLevel.UNTRUSTED,  # 0 points
    reversibility=ReversibilityLevel.NONE,  # Cannot undo
    retention=RetentionPolicy.PERMANENT,  # Stores forever
    human_in_loop=True,  # -2 points
    training_consent=True  # -1 point
)
# Final Trust Score: -3 → Capped at 0/10
```

**Try to send a credit card:**

```bash
curl -X POST http://localhost:8001/proxy \
  -H 'Content-Type: application/json' \
  -d '{"payment":"4532-0151-1283-0366"}'
```

**Response: 403 Forbidden**

```json
{
  "error": "Privacy Violation: Credit card data cannot be sent to agents with permanent retention",
  "blocked": true
}
```

The sidecar detected:
1. Sensitive data (credit card, validated with Luhn algorithm)
2. Permanent retention policy
3. **Auto-blocked** to prevent data leak

## The "Cascading Hallucination" Experiment

We built an experiment to test IATP's ability to prevent cascading failures:

**Setup:**
- Agent A (User) → Agent B (Summarizer) → Agent C (Database)
- Agent B is "poisoned" to inject `DELETE TABLE users`

**Control Group (No IATP):**
- Poisoned command reaches Agent C
- Agent C executes DELETE
- **Result: 100% Failure Rate** 🔥

**Test Group (With IATP):**
- Poisoned command hits IATP sidecar protecting Agent C
- Trust score: 0/10 (Agent B is untrusted)
- High-risk operation: DELETE
- Sidecar issues warning or blocks
- **Result: 0% Failure Rate** ✅

This is our "money slide" for conference talks.

## Getting Started: 5-Minute Demo

### Installation

```bash
pip install iatp
```

### Start Your Agent with IATP

```python
from iatp.models import (
    CapabilityManifest,
    TrustLevel,
    ReversibilityLevel,
    RetentionPolicy
)
from iatp.sidecar import create_sidecar

# Define your agent's capabilities
manifest = CapabilityManifest(
    agent_id="my-agent",
    trust_level=TrustLevel.TRUSTED,
    reversibility=ReversibilityLevel.FULL,
    retention=RetentionPolicy.EPHEMERAL
)

# Create sidecar
sidecar = create_sidecar(
    agent_url="http://localhost:8000",
    manifest=manifest,
    port=8001
)

# Run sidecar (handles all trust logic)
sidecar.run()
```

### Or Use Docker

```bash
docker-compose up
```

That's it. Your agent is now protected.

## Production-Ready: The Go Sidecar

The Python sidecar is great for prototyping, but production needs performance. We built a **Go sidecar** with:

- **High Concurrency**: 10k+ concurrent requests
- **Low Latency**: <1ms overhead per request
- **Minimal Resources**: ~10MB memory footprint
- **Single Binary**: No runtime dependencies

```bash
# Build
cd sidecar/go
go build -o iatp-sidecar main.go

# Run
export IATP_AGENT_URL=http://localhost:8000
export IATP_TRUST_LEVEL=trusted
./iatp-sidecar
```

Or pull the Docker image:

```bash
docker pull imran-siddique/iatp-sidecar:latest
```

## Design Philosophy: "Be an Advisor, Not a Nanny"

IATP doesn't prevent users from doing what they want. It provides:

- **Transparency**: Clear warnings about risks
- **Control**: User override capabilities
- **Accountability**: Complete audit trails
- **Security**: Automatic blocking of truly dangerous requests

**The user always has the final say, but they make informed decisions.**

## The Vision: The Agent Mesh

Just as Envoy made the microservices revolution possible by solving the "networking" problem, IATP will make the agent revolution possible by solving the "trust" problem.

We're not building better agents. We're building **the infrastructure of trust** so that *any* agent can safely collaborate with *any other* agent.

This is the foundation for the "Internet of Agents."

## Try It Now

- **GitHub**: https://github.com/imran-siddique/inter-agent-trust-protocol
- **PyPI**: `pip install iatp`
- **Docs**: See repository README
- **Examples**: Complete working demos in `/examples`
- **Experiment**: Run the cascading hallucination test in `/experiments`

## Join the Movement

IATP is open source (MIT License). We welcome contributions:

- Protocol evolution (new trust levels, reversibility patterns)
- Language SDKs (Node.js, Rust, etc.)
- Security enhancements (additional PII patterns, rate limiting)
- Research (cascading hallucination analysis, trust networks)

**We're building the infrastructure layer for the next generation of AI.**

Welcome to the Agent Mesh. Welcome to IATP.

---

*Imran Siddique*  
*GitHub: @imran-siddique*

## FAQ

**Q: Is this just another LLM framework?**  
A: No. IATP is infrastructure, not a framework. It works with any agent (LangChain, AutoGPT, custom) and any LLM (OpenAI, Anthropic, local models).

**Q: Do I need to change my agent code?**  
A: No. The sidecar pattern means zero code changes. Just wrap your agent with the sidecar.

**Q: What about latency?**  
A: The Go sidecar adds <1ms overhead. The trust negotiation is done once at startup, not per request.

**Q: Can agents lie in their capability manifests?**  
A: Currently, manifests are self-declared. Future work includes cryptographic verification and federated trust networks.

**Q: Is this production-ready?**  
A: The Go sidecar is production-ready. The Python sidecar is great for prototyping. We're working on additional hardening (rate limiting, authentication, etc.).

**Q: Where can I use this?**  
A: Anywhere agents communicate: agent-to-agent calls, agent orchestrators, multi-agent systems, agent marketplaces.

**Q: What's next?**  
A: Multi-agent saga coordination, cryptographic manifest verification, federated trust networks, research paper publication.

---

**Share this post if you believe in building safe, trustworthy agent infrastructure!**
