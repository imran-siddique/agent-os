---
layout: default
title: Policy Reference
parent: Documentation
nav_order: 5
has_children: true
permalink: /docs/policies/
description: "Complete reference for Agent OS policy language - rules, conditions, actions, and examples."
---

# Policy Reference
{: .fs-9 }

Define what your agents can and cannot do with declarative policies.
{: .fs-6 .fw-300 }

---

## Policy Basics

Policies are YAML files that define rules for what agents can do. The kernel evaluates every action against these rules before execution.

```yaml
# my-policy.yaml
version: "1.0"
name: "Production Policy"
mode: strict  # strict | permissive | audit

rules:
  - action: file_write
    resource: "/prod/*"
    effect: deny
    reason: "Production writes blocked"
```

---

## Built-in Policy Modes

### Strict Mode (Default)

Blocks known dangerous operations by default:

| Action | Blocked |
|:-------|:--------|
| `file_write` | `/prod/*`, `/etc/*`, system paths |
| `file_delete` | All paths by default |
| `sql` | `DROP`, `DELETE`, `TRUNCATE`, `ALTER` |
| `shell` | All shell execution |
| `network` | Unknown external domains |
| `secrets` | Hardcoded API keys, passwords |

```python
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")
```

### Permissive Mode

Allows most operations, only blocks explicit denies:

```python
kernel = KernelSpace(policy="permissive")
```

### Audit Mode

Allows all operations but logs everything:

```python
kernel = KernelSpace(policy="audit")
```

---

## Policy Structure

### Full Policy Schema

```yaml
version: "1.0"                    # Policy format version
name: "My Policy"                 # Human-readable name
description: "Policy for..."      # Optional description
mode: strict                      # Base mode

# Global settings
settings:
  audit_level: comprehensive      # minimal | standard | comprehensive
  violation_action: block         # block | warn | log
  alert_channel: pagerduty        # Optional alerting

# Custom rules (evaluated in order)
rules:
  - action: <action_type>
    resource: <resource_pattern>  # Optional
    effect: allow | deny
    conditions: [...]             # Optional
    reason: "..."                 # Optional human message
    alert: <severity>             # Optional: critical | warning | info
```

---

## Actions

### File Operations

```yaml
# Block all file writes to production
- action: file_write
  resource: "/prod/**"
  effect: deny

# Allow reads from specific paths
- action: file_read
  resource: "/data/public/*"
  effect: allow

# Block all deletes
- action: file_delete
  resource: "*"
  effect: deny
  alert: critical
```

### SQL Operations

```yaml
# Block destructive SQL
- action: sql
  pattern: "DROP|DELETE|TRUNCATE"
  effect: deny
  reason: "Destructive SQL blocked"

# Allow SELECT only
- action: sql
  pattern: "^SELECT"
  effect: allow
  
# Block SQL injection patterns
- action: sql
  pattern: "--|;.*SELECT|UNION.*SELECT"
  effect: deny
  alert: critical
```

### Network Operations

```yaml
# Allow only specific domains
- action: network
  resource: "api.openai.com"
  effect: allow

- action: network
  resource: "*.internal.company.com"
  effect: allow

# Block all other external
- action: network
  resource: "external:*"
  effect: deny
```

### Shell Operations

```yaml
# Block all shell by default
- action: shell
  effect: deny

# Allow specific safe commands
- action: shell
  pattern: "^(ls|cat|grep|head|tail)"
  effect: allow
```

### Secret Operations

```yaml
# Block hardcoded secrets in output
- action: output
  conditions:
    - contains_pattern: "(api[_-]?key|password|secret|token)\\s*[=:]\\s*['\"][^'\"]{8,}"
  effect: deny
  reason: "Potential secret in output"
```

---

## Conditions

Conditions add fine-grained control to rules:

### Time-Based

```yaml
- action: sql
  pattern: "DELETE"
  conditions:
    - time_window: "business_hours"  # 9am-5pm local
  effect: allow
  
# Define custom windows
time_windows:
  business_hours:
    start: "09:00"
    end: "17:00"
    timezone: "America/New_York"
    days: [mon, tue, wed, thu, fri]
```

### Role-Based

