# Agent OS Quickstart

> **60 seconds to your first governed agent.**

## Prerequisites

- Python 3.10+
- pip

## Installation

```bash
pip install agent-os
```

Or with all extras:

```bash
pip install agent-os[full]
```

## Your First Governed Agent

### Step 1: Initialize

```bash
agentos init my-first-agent
cd my-first-agent
```

This creates:

```
my-first-agent/
├── .agents/
│   ├── agents.md        # Agent instructions (AGENTS.md compatible)
│   └── security.md      # Kernel policies
├── agent.py             # Your agent code
└── pyproject.toml
```

### Step 2: Review the Policies

```yaml
# .agents/security.md
kernel:
  version: "1.0"
  mode: strict

signals:
  - SIGSTOP   # Pause for inspection
  - SIGKILL   # Terminate on violation

policies:
  - name: read_only
    blocked_actions:
      - file_write
      - database_write
      - send_email
  
  - name: no_pii
    blocked_patterns:
      - "\\bssn\\b"
      - "\\bcredit.card\\b"
```

### Step 3: Write Your Agent

```python
# agent.py
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str):
    # Your LLM code here
    from openai import OpenAI
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": task}]
    )
    return response.choices[0].message.content

# Run with governance
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(kernel.execute(my_agent, "Summarize this document"))
    print(result)
```

### Step 4: Run It

```bash
agentos run
```

### What Just Happened?

1. **`agentos init`** created a `.agents/` directory with default policies
2. **`agentos run`** started the kernel with your agent in user space
3. If your agent tries anything unsafe → **automatic SIGKILL**

```
┌─────────────────────────────────────────────────────────┐
│              USER SPACE (Your Agent)                    │
│   my_agent() runs here. Can crash, hallucinate, etc.   │
├─────────────────────────────────────────────────────────┤
│              KERNEL SPACE (Agent OS)                    │
│   Policy Engine checks every action before execution    │
│   If policy violated → SIGKILL (non-catchable)         │
└─────────────────────────────────────────────────────────┘
```

---

## Try a Dangerous Action

Edit `agent.py` to attempt a blocked action:

```python
@kernel.register
async def my_agent(task: str):
    # This will be blocked by read_only policy!
    import os
    os.remove("/important/file.txt")  # ← SIGKILL
    return "Done"
```

Run it:

```bash
agentos run
```

Output:

```
⚠️  POLICY VIOLATION DETECTED
⚠️  Signal: SIGKILL
⚠️  Agent: my_agent
⚠️  Action: file_write
⚠️  Policy: read_only
⚠️  Status: TERMINATED

The kernel blocked the dangerous action before it executed.
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `agentos init <name>` | Initialize new agent project |
| `agentos run` | Run agent with kernel governance |
| `agentos secure` | Validate security configuration |
| `agentos audit` | Audit security policies |
| `agentos status` | Show kernel status |

### Templates

```bash
# Strict mode (default) - blocks writes, PII, shell
agentos init my-agent --template strict

# Permissive mode - logging only, no blocking
agentos init my-agent --template permissive

# Audit mode - logs everything, blocks nothing
agentos init my-agent --template audit
```

---

## Next Steps

| Tutorial | Description | Time |
|----------|-------------|------|
| [Carbon Auditor](../examples/carbon-auditor/) | Build a multi-agent fraud detection system | 15 min |
| [MCP Integration](mcp-integration.md) | Use Agent OS with Claude Desktop | 10 min |
| [Observability](observability.md) | Add Prometheus metrics and Grafana | 10 min |
| [Multi-Agent](multi-agent.md) | Connect agents with IATP trust protocol | 20 min |

---

## Common Issues

### "Command not found: agentos"

```bash
# Ensure the package is installed
pip install agent-os

# Or check your PATH
python -m agent_os.cli --help
```

### "Policy violation but I expected it to pass"

Check your `.agents/security.md`:

```bash
agentos audit
```

This shows which policies are active and what they block.

### "Agent runs but nothing happens"

Ensure you're using `@kernel.register`:

```python
# ✗ Wrong - not governed
async def my_agent(task):
    return llm(task)

# ✓ Correct - governed by kernel
@kernel.register
async def my_agent(task):
    return llm(task)
```

---

## Get Help

- [GitHub Issues](https://github.com/imran-siddique/agent-os/issues)
- [Documentation](https://github.com/imran-siddique/agent-os/tree/main/docs)
- [Examples](https://github.com/imran-siddique/agent-os/tree/main/examples)

---

<div align="center">

**Ready to build something real?**

[Carbon Auditor Tutorial →](../examples/carbon-auditor/)

</div>
