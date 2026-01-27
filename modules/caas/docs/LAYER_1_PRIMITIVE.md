# Layer 1: The Primitive (caas-core)

## Elevator Pitch

A pure, logic-only library for routing context, handling RAG fallacies, and managing context windows. It does not know what an "agent" is; it only knows about text and vectors.

## Publication Target

```bash
pip install caas-core
```

## Allowed Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| numpy | Data handling, vector operations | ✅ Allowed |
| pandas | Data handling, analysis | ✅ Allowed |
| openai | Embeddings (optional) | ✅ Allowed (optional) |
| langchain | Embeddings (optional) | ✅ Allowed (optional) |
| scikit-learn | TF-IDF, similarity | ✅ Allowed |
| pydantic | Data validation | ✅ Allowed |
| fastapi | API server | ✅ Allowed |
| tiktoken | Token counting | ✅ Allowed |

## Strictly Forbidden Dependencies

The following packages **MUST NEVER** be imported or added as dependencies:

| Package | Reason |
|---------|--------|
| `agent-control-plane` | Agent orchestration - violates primitive layer |
| `iatp` | Agent transport protocol - violates primitive layer |
| `scak` | Agent coordination - violates primitive layer |
| Any `*Agent` class | Agent abstraction - violates primitive layer |
| Any `*Supervisor` class | Agent orchestration - violates primitive layer |

## Design Principles

### 1. Stateless Context Routing

All context routing logic MUST be stateless. It should only process the data passed to it.

```python
# ✅ CORRECT: Stateless routing
def route_context(query: str, metadata: dict) -> RoutingDecision:
    # Process only the data passed in
    return analyze_query(query, metadata)

# ❌ WRONG: Querying active runtime
def route_context(query: str, agent: Agent) -> RoutingDecision:
    # DON'T query agent runtime state
    state = agent.get_current_state()  # FORBIDDEN
    return analyze_query(query, state)
```

### 2. Generic Identifiers, Not Objects

Accept `agent_id: str` or `metadata: dict`, not `Agent` objects.

```python
# ✅ CORRECT: Generic identifier
def add_hot_context(content: str, source_id: str, metadata: dict) -> str:
    return store_context(content, source_id, metadata)

# ❌ WRONG: Agent object dependency
def add_hot_context(content: str, agent: Agent) -> str:
    source_id = agent.id  # FORBIDDEN
    return store_context(content, source_id, agent.metadata)
```

### 3. Data In, Data Out

Methods receive data and return data. No side effects on external systems.

```python
# ✅ CORRECT: Pure function
def extract_context(document: Document, query: str, max_tokens: int) -> ContextResponse:
    sections = score_sections(document, query)
    return build_response(sections, max_tokens)

# ❌ WRONG: Side effects
def extract_context(document: Document, agent_bus: AgentBus) -> ContextResponse:
    agent_bus.notify("context_extracted")  # FORBIDDEN
    return response
```

## Core Components

### Context Triad (Hot/Warm/Cold)

Pure context tier management with no agent awareness:

```python
from caas.triad import ContextTriadManager

triad = ContextTriadManager()

# Add context by layer (accepts generic metadata, not agents)
triad.add_hot_context("Current error log", metadata={"source": "system"})
triad.add_warm_context("User prefers verbose output", metadata={"type": "preference"})
triad.add_cold_context("2023 Q1 meeting notes", metadata={"date": "2023-01-15"})

# Get context (pure data retrieval)
hot = triad.get_hot_context(max_tokens=1000)
```

### Heuristic Router

Deterministic routing without LLM classification overhead:

```python
from caas.routing import HeuristicRouter

router = HeuristicRouter()

# Route based on query content only (stateless)
decision = router.route("Summarize this document")
print(decision.model_tier)  # ModelTier.SMART
print(decision.reason)       # "Complex task keywords detected: summarize"
```

### Conversation Manager (Sliding Window)

FIFO conversation management - no summarization, no agent awareness:

```python
from caas.conversation import ConversationManager

conv = ConversationManager(max_turns=10)

# Add turns (accepts strings, not agent objects)
conv.add_turn(user_message="What is X?", ai_response="X is...")

# Get history (pure data)
history = conv.get_conversation_history()
```

### Trust Gateway

Enterprise security without agent coupling:

```python
from caas.gateway import TrustGateway, SecurityPolicy

gateway = TrustGateway(
    security_policy=SecurityPolicy(
        deployment_mode="on_prem",
        security_level="high"
    )
)

# Validate request (accepts generic identifiers)
result = gateway.validate_request(
    request_data={"query": "..."},
    user_id="user-123",  # String identifier, not User object
    data_classification="confidential"
)
```

## Integration Pattern

External systems (agent frameworks, orchestrators) should use CaaS as a **service layer**:

```python
# Example: How an external agent framework uses caas-core

from caas.triad import ContextTriadManager
from caas.routing import HeuristicRouter

# Initialize caas-core components
triad = ContextTriadManager()
router = HeuristicRouter()

class MyExternalAgent:
    """This agent class is OUTSIDE caas-core, not inside."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
    
    def process_query(self, query: str) -> str:
        # Use caas-core as a service (passing data, not self)
        routing = router.route(query)
        
        # Get context (passing identifier, not agent object)
        triad.add_hot_context(query, metadata={"agent_id": self.agent_id})
        context = triad.get_merged_context(max_tokens=4000)
        
        # Agent does its own LLM call
        return self.call_llm(context, query, routing.suggested_model)
```

## Verification Checklist

Before any release, verify:

- [ ] `grep -r "import.*Agent" src/caas/` returns no results
- [ ] `grep -r "from.*Agent" src/caas/` returns no results
- [ ] `grep -r "import.*Supervisor" src/caas/` returns no results
- [ ] `grep -r "agent-control-plane\|iatp\|scak" src/caas/` returns no results
- [ ] All public methods accept `str` or `dict` for identifiers, not objects
- [ ] No methods query external runtime state
