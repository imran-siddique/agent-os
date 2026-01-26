# Paper Submission Checklist

Compliance checklist for top-tier AI/ML venues (NeurIPS, ICML, ICLR, AAMAS).

## Agent Control Plane Paper

### Content Sections
- [x] Title: ""Agent Control Plane: A Deterministic Kernel for Zero-Violation Governance in Agentic AI""
- [x] Abstract (248 words): 0% violations, 98.1% token reduction, ablations
- [x] Introduction: Problem (jailbreaks, prompt injection), solution (kernel philosophy), contributions
- [x] Related Work: RLHF, LlamaGuard, Guardrails.ai, NeMo, LangChain, ABAC
- [x] System Design: Architecture, PolicyEngine, ConstraintGraphs, MuteAgent, FlightRecorder
- [x] Experiments: Main results table, ablation table with p-values/Cohen's d
- [x] Discussion & Limitations: Dataset scope, modality, baselines, ethics
- [x] Conclusion: Summary with key stats
- [x] References: 30+ citations

### Figures & Tables
- [x] Table 1: Main benchmark results
- [x] Table 2: Ablation study with statistics
- [x] Table 3: Latency breakdown

### Bibliography
- [x] references.bib created with 30+ entries

### Reproducibility Artifacts
- [x] Code publicly available (GitHub)
- [x] PyPI package (`pip install agent-control-plane`)
- [x] Dataset on HuggingFace
- [x] Docker configuration
- [x] Frozen dependencies (requirements_frozen.txt)
- [x] Seeds documented (42, 123, 456, 789, 1024)
- [x] Hardware specs documented
- [x] Statistical methods documented (Welch's t-test, Bonferroni, Cohen's d)

---

## Submission Requirements

### 1. Anonymity (Double-Blind Review)

- Do NOT include author names in paper PDF
- Do NOT include institutional affiliations in paper PDF  
- Cite own work in third person
- Use anonymous repository links

### 2. LLM Usage Disclosure

Most venues require explicit disclosure of LLM usage in writing/editing.

```latex
\section*{LLM Usage Statement}

We used [LLM name/version] for the following purposes:
- Initial outlining of paper structure
- Grammar and clarity improvements

All claims, experiments, and results are author-original.
```

### 3. Page Limits (2025-2026)

| Venue | Main Paper | Appendix |
|-------|-----------|----------|
| NeurIPS | 9 pages | Unlimited |
| ICML | 8 pages | Unlimited |
| ICLR | 9 pages | Unlimited |
| AAMAS | 8 pages | 1 page |

---

*Last Updated: January 2026*
