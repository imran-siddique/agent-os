# Results Tables for Paper

## Table 1: Corpus Statistics

| Property | Value |
|----------|-------|
| Documents | 16 |
| Lines | 2,935 |
| Characters | 100,562 |
| Tokens (est.) | 16,286 |
| Formats | 5 (MD, PY, HTML, SQL, YAML) |
| Domains | 6 (Eng, Docs, HR, Legal, Security, Business) |

## Table 2: Main Results

| Method | P@5 | NDCG@10 | Latency |
|--------|-----|---------|---------|
| Baseline | 0.640 ± 0.057 | 0.610 ± 0.048 | 38ms |
| **CaaS** | **0.820 ± 0.045** | **0.780 ± 0.042** | 45ms |
| Δ | **+28.1%** | **+27.9%** | +18.4% |

## Table 3: Ablation Study

| Config | P@5 | NDCG@10 | Δ P@5 vs Base |
|--------|-----|---------|---------------|
| Baseline | 0.640 | 0.610 | — |
| + Structure-Aware | 0.740 | 0.700 | +15.6% |
| + Time Decay | 0.700 | 0.670 | +9.4% |
| + Metadata | 0.720 | 0.690 | +12.5% |
| + Pragmatic Truth | 0.680 | 0.650 | +6.3% |
| **Full CaaS** | **0.820** | **0.780** | **+28.1%** |

## Table 4: Statistical Significance

| Metric | t-stat | p-value | Cohen's d |
|--------|--------|---------|-----------|
| P@5 | 22.31 | < 0.001 | 3.36 (large) |
| NDCG@10 | 19.87 | < 0.001 | 2.98 (large) |

## Table 5: Routing Latency

| Router Type | Mean | p95 | p99 |
|-------------|------|-----|-----|
| Heuristic (Ours) | **0.003ms** | 0.005ms | 0.008ms |
| ML-based | 15.2ms | 28.4ms | 45.1ms |
| LLM-based | 450ms | 890ms | 1,200ms |

---

*Data source: benchmarks/results/evaluation_2026-01-20.json, statistical_results.json*
