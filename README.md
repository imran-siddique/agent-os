# SDLC Agents

> AI agents designed to automate and enhance the Software Development Lifecycle for AX&E Engineering.

---

## 📊 Status Summary

| Status | Icon | Count | Description |
|--------|------|-------|-------------|
| Experimental | 🧪 | 4 | Early exploration, expect breaking changes |
| Beta | 🟡 | 5 | Functional but still being refined |
| Stable | 🟢 | 1 | Production-ready |
| On Hold | ⛔ | 1 | Paused due to constraints |
| **Total** | | **11** | |

---

## 🗂️ Quick Reference

| Agent | Category | Maturity | Role | Key Status |
|-------|----------|----------|------|------------|
| [Planning Agent](agents/planning-agent.md) | orchestrator | 🟡 beta | coordinator | Localization ✅, Learn 🔄 |
| [Onboarding Agent](agents/onboarding-agent.md) | capture | 🧪 experimental | worker | Just kicking off |
| [Design Review Agent](agents/design-review-agent.md) | hybrid | 🟡 beta | standalone | Merging 2 prototypes |
| [Accessibility Agent](agents/accessibility-agent.md) | hybrid | 🟡 beta | worker | PR integration planned |
| [Productivity Agent](agents/productivity-agent.md) | analyst | 🧪 experimental | worker | Partnership approach |
| [Unit & Scenario Testing](agents/unit-and-scenario-testing-agent.md) | analyst | 🟡 beta | worker | ⭐ Sponsored, org-wide rollout |
| [S360 Agent](agents/s360-agent.md) | hybrid | 🟡 beta | coordinator | 3 workstreams, heavily adopted |
| [Release Freshness Agent](agents/release-freshness-agent.md) | analyst | 🧪 experimental | worker | Dashboard ✅, agent 🔜 |
| [Zero Production Touch](agents/zero-production-touch.md) | orchestrator | ⛔ on hold | coordinator | No sponsorship |
| [SRE Agent](agents/sre-agent.md) | orchestrator | 🧪 experimental | coordinator | Sev3 self-service goal |
| [DRI Report Agent](agents/dri-report-agent.md) | analyst | 🟢 stable | worker | ⭐ Org-wide, saving hours |

---

## 📋 Agents by SDLC Phase

### Planning & Requirements

| Agent | Status | Description |
|-------|--------|-------------|
| [Planning Agent](agents/planning-agent.md) | 🟡 beta | Engineering productivity: ADO hygiene, Power Operating Model compliance |
| [Onboarding Agent](agents/onboarding-agent.md) | 🧪 experimental | Generate blessed artifacts (C4, dataflow) for repos |

### Design & Architecture

| Agent | Status | Description |
|-------|--------|-------------|
| [Design Review Agent](agents/design-review-agent.md) | 🟡 beta | Early feedback on design; merging structure + architecture prototypes |

### Development & Coding

| Agent | Status | Description |
|-------|--------|-------------|
| [Accessibility Agent](agents/accessibility-agent.md) | 🟡 beta | A11y checks at PR time; fix suggestions |
| [Productivity Agent](agents/productivity-agent.md) | 🧪 experimental | IDE monitoring for before/after AI productivity measurement |

### Testing & Quality

| Agent | Status | Description |
|-------|--------|-------------|
| [Unit & Scenario Testing](agents/unit-and-scenario-testing-agent.md) | 🟡 beta | ⭐ **Sponsored** — AI-assisted test generation, org-wide rollout |
| [S360 Agent](agents/s360-agent.md) | 🟡 beta | S360 explainer + WIT creator + auto-fix generator |

### Deployment & Operations

| Agent | Status | Description |
|-------|--------|-------------|
| [Release Freshness Agent](agents/release-freshness-agent.md) | 🧪 experimental | Dashboard live; agent automation planned |
| [Zero Production Touch](agents/zero-production-touch.md) | ⛔ on hold | Dashboard working; AI automation needs sponsorship |

### Monitoring & Maintenance

| Agent | Status | Description |
|-------|--------|-------------|
| [SRE Agent](agents/sre-agent.md) | 🧪 experimental | Sev3 self-service goal; evaluating tools |

### Reporting

| Agent | Status | Description |
|-------|--------|-------------|
| [DRI Report Agent](agents/dri-report-agent.md) | 🟢 stable | ⭐ Automated DRI reports; saving hours across AX&E |

---

## 🔗 Agent Relationships

```
                                    ┌─────────────────────┐
                                    │   Planning Agent    │
                                    │   (coordinator)     │
                                    └──────────┬──────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
         ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
         │ Design Review    │       │ DRI Report Agent │       │ Onboarding Agent │
         │ Agent            │       │                  │       │                  │
         └────────┬─────────┘       └────────┬─────────┘       └──────────────────┘
                  │                          │
                  ▼                          ▼
         ┌──────────────────┐       ┌──────────────────┐
         │ Unit & Scenario  │       │    S360 Agent    │◀─────────────────┐
         │ Testing Agent    │       │   (coordinator)  │                  │
         └──────────────────┘       └────────┬─────────┘                  │
                                             │                            │
                                             ▼                            │
                                    ┌──────────────────┐       ┌──────────────────┐
                                    │ Accessibility    │       │ Release Freshness│
                                    │ Agent            │       │ Agent            │
                                    └──────────────────┘       └────────┬─────────┘
                                                                        │
                                                                        ▼
                                                               ┌──────────────────┐
                                                               │    SRE Agent     │
                                                               │   (coordinator)  │
                                                               └──────────────────┘
```

