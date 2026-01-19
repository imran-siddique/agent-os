# Figures for SCAK Paper

This folder contains figures for the Self-Correcting Agent Kernel paper.

## Figure Status

| Figure | Description | Source | Status |
|--------|-------------|--------|--------|
| `fig1_ooda_architecture.md` | Dual-Loop OODA Architecture | draft_main.md §3.2 | ✅ Spec ready |
| `fig2_memory_hierarchy.md` | Three-Tier Memory System | draft_main.md §3.5 | ✅ Spec ready |
| `fig3_gaia_results.md` | GAIA Benchmark Bar Chart | draft_main.md Table 1 | ✅ Spec ready |
| `fig4_ablation_heatmap.md` | Ablation Study Results | draft_main.md Table 4 | ✅ Spec ready |
| `fig5_context_reduction.md` | Token Reduction Over Time | draft_main.md Table 2 | ✅ Spec ready |
| `fig6_mttr_boxplot.md` | MTTR Comparison Box Plot | draft_main.md Table 3 | ✅ Spec ready |

## Next Steps

1. Convert `.md` specs to vector graphics (PDF/SVG)
2. Use tools: draw.io, Matplotlib, TikZ, or Excalidraw
3. Each `.md` file contains:
   - ASCII reference diagram
   - Color scheme
   - Data tables
   - Caption text

## Tools

- **Draw.io / diagrams.net** - Architecture diagrams
- **Matplotlib / Seaborn** - Charts and plots
- **TikZ** - LaTeX-native figures
- **Mermaid** - Quick flowcharts (convert to PDF)

## Generation Scripts

```python
# Example: Generate GAIA results bar chart
import matplotlib.pyplot as plt
import numpy as np

methods = ['GPT-4o\n(baseline)', 'AutoGen', 'LangGraph', 'o1-preview\nalone', 'SCAK\n(ours)']
correction_rates = [8, 15, 0, 40, 72]
colors = ['#cccccc', '#cccccc', '#cccccc', '#cccccc', '#2ecc71']

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(methods, correction_rates, color=colors, edgecolor='black')
ax.set_ylabel('Correction Rate (%)', fontsize=12)
ax.set_title('GAIA Laziness Benchmark: Correction Rates', fontsize=14)
ax.set_ylim(0, 100)

# Add value labels
for bar, val in zip(bars, correction_rates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
            f'{val}%', ha='center', fontsize=11)

plt.tight_layout()
plt.savefig('fig3_gaia_results.pdf', format='pdf', bbox_inches='tight')
```

## Format Requirements

- **Vector format:** PDF preferred (scalable, crisp in LaTeX)
- **Resolution:** 300 DPI minimum for raster fallback
- **Color scheme:** Consistent across all figures
- **Font size:** Legible at column width (~3.5 inches)
- **Labels:** Clear axis labels, legends inside or below

## NeurIPS Style Notes

- Maximum width: 5.5 inches (single column) or 7 inches (full width)
- Use `\includegraphics[width=\columnwidth]{figures/fig1_architecture.pdf}`
- Caption below figure, numbered sequentially
