# LangChain Integration Guide

## Overview

The SCAK LangChain integration provides three core components that enable self-correcting capabilities for LangChain agents:

1. **SCAKMemory**: Dynamic memory adapter for SCAK's 3-Tier memory hierarchy
2. **SCAKCallbackHandler**: Background auditor for detecting agent "laziness"
3. **SelfCorrectingRunnable**: Runtime guard for automatic failure handling

## Installation

```bash
# Install SCAK with LangChain support
pip install scak[langchain]

# Or install dependencies separately
pip install scak langchain langchain-core
```

## Quick Start

### Basic Integration (5 lines of code)

Add SCAK monitoring to an existing LangChain agent:

```python
from langchain.agents import AgentExecutor
from scak.integrations.langchain import SCAKCallbackHandler

# Your existing agent
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Add SCAK monitoring
scak_handler = SCAKCallbackHandler()
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[scak_handler]  # Just add this line!
)
```

### Full Integration

For maximum reliability, use all SCAK components:

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from scak.integrations.langchain import (
    SCAKMemory,
    SCAKCallbackHandler,
    SelfCorrectingRunnable
)

# 1. Initialize SCAK components
scak_memory = SCAKMemory()
scak_handler = SCAKCallbackHandler()

# 2. Create prompt with memory placeholder
prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_patch}\n\nYou are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 3. Create agent
llm = ChatOpenAI(model="gpt-4o")
agent = create_openai_tools_agent(llm, tools, prompt)

# 4. Create executor with SCAK
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=scak_memory,
    callbacks=[scak_handler],
    verbose=True
)

# 5. Wrap with self-correction
correcting_agent = SelfCorrectingRunnable(agent_executor)

# 6. Use normally
result = correcting_agent.invoke({"input": "Find error logs"})
```

### Convenience Function

The quickest way to add SCAK:

```python
from scak.integrations.langchain import create_scak_agent

# Your base agent
base_agent = AgentExecutor(agent=agent, tools=tools)

# Add SCAK in one line
scak_agent = create_scak_agent(base_agent)

# Use normally
result = scak_agent.invoke({"input": "Do something"})
```

## Component Details

### 1. SCAKMemory

Dynamic memory adapter that implements SCAK's 3-Tier hierarchy:

- **Tier 1 (Kernel)**: Safety-critical rules always active
- **Tier 2 (Skill Cache)**: Tool-specific rules injected conditionally
- **Tier 3 (Archive)**: Long-tail wisdom retrieved on-demand

**Key Features:**
- Reduces context size by 40-60% compared to naive memory
- Only injects relevant rules based on active tools
- Semantic search for complex queries
- Compatible with LangChain's `BaseMemory` interface

**Usage:**

```python
from scak.integrations.langchain import SCAKMemory

# Initialize
memory = SCAKMemory()

# Use in prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_patch}"),  # Dynamic context injected here
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}"),
])

# Use in agent
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory  # SCAK memory
)
```

**Configuration:**

```python
from src.kernel.memory import MemoryController

# Customize memory controller
controller = MemoryController(
    vector_store=my_vector_db,
    redis_cache=my_redis_client
)

memory = SCAKMemory(
    controller=controller,
    memory_key="chat_history",
    system_patch_key="system_context"
)
```

### 2. SCAKCallbackHandler

Background auditor that detects agent "laziness" using differential auditing.

**Key Features:**
- Detects "give-up signals" (e.g., "No data found", "Cannot answer")
- Triggers Shadow Teacher audits asynchronously (non-blocking)
- Audits only 5-10% of interactions (differential auditing)
- Emits structured telemetry for offline analysis

**Usage:**

```python
from scak.integrations.langchain import SCAKCallbackHandler

# Initialize
handler = SCAKCallbackHandler(agent_id="my_agent")

# Add to agent
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[handler]
)

# Check statistics
print(f"Give-up signals detected: {handler.give_up_count}")
print(f"Audits triggered: {handler.audit_count}")
```

**Detected Give-Up Signals:**
- "no data found"
- "cannot answer"
- "no results"
- "not available"
- "insufficient info"
- "i couldn't find"
- "i was unable to"

**Configuration:**

```python
from src.kernel.auditor import CompletenessAuditor

# Customize auditor
auditor = CompletenessAuditor(teacher_model="o1-preview")