---

## 🧭 Strategic Considerations

> Areas we're still brainstorming and need to think through.

### 🔴 Open Questions (To-Do)

| Area | Questions to Answer | Status |
|------|---------------------|--------|
| **Culture & Adoption** | How do we drive adoption? What behavior changes are needed? | 🤔 Not started |
| **Success Measurement** | How do we measure overall SDLC agent success? What KPIs? | 🤔 Not started |
| **Build vs Buy vs Leverage** | Build custom? Use Microsoft tools only? Allow OSS? | 🤔 Not started |
| **Agent Framework** | Which framework for multi-agent scenarios? AutoGen? Semantic Kernel? | 🤔 Not started |
| **Microsoft vs OSS** | Microsoft-only stack or open to OSS solutions? | 🤔 Not started |
| **Multi-Agent Orchestration** | How do agents communicate and hand off work? | 🤔 Not started |
| **Governance Model** | Who approves new agents? Who maintains them? | 🤔 Not started |
| **Security & Compliance** | What guardrails are needed for production use? | 🤔 Not started |

### 📝 Notes

These are early-stage brainstorming items. We haven't thought through these aspects yet but they're critical for scaling the SDLC agent initiative.

#### Culture Changes Needed
- *To be defined*

#### Success Metrics (Overall Initiative)
- *To be defined*

#### Technology Decisions
- *To be defined*

---

## 📋 Agent Specification

All agents follow the [Agent Specification v1.0](agent-specification.md), which defines:

| Section | What It Covers |
|---------|----------------|
| **1. Metadata** | Name, version, category, maturity |
| **2. Capabilities** | Tools, integrations, orchestration role |
| **3. Risk Assessment** | Autonomy, blast radius, failure modes |
| **4. Workflow Integration** | Triggers, inputs, outputs, agent relationships |
| **5. Evaluation & Adoption** | Success metrics, prerequisites |
| **6. Governance** | Ownership, changelog, deprecation |

### Agent Categories

| Category | Description |
|----------|-------------|
| **capture** | Gather and structure information |
| **coach** | Guide and teach users |
| **analyst** | Research, analyze, and report |
| **orchestrator** | Coordinate workflows and other agents |
| **hybrid** | Combine multiple capabilities |

### Maturity Levels

| Level | Icon | Description |
|-------|------|-------------|
| `experimental` | 🧪 | Early exploration, expect breaking changes |
| `beta` | 🟡 | Functional but still being refined |
| `stable` | 🟢 | Production-ready |
| `deprecated` / `on hold` | ⛔ | No longer actively maintained or paused |

---

## 📁 Repository Structure

```
sdlc_agents/
├── README.md                    # This file
├── agent-specification.md       # Formal taxonomy for agent specs (v1.0)
└── agents/
    ├── accessibility-agent.md
    ├── design-review-agent.md
    ├── dri-report-agent.md
    ├── onboarding-agent.md
    ├── planning-agent.md
    ├── productivity-agent.md
    ├── release-freshness-agent.md
    ├── s360-agent.md
    ├── sre-agent.md
    ├── unit-and-scenario-testing-agent.md
    └── zero-production-touch.md
```

---

## 🤝 Contributing

### Adding a New Agent

1. **Create file** in `agents/` directory
2. **Follow the spec** — Use [Agent Specification v1.0](agent-specification.md) format
3. **Use the template**:

```markdown
---
name: Agent Name
version: 0.1.0
description: One-line description
category: analyst | capture | coach | orchestrator | hybrid
maturity: experimental | beta | stable | deprecated
owner: AX&E Engineering
last-validated: YYYY-MM-DD
---

# Agent Name

> One-line description

## 🎯 Vision
(What problem does this solve?)

## Related Agents
(Links to related agents)

## Capabilities
(Tools, integrations)

## Risk Assessment
(Autonomy, blast radius, checkpoints)

## Workflow Integration
(Triggers, inputs, outputs, flow diagram)

## Evaluation & Adoption
(Metrics, status, prerequisites)

## Governance
(Owner, changelog)
```

4. **Start with `experimental`** maturity
5. **Update this README** — Add to the quick reference and appropriate SDLC phase section

### Updating an Agent

1. Update the agent file
2. Bump the version number
3. Add entry to changelog
4. Update `last-validated` date

---

## 📚 Resources

- [Agent Specification v1.0](agent-specification.md) — Formal taxonomy for agent definitions
- [Octane Onboarding Guide](docs/octane-onboarding.md) — How to deploy agents to the Octane platform
- [Contributing Guidelines](docs/CONTRIBUTING.md) — How to add or update agents

---

*Last updated: 2026-01-21 · Owner: AX&E Engineering*
