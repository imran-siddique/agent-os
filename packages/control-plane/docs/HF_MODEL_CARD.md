---
license: MIT
tags:
  - ai-safety
  - agents
  - governance
  - control-plane
  - deterministic
  - agentic-ai
  - guardrails
language:
  - en
library_name: agent-control-plane
pipeline_tag: other
---

# Agent Control Plane (ACP)

[![PyPI version](https://badge.fury.io/py/agent-control-plane.svg)](https://badge.fury.io/py/agent-control-plane)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A **deterministic kernel** for zero-violation governance in agentic AI systems. ACP interposes between LLM intent and action execution, providing ABAC-based policy enforcement, constraint graphs, and shadow mode simulation.

> "Vibes are not engineering. We don't ask a database to 'please not drop tables' — we enforce permissions via ACLs."

## 🎯 Intended Use

**Primary Use Cases:**
- Enterprise AI agent governance and safety enforcement
- Multi-agent orchestration with policy-based access control (ABAC)
- Research into deterministic AI safety mechanisms
- Drop-in middleware for OpenAI, LangChain, and MCP-based agents
- Red team testing and safety benchmarking

**Out-of-Scope Uses:**
- ⚠️ Direct use as an LLM or chat model (this is a governance layer, not a model)
- ⚠️ Content moderation (this is action-level, not content-level governance)
- ⚠️ Replacing human oversight in safety-critical systems
- ⚠️ Guaranteed protection against all possible adversarial attacks

## ⚠️ Limitations

| Limitation | Details |
|------------|---------|
| **Policy Configuration Required** | ACP requires explicit policy configuration for each deployment. Default policies provide baseline protection but should be customized. |
| **Not a Silver Bullet** | Does not prevent all possible adversarial attacks. Defense-in-depth is required. |
| **Shadow Mode ≠ Production** | Shadow mode simulation does not guarantee real-world behavior. Always test in staging. |
| **Performance Overhead** | Latency scales with policy complexity. Complex constraint graphs add ~5-10ms overhead. |
| **No Content Analysis** | Governs actions, not content. Use complementary content moderation for text safety. |

## 📊 Evaluation Results

Results from the 60-prompt red team benchmark (`imran-siddique/agent-control-redteam-60`):

| Metric | Value | Notes |
|--------|-------|-------|
| **Safety Violation Rate** | 0.00% | All 60 adversarial prompts blocked |
| **False Positive Rate** | 0.00% | All legitimate actions permitted |
| **Token Reduction** | 98.1% | "Scale by Subtraction" vs verbose refusals |
| **Avg Latency Overhead** | <5ms | Per policy check (simple rules) |
| **P99 Latency** | <15ms | Per policy check (complex constraints) |

### Statistical Validation

| Ablation | Violation Rate | p-value | Cohen's d |
|----------|---------------|---------|-----------|
| Full ACP | 0.00% | - | - |
| Without PolicyEngine | 40.00% | <0.0001 | 8.7 |
| Without ConstraintGraphs | 15.00% | <0.001 | 4.2 |
| Without MuteAgent | 0.00% (token leak) | - | - |

## 🚀 Installation

```bash
pip install agent-control-plane
```

For Hugging Face Hub integration:
```bash
pip install agent-control-plane[hf]
# or
pip install agent-control-plane huggingface_hub datasets
```

## 📖 Quick Start

```python
from agent_control_plane import AgentControlPlane, create_governed_client

# Wrap any OpenAI-compatible client
governed_client = create_governed_client(
    openai_client,
    permission_level="read_only"  # NONE, READ_ONLY, READ_WRITE, ADMIN
)

# All tool calls are now governed
response = governed_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Read the Q3 sales report"}],
    tools=[{
        "type": "function",
        "function": {"name": "read_file", "parameters": {...}}
    }]
)
```

### With LangChain

```python
from agent_control_plane import create_governed_langchain_client

agent = create_governed_langchain_client(
    langchain_agent,
    permission_level="read_write"
)
```

### Shadow Mode (Simulation)

```python
control_plane = AgentControlPlane(
    enable_shadow_mode=True,
    enable_constraint_graphs=True
)

# Simulate without executing
result = control_plane.shadow_execute(
    agent_id="analyst",
    tool_name="database_query",
    tool_args={"query": "SELECT * FROM sensitive_data"}
)
print(f"Would be blocked: {result.would_block}")
```

## 📚 Resources

- **Paper**: [Agent Control Plane: A Deterministic Kernel for Zero-Violation Governance in Agentic AI](https://arxiv.org/abs/...)
- **Documentation**: [GitHub Docs](https://github.com/imran-siddique/agent-control-plane/tree/main/docs)
- **Red Team Dataset**: [imran-siddique/agent-control-redteam-60](https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60)
- **Reproducibility**: See `reproducibility/` folder for exact commands and configs

## 📜 Citation

If you use this work in your research, please cite:

```bibtex
@article{siddique2026acp,
  title={Agent Control Plane: A Deterministic Kernel for Zero-Violation Governance in Agentic AI},
  author={Siddique, Imran},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2026}
}
```

## 👤 Author

**Imran Siddique**  
Principal Group Engineering Manager, Microsoft  
[imran.siddique@microsoft.com](mailto:imran.siddique@microsoft.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/imran-siddique/agent-control-plane/blob/main/LICENSE) file for details.

---

*"The LLM is the CPU. The Control Plane is the Operating System."*
