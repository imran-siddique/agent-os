# Paper Draft Folder

**Project:** Self-Correcting Agent Kernel (SCAK)  
**Target:** NeurIPS 2026 / ICML 2026 (Main Track or Self-Improving AI Workshop)  
**Status:** Draft v0.2 (polished skeleton)  
**arXiv Preprint Target:** January 20–22, 2026

---

## Files in This Folder

| File | Purpose | Status |
|------|---------|--------|
| `draft_main.md` | **Primary paper draft** (camera-ready skeleton) | ✅ Complete |
| `appendix.md` | Paper appendix (Sections A-G) | ✅ Complete |
| `bibliography.bib` | BibTeX references (30+ citations) | ✅ Ready |
| `PAPER_CHECKLIST.md` | Submission checklist & progress tracker | ✅ Updated |
| `LLM_DISCLOSURE.md` | Required LLM usage disclosure | ✅ Complete |
| `figures/` | Architecture diagrams, result charts | ✅ Specs ready |
| `build.sh` | Pandoc build script | ✅ Ready |

---

## Quick Start

### View/Edit Draft
```bash
# Markdown (recommended for quick editing)
code paper/draft_main.md

# Or open in any markdown editor
```

### Build PDF (Local)
```bash
# Using Pandoc (install: https://pandoc.org/installing.html)
pandoc paper_draft.md -o scak_paper.pdf --pdf-engine=xelatex --bibliography=bibliography.bib

# Or using Docker
docker run --rm -v $(pwd):/data pandoc/latex paper_draft.md -o scak_paper.pdf
```

### Build PDF (Overleaf - Recommended)
1. Create new project on [Overleaf](https://www.overleaf.com)
2. Upload `paper_draft.md` and convert to LaTeX, or start fresh with NeurIPS template
3. Upload `bibliography.bib` for references
4. Upload figures from `figures/` folder

---

## Paper Structure

```
Title: Self-Correcting Agent Kernel: Automated Alignment via 
       Differential Auditing and Semantic Memory Hygiene

1. Abstract (246 words)               ✅ Complete
2. Introduction (2 pages)             ✅ Complete
3. Related Work (2 pages)             ✅ Complete
4. System Design (3 pages)            ✅ Complete
   - 3.1 Problem Formulation
   - 3.2 Dual-Loop Architecture
   - 3.3 Differential Auditing
   - 3.4 Semantic Purge
   - 3.5 Memory Hierarchy
5. Experiments (3 pages)              ✅ Complete
   - 4.1 Setup (datasets, baselines)
   - 4.2 GAIA Laziness Benchmark
   - 4.3 Amnesia Test
   - 4.4 Chaos Engineering
   - 4.5 Ablation Studies
6. Discussion (1 page)                ✅ Complete
7. Conclusion (0.5 pages)             ✅ Complete
8. References (30+ citations)         ✅ Complete
9. Appendix (unlimited)               ✅ See reproducibility/
```

---

## Key Results (for Abstract/Intro)

| Metric | Result | Comparison |
|--------|--------|------------|
| Laziness Detection | 100% | vs. 0% baseline |
| Correction Rate | 72% ± 4.2% | vs. 8% baseline (p<0.001) |
| Context Reduction | 45% | vs. 0% without purge |
| MTTR | 28s ± 6s | vs. ∞ (never recovers) |
| Post-Patch Success | 82% ± 3.1% | validated on similar queries |

---

## Figures Needed

1. **Figure 1: Dual-Loop OODA Architecture**
   - Source: ASCII in `paper_draft.md` Section 3.2
   - Tool: Draw.io, Mermaid, or TikZ
   - Format: PDF (vector) for LaTeX

2. **Figure 2: Three-Tier Memory Hierarchy**
   - Source: Table in `paper_draft.md` Section 3.5
   - Tool: Draw.io or TikZ
   - Format: PDF

3. **Figure 3: GAIA Results Bar Chart**
   - Source: Table 2 in `paper_draft.md`
   - Tool: Matplotlib, Seaborn, or pgfplots
   - Format: PDF

4. **Figure 4: Ablation Heatmap**
   - Source: Table 5 in `paper_draft.md`
   - Tool: Seaborn heatmap
   - Format: PDF

---

## Cross-References

- **Companion Paper:** Agent Control Plane (runtime governance focus)
- **Appendix Materials:** `../reproducibility/paper_appendix.md`
- **Ablation Details:** `../reproducibility/ABLATIONS.md`
- **Limitations:** `../LIMITATIONS.md`
- **Full Bibliography:** `bibliography.bib` (30+ refs)

---

## Submission Checklist (Quick View)

- [x] Abstract ≤250 words (246 ✓)
- [x] Main content drafted
- [x] Statistical significance reported (p-values, Cohen's d)
- [x] Ablation studies complete
- [x] Reproducibility materials ready
- [x] LLM disclosure prepared
- [ ] Figures created (vector PDF)
- [ ] Convert to LaTeX (NeurIPS template)
- [ ] Anonymize for double-blind
- [ ] Internal review (2-3 readers)
- [ ] Upload to arXiv

---

## Build Script (Optional)

Create `build.sh` for automated PDF generation:

```bash
#!/bin/bash
# Build SCAK paper PDF from markdown

echo "Building SCAK paper..."

# Pandoc with bibliography
pandoc paper_draft.md \
  -o scak_paper.pdf \
  --pdf-engine=xelatex \
  --bibliography=bibliography.bib \
  --citeproc \
  -V geometry:margin=1in \
  -V fontsize=11pt

echo "Done: scak_paper.pdf"
```

---

## Timeline

| Date | Milestone |
|------|-----------|
| Jan 18, 2026 | Draft complete ✅ |
| Jan 19, 2026 | Create figures, convert to LaTeX |
| Jan 20, 2026 | Internal review, polish |
| Jan 21, 2026 | Anonymize, final checks |
| Jan 22, 2026 | Upload to arXiv |
| TBD | Submit to NeurIPS 2026 |

---

**Last Updated:** 2026-01-18
