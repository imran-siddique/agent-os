# Figure: Dual-Loop OODA Architecture
# Filename: ooda_architecture.png / ooda_architecture.pdf

## Description
High-level view of SCAK's dual-loop architecture based on Boyd's OODA loop.

## ASCII Reference (for vector conversion)

```
                           ┌─────────────────────────────────────────────────────────────┐
                           │                     USER QUERY                              │
                           └──────────────────────────┬──────────────────────────────────┘
                                                      │
                                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               LOOP 1: RUNTIME (OBSERVE → ACT)                            │
│  ┌────────────────┐        ┌────────────────┐        ┌────────────────┐                 │
│  │    TRIAGE      │  ──▶   │    EXECUTE     │  ──▶   │    RESPOND     │  ──▶ User      │
│  │    ENGINE      │        │    AGENT       │        │                │                 │
│  │ ┌────────────┐ │        │ ┌────────────┐ │        │ ┌────────────┐ │                 │
│  │ │ Sync/Async │ │        │ │   GPT-4o   │ │        │ │   Return   │ │                 │
│  │ │  Decision  │ │        │ │ + Tools    │ │        │ │  Response  │ │                 │
│  │ └────────────┘ │        │ └────────────┘ │        │ └────────────┘ │                 │
│  └────────────────┘        └───────┬────────┘        └────────────────┘                 │
│           │                        │                                                     │
│           │                        │ give-up signal?                                     │
│           │                        ▼                                                     │
│           │               ┌────────────────┐                                            │
│           │               │  GIVE-UP       │                                            │
│           │               │  DETECTOR      │                                            │
│           │               │ "couldn't find"│                                            │
│           │               │ "access denied"│                                            │
│           │               └───────┬────────┘                                            │
│           │                       │ YES (5-10%)                                          │
└───────────┼───────────────────────┼─────────────────────────────────────────────────────┘
            │                       │ (async)
            │                       ▼
┌───────────┼───────────────────────────────────────────────────────────────────────────────┐
│           │              LOOP 2: ALIGNMENT (ORIENT → DECIDE)                              │
│           │                                                                               │
│  ┌────────┴───────┐        ┌────────────────┐        ┌────────────────┐                  │
│  │  COMPLETENESS  │  ──▶   │    SHADOW      │  ──▶   │    MEMORY      │                  │
│  │    AUDITOR     │        │    TEACHER     │        │   CONTROLLER   │                  │
│  │ ┌────────────┐ │        │ ┌────────────┐ │        │ ┌────────────┐ │                  │
│  │ │ Diff Audit │ │        │ │ o1-preview │ │        │ │   Tiered   │ │                  │
│  │ │   Check    │ │        │ │  Diagnosis │ │        │ │   Storage  │ │                  │
│  │ └────────────┘ │        │ └────────────┘ │        │ └────────────┘ │                  │
│  └────────────────┘        └───────┬────────┘        └───────┬────────┘                  │
│                                    │                         │                            │
│                                    ▼                         ▼                            │
│                           ┌────────────────┐        ┌────────────────┐                   │
│                           │   GAP ANALYSIS │        │   APPLY PATCH  │                   │
│                           │  "Agent missed │  ──▶   │  to Tier 1/2/3 │                   │
│                           │   retry logic" │        │     Memory     │                   │
│                           └────────────────┘        └────────────────┘                   │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

## Color Scheme (for final rendering)
- Loop 1 (Runtime): Light blue background (#E3F2FD)
- Loop 2 (Alignment): Light green background (#E8F5E9)
- Triage Engine: Orange (#FF9800)
- Shadow Teacher: Purple (#9C27B0)
- Memory Controller: Teal (#009688)
- Arrows: Dark gray (#424242)

## Tools for Conversion
- Mermaid.js → SVG → PDF
- draw.io / diagrams.net
- Excalidraw (hand-drawn style)
- TikZ (LaTeX native)

## Caption
**Figure 1: SCAK Dual-Loop Architecture.** Loop 1 (Runtime) handles user queries with minimal latency. Loop 2 (Alignment) triggers asynchronously on give-up signals, using differential auditing to detect laziness and generate competence patches.
