# API Reference

## Core Modules

### `agent_os.StatelessKernel`

Lightweight kernel for stateless policy enforcement.

```python
from agent_os import StatelessKernel

kernel = StatelessKernel(policies=["read_only", "no_pii"])
result = await kernel.execute(
    action="database_query",
    params={"query": "SELECT * FROM users"},
    policies=["read_only"],
)
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `policies: list[str]` | — | Create kernel with named policies |
| `execute` | `action: str, params: dict, policies: list[str], agent_id: str` | `ExecutionResult` | Execute an action with policy enforcement |
| `load_policy_yaml` | `yaml_content: str` | `Policy` | Load a YAML policy string |

---

### `agent_os.KernelSpace`

Full kernel with signals, VFS, flight recorder, and agent lifecycle.

```python
from agent_os import KernelSpace, AgentSignal

kernel = KernelSpace(policy_file="policies.yaml")
ctx = kernel.create_agent_context("agent-001")
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `policy_file: str = "strict"` | — | Create kernel (strict/permissive/audit or path to YAML) |
| `create_agent_context` | `agent_id: str` | `AgentContext` | Create execution context for an agent |
| `register` | decorator | — | Register an async function as a governed agent |
| `execute` | `action, params, agent_id, policies` | `ExecutionResult` | Execute with full governance |
| `flight_recorder` | (property) | `FlightRecorder` | Access the audit log |

---

### `agent_control_plane.PolicyEngine`

ABAC-based policy evaluation engine (<5 ms per decision).

```python
from agent_control_plane import PolicyEngine

engine = PolicyEngine()
engine.load_yaml(yaml_content)
decision = engine.evaluate(agent_did="agent-001", context={"action": "read"})
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `load_policy` | `policy: Policy` | — | Register a parsed policy |
| `load_yaml` | `yaml_content: str` | `Policy` | Parse and register a YAML policy |
| `load_json` | `json_content: str` | `Policy` | Parse and register a JSON policy |
| `evaluate` | `agent_did: str, context: dict` | `PolicyDecision` | Evaluate action against all loaded policies |
| `get_policy` | `name: str` | `Policy \| None` | Get a registered policy by name |
| `list_policies` | — | `list[str]` | List all loaded policy names |
| `remove_policy` | `name: str` | `bool` | Remove a policy by name |

#### `PolicyDecision`

| Field | Type | Description |
|-------|------|-------------|
| `allowed` | `bool` | Whether the action is permitted |
| `action` | `str` | `allow`, `deny`, `warn`, `require_approval`, `log` |
| `matched_rule` | `str` | Name of the rule that triggered |
| `policy_name` | `str` | Name of the parent policy |
| `reason` | `str` | Human-readable explanation |
| `rate_limited` | `bool` | True if denied due to rate limit |
| `evaluation_ms` | `float` | Evaluation time in milliseconds |

---

### `agent_os.emk.EpisodicMemory`

Append-only episodic memory with semantic indexing.

```python
from agent_os.emk import EpisodicMemory

memory = EpisodicMemory(max_turns=50, summarize_after=20)
memory.add_turn(conversation_id, user_msg, agent_response)
history = memory.get_history(conversation_id)
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_turn` | `conversation_id, user_msg, response` | — | Record a conversation turn |
| `get_history` | `conversation_id, limit` | `list[dict]` | Retrieve conversation history |
| `search` | `query, top_k` | `list[Episode]` | Semantic search over episodes |
| `compress` | `conversation_id` | `str` | Summarize old turns to save context |

---

### `agent_control_plane.GovernanceEngine`

Compliance framework validation (GDPR, HIPAA, SOC 2, PCI DSS).

```python
from agent_control_plane import GovernanceEngine

gov = GovernanceEngine()
report = gov.validate(agent_config, framework="gdpr")
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate` | `config: dict, framework: str` | `ComplianceReport` | Validate against a compliance framework |
| `list_frameworks` | — | `list[str]` | List available frameworks |
| `get_requirements` | `framework: str` | `list[Requirement]` | Get framework requirements |

---

### `agent_control_plane.ObservabilityEngine`

Prometheus metrics and OpenTelemetry tracing.

```python
from agent_control_plane import ObservabilityEngine

obs = ObservabilityEngine()
obs.record_latency("policy_evaluation", 4.2)
obs.increment_counter("actions_blocked")
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `record_latency` | `metric: str, value_ms: float` | — | Record a latency measurement |
| `increment_counter` | `metric: str, labels: dict` | — | Increment a counter metric |
| `get_metrics` | — | `dict` | Get all current metric values |

---

## CLI Reference

```
agentos init [--template strict|permissive|audit] [--force]
agentos secure [--verify]
agentos audit [--format text|json]
agentos status
agentos check [files...] [--staged] [--ci] [--format text|json]
agentos review <file> [--cmvk] [--models MODEL1,MODEL2]
agentos validate [files...] [--strict]
agentos install-hooks [--force] [--append]
```

See `agentos <command> --help` for detailed usage of each command.

---

## Extensions

### Copilot Extension

Endpoint: `POST /api/copilot`

```bash
curl -X POST https://your-deploy.vercel.app/api/copilot \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"@agentos help"}]}'
```

### MCP Server

```bash
npx agentos-mcp-server
```

Tools: `create_agent`, `list_templates`, `check_compliance`, `run_tests`, `security_audit`, `debug_agent`

See [`extensions/mcp-server/README.md`](../extensions/mcp-server/README.md) for full tool documentation.
