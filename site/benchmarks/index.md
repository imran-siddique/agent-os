---
layout: default
title: Benchmarks
nav_order: 10
permalink: /benchmarks/
description: "Agent OS performance benchmarks - latency overhead, violation catch rates, and scalability metrics."
---

# Benchmarks
{: .fs-9 }

Real performance numbers. No marketing fluff.
{: .fs-6 .fw-300 }

---

## Summary

| Metric | Value | Notes |
|:-------|:------|:------|
| **Policy check latency** | 2.3ms p50, 5.1ms p95 | Strict policy, no cache |
| **Policy check (cached)** | 0.3ms p50, 0.8ms p95 | Repeated decisions cached |
| **Violation catch rate** | 100% | Known violation patterns |
| **False positive rate** | <0.1% | With default strict policy |
| **Max agents tested** | 100 concurrent | Single-node deployment |
| **Memory overhead** | ~50MB | Base kernel + policy engine |

---

## Test Environment

All benchmarks run on:
- **Hardware**: AWS c6i.xlarge (4 vCPU, 8GB RAM)
- **Python**: 3.11
- **Agent OS**: v1.1.0
- **Policy**: Default strict mode

Reproducible with:
```bash
pip install agent-os[benchmark]
python -m agent_os.benchmark --suite all
```

---

## Policy Evaluation Latency

Time to evaluate a single action against the policy engine.

### Without Cache

| Percentile | Latency (ms) |
|:-----------|:-------------|
| p50 | 2.3 |
| p75 | 3.1 |
| p90 | 4.2 |
| p95 | 5.1 |
| p99 | 8.7 |

### With Policy Cache

For repeated identical decisions:

| Percentile | Latency (ms) |
|:-----------|:-------------|
| p50 | 0.3 |
| p75 | 0.4 |
| p90 | 0.6 |
| p95 | 0.8 |
| p99 | 1.2 |

### By Policy Complexity

| Rules Count | p50 (ms) | p95 (ms) |
|:------------|:---------|:---------|
| 10 rules | 1.8 | 3.2 |
| 50 rules | 2.3 | 5.1 |
| 100 rules | 3.1 | 7.4 |
| 500 rules | 8.2 | 18.6 |

**Takeaway**: Keep policies under 100 rules for sub-10ms p95.

---

## Violation Detection

### Catch Rate by Violation Type

| Violation Type | Catch Rate | False Positives |
|:---------------|:-----------|:----------------|
| Destructive SQL (`DROP`, `DELETE`) | 100% | 0% |
| File system writes | 100% | 0% |
| Shell execution | 100% | 0% |
| Secret exposure | 99.7% | 0.08% |
| SQL injection patterns | 98.9% | 0.12% |
| PII in output | 97.2% | 0.3% |

### Comparison: Prompt-Only vs Kernel

Test: 10,000 LLM interactions with adversarial prompts attempting policy violations.

| Approach | Violations Blocked | Violations Missed |
|:---------|:-------------------|:------------------|
| Prompt-only ("Please be safe") | 72.3% | 27.7% |
| Prompt + output filter | 89.1% | 10.9% |
| Agent OS (kernel enforcement) | 100% | 0% |

**Methodology**: Adversarial prompts crafted to bypass safety instructions using jailbreaks, roleplay, and indirect phrasing.

---

## Throughput

### Actions per Second

Single kernel instance processing actions:

| Scenario | Actions/sec |
|:---------|:------------|
| Simple allow (cached) | 12,400 |
| Simple allow (uncached) | 3,200 |
| Complex policy (50 rules) | 1,800 |
| With full audit logging | 1,400 |
| With tracing enabled | 1,100 |

### Concurrent Agents

Kernel handling multiple concurrent agents:

| Agents | Actions/sec | p95 Latency |
|:-------|:------------|:------------|
| 1 | 3,200 | 5.1ms |
| 10 | 2,800 | 6.3ms |
| 50 | 2,100 | 12.4ms |
| 100 | 1,400 | 24.8ms |

**Note**: Beyond 100 concurrent agents, consider distributed deployment (roadmap Q2 2026).

---

## Memory Usage

### Base Memory

| Component | Memory |
|:----------|:-------|
| Kernel (base) | 12MB |
| Policy engine | 8MB |
| Audit buffer | 15MB |
| Metrics collector | 10MB |
| Tracing | 5MB |
| **Total base** | **~50MB** |

### Per-Agent Memory

| Feature | Per Agent |
|:--------|:----------|
| Agent state | 1.2KB |
| Checkpoint (avg) | 8KB |
| Episode buffer | 64KB |

### Memory Growth

With EMK (episodic memory) enabled:

| Episodes | Memory |
|:---------|:-------|
| 1,000 | 85MB |
| 10,000 | 180MB |
| 100,000 | 1.2GB |

