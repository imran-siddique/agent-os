# Security Policy

## About Agent OS

**Agent OS** is part of the [Agent Governance Ecosystem](https://github.com/imran-siddique) — a suite of open-source projects for building, orchestrating, and governing autonomous AI agents in enterprise environments.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest | :x:               |

Only the latest release of Agent OS receives security updates. Users are strongly encouraged to stay up to date.

## Reporting a Vulnerability

If you discover a security vulnerability in Agent OS, please report it responsibly.

**Email:** [security@imransiddique.com](mailto:security@imransiddique.com)

**Please include:**

- A description of the vulnerability
- Steps to reproduce the issue
- Affected version(s)
- Any potential impact assessment

> **Do not open a public GitHub issue for security vulnerabilities.**

## What to Expect

| Step                        | Timeline     |
| --------------------------- | ------------ |
| Acknowledgment of report    | Within 48 hours |
| Initial assessment          | Within 5 business days |
| Fix development and testing | Within 30 days (critical), 90 days (non-critical) |
| CVE assignment              | If applicable, coordinated with the reporter |
| Public disclosure           | After fix is released, per responsible disclosure timeline |

We will keep you informed throughout the process and credit reporters (unless anonymity is requested).

## Responsible Disclosure Timeline

We follow a **90-day responsible disclosure policy**:

1. Reporter submits vulnerability via the email above.
2. We acknowledge receipt within **48 hours**.
3. We work to develop and release a fix within **90 days**.
4. Once the fix is released, the vulnerability may be publicly disclosed.
5. If we are unable to fix the issue within 90 days, we will coordinate with the reporter on an appropriate disclosure timeline.

## Scope

### In Scope

- Source code of Agent OS
- Third-party dependencies used by Agent OS
- Configuration files and deployment templates
- CI/CD pipeline configurations
- Documentation that could lead to insecure usage

### Out of Scope

- Social engineering attacks against maintainers or users
- Denial of Service (DoS/DDoS) attacks
- Attacks requiring physical access
- Issues in third-party services not controlled by this project
- Vulnerabilities already reported and being addressed

## Security Best Practices for Users

- **Keep dependencies updated:** Regularly run dependency audits and update to the latest versions.
- **Use environment variables for secrets:** Never hardcode credentials, API keys, or tokens in configuration files.
- **Enable access controls:** Follow the principle of least privilege when configuring agent permissions.
- **Review configurations:** Audit your deployment configurations against the provided security guidelines.
- **Monitor for advisories:** Watch this repository for security advisories and release notes.
- **Use signed commits:** Enable GPG or SSH commit signing to ensure code integrity.
- **Run in isolated environments:** Use containers or sandboxed environments for agent workloads.

## Agent Governance Ecosystem

Agent OS is part of the broader **Agent Governance Ecosystem**, which provides a unified framework for secure, observable, and compliant AI agent operations. Security policies are coordinated across all ecosystem projects to ensure consistent protection.

For ecosystem-wide security concerns, please contact [security@imransiddique.com](mailto:security@imransiddique.com).

---

Thank you for helping keep Agent OS and the Agent Governance Ecosystem safe for everyone.
