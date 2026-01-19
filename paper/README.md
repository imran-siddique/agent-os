# Paper Draft Folder

## Current Status

**Stage**: Draft complete, ready for LaTeX conversion (arXiv target: Jan 20–22, 2026)

**Title**: "Agent Control Plane: A Deterministic Kernel for Zero-Violation Governance in Agentic AI Systems"

**Target Venues**:
- arXiv preprint (cs.AI) — immediate
- NeurIPS 2026 Workshop on AI Safety — May/June deadline
- ICLR 2027 — Fall cycle

## Files

| File | Description | Status |
|------|-------------|--------|
| `draft_main.md` | **Full paper draft** | ✅ Complete (~3,500 words) |
| `PAPER_DRAFT.md` | Earlier outline version | ✅ Reference |
| `PAPER_OUTLINE.md` | Section-by-section outline | ✅ Reference |
| `PAPER_CHECKLIST.md` | Submission checklist | ✅ Updated |
| `ETHICS_STATEMENT.md` | Ethics considerations | ✅ Complete |
| `appendix.md` | Reproducibility, ablations, limitations | ✅ Complete |
| `references.bib` | BibTeX citations | ✅ 30+ refs |
| `build.sh` | Pandoc PDF build script | ✅ Ready |
| `figures/` | Architecture diagrams, charts | 🔄 TODO |

## Building PDF

### Option 1: Overleaf (Recommended)
1. Upload `PAPER_DRAFT.md` content to Overleaf
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
pandoc PAPER_DRAFT.md -o draft.pdf --pdf-engine=xelatex
```

## Sections Completed

- [x] Abstract (247 words)
- [x] Introduction (problem, approach, contributions)
- [x] Related Work (Guardrails.ai, LlamaGuard, MAESTRO)
- [x] System Design (architecture, PolicyEngine, MuteAgent)
- [x] Experiments (60-prompt benchmark, ablations)
- [x] Discussion & Limitations
- [x] Conclusion
- [ ] Figures (architecture diagram, results chart)
- [x] References (30+ citations in references.bib)

## Key Results to Highlight

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

## Next Steps

1. [ ] Create architecture figure (`figures/architecture.png`)
2. [ ] Create results bar chart (`figures/results_chart.pdf`)
3. [ ] Convert to LaTeX in Overleaf
4. [ ] Final polish and proofreading
5. [ ] Upload to arXiv (cs.AI, CC-BY 4.0)
6. [ ] Twitter announcement @mosiddi

---

*Last updated: January 2026*
