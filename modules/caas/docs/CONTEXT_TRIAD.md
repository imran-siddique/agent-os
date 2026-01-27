# Context Triad Implementation

## Overview

The **Context Triad** is a three-tier context management system that treats context like a tiered storage system defined by **intimacy**, not just speed. This implementation solves the "Flat Chunk Fallacy" by introducing layered context with clear policies for each tier.

## The Problem: The Naive Approach

**"Stuff everything into the Context Window until it's full."**

This approach treats all context equally, leading to:
- Important current information gets buried
- User preferences are inconsistently applied  
- Historical data pollutes the working context
- No clear prioritization strategy

## The Solution: The Context Triad

The Context Triad introduces three layers based on **intimacy and access policy**:

### L1: Hot Context (The Situation)

**Definition:** What is happening right now?

**Examples:**
- Current conversation messages
- Open VS Code tabs
- Error logs streaming in real-time
- Active debugging session
- Recently viewed files

**Policy:** "Attention Head" - Overrides everything
- Highest priority
- Always included (unless explicitly disabled)
- Automatically maintained to keep fresh (limits to 50 most recent items)
- Sorted by priority and recency

### L2: Warm Context (The Persona)

**Definition:** Who am I?

**Examples:**
- LinkedIn profile
- Medium articles  
- GitHub bio
- Coding style preferences (type hints, docstrings)
- Favorite libraries and frameworks
- Communication style preferences
- Technology stack

**Policy:** "Always On Filter" - Colors how AI speaks to you
- Persistent across sessions
- Should be part of the system prompt
- Doesn't need retrieval every time
- Influences all AI responses

### L3: Cold Context (The Archive)

**Definition:** What happened last year?

**Examples:**
- Old tickets from previous years
- Closed pull requests
- Historical design documents
- Legacy system documentation
- Archived meeting notes
- Past project specifications

**Policy:** "On Demand Only" - Fetch only when explicitly asked
- **Never** automatically included
- Requires explicit query to access
- Prevents historical data from polluting hot window
- Only surfaces when user asks for history

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Context Triad Manager                  │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Hot Context (L1 - The Situation)              │    │
│  │  Priority: Highest                              │    │
│  │  Policy: "Attention Head" - Always On          │    │
│  │  Auto-limit: 50 most recent items              │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Warm Context (L2 - The Persona)               │    │
│  │  Priority: Medium                               │    │
│  │  Policy: "Always On Filter" - Persistent       │    │
│  │  Use: System prompt initialization              │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Cold Context (L3 - The Archive)               │    │
│  │  Priority: Low                                  │    │
│  │  Policy: "On Demand Only" - Query Required     │    │
│  │  Access: Explicit query only                    │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Usage Examples

### Python API

#### Adding Context to Layers

```python
from caas.triad import ContextTriadManager

manager = ContextTriadManager()

# Add hot context (current situation)
manager.add_hot_context(
    "User is debugging: NullPointerException at line 145",
    metadata={"source": "error_log"},
    priority=3.0
)

# Add warm context (user persona)
manager.add_warm_context(
    "Senior Python developer, prefers type hints",
    metadata={"category": "Profile"},
    priority=2.0
)

# Add cold context (historical archive)
manager.add_cold_context(
    "Ticket #1234: Fixed similar bug in 2023",
    metadata={"date": "2023-06-15"},
    priority=1.0
)
```

#### Retrieving Context

```python
# Default: Hot + Warm only (Cold excluded)
result = manager.get_full_context(
    include_hot=True,
    include_warm=True,
    include_cold=False
)

print(result['hot_context'])   # Current situation
print(result['warm_context'])  # User persona
print(result['cold_context'])  # Empty (not included)

# Explicit query for cold context
result = manager.get_full_context(
    include_hot=True,
    include_warm=True,
    include_cold=True,
    cold_query="authentication"  # Required for cold context
)

print(result['cold_context'])  # Historical data matching query
```

### REST API

#### Add Hot Context

```bash
curl -X POST "http://localhost:8000/triad/hot" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User debugging NullPointerException",
    "metadata": {"source": "error_log"},
    "priority": 3.0
  }'
```

#### Add Warm Context

```bash
curl -X POST "http://localhost:8000/triad/warm" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Senior Python developer, prefers FastAPI",
    "metadata": {"category": "Profile"},
    "priority": 2.0
  }'
```

#### Add Cold Context

```bash
curl -X POST "http://localhost:8000/triad/cold" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Ticket #1234 from 2023",
    "metadata": {"date": "2023-06-15"},
    "priority": 1.0
  }'
```

#### Retrieve Context Triad

```bash
# Default: Hot + Warm only
curl -X POST "http://localhost:8000/triad" \
  -H "Content-Type: application/json" \
  -d '{
    "include_hot": true,
    "include_warm": true,
    "include_cold": false
  }'

# With cold context (requires query)
curl -X POST "http://localhost:8000/triad" \
  -H "Content-Type: application/json" \
  -d '{
    "include_hot": true,
    "include_warm": true,
    "include_cold": true,
    "query": "authentication",
    "max_tokens_per_layer": {
      "hot": 1000,
      "warm": 500,
      "cold": 1000
    }
  }'
```

#### Get Triad State

```bash
curl -X GET "http://localhost:8000/triad/state"
```

#### Clear Context Layers

