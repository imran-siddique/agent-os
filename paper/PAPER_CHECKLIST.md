# Paper Preparation Checklist

## Submission Target

- [x] **Venue:** NeurIPS 2026 / ICML 2026 / ICLR 2026 / AAMAS 2026
- [x] **Track:** Agent Systems / Production ML / Self-Improving Systems
- [ ] **Submission Deadline:** TBD
- [x] **Page Limit:** 9 pages main + unlimited appendix

---

## Pre-Submission Checklist

### 1. Novelty & Contribution Framing ✅

- [x] Clear novelty statement in abstract
- [x] Contribution comparison table (vs. Reflexion, Constitutional AI, Voyager, etc.)
- [x] Related work section with 30+ citations
- [x] Quantitative differentiation from baselines
- [ ] Expert review: Have 2-3 researchers read novelty claims

### 2. Empirical Rigor ✅

- [x] GAIA Benchmark (50 queries)
- [x] Amnesia Test (60 patches)
- [x] Chaos Engineering (20 scenarios)
- [x] Statistical significance (p-values, confidence intervals)
- [x] Ablation studies (remove each component)
- [x] Broader baselines (AutoGen, LangGraph, o1-preview)
- [x] Error analysis (failure mode breakdown)

### 3. Reproducibility ✅

- [x] Datasets uploaded (GitHub + plan for Hugging Face)
- [x] Docker image with pinned dependencies
- [x] Seed control utilities
- [x] Experiment scripts tested end-to-end
- [x] README with exact reproduction commands
- [x] Hardware specifications documented
- [x] API costs calculated and reported

### 4. Anonymization (Critical for Double-Blind)

- [ ] Remove author names from all files
- [ ] Cite own repos in third person ("Prior work [Anonymous, 2026] introduced...")
- [ ] No GitHub URLs in paper body (move to appendix after acceptance)
- [ ] No identifying information in code comments
- [ ] No screenshots with author names
- [ ] Check LaTeX metadata (remove author info from PDF properties)

### 5. LLM Disclosure (Required by Most 2026 Venues)

- [x] Create LLM_DISCLOSURE.md with specific details:
  - [x] Which LLM(s) used (e.g., "Grok-3 for grammar checking")
  - [x] How used (e.g., "Edited abstract for clarity")
  - [x] Scope (e.g., "NOT used for experimental results or claims")
  - [x] Statement: "All intellectual contributions are author-original"

### 6. Paper Structure

#### Abstract (250 words)
- [x] Problem statement (context bloat, laziness, silent failures)
- [x] Novelty statement (Type A/B decay, differential auditing, dual-loop)
- [x] Empirical claims (72% correction, 50% reduction, <30s MTTR)
- [x] Significance (production-ready, p<0.001, outperforms baselines)

#### 1. Introduction (2 pages)
- [x] Motivation: Why agent reliability matters (production failures, cost)
- [x] Gap: What existing work doesn't solve (context bloat, laziness, efficiency)
- [x] Contributions: Three bullets (Semantic Purge, Differential Auditing, Dual-Loop)
- [x] Roadmap: "Section 2 reviews related work, Section 3 describes..."

#### 2. Related Work (2-3 pages)
- [x] Self-Correcting Systems (Reflexion, Self-Refine, Self-Debug)
- [x] Safety & Alignment (Constitutional AI, LlamaGuard, WildGuard)
- [x] Multi-Agent Systems (Voyager, AutoGen, MetaGPT)
- [x] Context Management (Lost in the Middle, RAG, Landmark Attention)
- [x] Production ML (Hidden Technical Debt, Data Validation)
- [x] Comparison table (Table 1: Contribution Comparison)

#### 3. Method (3 pages)
- [x] 3.1 Problem Formulation (formal definitions)
- [x] 3.2 Dual-Loop Architecture (Figure 1: OODA diagram)
- [x] 3.3 Differential Auditing (Algorithm 1: Audit trigger logic)
- [x] 3.4 Semantic Purge (Algorithm 2: Type A/B classification)
- [x] 3.5 Memory Hierarchy (Figure 2: Tier 1/2/3 architecture)

