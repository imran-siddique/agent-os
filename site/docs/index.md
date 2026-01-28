---
layout: default
title: Documentation
nav_order: 2
has_children: true
permalink: /docs/
description: "Complete documentation for Agent OS - the kernel architecture for AI agent governance."
---

# Agent OS Documentation

Welcome to the Agent OS documentation. Here you'll find everything you need to build, deploy, and govern AI agents with kernel-level safety.

---

## Quick Links

<div class="quick-links" markdown="1">

| Getting Started | Core Concepts | Advanced |
|:----------------|:--------------|:---------|
| [5-Minute Quickstart](/docs/tutorials/quickstart/) | [Kernel Architecture](/docs/concepts/kernel/) | [Custom Policies](/docs/tutorials/custom-policies/) |
| [Installation Guide](/docs/tutorials/installation/) | [Policy Engine](/docs/concepts/policies/) | [Multi-Agent Systems](/docs/tutorials/multi-agent/) |
| [First Governed Agent](/docs/tutorials/first-agent/) | [Signals (POSIX)](/docs/concepts/signals/) | [Production Deployment](/docs/tutorials/production/) |

</div>

---

## Documentation Sections

### 📘 [Concepts](/docs/concepts/)
Core concepts and architecture of Agent OS.
- [Kernel Space vs User Space](/docs/concepts/kernel/)
- [Policy Engine](/docs/concepts/policies/)
- [Signals (SIGKILL, SIGSTOP, SIGCONT)](/docs/concepts/signals/)
- [Virtual File System (VFS)](/docs/concepts/vfs/)

### 📗 [Tutorials](/docs/tutorials/)
Step-by-step guides for common tasks.
- [5-Minute Quickstart](/docs/tutorials/quickstart/)
- [30-Minute Deep Dive](/docs/tutorials/deep-dive/)
- [Building Your First Agent](/docs/tutorials/first-agent/)
- [Framework Integrations](/docs/tutorials/integrations/)

### 📙 [Modules](/docs/modules/)
Documentation for Agent OS modules.
- [CMVK - Cross-Model Verification](/docs/modules/cmvk/)
- [EMK - Episodic Memory Kernel](/docs/modules/emk/)
- [IATP - Inter-Agent Trust Protocol](/docs/modules/iatp/)
- [AMB - Agent Message Bus](/docs/modules/amb/)

### 📕 [API Reference](/docs/api/)
Complete API documentation.
- [KernelSpace](/docs/api/kernel-space/)
- [Policy](/docs/api/policy/)
- [SignalDispatcher](/docs/api/signal-dispatcher/)
- [AgentVFS](/docs/api/agent-vfs/)

### 🔌 [Integrations](/docs/integrations/)
Framework and tool integrations.
- [LangChain](/docs/integrations/langchain/)
- [CrewAI](/docs/integrations/crewai/)
- [OpenAI Assistants](/docs/integrations/openai/)
- [Semantic Kernel](/docs/integrations/semantic-kernel/)

### 🧩 [Extensions](/docs/extensions/)
IDE and CLI extensions.
- [VS Code Extension](/docs/extensions/vscode/)
- [JetBrains Plugin](/docs/extensions/jetbrains/)
- [Cursor Integration](/docs/extensions/cursor/)
- [Chrome DevTools](/docs/extensions/chrome/)

---

## Learning Paths

Choose your path based on your goals:

### 🚀 I want to get started quickly
1. [5-Minute Quickstart](/docs/tutorials/quickstart/)
2. [First Governed Agent](/docs/tutorials/first-agent/)

### 🏗️ I want to understand the architecture
1. [Kernel Architecture](/docs/concepts/kernel/)
2. [Policy Engine](/docs/concepts/policies/)
3. [30-Minute Deep Dive](/docs/tutorials/deep-dive/)

### 🔧 I want to integrate with my existing framework
1. [Framework Integrations Overview](/docs/integrations/)
2. Choose your framework guide

### 🏢 I want to deploy to production
1. [Production Deployment](/docs/tutorials/production/)
2. [Observability Setup](/docs/tutorials/observability/)
3. [Security Best Practices](/docs/tutorials/security/)

---

## Interactive Notebooks

Learn by doing with our Jupyter notebooks:

| Notebook | Time | Description |
|:---------|:-----|:------------|
| [Hello Agent OS](/notebooks/01-hello-agent-os/) | 5 min | Your first governed agent |
| [Episodic Memory](/notebooks/02-episodic-memory/) | 15 min | Persistent agent memory |
| [Time-Travel Debugging](/notebooks/03-time-travel/) | 20 min | Replay agent decisions |
| [Cross-Model Verification](/notebooks/04-cmvk/) | 15 min | Detect hallucinations |
| [Multi-Agent Coordination](/notebooks/05-multi-agent/) | 20 min | Agent trust protocols |
| [Policy Engine](/notebooks/06-policies/) | 15 min | Deep dive into policies |

---

## Need Help?

- **Community**: [GitHub Discussions](https://github.com/imran-siddique/agent-os/discussions)
- **Bugs**: [GitHub Issues](https://github.com/imran-siddique/agent-os/issues)
- **FAQ**: [Frequently Asked Questions](/faq/)
