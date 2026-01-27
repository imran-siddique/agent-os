# CMVK Algorithm: Handling Model Disagreements

> Technical documentation of how CMVK handles disagreements between multiple LLM models.

## Overview

CMVK (Cross-Model Verification Kernel) verifies claims by requiring consensus across multiple heterogeneous LLM models. When models disagree, CMVK must decide whether to:

1. **Accept** - Responses are close enough
2. **Flag** - Responses diverge, needs review
3. **Reject** - Responses contradict, claim is unreliable

## The Algorithm

### Step 1: Collect Responses

Query each model with the same prompt:

```python
responses = []
for model in models:
    response = model.generate(prompt)
    responses.append({
        "model": model.name,
        "response": response,
        "embedding": embed(response)  # For semantic comparison
    })
```

### Step 2: Calculate Pairwise Drift

For each pair of responses, calculate a drift score:

```python
def calculate_drift(response_a, response_b, metric="cosine"):
    """
    Drift = 0.0 means identical
    Drift = 1.0 means completely different
    """
    if metric == "cosine":
        # Cosine distance (1 - similarity)
        sim = dot(a, b) / (norm(a) * norm(b))
        return 1.0 - sim
    
    elif metric == "euclidean":
        # Normalized Euclidean distance
        return norm(a - b) / (norm(a) + norm(b))
    
    elif metric == "semantic":
        # Embedding-based semantic similarity
        emb_a = embed(response_a)
        emb_b = embed(response_b)
        return cosine_distance(emb_a, emb_b)
```

### Step 3: Detect Disagreement

```python
def detect_disagreement(responses, threshold=0.15):
    """
    Calculate all pairwise drifts.
    If max drift > threshold, models disagree.
    """
    drifts = []
    for i in range(len(responses)):
        for j in range(i + 1, len(responses)):
            drift = calculate_drift(responses[i], responses[j])
            drifts.append(drift)
    
    max_drift = max(drifts)
    avg_drift = mean(drifts)
    
    return {
        "disagreement": max_drift > threshold,
        "max_drift": max_drift,
        "avg_drift": avg_drift,
        "confidence": 1.0 - avg_drift
    }
```

### Step 4: Decision Logic

```
                    ┌──────────────────┐
                    │ Collect Responses │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Calculate Drifts  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
         ┌──────────│ max_drift > 0.30 │──────────┐
         │ YES      └──────────────────┘      NO  │
         ▼                                        ▼
┌──────────────────┐                    ┌──────────────────┐
│     REJECT       │                    │ max_drift > 0.15 │
│ (High conflict)  │         ┌──────────│                  │──────────┐
└──────────────────┘         │ YES      └──────────────────┘      NO  │
                             ▼                                        ▼
                    ┌──────────────────┐                    ┌──────────────────┐
                    │      FLAG        │                    │     ACCEPT       │
                    │ (Needs review)   │                    │ (Consensus)      │
                    └──────────────────┘                    └──────────────────┘
```

## Consensus Methods

### 1. Majority Vote

Accept if >50% of models agree:

```python
def majority_vote(responses, ground_truth):
    correct = sum(1 for r in responses if matches(r, ground_truth))
    return correct > len(responses) / 2
```

**Pros:** Simple, tolerates one outlier  
**Cons:** Ignores degree of disagreement

### 2. Unanimous Consensus

Require all models to agree:

```python
def unanimous(responses, ground_truth):
    return all(matches(r, ground_truth) for r in responses)
```

**Pros:** Highest confidence when achieved  
**Cons:** Too strict, often fails

### 3. Drift-Based Consensus (Recommended)

Accept if responses are within drift threshold:

```python
def drift_consensus(responses, threshold=0.15):
    max_drift = calculate_max_drift(responses)
    
    if max_drift > threshold:
        return {
            "decision": "FLAG",
            "reason": f"Drift {max_drift:.2f} exceeds threshold {threshold}",
            "confidence": 1.0 - max_drift
        }
    
    return {
        "decision": "ACCEPT",
        "response": responses[0],  # Any response (they agree)
        "confidence": 1.0 - max_drift
    }
```

**Pros:** Quantitative, tunable, confidence score  
**Cons:** Requires threshold calibration

