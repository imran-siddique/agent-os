# Agent OS Governance Bot

A GitHub App that provides zero-config, automated governance reviews on pull requests.

## Features

- **Prompt injection scanning** — Detects injection patterns in code, configs, and prompts
- **Policy compliance** — Validates against configurable governance rule sets
- **Security pattern scanning** — Catches secrets, unsafe patterns, dangerous code
- **Inline review comments** — Annotates specific lines with findings and fix suggestions
- **Check run integration** — Pass/fail status blocking merge on critical findings

## Quick Start

1. Install the app from [GitHub Marketplace](#) (coming soon)
2. Optionally add `.github/agent-governance.yml` to your repo to customize
3. Every PR gets reviewed automatically

## Configuration

Create `.github/agent-governance.yml` in your repository:

```yaml
# Governance profile: security | compliance | agent-safety | all
profile: security

# Severity threshold for blocking merge (error = blocks, warning = advisory)
block_on: error

# Files to scan (glob patterns)
include:
  - "**/*.py"
  - "**/*.yaml"
  - "**/*.yml"
  - "**/*.json"
  - "**/*.md"

# Files to skip
exclude:
  - "node_modules/**"
  - "*.lock"
  - "dist/**"

# Custom blocked patterns (in addition to profile defaults)
custom_patterns:
  - pattern: "TODO.*hack"
    severity: warning
    message: "Suspicious TODO comment"
```

## Governance Profiles

### `security` (default)
- Prompt injection patterns in code/config files
- Hardcoded secrets and API keys
- Dangerous code patterns (eval, exec, subprocess)
- Insecure configuration values

### `compliance`
- License header checks
- PII patterns in code
- Audit logging requirements
- Data retention policy references

### `agent-safety`
- Agent prompt files for injection vulnerabilities
- MCP server configuration safety
- Tool allowlist/blocklist validation
- Trust configuration review

## Architecture

```
GitHub PR Event (webhook)
    ↓
Webhook Handler (Azure Functions / Vercel)
    ↓
File Analyzer
    ├─ PromptInjectionDetector
    ├─ SecurityPatternScanner
    └─ PolicyEvaluator
    ↓
Review Builder → GitHub Check Run + PR Review Comments
```

## Development

```bash
cd github-app
pip install -r requirements.txt
python -m pytest tests/ -v

# Local testing with webhook proxy
python app.py
```

## Deployment

### Option 1: Azure Functions

1. Create a Function App in Azure Portal (Python 3.11+ runtime)
2. Configure app settings:
   ```
   GITHUB_APP_ID=<your-app-id>
   GITHUB_APP_PRIVATE_KEY=<base64-encoded-private-key>
   GITHUB_WEBHOOK_SECRET=<your-webhook-secret>
   ```
3. Deploy:
   ```bash
   cd azure-function
   func azure functionapp publish <your-function-app-name>
   ```

### Option 2: Docker / Any server

```bash
cd github-app
pip install -r requirements.txt
# Set environment variables
export GITHUB_APP_ID=...
export GITHUB_APP_PRIVATE_KEY=...
export GITHUB_WEBHOOK_SECRET=...
# Run
python webhook.py
```

### Register the App

1. Go to https://github.com/settings/apps/new
2. Set webhook URL to your deployment URL + `/webhook`
3. Set permissions: Pull Requests (read/write), Contents (read), Checks (write)
4. Subscribe to events: Pull Request
5. Generate a private key and save it
6. Set env vars and deploy

Or use the manifest flow:
1. Base64-encode `app.yml`
2. POST to https://github.com/settings/apps/new?manifest=true
