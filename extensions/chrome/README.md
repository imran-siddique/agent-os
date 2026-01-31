# Agent OS Browser Extension

> **Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents

**Safe AI agents for GitHub, Jira, AWS Console, and more - directly in your browser.**

## What's New in v1.0

- 🤖 **Universal Agent Bar** - Access agents from any supported page
- 🐙 **GitHub Integration** - PR reviews, policy checks, auto-merge
- 📋 **Jira Integration** - Issue automation, sprint planning
- ☁️ **AWS Console Integration** - Cost monitoring, security alerts
- ⚙️ **Settings Page** - Full configuration UI

## Features

### 🐙 GitHub Integration

- **PR Policy Tab** - See policy check results on every pull request
- **Auto-merge** - Merge safe PRs automatically
- **Issue Labeler** - Auto-label issues based on content
- **Security Scan** - Check code for vulnerabilities

### 📋 Jira Integration

- **Break into Subtasks** - Auto-decompose epics and stories
- **Story Point Estimation** - AI-powered estimates
- **Find Related PRs** - Link issues to code changes
- **Sprint Planning** - Optimize sprint assignments

### ☁️ AWS Console Integration

- **Cost Alerts** - Get notified of budget overruns
- **Security Scan** - Audit security groups and IAM policies
- **Resource Optimization** - Suggestions for right-sizing
- **Compliance Check** - Verify against SOC2, HIPAA, etc.

### 🤖 Universal Agent Bar

Floating action button on every supported page:
- Create agents for the current page
- View running agents
- Access audit logs
- Quick settings

## Installation

### From Chrome Web Store

1. Visit the [Chrome Web Store](https://chrome.google.com/webstore)
2. Search for "AgentOS"
3. Click "Add to Chrome"

### Manual Installation (Developer Mode)

1. Clone the repository:
   ```bash
   git clone https://github.com/imran-siddique/agent-os.git
   cd agent-os/extensions/chrome
   ```

2. Install dependencies and build:
   ```bash
   npm install
   npm run build
   ```

3. Open Chrome and go to `chrome://extensions/`

4. Enable "Developer mode" (toggle in top right)

5. Click "Load unpacked" and select the `dist` folder

## Quick Start

1. **Click the extension icon** to open the popup
2. **Sign in** with your AgentOS account (or create one)
3. **Enable platforms** in Settings (GitHub, Jira, AWS)
4. **Visit a supported site** and see agents in action

## Popup Interface

The popup shows:
- **Status Banner** - AgentOS active/disabled
- **Current Page** - Detected platform
- **Active Agents** - Running agents with controls
- **Suggested Agents** - Recommendations for the page

## Configuration

Click the ⚙️ icon to access settings:

| Setting | Default | Description |
|---------|---------|-------------|
| Enable AgentOS | true | Master on/off switch |
| Notifications | true | Browser notifications |
| Auto-run Agents | false | Run agents automatically |
| GitHub | true | Enable GitHub integration |
| Jira | true | Enable Jira integration |
| AWS | false | Enable AWS Console integration |

## Platform Support

### Supported Platforms

| Platform | Status | Features |
|----------|--------|----------|
| GitHub | ✅ Full | PR reviews, issue automation, security |
| Jira | ✅ Full | Sprint planning, estimation, breakdown |
| AWS Console | ✅ Full | Cost, security, optimization |
| GitLab | 🚧 Coming | Similar to GitHub |
| Linear | 🚧 Coming | Similar to Jira |

### Browser Support

| Browser | Status |
|---------|--------|
| Chrome | ✅ Supported |
| Edge | ✅ Supported |
| Brave | ✅ Supported |
| Firefox | 🚧 Coming soon |
| Safari | 🚧 Planned |

## Privacy & Security

- **Minimal Permissions** - Only requests what's needed
- **Local-first** - Agent configs stored locally
- **Optional Cloud Sync** - Encrypted if enabled
- **No Tracking** - No analytics without consent
- **Open Source** - Inspect the code yourself

## Development

```bash
# Install dependencies
npm install

# Development build (watch mode)
npm run dev

# Production build
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

### Project Structure

```
chrome/
├── src/
│   ├── background/      # Service worker
│   ├── content/         # Platform content scripts
│   │   ├── github.ts
│   │   ├── jira.ts
│   │   └── aws.ts
│   ├── popup/           # Extension popup (React)
│   ├── options/         # Settings page (React)
│   └── shared/          # Shared utilities
├── manifest.json        # Extension manifest
├── webpack.config.js    # Build configuration
└── package.json
```

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../../LICENSE).

---

**Made with 🛡️ by the Agent OS team**

[GitHub](https://github.com/imran-siddique/agent-os) | [Documentation](https://agent-os.dev/docs) | [Report Issue](https://github.com/imran-siddique/agent-os/issues)

---

**Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents
