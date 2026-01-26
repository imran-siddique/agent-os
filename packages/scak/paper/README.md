# Paper

**Project:** Self-Correcting Agent Kernel (SCAK)  
**Target Venue:** NeurIPS 2026 / ICML 2026

---

## Files

| File | Purpose |
|------|---------|
| `main.tex` | Primary paper (LaTeX) |
| `main.md` | Paper source (Markdown) |
| `appendix.md` | Paper appendix (Sections A-G) |
| `bibliography.bib` | BibTeX references (30+ citations) |
| `LLM_DISCLOSURE.md` | LLM usage disclosure |
| `figures/` | Figure specifications |
| `build.sh` | Build script |

---

## Building the Paper

### Build PDF (Local - LaTeX)

```bash
# Using pdflatex (recommended)
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Or using latexmk
latexmk -pdf main.tex
```

### Build PDF (Overleaf)

1. Create new project on [Overleaf](https://www.overleaf.com)
2. Upload `main.tex`, `bibliography.bib`, and `figures/` folder
3. Set compiler to pdfLaTeX
4. Click "Recompile"

### Build PDF (Docker)

```bash
docker run --rm -v $(pwd):/data blang/latex:ctanfull \
    sh -c "pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex"
```

---

## Paper Structure

```
Title: Self-Correcting Agent Kernel: Automated Alignment via 
       Differential Auditing and Semantic Memory Hygiene

1. Abstract (~250 words)
2. Introduction (2 pages)
3. Related Work (1.5 pages)
4. System Design (3 pages)
   - 4.1 Problem Formulation
   - 4.2 Dual-Loop Architecture
   - 4.3 Differential Auditing
   - 4.4 Semantic Purge
   - 4.5 Memory Hierarchy
5. Experiments (3 pages)
   - 5.1 Setup
   - 5.2 GAIA Laziness Benchmark
   - 5.3 Amnesia Test
   - 5.4 Chaos Engineering
   - 5.5 Ablation Studies
   - 5.6 Cost Analysis
6. Discussion (1 page)
7. Conclusion (0.5 pages)
8. References (30+ citations)
9. Appendix
```

---

## Key Results

| Metric | Result | Comparison |
|--------|--------|------------|
| Laziness Detection | 100% | vs. 0% baseline |
| Correction Rate | 72% ± 4.2% | vs. 8% baseline (p<0.001) |
| Context Reduction | 45% | vs. 0% without purge |
| MTTR | 28s ± 6s | vs. ∞ (never recovers) |
| Post-Patch Success | 82% ± 3.1% | validated on similar queries |

---

## Figures

| Figure | Description |
|--------|-------------|
| Figure 1 | Dual-Loop OODA Architecture |
| Figure 2 | Three-Tier Memory Hierarchy |
| Figure 3 | GAIA Results Bar Chart |
| Figure 4 | Ablation Heatmap |
| Figure 5 | Context Reduction Over Time |
| Figure 6 | MTTR Comparison Box Plot |

---

## Cross-References

- **Reproducibility:** `../reproducibility/`
- **Ablation Details:** `../reproducibility/ABLATIONS.md`
- **Limitations:** `../LIMITATIONS.md`
