---
layout: default
title: Roadmap
nav_order: 8
description: "Agent OS public roadmap - upcoming features, current limitations, and development timeline."
permalink: /roadmap/
---

# Roadmap
{: .fs-9 }

We build in the open. Here's where Agent OS is heading.
{: .fs-6 .fw-300 }

---

## Current Version: 1.1.0

Released January 2026. [View changelog →](https://github.com/imran-siddique/agent-os/releases)

### What's Working Well

| Feature | Status | Notes |
|:--------|:-------|:------|
| **Core Kernel** | ✅ Stable | Policy enforcement, signals, memory VFS |
| **Python SDK** | ✅ Stable | Full API, type hints, async support |
| **CMVK** | ✅ Stable | Cross-model verification with 3+ models |
| **EMK** | ✅ Stable | Episodic memory, time-travel debugging |
| **IATP** | ✅ Stable | Inter-agent trust, cryptographic signing |
| **Observability** | ✅ Stable | Prometheus, OpenTelemetry, Grafana |
| **LangChain Integration** | ✅ Stable | Wrap any chain or agent |
| **CrewAI Integration** | ✅ Stable | Full crew governance |

---

## 2026 Roadmap

### Q1 2026 (Jan-Mar)

| Feature | Status | Description |
|:--------|:-------|:------------|
| TypeScript SDK | 🔄 In Progress | Native TS/JS SDK for Node.js and Deno |
| Go SDK | 📋 Planned | High-performance SDK for Go applications |
| Policy Templates Library | 🔄 In Progress | Pre-built policies for common compliance needs |
| VS Code Extension v2 | 🔄 In Progress | Visual policy editor, inline diagnostics |

### Q2 2026 (Apr-Jun)

| Feature | Status | Description |
|:--------|:-------|:------------|
| Visual Policy Editor | 📋 Planned | Drag-and-drop policy creation UI |
| Large Swarm Support | 📋 Planned | Optimized for 1000+ concurrent agents |
| Distributed Kernel | 📋 Planned | Multi-node kernel for horizontal scaling |
| AutoGen v2 Integration | 📋 Planned | Deep integration with Microsoft AutoGen |

### Q3 2026 (Jul-Sep)

| Feature | Status | Description |
|:--------|:-------|:------------|
| Declarative Policy Language | 📋 Planned | Rego-like DSL for complex policies |
| Enterprise SSO | 📋 Planned | SAML, OIDC, Active Directory integration |
| RBAC | 📋 Planned | Role-based access control for teams |
| Compliance Dashboards | 📋 Planned | SOC2, HIPAA, GDPR reporting templates |

### Q4 2026 (Oct-Dec)

| Feature | Status | Description |
|:--------|:-------|:------------|
| Agent Marketplace | 📋 Planned | Share and discover governed agent templates |
| Federated Kernels | 📋 Planned | Cross-organization agent governance |
| Hardware Attestation | 📋 Planned | TEE support for sensitive workloads |
| Cloud-Native Deployment | 📋 Planned | Kubernetes operator, Helm charts |

---

## Current Limitations

We believe in transparency. Here's what Agent OS **cannot** do yet:

<div class="limitations-box" markdown="1">

### Language Support
- **Python only** — TypeScript and Go SDKs are in development
- Python 3.9+ required — no legacy Python support planned

### Scale
- **Tested up to ~100 concurrent agents** — larger swarms need optimization
- Single-node kernel — distributed mode coming Q2 2026

### Policies
- YAML-based only — declarative DSL coming Q3 2026
- No visual editor yet — command-line and code only

### Enterprise
- No SSO/RBAC yet — coming Q3 2026
- Self-hosted only — no managed cloud offering yet

</div>

---

## How We Prioritize

We prioritize based on:

1. **Community requests** — [GitHub Discussions](https://github.com/imran-siddique/agent-os/discussions) votes
2. **Production needs** — What paying users need
3. **Safety impact** — Features that prevent incidents get priority
4. **Technical feasibility** — Dependencies and complexity

---

## Request a Feature

Have something you need? Let us know:

[Request Feature →](https://github.com/imran-siddique/agent-os/discussions/new?category=ideas){: .btn .btn-primary }
[View All Requests →](https://github.com/imran-siddique/agent-os/discussions/categories/ideas){: .btn }

---

## Contributing

Want to help build these features? We welcome contributions:

- [Good first issues](https://github.com/imran-siddique/agent-os/labels/good%20first%20issue)
- [Help wanted](https://github.com/imran-siddique/agent-os/labels/help%20wanted)
- [Contributing guide](https://github.com/imran-siddique/agent-os/blob/main/CONTRIBUTING.md)

---

<div class="cta-small" markdown="1">

**Stay updated:** [⭐ Star on GitHub](https://github.com/imran-siddique/agent-os) to follow our progress.

</div>
