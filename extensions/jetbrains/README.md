# Agent OS for JetBrains IDEs

> **Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents

**Kernel-level safety for AI coding assistants in IntelliJ, PyCharm, WebStorm, and all JetBrains IDEs.**

## The Problem

AI coding assistants can suggest dangerous code:
- `DROP TABLE users` - deleting production data
- Hardcoded API keys and secrets
- `rm -rf /` - destructive file operations
- Code with security vulnerabilities

## The Solution

Agent OS wraps your AI assistant with a kernel that provides:

- 🛡️ **Real-time policy enforcement** - Block destructive operations before they execute
- 🔍 **Multi-model code review (CMVK)** - Verify code with GPT-4, Claude, and Gemini
- 📋 **Complete audit trail** - Log every AI suggestion and your decisions
- 👥 **Team-shared policies** - Consistent safety across your organization

## Installation

### From JetBrains Marketplace

1. Open Settings/Preferences → Plugins
2. Search for "Agent OS"
3. Click Install

### Manual Installation

1. Download the latest `.zip` from [Releases](https://github.com/imran-siddique/agent-os/releases)
2. Open Settings/Preferences → Plugins → ⚙️ → Install Plugin from Disk
3. Select the downloaded file

## Features

### 1. Real-Time Code Analysis

Agent OS analyzes code as you type and highlights dangerous patterns:

| Policy | Default | Description |
|--------|---------|-------------|
| Destructive SQL | ✅ On | Block DROP, DELETE, TRUNCATE |
| File Deletes | ✅ On | Block rm -rf, unlink, rmtree |
| Secret Exposure | ✅ On | Block hardcoded API keys, passwords |
| Privilege Escalation | ✅ On | Block sudo, chmod 777 |
| Unsafe Network | ❌ Off | Block HTTP (non-HTTPS) calls |

### 2. Inline Warnings

Dangerous code is highlighted directly in the editor with gutter icons:

```
🛡️ Line 42: Destructive SQL operation detected
   DELETE FROM users WHERE active = false
   
   [Allow Once] [Add to Allowlist] [Learn More]
```

### 3. CMVK Multi-Model Review

Right-click on code and select **"Agent OS → Review with CMVK"**:

```
🛡️ Agent OS Code Review

Consensus: 66% Agreement

✅ GPT-4:     No issues
✅ Claude:    No issues  
⚠️  Gemini:   Potential SQL injection (Line 42)

Recommendations:
1. Use parameterized queries to prevent SQL injection
```

### 4. Tool Window

The Agent OS tool window shows:
- Safety status overview
- Recent blocked operations
- Audit log
- Policy configuration

### 5. Team Policies

Share policies via `.idea/agent-os.xml` or `.agent-os/config.yaml`:

```yaml
# .agent-os/config.yaml
policies:
  blockDestructiveSQL: true
  blockFileDeletes: true
  blockSecretExposure: true
  
customRules:
  - name: no_console_log
    pattern: "console\\.log"
    message: "Remove console.log before committing"
    severity: warning
```

## Configuration

Open Settings/Preferences → Tools → Agent OS:

| Setting | Default | Description |
|---------|---------|-------------|
| Enable Agent OS | true | Enable/disable all checks |
| Mode | basic | basic, enhanced (CMVK), enterprise |
| CMVK Enabled | false | Enable multi-model verification |
| CMVK Models | GPT-4, Claude, Gemini | Models for verification |
| Consensus Threshold | 80% | Required agreement |
| Audit Retention | 7 days | Days to keep logs |

## Supported IDEs

- IntelliJ IDEA (Community & Ultimate)
- PyCharm (Community & Professional)
- WebStorm
- PhpStorm
- GoLand
- RubyMine
- CLion
- Rider
- DataGrip
- Android Studio

**Requires IDE version 2023.1 or later**

## Actions

| Action | Shortcut | Description |
|--------|----------|-------------|
| Review with CMVK | `Ctrl+Shift+R` | Multi-model code review |
| Toggle Agent OS | `Ctrl+Shift+A` | Enable/disable protection |
| Show Audit Log | - | Open audit log tool window |
| Configure Policies | - | Open settings |

## Privacy

- **Local-first**: Policy checks run entirely in the plugin
- **No network**: Basic mode never sends code anywhere
- **Opt-in CMVK**: You choose when to use cloud verification
- **Open source**: Inspect the code yourself

## Building from Source

```bash
cd extensions/jetbrains
./gradlew build

# Run in sandbox IDE
./gradlew runIde

# Create distribution
./gradlew buildPlugin
```

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE).

---

**Made with 🛡️ by the Agent OS team**

[GitHub](https://github.com/imran-siddique/agent-os) | [Documentation](https://agent-os.dev/docs) | [Report Issue](https://github.com/imran-siddique/agent-os/issues)
