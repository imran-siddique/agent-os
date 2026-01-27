# Agent OS for GitHub Copilot

> **Part of [Agent OS](https://github.com/imran-siddique/agent-os)** - Kernel-level governance for AI agents

**The Safety Layer Copilot Needs**

[![npm version](https://badge.fury.io/js/@agent-os%2Fcopilot-extension.svg)](https://www.npmjs.com/package/@agent-os/copilot-extension)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Agent OS Copilot Extension acts as a safety layer between GitHub Copilot and your IDE. It filters suggestions, verifies code with multi-model review (CMVK), and maintains an audit trail.

```
┌──────────────────────────────────────┐
│  Developer                           │
└────────────┬─────────────────────────┘
             │ Request
┌────────────▼─────────────────────────┐
│  GitHub Copilot                      │
└────────────┬─────────────────────────┘
             │ Suggestion
┌────────────▼─────────────────────────┐
│  🛡️ Agent OS Extension              │
│  - Policy Check                      │
│  - CMVK Verification                 │
│  - Audit Log                         │
└────────────┬─────────────────────────┘
             │ Safe Suggestion
┌────────────▼─────────────────────────┐
│  VS Code / IDE                       │
└──────────────────────────────────────┘
```

## Features

### 1. Suggestion Filtering

Automatically screens Copilot suggestions for:
- Destructive SQL operations (DROP, DELETE, TRUNCATE)
- Hardcoded secrets (API keys, passwords, tokens)
- Dangerous file operations (rm -rf)
- Privilege escalation (sudo, chmod 777)

### 2. Chat Commands

Use `@agent-os` in Copilot Chat:

```
@agent-os review    - Review code with CMVK multi-model verification
@agent-os policy    - Show active safety policies
@agent-os audit     - View recent safety audit log
@agent-os help      - Show help
```

### 3. Safety Annotations

Copilot suggestions are annotated with safety status:

```
✅ Suggestion 1 - Verified safe by Agent OS
⚠️ Suggestion 2 - Warning: Potential SQL injection
❌ Suggestion 3 - Blocked: Hardcoded API key detected
```

## Installation

### As a Copilot Extension (Recommended)

1. Go to GitHub Settings → Copilot → Extensions
2. Search for "Agent OS Safety"
3. Enable the extension

### Self-Hosted

```bash
# Clone the repository
git clone https://github.com/imran-siddique/agent-os
cd agent-os/copilot-extension

# Install dependencies
npm install

# Build
npm run build

# Run
npm start
```

## Configuration

### Environment Variables

```bash
# .env
PORT=3000
LOG_LEVEL=info
CMVK_API_ENDPOINT=https://api.agent-os.dev/cmvk
CMVK_API_KEY=your-api-key  # Optional: enables real CMVK
```

### Policy Configuration

Create `.github/agent-os.json` in your repository:

```json
{
  "policies": {
    "blockDestructiveSQL": true,
    "blockFileDeletes": true,
    "blockSecretExposure": true,
    "blockPrivilegeEscalation": true,
    "blockUnsafeNetworkCalls": false
  },
  "cmvk": {
    "enabled": true,
    "models": ["gpt-4", "claude-sonnet-4", "gemini-pro"],
    "consensusThreshold": 0.8
  }
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/filter` | POST | Filter Copilot suggestions |
| `/api/chat` | POST | Handle @agent-os chat commands |
| `/api/annotate` | POST | Get safety annotations for code |
| `/api/audit` | GET | Get audit log |
| `/api/policy` | GET/POST | Get or update policies |
| `/health` | GET | Health check |

## Example Usage

### Filter Suggestions

```bash
curl -X POST http://localhost:3000/api/filter \
  -H "Content-Type: application/json" \
  -d '{
    "suggestions": [
      {
        "id": "1",
        "code": "await db.query(\"DROP TABLE users\")",
        "language": "javascript"
      }
    ],
    "context": {
      "file": { "path": "src/api.js", "language": "javascript" }
    }
  }'
```

### Chat Command

```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "@agent-os review",
    "command": "review",
    "context": {
      "selection": {
        "text": "function processPayment(userId, amount) { ... }"
      }
    }
  }'
```

## Docker Deployment

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

```bash
docker build -t agent-os-copilot .
docker run -p 3000:3000 agent-os-copilot
```

## Security

- All policy checks run locally (no data sent externally)
- CMVK is opt-in and only sends code when explicitly requested
- Audit logs are stored locally only
- No telemetry or analytics

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE).

---

**Part of the [Agent OS](https://github.com/imran-siddique/agent-os) ecosystem**
