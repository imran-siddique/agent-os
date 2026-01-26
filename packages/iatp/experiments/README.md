# IATP Experiments

Research experiments demonstrating the effectiveness of the Inter-Agent Trust Protocol.

## Cascading Hallucination Prevention

**Location**: `cascading_hallucination/`

This experiment demonstrates how IATP prevents cascading failures in multi-agent systems.

### The Problem

In multi-agent systems, a single "poisoned" agent can inject malicious instructions that propagate through the chain, causing catastrophic failures:

```
Agent A (User) → Agent B (Poisoned) → Agent C (Database)
      ↓                ↓                    ↓
  "Summarize"    "DELETE ALL"      ❌ Data Lost Forever
```

### The Solution

IATP's sidecar intercepts requests and validates them against the agent's capability manifest:

```
Agent A (User) → Agent B (Poisoned) → IATP Sidecar → Agent C (Database)
      ↓                ↓                  ↓               ↓
  "Summarize"    "DELETE ALL"      🚫 BLOCKED      ✅ Data Safe
```

### Results

| Group | IATP Protection | Failure Rate |
|-------|-----------------|--------------|
| Control | ❌ None | **100%** (DELETE executed) |
| Test | ✅ Enabled | **0%** (BLOCKED) |

### Running the Experiment

#### Option 1: Standalone Proof of Concept
```bash
python experiments/cascading_hallucination/proof_of_concept.py
```

#### Option 2: Full Multi-Agent Experiment (requires Docker)
```bash
python experiments/cascading_hallucination/run_experiment.py
```

See [cascading_hallucination/README.md](cascading_hallucination/README.md) for detailed instructions.

## Research Paper

The results of these experiments are documented in the research paper:

- **Title**: "The Trust Boundary: Preventing Cascading Hallucinations in Multi-Agent AI Systems"
- **Location**: [paper/PAPER.md](../paper/PAPER.md)
- **Key Finding**: IATP reduces cascading failure rates from 100% to 0%
