---
layout: default
title: FAQ
nav_order: 6
permalink: /faq/
description: "Frequently asked questions about Agent OS - the kernel architecture for AI agent governance."
---

# Frequently Asked Questions
{: .no_toc }

Common questions about Agent OS, answered.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## General Questions

### What is Agent OS?

Agent OS is a **kernel architecture for governing autonomous AI agents**. It applies operating system concepts (like Linux's process control) to AI agents, providing deterministic policy enforcement rather than relying on prompts to control agent behavior.

Instead of asking an agent "please don't do dangerous things" (and hoping it complies), Agent OS intercepts every action and **enforces policies before execution**. If an agent tries to do something blocked by policy, it's stopped—the agent has no choice in the matter.

### How is Agent OS different from LangChain or CrewAI?

**LangChain and CrewAI** are frameworks for **building agents**—they provide tools to create agent workflows, chain LLM calls, and orchestrate multiple agents.

**Agent OS** is infrastructure for **governing agents**—it wraps around any agent framework and enforces safety policies.

| | LangChain/CrewAI | Agent OS |
|:--|:-----------------|:---------|
| **Purpose** | Build agents | Govern agents |
| **Layer** | Application | Infrastructure |
| **Safety** | Prompt-based | Kernel-enforced |
| **Relationship** | You build with it | It wraps your agents |

**You can use them together**:
```python
from langchain.agents import AgentExecutor
from agent_os.integrations import LangChainKernel

kernel = LangChainKernel()
governed_agent = kernel.wrap(my_langchain_agent)
```

### Is Agent OS open source?

Yes. Agent OS is released under the MIT License. You can view, modify, and distribute the code freely.

[View on GitHub →](https://github.com/imran-siddique/agent-os)

### What programming languages does Agent OS support?

Agent OS is primarily a **Python library**. The core package (`agent-os`) requires Python 3.9+.

IDE extensions are available for VS Code, JetBrains IDEs, and Cursor, supporting any language you work with in those environments.

---

## Installation & Setup

### How do I install Agent OS?

```bash
pip install agent-os
```

For all features:
```bash
pip install agent-os[full]
```

For specific components:
```bash
pip install agent-os[cmvk]           # Cross-model verification
pip install agent-os[observability]  # Prometheus/OpenTelemetry
pip install agent-os[iatp]           # Inter-agent trust
```

### What are the system requirements?

- **Python**: 3.9 or higher
- **OS**: Linux, macOS, Windows
- **Memory**: Minimal overhead (~50MB for basic usage)
- **Dependencies**: `pydantic>=2.0.0` (core), additional deps based on extras

### Does Agent OS require API keys or external services?

**No.** The core Agent OS functionality runs entirely locally with no external dependencies.

Optional features may require API keys:
- **CMVK with cloud models**: Requires API keys for GPT-4, Claude, etc.
- **Observability**: May require Prometheus/Grafana setup

---

## Technical Questions

### What policies are included by default?

The `strict` policy (default) blocks:
- **File operations**: write, delete, modify
- **Database operations**: DROP, DELETE, TRUNCATE
- **Shell execution**: system(), exec(), subprocess
- **Secret exposure**: hardcoded API keys, passwords
- **Network calls** (optional): requests to unknown domains

### Can I create custom policies?

Yes. You can define policies in Python or YAML:

```python
from agent_os.policies import Policy, Pattern

policy = Policy(
    name="my-policy",
    blocked_actions=["file_write", "database_delete"],
    blocked_patterns=[
        Pattern(r"\bpassword\b", "PII detected"),
        Pattern(r"DROP\s+TABLE", "Destructive SQL")
    ]
)

kernel = KernelSpace(policy=policy)
```

Or in YAML:
```yaml
policies:
  - name: my-policy
    blocked_actions:
      - file_write
      - database_delete
    blocked_patterns:
      - pattern: "\\bpassword\\b"
        reason: "PII detected"
```

[See Custom Policies Documentation →](/docs/policies/)

### What happens when a policy is violated?

By default, a policy violation triggers **SIGKILL**—immediate termination of the agent action. The action is blocked **before it executes**.

You can configure different responses:
- **SIGKILL**: Terminate immediately (non-catchable)
- **SIGSTOP**: Pause for human review
- **SIGWARN**: Log a warning but continue

### How does Agent OS intercept agent actions?

Agent OS wraps agent functions with a governance layer. When you call `kernel.execute()`, the kernel:

1. Captures the function call and its arguments
2. Analyzes the code/data against active policies
3. If blocked → signals SIGKILL before execution
4. If allowed → executes the function and logs the result

This is similar to how operating system kernels intercept syscalls.

### Does Agent OS slow down my agents?

Minimal overhead. Policy checks typically add < 5ms per action. For most use cases, this is negligible compared to LLM latency (100ms+).

Benchmark results:
- Policy check: ~2-5ms average
- CMVK verification: ~100-500ms (depends on models)
- Memory operations (VFS): < 1ms

### Can I use Agent OS with async/await?

Yes. Agent OS is async-native:

```python
@kernel.register
async def my_agent(task: str):
    result = await some_async_operation()
    return result

result = await kernel.execute(my_agent, "task")
```

---

## Framework Integration

### How do I use Agent OS with LangChain?

```python
from langchain.agents import AgentExecutor
from agent_os.integrations import LangChainKernel

# Your existing LangChain agent
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Wrap with Agent OS
kernel = LangChainKernel()
governed_agent = kernel.wrap(agent_executor)

# Use the governed agent
result = governed_agent.invoke({"input": "analyze this data"})
```

[See Integrations Guide →](/docs/integrations/)

### How do I use Agent OS with CrewAI?

```python
from crewai import Crew
from agent_os.integrations import CrewAIKernel

# Your existing CrewAI crew
crew = Crew(agents=[agent1, agent2], tasks=[task1, task2])

# Wrap with Agent OS
kernel = CrewAIKernel()
governed_crew = kernel.wrap(crew)

# Run the governed crew
result = governed_crew.kickoff()
```

[See Integrations Guide →](/docs/integrations/)

### Does Agent OS work with OpenAI's Assistants API?

Yes:

```python
from openai import OpenAI
from agent_os.integrations import OpenAIKernel

client = OpenAI()
assistant = client.beta.assistants.create(...)

kernel = OpenAIKernel()
governed = kernel.wrap_assistant(assistant, client)
```

[See Integrations Guide →](/docs/integrations/)

---

## Security & Trust

### How does IATP (Inter-Agent Trust Protocol) work?

IATP provides cryptographic message signing between agents:

1. Each agent has a **public/private key pair**
2. Messages are **signed** with the sender's private key
3. Recipients **verify** signatures before processing
4. A **trust registry** tracks agent identities and trust levels

This ensures you know exactly which agent sent each message and that the message wasn't tampered with.

```python
from iatp import AgentIdentity, SignedMessage, TrustRegistry

# Create identity
agent = AgentIdentity.create("agent-001", "My Agent", ["capabilities"])

# Sign message
message = SignedMessage.create(sender=agent, recipient_id="agent-002", content={...})

# Verify
registry = TrustRegistry()
result = registry.verify(message)  # Returns verification result
```

[See IATP Documentation →](/docs/modules/iatp/)

### What is CMVK (Cross-Model Verification Kernel)?

CMVK detects hallucinations by comparing outputs across multiple LLMs:

1. Send the same prompt to multiple models (GPT-4, Claude, Gemini)
2. Compare their outputs for semantic similarity
3. If models agree → high confidence
4. If models disagree → flag for review

```python
from cmvk import ConsensusVerifier

verifier = ConsensusVerifier(models=["gpt-4", "claude-3", "gemini-pro"])
result = await verifier.verify_consensus(prompt, threshold=0.8)
```

[See CMVK Documentation →](/docs/modules/cmvk/)

### Can agents be revoked or banned?

Yes. The trust registry supports revocation:

```python
registry.revoke("agent-001", reason="Suspicious activity")
```

After revocation:
- Messages from the agent fail verification
- The agent's trust level becomes `NONE`
- Other agents refuse to communicate with it

---

## Production & Operations

### How do I monitor agents in production?

Agent OS integrates with standard observability tools:

**Prometheus Metrics**:
```python
# Enable metrics
kernel = KernelSpace(policy="strict", metrics=True)
```

Metrics exposed:
- `agent_os_violations_total` — Policy violations
- `agent_os_policy_check_duration_seconds` — Check latency
- `agent_os_sigkill_total` — Terminations

**OpenTelemetry Tracing**:
```python
from agent_os.observability import enable_tracing
enable_tracing()
```

**Grafana Dashboards**: Pre-built dashboards included in `/examples/`.

[See Observability Guide →](/docs/observability/)

### Can I use Agent OS in a distributed system?

Yes. Agent OS components are designed for distributed deployment:

- **AMB (Agent Message Bus)**: Supports Redis, Kafka, NATS, AWS SQS
- **IATP**: Works across network boundaries
- **Stateless kernel**: Each instance independent

### Is Agent OS production-ready?

Agent OS is functional and used in production by early adopters. The project is under active development, so expect API changes.

**What works well**:
- Policy engine with signal-based enforcement
- Framework integrations (LangChain, CrewAI, etc.)
- Observability (Prometheus, OpenTelemetry)
- IDE extensions

**What's experimental**:
- Benchmark numbers need independent verification
- Some integrations are basic wrappers

---

## Contributing

### How can I contribute to Agent OS?

We welcome contributions! See our [Contributing Guide](https://github.com/imran-siddique/agent-os/blob/main/CONTRIBUTING.md).

Ways to contribute:
- Report bugs and request features
- Improve documentation
- Add new framework integrations
- Write tests
- Review pull requests

### How do I report a bug?

Open an issue on GitHub: [Report Bug →](https://github.com/imran-siddique/agent-os/issues/new)

Include:
- Agent OS version
- Python version
- Minimal reproduction code
- Expected vs actual behavior

---

## Still Have Questions?

- [GitHub Discussions](https://github.com/imran-siddique/agent-os/discussions) — Ask the community
- [GitHub Issues](https://github.com/imran-siddique/agent-os/issues) — Report bugs
- [Documentation](/docs/) — Full docs
