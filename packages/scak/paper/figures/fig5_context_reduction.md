# Figure: Context Reduction via Semantic Purge
# Filename: context_reduction.png / context_reduction.pdf

## Description
Line chart showing context token growth over time, with and without Semantic Purge.

## Data

| Time Point | Without Purge | With SCAK Purge | Reduction |
|------------|---------------|-----------------|-----------|
| Initial (T0) | 800 tokens | 800 tokens | 0% |
| +10 patches | 960 tokens | 960 tokens | 0% |
| +20 patches | 1,120 tokens | 1,120 tokens | 0% |
| +30 patches | 1,280 tokens | 1,280 tokens | 0% |
| +40 patches | 1,440 tokens | 1,440 tokens | 0% |
| +50 patches | 1,600 tokens | 1,600 tokens | 0% |
| **Model Upgrade** | 1,600 tokens | **880 tokens** | **45%** |
| +60 patches | 1,760 tokens | 1,040 tokens | 41% |
| +70 patches | 1,920 tokens | 1,200 tokens | 38% |

## Chart Specification

```
        CONTEXT TOKEN GROWTH: WITH AND WITHOUT SEMANTIC PURGE
        
Tokens │
       │
 2000  ┤                                                    ──────── No Purge
       │                                               ●────────────  (unbounded)
 1800  ┤                                          ●────
       │                                     ●────
 1600  ┤                                ●────●               ▲ Model Upgrade
       │                           ●────     │               │ (GPT-4o → GPT-5)
 1400  ┤                      ●────          │               │
       │                 ●────               │               
 1200  ┤            ●────                    │          ○────○ SCAK
       │       ●────                         │     ○────      (with purge)
 1000  ┤  ●────                              │○────
       │  │                                  ○
  800  ┤  ●────●────●────●────●────●────●────○               
       │  │    │    │    │    │    │    │    │               
  600  ┤  │    │    │    │    │    │    │    │    45% reduction
       │  │    │    │    │    │    │    │    │    ▼
  400  ┤  │    │    │    │    │    │    │    │               
       │                                                      
  200  ┤                                                      
       │                                                      
    0  ┼──┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────►
          T0  +10  +20  +30  +40  +50  UPG  +60  +70        
                                            │
                      Patches Added         │
                                    Semantic Purge
                                    (Type A deleted)

    ─── No Purge (unbounded growth)
    ─○─ SCAK with Semantic Purge (45% reduction at upgrade)
```

## Annotations
1. Vertical dashed line at "Model Upgrade" point
2. Shaded region showing "Type A patches purged" area
3. Label: "45% reduction, 100% business rules retained"

## Color Scheme
- No Purge line: Red (#F44336) — Warning, unbounded growth
- SCAK line: Green (#4CAF50) — Healthy, managed growth
- Purge event: Blue vertical line (#2196F3)
- Shaded reduction area: Light blue (#BBDEFB)

## Caption
**Figure 5: Context Reduction via Semantic Purge.** Without purge (red), context grows unboundedly with accumulated patches. SCAK's Semantic Purge (green) deletes Type A (syntax) patches on model upgrades, achieving 45% reduction while retaining all Type B (business) patches. This prevents context rot and reduces API costs.
