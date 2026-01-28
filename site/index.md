---
layout: home
title: Home
nav_order: 1
description: "Agent OS - The kernel architecture for governing autonomous AI agents with deterministic policy enforcement."
permalink: /
---

<div class="hero" markdown="1">

# The Operating System for AI Agents
{: .fs-9 }

Kernel-level governance for autonomous AI agents. Stop hoping your agents behave—**enforce it**.
{: .fs-6 .fw-300 }

[Get Started Now](#getting-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/imran-siddique/agent-os){: .btn .fs-5 .mb-4 .mb-md-0 }

</div>

---

## The Problem with AI Agents Today

Traditional agent safety relies on **prompts**: *"Please don't do dangerous things."*

The agent decides whether to comply. That's not safety—that's hope.

```
Prompt-Based Safety:          Kernel-Based Safety:
                              
  "Please be safe"              Every action is checked
         ↓                             ↓
  LLM decides to comply         Kernel decides to allow
         ↓                             ↓
  Maybe it doesn't 🤷           No choice - blocked or allowed
```

## Agent OS: Kernel-Level Enforcement

Agent OS applies operating system concepts to AI agent governance. Just like Linux doesn't ask applications to behave—it **enforces permissions**—Agent OS doesn't ask agents to be safe—it **enforces policies**.

```python
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str):
    # Your agent code here
    return process(task)

# Every action is checked against policies
result = await kernel.execute(my_agent, "analyze data")
```

{: .highlight }
> **Zero violations.** Not because agents are trained to behave, but because the kernel won't let violations execute.

---

## Key Features

<div class="features-grid" markdown="1">

### 🛡️ Policy Engine
{: .text-purple-000 }
Define what agents can and cannot do. Block destructive SQL, file deletes, secret exposure—before execution.

### ⚡ POSIX Signals
{: .text-purple-000 }
`SIGKILL`, `SIGSTOP`, `SIGCONT`—control agent execution like processes. Non-catchable termination on violations.

### 🔍 Cross-Model Verification
{: .text-purple-000 }
Verify outputs across multiple LLMs. Detect hallucinations through consensus, not trust.

### 🧠 Episodic Memory
{: .text-purple-000 }
Immutable, append-only ledger of agent experiences. Time-travel debugging. Learn from mistakes.

### 🤝 Inter-Agent Trust
{: .text-purple-000 }
Cryptographic signing of messages between agents. Know exactly who said what.

### 📊 Full Observability
{: .text-purple-000 }
Prometheus metrics, OpenTelemetry tracing, Grafana dashboards—see everything your agents do.

</div>

---

## Getting Started
{: #getting-started }

### Installation

```bash
pip install agent-os
```

Or with all features:

```bash
pip install agent-os[full]
```

### Your First Governed Agent

```python
from agent_os import KernelSpace

# Create kernel with strict policy
kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str):
    # Your LLM logic here
    return f"Processed: {task}"

# Run with governance
import asyncio
result = asyncio.run(kernel.execute(my_agent, "Hello, Agent OS!"))
print(result)
```

### What Happens

1. **`@kernel.register`** wraps your function with kernel governance
2. **`kernel.execute()`** runs your agent through the policy engine
3. **If policy violated** → automatic `SIGKILL` before execution

[Read the Full Tutorial →](/docs/tutorials/quickstart/)
{: .fs-5 }

---

## Framework Integrations

Agent OS wraps existing frameworks—use it with what you already have:

| Framework | Integration |
|:----------|:------------|
| **LangChain** | `LangChainKernel().wrap(my_chain)` |
| **CrewAI** | `CrewAIKernel().wrap(my_crew)` |
| **OpenAI Assistants** | `OpenAIKernel().wrap_assistant(assistant)` |
| **Semantic Kernel** | `SemanticKernelWrapper().wrap(kernel)` |
| **AutoGen** | `AutoGenKernel().wrap(agents)` |

[See All Integrations →](/docs/integrations/)

---

## IDE & CLI Extensions

Use Agent OS directly in your development environment:

| Tool | Description |
|:-----|:------------|
| **VS Code** | Real-time policy checks, kernel debugger, memory browser |
| **Cursor** | Composer interception, safe alternatives |
| **JetBrains** | IntelliJ, PyCharm, WebStorm plugins |
| **GitHub Copilot** | Safety layer for AI suggestions |
| **Chrome DevTools** | Monitor AMB messages and IATP trust |

[Browse Extensions →](/docs/extensions/)

---

## Production Examples

See Agent OS in action with full observability:

<div class="examples-grid" markdown="1">

### Carbon Credit Auditor
Satellite-verified fraud detection. Multi-model consensus. 14.9% fraud rate caught.

[View Demo →](/use-cases/carbon-auditor/)

### DeFi Risk Sentinel
Sub-second attack detection. $4.7M value protected. 45ms p95 latency.

[View Demo →](/use-cases/defi-sentinel/)

### Grid Balancing Swarm
100 agents negotiating energy. 97.3% consensus rate. Zero violations.

[View Demo →](/use-cases/grid-balancing/)

</div>

---

## Why Agent OS?

| | Traditional Approach | Agent OS |
|:--|:---------------------|:---------|
| **Safety** | Prompt-based (hope) | Kernel-enforced (guarantee) |
| **Violations** | Detected after the fact | Blocked before execution |
| **Audit** | Logs if you remember | Complete immutable ledger |
| **Control** | Restart the whole thing | SIGSTOP/SIGCONT any agent |
| **Trust** | "I think it's working" | Cryptographic verification |

[Read the Full Comparison →](/compare/)

---

## Community

<div class="community-links" markdown="1">

- [GitHub Discussions](https://github.com/imran-siddique/agent-os/discussions) — Ask questions, share ideas
- [GitHub Issues](https://github.com/imran-siddique/agent-os/issues) — Report bugs, request features
- [Contributing Guide](https://github.com/imran-siddique/agent-os/blob/main/CONTRIBUTING.md) — Help build Agent OS

</div>

---

## Stay Updated

Agent OS is actively developed. Star the repo to follow updates:

[⭐ Star on GitHub](https://github.com/imran-siddique/agent-os){: .btn .btn-primary .fs-5 }

---

<div class="footer-cta" markdown="1">

## Ready to Govern Your Agents?

```bash
pip install agent-os
```

[Get Started →](/docs/tutorials/quickstart/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[Read the Docs →](/docs/){: .btn .fs-5 .mb-4 .mb-md-0 }

</div>
