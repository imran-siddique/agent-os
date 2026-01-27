# emk - Episodic Memory Kernel

> **Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents

[![PyPI](https://img.shields.io/pypi/v/emk)](https://pypi.org/project/emk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/imran-siddique/emk/ci.yml?branch=main)](https://github.com/imran-siddique/emk/actions)

**An immutable, append-only ledger for agent experiences. Part of the Agent OS ecosystem.**

---

## Why emk?

Agents that cannot remember their past repeat the same mistakes. Traditional databases let you update or delete records—this is dangerous for agent memory. What if a bug overwrites critical learning? What if you need to audit agent decisions?

We built `emk` to **subtract the problem of mutable memory.** Instead of complex database transactions and state management, we provide a single abstraction: the immutable Episode. Once written, never changed. This constraint eliminates entire classes of bugs and enables reliable agent learning systems.

**Scale by Subtraction:** By removing the ability to modify history, we remove the need for complex versioning, rollback logic, and concurrency controls. The result is a memory system that scales reliably.

---

## Installation

```bash
pip install emk
```

---

## Quick Start

```python
from emk import Episode, FileAdapter

store = FileAdapter("agent_memory.jsonl")
episode = Episode(goal="Query user data", action="SELECT * FROM users", 
                  result="200 rows", reflection="Query was fast")
store.store(episode)
```

That's it. Five lines. Your agent's experience is now permanently recorded.

---

## Memory Management Features 🆕

`emk` now includes powerful memory management features to address the challenge: **Infinite memory leads to infinite retrieval costs and confusing context.**

### Memory Decay & Compression (Sleep Cycle)

Automatically summarize old episodes into semantic rules:

```python
from emk import MemoryCompressor

compressor = MemoryCompressor(store, age_threshold_days=30)
result = compressor.compress_old_episodes()
# Compress 1000 episodes → 20 semantic rules
```

**Benefits:** 50-100x storage reduction, faster retrieval, preserved knowledge without overwhelming detail.

### Negative Memory (Anti-Patterns)

Explicitly track failures to avoid repeating mistakes:

```python
# Mark failures
failed = episode.mark_as_failure(reason="Connection timeout")
store.store(failed)

# Query both successes AND failures
patterns = store.retrieve_with_anti_patterns()
print(f"What works: {len(patterns['successes'])}")
print(f"What to avoid: {len(patterns['failures'])}")
```

**Benefits:** Prune search space instantly, learn from both successes and failures, "DO NOT TOUCH" vectors.

📖 **Full documentation:** See [docs/MEMORY_MANAGEMENT.md](docs/MEMORY_MANAGEMENT.md) and [examples/memory_features_demo.py](examples/memory_features_demo.py)

---

## Architecture

`emk` sits at **Layer 1 (Primitives)** of the Agent OS stack. It provides the foundational storage abstraction that higher layers depend on:

- **Layer 1 (Primitives):** `emk` stores raw episodes. `caas` (Context-as-a-Service) reads from `emk` to build working memory. `cmvk` (Cryptographic Message Verification Kernel) may sign episodes for audit trails.
- **Layer 2 (Infrastructure):** `amb` (Agent Message Bus) transports messages. `iatp` (Inter-Agent Trust Protocol) verifies trust. These layers may log their own episodes into `emk`.
- **Layer 3 (Framework):** `agent-control-plane` orchestrates agents. `scak` (Self-Correction and Alignment Kernel) uses `emk` to learn from mistakes.

`emk` has **zero** dependencies on other Agent OS components. It is the foundation, not the application.

---

## The Ecosystem Map

`emk` is one component of the modular Agent OS. Here's how the pieces fit together:

| Layer              | Component                  | Purpose                                   | Repository                                      |
|--------------------|----------------------------|-------------------------------------------|-------------------------------------------------|
| **Primitives**     | `caas`                     | Context-as-a-Service (Working Memory)     | [caas](https://github.com/imran-siddique/caas)  |
| **Primitives**     | `cmvk`                     | Cryptographic Verification Kernel         | [cmvk](https://github.com/imran-siddique/cmvk)  |
| **Primitives**     | `emk`                      | Episodic Memory Kernel                    | [emk](https://github.com/imran-siddique/emk)    |
| **Infrastructure** | `iatp`                     | Inter-Agent Trust Protocol                | [iatp](https://github.com/imran-siddique/iatp)  |
| **Infrastructure** | `amb`                      | Agent Message Bus                         | [amb](https://github.com/imran-siddique/amb)    |
| **Infrastructure** | `atr`                      | Agent Tool Registry                       | [atr](https://github.com/imran-siddique/atr)    |
| **Framework**      | `agent-control-plane`      | Agent Orchestration and Control           | [agent-control-plane](https://github.com/imran-siddique/agent-control-plane) |
| **Framework**      | `scak`                     | Self-Correction and Alignment Kernel      | [scak](https://github.com/imran-siddique/scak)  |

Each component is independently useful. Together, they form a complete Agent Operating System.

---

## Citation

If you use `emk` in your research or production systems, please cite:

```bibtex
@software{emk2024,
  author       = {Siddique, Imran},
  title        = {emk: Episodic Memory Kernel for Agent Systems},
  year         = {2024},
  publisher    = {GitHub},
  url          = {https://github.com/imran-siddique/emk},
  note         = {Part of the Agent OS ecosystem}
}
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
