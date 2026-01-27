# arXiv Submission Metadata

**Submission Package**: `arxiv_submission.tar` (399 KB)  
**Generated**: January 22, 2026

---

## Required Metadata Fields

### Title
```
Context-as-a-Service: A Principled Architecture for Enterprise RAG Systems
```

### Authors
```
Imran Siddique
Microsoft
imran.siddique@microsoft.com
```

### Abstract
```
Retrieval-Augmented Generation (RAG) systems have become essential for grounding LLM outputs in factual content. However, production deployments face seven critical fallacies that current frameworks fail to address: (1) the Flat Chunk Fallacy, treating all content equally regardless of structural importance; (2) Context Amnesia, losing metadata when chunks are extracted; (3) Time-Blind Retrieval, ignoring content freshness; (4) Flat Context, lacking priority tiers for different context types; (5) Official Truth Fallacy, favoring documentation over practical knowledge; (6) Brutal Squeeze, using lossy summarization instead of precision truncation; and (7) the Middleware Gap, trusting third-party routers with sensitive data.

We present Context-as-a-Service (CaaS), an open-source framework that systematically addresses these challenges through five novel components: (a) Structure-Aware Indexing with three-tier value hierarchies; (b) Context Triad for Hot/Warm/Cold intimacy-based prioritization; (c) Pragmatic Truth tracking that surfaces practical knowledge alongside official sources; (d) Heuristic Router for zero-latency deterministic query routing; and (e) Trust Gateway for enterprise-grade on-premises deployment.

We evaluate CaaS on a new benchmark corpus of 16 enterprise documents spanning code, legal, HR, and engineering domains. Our experiments demonstrate 28.1% improvement in Precision@5 and 27.9% improvement in NDCG@10 over flat-chunk baselines, with sub-millisecond routing latency (0.003ms) and only 18.4% latency overhead for the full pipeline. CaaS is available as an open-source Python package with MIT license, Docker support, and a public Hugging Face dataset for reproducibility.
```

### Categories

**Primary Category**:
```
cs.AI - Artificial Intelligence
```

**Cross-list Categories** (select all that apply):
```
cs.CL - Computation and Language
cs.IR - Information Retrieval
cs.SE - Software Engineering
```

### Comments Field
```
Code: https://github.com/imran-siddique/context-as-a-service
PyPI: https://pypi.org/project/context-as-a-service/
Dataset: https://huggingface.co/datasets/imran-siddique/context-as-a-service
12 pages, 4 figures, 9 tables
```

### License
```
CC BY 4.0 (Creative Commons Attribution 4.0 International)
```

### ACM Classification (optional)
```
I.2.7 Natural Language Processing
H.3.3 Information Search and Retrieval
```

### Keywords (for discoverability)
```
Retrieval-Augmented Generation, RAG, Enterprise AI, Context Management, LLM, Large Language Models, Information Retrieval, Context Window, Document Indexing, Accumulation Paradox
```

---

## Submission Checklist

### Before Submission
- [x] Update author names and affiliations in `main.tex` (line ~52)
- [x] Update email addresses in `main.tex`
- [ ] Verify all figures render correctly
- [ ] Verify all citations compile without errors
- [ ] Run spell check on abstract and paper
- [ ] Verify URLs in Comments field are accessible

### Package Contents
- [x] `main.tex` - Main LaTeX source (20.7 KB)
- [x] `references.bib` - BibTeX bibliography with 17 entries (6.2 KB)
- [x] `figures/fig1_system_architecture.png` - System architecture (105 KB)
- [x] `figures/fig2_context_triad.png` - Context Triad diagram (115 KB)
- [x] `figures/fig3_ablation_results.png` - Ablation study (83 KB)
- [x] `figures/fig4_routing_latency.png` - Routing latency (72 KB)

**Total Package Size**: 399 KB (well under arXiv's 10 MB limit)

### Compilation Instructions
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## Key References Added (Accumulation Paradox)

The following verified citations were added to support the Accumulation Paradox concept:

1. **Liu et al. (2023)** - "Lost in the Middle: How Language Models Use Long Contexts"
   - Venue: TACL
   - arXiv: 2307.03172
   - Key contribution: U-shaped performance curve in long contexts

2. **Xiao et al. (2024)** - "Efficient Streaming Language Models with Attention Sinks"
   - Venue: ICLR 2024
   - arXiv: 2309.17453
   - Key contribution: Attention sink phenomenon

3. **Li et al. (2024)** - "Long-context LLMs Struggle with Long In-context Learning"
   - Venue: arXiv preprint
   - arXiv: 2404.02060
   - Key contribution: Performance degradation with accumulated context

4. **Packer et al. (2023)** - "MemGPT: Towards LLMs as Operating Systems"
   - Venue: arXiv preprint
   - arXiv: 2310.08560
   - Key contribution: Virtual context management for agentic AI

---

## arXiv Submission Steps

1. Go to: https://arxiv.org/submit
2. Sign in or create an arXiv account
3. Click "Start New Submission"
4. Select primary category: **cs.AI**
5. Add cross-list categories: **cs.CL**, **cs.IR**
6. Fill in metadata from fields above
7. Upload `arxiv_submission.tar`
8. Select license: **CC BY 4.0**
9. Add comments with code/data URLs
10. Preview PDF compilation
11. Submit for moderation

**Expected Processing Time**: 1-2 business days for moderation

---

*All citations in this submission are verified as real and accurate.*