### 4. Weighted Consensus

Weight models by their reliability:

```python
def weighted_consensus(responses, weights):
    """
    weights = {"gpt-4": 0.4, "claude": 0.35, "gemini": 0.25}
    """
    weighted_sum = sum(
        weights[r.model] * matches(r, ground_truth)
        for r in responses
    )
    return weighted_sum > 0.5
```

**Pros:** Accounts for model quality differences  
**Cons:** Requires weight calibration

## Threshold Selection

### Domain-Specific Thresholds

Different domains have different tolerance for disagreement:

| Domain | Threshold | Rationale |
|--------|-----------|-----------|
| **Medical** | 0.05 | Life-critical, require strong consensus |
| **Financial** | 0.10 | Regulatory risk, conservative |
| **General** | 0.15 | Balanced default |
| **Creative** | 0.30 | High variance expected |

### Calibration Process

1. Create labeled dataset of 100+ examples
2. Run CMVK with various thresholds
3. Plot precision-recall curve
4. Select threshold based on acceptable false positive rate

```python
def calibrate_threshold(labeled_data):
    best_f1 = 0
    best_threshold = 0.15
    
    for threshold in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        precision, recall = evaluate(labeled_data, threshold)
        f1 = 2 * precision * recall / (precision + recall)
        
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    return best_threshold
```

## Handling Edge Cases

### Case 1: Two Models Agree, One Disagrees

```python
if num_clusters == 2 and largest_cluster >= 2:
    # Majority cluster is likely correct
    return {
        "decision": "ACCEPT",
        "response": majority_response,
        "confidence": 0.7,  # Lower confidence due to outlier
        "note": f"{outlier_model} disagrees"
    }
```

### Case 2: All Models Disagree

```python
if all_different(responses):
    return {
        "decision": "REJECT",
        "reason": "No consensus achievable",
        "confidence": 0.0,
        "note": "Consider reformulating the query"
    }
```

### Case 3: Models Agree on Wrong Answer

This is the fundamental limitation of CMVK. If all models share the same training data bias, they'll all be wrong together.

**Mitigations:**
- Use heterogeneous models (different architectures, training data)
- Include at least one open-source model
- For critical domains, include human review in the loop

## Implementation

### Python Interface

```python
from cmvk import CrossModelVerifier

verifier = CrossModelVerifier(
    models=["gpt-4", "claude-sonnet-4", "gemini-pro"],
    consensus_method="drift",
    threshold=0.15
)

result = verifier.verify("What is the capital of France?")

print(f"Answer: {result.response}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Drift: {result.drift_score:.3f}")
print(f"Decision: {result.decision}")
```

### MCP Tool Interface

```json
{
  "name": "cmvk_verify",
  "arguments": {
    "claim": "The capital of France is Paris",
    "models": ["gpt-4", "claude-sonnet-4", "gemini-pro"],
    "threshold": 0.15
  }
}
```

Response:
```json
{
  "verified": true,
  "confidence": 0.95,
  "drift_score": 0.05,
  "model_responses": [
    {"model": "gpt-4", "agrees": true},
    {"model": "claude-sonnet-4", "agrees": true},
    {"model": "gemini-pro", "agrees": true}
  ]
}
```

## Metrics

Key metrics to track:

| Metric | Definition | Target |
|--------|------------|--------|
| **Accuracy** | Correct decisions / Total | >90% |
| **Precision** | True positives / (True + False positives) | >95% |
| **Recall** | True positives / (True + False negatives) | >85% |
| **Flagging Rate** | Flagged for review / Total | <20% |
| **Avg Latency** | Mean response time | <5s |

## Limitations

1. **Cost**: 3x API costs compared to single model
2. **Latency**: ~2-3x slower (parallel calls help)
3. **Correlated Errors**: Models trained on similar data fail together
4. **Threshold Sensitivity**: Wrong threshold leads to over/under-flagging

## References

- [CMVK Source Code](../../packages/cmvk/)
- [Benchmark Suite](../../packages/cmvk/src/cmvk/benchmarks.py)
- [RFC-004: Agent Primitives](../rfcs/RFC-004-Agent-Primitives.md)
