# Multi-Agent Collaboration Examples

This directory contains examples demonstrating how multiple AI agents can collaborate using shared Context-as-a-Service (CaaS) context.

## Examples

### 1. Research Team (`research_team.py`)

A collaborative research workflow with three specialized agents:

- **Researcher Agent**: Investigates topics using HOT context (most relevant, recent)
- **Critic Agent**: Reviews findings using WARM context (broader coverage)
- **Summarizer Agent**: Creates reports using COLD context (comprehensive)

**Run:**
```bash
python examples/multi_agent/research_team.py
```

**Key Features:**
- Shared ContextTriad instance across all agents
- Role-based context tier selection (Hot/Warm/Cold)
- Iterative refinement through agent collaboration
- Source tracking and validation
- Conflict detection

## Integration with Multi-Agent Frameworks

### AutoGen Integration

```python
from autogen import Agent
from caas.triad import ContextTriad

# Create shared CaaS context
context_triad = ContextTriad(doc_store)

# Configure AutoGen agents with CaaS
researcher = Agent(
    name="Researcher",
    system_message="You have access to CaaS context...",
    context_provider=lambda query: context_triad.hot_context.get_context(query)
)
```

### LangGraph Integration

```python
from langgraph.graph import StateGraph
from caas.triad import ContextTriad

# Use CaaS as state management layer
class AgentState(TypedDict):
    messages: List[str]
    context: ContextTriad
    
# Define workflow with shared context
workflow = StateGraph(AgentState)
```

### CrewAI Integration

```python
from crewai import Agent, Crew
from caas.triad import ContextTriad

# Provide CaaS context to crew members
context_triad = ContextTriad(doc_store)

researcher = Agent(
    role="Researcher",
    context=lambda query: context_triad.hot_context.get_context(query)
)

crew = Crew(agents=[researcher, critic, summarizer])
```

## Architecture Benefits

### Shared Context
- All agents access the same context source
- No redundant context fetching
- Consistent information across the team

### Tier-Based Access
- HOT: Immediate, critical information
- WARM: Background, verification data
- COLD: Historical, comprehensive knowledge

### Efficient Collaboration
- Context-driven coordination
- Source tracking for verification
- Conflict detection and resolution

## Adding Your Own Multi-Agent Examples

1. Create a new file in this directory
2. Import CaaS components:
   ```python
   from caas.storage.document_store import DocumentStore
   from caas.triad import ContextTriad
   ```
3. Define agent classes inheriting from BaseAgent (or create your own)
4. Share ContextTriad instance across agents
5. Document your workflow in this README

## Common Patterns

### Pattern 1: Sequential Workflow
```python
# Agent 1 → Agent 2 → Agent 3
result1 = agent1.process(query)
result2 = agent2.review(result1)
final = agent3.synthesize(result1, result2)
```

### Pattern 2: Parallel Processing
```python
# Multiple agents work simultaneously
results = []
for agent in agents:
    result = agent.process(query)  # Each uses shared context
    results.append(result)
```

### Pattern 3: Consensus Building
```python
# Agents vote/reach consensus
votes = [agent.evaluate(query) for agent in agents]
consensus = majority_vote(votes)
```

## Best Practices

1. **Initialize Context Once**: Share the ContextTriad instance, don't create multiple
2. **Choose Appropriate Tier**: Match context tier to agent role (Hot/Warm/Cold)
3. **Track Sources**: Store which chunks each agent used
4. **Handle Conflicts**: Use CaaS conflict detection
5. **Log Interactions**: Keep conversation history for debugging

## Future Examples

Coming soon:
- Code Review Team (senior dev, junior dev, security reviewer)
- Customer Support Team (L1, L2, specialist)
- Content Creation Team (writer, editor, fact-checker)
- Software Architecture Team (architect, developer, reviewer)

## Contributing

Add your multi-agent examples! Requirements:
- Clear agent roles and responsibilities
- Shared CaaS context usage
- Example output or demo
- Integration with popular frameworks (optional)

---

*Multi-agent AI is the future. CaaS makes it practical.*
