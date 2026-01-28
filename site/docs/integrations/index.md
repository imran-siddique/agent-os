---
layout: default
title: Integrations
parent: Documentation
nav_order: 7
has_children: true
permalink: /docs/integrations/
description: "Integrate Agent OS with LangChain, CrewAI, AutoGen, OpenAI Assistants, and more."
---

# Framework Integrations
{: .fs-9 }

Agent OS wraps existing frameworks—use it with what you already have.
{: .fs-6 .fw-300 }

---

## Overview

Agent OS is **not** a replacement for your agent framework. It's a governance layer that sits between your agents and their actions.

<div class="mermaid">
graph LR
    A[Your Code] --> B[LangChain/CrewAI/etc]
    B --> C[Agent OS Kernel]
    C --> D{Policy Check}
    D -->|Allow| E[Execute Action]
    D -->|Deny| F[Block + Log]
</div>

---

## Quick Integration Table

| Framework | Integration | Install |
|:----------|:------------|:--------|
| **LangChain** | `LangChainKernel().wrap(chain)` | `pip install agent-os[langchain]` |
| **CrewAI** | `CrewAIKernel().wrap(crew)` | `pip install agent-os[crewai]` |
| **OpenAI Assistants** | `OpenAIKernel().wrap_assistant(asst)` | `pip install agent-os[openai]` |
| **Semantic Kernel** | `SemanticKernelWrapper().wrap(sk)` | `pip install agent-os[semantic-kernel]` |
| **AutoGen** | `AutoGenKernel().wrap(agents)` | `pip install agent-os[autogen]` |
| **Claude/Anthropic** | `AnthropicKernel().wrap(client)` | `pip install agent-os[anthropic]` |

---

## LangChain

### Basic Integration

```python
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from agent_os.integrations import LangChainKernel

# Create your LangChain agent as usual
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_functions_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# Wrap with Agent OS
kernel = LangChainKernel(policy="strict")
governed_executor = kernel.wrap(executor)

# Run - all tool calls go through policy engine
result = governed_executor.invoke({"input": "Query the database"})
```

### Tool-Level Governance

```python
from agent_os.integrations import govern_tool

@govern_tool(policy="strict")
def query_database(sql: str) -> str:
    """Execute SQL query."""
    # Kernel checks SQL before execution
    return db.execute(sql)

# Use governed tool in LangChain
tools = [query_database]
```

### Chain Governance

```python
from langchain.chains import LLMChain
from agent_os.integrations import govern_chain

chain = LLMChain(llm=llm, prompt=prompt)
governed_chain = govern_chain(chain, policy="strict")

# All chain invocations are policy-checked
result = governed_chain.invoke({"input": "..."})
```

---

## CrewAI

### Full Crew Governance

```python
from crewai import Crew, Agent, Task
from agent_os.integrations import CrewAIKernel

# Create your crew as usual
researcher = Agent(role="Researcher", ...)
writer = Agent(role="Writer", ...)

task = Task(description="Research and write about...", agent=researcher)
crew = Crew(agents=[researcher, writer], tasks=[task])

# Wrap entire crew
kernel = CrewAIKernel(policy="strict")
governed_crew = kernel.wrap(crew)

# Run - all agent actions go through kernel
result = governed_crew.kickoff()
```

### Per-Agent Policies

```python
kernel = CrewAIKernel(
    default_policy="strict",
    agent_policies={
        "Researcher": "permissive",  # More freedom for research
        "Writer": "strict"           # Strict for production content
    }
)
```

### Task-Level Control

```python
from agent_os.integrations import govern_task

@govern_task(
    policy="strict",
    max_iterations=10,
    timeout_seconds=300
)
def research_task(topic: str) -> str:
    # Task execution with governance
    pass
```

---

## OpenAI Assistants API

### Assistant Governance

```python
from openai import OpenAI
from agent_os.integrations import OpenAIKernel

client = OpenAI()
kernel = OpenAIKernel(policy="strict")

# Wrap the client
governed_client = kernel.wrap(client)

# Create assistant - function calls are governed
assistant = governed_client.beta.assistants.create(
    name="Data Analyst",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-turbo"
)

# Run thread - all tool executions go through kernel
run = governed_client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)
```

### Function Calling Governance

```python
# Define your functions
functions = [
    {
        "name": "execute_sql",
        "description": "Execute SQL query",
        "parameters": {...}
    }
]

# Kernel intercepts function calls
governed_client = kernel.wrap(client, 
    function_handlers={
        "execute_sql": lambda args: db.execute(args["query"])
    }
)
```

---

## Microsoft Semantic Kernel

### Basic Integration