handler = SCAKCallbackHandler(
    auditor=auditor,
    agent_id="production_agent"
)
```

### 3. SelfCorrectingRunnable

Runtime guard that intercepts failures and applies corrections automatically.

**Key Features:**
- Transparent wrapping (works with any `Runnable`)
- Smart triage: SYNC_JIT for critical, ASYNC_BATCH for non-critical
- Auto-retry with corrected context
- Structured telemetry for all corrections

**Usage:**

```python
from scak.integrations.langchain import SelfCorrectingRunnable

# Wrap your agent
base_agent = AgentExecutor(agent=agent, tools=tools)
correcting_agent = SelfCorrectingRunnable(base_agent)

# Use normally - failures are handled automatically
result = correcting_agent.invoke({"input": "Do something risky"})

# Check statistics
print(f"Failures detected: {correcting_agent.failure_count}")
print(f"Auto-corrections: {correcting_agent.correction_count}")
```

**Correction Strategies:**

The triage engine decides between two strategies:

1. **SYNC_JIT** (Synchronous, Just-In-Time):
   - For critical operations (delete, payment, etc.)
   - Blocks user while correction is applied
   - Retries immediately with corrected context

2. **ASYNC_BATCH** (Asynchronous, Background):
   - For non-critical operations (read, query, etc.)
   - Returns error quickly to user
   - Queues for background correction

**Configuration:**

```python
from src.kernel.triage import FailureTriage
from src.kernel.patcher import AgentPatcher

# Customize triage
triage = FailureTriage(config={
    "critical_tools": ["delete_user", "process_payment"],
    "high_effort_keywords": ["critical", "urgent", "must"]
})

# Customize patcher
patcher = AgentPatcher()

# Create runnable
correcting_agent = SelfCorrectingRunnable(
    agent=base_agent,
    triage=triage,
    patcher=patcher,
    agent_id="production_agent"
)
```

## Architecture

### Dual-Loop Architecture

SCAK implements a two-loop architecture aligned with LangChain's execution model:

```
┌─────────────────────────────────────────────────────────────┐
│                      LangChain Agent                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Loop 1: Runtime Safety (SelfCorrectingRunnable)      │  │
│  │                                                       │  │
│  │  User Input → Triage → Execute → Error?             │  │
│  │                 ↓                    ↓               │  │
│  │           SYNC_JIT         Apply Patch → Retry      │  │
│  │           ASYNC_BATCH      Queue → Background       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Loop 2: Quality/Efficiency (SCAKCallbackHandler)     │  │
│  │                                                       │  │
│  │  Agent Finish → Give-up Signal? → Shadow Teacher    │  │
│  │                       ↓                  ↓           │  │
│  │                   Audit Async    Generate Patch     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Memory: 3-Tier Hierarchy (SCAKMemory)                │  │
│  │                                                       │  │
│  │  Tier 1: Kernel (Always Active)                     │  │
│  │  Tier 2: Skill Cache (Conditional)                  │  │
│  │  Tier 3: Archive (On-Demand)                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

| SCAK Component | LangChain Equivalent | Integration Method |
|----------------|---------------------|-------------------|
| Loop 2: Alignment | `BaseCallbackHandler` | `SCAKCallbackHandler` listens to `on_agent_finish` |
| Memory Hierarchy | `BaseChatMemory` | `SCAKMemory` implements `load_memory_variables` |
| Loop 1: Runtime | `RunnableBinding` | `SelfCorrectingRunnable` wraps agent execution |

## Best Practices

### 1. Start with Monitoring Only

Begin by adding just the `SCAKCallbackHandler` to observe agent behavior:

```python
# Phase 1: Observe
handler = SCAKCallbackHandler()
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[handler]
)

# Run for a week and analyze telemetry
```

### 2. Add Memory for Context Efficiency

Once you understand the patterns, add `SCAKMemory` to reduce context size:

```python
# Phase 2: Optimize context
memory = SCAKMemory()
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    callbacks=[handler]
)
```

### 3. Enable Self-Correction for Production

Finally, wrap with `SelfCorrectingRunnable` for full reliability:

```python
# Phase 3: Self-healing
correcting_agent = SelfCorrectingRunnable(agent_executor)
```

### 4. Monitor Telemetry

SCAK emits structured JSON logs. Aggregate them for insights:

```python
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# Telemetry will be emitted as JSON
# Parse with your log aggregation tool (CloudWatch, Datadog, etc.)
```

### 5. Customize for Your Domain

Configure components based on your specific needs:

