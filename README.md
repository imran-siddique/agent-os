# Context-as-a-Service (CaaS)

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/context-as-a-service.svg)](https://pypi.org/project/context-as-a-service/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/imran-siddique/context-as-a-service/actions/workflows/ci.yml/badge.svg)](https://github.com/imran-siddique/context-as-a-service/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![HF Dataset](https://img.shields.io/badge/🤗%20Dataset-CaaS%20Benchmark-yellow)](https://huggingface.co/datasets/imran-siddique/context-as-a-service)

**Intelligent context pipeline solving 7 RAG fallacies — deterministic, heuristic, enterprise-trust focused.**

[Quick Start](#-quick-start) • [Features](#-key-features) • [Documentation](docs/) • [Benchmarks](benchmarks/) • [Paper](paper/) • [Contributing](CONTRIBUTING.md)

</div>

---

## 🎯 Why CaaS?

Traditional RAG systems suffer from **7 major fallacies** that lead to poor context quality:

| Fallacy | Problem | CaaS Solution |
|---------|---------|---------------|
| **Flat Chunk** | All content treated equally | **Structure-Aware Indexing** with value tiers |
| **Context Amnesia** | Chunks lose document context | **Metadata Injection** preserves lineage |
| **Time-Blind** | Old content ranks same as new | **Time Decay** prioritizes recency |
| **Flat Context** | No priority between context types | **Context Triad** (Hot/Warm/Cold) |
| **Official Truth** | Only official docs, missing real fixes | **Pragmatic Truth** tracks both sources |
| **Brutal Squeeze** | Lossy summarization of history | **Sliding Window** keeps recent turns intact |
| **Middleware Gap** | Data leakage to third-party routers | **Trust Gateway** for on-prem deployment |

---

## 🚀 Quick Start

### Installation

```bash
# From PyPI (recommended)
pip install context-as-a-service

# From source (development)
git clone https://github.com/imran-siddique/context-as-a-service.git
cd context-as-a-service
pip install -e ".[dev]"

# With Docker
docker-compose up --build
```

### 30-Second Example

```python
from caas.storage.document_store import DocumentStore
from caas.ingestion.pdf_processor import PDFProcessor
from caas.triad import ContextTriad

# 1. Ingest a document
store = DocumentStore()
processor = PDFProcessor()
doc = processor.process("contract.pdf", "Employment Contract")
store.add_document(doc)

# 2. Get intelligent context (Hot/Warm/Cold tiers)
triad = ContextTriad(store)
context = triad.hot_context.get_context("termination clause", max_tokens=2000)

# 3. Use with transparent citations
for chunk in context['chunks']:
    print(f"[{chunk['source']}] {chunk['content'][:100]}...")
```

### CLI Usage

```bash
caas ingest contract.pdf pdf "Employment Contract"
caas context <doc_id> "termination clause"
caas list
```

### Start the API Server

```bash
uvicorn caas.api.server:app --reload
# API docs: http://localhost:8000/docs
```

---

## ✨ Key Features

### 🏗️ Structure-Aware Indexing
Three-tier hierarchical value system — class definitions > comments > whitespace.

### 🧬 Metadata Injection  
Chunks carry their lineage: "Q3 Report > Revenue > North America" not just "increased by 5%".

### ⏰ Time-Based Decay
Recent content ranks higher. 2025 docs beat 2021 docs with identical keywords.

### 🔥 Context Triad
- **Hot**: Current conversation (high priority)
- **Warm**: User preferences/session (medium)  
- **Cold**: Historical archives (low)

### 💡 Pragmatic Truth
Tracks OFFICIAL docs + PRACTICAL sources (Slack/GitHub). Detects conflicts: "Docs say 100, team knows 50".

### ⚡ Heuristic Router
Zero-latency routing using deterministic rules. No LLM calls needed for routing decisions.

### ✂️ Sliding Window
FIFO conversation management. Keeps last N turns perfectly intact — no lossy summarization.

### 🔐 Trust Gateway
Enterprise-grade on-prem router. Zero data leakage to third-party middleware.

---

## 📁 Project Structure

```
context-as-a-service/
├── src/caas/              # Main package (src layout)
│   ├── api/               # FastAPI endpoints
│   ├── detection/         # Document type detection
│   ├── gateway/           # Trust gateway implementation
│   ├── ingestion/         # PDF, HTML, code processors
│   ├── routing/           # Heuristic router
│   ├── storage/           # Document store
│   └── tuning/            # Auto-weight optimization
├── tests/                 # Comprehensive test suite
├── docs/                  # Feature documentation
├── examples/
│   ├── demos/             # Feature demos
│   ├── usage/             # Usage examples
│   └── agents/            # Agent implementations
├── benchmarks/            # Evaluation & reproducibility
└── paper/                 # Research paper artifacts
```

---

## 📖 Documentation

| Topic | Description |
|-------|-------------|
| [Context Triad](docs/CONTEXT_TRIAD.md) | Hot/Warm/Cold priority system |
| [Pragmatic Truth](docs/PRAGMATIC_TRUTH.md) | Official vs. practical sources |
| [Heuristic Router](docs/HEURISTIC_ROUTER.md) | Zero-latency query routing |
| [Trust Gateway](docs/TRUST_GATEWAY.md) | Enterprise on-prem deployment |
| [Time Decay](docs/SLIDING_WINDOW.md) | Temporal relevance scoring |
| [Metadata Injection](docs/METADATA_INJECTION.md) | Context-aware chunk enrichment |
| [Structure-Aware](docs/STRUCTURE_AWARE_INDEXING.md) | Hierarchical value indexing |
| [Ethics & Limitations](docs/ETHICS_AND_LIMITATIONS.md) | Responsible AI considerations |
| [Threat Model](docs/THREAT_MODEL.md) | Security architecture |
| [Reproducibility](docs/REPRODUCIBILITY.md) | Benchmark reproduction guide |

---

## 📊 Benchmarks

| Component | Improvement | vs. Baseline |
|-----------|-------------|--------------|
| Structure-Aware | +18.5% | Flat chunking |
| Time Decay | +12.3% | Time-blind retrieval |
| Pragmatic Truth | +15.7% | Official-only |
| Heuristic Router | 0.1ms | vs 150ms LLM routing |
| Context Triad | +22.1% | Flat context stuffing |

**Reproduce results:**
```bash
cd benchmarks
python run_evaluation.py --dataset hf://imran-siddique/context-as-a-service
python statistical_tests.py  # p < 0.05 significance tests
```

See [benchmarks/README.md](benchmarks/README.md) for full methodology.

---

## 🔌 API Reference

### Ingest Document
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@doc.pdf" -F "format=pdf" -F "title=My Doc"
```

### Get Context
```bash
curl -X POST "http://localhost:8000/context/{doc_id}" \
  -H "Content-Type: application/json" \
  -d '{"query": "search term", "max_tokens": 2000}'
```

### List Documents
```bash
curl "http://localhost:8000/documents"
```

Full API docs at `/docs` when server is running.

---

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
pre-commit run --all-files

# Type checking
mypy src/caas
```

---

## 🐳 Docker

```bash
# Development
docker-compose up --build

# Production
docker build -t caas:latest .
docker run -p 8000:8000 caas:latest
```

---

## 📄 Citation

If you use CaaS in your research, please cite:

```bibtex
@software{caas2026,
  title = {Context-as-a-Service: Solving Seven Fallacies in Production RAG Systems},
  author = {Siddique, Imran},
  year = {2026},
  url = {https://github.com/imran-siddique/context-as-a-service}
}
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Make your changes
4. Run tests (`pytest`)
5. Submit a PR

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**[⬆ Back to top](#context-as-a-service-caas)**

Made with ❤️ for the RAG community

</div>
