# Figure: Three-Tier Memory Hierarchy
# Filename: memory_hierarchy.png / memory_hierarchy.pdf

## Description
Visualization of SCAK's tiered storage with Type A/B decay lifecycle.

## ASCII Reference (for vector conversion)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         THREE-TIER MEMORY HIERARCHY                             │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────┐
                              │   TIER 1: KERNEL    │
                              │   (System Prompt)   │
                              │  ┌───────────────┐  │
                              │  │ 500 tokens    │  │
                              │  │ ALWAYS active │  │
                              │  │ Safety rules  │  │
                              │  │ Core identity │  │
                              │  └───────────────┘  │
                              └─────────┬───────────┘
                                        │
                         HOT ◄──────────┼──────────► COLD
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
          ▼                             ▼                             ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   TIER 2: CACHE     │    │     PROMOTION       │    │   TIER 3: ARCHIVE   │
│      (Redis)        │ ◄──│    /DEMOTION        │──► │    (Vector DB)      │
│  ┌───────────────┐  │    │  ┌───────────────┐  │    │  ┌───────────────┐  │
│  │ 10K entries   │  │    │  │ >10 hits/week │  │    │  │ Unlimited     │  │
│  │ Conditional   │  │    │  │   → promote   │  │    │  │ On-demand RAG │  │
│  │ Tool-specific │  │    │  │ <1 hit/month  │  │    │  │ Long-tail     │  │
│  │ Skill lessons │  │    │  │   → demote    │  │    │  │ wisdom        │  │
│  └───────────────┘  │    │  └───────────────┘  │    │  └───────────────┘  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘

                    ┌─────────────────────────────────────────┐
                    │           TYPE A/B LIFECYCLE            │
                    └─────────────────────────────────────────┘

    ┌───────────────────────────────┐    ┌───────────────────────────────┐
    │         TYPE A PATCHES        │    │         TYPE B PATCHES        │
    │    (Syntax / Capability)      │    │    (Business / Context)       │
    │  ┌─────────────────────────┐  │    │  ┌─────────────────────────┐  │
    │  │ • "Output valid JSON"  │  │    │  │ • "Fiscal year: July 1" │  │
    │  │ • "Use ISO 8601 dates" │  │    │  │ • "Project_Alpha: dead" │  │
    │  │ • "Limit to 10 results"│  │    │  │ • "VIP users: priority" │  │
    │  └─────────────────────────┘  │    │  └─────────────────────────┘  │
    │                               │    │                               │
    │   ┌───────────────────────┐   │    │   ┌───────────────────────┐   │
    │   │    HIGH DECAY         │   │    │   │    ZERO DECAY         │   │
    │   │ Delete on model       │   │    │   │ Retain indefinitely   │   │
    │   │ upgrade (GPT-4→5)     │   │    │   │ Business truth        │   │
    │   │ ~50 patches purged    │   │    │   │ ~10 patches kept      │   │
    │   └───────────────────────┘   │    │   └───────────────────────┘   │
    └───────────────────────────────┘    └───────────────────────────────┘

                              │
                              ▼
                    ┌─────────────────────┐
                    │   SEMANTIC PURGE    │
                    │   (Model Upgrade)   │
                    │  ┌───────────────┐  │
                    │  │ 45% reduction │  │
                    │  │ 100% business │  │
                    │  │ rule retained │  │
                    │  └───────────────┘  │
                    └─────────────────────┘
```

## Color Scheme (for final rendering)
- Tier 1: Red/Orange (#FFCDD2) - Critical, always active
- Tier 2: Yellow (#FFF9C4) - Fast, conditional
- Tier 3: Blue (#BBDEFB) - Deep, archival
- Type A: Gray (#ECEFF1) - Temporary
- Type B: Green (#C8E6C9) - Permanent

## Caption
**Figure 2: Three-Tier Memory Hierarchy with Type A/B Lifecycle.** Tier 1 (Kernel) holds safety-critical rules always in context. Tier 2 (Cache) stores frequently-accessed skill lessons. Tier 3 (Archive) persists all patches for RAG retrieval. Type A patches (syntax fixes) are purged on model upgrades; Type B patches (business knowledge) are retained indefinitely.
