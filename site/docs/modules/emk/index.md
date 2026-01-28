---
layout: default
title: EMK
parent: Modules
nav_order: 2
permalink: /docs/modules/emk/
description: "Episodic Memory Kernel - immutable, append-only ledger of agent experiences with time-travel debugging."
---

# EMK - Episodic Memory Kernel
{: .fs-9 }

Immutable, append-only ledger of agent experiences. Time-travel debugging.
{: .fs-6 .fw-300 }

---

## Overview

EMK provides agents with persistent memory that cannot be modified—only appended. This enables complete audit trails and the ability to "replay" agent behavior from any point in time.

## Quick Start

```python
from agent_os.emk import Episode, MemoryStore, FileAdapter

store = MemoryStore(FileAdapter("memory.jsonl"))

episode = Episode(
    goal="Query user data",
    action="SELECT * FROM users WHERE active=true",
    result="Retrieved 200 rows",
    reflection="Query was fast, results as expected"
)

store.store(episode)

# Retrieve by semantic search
similar = store.search("database queries", limit=5)
```

## Key Features

- **Immutable episodes** — Cannot be modified after storage
- **Semantic search** — Find relevant memories by meaning
- **Time-travel debugging** — Replay agent behavior from checkpoints
- **Memory compression** — "Sleep cycles" consolidate memories
- **Negative memory** — Learn from failures and anti-patterns

## Storage Backends

| Backend | Use Case |
|:--------|:---------|
| `FileAdapter` | Development, small scale |
| `SQLiteAdapter` | Single-node production |
| `PostgresAdapter` | Multi-node, enterprise |
| `RedisAdapter` | High-performance caching |

## API Reference

See [API Reference](/docs/api/) for complete documentation.

---

[Back to Modules →](/docs/modules/)
