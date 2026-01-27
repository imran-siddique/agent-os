# ATR Paper

This directory contains the research paper and supporting materials for the Agent Tool Registry (ATR).

## Contents

- [whitepaper.md](whitepaper.md) - Main paper in Markdown format
- [structure.tex](structure.tex) - LaTeX template for academic submission
- [figures/](figures/) - Diagrams and visualizations
- [references.bib](references.bib) - BibTeX bibliography

## Building the Paper

### From Markdown (Pandoc)

```bash
pandoc whitepaper.md -o paper.pdf \
  --bibliography=references.bib \
  --citeproc \
  --pdf-engine=xelatex
```

### From LaTeX

```bash
pdflatex structure.tex
bibtex structure
pdflatex structure.tex
pdflatex structure.tex
```

## Submission Targets

- **Conferences**: ICML, NeurIPS, AAAI (AI Agents track)
- **Journals**: JMLR, AIJ
- **Workshops**: Agent Workshop @ NeurIPS, LLM Agents @ ICML
