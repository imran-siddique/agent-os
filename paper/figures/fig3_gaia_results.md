# Figure: GAIA Laziness Benchmark Results
# Filename: gaia_results.png / gaia_results.pdf

## Description
Bar chart comparing correction rates across methods on the GAIA laziness benchmark.

## Data

| Method | Detection Rate | Correction Rate | Post-Patch Success |
|--------|----------------|-----------------|-------------------|
| GPT-4o (no SCAK) | 0% | 8% | 8% |
| AutoGen | 15% | 15% | 18% |
| LangGraph | 0% | 0% | 5% |
| o1-preview alone | N/A | 40% | 45% |
| Self-Critique | 100% | 40% | 48% |
| **SCAK (ours)** | **100%** | **72%** | **82%** |

## Chart Specification

```
GAIA Laziness Benchmark: Correction Rate Comparison
                                                          
100% ┤                                                    
     │                                         ████████  
 90% ┤                                         ████████  
     │                                         ████████  
 80% ┤                                         ████████  Post-Patch
     │                                 ▒▒▒▒    ████████  Success
 70% ┤                                 ▒▒▒▒    ████████  ────────
     │                                 ▒▒▒▒    ████████  
 60% ┤                                 ▒▒▒▒    ████████  Correction
     │                                 ▒▒▒▒    ████████  Rate
 50% ┤                         ▒▒▒▒    ▒▒▒▒    ████████  ▒▒▒▒▒▒▒▒
     │                 ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
 40% ┤                 ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
     │                 ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
 30% ┤                 ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
     │                 ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
 20% ┤         ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
     │         ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
 10% ┤ ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
     │ ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ▒▒▒▒    ████████  
  0% ┼─▒▒▒▒────▒▒▒▒────▒▒▒▒────▒▒▒▒────▒▒▒▒────████████──
     │GPT-4o  AutoGen LangGr  o1-prev Self-C   SCAK     
     │ alone                  alone  Critique  (Ours)   

     *** p<0.001 vs GPT-4o baseline (Cohen's d=15.2)
```

## Statistical Annotations
- Error bars: ± standard deviation (5 runs)
- Significance stars: * p<0.05, ** p<0.01, *** p<0.001
- SCAK bar should be highlighted (different color or bold border)

## Color Scheme
- GPT-4o alone: Light gray (#BDBDBD)
- AutoGen: Orange (#FF9800)
- LangGraph: Blue (#2196F3)
- o1-preview alone: Purple (#9C27B0)
- Self-Critique: Teal (#009688)
- SCAK: Green (#4CAF50) with gold border

## Caption
**Figure 3: GAIA Laziness Benchmark Results.** SCAK achieves 72% correction rate, significantly outperforming all baselines including o1-preview alone (40%) and self-critique (40%). Error bars show standard deviation over 5 runs. Statistical significance: p<0.001, Cohen's d=15.2 vs. GPT-4o baseline.
