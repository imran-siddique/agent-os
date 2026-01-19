# Paper Submission Checklist

This checklist ensures compliance with 2025-2026 top-tier AI/ML venue requirements (NeurIPS, ICML, ICLR, AAMAS, etc.).

## Agent Control Plane Paper Status

### Content Sections
- [x] Title finalized: "Agent Control Plane: A Deterministic Kernel for Zero-Violation Governance in Agentic AI"
- [x] Abstract complete (248 words): 0% violations, 98.1% token reduction, ablations
- [x] Introduction: Problem (jailbreaks, prompt injection), solution (kernel philosophy), contributions
- [x] Related Work: RLHF, LlamaGuard, Guardrails.ai, NeMo, LangChain, ABAC
- [x] System Design: Architecture, PolicyEngine, ConstraintGraphs, MuteAgent, FlightRecorder
- [x] Experiments: Main results table, ablation table with p-values/Cohen's d
- [x] Discussion & Limitations: Dataset scope, modality, baselines, ethics
- [x] Conclusion: Summary with key stats
- [x] References: 20 citations (expand to 30+ for submission)
- [x] Cross-reference to companion paper (Self-Correcting Agent Kernel)

### Figures & Tables
- [ ] Architecture diagram (figures/architecture.png) - TODO
- [ ] Results bar chart (figures/results_chart.pdf) - TODO
- [x] Table 1: Main benchmark results
- [x] Table 2: Ablation study with statistics
- [x] Table 3: Latency breakdown

### Bibliography
- [x] references.bib created with 30+ entries
- [ ] Verify all citations have complete metadata
- [ ] Check for duplicate entries
- [ ] Add missing arXiv IDs where applicable

### Reproducibility Artifacts
- [x] Code publicly available (GitHub)
- [x] PyPI package (`pip install agent-control-plane`)
- [x] Dataset on HuggingFace
- [x] Docker configuration
- [x] Frozen dependencies (requirements_frozen.txt)
- [x] Seeds documented (42, 123, 456, 789, 1024)
- [x] Hardware specs documented
- [x] Statistical methods documented (Welch's t-test, Bonferroni, Cohen's d)

### Build & Format
- [ ] Convert to LaTeX (Overleaf with NeurIPS/ICLR template)
- [ ] PDF builds without errors
- [ ] Page count within limits (target: 8-9 pages + appendix)
- [ ] Font and margin compliance

---

## Pre-Submission Requirements

### 1. Anonymity (Double-Blind Review)

#### Code and Repository
- [ ] Do NOT include author names in paper PDF
- [ ] Do NOT include institutional affiliations in paper PDF
- [ ] Cite own work in third person: "Prior work [anonymized] introduced..."
- [ ] Remove author names from code comments in repository screenshots
- [ ] Remove author names from README if including repository link
- [ ] Use anonymous repository links (e.g., Anonymous GitHub or separate anonymous fork)

#### Common Anonymity Violations to Avoid
- ❌ Self-citations in first person: "We previously showed..." → ✅ "Prior work [X] showed..."
- ❌ Acknowledgments in main paper → ✅ Move to camera-ready version only
- ❌ Institutional logos in figures → ✅ Remove or anonymize
- ❌ URLs containing author/org names → ✅ Use bit.ly or anonymous domains
- ❌ ArXiv preprints with author names → ✅ Cite as [anonymized] if not public at deadline

### 2. LLM Usage Disclosure

#### Required Statement (Add to Paper)

Most venues (ICLR 2026, NeurIPS 2025+, ICML 2026) require explicit disclosure of LLM usage in writing/editing.

**Template**:
```latex
\section*{LLM Usage Statement}

We used [LLM name/version] for the following purposes:
- Initial outlining of paper structure
- Grammar and clarity improvements

All claims, experiments, and results are author-original.
```

### 3. No Dual Submission

- [ ] Verify paper is NOT under review at another venue at the same time
- [ ] Check workshop submissions (some conferences prohibit dual submission to workshops)
- [ ] Confirm ArXiv preprints are allowed (most venues allow, but check)

### 4. Reproducibility Requirements

- [ ] Code is publicly available (GitHub)
- [ ] Code includes README with installation instructions
- [ ] Datasets are publicly available
- [ ] Random seeds specified (if applicable)
- [ ] Hardware specs documented (CPU, GPU, RAM)
- [ ] Software versions documented

### 5. Ethics and Broader Impact

Include discussion of ethical implications and limitations.

### 6. Formatting and Length

#### Page Limits (2025-2026)

| Venue | Main Paper | Appendix |
|-------|-----------|----------|
| NeurIPS | 9 pages | Unlimited |
| ICML | 8 pages | Unlimited |
| ICLR | 9 pages | Unlimited |
| AAMAS | 8 pages | 1 page |

---

**Last Updated**: January 2026