```yaml
- action: file_delete
  resource: "/data/*"
  conditions:
    - role: admin
  effect: allow

- action: file_delete
  resource: "/data/*"
  conditions:
    - role: [user, viewer]
  effect: deny
```

### Rate Limiting

```yaml
- action: api_call
  resource: "openai"
  conditions:
    - rate_limit:
        max: 100
        window: 60  # seconds
  effect: allow
```

### Content-Based

```yaml
- action: output
  conditions:
    - contains_pii: false
    - content_length: { max: 10000 }
  effect: allow
```

---

## Resource Patterns

Patterns support glob-style matching:

| Pattern | Matches |
|:--------|:--------|
| `*` | Any single path segment |
| `**` | Any path depth |
| `{a,b}` | Either a or b |
| `[0-9]` | Character ranges |

```yaml
# Examples
resource: "/data/*"          # /data/file.txt (not /data/sub/file.txt)
resource: "/data/**"         # /data/any/depth/file.txt
resource: "*.{json,yaml}"    # file.json, file.yaml
resource: "/logs/2026-01-*"  # /logs/2026-01-15.log
```

---

## Policy Loading

### From File

```python
from agent_os import KernelSpace
from agent_os.policies import load_policy

kernel = KernelSpace(policy=load_policy("my-policy.yaml"))
```

### From String

```python
policy_yaml = """
version: "1.0"
rules:
  - action: shell
    effect: deny
"""

kernel = KernelSpace(policy=load_policy(policy_yaml))
```

### Programmatic

```python
from agent_os.policies import Policy, Rule

policy = Policy(
    name="My Policy",
    mode="strict",
    rules=[
        Rule(action="shell", effect="deny"),
        Rule(action="file_write", resource="/tmp/*", effect="allow"),
    ]
)

kernel = KernelSpace(policy=policy)
```

---

## Policy Composition

Combine multiple policies:

```python
from agent_os.policies import compose

base = load_policy("base.yaml")
production = load_policy("production.yaml")

# Later rules override earlier
combined = compose(base, production)
kernel = KernelSpace(policy=combined)
```

---

## Example Policies

### Production API Server

```yaml
version: "1.0"
name: "Production API"
mode: strict

rules:
  # Allow database reads
  - action: sql
    pattern: "^SELECT"
    effect: allow
    
  # Block all writes except specific tables
  - action: sql
    pattern: "INSERT INTO (logs|events)"
    effect: allow
    
  # Allow specific external APIs
  - action: network
    resource: "api.stripe.com"
    effect: allow
    
  - action: network
    resource: "api.sendgrid.com"
    effect: allow
```

### Development Mode

```yaml
version: "1.0"
name: "Development"
mode: permissive

rules:
  # Still block production even in dev
  - action: "*"
    resource: "/prod/**"
    effect: deny
    
  # Audit all for learning
  - action: "*"
    effect: allow
    audit: true
```

### Healthcare (HIPAA)

```yaml
version: "1.0"
name: "HIPAA Compliant"
mode: strict

settings:
  audit_level: comprehensive
  
rules:
  # PHI access requires purpose
  - action: read
    resource: "/data/patient/*"
    conditions:
      - purpose: [treatment, operations, research]
      - audit: required
    effect: allow
    
  # Block PHI in outputs
  - action: output
    conditions:
      - contains_phi: true
    effect: deny
    alert: critical
```

---

## Debugging Policies

### Dry Run Mode

Test policies without enforcement:

```python
kernel = KernelSpace(policy=my_policy, dry_run=True)

# Actions are checked but not blocked
# Violations are logged
```

### Policy Explain

Understand why an action was allowed/denied:

```python
result = kernel.policy.explain(
    action="file_write",
    resource="/prod/config.yaml"
)

print(result.decision)      # "deny"
print(result.matching_rule) # Rule that matched
print(result.reason)        # "Production writes blocked"
```

---

## Next Steps

- [Quickstart Tutorial](/docs/tutorials/quickstart/) — Get started
- [Observability Setup](/docs/observability/) — Monitor policy enforcement
- [Healthcare Policy Template](/use-cases/healthcare/) — HIPAA example
- [Education Policy Template](/use-cases/education/) — COPPA example
