# Carbon Auditor Swarm

An autonomous auditing system for the Voluntary Carbon Market (VCM).

> **"The AI didn't decide; the Math decided. The AI just managed the workflow."**

## Overview

This system ingests a Project Design Document (PDF) claiming "We protected this forest," compares it against historical Satellite Data (Sentinel-2), and outputs a `VerificationReport` using deterministic mathematical verification.

## Architecture (The Swarm)

Three specialized agents communicate over the AMB (Agent Message Bus):

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  claims-agent   │     │   geo-agent     │     │  auditor-agent  │
│  "The Reader"   │     │   "The Eye"     │     │  "The Judge"    │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ • PDF Parser    │────▶│ • Sentinel API  │────▶│ • cmvk Kernel   │
│ • Table Extract │     │ • NDVI Calc     │     │ • Drift Score   │
│                 │     │                 │     │ • FRAUD/VERIFY  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
    [CLAIMS]              [OBSERVATIONS]        [VERIFICATION]
        └───────────────────────┴───────────────────────┘
                            AMB (Message Bus)
```

### Agent A: `claims-agent` (The Reader)
- **Role**: Ingests the PDF (Project Design Document)
- **Tools**: `pdf_parser`, `table_extractor`
- **Output**: Structured `Claim` object with polygon coordinates and claimed NDVI

### Agent B: `geo-agent` (The Eye)
- **Role**: Satellite interface
- **Tools**: `sentinel_api`, `ndvi_calculator`
- **Output**: `Observation` object with actual NDVI from satellite imagery

### Agent C: `auditor-agent` (The Judge)
- **Role**: Decision maker
- **Dependencies**: `cmvk` (Verification Kernel)
- **Output**: Verification result (VERIFIED / FLAGGED / FRAUD)

## The Killer Feature: cmvk

The **Carbon Market Verification Kernel** performs mathematical verification, not LLM inference:

```python
from cmvk import VerificationKernel, DriftMetric

kernel = VerificationKernel()
drift_score = kernel.verify(
    target=claim_vector,      # [0.82 NDVI, 180 tonnes]
    actual=observation_vector, # [0.45 NDVI, 50 tonnes]
    metric=DriftMetric.EUCLIDEAN
)

if drift_score > 0.15:
    return "FRAUD"  # Math decided, not AI
```

**Why this matters for Enterprise Safety**: The verification decision is auditable, deterministic, and explainable—not a black-box LLM response.

## Quick Start

```bash
# Install dependencies
pip install numpy pydantic

# Run the fraud detection demo
python demo_audit.py

# Run the verified scenario
python demo_audit.py --verified

# Run both scenarios
python demo_audit.py --both
```

## Project Structure

```
carbon-auditor-swarm/
├── src/
│   ├── agents/           # Agent implementations
│   │   ├── base.py       # Base Agent class
│   │   ├── claims_agent.py
│   │   ├── geo_agent.py
│   │   └── auditor_agent.py
│   ├── amb/              # Agent Message Bus
│   │   ├── message_bus.py
│   │   └── topics.py
│   ├── atr/              # Agent Tool Registry
│   │   ├── tools.py      # PDF, Sentinel, NDVI tools
│   │   └── registry.py
│   └── cmvk/             # Verification Kernel
│       ├── kernel.py     # Mathematical verification
│       └── vectors.py    # Claim/Observation vectors
├── tests/
│   └── data/             # Mock test data
│       ├── project_design.txt
│       └── sentinel_data.json
├── demo_audit.py         # Main demo script
├── pyproject.toml
└── README.md
```

## Verification Logic

| Drift Score | Status    | Action                            |
|-------------|-----------|-----------------------------------|
| < 0.10      | VERIFIED  | Claims match observations         |
| 0.10 - 0.15 | FLAGGED   | Minor discrepancy, manual review  |
| > 0.15      | FRAUD     | Significant discrepancy, alert    |

## Future: Cryptographic Oracle (ATR Enhancement)

Current tool output:
```json
{"ndvi": 0.5}
```

Future with provenance:
```json
{
  "ndvi": 0.5,
  "signature": "sha256:...",
  "source": "copernicus.eu"
}
```

This enables verification that satellite data hasn't been tampered with.

## License

MIT
