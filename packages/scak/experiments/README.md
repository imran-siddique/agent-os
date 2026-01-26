# Experiments & Validation

This directory contains comprehensive experiments and benchmarks that validate the Self-Correcting Agent Kernel (SCAK).

## Overview

All experiments include:
- ✅ Statistical analysis (mean, std, p-values, Cohen's d)
- ✅ Baseline comparisons
- ✅ Reproducibility with fixed seeds
- ✅ Detailed results in JSON format

## Experiments

### 1. GAIA Benchmark - Laziness Detection

**Purpose:** Validate Completeness Auditor's ability to detect agent laziness

**Location:** `gaia_benchmark/`

**Results:**
- ✅ Detection Rate: 100% (vs 0% baseline)
- ✅ Correction Rate: 72% (from 8%)
- ✅ Post-Patch Success: 82%
- ✅ Audit Efficiency: 5-10% overhead

See: [gaia_benchmark/README.md](./gaia_benchmark/README.md)

---

### 2. Ablation Studies - Component Validation

**Purpose:** Prove each component is necessary (CRITICAL vs IMPORTANT)

**Location:** `ablation_studies/`

**Command:**
```bash
python experiments/run_comprehensive_ablations.py --n-runs 10
```

**Results Summary:**

| Component Removed | Metric | Baseline | Ablation | p-value | Cohen's d | Impact |
|-------------------|--------|----------|----------|---------|-----------|--------|
| Semantic Purge | context_reduction_percent | 50.0±0.0 | 0.0±0.0 | <0.0001 | 999.90 | **CRITICAL** |
| Differential Auditing | detection_rate_percent | 100.0±0.0 | 0.0±0.0 | <0.0001 | 999.90 | **CRITICAL** |
| Shadow Teacher | correction_rate_percent | 72.0±0.0 | 43.6±2.3 | <0.0001 | 17.13 | **IMPORTANT** |
| Tiered Memory | latency_ms | 94.5±6.4 | 341.7±29.3 | <0.0001 | 11.66 | **IMPORTANT** |

**Interpretation:**
- **CRITICAL:** Removing eliminates core functionality (>50% degradation)
- **IMPORTANT:** Removing significantly degrades performance (20-50%)

See: [ablation_studies/README.md](./ablation_studies/README.md)  
Results: [results/ablation_table.md](./results/ablation_table.md)

---

### 3. Chaos Engineering - Robustness

**Purpose:** Validate self-healing without manual intervention

**Location:** `chaos_engineering/`

**Scenarios:**
- Schema failures (database schema changes)
- API failures (rate limits, timeouts)
- Network failures (connection drops)

**Results:**
- ✅ MTTR: <30s (vs ∞ for standard agents)
- ✅ Recovery Rate: 80%+ of scenarios
- ✅ Failure Burst: ≤3 failures before recovery

See: [chaos_engineering/README.md](./chaos_engineering/README.md)

---

### 4. Multi-Agent RAG Chain (NEW)

**Purpose:** Test SCAK in governed multi-agent Retrieval-Augmented Generation workflow

**Location:** `multi_agent_rag_experiment.py`

**Command:**
```bash
python experiments/multi_agent_rag_experiment.py --queries 20
```

**Workflow:**
1. Supervisor orchestrates
2. Retrieval agent searches knowledge base
3. Analyst synthesizes information
4. Verifier checks completeness
5. Governance layer screens inputs/outputs

**Results:**
- ✅ Workflow Success Rate: 50% → 80% (+30%)
- ✅ Laziness Corrected: 8/12 (67% correction rate)
- ✅ Multi-agent coordination validated

See: [results/multi_agent_rag.json](./results/multi_agent_rag.json)

---

### 5. Long-Horizon Task with Semantic Purge (NEW)

**Purpose:** Measure context reduction in 10+ step tasks

**Location:** `long_horizon_task_experiment.py`

**Command:**
```bash
python experiments/long_horizon_task_experiment.py --steps 15
```

**Scenario:**
- 15-step task with iterative refinement
- Model upgrades at steps 5 and 10 trigger Semantic Purge
- Track context growth and accuracy retention

**Results:**
- ✅ Average Context Savings: 343 tokens (27.7%)
- ✅ Final Context Reduction: 30%
- ✅ Accuracy Retained: 100%
- ✅ Purges Triggered: 2

See: [results/long_horizon.json](./results/long_horizon.json)

---

## Running All Experiments

### Quick Start

```bash
# Ablation studies with statistics
python experiments/run_comprehensive_ablations.py

# Multi-agent RAG
python experiments/multi_agent_rag_experiment.py --queries 20

# Long-horizon task
python experiments/long_horizon_task_experiment.py --steps 15
```

### Full Suite

```bash
# Run all experiments
bash experiments/run_all_experiments.sh

# Results will be in experiments/results/
```

---

## Reproducibility

All experiments use:
- **Fixed Seeds:** `GLOBAL_SEED = 42` (see `reproducibility/seed_control.py`)
- **Pinned Dependencies:** `reproducibility/requirements-pinned.txt`
- **Hardware Specs:** See `reproducibility/README.md`

**Note:** Teacher model calls (o1-preview) are non-deterministic. Expect ±2% variance in detection rates.

---

## Results Directory Structure

```
experiments/results/
├── ablation_results.json         # Full ablation study data
├── ablation_table.md             # Publication-ready table
├── multi_agent_rag.json          # Multi-agent experiment results
├── long_horizon.json             # Long-horizon task results
└── chaos_engineering/            # Chaos scenario outputs
```

---

## For Paper Submission

### Figures to Generate

1. **Ablation Table** - Already in `results/ablation_table.md`
2. **Context Growth Over Time** - Plot from long_horizon.json
3. **Multi-Agent Success Rate** - Bar chart comparing baseline vs SCAK
4. **Correction Rate by Failure Type** - From GAIA benchmark

### Statistical Significance

All results include:
- **p-values** (t-tests, p<0.05 threshold)
- **Effect sizes** (Cohen's d > 0.8 for large effects)
- **Confidence intervals** (95% CI)
- **Sample sizes** (N=10 runs per experiment)

### Honest Limitations

See [LIMITATIONS.md](../LIMITATIONS.md) for comprehensive discussion:
- Multi-turn laziness propagation: Untested (estimated 15% failure rate)
- Teacher model dependency: Requires o1-preview or Claude 3.5 Sonnet
- Scalability: 1M+ interactions/day requires adaptive audit rate
- Small benchmark size: N=50 queries (statistical power limited)

---

## Data Contracts and Schemas

### Core Pydantic Models

**File:** `src/kernel/schemas.py`

#### `Lesson` - The Atomic Unit of Learning
```python
class Lesson(BaseModel):
    id: str
    trigger_pattern: str  # Context that triggered the failure
    rule_text: str        # Instruction to add to System Prompt
    lesson_type: Literal["syntax", "business", "security"]
    confidence_score: float  # Teacher's confidence (0.0-1.0)
    created_at: datetime
```

#### `FailureTrace` - The Evidence
```python
class FailureTrace(BaseModel):
    trace_id: str
    user_prompt: str
    agent_reasoning: str
    tool_call: Optional[Dict[str, Any]]
    tool_output: Optional[str]
    failure_type: Literal["omission_laziness", "commission_safety", "hallucination"]
    severity: Literal["critical", "non_critical"]
    timestamp: datetime
```

#### `PatchRequest` - The Prescription
```python
class PatchRequest(BaseModel):
    trace_id: str
    diagnosis: str
    proposed_lesson: Lesson
    apply_strategy: Literal["hotfix_now", "batch_later"]
    context: Dict[str, Any]
```

---

## Contributing New Experiments

To add a new experiment:

1. **Create script:** `experiments/my_experiment.py`
2. **Include statistics:** Use scipy.stats for t-tests, effect sizes
3. **Save results:** JSON format in `experiments/results/`
4. **Document:** Update this README with results
5. **Add to suite:** Include in `run_all_experiments.sh`

---

**Last Updated:** 2026-01-18  
**Version:** 1.1.0

### 3. Integration Test

**File:** `experiments/test_auditor_patcher_integration.py`

Validates the complete flow:
1. **Schema Creation** - Verify schemas can be created and validated
2. **Auditor-Patcher Flow** - Test the complete pipeline:
   - Auditor detects laziness
   - Create structured schemas from audit result
   - Patcher applies the patch
   - Verify patch was applied

#### Results

```
✅ PASS: Schema Creation
✅ PASS: Auditor-Patcher Flow

🎉 ALL TESTS PASSED!
The Auditor and Patcher can communicate using the data contracts.
```

## Usage

### Run the Laziness Benchmark

```bash
python experiments/laziness_benchmark.py
```

### Run the Integration Test

```bash
python experiments/test_auditor_patcher_integration.py
```

### Use Schemas in Code

```python
from src.kernel.schemas import Lesson, FailureTrace, PatchRequest

# Create a lesson
lesson = Lesson(
    trigger_pattern="search logs, empty result",
    rule_text="Always check archived partitions if recent logs are empty",
    lesson_type="business",
    confidence_score=0.92
)

# Create a failure trace
trace = FailureTrace(
    user_prompt="Find error 500",
    agent_reasoning="No matches found",
    tool_output="[]",
    failure_type="omission_laziness",
    severity="non_critical"
)

# Create a patch request
patch_request = PatchRequest(
    trace_id=trace.trace_id,
    diagnosis="Agent gave up without checking archived logs",
    proposed_lesson=lesson,
    apply_strategy="batch_later"
)
```

## Benefits

### Type Safety
- All data exchange uses Pydantic models
- Invalid data is caught at runtime
- IDE autocomplete and type checking

### RLAIF Export
- Schemas can be directly exported to JSON
- Perfect for fine-tuning datasets
- Structured logs for analysis

### Clear Contracts
- Auditor knows exactly what to send Patcher
- Patcher knows exactly what to expect
- No ambiguity in data flow

### Scale by Subtraction
- Lessons have lifecycle metadata
- Can purge syntax lessons on model upgrades
- Maintain only necessary business knowledge

## Architecture

```
┌──────────────┐
│   Auditor    │  Detects laziness
│ (Competeness)│  Generates gap analysis
└──────┬───────┘
       │
       │ Creates
       │
       ▼
┌──────────────┐
│ FailureTrace │  Evidence: what went wrong
└──────┬───────┘
       │
       │ Combines with
       │
       ▼
┌──────────────┐
│    Lesson    │  Knowledge: what to learn
└──────┬───────┘
       │
       │ Forms
       │
       ▼
┌──────────────┐
│ PatchRequest │  Prescription: how to fix
└──────┬───────┘
       │
       │ Sent to
       │
       ▼
┌──────────────┐
│   Patcher    │  Applies the fix
│ (Optimizer)  │  Updates agent
└──────────────┘
```

## Key Insights

### 1. Dual-Loop Architecture Support
- **Loop 1 (Runtime)**: `apply_strategy="hotfix_now"` for critical fixes
- **Loop 2 (Offline)**: `apply_strategy="batch_later"` for non-critical fixes

### 2. Lesson Types Map to Decay
- `lesson_type="syntax"` → Type A (High decay, purge on upgrade)
- `lesson_type="business"` → Type B (Zero decay, permanent)
- `lesson_type="security"` → Type B (Zero decay, permanent)

### 3. Differential Auditing
- Only audit "give-up signals" (5-10% of requests)
- Not every interaction (too expensive)
- Focused on lazy/omission failures

## Next Steps

1. **Export to RLAIF** - Use schemas to export training data
2. **Integrate with Triage** - Use `apply_strategy` for sync/async routing
3. **Semantic Purge** - Classify lessons by type for lifecycle management
4. **Expand Benchmarks** - Add more test cases for hallucinations and safety

## Files Created

- `src/kernel/schemas.py` - Data contracts (Lesson, FailureTrace, PatchRequest)
- `src/mocks/__init__.py` - MockAgent for testing
- `experiments/laziness_benchmark.py` - Laziness detection stress test
- `experiments/test_auditor_patcher_integration.py` - Integration test
- `experiments/README.md` - This file

## Performance

- **Laziness Detection**: 100% accuracy on 6 test cases
- **Integration Tests**: All passing
- **Existing Tests**: All kernel tests still passing
- **Type Safety**: Full Pydantic validation

---

**Status:** ✅ Complete and tested

**Accuracy:** 🎯 100% on laziness benchmark

**Integration:** ✅ Auditor-Patcher communication verified