```bash
# Clear hot context
curl -X DELETE "http://localhost:8000/triad/hot"

# Clear warm context
curl -X DELETE "http://localhost:8000/triad/warm"

# Clear cold context
curl -X DELETE "http://localhost:8000/triad/cold"

# Clear all layers
curl -X DELETE "http://localhost:8000/triad"
```

## Key Features

### 1. Priority-Based Ordering

Items within each layer are ordered by priority:
- Higher priority items appear first
- Ensures most important information is always visible
- Configurable per-item priority levels

### 2. Token Limits Per Layer

Control context size with per-layer token limits:
```python
max_tokens_per_layer = {
    "hot": 1000,   # Current situation
    "warm": 500,   # User persona
    "cold": 1000   # Historical archive
}
```

### 3. Automatic Hot Context Management

Hot context is automatically maintained:
- Limits to 50 most recent items
- Automatically removes oldest items
- Keeps context fresh and relevant

### 4. Policy Enforcement

The system enforces clear policies:
- **Hot:** Always included by default
- **Warm:** Always on (persistent)
- **Cold:** Requires explicit query (never auto-included)

### 5. Metadata Support

Each context item supports rich metadata:
```python
metadata = {
    "source": "error_log",
    "severity": "error",
    "file": "auth_service.py",
    "line": 145
}
```

## Use Cases

### 1. AI Coding Assistant

**Hot Context:**
- Current file being edited
- Active error messages
- Current conversation

**Warm Context:**
- User's coding style preferences
- Preferred libraries
- Communication style

**Cold Context:**
- Similar bugs fixed in the past
- Historical design decisions
- Legacy documentation

### 2. Customer Support Bot

**Hot Context:**
- Current customer message
- Active ticket details
- Recent conversation history

**Warm Context:**
- Customer profile
- Subscription tier
- Communication preferences

**Cold Context:**
- Past tickets from this customer
- Historical product issues
- Archived KB articles

### 3. Document Analysis System

**Hot Context:**
- Document being analyzed
- Current user query
- Active section being read

**Warm Context:**
- User's domain expertise
- Preferred analysis depth
- Language preferences

**Cold Context:**
- Related historical documents
- Past analysis results
- Archived reference materials

## Benefits

### ✅ Solves the "Flat Chunk Fallacy"

Traditional systems treat all context equally. The Context Triad introduces clear layers with distinct policies.

### ✅ Prevents Context Pollution

Cold data never automatically pollutes the hot window. Historical information is only retrieved on explicit request.

### ✅ Improves AI Response Quality

Warm context acts as a persistent filter, ensuring the AI always speaks in a style appropriate for the user.

### ✅ Prioritizes What Matters

Hot context (current situation) always takes precedence over historical data.

### ✅ Efficient Token Usage

Per-layer token limits ensure optimal use of context window space.

## Testing

Run the comprehensive test suite:

```bash
# Run context triad tests
python test_context_triad.py

# Run demo
python demo_context_triad.py
```

## API Reference

### ContextTriadManager Methods

#### `add_hot_context(content, metadata, priority)`
Add hot context item (current situation).

#### `add_warm_context(content, metadata, priority)`
Add warm context item (user persona).

#### `add_cold_context(content, metadata, priority)`
Add cold context item (historical archive).

#### `get_hot_context(max_tokens, include_metadata)`
Retrieve hot context.

#### `get_warm_context(max_tokens, include_metadata)`
Retrieve warm context.

#### `get_cold_context(query, max_tokens, include_metadata)`
Retrieve cold context (requires query).

#### `get_full_context(include_hot, include_warm, include_cold, cold_query, max_tokens_per_layer)`
Retrieve complete context triad.

#### `clear_hot_context()`
Clear all hot context items.

#### `clear_warm_context()`
Clear all warm context items.

#### `clear_cold_context()`
Clear all cold context items.

#### `clear_all()`
Clear all context layers.

#### `remove_item(item_id, layer)`
Remove specific item from context.

#### `get_state()`
Get current context triad state.

## Design Principles

1. **Intimacy over Speed:** Context layers are defined by how intimate/relevant they are, not how fast they can be retrieved.

2. **Clear Policies:** Each layer has a clear policy that's always enforced.

3. **No Automatic Pollution:** Cold data never automatically appears in the context window.

4. **User Persona as Filter:** Warm context acts as a persistent filter that colors all AI responses.

5. **Current Situation Takes Priority:** Hot context always has highest priority.

## Comparison with Traditional Approaches

| Aspect | Traditional (Flat) | Context Triad |
|--------|-------------------|---------------|
| Context Organization | All equal | 3 tiers by intimacy |
| Historical Data | Always included | On-demand only |
| User Preferences | Inconsistent | Always-on filter |
| Priority | Unclear | Clear hierarchy |
| Token Efficiency | Poor | Optimized per layer |
| Context Pollution | Common | Prevented |

## Future Enhancements

Potential improvements:
- Automatic warm context learning from user behavior
- Semantic search within cold context
- Context persistence across sessions
- Context analytics and insights
- Integration with vector databases for better cold context retrieval

## Conclusion

The Context Triad represents an engineering-focused approach to context management, moving beyond naive "stuff everything in" approaches to a thoughtful, policy-driven system that respects the intimacy and relevance of different types of context.

**The Reality:** Not all context is created equal. The Context Triad ensures the right context is available at the right time with the right priority.
