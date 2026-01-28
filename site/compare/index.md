---
layout: default
title: Compare
nav_order: 5
has_children: true
permalink: /compare/
description: "Compare Agent OS with other AI agent frameworks like LangChain, CrewAI, AutoGen, and more."
---

# Agent OS Comparisons
{: .no_toc }

Understand how Agent OS differs from other tools in the AI agent ecosystem.
{: .fs-6 .fw-300 }

---

## Quick Comparison

| Feature | Agent OS | LangChain | CrewAI | AutoGen |
|:--------|:---------|:----------|:-------|:--------|
| **Primary Purpose** | Govern agents | Build agents | Build crews | Build conversations |
| **Safety Model** | Kernel-enforced | Prompt-based | Prompt-based | Prompt-based |
| **Policy Enforcement** | Deterministic | None built-in | None built-in | None built-in |
| **Audit Trail** | Immutable ledger | Callbacks | Callbacks | Callbacks |
| **Process Control** | SIGKILL/SIGSTOP | None | None | None |
| **Works With** | All frameworks | N/A | N/A | N/A |

---

## Understanding the Difference

### Building vs. Governing

**LangChain, CrewAI, and AutoGen** are frameworks for **building AI agents**. They provide:
- Tools for chaining LLM calls
- Abstractions for agent workflows
- Integrations with various models and services

**Agent OS** is infrastructure for **governing AI agents**. It provides:
- Policy enforcement before actions execute
- Deterministic safety guarantees
- Audit trails and observability
- Process control (pause, resume, terminate)

**They solve different problems.** You can—and often should—use them together:

```python
# Build with LangChain
from langchain.agents import AgentExecutor
agent = AgentExecutor(agent=..., tools=...)

# Govern with Agent OS
from agent_os.integrations import LangChainKernel
kernel = LangChainKernel()
governed_agent = kernel.wrap(agent)
```

---

## Detailed Comparisons

### [Agent OS vs LangChain](/compare/langchain/)

LangChain is an application framework for building LLM-powered applications. Agent OS is a governance layer that wraps LangChain agents.

| | Agent OS | LangChain |
|:--|:---------|:----------|
| **What it does** | Enforces safety policies | Chains LLM calls |
| **Safety approach** | Kernel intercepts actions | Callbacks (optional) |
| **Can block actions** | Yes, before execution | No (only observe) |
| **Audit trail** | Built-in, immutable | Via callbacks |
| **Best for** | Production safety | Rapid prototyping |

[Read full comparison →](/compare/langchain/)

---

### [Agent OS vs CrewAI](/compare/crewai/)

CrewAI is a framework for orchestrating role-playing AI agents. Agent OS governs those agents.

| | Agent OS | CrewAI |
|:--|:---------|:-------|
| **What it does** | Governs agent execution | Orchestrates agent teams |
| **Agent design** | Framework-agnostic | Role-based crews |
| **Safety** | Deterministic enforcement | Prompt-based |
| **Process control** | SIGKILL/SIGSTOP/SIGCONT | None |
| **Best for** | Safety & compliance | Multi-agent workflows |

[Read full comparison →](/compare/crewai/)

---

### [Agent OS vs AutoGen](/compare/autogen/)

AutoGen (Microsoft) is a framework for multi-agent conversations. Agent OS provides safety infrastructure.

| | Agent OS | AutoGen |
|:--|:---------|:--------|
| **What it does** | Enforces policies | Enables agent conversations |
| **Paradigm** | Governance layer | Conversational agents |
| **Safety** | Kernel-enforced | Human-in-the-loop |
| **Audit** | Immutable ledger | Conversation logs |
| **Best for** | Deterministic safety | Research & prototyping |

[Read full comparison →](/compare/autogen/)

---

### [Agent OS vs Semantic Kernel](/compare/semantic-kernel/)

Semantic Kernel (Microsoft) is an SDK for building AI applications. Agent OS adds governance.

| | Agent OS | Semantic Kernel |
|:--|:---------|:----------------|
| **What it does** | Governs AI agents | Builds AI apps |
| **Design** | Linux kernel model | Plugin architecture |
| **Safety** | Deterministic | Prompt-based |
| **Enterprise ready** | Yes (SOC 2 support) | Yes |
| **Best for** | Safety requirements | Enterprise AI apps |

[Read full comparison →](/compare/semantic-kernel/)

---

## Why Not Just Use Guardrails/Prompts?

Traditional "safety" for AI agents relies on:

1. **System prompts**: "You are a helpful assistant that never does harmful things..."
2. **Guardrail prompts**: "Before each action, check if it's safe..."
3. **Output filters**: Scan outputs for dangerous patterns

**The problem**: The LLM decides whether to comply. You're hoping, not enforcing.

**Agent OS is different**:

```
Prompt-based:                 Kernel-based:
                              
Agent decides to comply       Kernel decides to allow
       ↓                             ↓
Maybe it does                 Deterministic
Maybe it doesn't              No exceptions
```

### Real Example

**Prompt-based guardrail**:
```python
prompt = """
Before executing any action, verify it's safe.
Never delete files or drop database tables.
"""
# Agent might still do it if it "reasons" it's necessary
```

**Agent OS kernel**:
```python
policy = Policy(blocked_actions=["file_delete", "database_drop"])
kernel = KernelSpace(policy=policy)

# Agent CAN'T delete files or drop tables
# The kernel blocks it before execution
```

---

## When to Use Agent OS

### Use Agent OS when you need:

✅ **Deterministic safety** — Actions blocked before execution, not after
✅ **Audit compliance** — Immutable logs of every action
✅ **Process control** — Pause, resume, or terminate agents
✅ **Multi-agent trust** — Cryptographic verification of agent messages
✅ **Production deployment** — Enterprise-grade safety for AI systems

### Use other frameworks when you need:

✅ **Rapid prototyping** — LangChain, CrewAI are great for quick experiments
✅ **Building agent logic** — Define what agents do (then govern with Agent OS)
✅ **Research** — AutoGen is excellent for exploring multi-agent dynamics

### Best practice: Use both

1. **Build** your agents with LangChain, CrewAI, or AutoGen
2. **Govern** them with Agent OS before production

```python
# 1. Build with your favorite framework
from crewai import Crew, Agent, Task
crew = Crew(agents=[...], tasks=[...])

# 2. Govern with Agent OS
from agent_os.integrations import CrewAIKernel
kernel = CrewAIKernel(policy="strict")
governed_crew = kernel.wrap(crew)

# 3. Deploy safely
result = governed_crew.kickoff()
```

---

## Still Deciding?

- [Try the 5-Minute Quickstart](/docs/tutorials/quickstart/) — See Agent OS in action
- [Read the FAQ](/faq/) — Common questions answered
- [View Examples](/use-cases/) — Real-world use cases
