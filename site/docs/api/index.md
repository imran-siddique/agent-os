---
layout: default
title: API Reference
parent: Documentation
nav_order: 8
has_children: true
permalink: /docs/api/
description: "Complete API reference for Agent OS - KernelSpace, policies, signals, memory, and modules."
---

# API Reference
{: .fs-9 }

Complete reference for all Agent OS classes and functions.
{: .fs-6 .fw-300 }

---

## Core Classes

### KernelSpace

The main entry point for Agent OS.

```python
from agent_os import KernelSpace

kernel = KernelSpace(
    policy: str | Policy = "strict",
    audit_level: str = "standard",
    metrics_port: int | None = None,
    tracing: bool = False
)
```

#### Parameters

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `policy` | `str \| Policy` | `"strict"` | Policy mode or Policy object |
| `audit_level` | `str` | `"standard"` | `"minimal"`, `"standard"`, or `"comprehensive"` |
| `metrics_port` | `int \| None` | `None` | Port for Prometheus metrics (None = disabled) |
| `tracing` | `bool` | `False` | Enable OpenTelemetry tracing |

#### Methods

##### `register(func)`

Decorator to register a function with the kernel.

```python
@kernel.register
async def my_agent(task: str) -> str:
    return f"Processed: {task}"
```

##### `execute(func, *args, **kwargs)`

Execute a registered function with governance.

```python
result = await kernel.execute(my_agent, "task")
```

**Returns**: Result of the function or raises `PolicyViolation`.

##### `signal(agent_id, signal)`

Send a signal to a running agent.

```python
from agent_os import AgentSignal

kernel.signal("agent-001", AgentSignal.SIGSTOP)  # Pause
kernel.signal("agent-001", AgentSignal.SIGCONT)  # Resume
kernel.signal("agent-001", AgentSignal.SIGKILL)  # Terminate
```

##### `checkpoint(agent_id)`

Create a checkpoint of agent state.

```python
checkpoint_id = kernel.checkpoint("agent-001")
```

##### `restore(checkpoint_id)`

Restore agent to a previous checkpoint.

```python
kernel.restore(checkpoint_id)
```

---

### Policy

Represents a governance policy.

```python
from agent_os.policies import Policy, Rule, load_policy

# From file
policy = load_policy("my-policy.yaml")

# Programmatic
policy = Policy(
    name="My Policy",
    mode="strict",
    rules=[
        Rule(action="shell", effect="deny"),
        Rule(action="file_write", resource="/tmp/*", effect="allow"),
    ]
)
```

#### Attributes

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `name` | `str` | Policy name |
| `mode` | `str` | `"strict"`, `"permissive"`, or `"audit"` |
| `rules` | `list[Rule]` | List of policy rules |

#### Methods

##### `evaluate(action, context)`

Evaluate an action against the policy.

```python
decision = policy.evaluate(
    action="file_write",
    context={"resource": "/prod/config.yaml"}
)

print(decision.allowed)  # False
print(decision.reason)   # "Production writes blocked"
```

##### `explain(action, context)`

Get detailed explanation of policy decision.

```python
explanation = policy.explain(action="sql", context={"query": "DROP TABLE users"})
print(explanation.matching_rule)
print(explanation.evaluation_path)
```

---

### Rule

A single policy rule.

```python
from agent_os.policies import Rule

rule = Rule(
    action: str,                    # Action type
    resource: str | None = None,    # Resource pattern (optional)
    effect: str = "deny",           # "allow" or "deny"
    conditions: list[dict] = [],    # Additional conditions
    reason: str | None = None,      # Human-readable reason
    alert: str | None = None        # Alert severity
)
```

---

## Signals

### AgentSignal

Enumeration of supported signals.

```python
from agent_os import AgentSignal

AgentSignal.SIGKILL   # Immediate termination (non-catchable)
AgentSignal.SIGSTOP   # Pause execution
AgentSignal.SIGCONT   # Resume execution
AgentSignal.SIGTERM   # Graceful termination request
AgentSignal.SIGUSR1   # User-defined signal 1
AgentSignal.SIGUSR2   # User-defined signal 2
```

### Signal Handlers

Register custom signal handlers:

```python
@kernel.on_signal(AgentSignal.SIGUSR1)
async def handle_usr1(agent_id: str, context: dict):
    print(f"Agent {agent_id} received USR1")
```

---

## Memory (EMK)

### Episode

An immutable memory episode.

```python
from agent_os.emk import Episode

episode = Episode(
    goal: str,              # What the agent was trying to do
    action: str,            # What action was taken
    result: str,            # What happened
    reflection: str = "",   # Agent's reflection
    metadata: dict = {}     # Additional metadata
)
```

