# IATP Python SDK

A lightweight Python library for implementing the Inter-Agent Trust Protocol (IATP). This SDK provides both a sidecar server and decorators for directly integrating IATP into your Python agents.

## Installation

```bash
pip install iatp
```

Or from source:
```bash
cd sdk/python
pip install -e .
```

## Quick Start

### Option 1: Sidecar Mode (Recommended)

Run IATP as a separate process that wraps your existing agent:

```python
from iatp import IATPSidecar
from iatp.models import CapabilityManifest, AgentCapabilities, PrivacyContract

# Define your agent's capabilities
manifest = CapabilityManifest(
    agent_id="my-agent-v1.0.0",
    trust_level="standard",
    capabilities=AgentCapabilities(
        idempotency=True,
        reversibility="partial",
        undo_window="1h"
    ),
    privacy_contract=PrivacyContract(
        retention="ephemeral",
        storage_location="us-west-2"
    )
)

# Start the sidecar (wraps your agent on port 8000)
sidecar = IATPSidecar(
    manifest=manifest,
    backend_url="http://localhost:8000",
    sidecar_port=8001
)
sidecar.run()
```

### Option 2: Decorator Mode

Integrate IATP directly into your agent code:

```python
from iatp.decorators import iatp_protect
from iatp.models import CapabilityManifest

manifest = CapabilityManifest(
    agent_id="my-agent-v1.0.0",
    trust_level="standard"
)

@iatp_protect(manifest)
async def book_flight(destination: str, date: str):
    # Your agent logic here
    return {"status": "booked", "confirmation": "ABC123"}
```

## Core Components

### 1. Capability Manifest

Declare what your agent can do and how it handles data:

```python
from iatp.models import (
    CapabilityManifest,
    TrustLevel,
    AgentCapabilities,
    ReversibilityLevel,
    PrivacyContract,
    RetentionPolicy
)

manifest = CapabilityManifest(
    agent_id="booking-agent-v2.1.0",
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
        human_review=False,
        training_consent=False
    )
)

# Calculate trust score (0-10)
score = manifest.calculate_trust_score()
print(f"Trust Score: {score}/10")
```

### 2. Security Validation

Automatic detection of sensitive data:

```python
from iatp.security import SecurityValidator

validator = SecurityValidator()

# Detect sensitive data
data = {"payment": "4532015112830366"}
sensitive = validator.detect_sensitive_data(data)
# Returns: ["credit_card"]

# Validate against privacy policy
manifest = CapabilityManifest(
    agent_id="test",
    trust_level="untrusted",
    privacy_contract=PrivacyContract(retention="permanent")
)

validation = validator.validate_privacy_policy(data, manifest)
# Returns: {"blocked": True, "reason": "Credit card sent to untrusted agent..."}
```

### 3. Flight Recorder

Comprehensive audit logging:

```python
from iatp.telemetry import FlightRecorder

recorder = FlightRecorder(log_dir="./logs")

# Log a request
trace_id = "abc-123"
recorder.log_request(
    trace_id=trace_id,
    request={"task": "book_flight", "data": {...}},
    manifest=manifest
)

# Log a response
recorder.log_response(
    trace_id=trace_id,
    response={"result": "success"},
    latency_ms=1243.56
)

# Retrieve logs
logs = recorder.get_logs(trace_id)
```

### 4. Privacy Scrubbing

Automatic redaction of sensitive data in logs:

```python
from iatp.security import PrivacyScrubber

scrubber = PrivacyScrubber()

data = {
    "payment": "4532-0151-1283-0366",
    "ssn": "123-45-6789",
    "email": "user@example.com"
}

scrubbed = scrubber.scrub(data)
# Returns:
# {
#   "payment": "[CREDIT_CARD_REDACTED]",
#   "ssn": "[SSN_REDACTED]",
#   "email": "user@example.com"
# }
```

## API Reference

### Sidecar Endpoints

When running in sidecar mode, the following endpoints are exposed:

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

## Configuration

### Environment Variables

```bash
# Backend agent URL
IATP_BACKEND_URL=http://localhost:8000

# Sidecar port
IATP_SIDECAR_PORT=8001

# Flight recorder log directory
IATP_LOG_DIR=./logs

# Trust threshold (requests below this score trigger warnings)
IATP_TRUST_THRESHOLD=3
```

### Programmatic Configuration

```python
from iatp import IATPConfig

config = IATPConfig(
    backend_url="http://localhost:8000",
    sidecar_port=8001,
    log_dir="./logs",
    trust_threshold=3,
    enable_quarantine=True,
    enable_override=True
)
```

## Testing

Run the test suite:

```bash
pytest sdk/python/iatp/tests/ -v
```

Run with coverage:

```bash
pytest sdk/python/iatp/tests/ --cov=iatp --cov-report=html
```

## Examples

See the `/examples` directory for complete working examples:
- `backend_agent.py` - Sample backend agent
- `run_sidecar.py` - Trusted agent configuration
- `run_untrusted_sidecar.py` - Untrusted agent configuration
- `client.py` - Client making requests
- `test_untrusted.py` - Testing with low-trust agents

## Architecture

The Python SDK implements IATP as a FastAPI-based sidecar:

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

## Design Philosophy

> **"Be an Advisor, not a Nanny"**

IATP doesn't prevent users from doing what they want. It provides:
- **Transparency**: Clear warnings about risks
- **Control**: User override capabilities
- **Accountability**: Complete audit trails via flight recorder
- **Security**: Automatic blocking of truly dangerous requests

## Contributing

Contributions welcome! Areas of interest:
- Additional sensitive data patterns
- More sophisticated trust scoring algorithms
- Rate limiting implementations
- Authentication mechanisms

## License

MIT License - see LICENSE file for details

## Support

- Documentation: https://inter-agent-trust.org/docs
- GitHub Issues: https://github.com/imran-siddique/inter-agent-trust-protocol/issues
- Protocol Spec: See `/spec` directory
