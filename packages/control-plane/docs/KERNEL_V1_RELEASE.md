# Agent Control Plane v1.0 - The "Kernel" Release

## 🎯 Overview

Agent Control Plane v1.0 ("The Kernel Release") introduces three major features that transform the control plane from a research prototype into a production-ready governance layer for AI agents:

1. **Async Support** - Non-blocking agent operations for concurrent execution
2. **ABAC (Attribute-Based Access Control)** - Context-aware, condition-based policies
3. **Flight Recorder** - Black box audit logging for compliance and forensics

This release implements the "Linux Kernel for AI Agents" vision - a deterministic runtime layer that enforces safety boundaries before an LLM's intent becomes an action.

## 🚀 What's New

### 1. Async Support

The kernel now supports async/await for non-blocking agent operations:

```python
import asyncio
from agent_control_plane import AgentKernel, PolicyEngine

kernel = AgentKernel(policy_engine=policy)

# Async version for concurrent operations
result = await kernel.intercept_tool_execution_async(
    agent_id="agent-1",
    tool_name="process_data",
    tool_args={"data": "..."}
)

# Sync version for backward compatibility
result = kernel.intercept_tool_execution(
    agent_id="agent-1",
    tool_name="process_data",
    tool_args={"data": "..."}
)
```

**Benefits:**
- Multiple agents can operate concurrently
- Non-blocking I/O for better performance
- Backward compatible with existing sync code

### 2. ABAC (Attribute-Based Access Control)

Move beyond role-based access control to context-aware policies:

```python
from agent_control_plane import PolicyEngine, Condition, ConditionalPermission

policy = PolicyEngine()

# Define conditions
conditions = [
    Condition("user_status", "eq", "verified"),  # User must be verified
    Condition("args.amount", "lt", 1000)          # Amount must be under $1000
]

# Create conditional permission
permission = ConditionalPermission(
    tool_name="refund_user",
    conditions=conditions,
    require_all=True  # All conditions must be met (AND logic)
)

# Add to policy
policy.add_conditional_permission("finance-agent", permission)

# Set agent context
policy.set_agent_context("finance-agent", {"user_status": "verified"})

# Now the agent can only refund if BOTH conditions are met
```

**Supported Operators:**
- `eq` - Equal to
- `ne` - Not equal to
- `gt` - Greater than
- `lt` - Less than
- `gte` - Greater than or equal to
- `lte` - Less than or equal to
- `in` - Value in list
- `not_in` - Value not in list
- `contains` - String contains substring

**Nested Attributes:**
```python
# Access nested values with dot notation
Condition("args.payment.amount", "lt", 1000)
Condition("context.user.role", "in", ["admin", "manager"])
```

### 3. Flight Recorder (Black Box Audit Logging)

Complete audit trail for compliance and forensic analysis:

```python
from agent_control_plane import AgentKernel, FlightRecorder

# Create flight recorder
recorder = FlightRecorder("flight_recorder.db")

# Attach to kernel
kernel = AgentKernel(policy_engine=policy, audit_logger=recorder)

# All actions are automatically logged
kernel.intercept_tool_execution(
    agent_id="finance-agent",
    tool_name="transfer_funds",
    tool_args={"amount": 500, "to": "account-123"},
    input_prompt="User: Transfer $500 to my savings account"
)

# Query logs
logs = recorder.query_logs(
    agent_id="finance-agent",
    policy_verdict="blocked",
    limit=10
)

# Get statistics
stats = recorder.get_statistics()
print(f"Total actions: {stats['total_actions']}")
print(f"Blocked: {stats['by_verdict']['blocked']}")
```

**What Gets Logged:**
- `trace_id` - Unique identifier for each action
- `timestamp` - When the action was attempted
- `agent_id` - Which agent attempted the action
- `tool_name` - What tool was called
- `tool_args` - Arguments passed to the tool
- `input_prompt` - The original user/agent prompt (optional)
- `policy_verdict` - allowed, blocked, shadow, error
- `violation_reason` - Why the action was blocked (if applicable)
- `result` - What happened (for allowed actions)
- `execution_time_ms` - How long it took

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      LLM / Agent                            │
│                  (Generates Intent)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Kernel                              │
│              (The Checkpoint)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. Start Trace (Flight Recorder)                    │   │
│  │ 2. Check Policy (RBAC + ABAC)                       │   │
│  │ 3. Validate Arguments (Dangerous patterns)          │   │
│  │ 4. Log Decision (Blocked/Allowed/Shadow)            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    ✅ Allow    ❌ Block    🔍 Shadow
```

## 🔒 Security Model

The Kernel Release implements a "Scale by Subtraction" security model:

1. **Default Deny**: Everything is blocked unless explicitly allowed
2. **Layered Checks**: 
   - Role-based (Is tool allowed for this role?)
   - Condition-based (Are conditions met?)
   - Argument-based (Are arguments safe?)
3. **Mute Protocol**: Blocked actions return system errors, not polite refusals
4. **Audit Everything**: All decisions are logged for forensic analysis

## 📝 Examples

### Example 1: Financial Agent with Limits

```python
from agent_control_plane import (
    AgentKernel, PolicyEngine, Condition, 
    ConditionalPermission, FlightRecorder
)

# Setup
recorder = FlightRecorder("financial_audit.db")
policy = PolicyEngine()

# Finance agent can refund IF:
# - Customer is verified AND
# - Amount is under $1000
conditions = [
    Condition("customer_verified", "eq", True),
    Condition("args.amount", "lte", 1000)
]
permission = ConditionalPermission("process_refund", conditions)
policy.add_conditional_permission("finance-agent", permission)

