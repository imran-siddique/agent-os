---
layout: default
title: AMB
parent: Modules
nav_order: 4
permalink: /docs/modules/amb/
description: "Agent Message Bus - decoupled communication between agents with multiple backend support."
---

# AMB - Agent Message Bus
{: .fs-9 }

Decoupled communication between agents with pub/sub and request/reply patterns.
{: .fs-6 .fw-300 }

---

## Overview

AMB provides a message bus for agent-to-agent communication. Agents can publish messages to topics and subscribe to receive messages, without knowing about each other directly.

## Quick Start

```python
from agent_os.amb import MessageBus
from agent_os.amb.adapters import RedisBroker

# Create bus with Redis backend
broker = RedisBroker(url="redis://localhost:6379")
bus = MessageBus(broker)

# Publish message
await bus.publish("agent.tasks", {
    "type": "analyze",
    "data": "sales_q4"
})

# Subscribe to messages
async def handler(message):
    print(f"Received: {message}")

await bus.subscribe("agent.results", handler)
```

## Key Features

- **Multiple backends** — Redis, Kafka, NATS, SQS, in-memory
- **Pub/sub** — One-to-many messaging
- **Request/reply** — Synchronous-style communication
- **Message routing** — Route messages based on content
- **Dead letter queues** — Handle failed messages

## Backends

| Backend | Best For |
|:--------|:---------|
| `InMemoryBroker` | Testing, development |
| `RedisBroker` | Low-latency, simple setup |
| `KafkaBroker` | High-throughput, durability |
| `NATSBroker` | Lightweight, cloud-native |
| `SQSBroker` | AWS integration |

## Message Patterns

### Pub/Sub

```python
# Publisher
await bus.publish("events.user.created", user_data)

# Subscriber
await bus.subscribe("events.user.*", handle_user_events)
```

### Request/Reply

```python
# Request
response = await bus.request("services.analyzer", {
    "action": "analyze",
    "data": payload
}, timeout=30)
```

## API Reference

See [API Reference](/docs/api/) for complete documentation.

---

[Back to Modules →](/docs/modules/)
