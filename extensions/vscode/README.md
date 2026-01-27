# Agent OS for VS Code

> **Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents

**Kernel-level safety for AI coding assistants.**

![Agent OS Banner](images/banner.png)

## The Problem

AI coding assistants (GitHub Copilot, Cursor, Claude) generate code without safety guarantees. They can suggest:
- `DROP TABLE users` - deleting production data
- Hardcoded API keys and secrets
- `rm -rf /` - destructive file operations
- Code with SQL injection vulnerabilities

**73% of developers are hesitant to trust AI for critical code.**

## The Solution

Agent OS wraps your AI assistant with a kernel that provides:

- 🛡️ **Real-time policy enforcement** - Block destructive operations before they execute
- 🔍 **Multi-model code review (CMVK)** - Verify code with GPT-4, Claude, and Gemini
- 📋 **Complete audit trail** - Log every AI suggestion and your decisions
- 👥 **Team-shared policies** - Consistent safety across your organization

## Quick Start

1. Install from VS Code Marketplace
2. Start coding - Agent OS protects you automatically

```
⚠️  Agent OS Warning

Blocked: Destructive SQL operation detected

The AI suggested: DELETE FROM users WHERE ...
This violates your safety policy.

[Review Policy] [Allow Once] [Suggest Alternative]
```

## Features

### 1. Real-Time Code Safety

Agent OS analyzes code as you type/paste and blocks dangerous patterns:

| Policy | Default | Description |
|--------|---------|-------------|
| Destructive SQL | ✅ On | Block DROP, DELETE, TRUNCATE |
| File Deletes | ✅ On | Block rm -rf, unlink, rmtree |
| Secret Exposure | ✅ On | Block hardcoded API keys, passwords |
| Privilege Escalation | ✅ On | Block sudo, chmod 777 |
| Unsafe Network | ❌ Off | Block HTTP (non-HTTPS) calls |

### 2. CMVK Multi-Model Review

Right-click on code and select **"Agent OS: Review Code with CMVK"** to get a consensus review from multiple AI models:

```
🛡️ Agent OS Code Review

Consensus: 66% Agreement

✅ GPT-4:     No issues
✅ Claude:    No issues  
⚠️  Gemini:   Potential SQL injection (Line 42)

Recommendations:
1. Use parameterized queries to prevent SQL injection
```

### 3. Audit Log Sidebar

Click the shield icon in the activity bar to see:
- Blocked operations today/this week
- Warning history
- CMVK review results
- Export capability for compliance

### 4. Team Policies

Share policies via `.vscode/agent-os.json`:

```json
{
  "policies": {
    "blockDestructiveSQL": true,
    "blockFileDeletes": true,
    "blockSecretExposure": true
  },
  "customRules": [
    {
      "name": "no_console_log",
      "pattern": "console\\.log",
      "message": "Remove console.log before committing",
      "severity": "low"
    }
  ]
}
```

Commit to your repo - all team members get the same policies.

## Configuration

Open Settings (Ctrl+,) and search for "Agent OS":

| Setting | Default | Description |
|---------|---------|-------------|
| `agentOS.enabled` | true | Enable/disable Agent OS |
| `agentOS.mode` | basic | basic, enhanced (CMVK), enterprise |
| `agentOS.cmvk.enabled` | false | Enable multi-model verification |
| `agentOS.cmvk.models` | ["gpt-4", "claude-sonnet-4", "gemini-pro"] | Models for CMVK |
| `agentOS.cmvk.consensusThreshold` | 0.8 | Required agreement (0.5-1.0) |
| `agentOS.audit.retentionDays` | 7 | Days to keep audit logs |

## Commands

| Command | Description |
|---------|-------------|
| `Agent OS: Review Code with CMVK` | Multi-model code review |
| `Agent OS: Toggle Safety Mode` | Enable/disable protection |
| `Agent OS: Show Audit Log` | Open audit log sidebar |
| `Agent OS: Configure Policies` | Open policy configuration |
| `Agent OS: Export Audit Log` | Export logs to JSON |

## Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | Local policies, 7-day audit, 10 CMVK/day |
| **Pro** | $9/mo | Unlimited CMVK, 90-day audit, priority support |
| **Enterprise** | Custom | Self-hosted, SSO, compliance reports |

## Privacy

- **Local-first**: Policy checks run entirely in the extension
- **No network**: Basic mode never sends code anywhere
- **Opt-in CMVK**: You choose when to use cloud verification
- **Open source**: Inspect the code yourself

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE).

---

**Made with 🛡️ by the Agent OS team**

[GitHub](https://github.com/imran-siddique/agent-os) | [Documentation](https://agent-os.dev/docs) | [Report Issue](https://github.com/imran-siddique/agent-os/issues)
