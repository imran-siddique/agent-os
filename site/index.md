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

[Get Started in 5 Minutes](#getting-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/imran-siddique/agent-os){: .btn .fs-5 .mb-4 .mb-md-0 }

<div class="github-badges" markdown="1">
[![GitHub stars](https://img.shields.io/github/stars/imran-siddique/agent-os?style=social)](https://github.com/imran-siddique/agent-os)
[![PyPI version](https://img.shields.io/pypi/v/agent-os)](https://pypi.org/project/agent-os/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
</div>

</div>

---

## Quick Answers
{: .executive-summary }

<div class="faq-quick" markdown="1">

<details open>
<summary><strong>What is Agent OS?</strong></summary>
A kernel architecture that enforces safety policies on AI agents at runtime—like how Linux enforces permissions on applications. Your agents can't violate rules because the kernel blocks violations before execution.
</details>

<details>
<summary><strong>Who is it for?</strong></summary>
Teams deploying AI agents in production who need **compliance guarantees**, **audit trails**, and **runtime control**. Finance (trading bots), healthcare (patient data agents), DevOps (autonomous infrastructure), and any domain where "the AI went rogue" isn't acceptable.
</details>

<details>
<summary><strong>How is it different from LangChain's built-in safety?</strong></summary>
LangChain/CrewAI safety relies on prompts and callbacks—the agent decides whether to comply. Agent OS uses **kernel-level enforcement**—the agent has no choice. You can use both together: build with LangChain, govern with Agent OS.
</details>

<details>
<summary><strong>How fast can I get started?</strong></summary>
Two lines: `pip install agent-os` then wrap your agent. See [5-minute quickstart](#getting-started).
</details>

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

# 1. Create kernel with strict policy - blocks destructive operations
kernel = KernelSpace(policy="strict")

# 2. Register your agent function with the kernel
@kernel.register
async def my_agent(task: str):
    # Your LLM logic here - any framework works
    return f"Processed: {task}"

# 3. Execute through the kernel - all actions are policy-checked
import asyncio
result = asyncio.run(kernel.execute(my_agent, "Hello, Agent OS!"))
print(result)  # Output: Processed: Hello, Agent OS!
```

<div class="code-explanation" markdown="1">

| Line | What it does |
|:-----|:-------------|
| `KernelSpace(policy="strict")` | Creates a kernel that blocks file writes, destructive SQL, shell commands, and secret exposure |
| `@kernel.register` | Wraps your function so every call goes through the policy engine |
| `kernel.execute()` | Runs your agent with governance—violations trigger `SIGKILL` before execution |

</div>

### What Happens

1. **`@kernel.register`** wraps your function with kernel governance
2. **`kernel.execute()`** runs your agent through the policy engine
3. **If policy violated** → automatic `SIGKILL` before execution

[Read the Full Tutorial →](/docs/tutorials/quickstart/)
{: .fs-5 }

---

## What Teams Are Saying
{: #testimonials }

<div class="testimonials-grid" markdown="1">

> "Reduced our compliance review time from 2 weeks to 2 days. The audit logs alone saved us."
> {: .testimonial-quote }
> — **DevOps Lead**, Fortune 500 Financial Services
{: .testimonial }

> "We went from 'hoping the agent doesn't delete production data' to actually sleeping at night."
> {: .testimonial-quote }
> — **ML Platform Engineer**, Healthcare Startup
{: .testimonial }

> "The CMVK module caught 3 hallucination incidents in our first week that would have gone to customers."
> {: .testimonial-quote }
> — **AI Safety Researcher**, Enterprise SaaS
{: .testimonial }

</div>

<div class="cta-small" markdown="1">
**Have a story?** [Share it on GitHub Discussions →](https://github.com/imran-siddique/agent-os/discussions/categories/show-and-tell)
</div>

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

<div class="example-card" markdown="1">
### 🏦 Carbon Credit Auditor
**Finance / ESG**

Satellite-verified fraud detection. Multi-model consensus. 14.9% fraud rate caught.

[View Demo →](/use-cases/carbon-auditor/)
</div>

<div class="example-card" markdown="1">
### 💰 DeFi Risk Sentinel
**Cryptocurrency**

Sub-second attack detection. $4.7M value protected. 45ms p95 latency.

[View Demo →](/use-cases/defi-sentinel/)
</div>

<div class="example-card" markdown="1">
### ⚡ Grid Balancing Swarm
**Energy / IoT**

100 agents negotiating energy. 97.3% consensus rate. Zero violations.

[View Demo →](/use-cases/grid-balancing/)
</div>

<div class="example-card" markdown="1">
### 🏥 HIPAA-Compliant Data Agent
**Healthcare**

Patient data analysis with guaranteed PHI protection. Full audit trail for compliance.

[View Demo →](/use-cases/healthcare/)
</div>

<div class="example-card" markdown="1">
### 🎓 Safe Tutoring Bot
**Education**

Age-appropriate content filtering. No PII collection. Parent-visible audit logs.

[View Demo →](/use-cases/education/)
</div>

<div class="example-card" markdown="1">
### 🔧 Autonomous DevOps
**Infrastructure**

Self-healing infrastructure with guardrails. Can't delete prod, can't expose secrets.

[View Demo →](/use-cases/devops/)
</div>

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

## Roadmap & Transparency
{: #roadmap }

We believe in building in the open. Here's what's coming:

| Timeline | Feature | Status |
|:---------|:--------|:-------|
| **Q1 2026** | Multi-language SDKs (TypeScript, Go) | 🔄 In Progress |
| **Q2 2026** | Visual Policy Editor | 📋 Planned |
| **Q2 2026** | Large swarm support (1000+ agents) | 📋 Planned |
| **Q3 2026** | Declarative policy language (Rego-like) | 📋 Planned |
| **Q3 2026** | Enterprise SSO & RBAC | 📋 Planned |

<div class="limitations-box" markdown="1">

**Current Limitations:**
- Python-only (TypeScript SDK coming Q1 2026)
- Tested up to ~100 concurrent agents (scaling improvements underway)
- Requires Python 3.9+ (no legacy support planned)

[View full roadmap on GitHub →](https://github.com/imran-siddique/agent-os/projects)

</div>

---

## Community

<div class="community-links" markdown="1">

- [GitHub Discussions](https://github.com/imran-siddique/agent-os/discussions) — Ask questions, share ideas
- [GitHub Issues](https://github.com/imran-siddique/agent-os/issues) — Report bugs, request features
- [Contributing Guide](https://github.com/imran-siddique/agent-os/blob/main/CONTRIBUTING.md) — Help build Agent OS

</div>

<div class="social-share" markdown="1">

**Share Agent OS:**

[![Twitter](https://img.shields.io/badge/Share-Twitter-1DA1F2?logo=twitter&logoColor=white)](https://twitter.com/intent/tweet?text=Check%20out%20Agent%20OS%20-%20kernel-level%20governance%20for%20AI%20agents&url=https://imran-siddique.github.io/agent-os/)
[![LinkedIn](https://img.shields.io/badge/Share-LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/sharing/share-offsite/?url=https://imran-siddique.github.io/agent-os/)
[![Reddit](https://img.shields.io/badge/Share-Reddit-FF4500?logo=reddit&logoColor=white)](https://reddit.com/submit?url=https://imran-siddique.github.io/agent-os/&title=Agent%20OS%20-%20Kernel%20for%20AI%20Agent%20Governance)

</div>

---

## Stay Updated

Agent OS is actively developed. Star the repo to follow updates:

<div class="newsletter-signup" markdown="1">

[⭐ Star on GitHub](https://github.com/imran-siddique/agent-os){: .btn .btn-primary .fs-5 .mr-2 }
[📰 RSS Feed](/feed.xml){: .btn .fs-5 }

</div>

---

<div class="footer-cta" markdown="1">

## Ready to Govern Your Agents?

```bash
pip install agent-os
```

[Get Started →](/docs/tutorials/quickstart/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[Read the Docs →](/docs/){: .btn .fs-5 .mb-4 .mb-md-0 }

</div>
