# OpenAI Adapter Integration Guide

## Overview

The **ControlPlaneAdapter** provides "drop-in" middleware that wraps the OpenAI SDK to automatically govern LLM tool calls. This allows developers to continue using the standard OpenAI API while benefiting from Agent Control Plane's governance and safety features.

## Key Features

- **Zero Friction**: No changes to existing OpenAI code needed
- **Invisible Governance**: Control plane works behind the scenes
- **Automatic Tool Interception**: Blocks unauthorized tool calls at runtime
- **Full Audit Trail**: Complete logging of all actions and decisions
- **Customizable**: Support for custom tool names and mappings
- **Production Ready**: Callback support, statistics, and error handling

## Quick Start

### Basic Usage

```python
from openai import OpenAI
from agent_control_plane import (
    AgentControlPlane,
    ControlPlaneAdapter,
    ActionType,
    PermissionLevel
)

# 1. Setup control plane
control_plane = AgentControlPlane()

# 2. Create agent with permissions
permissions = {
    ActionType.DATABASE_QUERY: PermissionLevel.READ_ONLY,
    ActionType.FILE_READ: PermissionLevel.READ_ONLY,
    ActionType.FILE_WRITE: PermissionLevel.NONE,  # Blocked!
}
agent_context = control_plane.create_agent("my-agent", permissions)

# 3. Create OpenAI client
client = OpenAI(api_key="your-api-key")

# 4. Wrap with adapter
governed_client = ControlPlaneAdapter(
    control_plane=control_plane,
    agent_context=agent_context,
    original_client=client
)

# 5. Use exactly as you would use OpenAI!
response = governed_client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Query the database and save results to file"}
    ],
    tools=[
        {"type": "function", "function": {"name": "database_query"}},
        {"type": "function", "function": {"name": "write_file"}},
    ]
)

# Tool calls are automatically governed!
# database_query will be allowed
# write_file will be blocked and replaced with "blocked_action"
```

### One-Liner Setup

```python
from agent_control_plane import create_governed_client
from openai import OpenAI

control_plane = AgentControlPlane()
client = OpenAI(api_key="your-api-key")

# One line to create governed client
governed = create_governed_client(
    control_plane=control_plane,
    agent_id="my-agent",
    openai_client=client,
    permissions={
        ActionType.DATABASE_QUERY: PermissionLevel.READ_ONLY
    }
)

# Use immediately
response = governed.chat.completions.create(...)
```

## How It Works

The adapter intercepts LLM responses at the tool call level:

1. **LLM Thinks**: The OpenAI API is called normally
2. **Interception**: Tool calls in the response are intercepted
3. **Governance Check**: Each tool call is validated against agent permissions
4. **Blocking**: Unauthorized tools are replaced with `blocked_action`
5. **Response**: The (possibly modified) response is returned

```
┌─────────────┐
│   Your      │
│   Code      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  ControlPlaneAdapter    │
│  (Drop-in Middleware)   │
└──────┬──────────────────┘
       │
       ├──────► ┌──────────────┐
       │        │  OpenAI API  │
       │        └──────┬───────┘
       │               │
       │               ▼
       │        ┌──────────────┐
       │◄───────│  Response    │
       │        │  with Tools  │
       ▼        └──────────────┘
┌─────────────────────────┐
│  Agent Control Plane    │
│  (Governance Check)     │
└──────┬──────────────────┘
       │
       ▼
  ✅ Allowed
  ❌ Blocked → replaced with "blocked_action"
```

## Tool Name Mapping

The adapter automatically recognizes common tool names:

### Built-in Mappings

```python
# File operations
"read_file" → ActionType.FILE_READ
"write_file" → ActionType.FILE_WRITE

# Code execution
"execute_code" → ActionType.CODE_EXECUTION
"python" → ActionType.CODE_EXECUTION
"bash" → ActionType.CODE_EXECUTION

# Database operations
"database_query" → ActionType.DATABASE_QUERY
"sql_query" → ActionType.DATABASE_QUERY
"database_write" → ActionType.DATABASE_WRITE

# API calls
"api_call" → ActionType.API_CALL
"http_request" → ActionType.API_CALL
```

### Pattern Matching

The adapter also uses pattern matching for flexibility:

- `"get_file"`, `"fetch_document"`, `"load_file"` → FILE_READ
- `"save_file"`, `"create_document"` → FILE_WRITE
- `"run_code"`, `"eval_script"` → CODE_EXECUTION
- `"select_query"`, `"search_database"` → DATABASE_QUERY

### Custom Mappings

For company-specific tool names:

