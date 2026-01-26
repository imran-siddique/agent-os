# Release v0.1.0 - Initial Public Release

**EMK (Episodic Memory Kernel)** - An immutable, append-only ledger of agent experiences for AI systems.

## 🎯 Highlights

- **Immutable Storage**: Episodes follow the Goal → Action → Result → Reflection pattern
- **Pluggable Backends**: FileAdapter (JSONL) and ChromaDBAdapter (vector search)
- **Minimal Dependencies**: Core requires only `pydantic` and `numpy`
- **Research Ready**: Reproducible benchmarks, paper structure, HF Hub integration

## 📦 Installation

```bash
# Basic installation
pip install emk

# With vector search support
pip install emk[chromadb]

# With Hugging Face Hub integration
pip install emk[huggingface]

# Everything
pip install emk[all]
```

## 🚀 Quick Start

```python
from emk import Episode, FileAdapter

store = FileAdapter("memories.jsonl")

episode = Episode(
    goal="Retrieve user data",
    action="Query database",
    result="Success",
    reflection="Efficient query"
)

episode_id = store.store(episode)
```

## 📊 Performance (1000 episodes, seed=42)

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Episode Creation | 0.036ms | 27,694 ops/sec |
| Storage Write | 1.53ms | 652 ops/sec |
| Retrieval | 25.8ms | 39 ops/sec |
| Indexer | 0.088ms | 11,346 ops/sec |

## ✨ Features

### Core
- `Episode` - Immutable data structure with SHA-256 content-addressed IDs
- `FileAdapter` - JSONL-based local storage with metadata filtering
- `ChromaDBAdapter` - Vector similarity search (optional dependency)
- `Indexer` - Tag extraction and search text generation

### New in this release
- **GitHub Actions CI/CD** - Multi-platform testing, PyPI publishing with OIDC
- **Experiments** - Reproducible benchmark runner with fixed seeds
- **Hugging Face Integration** - Upload/download episodes to HF Hub
- **Research Paper** - Whitepaper structure for academic publication
- **PEP 561** - Typed package support with `py.typed` marker

## 📚 Documentation

- [README](https://github.com/imran-siddique/emk#readme)
- [Contributing Guide](https://github.com/imran-siddique/emk/blob/main/CONTRIBUTING.md)
- [Changelog](https://github.com/imran-siddique/emk/blob/main/CHANGELOG.md)

## 🔒 Security

- CodeQL scanning on all PRs
- Security policy in [SECURITY.md](https://github.com/imran-siddique/emk/blob/main/SECURITY.md)

---

**Full Changelog**: https://github.com/imran-siddique/emk/commits/v0.1.0
