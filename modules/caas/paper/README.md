# Paper: Context-as-a-Service

This directory contains materials for the academic paper submission.

## 📂 Structure

```
paper/
├── README.md              # This file
├── CHECKLIST.md           # Submission checklist (NeurIPS/ICML/ACL style)
├── LLM_DISCLOSURE.md      # AI assistance disclosure statement
├── abstract.md            # Working abstract draft
├── figures/               # Diagrams and visualizations
│   └── .gitkeep
├── tables/                # Result tables (generated from benchmarks)
│   └── .gitkeep
└── latex/                 # LaTeX source (when ready)
    └── .gitkeep
```

## 📋 Submission Targets

| Venue | Deadline | Format | Status |
|-------|----------|--------|--------|
| NeurIPS 2026 | May 2026 | 9 pages | 🎯 Target |
| ICML 2026 | Feb 2026 | 8 pages | Backup |
| ACL 2026 | TBD | 8 pages | NLP focus |
| EMNLP 2026 | TBD | 8 pages | NLP focus |

## 🏷️ Working Title

**"Context-as-a-Service: A Principled Architecture for Enterprise RAG Systems"**

Alternative titles:
- "Beyond Flat Chunks: Structure-Aware Context Extraction for LLMs"
- "Seven Fallacies of Context Management in Production RAG Systems"
- "The Trust Gateway: Enterprise-Grade Context Routing for LLMs"

## 📝 Key Contributions

1. **The Seven Fallacies Framework** - Taxonomy of common RAG pitfalls
2. **Structure-Aware Indexing** - Three-tier value hierarchy (not flat chunks)
3. **Context Triad** - Hot/Warm/Cold intimacy-based prioritization
4. **Pragmatic Truth** - Official vs. practical knowledge tracking
5. **Trust Gateway** - Enterprise-grade on-prem routing architecture
6. **Heuristic Router** - Zero-latency deterministic query routing
7. **Open Benchmark Corpus** - 16-document enterprise evaluation set

## 🔗 Resources

- **Code**: https://github.com/imran-siddique/context-as-a-service
- **PyPI**: https://pypi.org/project/context-as-a-service/
- **Dataset**: https://huggingface.co/datasets/imran-siddique/context-as-a-service
- **Docs**: https://github.com/imran-siddique/context-as-a-service/tree/main/docs

## 📊 Generating Results

```bash
# Run benchmark evaluation
python benchmarks/run_evaluation.py --corpus-path benchmarks/data/sample_corpus/

# Generate statistical comparisons  
python benchmarks/statistical_tests.py

# Output tables for paper
python benchmarks/run_evaluation.py --output paper/tables/
```

## ✅ Pre-submission Checklist

See [CHECKLIST.md](CHECKLIST.md) for the full submission checklist.