```python
import semantic_kernel as sk
from agent_os.integrations import SemanticKernelWrapper

# Create SK kernel as usual
kernel = sk.Kernel()
kernel.add_chat_service("chat", AzureChatCompletion(...))

# Wrap with Agent OS
aos = SemanticKernelWrapper(policy="strict")
governed_kernel = aos.wrap(kernel)

# Use governed kernel
result = await governed_kernel.run_async(
    my_function,
    input_vars=sk.ContextVariables(input="...")
)
```

### Plugin Governance

```python
# All plugin functions are automatically governed
governed_kernel.import_plugin(MyPlugin, "my_plugin")

# Or govern specific plugins
aos.govern_plugin(MyPlugin, policy="strict")
```

---

## AutoGen

### Multi-Agent Governance

```python
from autogen import AssistantAgent, UserProxyAgent
from agent_os.integrations import AutoGenKernel

# Create AutoGen agents
assistant = AssistantAgent("assistant", llm_config={...})
user_proxy = UserProxyAgent("user", code_execution_config={...})

# Wrap with Agent OS
kernel = AutoGenKernel(policy="strict")
governed_agents = kernel.wrap([assistant, user_proxy])

# Initiate chat - all code execution governed
user_proxy.initiate_chat(assistant, message="...")
```

### Code Execution Safety

```python
kernel = AutoGenKernel(
    policy="strict",
    code_execution={
        "allow_languages": ["python"],
        "block_imports": ["os", "subprocess", "shutil"],
        "max_execution_time": 30,
        "sandbox": True
    }
)
```

---

## Anthropic Claude

### Basic Integration

```python
from anthropic import Anthropic
from agent_os.integrations import AnthropicKernel

client = Anthropic()
kernel = AnthropicKernel(policy="strict")

# Wrap client
governed_client = kernel.wrap(client)

# Tool use is governed
response = governed_client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "..."}],
    tools=[...]  # Tool calls go through kernel
)
```

### MCP Integration

For Claude Desktop with MCP:

```python
from agent_os.mcp import MCPKernelServer

# Run Agent OS as MCP server
server = MCPKernelServer(policy="strict")
server.run()
```

Configure in Claude Desktop:
```json
{
  "mcpServers": {
    "agent-os": {
      "command": "python",
      "args": ["-m", "agent_os.mcp"]
    }
  }
}
```

---

## Custom Framework Integration

### Using the Generic Wrapper

```python
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

# Decorate any function
@kernel.register
async def my_custom_agent(task: str):
    # Your custom agent logic
    result = await custom_llm_call(task)
    return result

# Or wrap at call time
result = await kernel.execute(my_custom_agent, "task")
```

### Building a Custom Integration

```python
from agent_os.integrations import BaseIntegration

class MyFrameworkKernel(BaseIntegration):
    def wrap(self, framework_object):
        """Wrap framework object with governance."""
        return GovernedWrapper(framework_object, self.kernel)
    
    def intercept_action(self, action, context):
        """Called before each action."""
        decision = self.kernel.policy.evaluate(action)
        if decision.denied:
            raise PolicyViolation(decision.reason)
        return action
```

---

## Best Practices

### 1. Start Permissive, Then Tighten

```python
# Development
kernel = MyKernel(policy="audit")  # Log everything, block nothing

# Staging
kernel = MyKernel(policy="permissive")  # Block known dangers

# Production
kernel = MyKernel(policy="strict")  # Block by default
```

### 2. Use Framework-Specific Extras

```bash
# Install only what you need
pip install agent-os[langchain]    # LangChain support
pip install agent-os[crewai]       # CrewAI support
pip install agent-os[full]         # Everything
```

### 3. Combine Multiple Frameworks

```python
from agent_os import KernelSpace

# One kernel governs all
kernel = KernelSpace(policy="strict")

# Wrap different frameworks with same kernel
langchain_wrapper = LangChainKernel(kernel=kernel)
crewai_wrapper = CrewAIKernel(kernel=kernel)

# Unified observability and policy enforcement
```

---

## Troubleshooting

### "Module not found" Errors

```bash
# Install the specific integration
pip install agent-os[langchain]

# Or install all
pip install agent-os[full]
```

### Performance Overhead

Policy checks add ~1-5ms per action. For high-throughput scenarios:

```python
kernel = KernelSpace(
    policy="strict",
    cache_policy_decisions=True,  # Cache repeated checks
    async_audit=True              # Non-blocking audit logs
)
```

### Debugging Integration Issues

```python
import logging
logging.getLogger("agent_os.integrations").setLevel(logging.DEBUG)
```

---

## Next Steps

- [Policy Reference](/docs/policies/) — Define governance rules
- [Observability](/docs/observability/) — Monitor integrations
- [Tutorials](/docs/tutorials/) — Hands-on examples
