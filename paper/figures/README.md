# Figures Directory

This folder contains diagrams and charts for the paper.

## Required Figures

1. **architecture.png** - System architecture diagram
   - Show: AgentKernel, PolicyEngine, ConstraintGraphs, MuteAgent, FlightRecorder
   - Style: Clean boxes with arrows, similar to kernel architecture diagrams
   - Tools: draw.io, Lucidchart, or TikZ

2. **results_chart.pdf** - Main benchmark results
   - Bar chart: Baseline vs ACP for SVR and Token Reduction
   - Include error bars (std dev from 5 seeds)
   - Tools: matplotlib, seaborn

3. **ablation_chart.pdf** - Ablation study results
   - Bar chart: SVR for each ablation configuration
   - Highlight PolicyEngine as critical
   - Tools: matplotlib

## Creating Figures

### Option 1: Draw.io (Architecture)
1. Go to https://app.diagrams.net/
2. Create architecture diagram
3. Export as PNG (300 DPI for print quality)

### Option 2: Python/Matplotlib (Charts)
```python
import matplotlib.pyplot as plt
import numpy as np

# Main results
configs = ['Baseline\n(No ACP)', 'With ACP']
svr = [26.67, 0.0]
tokens = [127.4, 0.5]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

ax1.bar(configs, svr, color=['#ff6b6b', '#4ecdc4'])
ax1.set_ylabel('Safety Violation Rate (%)')
ax1.set_title('Safety Performance')

ax2.bar(configs, tokens, color=['#ff6b6b', '#4ecdc4'])
ax2.set_ylabel('Tokens per Blocked Request')
ax2.set_title('Token Efficiency')

plt.tight_layout()
plt.savefig('results_chart.pdf', dpi=300, bbox_inches='tight')
```

## Placeholder Note

Until figures are created, the paper draft uses ASCII diagrams and tables.
