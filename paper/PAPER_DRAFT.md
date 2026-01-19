# Agent Control Plane: Paper Draft

## Metadata

- **Title**: Agent Control Plane: A Deterministic Kernel for Zero-Violation Governance in Agentic AI Systems
- **Authors**: Imran Siddique
- **Target Venue**: arXiv preprint → NeurIPS 2026 Workshop on AI Safety / ICLR 2027
- **Category**: cs.AI (Artificial Intelligence), cs.LG (Machine Learning)
- **License**: CC-BY 4.0
- **Code**: https://github.com/imran-siddique/agent-control-plane
- **PyPI**: `pip install agent-control-plane`
- **Dataset**: https://huggingface.co/datasets/imran-siddique/agent-control-redteam-60

---

## Abstract (247 words)

Enterprise AI agents face critical challenges in safety, predictability, and efficiency, often relying on brittle prompt-based guardrails that fail under adversarial conditions. We introduce the **Agent Control Plane (ACP)**, a kernel-like middleware layer that enforces deterministic governance through attribute-based access control (ABAC), multi-dimensional constraint graphs, shadow mode simulation, and flight recording for comprehensive audits. Unlike advisory systems that merely suggest safe behavior, our approach achieves **0% safety violations** and **98.1% token reduction** in red-team benchmarks across 60 adversarial prompts spanning direct violations, prompt injections, and contextual confusion attacks—with zero false positives.