#### 4. Experiments (3 pages)
- [x] 4.1 Experimental Setup (datasets, baselines, metrics)
- [x] 4.2 GAIA Benchmark (Table 2: Detection/correction rates, Figure 3: Bar chart)
- [x] 4.3 Amnesia Test (Table 3: Context reduction, Figure 4: Line chart)
- [x] 4.4 Chaos Engineering (Table 4: MTTR, Figure 5: Box plot)
- [x] 4.5 Ablation Studies (Table 5: Component removal, Figure 6: Heatmap)
- [x] 4.6 Broader Baselines (Table 6: AutoGen, LangGraph, o1-preview)

#### 5. Discussion (1 page)
- [x] Key findings (summary of empirical results)
- [x] Limitations (honest assessment from LIMITATIONS.md)
- [x] Failure modes (multi-turn, adversarial, cold start)
- [x] Ethical considerations (data privacy, cost, bias)

#### 6. Conclusion (0.5 pages)
- [x] Restate contributions
- [x] Restate key results
- [x] Future work (federated patches, meta-learning, causal analysis)
- [x] Cross-reference to companion paper (Agent Control Plane)

#### Appendix (Unlimited)
- [x] A. Additional Ablation Results
- [x] B. Full Experiment Results (all 50 GAIA queries)
- [x] C. Patch Examples (Type A vs Type B)
- [x] D. Reproducibility Details (Docker commands, seeds, hardware)
- [x] E. Related Work Extended (full 50+ citations)
- [x] F. Ethical Statement
- [x] G. Limitations Extended (from LIMITATIONS.md)

### 7. Figures & Tables

#### Figures
- [x] Figure 1: Dual-Loop OODA Architecture (fig1_ooda_architecture.md)
- [x] Figure 2: Memory Hierarchy (fig2_memory_hierarchy.md)
- [x] Figure 3: GAIA Results (fig3_gaia_results.md)
- [x] Figure 4: Ablation Heatmap (fig4_ablation_heatmap.md)
- [x] Figure 5: Context Reduction (fig5_context_reduction.md)
- [x] Figure 6: MTTR Comparison (fig6_mttr_boxplot.md)

#### Tables
- [x] Table 1: Contribution Comparison (vs. prior work)
- [x] Table 2: GAIA Benchmark Results (with CI)
- [x] Table 3: Amnesia Test Results (context reduction)
- [x] Table 4: Chaos Engineering Results (MTTR, recovery rate)
- [x] Table 5: Ablation Study Summary
- [x] Table 6: Broader Baseline Comparison

### 8. Bibliography

- [x] Export all citations from RESEARCH.md to BibTeX
- [x] Add 2025-2026 papers:
  - [x] "Agentic AI: A Comprehensive Survey" (arXiv:2510.25445)
  - [x] LlamaGuard-2 (Meta 2024)
  - [x] WildGuard (arXiv:2406.18495)
  - [x] WEF 2025 Governance Whitepaper
- [x] Format all citations consistently (ACM/IEEE/NeurIPS style)
- [x] Verify all URLs are accessible
- [x] Total citations: 40+ (currently 30+, need minor additions)

### 9. Submission Materials

- [ ] Main PDF (9 pages + appendix)
- [ ] Supplementary materials:
  - [ ] Code (GitHub link or ZIP)
  - [ ] Datasets (Hugging Face links)
  - [ ] Reproducibility package (Docker image)
- [ ] Abstract (250 words, plain text)
- [ ] Keywords (5-10 keywords)
- [ ] Author information (name, affiliation, email)
- [ ] Conflict of interest statement
- [ ] LLM disclosure statement
- [ ] Ethics statement

### 10. Pre-Submission Review

- [ ] Internal review by 2-3 co-authors
- [ ] External review by 1-2 domain experts (if possible)
- [ ] Grammar check (Grammarly / LanguageTool)
- [ ] Plagiarism check (Turnitin / iThenticate)
- [ ] Anonymity check (no author-identifying information)
- [ ] Reference formatting check (consistent style)

