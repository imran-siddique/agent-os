# Pharma Compliance Swarm

**Find the Contradictions Humans Miss**

> "Watch 50 adverse event reports analyzed in 2 minutes with full audit trail."

## 🎬 Demo Video

[![Pharma Compliance Demo](https://img.shields.io/badge/Watch-Demo%20Video-red?style=for-the-badge&logo=youtube)](https://github.com/imran-siddique/agent-os)

**Script (60 seconds):**
```
[0:00] "50 adverse event reports. FDA requires review within 15 days."
[0:10] [Agent swarm activates: Reader, Classifier, Escalator]
[0:20] [Dashboard: Processing at 25 reports/minute]
[0:30] [Alert: "Serious AE detected - Death reported - Case #AE-2024-0742"]
[0:40] [CMVK verifies: 3/3 models agree on seriousness classification]
[0:50] "50 reports. 2 minutes. 3 serious AEs found. Zero policy violations."
```

## 🚀 Quick Start (One Command)

```bash
cd examples/pharma-compliance
cp .env.example .env
docker-compose up

# Wait 30 seconds, then open:
# → http://localhost:8083  (Demo UI)
# → http://localhost:3003  (Grafana Dashboard - admin/admin)
# → http://localhost:16689 (Jaeger Traces)
```

## 📊 Live Dashboard

```
┌─────────────────────────────────────────┐
│ Pharma Compliance - AE Processing       │
├─────────────────────────────────────────┤
│ Reports Processed:       47             │
│ Serious AEs Found:       3              │
│ CMVK Confidence:         96.8%          │
│ Processing Time:         2.4s (avg)     │
│ Escalations:             3              │
│ Policy Violations:       0              │
└─────────────────────────────────────────┘
```

## Overview

FDA drug applications are 100,000+ pages. One contradiction between lab reports can delay approval 6-12 months. Manual review takes weeks and misses subtle conflicts.

This demo shows how Agent OS uses Context as a Service (CAAS) and Agent VFS to perform deep document cross-referencing.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DOCUMENT CORPUS                                  │
│          50 Lab Reports + 1 IND Draft (100K+ pages)                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ Indexed in Agent VFS
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENT VFS                                        │
│  /agent/compliance/mem/documents/                                    │
│  ├── lab_reports/                                                    │
│  │   ├── report_001.json                                            │
│  │   └── ...                                                         │
│  └── drafts/                                                         │
│      └── ind_filing.json                                             │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
┌──────────────────────┐    ┌──────────────────────┐
│    WRITER AGENT      │    │  COMPLIANCE AGENT    │
│    Drafts clinical   │    │  (Adversarial)       │
│    summary           │    │  Scans for conflicts │
└──────────────────────┘    └──────────────────────┘
            │                             │
            └──────────────┬──────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTRADICTION REPORT                             │
│  - "Draft claims 95% efficacy, Lab Report #23 showed 89%"           │
│  - Citation: Page 42, Paragraph 3                                    │
│  - Recommendation: Update or explain variance                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent Types

### 1. Writer Agent
- Drafts clinical summaries
- Synthesizes data from multiple lab reports
- Must cite sources for every claim

### 2. Compliance Agent (Adversarial)
- Scans all documents for conflicts
- Cross-references claims against source data
- Flags contradictions with citations

## Key Features

### Context as a Service (CAAS)
- 200K+ token context window (Claude 3.5)
- Entire document corpus available for analysis
- No information loss from chunking

### Agent VFS
- Documents stored in virtual file system
- Standard mount points: `/mem/documents/`, `/state/`
- Backend-agnostic (can use vector store)

### Citation Linking
- Every claim traced to source document
- Page number + paragraph reference
- Explainable contradictions

### Policy Enforcement
- "No hallucination" policy at kernel level
- Self-Correcting Agent Kernel (SCAK) catches invented data
- Must cite source for every claim

## Quick Start

```bash
# Run the demo
docker-compose up

# Or run locally
pip install -e .
python demo.py

# Run with custom documents
python demo.py --reports ./my_reports/ --draft ./my_draft.pdf

# Run contradiction analysis only
python demo.py --mode contradiction_only
```

## Demo Scenarios

### Scenario 1: Efficacy Contradiction
Draft claims 95% efficacy, but Lab Report #23 shows 89%.

### Scenario 2: Dosage Discrepancy
Draft recommends 10mg dose, Lab Report #7 tested up to 8mg only.

### Scenario 3: Statistical Error
Draft reports p<0.001, Lab Report #15 shows p=0.03.

### Scenario 4: Timeline Inconsistency
Draft claims 12-month follow-up, Lab Report #42 covers only 9 months.

## Sample Output

```
CONTRADICTION REPORT
====================

Found 12 contradictions in 8 minutes:

1. EFFICACY MISMATCH (HIGH SEVERITY)
   - Draft: "Primary endpoint showed 95% response rate"
   - Lab Report #23, Page 42: "Response rate: 89% (95% CI: 85-93%)"
   - Recommendation: Update draft to match lab data

2. DOSAGE DISCREPANCY (MEDIUM SEVERITY)
   - Draft: "Recommended dose: 10mg daily"
   - Lab Report #7, Page 15: "Maximum tested dose: 8mg"
   - Recommendation: Add justification or adjust dose

3. STATISTICAL ERROR (HIGH SEVERITY)
   - Draft: "Statistical significance (p<0.001)"
   - Lab Report #15, Page 28: "p = 0.03"
   - Recommendation: Correct p-value in draft

... (9 more)
```

## Metrics

| Metric | Human Review | Agent OS |
|--------|-------------|----------|
| Time to Review | 2 weeks | 8 minutes |
| Contradictions Found | 3 | 12 |
| False Positives | N/A | 1 |
| Citations Provided | Partial | 100% |

## License

MIT
