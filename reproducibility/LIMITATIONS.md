# Limitations & Future Work

This document discusses the limitations of our empirical evaluation and areas for future research.

## Evaluation Limitations

### 1. Dataset Scope

**Synthetic/Controlled Benchmarks**:
- Red-team dataset (60 prompts) is synthetic, designed for coverage not realism
- Prompts are relatively short (<200 tokens) vs. real-world enterprise tasks
- Attack vectors are based on known patterns; novel attacks may bypass detection

**Implications**:
- Real-world enterprise tasks may have different attack surfaces
- Production deployments should continuously update threat patterns
- Consider domain-specific red-teaming for specialized applications

### 2. LLM Stochasticity

**Variance in Results**:
- Results averaged over 5 seeds (42, 123, 456, 789, 1024)
- LLM responses are non-deterministic even with temperature=0
- Production variance may be higher with different prompts/contexts

**Mitigation Applied**:
- Multiple seeds with mean ± std reporting
- Bonferroni-corrected p-values for statistical rigor
- Large effect sizes (Cohen's d > 2) indicate robust findings

**Future Work**:
- Increase to 10+ seeds for tighter confidence intervals
- Characterize variance across different LLM providers/versions

### 3. Modality Coverage

**Current Scope**: Primarily text-based tool-use agents

| Modality | Coverage | Notes |
|----------|----------|-------|
| Text/Tool-use | ✅ Full | 60-prompt benchmark |
| Vision | ⚠️ Partial | Capability exists, not benchmarked |
| Audio | ⚠️ Partial | Capability exists, not benchmarked |
| Long-horizon (100+ steps) | ⚠️ Partial | Tested qualitatively only |
| Multi-agent coordination | ⚠️ Partial | SupervisorAgents exist, not stress-tested |

**Future Work**:
- Multimodal safety benchmarks (image/audio injection attacks)
- Long-horizon task benchmarks (AutoGPT-style multi-step plans)
- Multi-agent adversarial scenarios

### 4. Baseline Comparisons

**Limited Baselines**:
- Compared against "no governance" baseline only
- Did not compare against other safety frameworks (Guardrails AI, LlamaGuard, NeMo Guardrails)

**Rationale**:
- ACP is complementary to (not competing with) content moderation systems
- ACP focuses on action-level enforcement, others focus on content filtering
- Direct comparison would require adapting other systems to action governance

**Future Work**:
- Integrate with Guardrails AI/LlamaGuard and measure combined effectiveness
- Compare latency/overhead with other governance approaches

### 5. Cost Considerations

**Current Costs**:
- ~$0.15-0.25 for full 60-prompt red-team run
- PolicyEngine adds ~12ms latency (negligible vs. LLM inference)

**Potential Production Costs**:
- ML-based safety features (JailbreakDetector, AnomalyDetector) may require GPU
- High-throughput scenarios (>1000 agents) may need horizontal scaling
- Constitutional AI self-critique doubles LLM calls (2x cost)

**Future Work**:
- Distillation: Train smaller safety models from larger teachers
- Caching: Reuse policy decisions for similar requests
- Tiered safety: Use lighter checks for low-risk operations

---

## Methodological Limitations

### 6. Statistical Testing

**Approach Used**:
- Welch's t-test (unequal variances assumed)
- Bonferroni correction for multiple comparisons
- Cohen's d for effect sizes

**Limitations**:
- t-test assumes approximately normal distributions
- Small sample sizes (n=5 seeds) limit statistical power
- Effect sizes are point estimates without confidence intervals

**Future Work**:
- Bootstrap confidence intervals for effect sizes
- Non-parametric alternatives (Mann-Whitney U)
- Power analysis for determining optimal seed count

### 7. Generalization Claims

**Scope of Claims**:
- Results apply to: text-based enterprise tool-use agents
- Results may not apply to: embodied agents, creative writing agents, multi-user systems

**Assumptions**:
- Policies are correctly configured
- Attack prompts are representative of real threats
- LLM behavior is consistent across versions

---

## Threats to Validity

### Internal Validity
- **Selection bias**: Red-team prompts were designed to test specific components
- **Instrumentation**: Results depend on specific LLM versions (gpt-4o-2024-08-06)

### External Validity
- **Generalization**: Results from synthetic benchmark may not transfer to production
- **Population**: Tested on limited set of attack patterns

### Construct Validity
- **Measurement**: "Safety Violation Rate" is binary; doesn't capture severity
- **Operationalization**: "Token Reduction" measures efficiency but not quality

---

## Future Research Directions

1. **Adaptive Adversaries**: Test against attackers who know the system design
2. **Formal Verification**: Prove safety properties mathematically
3. **Human Studies**: Measure user trust and adoption barriers
4. **Longitudinal Studies**: Track safety drift over extended deployments
5. **Cross-Domain Transfer**: Test policies trained in one domain on another

---

*See also: [docs/LIMITATIONS.md](../docs/LIMITATIONS.md) for system limitations*

*Last updated: January 2026 | Version 1.1.0*
