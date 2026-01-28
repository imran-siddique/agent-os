---
layout: default
title: Core Concepts
parent: Documentation
nav_order: 1
has_children: true
permalink: /docs/concepts/
description: "Understand the core concepts of Agent OS: kernel architecture, policy engine, signals, and virtual file system."
---

# Core Concepts

Agent OS applies operating system principles to AI agent governance. Understanding these concepts will help you design safer, more controllable agent systems.

---

## The Core Idea

**Traditional agent safety** relies on prompts:
```
"Please don't delete important files"
```
The agent decides whether to comply.

**Agent OS safety** relies on enforcement:
```
Every action → Policy Engine → Allow or Block
```
The kernel decides. The agent has no choice.

---

## Key Concepts

### 1. Kernel Space vs User Space

```
┌─────────────────────────────────────────────────────────┐
│              USER SPACE (Agent Code)                    │
│   Your agent code runs here. Can crash, hallucinate,    │
│   try dangerous things—but the kernel intercepts first. │
├─────────────────────────────────────────────────────────┤
│              KERNEL SPACE (Agent OS)                    │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│   │Policy Engine│  │Flight Recorder│ │Signal Dispatch│   │
│   └─────────────┘  └─────────────┘  └─────────────┘    │
│   Actions are checked, logged, and controlled here.     │
└─────────────────────────────────────────────────────────┘
```

**User Space**: Where your agent code runs. It can try anything.

**Kernel Space**: Where Agent OS runs. It intercepts every action and decides whether to allow it based on policies.

[Learn more about Kernel Architecture →](/docs/concepts/kernel/)

---

### 2. Policy Engine

Policies define what agents can and cannot do:

```yaml
policies:
  - name: read_only
    blocked_actions:
      - file_write
      - file_delete
      - database_write
    
  - name: no_pii
    blocked_patterns:
      - "\\bssn\\b"
      - "\\bcredit.card\\b"
```

When an agent tries a blocked action, it's stopped **before execution**.

[Learn more about Policies →](/docs/concepts/policies/)

---

### 3. Signals (POSIX-Style Control)

Agent OS uses POSIX-style signals to control agent execution:

| Signal | Description | Catchable? |
|:-------|:------------|:-----------|
| `SIGKILL` | Terminate immediately | No |
| `SIGSTOP` | Pause for human review | No |
| `SIGCONT` | Resume execution | N/A |
| `SIGTERM` | Graceful termination | Yes |

```python
from agent_os import SignalDispatcher, AgentSignal

dispatcher.signal(agent_id, AgentSignal.SIGSTOP)  # Pause
dispatcher.signal(agent_id, AgentSignal.SIGCONT)  # Resume
dispatcher.signal(agent_id, AgentSignal.SIGKILL)  # Terminate
```

[Learn more about Signals →](/docs/concepts/signals/)

---

### 4. Virtual File System (VFS)

Agents have isolated, structured memory via VFS:

```
/
├── mem/
│   ├── working/     # Agent's scratch space (read/write)
│   ├── episodic/    # Historical episodes (read-only)
│   └── semantic/    # Long-term knowledge (read-only)
├── policy/          # Active policies (read-only)
└── proc/            # Agent process info (read-only)
```

```python
from agent_os import AgentVFS

vfs = AgentVFS(agent_id="agent-001")
vfs.write("/mem/working/task.txt", "Current task")
vfs.read("/policy/rules.yaml")  # Read-only from user space
```

[Learn more about VFS →](/docs/concepts/vfs/)

---

## POSIX Inspiration

Agent OS borrows heavily from POSIX operating systems:

| POSIX Concept | Agent OS Equivalent | Purpose |
|:--------------|:--------------------|:--------|
| Process | Agent | Unit of execution |
| Kernel | KernelSpace | Enforces rules |
| Syscalls | `kernel.execute()` | Request resources |
| Signals | `AgentSignal` | Control execution |
| `/proc` | `/mem/`, `/proc/` | Agent state |
| Permissions | Policies | Access control |

---

## Next Steps

<div class="next-steps" markdown="1">

- [Kernel Architecture](/docs/concepts/kernel/) — Deep dive into kernel design
- [Policy Engine](/docs/concepts/policies/) — Define agent permissions
- [Signals](/docs/concepts/signals/) — Control agent execution
- [VFS](/docs/concepts/vfs/) — Agent memory and state

</div>
