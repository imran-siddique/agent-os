# Context-as-a-Service (CaaS)

[![PyPI](https://img.shields.io/pypi/v/caas-core.svg)](https://pypi.org/project/caas-core/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/imran-siddique/context-as-a-service/actions/workflows/ci.yml/badge.svg)](https://github.com/imran-siddique/context-as-a-service/actions/workflows/ci.yml)

**Stateless context management primitive for RAG systems. Part of the Agent OS ecosystem.**

---

## Philosophy: Why CaaS Exists

RAG systems fail because they treat context as a flat stream. Documents lose structure. Time becomes meaningless. Official docs conflict with reality. LLMs waste tokens on stale data.

We built CaaS to subtract these problems. No agent frameworks. No middleware dependencies. Just pure context logic that routes, prioritizes, and filters data based on deterministic rules.

**Scale by Subtraction:** Remove the coupling between context management and agent execution. CaaS processes text and metadata—nothing more. This constraint forces clarity and enables reuse across any agent system.

---

## Installation

```bash
pip install caas-core
```

---

## Quick Start

```python
from caas import ContextTriadManager, HeuristicRouter, DocumentStore

store = DocumentStore()
store.add_document({"content": "API auth uses JWT", "timestamp": "2025-01-15"})
router = HeuristicRouter()
decision = router.route("How does authentication work?")  # Returns ModelTier.FAST
```

CaaS provides stateless functions. You control storage, agents, and orchestration.

---

## Core Features

### 1. Virtual File System (Project State)

A lightweight in-memory file system that maintains project state shared across multiple SDLC agents.

```python
from caas import VirtualFileSystem

# Create shared VFS
vfs = VirtualFileSystem()

# Agent 1 creates a file
vfs.create_file("/project/main.py", "print('hello')", agent_id="agent-1")

# Agent 2 reads and updates the file
content = vfs.read_file("/project/main.py")
vfs.update_file("/project/main.py", "print('world')", agent_id="agent-2")

# View edit history
history = vfs.get_file_history("/project/main.py")
# Shows edits from both agents
```

**Why VFS?** SDLC agents don't just chat—they edit files. The VFS ensures all agents see each other's changes, enabling true multi-agent collaboration on codebases.

### 2. Context Management

---

## Architecture

CaaS sits in **Layer 1: Primitives** of the Agent OS.

- **Layer 1 (Primitives):** `caas` (Context), `cmvk` (Verification), `emk` (Memory)  
- **Layer 2 (Infrastructure):** `iatp` (Trust Protocol), `amb` (Message Bus), `atr` (Tool Registry)  
- **Layer 3 (Framework):** `agent-control-plane` (Core), `scak` (Self-Correction)

CaaS does not import `iatp` or `agent-control-plane`. It returns structured data that upper layers consume. This decoupling is intentional.

**Example:** The `ContextTriadManager` produces a `ContextTriadState` object. The `amb` message bus transports it. The `agent-control-plane` interprets it. Each layer operates independently.

---

## Key Features

### 🗂️ Virtual File System (Project State)
- **Multi-agent collaboration**: All agents see each other's file edits in real-time
- **Edit history**: Track who changed what and when
- **In-memory performance**: Fast operations with optional disk persistence
- **Path normalization**: Consistent file paths across agents
- **Use case**: SDLC agents collaboratively editing codebases

### 🎯 Context Routing & Management
- **Heuristic Router**: Zero-latency query routing to appropriate model tiers
- **Context Triad**: Hot/Warm/Cold context layers for optimal retrieval
- **Time Decay**: Prioritize recent information with configurable decay
- **Structure-aware**: Preserve document hierarchy and relationships

### 🔒 Enterprise Features
- **Trust Gateway**: On-premises deployment with security policies
- **Audit logging**: Complete audit trail of all operations
- **Conflict detection**: Identify conflicts between official docs and practical reality
- **Source citations**: Transparent provenance for all information

---

## The Ecosystem Map

CaaS is one component in a modular Agent Operating System. Related projects:

### Primitives (Layer 1)
- **[caas](https://github.com/imran-siddique/context-as-a-service)** — Context routing, triad management, RAG fallacy solutions  
- **cmvk** — Cryptographic verification for agent messages (planned)  
- **emk** — Episodic memory with time-decay and retrieval policies (planned)

### Infrastructure (Layer 2)
- **iatp** — Inter-Agent Trust Protocol for authenticated message exchange (planned)  
- **amb** — Agent Message Bus for decentralized pub/sub (planned)  
- **atr** — Agent Tool Registry with sandboxed execution (planned)

### Framework (Layer 3)
- **agent-control-plane** — Supervisor, orchestration, and failure handling (planned)  
- **scak** — Self-Correction Agent Kernel for adaptive refinement (planned)

CaaS is production-ready. Other components are in design or alpha stages.

---

## Citation

```bibtex
@software{caas2026,
  title        = {Context-as-a-Service: Stateless Primitives for RAG Systems},
  author       = {Siddique, Imran},
  year         = {2026},
  version      = {0.2.0},
  url          = {https://github.com/imran-siddique/context-as-a-service},
  note         = {Part of the Agent Operating System project}
}
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