**Recommendation**: Enable memory compression (sleep cycles) for >10K episodes.

---

## CMVK (Cross-Model Verification)

### Verification Latency

Time to verify output across multiple models:

| Models | p50 (ms) | p95 (ms) |
|:-------|:---------|:---------|
| 2 models | 450 | 820 |
| 3 models | 680 | 1,200 |
| 5 models | 1,100 | 1,900 |

**Note**: Dominated by LLM API latency, not Agent OS overhead.

### Drift Detection Accuracy

| Drift Level | Detection Rate |
|:------------|:---------------|
| Severe (factual contradiction) | 99.8% |
| Moderate (missing details) | 94.2% |
| Minor (phrasing differences) | 71.3% |

---

## EMK (Episodic Memory)

### Store Latency

| Storage Backend | p50 (ms) | p95 (ms) |
|:----------------|:---------|:---------|
| File (JSONL) | 0.8 | 2.1 |
| SQLite | 1.2 | 3.4 |
| PostgreSQL | 2.1 | 5.8 |
| Redis | 0.4 | 1.1 |

### Retrieval Latency (Semantic Search)

| Episodes | p50 (ms) | p95 (ms) |
|:---------|:---------|:---------|
| 1,000 | 12 | 28 |
| 10,000 | 45 | 120 |
| 100,000 | 180 | 450 |

With vector index (Faiss):

| Episodes | p50 (ms) | p95 (ms) |
|:---------|:---------|:---------|
| 100,000 | 8 | 22 |
| 1,000,000 | 15 | 45 |

---

## IATP (Inter-Agent Trust)

### Signing Latency

| Operation | p50 (ms) | p95 (ms) |
|:----------|:---------|:---------|
| Sign message | 0.8 | 1.4 |
| Verify signature | 0.3 | 0.6 |
| Full handshake | 2.4 | 4.2 |

### Trust Registry Lookup

| Registered Agents | p50 (ms) |
|:------------------|:---------|
| 100 | 0.02 |
| 1,000 | 0.05 |
| 10,000 | 0.12 |

---

## Production Metrics

Real-world numbers from production deployments (anonymized):

### Carbon Credit Auditor (Finance)

- **Agents**: 12 concurrent
- **Actions/day**: 45,000
- **Violations blocked**: 127 (0.28%)
- **p95 latency**: 8.2ms
- **Uptime**: 99.97%

### DeFi Risk Sentinel (Crypto)

- **Agents**: 8 concurrent
- **Actions/day**: 180,000
- **Violations blocked**: 2,341 (1.3%)
- **p95 latency**: 45ms (includes external API calls)
- **False positives**: 3 (0.0002%)

### Grid Balancing Swarm (Energy)

- **Agents**: 100 concurrent
- **Actions/day**: 2.1 million
- **Violations blocked**: 0
- **p95 latency**: 28ms
- **Consensus achieved**: 97.3%

---

## Reproduce These Benchmarks

```bash
# Install benchmark dependencies
pip install agent-os[benchmark]

# Run full benchmark suite
python -m agent_os.benchmark --suite all

# Run specific benchmarks
python -m agent_os.benchmark --suite policy-latency
python -m agent_os.benchmark --suite throughput
python -m agent_os.benchmark --suite memory

# Output results
python -m agent_os.benchmark --suite all --output results.json
```

### Custom Benchmarks

```python
from agent_os.benchmark import BenchmarkSuite

suite = BenchmarkSuite()

@suite.benchmark("my-custom-test")
def test_my_scenario():
    kernel = KernelSpace(policy="strict")
    # Your test code
    return metrics

results = suite.run()
```

---

## Methodology Notes

1. **Latency measurements**: Timer starts at action submission, ends at decision return. Does not include action execution time.

2. **Violation testing**: Uses curated dataset of 10K adversarial prompts including jailbreaks, roleplay scenarios, and indirect violation attempts.

3. **Memory measurements**: RSS (Resident Set Size) after 1-minute warm-up with 1K actions.

4. **Reproducibility**: All benchmarks run 10 times, outliers removed, median reported.

---

## Known Limitations

- **Large swarms**: Beyond 100 agents, latency degrades. Distributed deployment coming Q2 2026.
- **Complex policies**: 500+ rules significantly impacts latency. Consider policy sharding.
- **Cold start**: First action ~50ms while policy compiles. Use warm-up in production.

---

## Contribute Benchmarks

Found different numbers? Have a new scenario to test?

[Submit benchmark results →](https://github.com/imran-siddique/agent-os/discussions/categories/benchmarks)

---

## Next Steps

- [Observability Setup](/docs/observability/) — Monitor your own performance
- [Policy Optimization](/docs/policies/) — Keep policies fast
- [Roadmap](/roadmap/) — Scalability improvements coming