kernel = AgentKernel(policy_engine=policy, audit_logger=recorder)

# Set customer context
policy.set_agent_context("finance-agent", {"customer_verified": True})

# Small refund - ALLOWED
result = kernel.intercept_tool_execution(
    "finance-agent", "process_refund", {"amount": 500}
)
# Returns: None (allowed)

# Large refund - BLOCKED
result = kernel.intercept_tool_execution(
    "finance-agent", "process_refund", {"amount": 1500}
)
# Returns: {"status": "blocked", "error": "...", "mute": True}
```

### Example 2: Time-Based Access Control

```python
from datetime import datetime

# Agent can only execute trades during business hours
hour = datetime.now().hour
is_business_hours = 9 <= hour <= 17

conditions = [
    Condition("context.business_hours", "eq", True)
]
permission = ConditionalPermission("execute_trade", conditions)
policy.add_conditional_permission("trading-agent", permission)

# Set context
policy.set_agent_context("trading-agent", {
    "business_hours": is_business_hours
})
```

### Example 3: Multi-Tier Approval

```python
# Small purchases: Any agent
# Medium purchases: Supervisor approval required
# Large purchases: Admin approval required

# Small purchases (< $100)
small_purchase = ConditionalPermission(
    "make_purchase",
    [Condition("args.amount", "lt", 100)],
)
policy.add_conditional_permission("agent", small_purchase)

# Medium purchases ($100-$1000) - require supervisor
medium_purchase = ConditionalPermission(
    "make_purchase",
    [
        Condition("args.amount", "gte", 100),
        Condition("args.amount", "lt", 1000),
        Condition("supervisor_approved", "eq", True)
    ],
)
policy.add_conditional_permission("agent", medium_purchase)
```

## 🧪 Testing

The release includes comprehensive test coverage:

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/test_kernel_interception.py  # Original tests (15 tests)
pytest tests/test_new_features.py         # New feature tests (23 tests)

# Total: 86 tests passing
```

## 🎮 Demo

Run the interactive demo to see all features in action:

```bash
python examples/kernel_v1_demo.py
```

This demo showcases:
1. Async concurrent agent operations
2. ABAC with conditional permissions
3. Flight Recorder audit logging
4. Real-world e-commerce scenario

## 📚 API Reference

### AgentKernel

```python
class AgentKernel:
    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        shadow_mode: bool = False,
        audit_logger: Optional[FlightRecorder] = None
    )
    
    async def intercept_tool_execution_async(
        self,
        agent_id: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        input_prompt: Optional[str] = None
    ) -> Dict[str, Any]
    
    def intercept_tool_execution(
        self,
        agent_id: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        input_prompt: Optional[str] = None
    ) -> Optional[Dict[str, Any]]
```

### PolicyEngine

```python
class PolicyEngine:
    def add_conditional_permission(
        self,
        agent_role: str,
        permission: ConditionalPermission
    )
    
    def set_agent_context(
        self,
        agent_role: str,
        context: Dict[str, Any]
    )
    
    def update_agent_context(
        self,
        agent_role: str,
        updates: Dict[str, Any]
    )
```

### FlightRecorder

```python
class FlightRecorder:
    def __init__(self, db_path: str = "flight_recorder.db")
    
    def start_trace(
        self,
        agent_id: str,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        input_prompt: Optional[str] = None
    ) -> str
    
    def log_violation(self, trace_id: str, violation_reason: str)
    
    def log_success(
        self,
        trace_id: str,
        result: Optional[Any] = None,
        execution_time_ms: Optional[float] = None
    )
    
    def query_logs(
        self,
        agent_id: Optional[str] = None,
        policy_verdict: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> list
    
    def get_statistics(self) -> Dict[str, Any]
```

## 🔄 Migration Guide

### From v0.x to v1.0

**1. Async Support (Optional)**

If you want to use async, update your code:

```python
# Before (still works)
result = kernel.intercept_tool_execution(agent_id, tool_name, args)

# After (for async)
result = await kernel.intercept_tool_execution_async(agent_id, tool_name, args)
```

**2. ABAC (New Feature)**

Add conditional permissions for context-aware policies:

```python
# Before: Simple role-based
policy.add_constraint("agent", ["read", "write"])

# After: Add conditions for fine-grained control
permission = ConditionalPermission(
    "write",
    [Condition("args.path", "not_in", ["/etc/", "/sys/"])]
)
policy.add_conditional_permission("agent", permission)
```

**3. Flight Recorder (Recommended)**

Enable audit logging for compliance:

```python
# Add to your initialization
from agent_control_plane import FlightRecorder

recorder = FlightRecorder("audit.db")
kernel = AgentKernel(policy_engine=policy, audit_logger=recorder)

# No other changes needed - logging is automatic
```

## 🛣️ Roadmap

Future enhancements planned:

- **v1.1**: OpenAI Tool Calls Integration - Direct interception of ChatCompletion tool_calls
- **v1.2**: Policy Templates - Pre-built policies for common scenarios
- **v1.3**: Real-time Monitoring Dashboard - Web UI for flight recorder data
- **v1.4**: Multi-Agent Coordination - Policies that span multiple agents

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.

## 📧 Support

- GitHub Issues: https://github.com/imran-siddique/agent-control-plane/issues
- Documentation: https://github.com/imran-siddique/agent-control-plane/tree/main/docs

---

**Built with ❤️ for the AI Safety Community**