### 11. Venue-Specific Requirements

#### NeurIPS 2026
- [ ] 9 pages main + unlimited appendix
- [ ] Double-blind review (strict anonymity)
- [ ] LLM disclosure required (new in 2025+)
- [ ] Code submission encouraged (GitHub or OpenReview)
- [ ] No dual submission at time of deadline

#### ICML 2026
- [ ] 8 pages main + unlimited appendix
- [ ] Double-blind review
- [ ] Reproducibility checklist (mandatory)
- [ ] Ethics statement (mandatory)

#### ICLR 2026
- [ ] No page limit (discouraged >10 pages main)
- [ ] Double-blind review
- [ ] OpenReview submission (public after acceptance)

#### AAMAS 2026
- [ ] 8 pages main + 1 page references + unlimited appendix
- [ ] Agent-focused track (perfect fit)
- [ ] Industry track option (production-ready systems)

### 12. Post-Acceptance Tasks

- [ ] Upload camera-ready PDF
- [ ] Upload supplementary materials
- [ ] Upload poster (if required)
- [ ] Prepare presentation (15-20 min talk)
- [ ] Update GitHub README with paper link
- [ ] Publish to arXiv (if allowed by venue)
- [ ] Tweet/blog post announcement
- [ ] Update CITATION.cff with paper details

---

## LaTeX Template

**Template:** NeurIPS 2026 / ICML 2026 (download from venue website)

**Recommended Structure:**
```latex
\documentclass{article}
\usepackage{neurips_2026}  % Or icml2026, iclr2026, etc.

\title{Self-Correcting Agent Kernel: Automated Alignment via \\ Differential Auditing and Semantic Memory Hygiene}

\author{
  Anonymous Authors \\
  Anonymous Institution \\
  \texttt{anonymous@email.com}
}

\begin{document}

\maketitle

\begin{abstract}
% 250 words
\end{abstract}

\section{Introduction}
% Motivation, gap, contributions, roadmap

\section{Related Work}
% 5 subsections: Self-correction, Safety, Multi-agent, Context, Production ML

\section{Method}
% 5 subsections: Problem, Dual-Loop, Differential Auditing, Semantic Purge, Memory

\section{Experiments}
% 6 subsections: Setup, GAIA, Amnesia, Chaos, Ablation, Baselines

\section{Discussion}
% Findings, limitations, ethics

\section{Conclusion}
% Summary, future work

\bibliographystyle{plain}
\bibliography{references}

\appendix
\section{Additional Results}
% Full tables, figures, proofs

\end{document}
```

---

## Timeline

**Assuming submission in 6 months (July 2026):**

- **Month 1-2 (Now - March):** Complete experiments, ablation, baselines
- **Month 3 (April):** Statistical analysis, generate figures/tables
- **Month 4 (May):** Write first draft (all sections)
- **Month 5 (June):** Internal review, revisions, polish
- **Month 6 (July):** Final checks, submit

---

## Resources

- **NeurIPS 2026:** https://neurips.cc/
- **ICML 2026:** https://icml.cc/
- **ICLR 2026:** https://iclr.cc/
- **AAMAS 2026:** https://aamas2026.org/
- **arXiv:** https://arxiv.org/
- **Hugging Face Datasets:** https://huggingface.co/datasets
- **OpenReview:** https://openreview.net/

---

## arXiv Pre-print Checklist

- [x] PDF builds without errors (Pandoc tested)
- [x] Abstract ≤1920 characters
- [x] Title ≤200 characters
- [ ] Author metadata prepared
- [ ] Primary category: cs.AI or cs.LG
- [ ] Secondary categories: cs.CL, cs.SE
- [ ] License: CC BY 4.0
- [x] No copyrighted figures
- [x] References formatted correctly
- [ ] Ancillary files (code.zip) prepared

---

**Last Updated:** 2026-01-18  
**Version:** 1.1  
**Next Review:** Before submission
