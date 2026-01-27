# Policy Templates

Pre-built policy templates for common use cases.

## Available Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| [secure-coding.yaml](secure-coding.yaml) | Prevents common security vulnerabilities | All development |
| [data-protection.yaml](data-protection.yaml) | PII protection and data handling | Apps handling user data |
| [enterprise.yaml](enterprise.yaml) | Comprehensive enterprise governance | Production deployments |

## Quick Start

### Using CLI

```bash
# Initialize with a template
agentos init my-project --template secure-coding

# Or copy template to existing project
agentos policy apply secure-coding
```

### Manual Setup

Copy the desired template to your project:

```bash
cp templates/policies/secure-coding.yaml .agents/security.md
```

## Template Comparison

| Feature | Secure Coding | Data Protection | Enterprise |
|---------|--------------|-----------------|------------|
| SQL Injection Prevention | ✅ | ⚪ | ✅ |
| Destructive SQL Blocking | ✅ | ⚪ | ✅ |
| Hardcoded Secrets | ✅ | ✅ | ✅ |
| PII Detection | ⚪ | ✅ | ✅ |
| Financial Data | ⚪ | ✅ | ✅ |
| Health Data (HIPAA) | ⚪ | ✅ | ✅ |
| Rate Limiting | ⚪ | ⚪ | ✅ |
| Cost Controls | ⚪ | ⚪ | ✅ |
| Approval Workflows | ⚪ | ⚪ | ✅ |
| SIEM Integration | ⚪ | ⚪ | ✅ |
| SSO Support | ⚪ | ⚪ | ✅ |

## Customization

Templates are starting points. Customize by:

1. **Adding rules**: Add patterns specific to your codebase
2. **Adjusting severity**: Change `SIGKILL` to `SIGSTOP` for warnings
3. **Adding exceptions**: Whitelist known-safe patterns
4. **Combining templates**: Merge multiple templates

### Example: Combining Templates

```yaml
# .agents/security.md
kernel:
  version: "1.0"
  mode: strict

# Include secure coding rules
include:
  - templates/policies/secure-coding.yaml
  - templates/policies/data-protection.yaml

# Add custom rules
policies:
  - name: my_custom_rule
    deny:
      - patterns:
          - "my_specific_pattern"
```

## Contributing Templates

We welcome new policy templates! See [CONTRIBUTING.md](../CONTRIBUTING.md).

Useful templates to contribute:
- `frontend.yaml` - React/Vue/Angular specific
- `api.yaml` - REST/GraphQL API development
- `ml.yaml` - Machine learning pipelines
- `devops.yaml` - CI/CD and infrastructure
