# API Reference

This document provides a comprehensive API reference for the Agent Control Plane.

## Core Classes

### AgentControlPlane

The main interface for the Agent Control Plane.

```python
from agent_control_plane import AgentControlPlane

control_plane = AgentControlPlane()
```

#### Methods

##### `create_agent(agent_id: str, permissions: Dict[ActionType, PermissionLevel]) -> AgentContext`

Create a new agent with specified permissions.

**Parameters:**
- `agent_id` (str): Unique identifier for the agent
- `permissions` (Dict[ActionType, PermissionLevel]): Permission mapping

**Returns:**
- `AgentContext`: Agent context object

**Example:**
```python
from agent_control_plane.agent_kernel import ActionType, PermissionLevel

permissions = {
    ActionType.FILE_READ: PermissionLevel.READ_ONLY,
    ActionType.API_CALL: PermissionLevel.READ_WRITE,
}

agent = control_plane.create_agent("my-agent", permissions)
```

##### `execute_action(agent_context: AgentContext, action_type: ActionType, params: Dict[str, Any]) -> Dict[str, Any]`

Execute an action on behalf of an agent.

**Parameters:**
- `agent_context` (AgentContext): Agent context
- `action_type` (ActionType): Type of action to execute
- `params` (Dict[str, Any]): Action parameters

**Returns:**
- Dict with keys: `success` (bool), `result` (Any), `error` (str), `risk_score` (float)

**Example:**
```python
result = control_plane.execute_action(
    agent,
    ActionType.FILE_READ,
    {"path": "/data/file.txt"}
)

if result["success"]:
    print(result["result"])
else:
    print(result["error"])
```

##### `get_audit_log(agent_id: str) -> List[Dict]`

Get audit log entries for an agent.

**Parameters:**
- `agent_id` (str): Agent identifier

**Returns:**
- List[Dict]: Audit log entries

## Enums

### ActionType

Types of actions an agent can request.

```python
from agent_control_plane.agent_kernel import ActionType

ActionType.CODE_EXECUTION     # Execute code
ActionType.FILE_READ          # Read files
ActionType.FILE_WRITE         # Write files
ActionType.API_CALL           # Make API calls
ActionType.DATABASE_QUERY     # Query database
ActionType.DATABASE_WRITE     # Write to database
ActionType.WORKFLOW_TRIGGER   # Trigger workflows
```

### PermissionLevel

Permission levels for actions.

```python
from agent_control_plane.agent_kernel import PermissionLevel

PermissionLevel.NONE          # No access
PermissionLevel.READ_ONLY     # Read-only access
PermissionLevel.READ_WRITE    # Read and write access
PermissionLevel.ADMIN         # Administrative access
```

### ExecutionStatus

Status of an execution request.

```python
from agent_control_plane.agent_kernel import ExecutionStatus

ExecutionStatus.PENDING       # Request pending
ExecutionStatus.APPROVED      # Request approved
ExecutionStatus.DENIED        # Request denied
ExecutionStatus.EXECUTING     # Currently executing
ExecutionStatus.COMPLETED     # Execution completed
ExecutionStatus.FAILED        # Execution failed
ExecutionStatus.ROLLED_BACK   # Execution rolled back
```

## Policy Engine

### ResourceQuota

Resource quota configuration for an agent.

```python
from agent_control_plane.policy_engine import ResourceQuota

quota = ResourceQuota(
    agent_id="my-agent",
    max_requests_per_minute=60,
    max_requests_per_hour=1000,
    max_execution_time_seconds=300.0,
    max_concurrent_executions=5
)

control_plane.policy_engine.set_quota("my-agent", quota)
```

### RiskPolicy

Risk-based policy configuration.

```python
from agent_control_plane.policy_engine import RiskPolicy

policy = RiskPolicy(
    max_risk_score=0.5,
    require_approval_above=0.7,
    deny_above=0.9
)

control_plane.policy_engine.set_risk_policy("default", policy)
```

## Helper Functions

### `create_read_only_agent(control_plane: AgentControlPlane, agent_id: str) -> AgentContext`

Create an agent with read-only permissions.

```python
from agent_control_plane import create_read_only_agent

agent = create_read_only_agent(control_plane, "reader")
```

### `create_standard_agent(control_plane: AgentControlPlane, agent_id: str) -> AgentContext`

Create an agent with standard permissions (read/write but not admin).

```python
from agent_control_plane import create_standard_agent

agent = create_standard_agent(control_plane, "worker")
```

### `create_admin_agent(control_plane: AgentControlPlane, agent_id: str) -> AgentContext`

Create an agent with administrative permissions.

```python
from agent_control_plane import create_admin_agent

agent = create_admin_agent(control_plane, "admin")
```

## Advanced Features

### Shadow Mode

Enable simulation mode for testing without side effects.

```python
from agent_control_plane.shadow_mode import ShadowModeConfig

config = ShadowModeConfig(
    enabled=True,
    log_reasoning=True
)

control_plane.enable_shadow_mode("agent-id", config)
```

### Mute Agent

Create capability-based agents that return NULL for out-of-scope requests.

```python
from agent_control_plane.mute_agent import create_mute_sql_agent

config = create_mute_sql_agent("sql-agent")
control_plane.enable_mute_agent("sql-agent", config)
```

### Constraint Graphs

Define multi-dimensional context for agents.

```python
from agent_control_plane.constraint_graphs import (
    DataGraph, TemporalGraph, GraphNode, GraphNodeType
)

# Data Graph
data_graph = DataGraph()
data_graph.add_node(GraphNode(
    id="allowed_data",
    node_type=GraphNodeType.FILE,
    metadata={"path": "/data/"}
))

control_plane.set_data_graph("agent-id", data_graph)

# Temporal Graph
from datetime import time

temporal_graph = TemporalGraph()
temporal_graph.set_business_hours(time(9, 0), time(17, 0))

control_plane.set_temporal_graph("agent-id", temporal_graph)
```

## Error Handling

All operations return dictionaries with consistent structure:

```python
result = control_plane.execute_action(agent, action_type, params)

if result["success"]:
    # Operation succeeded
    data = result["result"]
    risk = result.get("risk_score", 0.0)
else:
    # Operation failed
    error = result["error"]
    reason = result.get("reason", "Unknown")
```

## See Also

- [Quick Start Guide](../docs/guides/QUICKSTART.md)
- [Examples](../examples/)
- [Architecture](../docs/architecture/architecture.md)
