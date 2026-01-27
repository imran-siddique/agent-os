# CMVK - Cross-Model Verification Kernel

> **Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents

[![PyPI version](https://badge.fury.io/py/cmvk.svg)](https://badge.fury.io/py/cmvk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Mathematical drift detection between outputs—pure functions, zero dependencies on agent logic.**

---

## 🧠 Why CMVK?

Agent systems fail when they cannot measure semantic drift. LLMs hallucinate, models diverge, and outputs degrade without quantifiable verification. The naive approach couples verification logic directly into agent control loops, creating brittle, untestable architectures.

**CMVK exists because verification is a primitive, not a feature.** We subtract LLM calls, agent orchestration, and correction loops from the verification layer. What remains is a pure mathematical kernel: `verify(a, b) -> score`. This separation enables composition—verification becomes a reusable building block across the Agent OS stack.

*Scale by Subtraction:* Remove dependencies on external services. CMVK uses only `numpy` (and optionally `scipy`). No API keys. No network calls. No side effects. Just deterministic drift calculation.

---

## 📦 Installation

```bash
pip install cmvk
```

For enhanced statistical functions:
```bash
pip install cmvk[scipy]
```

---

## ⚡ Quick Start

```python
from cmvk import verify

score = verify("def add(a, b): return a + b", "def add(x, y): return x + y")
print(f"Drift: {score.drift_score:.3f}")  # 0.0 = identical
```

That's it. Five lines, zero configuration. `verify()` returns a `VerificationScore` with drift magnitude (0.0-1.0), confidence, and classification (semantic, structural, numerical, or lexical).

---

## 🏗️ Architecture

CMVK sits at **Layer 1 (Primitives)** of the Agent OS. It provides low-level mathematical operations that higher layers depend on:

```
┌─────────────────────────────────────────┐
│  Layer 3: Framework (agent-control-plane)│
│  ├─ Self-Correction Loop (scak)         │
│  └─ Orchestration Logic                 │
└─────────────────────────────────────────┘
              ▲
              │ uses verification scores
              │
┌─────────────────────────────────────────┐
│  Layer 2: Infrastructure                │
│  ├─ iatp: Trust Protocol                │
│  ├─ amb: Message Bus                    │
│  └─ atr: Tool Registry                  │
└─────────────────────────────────────────┘
              ▲
              │ composes primitives
              │
┌─────────────────────────────────────────┐
│  Layer 1: Primitives (THIS LAYER)       │
│  ├─ cmvk: Verification (THIS PROJECT) * │
│  ├─ caas: Context-as-a-Service          │
│  └─ emk: Episodic Memory Kernel         │
└──────────────────────────────────────────┘
```

**Design Principle:** CMVK never calls external services. Higher layers (like `scak`) orchestrate correction loops *using* CMVK's verification scores. This inverted dependency enables testing, composability, and deterministic behavior.

**API Surface:**
- `verify(a, b)` — High-level text comparison
- `verify_embeddings(emb_a, emb_b)` — Vector comparison (cosine, euclidean)
- `verify_distributions(dist_a, dist_b)` — Distribution comparison (KL divergence, JS divergence)
- `verify_sequences(seq_a, seq_b)` — Sequence comparison (edit distance, LCS)
- `verify_batch(...)` — Batch operations with aggregation

All functions return immutable `VerificationScore` objects:
```python
@dataclass(frozen=True)
class VerificationScore:
    drift_score: float      # 0.0 (identical) to 1.0 (completely different)
    confidence: float       # 0.0 to 1.0
    drift_type: DriftType   # SEMANTIC | STRUCTURAL | NUMERICAL | LEXICAL
    details: dict           # Component scores and metadata
```

---

## 🗺️ Agent OS Ecosystem

CMVK is one component of a modular Agent Operating System. Each project solves a single problem without assuming the existence of others.

### Layer 1: Primitives
- **[caas](https://github.com/imran-siddique/caas)** — Context-as-a-Service: Efficient context window management
- **[cmvk](https://github.com/imran-siddique/cross-model-verification-kernel)** (this project) — Verification: Drift detection between outputs
- **[emk](https://github.com/imran-siddique/emk)** — Episodic Memory Kernel: Long-term memory for agents

### Layer 2: Infrastructure
- **[iatp](https://github.com/imran-siddique/iatp)** — Inter-Agent Trust Protocol: Cryptographic verification of agent messages
- **[amb](https://github.com/imran-siddique/amb)** — Agent Message Bus: Decoupled communication between agents
- **[atr](https://github.com/imran-siddique/atr)** — Agent Tool Registry: Dynamic tool discovery and invocation

### Layer 3: Framework
- **[agent-control-plane](https://github.com/imran-siddique/agent-control-plane)** — The Core: Orchestrates primitives and infrastructure
- **[scak](https://github.com/imran-siddique/scak)** — Self-Correction Agent Kernel: Verification-driven correction loops

**Philosophy:** Each layer subtracts complexity from the layer above. Primitives have zero cross-dependencies. Infrastructure composes primitives. Framework orchestrates infrastructure.

---

## 📚 Citation

If you use CMVK in research or production systems, please cite:

```bibtex
@software{cmvk2024,
  author = {Siddique, Imran},
  title = {CMVK: Cross-Model Verification Kernel},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/imran-siddique/cross-model-verification-kernel},
  note = {Part of the Agent OS ecosystem}
}
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Repository:** [github.com/imran-siddique/cross-model-verification-kernel](https://github.com/imran-siddique/cross-model-verification-kernel)
- **PyPI:** [cmvk](https://pypi.org/project/cmvk/)
- **Issues:** [GitHub Issues](https://github.com/imran-siddique/cross-model-verification-kernel/issues)
- **Changelog:** [CHANGELOG.md](https://github.com/imran-siddique/cross-model-verification-kernel/blob/main/CHANGELOG.md)
