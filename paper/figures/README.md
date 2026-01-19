# Figures

Figure specifications for the SCAK paper.

## Figures

| File | Description | Source |
|------|-------------|--------|
| `fig1_ooda_architecture.md` | Dual-Loop OODA Architecture | main.md §3.2 |
| `fig2_memory_hierarchy.md` | Three-Tier Memory System | main.md §3.5 |
| `fig3_gaia_results.md` | GAIA Benchmark Bar Chart | main.md Table 1 |
| `fig4_ablation_heatmap.md` | Ablation Study Results | main.md Table 4 |
| `fig5_context_reduction.md` | Token Reduction Over Time | main.md Table 2 |
| `fig6_mttr_boxplot.md` | MTTR Comparison Box Plot | main.md Table 3 |

## Tools

- **Draw.io / diagrams.net** - Architecture diagrams
- **Matplotlib / Seaborn** - Charts and plots
- **TikZ** - LaTeX-native figures

## Format Requirements

- **Vector format:** PDF preferred (scalable, crisp in LaTeX)
- **Resolution:** 300 DPI minimum for raster fallback
- **Font size:** Legible at column width (~3.5 inches)

## NeurIPS Style

- Maximum width: 5.5 inches (single column) or 7 inches (full width)
- Use `\includegraphics[width=\columnwidth]{figures/fig1_architecture.pdf}`
- Caption below figure, numbered sequentially