```python
custom_mapping = {
    "company_db_reader": ActionType.DATABASE_QUERY,
    "company_db_writer": ActionType.DATABASE_WRITE,
    "company_file_store": ActionType.FILE_WRITE,
}

governed = ControlPlaneAdapter(
    control_plane=control_plane,
    agent_context=agent_context,
    original_client=client,
    tool_mapping=custom_mapping
)
```

## Advanced Features

### Callbacks for Blocked Actions

Get notified when actions are blocked:

```python
def on_action_blocked(tool_name, tool_args, result):
    print(f"⚠️ ALERT: {tool_name} was blocked!")
    print(f"Reason: {result['error']}")
    # Send to monitoring system, alert security team, etc.

governed = ControlPlaneAdapter(
    control_plane=control_plane,
    agent_context=agent_context,
    original_client=client,
    on_block=on_action_blocked
)
```

### Statistics and Audit Trail

```python
# Get detailed statistics
stats = governed.get_statistics()
print(f"Agent: {stats['agent_id']}")
print(f"Session: {stats['session_id']}")
print(f"Audit entries: {len(stats['control_plane_audit'])}")

# Access control plane audit log
audit_log = control_plane.get_audit_log()
for entry in audit_log:
    print(f"{entry['timestamp']}: {entry['event_type']}")
```

### Adding Tool Mappings Dynamically

```python
governed.add_tool_mapping("my_custom_tool", ActionType.FILE_READ)
```

## Integration Patterns

### Pattern 1: Wrapper for Existing Code

Minimal changes to existing OpenAI code:

```python
# Before
client = OpenAI(api_key="...")
response = client.chat.completions.create(...)

# After (2 lines added)
governed = create_governed_client(control_plane, "agent-1", client, permissions)
response = governed.chat.completions.create(...)  # Same API!
```

### Pattern 2: Factory Function

Create a factory for consistent setup:

```python
def create_agent_client(agent_id, permissions):
    """Factory for governed OpenAI clients"""
    control_plane = AgentControlPlane()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    return create_governed_client(
        control_plane=control_plane,
        agent_id=agent_id,
        openai_client=client,
        permissions=permissions
    )

# Use throughout codebase
agent1 = create_agent_client("agent-1", read_only_permissions)
agent2 = create_agent_client("agent-2", write_permissions)
```

### Pattern 3: Context Manager

For scoped governance:

```python
from contextlib import contextmanager

@contextmanager
def governed_openai(agent_id, permissions):
    control_plane = AgentControlPlane()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    governed = create_governed_client(
        control_plane, agent_id, client, permissions
    )
    
    try:
        yield governed
    finally:
        # Cleanup, save audit logs, etc.
        audit = governed.get_statistics()
        save_audit_log(audit)

# Use with context manager
with governed_openai("agent-1", permissions) as client:
    response = client.chat.completions.create(...)
```

## Production Deployment

### Environment Configuration

```python
import os
from agent_control_plane import AgentControlPlane, FlightRecorder

# Initialize with production settings
control_plane = AgentControlPlane(
    enable_default_policies=True
)

# Setup audit logging to database
flight_recorder = FlightRecorder(db_path="prod_audit.db")
control_plane.kernel.audit_logger = flight_recorder

# Create governed client
governed = create_governed_client(
    control_plane=control_plane,
    agent_id=os.getenv("AGENT_ID"),
    openai_client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
    permissions=load_permissions_from_config()
)
```

### Monitoring and Alerts

```python
def alert_on_security_violation(tool_name, tool_args, result):
    """Send alerts for blocked actions"""
    severity = determine_severity(tool_name, tool_args)
    
    if severity == "high":
        send_pagerduty_alert({
            "tool": tool_name,
            "agent": result.get("agent_id"),
            "reason": result.get("error")
        })
    
    log_to_siem({
        "event": "agent_action_blocked",
        "tool": tool_name,
        "args": tool_args,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })

governed = ControlPlaneAdapter(
    control_plane=control_plane,
    agent_context=agent_context,
    original_client=client,
    on_block=alert_on_security_violation
)
```

### Database Audit Queries

The FlightRecorder uses SQLite with the following schema:

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    tool_args TEXT,
    input_prompt TEXT,
    policy_verdict TEXT NOT NULL,  -- 'allowed', 'blocked', 'shadow', 'error'
    violation_reason TEXT,
    result TEXT,
    execution_time_ms REAL,
    metadata TEXT
);
```

Example queries:

```python
# Query blocked actions in last 24 hours
from datetime import datetime, timedelta
from agent_control_plane import FlightRecorder

