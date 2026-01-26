# Quick Start Guide

Get started with the Agent Control Plane in 5 minutes.

## Installation

Currently, the Agent Control Plane is a standalone Python implementation. Simply clone the repository:

```bash
git clone https://github.com/imran-siddique/agent-control-plane.git
cd agent-control-plane
```

No external dependencies required - uses only Python standard library.

## Your First Agent

Create a new Python file `my_agent.py`:

```python
from control_plane import AgentControlPlane, create_standard_agent
from agent_kernel import ActionType

# 1. Create the control plane
control_plane = AgentControlPlane()

# 2. Create an agent
agent = create_standard_agent(control_plane, "my-first-agent")
print(f"Created agent: {agent.agent_id}")

# 3. Execute an action
result = control_plane.execute_action(
    agent,
    ActionType.FILE_READ,
    {"path": "/data/example.txt"}
)

# 4. Check the result
if result["success"]:
    print("Success!", result["result"])
    print(f"Risk score: {result['risk_score']}")
else:
    print("Failed:", result["error"])
```

Run it:

```bash
python3 my_agent.py
```

## Exploring Features

### See All Examples

```bash
python3 examples.py
```

This runs comprehensive examples showing:
- Permission control
- Rate limiting
- Policy enforcement
- Audit logging
- Risk management

### Run Tests

```bash
python3 test_control_plane.py
```

## Common Patterns

### Read-Only Agent

For agents that only need to read data:

```python
from control_plane import create_read_only_agent

agent = create_read_only_agent(control_plane, "reader-agent")

# Can read files
result = control_plane.execute_action(
    agent,
    ActionType.FILE_READ,
    {"path": "/data/file.txt"}
)  # ✓ Success

# Cannot write files
result = control_plane.execute_action(
    agent,
    ActionType.FILE_WRITE,
    {"path": "/data/file.txt", "content": "new data"}
)  # ✗ Denied
```

### Rate-Limited Agent

For agents that need strict rate limiting:

```python
from policy_engine import ResourceQuota

quota = ResourceQuota(
    agent_id="limited-agent",
    max_requests_per_minute=10,
    max_requests_per_hour=100,
)

agent = control_plane.create_agent(
    "limited-agent",
    quota=quota
)
```

### Custom Security Policy

Add your own security rules:

```python
from agent_kernel import PolicyRule, ActionType
import uuid

def my_validator(request):
    # Your custom validation logic
    if "dangerous" in str(request.parameters):
        return False
    return True

rule = PolicyRule(
    rule_id=str(uuid.uuid4()),
    name="my_security_rule",
    description="Blocks dangerous parameters",
    action_types=[ActionType.CODE_EXECUTION],
    validator=my_validator,
    priority=10
)

control_plane.add_policy_rule(rule)
```

### Monitoring Agent Activity

Track what your agents are doing:

```python
# Get audit log
audit_log = control_plane.get_audit_log(limit=10)
for entry in audit_log:
    print(f"{entry['event_type']}: {entry['details']}")

# Get agent status
status = control_plane.get_agent_status("my-agent")
print(f"Quota usage: {status['quota_status']}")
print(f"Recent executions: {status['execution_history']}")
```

## Understanding Action Types

The control plane supports these action types:

| Action Type | Description | Default Risk | Common Use |
|------------|-------------|--------------|------------|
| `FILE_READ` | Read files | Low (0.1) | Data access |
| `FILE_WRITE` | Write files | Medium (0.5) | Data storage |
| `CODE_EXECUTION` | Execute code | High (0.7) | Computation |
| `API_CALL` | HTTP requests | Medium (0.3) | External APIs |
| `DATABASE_QUERY` | Read from DB | Medium (0.4) | Data queries |
| `DATABASE_WRITE` | Write to DB | High (0.6) | Data updates |
| `WORKFLOW_TRIGGER` | Start workflows | Medium (0.5) | Orchestration |

## Understanding Permission Levels

| Level | Value | Description |
|-------|-------|-------------|
| `NONE` | 0 | No access |
| `READ_ONLY` | 1 | Read operations only |
| `READ_WRITE` | 2 | Read and write operations |
| `ADMIN` | 3 | Full access |

## Execution Flow

Every action goes through this pipeline:

```
1. Permission Check → Is agent allowed?
2. Policy Validation → Does it violate rules?
3. Risk Assessment → Is risk acceptable?
4. Rate Limiting → Within quotas?
5. Execution → Safe sandboxed execution
6. Audit Logging → Record everything
```

If any step fails, the action is denied and logged.

## Next Steps

- Read the [Architecture Documentation](architecture.md)
- Explore the [Examples](examples.py)
- Check out the [README](README.md) for detailed API reference
- Run the [Tests](test_control_plane.py) to understand behavior

## Need Help?

- Review the examples: `python3 examples.py`
- Run the tests: `python3 test_control_plane.py`
- Check the architecture docs: `architecture.md`

## Tips

1. **Start restrictive**: Begin with minimal permissions and add more as needed
2. **Use rate limits**: Prevent runaway agents with quotas
3. **Monitor actively**: Check audit logs regularly
4. **Test policies**: Validate rules work as expected before production
5. **Layer security**: Combine permissions, policies, and rate limits
