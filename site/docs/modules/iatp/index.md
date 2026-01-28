---
layout: default
title: IATP
parent: Modules
nav_order: 3
permalink: /docs/modules/iatp/
description: "Inter-Agent Trust Protocol - cryptographic signing and verification for multi-agent systems."
---

# IATP - Inter-Agent Trust Protocol
{: .fs-9 }

Cryptographic signing and verification for multi-agent communication.
{: .fs-6 .fw-300 }

---

## Overview

IATP ensures that agents can trust messages from other agents through cryptographic signatures. Every message is signed by the sender and can be verified by the recipient.

## Quick Start

```python
from agent_os.iatp import AgentIdentity, SignedMessage, TrustRegistry, TrustLevel

# Create agent identity
agent = AgentIdentity.create(
    agent_id="agent-001",
    name="Data Analyst",
    capabilities=["sql_read", "file_read"]
)

# Sign a message
message = SignedMessage.create(
    sender=agent,
    recipient_id="agent-002",
    content={"type": "request", "data": "analyze sales"}
)

# Verify message
registry = TrustRegistry()
registry.register(agent, TrustLevel.HIGH)
result = registry.verify(message)

print(result.valid)       # True
print(result.trust_level) # TrustLevel.HIGH
```

## Key Features

- **Agent identity** — Ed25519 key pairs for each agent
- **Message signing** — Cryptographic proof of sender
- **Trust levels** — HIGH, MEDIUM, LOW, UNTRUSTED
- **Revocation** — Immediately revoke compromised agents
- **Audit trail** — All trust decisions logged

## Trust Levels

| Level | Meaning | Use Case |
|:------|:--------|:---------|
| `HIGH` | Fully trusted | Internal, verified agents |
| `MEDIUM` | Trusted with limits | Partner agents |
| `LOW` | Minimal trust | New or external agents |
| `UNTRUSTED` | Not trusted | Blocked agents |

## API Reference

See [API Reference](/docs/api/) for complete documentation.

---

[Back to Modules →](/docs/modules/)