### MemoryStore

Storage backend for episodes.

```python
from agent_os.emk import MemoryStore, FileAdapter, PostgresAdapter

# File-based
store = MemoryStore(FileAdapter("memory.jsonl"))

# PostgreSQL
store = MemoryStore(PostgresAdapter(connection_string))

# Store episode
store.store(episode)

# Retrieve by semantic search
episodes = store.search("query about database operations", limit=5)

# Retrieve by time range
episodes = store.query(
    start_time=datetime(2026, 1, 1),
    end_time=datetime(2026, 1, 31)
)
```

---

## Verification (CMVK)

### CMVKVerifier

Cross-model verification.

```python
from agent_os.cmvk import CMVKVerifier

verifier = CMVKVerifier(
    models=["gpt-4", "claude-3", "gemini-pro"],
    threshold=0.8,  # 80% agreement required
    drift_tolerance=0.1
)

# Verify a response
result = await verifier.verify(
    prompt="What is the capital of France?",
    response="Paris is the capital of France."
)

print(result.verified)      # True
print(result.consensus)     # 1.0
print(result.drift_score)   # 0.0
```

### Drift Detection

```python
from agent_os.cmvk import detect_drift

score = detect_drift(
    original="The capital of France is Paris.",
    response="Paris is the capital city of France."
)

print(score.semantic_drift)   # 0.02
print(score.factual_drift)    # 0.0
print(score.is_hallucination) # False
```

---

## Trust (IATP)

### AgentIdentity

Create and manage agent identities.

```python
from agent_os.iatp import AgentIdentity

identity = AgentIdentity.create(
    agent_id="agent-001",
    name="Data Analyst",
    capabilities=["sql_read", "file_read"]
)

# Export public key
public_key = identity.public_key_pem()
```

### SignedMessage

Sign and verify messages between agents.

```python
from agent_os.iatp import SignedMessage

# Sign
message = SignedMessage.create(
    sender=sender_identity,
    recipient_id="agent-002",
    content={"type": "request", "data": {...}}
)

# Verify
result = message.verify(sender_public_key)
print(result.valid)
print(result.timestamp)
```

### TrustRegistry

Manage agent trust relationships.

```python
from agent_os.iatp import TrustRegistry, TrustLevel

registry = TrustRegistry()

# Register agent
registry.register(identity, TrustLevel.HIGH)

# Check trust
level = registry.get_trust_level("agent-001")

# Revoke
registry.revoke("agent-001", reason="Suspicious behavior")
```

---

## Observability

### Metrics

```python
from agent_os.observability import enable_metrics, MetricsConfig

config = MetricsConfig(
    port=9090,
    namespace="agent_os",
    include_process_metrics=True
)

enable_metrics(config)
```

### Tracing

```python
from agent_os.observability import enable_tracing, TracingConfig

config = TracingConfig(
    service_name="my-service",
    exporter="jaeger",
    endpoint="http://localhost:14268/api/traces"
)

enable_tracing(config)
```

### Logging

```python
from agent_os.observability import configure_logging, LoggingConfig

config = LoggingConfig(
    level="INFO",
    format="json",
    include_trace_ids=True
)

configure_logging(config)
```

---

## Exceptions

### PolicyViolation

Raised when an action violates policy.

```python
from agent_os.exceptions import PolicyViolation

try:
    await kernel.execute(agent, "delete all files")
except PolicyViolation as e:
    print(e.action)      # "file_delete"
    print(e.reason)      # "File deletion blocked"
    print(e.rule_id)     # "rule-005"
```

### SignalInterrupt

Raised when agent receives a termination signal.

```python
from agent_os.exceptions import SignalInterrupt

try:
    await kernel.execute(agent, task)
except SignalInterrupt as e:
    print(e.signal)      # AgentSignal.SIGKILL
    print(e.source)      # "policy_violation"
```

### VerificationFailed

Raised when CMVK verification fails.

```python
from agent_os.exceptions import VerificationFailed

try:
    result = await verifier.verify(prompt, response)
except VerificationFailed as e:
    print(e.drift_score)
    print(e.model_responses)
```

---

## Type Hints

All Agent OS APIs are fully typed. Use with mypy or Pyright:

```python
from agent_os import KernelSpace
from agent_os.types import AgentContext, PolicyDecision

async def my_agent(task: str, context: AgentContext) -> str:
    ...

decision: PolicyDecision = policy.evaluate(action, context)
```

---

## Next Steps

- [Quickstart Tutorial](/docs/tutorials/quickstart/) — Get started
- [Policy Reference](/docs/policies/) — Define governance rules
- [Module Documentation](/docs/modules/) — Deep dive into modules