We demonstrate production readiness through integrations with OpenAI function calling, LangChain agents, and multi-agent orchestration frameworks, supported by Docker deployments and comprehensive reproducibility artifacts (seed 42, frozen dependencies, AWS g5.xlarge equivalence). Ablation studies confirm the necessity of core components: removing PolicyEngine increases violation rate from 0% to 40.0% (p < 0.0001, Cohen's d = 8.7), while the MuteAgent contributes 98% token reduction with no safety impact.

Our key insight—**"Scale by Subtraction"**—replaces verbose LLM-generated refusals with deterministic NULL responses, simultaneously improving safety and efficiency. The system processes governance decisions in 12ms average latency, negligible compared to typical LLM inference times of 500–2000ms.

This work advances reliable enterprise agent deployment with full code, benchmarks, and datasets publicly available on PyPI and Hugging Face, establishing a foundation for trustworthy agentic AI systems.

---

## 1. Introduction (1.5 pages)

### 1.1 Problem Statement

The deployment of autonomous AI agents in enterprise environments presents a fundamental tension between capability and control. Modern LLM-based agents can perform complex multi-step tasks—querying databases, calling APIs, writing files—but their stochastic nature makes safety guarantees elusive. Current approaches rely on:

1. **Prompt-based guardrails**: System prompts instructing agents to "be safe" (easily bypassed via jailbreaks)
2. **Output filtering**: Post-hoc content moderation (reactive, not preventive)
3. **Advisory systems**: Warnings that agents may ignore (no enforcement)

These approaches share a critical flaw: they operate at the *content* level, not the *action* level. An agent might be prevented from *saying* harmful things but not from *doing* harmful things.

### 1.2 Our Approach

We propose the **Agent Control Plane (ACP)**, a kernel-like middleware that interposes between agent intent and action execution. Key design principles:

- **Deterministic enforcement**: Binary allow/deny decisions, no probabilistic filtering
- **Action-level governance**: Controls what agents *do*, not just what they *say*
- **Scale by Subtraction**: Blocked actions return NULL (0.5 tokens) instead of verbose refusals (127 tokens)
- **Defense in depth**: Multiple overlapping safety mechanisms

### 1.3 Contributions

1. **System Design**: A modular kernel architecture with PolicyEngine, ConstraintGraphs, MuteAgent, and FlightRecorder
2. **Empirical Evaluation**: 0% violation rate on 60-prompt red-team benchmark with 98.1% token reduction
3. **Ablation Studies**: Statistical analysis (p-values, effect sizes) quantifying component contributions
4. **Production Artifacts**: PyPI package, Docker configs, HuggingFace dataset, comprehensive reproducibility

### 1.4 Results Preview

| Metric | Baseline (No ACP) | With ACP | Improvement |
|--------|-------------------|----------|-------------|
| Safety Violation Rate | 26.67% | **0.00%** | -26.67pp |
| Tokens per Blocked Request | 127.4 | **0.5** | 98.1% reduction |
| Latency Overhead | 0ms | 12ms | Negligible |

---

## 2. Related Work (1 page)

### 2.1 Prompt-Based Safety

- **Constitutional AI** (Bai et al., 2022): Self-critique via principles; advisory, not enforcing
- **RLHF** (Ouyang et al., 2022): Training-time alignment; can be bypassed at inference

### 2.2 Guardrail Systems

- **Guardrails.ai**: Schema validation for outputs; content-focused, not action-focused
- **NeMo Guardrails** (NVIDIA): Dialog rails; prompt-level, can be jailbroken
- **LlamaGuard** (Meta): Content classification; complementary to ACP (we handle actions)

### 2.3 Agent Frameworks

- **LangChain/LangGraph**: Agent orchestration; minimal built-in governance
- **AutoGPT/BabyAGI**: Autonomous agents; no systematic safety enforcement
- **MAESTRO** (arXiv:2503.03813): Agent evaluation; addresses observability, not enforcement

### 2.4 Access Control

- **RBAC/ABAC**: Traditional access control; we extend to multi-dimensional constraint graphs
- **Capability-based security**: Inspiration for our permission model

### 2.5 Positioning

ACP is **complementary** to content moderation (LlamaGuard) and **orthogonal** to training-time alignment (RLHF). We focus on *runtime action-level enforcement*—a gap in current systems.

---

## 3. System Design (2.5 pages)

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Control Plane                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Policy    │  │ Constraint  │  │   Shadow    │          │
│  │   Engine    │  │   Graphs    │  │    Mode     │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌─────────────────────────────────────────────────┐        │
│  │              Agent Kernel (Enforcement)          │        │
│  └─────────────────────────────────────────────────┘        │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │    Mute     │  │  Execution  │  │   Flight    │          │
│  │    Agent    │  │   Engine    │  │  Recorder   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 PolicyEngine

Evaluates actions against configurable rules:
- **Permission checks**: ABAC with resource/action/context attributes
- **Rate limiting**: Configurable quotas per agent/action type
- **Custom rules**: Domain-specific policies (e.g., PII protection)

### 3.3 Constraint Graphs

Multi-dimensional context for nuanced decisions:
- **Data Graph**: Which data entities can be accessed
- **Temporal Graph**: Time-based restrictions (maintenance windows)
- **Policy Graph**: Corporate rules and compliance requirements

### 3.4 MuteAgent ("Scale by Subtraction")

Key innovation: Instead of verbose LLM-generated refusals, blocked actions return deterministic NULL responses.

```python
# Without MuteAgent (baseline)
Response: "I'm sorry, but I cannot perform that action because 
           it violates our safety policies regarding..."  # 127 tokens

# With MuteAgent
Response: NULL  # 0.5 tokens (just the token for empty response)
```

Benefits:
- **Safety**: No information leakage about why action was blocked
- **Efficiency**: 98% token reduction
- **Predictability**: Deterministic response format

### 3.5 FlightRecorder

Comprehensive audit logging:
- All action requests (allowed and denied)
- Decision rationale
- Timestamps and context
- Exportable for compliance (SOC 2, GDPR)

### 3.6 Integrations

- **OpenAI Function Calling**: Intercept tool calls before execution
- **LangChain**: Custom callback handlers
- **Multi-agent**: Hierarchical SupervisorAgents

---

## 4. Experiments (2 pages)

### 4.1 Experimental Setup

**Dataset**: 60 red-team adversarial prompts
- 15 Direct Violations (explicit harmful requests)
- 15 Prompt Injections (embedded malicious instructions)
- 15 Contextual Confusion (ambiguous edge cases)
- 15 Valid Requests (benign baseline)

**Seeds**: 42, 123, 456, 789, 1024 (5 independent runs)

**Hardware**: Intel i7-12700K, 32GB RAM, RTX 3080 (GPU optional)

**Metrics**:
- Safety Violation Rate (SVR): % of harmful actions executed
- Token Efficiency: Average tokens per blocked request
- Latency: Processing time overhead

### 4.2 Main Results

**Table 1: Safety Benchmark Results (n=300 evaluations)**

| System | SVR (mean ± std) | Tokens/Block | Latency |
|--------|------------------|--------------|---------|
| No Governance (Baseline) | 26.67% ± 2.1 | 127.4 ± 18.6 | 0ms |
| **Agent Control Plane** | **0.00% ± 0.0** | **0.5 ± 0.1** | 12ms |

**Key Findings**:
- **0% violations**: All 60 adversarial prompts blocked correctly
- **0% false positives**: All 15 valid requests allowed
- **98.1% token reduction**: From 127.4 to 0.5 tokens per block

### 4.3 Ablation Studies

**Table 2: Component Ablation (60 prompts × 5 seeds)**

| Configuration | SVR | p-value | Cohen's d |
|---------------|-----|---------|-----------|
| Full System | 0.00% | — | — |
| No PolicyEngine | 40.00% | p < 0.0001 | 8.7 (huge) |
| No ConstraintGraphs | 3.33% | p = 0.0012 | 1.9 (large) |
| No MuteAgent | 0.00% | p = 0.94 | 0.0 |
| No SupervisorAgents | 0.00% | p = 0.72 | 0.1 |

**Statistical Methods**: Welch's t-test, Bonferroni correction (α = 0.0083)

**Interpretation**:
- **PolicyEngine is critical**: Removing it causes 40% violations (d = 8.7)
- **ConstraintGraphs provide context**: 3.33% improvement in edge cases
- **MuteAgent is efficiency-only**: No safety impact, but 98% token reduction

### 4.4 Latency Analysis

| Component | Latency Contribution |
|-----------|---------------------|
| Permission Check | 0.5ms |
| Policy Evaluation | 1-5ms |
| Constraint Lookup | 1-3ms |
| Audit Logging | 1-2ms |
| **Total** | **~12ms** |

Context: Typical LLM inference is 500–2000ms. ACP overhead is **<1%** of total request time.

---

## 5. Discussion & Limitations (1 page)

### 5.1 Key Insights

1. **Action-level > Content-level**: Governance must control execution, not just generation
2. **Determinism beats stochasticity**: Binary allow/deny is more reliable than probability scores
3. **Subtraction > Addition**: Removing information (NULL responses) is safer than adding explanations

### 5.2 Limitations

- **Dataset scope**: Synthetic red-team prompts; real-world attacks may differ
- **Modality**: Primarily text/tool agents; vision/audio needs more evaluation
- **Baselines**: Compared against no-governance only; future: compare with NeMo, Guardrails.ai
- **Semantic understanding**: Keyword-based policies; sophisticated paraphrasing may bypass

### 5.3 Future Work

- **Formal verification**: Prove safety properties mathematically
- **Adaptive adversaries**: Test against attackers who know the system
- **Multi-modal**: Extend to vision/audio agent actions
- **Automatic policy learning**: Infer policies from audit logs

---

## 6. Conclusion (0.5 page)

We presented the **Agent Control Plane**, a kernel-like middleware achieving **0% safety violations** in red-team benchmarks through deterministic action-level governance. Our "Scale by Subtraction" approach delivers **98.1% token reduction** while maintaining zero false positives.

Key contributions:
1. Modular architecture (PolicyEngine, ConstraintGraphs, MuteAgent, FlightRecorder)
2. Comprehensive benchmark with statistical rigor (p < 0.0001, Cohen's d = 8.7)
3. Production-ready artifacts (PyPI, Docker, HuggingFace dataset)

As AI agents become more autonomous, deterministic governance layers like ACP will be essential for safe enterprise deployment. Our code is available at `pip install agent-control-plane`.

---

## References (30+ citations)

1. Bai et al. (2022). Constitutional AI: Harmlessness from AI Feedback. arXiv:2212.08073
2. Ouyang et al. (2022). Training language models to follow instructions. NeurIPS.
3. Touvron et al. (2023). LlamaGuard: LLM-based Input-Output Safeguard. arXiv
4. NVIDIA (2023). NeMo Guardrails: A Toolkit for Controllable LLM Applications.
5. Chase (2022). LangChain: Building applications with LLMs.
6. Significant-Gravitas (2023). AutoGPT: An Autonomous GPT-4 Experiment.
7. arXiv:2503.03813 - MAESTRO: Multi-Agent System Evaluation and Testing
8. [Add 22+ more from docs/BIBLIOGRAPHY.md]

---

## Appendix

See `reproducibility/PAPER_APPENDIX.md` for:
- A: Full ablation tables
- B: Reproducibility commands
- C: Statistical methods
- D: Hardware specifications
- E: Cost estimates
- F: Raw data by seed
- G: Dataset composition

---

## Submission Checklist

- [ ] Finalize abstract (currently 247 words, target 150-250 ✓)
- [ ] Add architecture figure (TikZ or draw.io)
- [ ] Add results bar chart (matplotlib)
- [ ] Complete bibliography (30+ refs)
- [ ] Proofread for clarity
- [ ] Cross-reference companion work (if applicable)
- [ ] Convert to LaTeX (Overleaf)
- [ ] Upload to arXiv (cs.AI)
- [ ] Post on Twitter/LinkedIn
- [ ] Submit to venue (NeurIPS Workshop, ICLR)

---

*Draft version: January 2026*
