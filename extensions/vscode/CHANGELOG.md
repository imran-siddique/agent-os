# Changelog

All notable changes to the Agent OS VS Code extension will be documented in this file.

## [0.1.0] - 2026-01-27

### Added
- Initial release
- Real-time code safety analysis
- Policy engine with 5 policy categories:
  - Destructive SQL (DROP, DELETE, TRUNCATE)
  - File deletes (rm -rf, unlink, rmtree)
  - Secret exposure (API keys, passwords, tokens)
  - Privilege escalation (sudo, chmod 777)
  - Unsafe network calls (HTTP instead of HTTPS)
- CMVK multi-model code review (mock implementation for demo)
- Audit log sidebar with recent activity
- Policies view showing active policies
- Statistics view with daily/weekly counts
- Status bar with real-time protection indicator
- Team policy sharing via `.vscode/agent-os.json`
- Export audit log to JSON
- Custom rule support

### Known Limitations
- CMVK uses mock responses (real API coming in v0.2.0)
- Inline completion interception is read-only (doesn't block)
- Limited to text change detection for now
