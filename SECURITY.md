# Security Policy

## Supported Versions

The following versions of CMVK are currently receiving security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| 0.x.x   | :x:                |

## Reporting a Vulnerability

We take the security of CMVK seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please email security concerns to: **imran.siddique@example.com**

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Assessment**: We will assess the vulnerability and provide an estimated timeline within 7 days
- **Fix**: Critical vulnerabilities will be addressed within 30 days
- **Disclosure**: We will coordinate disclosure timing with you

### Security Considerations for CMVK

#### Sandbox Execution

The `SandboxExecutor` tool executes untrusted code. Security measures include:

1. **Isolated Execution**: Code runs in isolated subprocess with restricted permissions
2. **Timeout Limits**: Execution is time-limited to prevent resource exhaustion
3. **Resource Caps**: Memory and CPU limits are enforced
4. **No Network Access**: Sandboxed code cannot make network requests by default

**Warning**: The sandbox is designed for development/research use. For production deployments, consider using containerized execution (Docker) or dedicated sandboxing solutions.

#### API Key Security

CMVK uses API keys for LLM providers. Best practices:

1. **Never commit API keys** to version control
2. Use environment variables: `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`
3. Use `.env` files that are `.gitignore`d
4. Rotate keys if accidentally exposed

#### Data Privacy

- Experiment traces may contain sensitive prompts/outputs
- Do not upload private data to Hugging Face Hub without review
- Use the `private=True` flag for sensitive datasets

## Security Features

### Trace Logging

All kernel operations are logged for audit purposes:

```python
kernel = VerificationKernel(
    generator=generator,
    verifier=verifier,
    enable_trace_logging=True  # Enable full audit trail
)
```

Traces can be reviewed in `logs/traces/` for security auditing.

### Model Diversity Enforcement

The kernel enforces that generator and verifier use different models, preventing single-point-of-failure scenarios:

```python
# This raises ValueError - same model is rejected
kernel = VerificationKernel(
    generator=OpenAIGenerator(model="gpt-4"),
    verifier=OpenAIGenerator(model="gpt-4")  # Error!
)
```

## Dependencies

We regularly audit dependencies for known vulnerabilities using:
- GitHub Dependabot
- `pip-audit` in CI pipeline

To check for vulnerable dependencies locally:

```bash
pip install pip-audit
pip-audit
```

## Responsible AI

CMVK is designed to improve AI safety through adversarial verification. However:

- Generated code should be reviewed before production use
- Verification is not a guarantee of correctness
- Human oversight remains essential for high-stakes applications

## Acknowledgments

We appreciate security researchers who help keep CMVK secure. Contributors who report valid vulnerabilities will be acknowledged in our security hall of fame (with permission).
