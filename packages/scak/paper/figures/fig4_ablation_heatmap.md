# Figure: Ablation Study Heatmap
# Filename: ablation_heatmap.png / ablation_heatmap.pdf

## Description
Heatmap showing impact of removing each SCAK component on detection and correction rates.

## Data

| Configuration | Detection | Correction | Δ Detection | Δ Correction | p-value | Cohen's d |
|--------------|-----------|------------|-------------|--------------|---------|-----------|
| Full SCAK | 100% | 72% | — | — | — | — |
| − Semantic Purge | 100% | 68% | 0% | -4% | 0.042* | 0.86 |
| − Teacher (o1) | 45% | 28% | -55% | -44% | <0.001*** | 7.89 |
| − Tiered Memory | 92% | 55% | -8% | -17% | 0.003** | 2.68 |
| − Differential Audit | 0% | 0% | -100% | -72% | <0.001*** | ∞ |
| Self-Critique Only | 100% | 40% | 0% | -32% | <0.001*** | 6.04 |

## Chart Specification

```
                    ABLATION STUDY: COMPONENT IMPACT HEATMAP
                    
                         Detection Rate (%)        Correction Rate (%)
                    ┌─────────────────────────┬─────────────────────────┐
                    │  0   20   40   60   80  │  0   20   40   60   80  │
    ────────────────┼─────────────────────────┼─────────────────────────┤
    Full SCAK       │ ████████████████████████│ ██████████████████      │ 100% / 72%
                    │ ████████████████████████│ ██████████████████      │
    ────────────────┼─────────────────────────┼─────────────────────────┤
    − Sem. Purge    │ ████████████████████████│ █████████████████       │ 100% / 68%
                    │ ████████████████████████│ █████████████████       │ (−4%)
    ────────────────┼─────────────────────────┼─────────────────────────┤
    − Teacher       │ ███████████             │ ███████                 │ 45% / 28%
                    │ ███████████    ▼▼▼      │ ███████    ▼▼▼          │ (−55% / −44%)
    ────────────────┼─────────────────────────┼─────────────────────────┤
    − Tiered Mem    │ ██████████████████████  │ ██████████████          │ 92% / 55%
                    │ ██████████████████████  │ ██████████████   ▼      │ (−8% / −17%)
    ────────────────┼─────────────────────────┼─────────────────────────┤
    − Diff Audit    │                    ▼▼▼  │                    ▼▼▼  │ 0% / 0%
                    │ ░░░░░░░░░░░░░░░░░░░░░░░░│ ░░░░░░░░░░░░░░░░░░░░░░░░│ (−100% / −72%)
    ────────────────┼─────────────────────────┼─────────────────────────┤
    Self-Critique   │ ████████████████████████│ ██████████              │ 100% / 40%
                    │ ████████████████████████│ ██████████      ▼▼      │ (−32%)
    ────────────────┴─────────────────────────┴─────────────────────────┘
    
    Legend:  ████ = Performance    ░░░░ = Zero performance    ▼ = Significant drop
             * p<0.05  ** p<0.01  *** p<0.001
```

## Key Insights (for annotation)
1. **Differential Auditing is ESSENTIAL** — Without it, system cannot detect laziness at all
2. **Teacher Model is CRITICAL** — Largest effect size (d=7.89), 61% relative drop
3. **Self-Critique is INSUFFICIENT** — Achieves only 55% of full SCAK performance
4. **Semantic Purge has MODEST impact** — Statistically significant but small effect

## Color Scheme
- High performance (>80%): Dark green (#1B5E20)
- Medium performance (50-80%): Light green (#81C784)
- Low performance (20-50%): Yellow (#FFF176)
- Very low performance (<20%): Orange (#FFB74D)
- Zero performance: Red (#E57373)

## Caption
**Figure 4: Ablation Study Heatmap.** Impact of removing each SCAK component on detection and correction rates. The teacher model (o1-preview) contributes most significantly (d=7.89); removing differential auditing completely disables laziness detection. All ablations are statistically significant (p<0.05).
