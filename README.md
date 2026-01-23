# Inter-Agent Trust Protocol (IATP)

A **Zero-Config Sidecar** for Agent Communication that solves the problems of **Discovery**, **Trust**, and **Reversibility**.

## 🎯 What is IATP?

IATP is a lightweight proxy (sidecar) that sits in front of your AI agent and handles security, privacy, trust validation, and telemetry **before** requests reach your agent. Your agent receives clean, validated JSON and doesn't need to worry about security checks.

### The Architecture: "The Invisible Sidecar"

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Client    │ ──────> │ IATP Sidecar │ ──────> │ Your Agent  │
│             │         │  (Port 8001) │         │ (Port 8000) │
└─────────────┘         └──────────────┘         └─────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  Security Checks    │
                    │  Privacy Validation │
                    │  Trace Logging      │
                    │  Rate Limiting      │
                    └─────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

**Step 1: Start your backend agent** (e.g., on port 8000)
```bash
python examples/backend_agent.py
```

**Step 2: Start the IATP sidecar** (wraps your agent on port 8001)
```bash
python examples/run_sidecar.py
```

**Step 3: Send requests through the sidecar**
```bash
curl -X POST http://localhost:8001/proxy \
  -H 'Content-Type: application/json' \
  -d '{"task": "book_flight", "data": {"destination": "NYC"}}'
```

## 🔑 Key Features

### 1. Capability Manifest Exchange

Every agent publishes a capability manifest that describes:
- **Trust Level**: verified_partner, trusted, standard, unknown, untrusted
- **Capabilities**: idempotency, reversibility, undo windows, SLA promises
- **Privacy Contract**: data retention, storage location, human review policies

```python
from iatp import CapabilityManifest, AgentCapabilities, PrivacyContract

manifest = CapabilityManifest(
    agent_id="booking-agent-v2",
    trust_level=TrustLevel.VERIFIED_PARTNER,
    capabilities=AgentCapabilities(
        idempotency=True,
        reversibility=ReversibilityLevel.PARTIAL,
        undo_window="24h",
        sla_latency="2000ms"
    ),
    privacy_contract=PrivacyContract(
        retention=RetentionPolicy.EPHEMERAL,
        storage_location="us-west",
        human_review=False
    )
)
```

### 2. Automatic Security Validation

The sidecar automatically:
- ✅ Detects sensitive data (credit cards, SSNs)
- ✅ Blocks requests that violate privacy policies
- ✅ Calculates trust scores (0-10)
- ✅ Quarantines risky requests

**Example: Blocked Request**
```python
# If an agent stores data forever and you send a credit card:
# → Sidecar BLOCKS the request automatically
{
  "error": "Privacy Violation: Agent stores data permanently and request contains credit card information.",
  "blocked": true,
  "trace_id": "abc-123"
}
```

### 3. User Override with Warnings

For risky (but not blocked) requests, users get a warning and can override:

```bash
# First attempt: Get warning
curl -X POST http://localhost:8001/proxy \
  -H 'Content-Type: application/json' \
  -d '{"task": "book_flight"}'

# Response (status 449):
{
  "warning": "⚠️ WARNING:\n  • Low trust score (2/10)\n  • Agent does not support transaction reversal\n  • Agent stores data indefinitely",
  "requires_override": true
}

# Second attempt: Override
curl -X POST http://localhost:8001/proxy \
  -H 'Content-Type: application/json' \
  -H 'X-User-Override: true' \
  -d '{"task": "book_flight"}'

# → Request goes through but is marked as quarantined in logs
```

### 4. Distributed Tracing & Flight Recorder

Every request gets a unique trace ID and is logged for audit:

```python
# All requests get traced
X-Agent-Trace-ID: e4b5c6d7-8a9b-0c1d-2e3f-4a5b6c7d8e9f

# Retrieve logs
curl http://localhost:8001/trace/{trace_id}

# Returns:
{
  "trace_id": "...",
  "logs": [
    {"type": "request", "timestamp": "...", "payload": "..."},
    {"type": "response", "timestamp": "...", "latency_ms": 123.45},
  ]
}
```

## 📋 API Reference

### Sidecar Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/.well-known/agent-manifest` | GET | Get the capability manifest |
| `/proxy` | POST | Proxy a request to the backend agent |
| `/health` | GET | Health check |
| `/trace/{trace_id}` | GET | Get flight recorder logs |
| `/quarantine/{trace_id}` | GET | Get quarantine session info |

### Request Headers

| Header | Description |
|--------|-------------|
| `X-User-Override` | Set to "true" to bypass warnings |
| `X-Agent-Trace-ID` | Optional trace ID for distributed tracing |

### Response Headers

| Header | Description |
|--------|-------------|
| `X-Agent-Trace-ID` | Trace ID for this request |
| `X-Agent-Trust-Score` | Trust score (0-10) |
| `X-Agent-Latency-Ms` | Backend latency in milliseconds |
| `X-Agent-Quarantined` | "true" if request was quarantined |

## 🧪 Testing

Run the test suite:

```bash
pip install -r requirements-dev.txt
pytest iatp/tests/ -v
```

## 📚 Examples

See the `examples/` directory for:
- `backend_agent.py` - Sample backend agent
- `run_sidecar.py` - How to configure and run the sidecar
- `client.py` - Example client making requests

## 🏗️ Architecture Details

### The Three Pillars

1. **Discovery**: Capability manifests let agents advertise what they can do
2. **Trust**: Automatic validation against security and privacy policies
3. **Reversibility**: Transaction tracking and audit logging for rollbacks

### The "Hell Breaks Loose" Handler

When a user wants to use a low-trust agent:
1. Sidecar detects risk and returns warning (status 449)
2. User acknowledges risk with `X-User-Override: true`
3. Request is processed but marked as "quarantined"
4. All quarantined requests are logged separately for audit

### Privacy Scrubbing

All logged data is automatically scrubbed of sensitive information:
- Credit cards → `[CREDIT_CARD_REDACTED]`
- SSNs → `[SSN_REDACTED]`

## 🤝 Contributing

Contributions welcome! Key areas:
- Additional sensitive data patterns
- More sophisticated trust scoring algorithms
- Rate limiting implementations
- Authentication mechanisms

## 📄 License

MIT License - see LICENSE file for details

## 🎯 Design Philosophy

> **"Be an Advisor, not a Nanny"**

IATP doesn't prevent users from doing what they want. It provides:
- **Transparency**: Clear warnings about risks
- **Control**: User override capabilities
- **Accountability**: Complete audit trails via flight recorder
- **Security**: Automatic blocking of truly dangerous requests (e.g., credit cards to untrusted agents)

The user always has the final say, but they make informed decisions.
