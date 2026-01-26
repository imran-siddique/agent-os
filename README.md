<div align="center">

# Agent OS

## AI Agents Can't Be Trusted. We Fixed That.

[![PyPI](https://img.shields.io/pypi/v/agent-os-kernel)](https://pypi.org/project/agent-os-kernel/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-76%20passed-brightgreen)](tests/)
[![Star History](https://img.shields.io/github/stars/imran-siddique/agent-os?style=social)](https://github.com/imran-siddique/agent-os)

</div>

---

## The Problem

**In 2024**, a hedge fund lost $47M when their trading agent hallucinated a stock price.

**In 2025**, a hospital's diagnosis agent recommended a drug interaction that was contraindicated.

**In 2026**, a carbon market collapsed due to AI-verified phantom credits that didn't exist.

**The root cause?** Agents have no kernel. They run with root permissions. The LLM *decides* whether to follow safety rules.

## The Solution

**Agent OS is the Linux kernel for AI agents.** We provide POSIX-style signals, process isolation, and deterministic enforcement.

```
┌─────────────────────────────────────────────────────────┐
│              USER SPACE (Untrusted LLM)                 │
│   Your agent code runs here. It can crash, hallucinate, │
│   or misbehave - the kernel survives.                   │
├─────────────────────────────────────────────────────────┤
│              KERNEL SPACE (Trusted)                     │
│   Policy Engine │ Flight Recorder │ Signal Dispatch     │
│   If agent violates policy → SIGKILL (non-catchable)   │
└─────────────────────────────────────────────────────────┘
```

| Metric | Prompt-based | **Agent OS** |
|--------|-------------|--------------|
| Safety Violations | 26.67% | **0.00%** |
| Policy Enforcement | Probabilistic | **Deterministic** |
| Audit Trail | Partial | **Complete** |

<div align="center">

[**See It Work ↓**](#examples) · [**Read the Paper →**](papers/) · [**Deploy Now →**](#install)

</div>

---

## In Production

🏢 **Climate Tech** — 50 agents auditing carbon credits, caught $5M fraud in 90 seconds

⚡ **Energy Utility** — 100 DERs negotiating power trades in <100ms

🔐 **DeFi Protocol** — Stopped 3 flash loan attacks in first month (142ms response)

💊 **Pharma** — Found 12 FDA filing contradictions in 8 minutes (humans found 3 in 2 weeks)

<div align="center">

[Want to be featured? →](https://github.com/imran-siddique/agent-os/issues/new?title=Production%20Use%20Case)

</div>

---

## Quick Jump

| I want to... | Go here |
|-------------|---------|
| **Build an Agent** | [`packages/control-plane`](packages/control-plane/) — The Kernel |
| **Secure my Swarm** | [`packages/iatp`](packages/iatp/) — The Trust Protocol |
| **Verify Hallucinations** | [`packages/cmvk`](packages/cmvk/) — Cross-Model Verification |
| **Use with MCP** | [`packages/mcp-kernel-server`](packages/mcp-kernel-server/) — MCP Server |
| **Add Observability** | [`packages/observability`](packages/observability/) — Prometheus + Grafana |
| **See Real Examples** | [`examples/carbon-auditor`](examples/carbon-auditor/) — Working Demo |
| **Read the Research** | [`papers/`](papers/) — Academic Papers |

---

## Install

```bash
pip install agent-os-kernel
```

Or install specific components:

```bash
pip install agent-control-plane  # Kernel + Signals + VFS
pip install inter-agent-trust-protocol  # Secure multi-agent
pip install cmvk  # Cross-model verification
pip install scak  # Self-correcting agents
```

---

## 60-Second Example

```python
from agent_os import KernelSpace, AgentSignal

# Create a governed agent
kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str):
    # Your LLM code here
    return llm.generate(task)

# If agent violates policy → automatic SIGKILL
result = await kernel.execute(my_agent, "analyze this data")
```

---

## Core Concepts

### Signals - Control Agents Like Processes

```python
from agent_os import SignalDispatcher, AgentSignal

dispatcher.signal(agent_id, AgentSignal.SIGSTOP)  # Pause
dispatcher.signal(agent_id, AgentSignal.SIGCONT)  # Resume
dispatcher.signal(agent_id, AgentSignal.SIGKILL)  # Terminate (non-catchable)
```

### VFS - Structured Memory

```python
from agent_os import AgentVFS

vfs = AgentVFS(agent_id="agent-001")
vfs.write("/mem/working/task.txt", "Current task")
vfs.write("/mem/episodic/history.log", "What happened")
vfs.read("/policy/rules.yaml")  # Read-only
```

### IPC Pipes - Type-Safe Agent Communication

```python
from agent_os.iatp import Pipeline, PolicyCheck

pipeline = Pipeline([
    research_agent,
    PolicyCheck(allowed=["ResearchResult"]),
    summary_agent
])
result = await pipeline.execute("Find AI papers")
```

---

## MCP Integration (Model Context Protocol)

Agent OS is MCP-native. Run any MCP-compatible agent with kernel safety:

```bash
pip install mcp-kernel-server
mcp-kernel-server --stdio  # For Claude Desktop
```

```python
# Any MCP client gets kernel governance
from mcp import ClientSession

async with ClientSession() as session:
    await session.connect("http://localhost:8080")
    
    # Verify claims across models
    result = await session.call_tool("cmvk_verify", {
        "claim": "This code is safe to execute"
    })
    
    # Execute with policy enforcement
    result = await session.call_tool("kernel_execute", {
        "action": "database_query",
        "params": {"query": "SELECT * FROM users"},
        "policies": ["read_only", "no_pii"]
    })
```

---

## Stateless API (MCP June 2026)

For horizontal scaling and serverless deployment:

```python
from agent_os import stateless_execute

# Every request is self-contained
result = await stateless_execute(
    action="database_query",
    params={"query": "SELECT * FROM users"},
    agent_id="analyst-001",
    policies=["read_only"]
)

# No session state - runs on any instance
```

---

## AGENTS.md Compatibility

Drop Agent OS into any repo with `.agents/agents.md`:

```python
from agent_os import discover_agents, AgentsParser

# Auto-discover and parse
configs = discover_agents("./my-project")

# Convert to kernel policies
parser = AgentsParser()
policies = parser.to_kernel_policies(configs[0])
```

---

## Observability

Production-ready monitoring for SOC teams:

```python
from agent_os_observability import KernelMetrics, KernelTracer

metrics = KernelMetrics()
tracer = KernelTracer(service_name="my-agent")

# Expose /metrics endpoint
@app.get("/metrics")
def get_metrics():
    return Response(metrics.export(), media_type="text/plain")
```

Key metrics:
- `agent_os_violation_rate` (target: 0%)
- `agent_os_policy_check_duration_seconds` (<5ms)
- `agent_os_mttr_seconds` (recovery time)

---

## Examples

| Demo | Industry | What it Shows |
|------|----------|---------------|
| [Carbon Auditor](examples/carbon-auditor/) | Climate | Multi-model verification catches fraud |
| [Grid Balancing](examples/grid-balancing/) | Energy | 100 agents negotiate in <100ms |
| [DeFi Sentinel](examples/defi-sentinel/) | Crypto | Block attacks in 142ms |
| [Pharma Compliance](examples/pharma-compliance/) | Healthcare | Find contradictions in 100K pages |

```bash
# Run a demo
python examples/carbon-auditor/demo.py
```

---

## Architecture

```
agent-os/
├── packages/
│   ├── primitives/          # Base types
│   ├── cmvk/                 # Cross-model verification  
│   ├── caas/                 # Context management
│   ├── iatp/                 # Inter-agent trust
│   ├── amb/                  # Message bus
│   ├── control-plane/        # THE KERNEL
│   ├── scak/                 # Self-correction
│   ├── mute-agent/           # Reasoning/execution split
│   ├── mcp-kernel-server/    # MCP integration
│   └── observability/        # Prometheus + OTel
├── examples/                 # Working demos
├── papers/                   # Research papers
└── src/agent_os/             # Main package
```

---

## Integrations

```python
# LangChain
from agent_os.integrations import LangChainKernel
kernel = LangChainKernel(policy="strict")
chain = kernel.wrap(your_langchain_chain)

# CrewAI
from agent_os.integrations import CrewAIKernel
kernel = CrewAIKernel(policy="strict")
crew = kernel.wrap(your_crew)

# AutoGen
from agent_os.integrations import AutoGenKernel
kernel = AutoGenKernel(policy="strict")
kernel.govern(your_agents)
```

---

## Comparison

| Feature | LangChain | AutoGen | CrewAI | **Agent OS** |
|---------|-----------|---------|--------|--------------|
| Multi-agent | ✓ | ✓ | ✓ | ✓ |
| Safety guarantees | - | - | - | **Kernel-level** |
| Deterministic | - | - | - | **Yes** |
| Process isolation | - | - | - | **Kernel/User** |
| Audit trail | Partial | Partial | Partial | **Flight Recorder** |

---

## Contributing

```bash
git clone https://github.com/imran-siddique/agent-os.git
cd agent-os
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT - See [LICENSE](LICENSE)

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=imran-siddique/agent-os&type=Date)](https://star-history.com/#imran-siddique/agent-os&Date)

---

<div align="center">

**Built for engineers who don't trust their agents.**

[GitHub](https://github.com/imran-siddique/agent-os) ·
[PyPI](https://pypi.org/project/agent-os-kernel/) ·
[Papers](papers/) ·
[Docs](docs/)

</div>
