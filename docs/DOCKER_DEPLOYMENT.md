# IATP Docker Deployment Guide

This guide explains how to deploy and test the Inter-Agent Trust Protocol (IATP) using Docker Compose.

## Quick Start

### 1. Start the Trust Mesh

Launch all services with a single command:

```bash
docker compose up
```

This starts:
- **bank-agent**: Secure banking agent (verified partner)
- **iatp-sidecar-python**: Python sidecar protecting the bank agent
- **iatp-sidecar-go**: Go sidecar (production version)
- **honeypot-agent**: Untrusted agent for testing
- **honeypot-sidecar**: Sidecar exposing the honeypot's manifest

### 2. Verify Services are Running

Check service health:

```bash
# Bank agent health
curl http://localhost:8000/health

# Python sidecar health
curl http://localhost:8001/health

# Go sidecar health
curl http://localhost:8002/health

# Honeypot health
curl http://localhost:8100/health
```

### 3. Test Capability Discovery

Fetch agent manifests:

```bash
# Bank agent manifest (via Python sidecar)
curl http://localhost:8001/.well-known/agent-manifest

# Honeypot manifest (via sidecar)
curl http://localhost:8101/.well-known/agent-manifest
```

## Testing the Trust Protocol

### Scenario 1: Secure Transaction

Send a request through the secure bank sidecar:

```bash
curl -X POST http://localhost:8001/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "task": "transfer",
    "data": {
      "amount": 100,
      "from_account": "12345",
      "to_account": "67890"
    }
  }'
```

**Expected Result**: Transaction succeeds with trace ID in response headers.

## Using the IATP CLI

### Scan an Agent

Get a trust score for a running agent:

```bash
# Scan secure bank sidecar
iatp scan http://localhost:8001

# Scan honeypot sidecar
iatp scan http://localhost:8101
```

### Verify a Manifest

Validate a manifest file before deployment:

```bash
# Verify secure bank manifest
iatp verify examples/manifests/secure_bank.json

# Verify with verbose output
iatp verify examples/manifests/standard_agent.json --verbose
```

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| bank-agent | 8000 | Secure banking agent (internal) |
| iatp-sidecar-python | 8001 | Python sidecar (public) |
| iatp-sidecar-go | 8002 | Go sidecar (public, production) |
| honeypot-agent | 8100 | Untrusted agent (internal) |
| honeypot-sidecar | 8101 | Honeypot sidecar (public) |

## Configuration

### Environment Variables

Customize sidecar behavior via environment variables in `docker-compose.yml`:

```yaml
environment:
  - IATP_AGENT_URL=http://bank-agent:8000  # Backend agent URL
  - IATP_PORT=8001                          # Sidecar port
  - IATP_AGENT_ID=secure-bank-agent        # Agent identifier
  - IATP_TRUST_LEVEL=verified_partner      # Trust level
  - IATP_REVERSIBILITY=full                # Reversibility support
  - IATP_RETENTION=ephemeral               # Data retention policy
  - IATP_HUMAN_REVIEW=false                # Human review requirement
```

## Additional Resources

- [Main README](../README.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Quick Start Guide](../QUICKSTART.md)
