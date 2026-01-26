## Ablation Study Results

| Component Removed | Metric | Baseline (mean±std) | Ablation (mean±std) | p-value | Cohen's d | Impact |
|-------------------|--------|---------------------|---------------------|---------|-----------|--------|
| Semantic Purge | context_reduction_percent | 50.0±0.0 | 0.0±0.0 | <0.0001 | 999.90 | **CRITICAL** |
| Semantic Purge | accuracy_retention | 1.0±0.0 | 1.0±0.0 | <0.0001 | 0.00 | **CRITICAL** |
| Differential Auditing | laziness_detection_rate_percent | 100.0±0.0 | 0.0±0.0 | <0.0001 | 999.90 | **CRITICAL** |
| Differential Auditing | correction_rate_percent | 72.0±0.0 | 0.0±0.0 | <0.0001 | 999.90 | **CRITICAL** |
| Shadow Teacher (o1-preview) | correction_rate_percent | 72.0±0.0 | 43.6±2.3 | <0.0001 | 17.13 | **IMPORTANT** |
| Shadow Teacher (o1-preview) | patch_quality_percent | 85.0±0.0 | 64.2±7.0 | <0.0001 | 4.23 | **IMPORTANT** |
| Tiered Memory Hierarchy | latency_ms | 94.5±6.4 | 341.7±29.3 | <0.0001 | 11.66 | **IMPORTANT** |
| Tiered Memory Hierarchy | context_size_tokens | 1522.2±88.1 | 2793.0±178.1 | <0.0001 | 9.04 | **IMPORTANT** |