recorder = FlightRecorder("audit.db")

yesterday = datetime.now() - timedelta(days=1)
blocked = recorder.query_logs(
    policy_verdict="blocked",
    start_time=yesterday,
    limit=100
)

for entry in blocked:
    print(f"{entry['timestamp']}: {entry['agent_id']} tried {entry['tool_name']}")
    print(f"  Reason: {entry['violation_reason']}")

# Get statistics
stats = recorder.get_statistics()
print(f"Total actions: {stats['total_actions']}")
print(f"Allowed: {stats['by_verdict'].get('allowed', 0)}")
print(f"Blocked: {stats['by_verdict'].get('blocked', 0)}")
```

## Testing

### Unit Tests

```python
import pytest
from agent_control_plane import (
    AgentControlPlane,
    ControlPlaneAdapter,
    ActionType,
    PermissionLevel
)

def test_blocks_unauthorized_action():
    control_plane = AgentControlPlane()
    permissions = {ActionType.FILE_READ: PermissionLevel.READ_ONLY}
    agent_context = control_plane.create_agent("test", permissions)
    
    # Mock OpenAI client that wants to write
    mock_client = create_mock_client_with_write_tool()
    
    governed = ControlPlaneAdapter(
        control_plane, agent_context, mock_client
    )
    
    response = governed.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Write file"}]
    )
    
    # Verify blocked
    assert response.choices[0].message.tool_calls[0].function.name == "blocked_action"
```

### Integration Tests

See `tests/test_adapter.py` for comprehensive test examples.

## Troubleshooting

### Issue: Tool calls not being intercepted

**Symptom**: Tool calls go through without governance checks.

**Solution**: Ensure you're using the governed client:
```python
# Wrong - using original client
response = client.chat.completions.create(...)

# Correct - using governed client
response = governed_client.chat.completions.create(...)
```

### Issue: Unknown tool name

**Symptom**: Log shows "Unknown tool 'xyz', allowing by default"

**Solution**: Add custom mapping:
```python
governed.add_tool_mapping("xyz", ActionType.FILE_READ)
```

### Issue: All tools blocked

**Symptom**: Every tool call is blocked, even valid ones.

**Solution**: Check agent permissions:
```python
print(agent_context.permissions)
# Ensure required ActionTypes have appropriate PermissionLevels
```

### Issue: Audit logs not appearing

**Symptom**: No entries in audit.db

**Solution**: Attach FlightRecorder to kernel:
```python
from agent_control_plane import FlightRecorder

recorder = FlightRecorder("audit.db")
control_plane.kernel.audit_logger = recorder
```

## Performance Considerations

- **Overhead**: The adapter adds minimal overhead (~0.01ms per tool call check)
- **Scaling**: The control plane is stateless and can handle multiple agents
- **Database**: SQLite is suitable for single-server deployments. For distributed systems, consider PostgreSQL.

## Security Best Practices

1. **Principle of Least Privilege**: Grant minimum required permissions
2. **Regular Audits**: Review blocked actions regularly
3. **Alert on Patterns**: Set up alerts for repeated blocks from same agent
4. **Version Control**: Store permission configs in version control
5. **Testing**: Test permission boundaries before production deployment

## Examples

See the following files for complete examples:

- `examples/adapter_demo.py` - Comprehensive demos of all features
- `tests/test_adapter.py` - Test examples showing various scenarios
- `benchmark.py` - Real-world usage in safety benchmarking

## API Reference

### ControlPlaneAdapter

```python
class ControlPlaneAdapter:
    def __init__(
        self,
        control_plane: AgentControlPlane,
        agent_context: AgentContext,
        original_client: Any,
        tool_mapping: Optional[Dict[str, ActionType]] = None,
        on_block: Optional[Callable[[str, Dict, Dict], None]] = None,
        logger: Optional[logging.Logger] = None
    )
```

### create_governed_client

```python
def create_governed_client(
    control_plane: AgentControlPlane,
    agent_id: str,
    openai_client: Any,
    permissions: Optional[Dict[ActionType, PermissionLevel]] = None,
    tool_mapping: Optional[Dict[str, ActionType]] = None
) -> ControlPlaneAdapter
```

## Next Steps

1. Try the examples in `examples/adapter_demo.py`
2. Run the benchmark: `python benchmark.py`
3. Review the tests: `tests/test_adapter.py`
4. Integrate into your application
5. Set up monitoring and alerts
6. Review audit logs regularly

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/imran-siddique/agent-control-plane/issues
- Documentation: https://github.com/imran-siddique/agent-control-plane/tree/main/docs