```python
# Define critical tools for your domain
triage = FailureTriage(config={
    "critical_tools": [
        "process_payment",
        "delete_user",
        "modify_database"
    ]
})

# Use stronger teacher model
auditor = CompletenessAuditor(teacher_model="o1-preview")

# Create custom memory tiers
from src.kernel.schemas import Lesson, MemoryTier, PatchRequest

# Add domain-specific kernel rules
controller = MemoryController()
# ... add your rules
```

## Performance Considerations

### Latency Impact

| Component | Added Latency | When |
|-----------|--------------|------|
| SCAKMemory | ~10-50ms | Per request (memory load) |
| SCAKCallbackHandler | ~0ms | Per request (async audit) |
| SelfCorrectingRunnable | ~0ms | Success case |
| SelfCorrectingRunnable | +50-500ms | SYNC_JIT correction |

### Cost Optimization

- **Differential Auditing**: Only 5-10% of interactions trigger expensive Shadow Teacher
- **Conditional Injection**: Tier 2 rules only loaded when tools are active
- **Semantic Purge**: Type A patches purged on model upgrade (40-60% reduction)

## Troubleshooting

### LangChain Import Errors

```python
# If you get: ImportError: cannot import name 'BaseMemory'
# Install langchain-core:
pip install langchain-core

# If you get: No module named 'langchain'
# Install langchain:
pip install langchain
```

### Memory Not Working

```python
# Ensure your prompt includes the memory placeholders:
prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_patch}"),  # Required for SCAK context
    MessagesPlaceholder(variable_name="history"),  # Required for chat history
    ("user", "{input}"),
])
```

### Callbacks Not Firing

```python
# Ensure callbacks are passed to invoke():
result = agent_executor.invoke(
    {"input": "Do something"},
    config={"callbacks": [scak_handler]}  # Pass here if not in constructor
)
```

### Self-Correction Not Working

```python
# Check if errors are being caught:
try:
    result = correcting_agent.invoke({"input": "..."})
except Exception as e:
    # If error propagates, check triage config
    print(f"Triage decision: {correcting_agent.triage.decide_strategy(...)}")
```

## Examples

See `examples/langchain_integration_example.py` for complete working examples:

1. Basic Integration
2. Full Integration (all components)
3. Convenience Function

Run with:

```bash
export OPENAI_API_KEY='your-key'
python examples/langchain_integration_example.py
```

## API Reference

### SCAKMemory

```python
SCAKMemory(
    memory_key: str = "history",
    system_patch_key: str = "system_patch",
    controller: Optional[MemoryController] = None,
    return_messages: bool = True
)
```

**Methods:**
- `load_memory_variables(inputs: Dict) -> Dict`: Load memory for agent
- `save_context(inputs: Dict, outputs: Dict) -> None`: Save conversation
- `clear() -> None`: Clear chat history

### SCAKCallbackHandler

```python
SCAKCallbackHandler(
    auditor: Optional[CompletenessAuditor] = None,
    agent_id: str = "langchain_agent"
)
```

**Methods:**
- `is_give_up_signal(response: str) -> bool`: Check for give-up pattern
- `on_agent_finish(finish: AgentFinish, **kwargs) -> None`: Async callback

**Attributes:**
- `total_executions: int`: Total agent executions
- `give_up_count: int`: Give-up signals detected
- `audit_count: int`: Shadow Teacher audits triggered

### SelfCorrectingRunnable

```python
SelfCorrectingRunnable(
    agent: Runnable,
    triage: Optional[FailureTriage] = None,
    patcher: Optional[AgentPatcher] = None,
    agent_id: str = "langchain_agent"
)
```

**Methods:**
- `invoke(input: Dict, config: Optional[RunnableConfig]) -> Dict`: Execute agent

**Attributes:**
- `execution_count: int`: Total executions
- `failure_count: int`: Failures detected
- `correction_count: int`: Auto-corrections applied

### create_scak_agent

```python
create_scak_agent(
    base_agent: Runnable,
    memory: Optional[SCAKMemory] = None,
    callback_handler: Optional[SCAKCallbackHandler] = None,
    enable_correction: bool = True,
    agent_id: str = "langchain_agent"
) -> Union[Runnable, SelfCorrectingRunnable]
```

Convenience function to wrap a base agent with SCAK components.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

MIT License. See [LICENSE](../LICENSE).

## Support

- **Documentation**: https://github.com/imran-siddique/self-correcting-agent-kernel/wiki
- **Issues**: https://github.com/imran-siddique/self-correcting-agent-kernel/issues
- **Discussions**: https://github.com/imran-siddique/self-correcting-agent-kernel/discussions
