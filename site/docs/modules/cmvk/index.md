---
layout: default
title: CMVK
parent: Modules
nav_order: 1
permalink: /docs/modules/cmvk/
description: "Cross-Model Verification Kernel - detect hallucinations through multi-model consensus."
---

# CMVK - Cross-Model Verification Kernel
{: .fs-9 }

Detect hallucinations by comparing outputs across multiple LLMs.
{: .fs-6 .fw-300 }

---

## Overview

CMVK verifies LLM outputs by checking consistency across multiple models. If models disagree significantly, the output may be a hallucination.

## Quick Start

```python
from agent_os.cmvk import CMVKVerifier

verifier = CMVKVerifier(
    models=["gpt-4", "claude-3", "gemini-pro"],
    threshold=0.8
)

result = await verifier.verify(
    prompt="What is the capital of France?",
    response="Paris is the capital of France."
)

print(result.verified)      # True
print(result.consensus)     # 1.0
print(result.drift_score)   # 0.0
```

## Key Features

- **Multi-model consensus** — Compare outputs across 2+ models
- **Semantic drift detection** — Measure how much responses diverge
- **Hallucination detection** — Flag outputs that models disagree on
- **Batch verification** — Verify multiple outputs efficiently

## API Reference

See [API Reference](/docs/api/) for complete documentation.

## Examples

- [Tutorials](/docs/tutorials/) — Step-by-step guides
- [API Reference](/docs/api/) — Complete API documentation

---

[Back to Modules →](/docs/modules/)
