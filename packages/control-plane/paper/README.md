# Paper

**Title**: "Agent Control Plane: A Deterministic Kernel for Zero-Violation Governance in Agentic AI Systems"

**Target Venues**:
- arXiv preprint (cs.AI)
- NeurIPS 2026 Workshop on AI Safety
- ICLR 2027

## Files

| File | Description |
|------|-------------|
| `main.md` | Full paper in Markdown (~3,500 words) |
| `main.tex` | Full paper in LaTeX (for arXiv) |
| `main_anonymous.md` | Anonymized Markdown for double-blind review |
| `main_anonymous.tex` | Anonymized LaTeX for double-blind review |
| `appendix.md` | Reproducibility, ablations, limitations |
| `PAPER_CHECKLIST.md` | Submission checklist |
| `ETHICS_STATEMENT.md` | Ethics considerations |
| `references.bib` | BibTeX citations (30+ refs) |
| `build.sh` | Pandoc PDF build script |
| `figures/` | Architecture diagrams, charts (PNG/PDF) |

### Generated Figures
| Figure | File | Description |
|--------|------|-------------|
| Figure 1 | `figures/architecture.png` | ACP system architecture |
| Figure 2 | `figures/constraint_graphs.png` | Multi-dimensional constraint validation |
| Figure 3 | `figures/results_chart.png` | Main benchmark results |
| Figure 4 | `figures/ablation_chart.png` | Ablation study results |

## Building PDF

### Option 1: Overleaf (Recommended)
1. Upload `main.md` content to Overleaf
2. Convert to LaTeX format
3. Use NeurIPS/ICLR template

### Option 2: Pandoc (Local)
```bash
# Install pandoc if needed
# Windows: choco install pandoc
# Mac: brew install pandoc
# Linux: apt install pandoc

# Build PDF
./build.sh
# Or manually:
pandoc main.md -o paper.pdf --pdf-engine=xelatex
```

## Key Results

| Metric | Value |
|--------|-------|
| Safety Violation Rate | **0.00%** (vs 26.67% baseline) |
| Token Reduction | **98.1%** |
| Latency Overhead | **12ms** (negligible) |
| PolicyEngine ablation | p < 0.0001, Cohen's d = 8.7 |

## Links

- **GitHub**: https://github.com/imran-siddique/agent-control-plane
- **PyPI**: `pip install agent-control-plane`
- **Dataset**: https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60
- **Reproducibility**: See `../reproducibility/` folder

---

*Last updated: January 2026*
