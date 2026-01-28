---
layout: default
title: 5-Minute Quickstart
parent: Tutorials
grand_parent: Documentation
nav_order: 1
permalink: /docs/tutorials/quickstart/
description: "Get started with Agent OS in 5 minutes. Install, create your first governed agent, and see policy enforcement in action."
---

# 5-Minute Quickstart
{: .no_toc }

Get from zero to governed agent in 5 minutes.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## TL;DR

```bash
pip install agent-os
```

```python
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str):
    return f"Processed: {task}"

import asyncio
result = asyncio.run(kernel.execute(my_agent, "Hello!"))
print(result)
```

That's it. Your agent now runs with kernel-level policy enforcement.

---

## Step 1: Install Agent OS

```bash
pip install agent-os
```

**Optional extras:**

```bash
pip install agent-os[cmvk]           # Cross-model verification
pip install agent-os[observability]  # Prometheus/OpenTelemetry
pip install agent-os[full]           # Everything
```

---

## Step 2: Create Your First Agent

Create a file called `my_agent.py`:

```python
from agent_os import KernelSpace

# Initialize the kernel with strict policy
kernel = KernelSpace(policy="strict")

@kernel.register
async def analyze_data(task: str):
    """Your agent logic goes here."""
    # This could be any LLM call, data processing, etc.
    return f"Analysis complete: {task}"

# Execute with governance
if __name__ == "__main__":
    import asyncio
    
    result = asyncio.run(
        kernel.execute(analyze_data, "Summarize Q4 sales data")
    )
    print(result)
```

---

## Step 3: Run It

```bash
python my_agent.py
```

Output:
```
Analysis complete: Summarize Q4 sales data
```

---

## What Just Happened?

```
┌─────────────────────────────────────────────────────────┐
│              USER SPACE (Your Code)                     │
│   analyze_data() runs here                              │
├─────────────────────────────────────────────────────────┤
│              KERNEL SPACE (Agent OS)                    │
│   Every action checked against policies                 │
│   Violations → SIGKILL (non-catchable)                  │
└─────────────────────────────────────────────────────────┘
```

1. **`@kernel.register`** wraps your function with kernel governance
2. **`kernel.execute()`** runs your agent through the policy engine
3. **If policy violated** → automatic SIGKILL before execution

---

## Step 4: See Policy Enforcement

Try a dangerous operation:

```python
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

@kernel.register
async def dangerous_agent(task: str):
    import os
    os.remove("/etc/passwd")  # ← This will be blocked!
    return "Done"

if __name__ == "__main__":
    import asyncio
    try:
        result = asyncio.run(kernel.execute(dangerous_agent, "cleanup"))
    except Exception as e:
        print(f"Blocked: {e}")
```

Output:
```
⚠️  POLICY VIOLATION DETECTED
⚠️  Signal: SIGKILL
⚠️  Action: file_write
⚠️  Status: TERMINATED

Blocked: Policy violation: file_write blocked by 'strict' policy
```

The kernel blocked the action **before** it executed.

---

## Step 5: Add an LLM (Optional)

```python
from agent_os import KernelSpace
from openai import OpenAI

kernel = KernelSpace(policy="strict")
client = OpenAI()

@kernel.register
async def smart_agent(task: str):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": task}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(kernel.execute(smart_agent, "What is 2+2?"))
    print(result)
```

---

## Common Patterns

### Wrap LangChain

```python
from agent_os.integrations import LangChainKernel

kernel = LangChainKernel()
governed = kernel.wrap(my_langchain_agent)
```

### Wrap CrewAI

```python
from agent_os.integrations import CrewAIKernel

kernel = CrewAIKernel()
governed = kernel.wrap(my_crew)
```

### Wrap OpenAI Assistants

```python
from agent_os.integrations import OpenAIKernel

kernel = OpenAIKernel()
governed = kernel.wrap_assistant(assistant, client)
```

---

## Next Steps

| Resource | What You'll Learn |
|:---------|:------------------|
| [Policy Reference](/docs/policies/) | Complete policy language docs |
| [Integrations](/docs/integrations/) | Framework-specific guides |
| [Modules](/docs/modules/) | CMVK, EMK, IATP, AMB |

---

## FAQ

### Do I need to change my agent code?

Minimal changes. Wrap your function with `@kernel.register` and call via `kernel.execute()`.

### What policies are included?

The `strict` policy blocks: file writes/deletes, destructive SQL, shell commands, secret exposure.

### Can I customize policies?

Yes. See [Policy Reference](/docs/policies/).

### Does it work with async code?

Yes. Agent OS is async-native.

---

## Get Help

- [GitHub Issues](https://github.com/imran-siddique/agent-os/issues) — Report bugs
- [GitHub Discussions](https://github.com/imran-siddique/agent-os/discussions) — Ask questions
- [Full FAQ](/faq/) — Common questions
