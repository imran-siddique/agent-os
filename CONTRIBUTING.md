# Contributing to Agent OS

Thank you for your interest in contributing! Agent OS is designed to be extended by the community.

---

## 🚀 Development Setup

### Prerequisites

- **Python 3.9+**
- **pip** (latest recommended)
- **git**

### Clone and Install

```bash
git clone https://github.com/imran-siddique/agent-os.git
cd agent-os
pip install -e ".[dev]"
```

### Verify Your Setup

```bash
# Run all tests (unit + module-specific)
pytest tests/ modules/*/tests -v

# Run a demo to confirm everything works
python examples/carbon-auditor/demo.py
```

### Developer Tooling

```bash
# Type checking
mypy src/

# Linting
ruff check .

# Formatting
ruff format .
```

> **Tip:** Run all three checks before opening a PR. CI will enforce them.

---

## 🏷️ Good First Issues

New to the project? Start here:

| Label | Description |
|-------|-------------|
| [`good-first-issue`](https://github.com/imran-siddique/agent-os/labels/good-first-issue) | Small, well-defined tasks |
| [`documentation`](https://github.com/imran-siddique/agent-os/labels/documentation) | Improve docs and examples |
| [`needs-tests`](https://github.com/imran-siddique/agent-os/labels/needs-tests) | Add test coverage |

---

## 🎁 Integration Bounties

We're actively looking for integration contributions:

| Integration | Description | Status |
|-------------|-------------|--------|
| **LangChain** | Wrap LangChain agents | 🟡 Starter code in `integrations/` |
| **CrewAI** | Wrap CrewAI crews | 🟡 Starter code in `integrations/` |
| **AutoGen** | Wrap Microsoft AutoGen | 🟡 Starter code in `integrations/` |
| **OpenAI Swarm** | Wrap OpenAI's Swarm | 🔴 Open |
| **LlamaIndex** | Wrap LlamaIndex agents | 🔴 Open |

See `src/agent_os/integrations/` for the adapter pattern.

---

## 📐 Architecture Overview

Agent OS follows a **4-layer modular kernel** architecture. Each layer has a clear responsibility and strict dependency rules.

| Layer | Name | Key Modules | Purpose |
|-------|------|-------------|---------|
| **L1** | Primitives | `primitives/` — CMVK, CaaS, EMK | Core identity, credentials, execution memory. Pure types with zero external dependencies. |
| **L2** | Infrastructure | `cmvk/`, `iatp/` — IATP, AMB, ATR | Inter-agent trust protocol, message bus, trust registry. Protocols and transport. |
| **L3** | Framework | `control-plane/` — Control plane, observability, nexus | Governance enforcement, kernel orchestration, observability. |
| **L4** | Intelligence | `scak/` — SCAK, mute-agent, MCP server | Semantic context awareness, self-correction, MCP kernel server. |

### Layer Boundary Rules

> **Lower layers must never import from upper layers.**

- L1 depends on **nothing** — pure types, zero deps
- L2 may depend on **L1 only**
- L3 may depend on **L1 and L2**
- L4 may depend on **L1, L2, and L3**

Violating layer boundaries will be caught by import linting (`.importlinter` config at the repo root).

### Project Structure

```
agent-os/
├── src/agent_os/        # Main package (re-exports everything)
│   ├── __init__.py      # Unified imports
│   ├── cli.py           # agentos CLI
│   └── integrations/    # Framework adapters (base.py, profiling.py)
├── modules/             # Individual kernel modules
│   ├── primitives/      # L1: Base types
│   ├── cmvk/            # L2: Verification
│   ├── iatp/            # L2: Trust protocol
│   ├── control-plane/   # L3: Kernel
│   └── scak/            # L4: Self-correction
├── extensions/          # IDE extensions
│   ├── vscode/          # VS Code extension
│   ├── copilot/         # GitHub Copilot extension
│   └── cursor/          # Cursor IDE extension
├── examples/            # Working demos
│   ├── getting-started/ # Hello world, chat, tools
│   └── production/      # Full demos with observability
├── docs/                # Documentation
└── tests/               # Integration tests
```

---

## 📝 Coding Standards

### Style & Formatting

- **Formatter / Linter:** [Ruff](https://docs.astral.sh/ruff/) (line-length: **100**, target: **Python 3.9+**)
- **Enabled rule sets:** `E`, `W`, `F`, `I` (isort), `B` (bugbear), `C4`, `UP` (pyupgrade)
- **Type checker:** MyPy in strict mode with the Pydantic plugin

### Docstrings

Use **Google-style** docstrings for all public functions, classes, and methods:

```python
def verify_credential(credential: Credential, policy: GovernancePolicy) -> bool:
    """Verify a credential against the governance policy.

    Args:
        credential: The credential to verify.
        policy: The governance policy to check against.

    Returns:
        True if the credential passes all policy checks.

    Raises:
        PolicyViolationError: If the credential violates a blocked pattern.
    """
```

### Type Hints

- **Required** on all public API functions, methods, and class attributes.
- Enforced by `mypy --strict`.

### Data Structures

- Use `dataclass` or Pydantic `BaseModel` for data structures — avoid raw dicts for structured data.
- Governance types: `GovernancePolicy`, `PatternType` (`SUBSTRING`, `REGEX`, `GLOB`), `GovernanceEventType` (`POLICY_CHECK`, `POLICY_VIOLATION`, `TOOL_CALL_BLOCKED`, `CHECKPOINT_CREATED`).

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | A new feature |
| `fix:` | A bug fix |
| `docs:` | Documentation only changes |
| `test:` | Adding or updating tests |
| `refactor:` | Code change that neither fixes a bug nor adds a feature |
| `chore:` | Maintenance tasks (deps, CI, tooling) |

Example: `git commit -m "feat(iatp): add mutual attestation handshake"`

---

## 🧪 Testing Requirements

### Running Tests

```bash
# Run all tests (unit + module-specific)
pytest tests/ modules/*/tests -v

# Run a specific layer's tests
pytest tests/test_layer1_primitives.py -v

# Run with coverage
pytest tests/ --cov=src/agent_os --cov-report=html --cov-branch

# Run demos as integration tests
python examples/hello-world/agent.py
python examples/carbon-auditor/demo.py --scenario both
python examples/grid-balancing/demo.py --agents 10
python examples/defi-sentinel/demo.py --attack all
python examples/pharma-compliance/demo.py --reports 10
```

### Test Expectations

- **All new features must include tests.** PRs without tests for new functionality will be requested to add them.
- **Minimum coverage:** Test the happy path **+** at least one edge case per feature.
- **Async tests:** Use `pytest-asyncio` (`asyncio_mode = "auto"` is configured in `pyproject.toml`).
- **Test location:** Unit tests go in `tests/`. Module-specific tests go in `modules/<module>/tests/`.

### Boundary: `test_mcp_server.py`

> **Never modify `tests/test_mcp_server.py`.** This file has a known pre-existing failure and is excluded from CI. Leave it as-is.

---

## 🔀 Pull Request Process

### Workflow

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make changes** following the coding standards above
4. **Run checks locally:**
   ```bash
   ruff check . && ruff format --check . && mypy src/ && pytest tests/ modules/*/tests -v
   ```
5. **Commit** using conventional commits:
   ```bash
   git commit -m "feat: add my feature"
   ```
6. **Push** your branch and **open a PR** against `main`
7. **Describe** what you changed and why in the PR body

### PR Review Criteria

- All CI checks pass (lint, type check, tests, layer boundary)
- Tests cover new functionality
- Documentation updated if applicable
- Follows coding standards above

---

## 📦 Release Process

Agent OS follows [Semantic Versioning](https://semver.org/):

- **Patch** (1.0.x): Bug fixes, dependency updates
- **Minor** (1.x.0): New features, backward-compatible
- **Major** (x.0.0): Breaking API changes

Releases are published to [PyPI](https://pypi.org/project/agent-os-kernel/) via the `publish.yml` workflow when a GitHub Release is created.

---

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/my-feature
   ```
7. **Open a PR** against `main`

### PR Checklist

Before requesting review, confirm:

- [ ] Code follows the project coding standards (Ruff, MyPy, Google docstrings)
- [ ] All new/changed public APIs have type hints
- [ ] Tests added for new functionality (happy path + edge case)
- [ ] All existing tests pass locally (`pytest tests/ modules/*/tests -v`)
- [ ] No secrets, API keys, or credentials committed
- [ ] Backward compatibility maintained (no breaking changes to public APIs)
- [ ] Governance policies not loosened (policies may only be tightened)
- [ ] Commit messages follow conventional commit format

### Review Process

- At least **one maintainer approval** is required to merge.
- CI must pass (lint, type-check, tests) before merge.
- Reviewers may request changes — please address feedback in follow-up commits.
- Squash-merge is preferred for clean history.

---

## 🚧 Boundaries

These rules are **non-negotiable** and enforced in review:

| Rule | Detail |
|------|--------|
| 🔑 **Never commit secrets** | No API keys, tokens, or credentials in source code — ever. |
| 🔒 **Never loosen GovernancePolicy** | Existing policy constraints may only be **tightened**, never relaxed. |
| 🔄 **Keep backward compatibility** | Do not break existing public API signatures. |
| 🚫 **Never modify `test_mcp_server.py`** | Known pre-existing failure; excluded from CI. |
| 📦 **Respect layer boundaries** | Lower layers must never import from upper layers. |

---

## 🎯 Design Philosophy

**"Scale by Subtraction"** — We value simplicity over features.

### We ✅ Want

- POSIX-inspired primitives (signals, VFS, pipes)
- CLI-first interfaces
- Safety guarantees (0% violation)
- Kernel/user space separation
- Minimal dependencies

### We ❌ Avoid

- Visual workflow editors
- CRM/ERP connectors
- Low-code builders
- Feature bloat
- Vendor lock-in

---

## 🌱 Path to Maintainer

We recognize and reward consistent contributors:

| Role | Requirements | Permissions |
|------|-------------|-------------|
| **Contributor** | 1+ merged PR | Listed in PR history |
| **Regular Contributor** | 5+ merged PRs | Recognized in README contributors section |
| **Reviewer** | 10+ merged PRs + active code reviews | Invited to review PRs, triaging issues |
| **Maintainer** | Invitation by existing maintainers | Merge access, release management, governance decisions |

### How Progression Works

- **Contributor → Regular Contributor:** Keep submitting quality PRs. Once you reach 5 merged PRs, you'll be added to the README contributors section.
- **Regular Contributor → Reviewer:** Demonstrate deep knowledge by reviewing others' PRs and participating in discussions. After 10+ merged PRs with active review participation, maintainers will invite you to the reviewer role.
- **Reviewer → Maintainer:** Maintainers are invited based on sustained contribution, sound judgment in reviews, and alignment with the project's design philosophy. There is no fixed threshold — existing maintainers decide by consensus.

---

## 💬 Getting Help

- **Questions?** Open a [Discussion](https://github.com/imran-siddique/agent-os/discussions)
- **Found a bug?** Open an [Issue](https://github.com/imran-siddique/agent-os/issues)
- **Want to chat?** See the README for community links

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.
