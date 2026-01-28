# Agent OS Chrome DevTools Extension

> **Monitor inter-agent communication (AMB) and trust protocols (IATP) directly in Chrome DevTools.**

## Features

### 🔍 AMB Message Monitor
Real-time capture and inspection of Agent Message Bus traffic:
- View all agent-to-agent messages
- Filter by sender, recipient, or content
- Inspect message signatures
- Export message logs

### 🛡️ IATP Trust Inspector
Monitor the Inter-Agent Trust Protocol:
- View registered agents and trust levels
- Track signature verifications
- See trust revocations in real-time
- Inspect public keys

### 🕸️ Agent Network Visualizer
Interactive graph of agent relationships:
- See which agents are communicating
- Color-coded by trust level
- Real-time connection updates

### 📊 Statistics Dashboard
Track key metrics:
- Messages sent/received
- Active agents
- Verification success/failure rates
- Policy violations

## Installation

### From Chrome Web Store (Coming Soon)
1. Visit the Chrome Web Store
2. Search for "Agent OS DevTools"
3. Click "Add to Chrome"

### Manual Installation (Developer Mode)
1. Clone the repository:
   ```bash
   git clone https://github.com/imran-siddique/agent-os.git
   cd agent-os/extensions/chrome
   ```

2. Open Chrome and go to `chrome://extensions/`

3. Enable "Developer mode" (toggle in top right)

4. Click "Load unpacked" and select the `chrome` folder

5. The extension will appear in your extensions list

## Usage

1. Open Chrome DevTools (F12 or Right-click → Inspect)

2. Look for the "Agent OS" tab in DevTools

3. The extension automatically detects Agent OS instances on the page

4. Use the tabs to switch between:
   - **AMB Messages**: View message traffic
   - **IATP Trust**: Monitor trust relationships
   - **Agent Network**: Visual graph of agents
   - **Statistics**: Performance metrics

## Integration with Your App

For the extension to detect your Agent OS instance, expose it on the window object:

```javascript
import { KernelSpace, TrustRegistry, MessageBus } from 'agent-os';

// Make Agent OS discoverable by the extension
window.__AGENT_OS__ = {
  kernel: new KernelSpace(policy),
  trustRegistry: new TrustRegistry(),
  messageBus: new MessageBus(),
  
  // Optional: emit method for real-time monitoring
  emit(event, data) {
    // The extension hooks into this
    console.log(`[Agent OS] ${event}:`, data);
  },
  
  // Helper for trust info lookup
  getTrustInfo(agentId) {
    return this.trustRegistry.getAgent(agentId);
  }
};
```

## DevTools API

The extension provides a JavaScript API accessible from the DevTools console:

```javascript
// Get message history
__AGENT_OS_DEVTOOLS__.getMessages()

// Get registered agents
__AGENT_OS_DEVTOOLS__.getAgents()

// Export logs
__AGENT_OS_DEVTOOLS__.exportLogs()

// Clear captured data
__AGENT_OS_DEVTOOLS__.clear()
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+F` | Filter messages |
| `Ctrl+K` | Clear messages |
| `Ctrl+R` | Refresh trust table |
| `Ctrl+E` | Export logs |

## Privacy

- **Local-only**: All data stays in your browser
- **No network calls**: Extension never sends data externally
- **Session-only**: Data is not persisted between sessions
- **Inspect the source**: Fully open source

## Development

```bash
# Install dependencies (if any)
npm install

# Build (if using TypeScript)
npm run build

# Load extension in Chrome
# chrome://extensions → Load unpacked → select this folder
```

### File Structure

```
chrome/
├── manifest.json        # Extension manifest
├── background.js        # Service worker
├── content.js          # Content script injected into pages
├── injected.js         # Script injected into page context
├── devtools/
│   ├── devtools.html   # DevTools page entry
│   ├── devtools.js     # DevTools panel registration
│   ├── panel.html      # Main panel UI
│   └── panel.js        # Panel logic
├── popup/
│   ├── popup.html      # Toolbar popup
│   └── popup.js        # Popup logic
└── icons/              # Extension icons
```

## Browser Support

- ✅ Chrome 88+
- ✅ Edge 88+
- ✅ Brave 1.20+
- ❌ Firefox (coming soon - requires WebExtensions port)
- ❌ Safari (not planned)

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../../LICENSE).

---

**Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents
