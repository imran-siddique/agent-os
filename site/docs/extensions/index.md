---
layout: default
title: Extensions
parent: Documentation
nav_order: 9
permalink: /docs/extensions/
description: "Agent OS IDE and browser extensions - VS Code, Cursor, JetBrains, Chrome DevTools."
---

# IDE & Browser Extensions
{: .fs-9 }

Use Agent OS directly in your development environment.
{: .fs-6 .fw-300 }

---

## Available Extensions

| Extension | Platform | Status | Features |
|:----------|:---------|:-------|:---------|
| **VS Code** | VS Code Marketplace | ✅ Available | Policy preview, kernel debugger, memory browser |
| **Cursor** | Cursor IDE | ✅ Available | Composer interception, safe alternatives |
| **JetBrains** | JetBrains Marketplace | ✅ Available | IntelliJ, PyCharm, WebStorm support |
| **Chrome DevTools** | Chrome Web Store | ✅ Available | AMB message monitor, IATP trust inspector |

---

## VS Code Extension

Real-time policy checks and kernel visualization.

### Installation

```bash
# From VS Code Marketplace
ext install agent-os.agent-os-vscode

# Or from source
cd extensions/vscode
npm install && npm run build
code --install-extension agent-os-vscode-*.vsix
```

### Features

- **Policy Preview** — See policy decisions before running
- **Kernel Debugger** — Visualize agent state, checkpoints, signals
- **Memory Browser** — Explore VFS paths and episodic memory
- **Auto-completion** — IntelliSense for policy YAML files

---

## Cursor Integration

Enhanced safety for AI-assisted coding.

### Installation

The Cursor wrapper is built into Agent OS:

```python
from agent_os.integrations.cursor import CursorKernel

kernel = CursorKernel(policy="strict")
# Automatically intercepts Composer suggestions
```

### Features

- **Composer Interception** — Check AI suggestions against policies
- **Safe Alternatives** — Suggest compliant alternatives when blocked
- **Auto-hibernation** — Pause kernel during inactive sessions

---

## JetBrains Plugins

Support for IntelliJ IDEA, PyCharm, WebStorm, and more.

### Installation

1. Open Settings → Plugins → Marketplace
2. Search "Agent OS"
3. Install and restart

### Features

- **Policy inspection** — View policy decisions in gutter
- **Run configurations** — Execute with governance
- **Tool window** — Monitor kernel state

---

## Chrome DevTools Extension

Monitor agent communication in web applications.

### Installation

```bash
# Build from source
cd extensions/chrome
npm install && npm run build
# Load unpacked extension in Chrome
```

### Features

- **AMB Monitor** — See all agent messages in real-time
- **IATP Inspector** — Verify trust chains and signatures
- **Network panel** — Agent-aware request/response logging

---

## Source Code

All extensions are open source:

- [VS Code Extension](https://github.com/imran-siddique/agent-os/tree/main/extensions/vscode)
- [Cursor Integration](https://github.com/imran-siddique/agent-os/tree/main/extensions/cursor)
- [JetBrains Plugins](https://github.com/imran-siddique/agent-os/tree/main/extensions/jetbrains)
- [Chrome DevTools](https://github.com/imran-siddique/agent-os/tree/main/extensions/chrome)

---

## Next Steps

- [VS Code Quickstart](/docs/tutorials/quickstart/) — Get started with the extension
- [Policy Reference](/docs/policies/) — Learn what policies you can check
- [Observability](/docs/observability/) — Monitor beyond the IDE
