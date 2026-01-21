# Octane Onboarding Guide

> How to integrate SDLC Agents with Octane's AI development framework once agents reach production-ready status.

---

## 📋 Overview

[Octane](https://github.com/azure-core/octane) is Azure Core's **AI development framework** that provides curated prompts, MCP servers, and templates in a one-click VS Code installation. It focuses on **scenarios, not tools**—covering the entire software lifecycle from planning through deployment.

This guide explains how our SDLC agents can leverage Octane's infrastructure and potentially contribute scenarios back to the framework.

### Why Integrate with Octane?

| Benefit | Description |
|---------|-------------|
| **Microsoft-Vetted** | Battle-tested prompts, agents, and MCP servers |
| **One-Click Deploy** | VS Code extension with embedded artifacts |
| **End-to-End Coverage** | AI integration across planning, coding, testing, deployment |
| **MCP Server Ecosystem** | Pre-built integrations (ADO, EV2, Engineering Copilot) |
| **Shared Infrastructure** | Reuse prompts, templates, and instructions |

### Octane vs SDLC Agents

| Aspect | Octane | Our SDLC Agents |
|--------|--------|-----------------|
| **Focus** | Developer workflows in VS Code | Automated backend processes |
| **Interaction** | Chat-based prompts (`/Octane.Planner.Requirements`) | Scheduled jobs, triggers, APIs |
| **Scope** | Individual developer productivity | Team/org-wide automation |
| **Delivery** | VS Code extension + CLI | Various (dashboards, bots, services) |

**Synergy**: Our agents can provide the *backend automation* while Octane provides the *developer experience*.

---

## 🔗 Scenario Alignment

Map our SDLC agents to Octane's existing scenarios:

### Direct Alignment

| Octane Scenario | Our Agent | Integration Opportunity |
|-----------------|-----------|------------------------|
| **Spec Driven Development** | [Planning Agent](../agents/planning-agent.md) | Feed ADO work items into SDD workflow |
| **Test Analysis** | [Unit & Scenario Testing](../agents/unit-and-scenario-testing-agent.md) | Automated test generation as Octane scenario |
| **EV2 Management** | [Release Freshness Agent](../agents/release-freshness-agent.md) | Deployment freshness monitoring |
| **Repository Overview** | [Onboarding Agent](../agents/onboarding-agent.md) | Generate blessed artifacts (C4, dataflow) |

### New Scenario Candidates

| Our Agent | Proposed Octane Scenario | Description |
|-----------|-------------------------|-------------|
| [DRI Report Agent](../agents/dri-report-agent.md) | `/Octane.Reporter.DRIStatus` | Generate DRI reports from chat |
| [S360 Agent](../agents/s360-agent.md) | `/Octane.Compliance.S360Explain` | Explain S360/SFI requirements |
| [Design Review Agent](../agents/design-review-agent.md) | `/Octane.Reviewer.DesignCheck` | Pre-PR design validation |
| [Accessibility Agent](../agents/accessibility-agent.md) | `/Octane.Tester.A11yAnalysis` | Accessibility issue analysis |
| [SRE Agent](../agents/sre-agent.md) | `/Octane.Deployer.IncidentAssist` | Live site incident assistance |

---

## 🚀 Integration Paths

### Path 1: Leverage Octane MCP Servers

Use Octane's pre-built MCP servers in our agents:

```yaml
# Available MCP Servers from Octane
mcp_servers:
  - name: Engineering Copilot
    url: https://mcp.engcopilot.net/
    use_case: Semantic codebase exploration
    
  - name: Azure DevOps MCP
    url: https://github.com/microsoft/azure-devops-mcp
    use_case: Work items, pipelines, PRs
    
  - name: EV2 MCP
    url: https://msazure.visualstudio.com/One/_git/Deployment-Ease
    use_case: Deployment platform integration
    
  - name: Microsoft Learn
    url: https://learn.microsoft.com/en-us/training/support/mcp
    use_case: Documentation resources
```

**Example**: Our Planning Agent could use the Azure DevOps MCP instead of building custom ADO integration.

### Path 2: Contribute Prompts to Octane

Package agent capabilities as reusable Octane prompts:

```markdown
<!-- .github/prompts/dri-report.prompt.md -->
---
name: DRI Report Generator
description: Generate a DRI report for the current sprint
tools:
  - power_bi
  - ado_api
---

# DRI Report Generator

Generate a comprehensive DRI report including:
1. Sprint progress and burndown
2. Active incidents and resolution status
3. Key metrics and trends
4. Action items for the upcoming week

## Instructions
- Query Power BI datasets for metrics
- Pull ADO work items for sprint status
- Format according to AX&E DRI template
```

### Path 3: Build Custom Octane Agent

Create a full Octane agent with instructions and skills:

```
.github/
├── agents/
│   └── axe-agent.md              # Agent definition
├── instructions/
│   └── axe-context.instructions.md  # Agent context
├── prompts/
│   ├── dri-report.prompt.md
│   ├── s360-explain.prompt.md
│   └── design-review.prompt.md
└── templates/
    └── dri-report.template.md
```

**Agent Definition Example:**
```markdown
<!-- .github/agents/axe-agent.md -->
---
name: AXE Engineering Agent
description: AI assistant for AX&E Engineering workflows
tools:
  - power_bi
  - ado_api
  - sharepoint_reader
instructions:
  - axe-context.instructions.md
prompts:
  - dri-report.prompt.md
  - s360-explain.prompt.md
---

# AXE Engineering Agent

Specialized agent for AX&E Engineering team workflows including:
- DRI report generation
- S360/SFI compliance assistance
- Sprint planning and hygiene
- Design review preparation
```

---

## 📦 Onboarding Steps

### Step 1: Install Octane

```bash
# Via VS Code Extension (recommended)
# Search "Octane" in VS Code Extensions marketplace

# Or via CLI
npm install -g @azure-core/octane-cli
octane install
```

### Step 2: Evaluate Existing Scenarios

Before building new integrations, test Octane's existing scenarios:

```shell
# Try these in VS Code with Octane installed:

# Repository overview (similar to our Onboarding Agent)
/Octane.Planner.RepositoryOverview

# Test analysis (similar to our Unit & Scenario Testing Agent)
/Octane.Tester.TestAnalysis UserRepository.cs

# Deployment monitoring (similar to our Release Freshness Agent)
/Octane.Deployer.Monitor
```

### Step 3: Identify Gaps

Document what Octane doesn't cover that our agents provide:

| Gap | Our Agent | Action |
|-----|-----------|--------|
| DRI reporting automation | DRI Report Agent | Propose new scenario |
| S360/SFI workflow | S360 Agent | Propose new scenario |
| Accessibility automation | Accessibility Agent | Extend Tester scenario |
| Proactive SRE monitoring | SRE Agent | Propose new scenario |

### Step 4: Contribute Back

If contributing scenarios to Octane:

1. **Fork** the Octane repo
2. **Create** prompt/agent files following their conventions
3. **Test** locally with the VS Code extension
4. **Submit PR** with documentation

---

## 🔧 Configuration

### Octane Config for AX&E

Create a team-specific Octane configuration:

```yaml
# .config/octane.yaml
team: axe-engineering
scenarios:
  testing:
    focus:
      - reliability
      - accessibility
      - coverage
    custom_rules:
      - require-a11y-tests
      - min-coverage-80
      
  planning:
    ado_project: AX&E
    work_item_types:
      - User Story
      - Bug
      - Task
    
  deployment:
    platform: ev2
    services:
      - service-a
      - service-b
```

### MCP Server Setup

Configure MCP servers for our agents:

```json
// .vscode/mcp.json
{
  "servers": {
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@microsoft/azure-devops-mcp"],
      "env": {
        "ADO_ORG": "msazure",
        "ADO_PROJECT": "AX&E"
      }
    },
    "engineering-copilot": {
      "url": "https://mcp.engcopilot.net/"
    }
  }
}
```

---

## 📊 Integration Status

Track which SDLC agents are integrated with Octane:

| Agent | Maturity | Octane Integration | Status |
|-------|----------|-------------------|--------|
| [DRI Report Agent](../agents/dri-report-agent.md) | 🟢 Stable | Propose `/Octane.Reporter.DRIStatus` | 🔜 Ready to propose |
| [Unit & Scenario Testing](../agents/unit-and-scenario-testing-agent.md) | 🟡 Beta | Extend `/Octane.Tester.*` | 🔜 Evaluate alignment |
| [Planning Agent](../agents/planning-agent.md) | 🟡 Beta | Leverage `/Octane.Planner.*` | 🔜 Use existing |
| [S360 Agent](../agents/s360-agent.md) | 🟡 Beta | Propose `/Octane.Compliance.*` | ⏳ After stabilization |
| [Design Review Agent](../agents/design-review-agent.md) | 🟡 Beta | Propose `/Octane.Reviewer.*` | ⏳ After merge |
| [Accessibility Agent](../agents/accessibility-agent.md) | 🟡 Beta | Extend `/Octane.Tester.A11y*` | ⏳ Pending |
| [Onboarding Agent](../agents/onboarding-agent.md) | 🧪 Experimental | Extend `/Octane.Planner.RepositoryOverview` | ❌ Too early |
| [Productivity Agent](../agents/productivity-agent.md) | 🧪 Experimental | TBD | ❌ Too early |
| [Release Freshness Agent](../agents/release-freshness-agent.md) | 🧪 Experimental | Leverage `/Octane.Deployer.*` | ❌ Too early |
| [SRE Agent](../agents/sre-agent.md) | 🧪 Experimental | Propose `/Octane.Deployer.IncidentAssist` | ❌ Too early |
| [Zero Production Touch](../agents/zero-production-touch.md) | ⏸️ On Hold | N/A | ❌ On hold |

---

## 🎯 Recommended Actions

### Immediate (This Sprint)

1. **Install Octane** extension for the team
2. **Evaluate** existing scenarios against our agent capabilities
3. **Document** gaps and overlaps

### Short-term (Next Quarter)

1. **Propose** DRI Report scenario to Octane team
2. **Integrate** Planning Agent with Octane's ADO MCP server
3. **Extend** Unit Testing Agent to work with Octane's Tester scenario

### Long-term

1. **Contribute** AX&E-specific scenarios back to Octane
2. **Build** unified developer experience combining Octane + our backend agents
3. **Establish** partnership with Octane team for ongoing collaboration

---

## 📚 Resources

### Octane Resources

- **Demo Video**: [3-Minute Demo](https://microsoft-my.sharepoint.com/:v:/p/jasonrobert/IQDDIvwU2aEQSIMdsh6qVFKNAXxuLQhL1PieN8Fye5XJQnY?e=eywYKQ)
- **Getting Started**: [Octane Setup Guide](https://github.com/azure-core/octane/blob/main/docs/getting-started.md)
- **Best Practices**: [AI Development Practices](https://github.com/azure-core/octane/blob/main/docs/best-practices.md)
- **All Scenarios**: [Scenario Documentation](https://github.com/azure-core/octane/blob/main/docs/scenarios.md)

### Our Resources

- [Agent Specification](../agent-specification.md) — Format for agent definitions
- [README](../README.md) — Repository overview and agent status
- [CONTRIBUTING](./CONTRIBUTING.md) — How to add or update agents

---

*Last updated: 2026-01-21 · Owner: AX&E Engineering*
