# Method

## System Overview

Context-as-a-Service (CaaS) is a modular pipeline for intelligent context extraction and serving. Figure 1 illustrates the overall architecture.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Ingestion  │ ──▶ │  Structure   │ ──▶ │  Metadata   │ ──▶ │    Time      │
│  (PDF/HTML/ │     │   Parser     │     │  Injector   │     │    Decay     │
│   Code)     │     └──────────────┘     └─────────────┘     └──────────────┘
└─────────────┘            │                    │                    │
                           ▼                    ▼                    ▼
                    ┌────────────────────────────────────────────────────┐
                    │              Indexed Document Store                │
                    │         (Three-Tier Value Hierarchy)              │
                    └────────────────────────────────────────────────────┘
                                          │
                                          ▼
                    ┌────────────────────────────────────────────────────┐
                    │              Context Triad Assembly                │
                    │         (Hot / Warm / Cold Prioritization)         │
                    └────────────────────────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
            ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
            │ Heuristic   │       │  Pragmatic  │       │    Trust    │
            │   Router    │       │    Truth    │       │   Gateway   │
            └─────────────┘       └─────────────┘       └─────────────┘
                    │                     │                     │
                    └─────────────────────┼─────────────────────┘
                                          ▼
                                    ┌───────────┐
                                    │    LLM    │
                                    └───────────┘
```

## Structure-Aware Indexing

### Problem

Traditional RAG systems use **flat chunking**: split documents into fixed-size segments (e.g., 500 tokens) and embed each equally. This approach treats a class definition the same as a TODO comment, losing the structural signals that encode importance.

### Solution: Three-Tier Value Hierarchy

We classify document content into three value tiers based on document type and structural patterns:

**Algorithm 1: Structure-Aware Classification**

```python
def classify_content(chunk, doc_type):
    if doc_type == "code":
        if is_class_or_function_definition(chunk):
            return HIGH_VALUE
        elif is_docstring_or_comment(chunk):
            return MEDIUM_VALUE
        else:  # imports, config, TODOs
            return LOW_VALUE
    
    elif doc_type == "legal":
        if is_definitions_or_liability(chunk):
            return HIGH_VALUE
        elif is_terms_or_conditions(chunk):
            return MEDIUM_VALUE
        else:  # boilerplate, signatures
            return LOW_VALUE
    
    # ... similar rules for policy, documentation, etc.
```

### Value Tier Definitions

| Tier | Code | Legal | Policy | Documentation |
|------|------|-------|--------|---------------|
| **HIGH** | Class/function defs | Definitions, liability | Core requirements | API endpoints |
| **MEDIUM** | Docstrings, comments | Terms, conditions | Guidelines | Examples, explanations |
| **LOW** | Imports, TODOs | Boilerplate, signatures | Formatting | Metadata, headers |

### Retrieval Weighting

During retrieval, we apply multiplicative weights:

$$\text{score}(c) = \text{similarity}(q, c) \times w_{\text{tier}}(c)$$

Where $w_{\text{HIGH}} = 1.5$, $w_{\text{MEDIUM}} = 1.0$, $w_{\text{LOW}} = 0.5$.

## Metadata Injection

### Problem

When chunks are extracted from documents, they lose context. "It increased by 5%" is meaningless without knowing the document path: `Q3 Earnings → Revenue → North America`.

### Solution: Contextual Breadcrumbs

We automatically inject metadata into each chunk:

```python
@dataclass
class EnrichedChunk:
    content: str
    metadata: ChunkMetadata

@dataclass  
class ChunkMetadata:
    document_path: str      # "Q3_Earnings.pdf"
    section_hierarchy: List[str]  # ["Revenue", "North America"]
    created_at: datetime
    updated_at: datetime
    source_type: str        # "official" | "informal"
    confidence: float       # 0.0 - 1.0
```

The metadata is prepended to the chunk content before sending to the LLM:

```
[Source: Q3_Earnings.pdf > Revenue > North America | Updated: 2026-01-15]
Revenue increased by 5% compared to Q2, driven primarily by...
```

## Time-Based Decay

### Problem

Semantic similarity ignores temporal relevance. A 2021 answer to "How to restart the server" may match perfectly but be dangerously outdated.

### Solution: Exponential Decay

We apply time-based decay using an exponential function inspired by radioactive decay:

$$\text{decay}(t) = e^{-\lambda t}$$

Where:
- $t$ = time since document creation/update (days)
- $\lambda = \ln(2) / T_{1/2}$ (decay constant)
- $T_{1/2}$ = half-life parameter (configurable per domain)

**Algorithm 2: Time-Aware Scoring**

```python
def time_adjusted_score(chunk, query, half_life_days=90):
    base_score = semantic_similarity(query, chunk.content)
    
    age_days = (now() - chunk.metadata.updated_at).days
    decay_factor = exp(-log(2) * age_days / half_life_days)
    
    return base_score * decay_factor
```

### Domain-Specific Half-Lives

| Domain | Half-Life | Rationale |
|--------|-----------|-----------|
| Code/Engineering | 90 days | APIs change frequently |
| Policy/HR | 365 days | Policies updated annually |
| Legal | 730 days | Contracts have longer validity |
| Incidents | 30 days | Recent incidents most relevant |

## Context Triad

### Problem

Traditional systems stuff context into the LLM window with no priority distinction. A user's current question, their preferences, and historical archives from years ago compete equally for space.

### Solution: Hot/Warm/Cold Classification

We organize context into three intimacy-based tiers:

| Tier | Content | Token Budget | Priority |
|------|---------|--------------|----------|
| **Hot** 🔥 | Current conversation, last 10 turns | 2,000 | Highest |
| **Warm** 🌡️ | User preferences, recent documents | 1,000 | Medium |
| **Cold** ❄️ | Historical archives, reference docs | 5,000 | Lowest |

**Algorithm 3: Context Assembly**

```python
def assemble_context(query, conversation, user_profile, retrieved_docs):
    context = ContextTriad()
    
    # Hot: Preserve recent turns exactly (FIFO, no summarization)
    context.hot = conversation.get_last_n_turns(10)
    context.hot.truncate_to_tokens(2000)
    
    # Warm: User context and recent activity
    context.warm = user_profile.preferences + user_profile.recent_docs
    context.warm.truncate_to_tokens(1000)
    
    # Cold: Retrieved documents, time-decayed and ranked
    context.cold = rank_by_relevance_and_time(retrieved_docs, query)
    context.cold.truncate_to_tokens(5000)
    
    return context.assemble()  # Total: 8,000 tokens
```

### FIFO vs. Summarization

We explicitly reject summarization for conversation history:

| Approach | Pros | Cons |
|----------|------|------|
| **Summarization** | Compresses more history | Loses nuance, costs tokens to generate |
| **FIFO (Ours)** | Preserves exact recent content | Loses older context |

Our philosophy: **"Chopping > Summarizing"**. Users rarely reference content from 20 minutes ago but frequently reference the exact code snippet from 30 seconds ago.

## Heuristic Router

### Problem

ML-based routers add latency (15-50ms). LLM-based routers are slower still (100-500ms). For high-volume enterprise deployments, this latency compounds.

### Solution: Deterministic Rules

We use a rule-based router with **zero model inference**:

**Algorithm 4: Heuristic Routing**

```python
def route_query(query):
    query_lower = query.lower()
    
    # Keyword-based routing
    if any(kw in query_lower for kw in ["error", "bug", "crash", "fail"]):
        return RouteType.TROUBLESHOOTING
    
    if any(kw in query_lower for kw in ["how to", "steps", "guide"]):
        return RouteType.PROCEDURAL
    
    if any(kw in query_lower for kw in ["policy", "rule", "allowed"]):
        return RouteType.POLICY
    
    if any(kw in query_lower for kw in ["api", "endpoint", "request"]):
        return RouteType.TECHNICAL
    
    # Default: general retrieval
    return RouteType.GENERAL
```

### Routing Performance

| Router | Mean Latency | Accuracy |
|--------|--------------|----------|
| LLM-based | 450ms | 95% |
| ML-based | 15ms | 92% |
| **Heuristic (Ours)** | **0.003ms** | **89%** |

We trade 3-6% accuracy for **5,000-150,000x speedup**. For most enterprise queries, deterministic rules suffice.

## Pragmatic Truth

### Problem

Official documentation often contains theoretical or aspirational information. The actual truth lives in Slack logs, incident reports, and team notes.

### Solution: Dual-Source Tracking

We maintain parallel indices for official and informal sources:

```python
@dataclass
class PragmaticTruthResult:
    official_answer: str
    official_source: str
    informal_answer: Optional[str]
    informal_source: Optional[str]
    conflict_detected: bool
    conflict_explanation: Optional[str]
```

**Algorithm 5: Conflict Detection**

```python
def detect_conflict(official_chunks, informal_chunks, query):
    official_answer = synthesize(official_chunks)
    informal_answer = synthesize(informal_chunks)
    
    # Semantic similarity between answers
    similarity = cosine_similarity(
        embed(official_answer), 
        embed(informal_answer)
    )
    
    if similarity < CONFLICT_THRESHOLD:  # e.g., 0.7
        return Conflict(
            official=official_answer,
            informal=informal_answer,
            explanation=generate_conflict_explanation(
                official_answer, informal_answer
            )
        )
    
    return NoConflict(answer=official_answer)
```

### Example Output

**Query**: "What's the API rate limit?"

| Source Type | Answer | Source |
|-------------|--------|--------|
| Official | "100 requests/minute" | api_docs.md |
| Informal | "Crashes around 50; the docs lie" | #engineering Slack |
| **Conflict** | ⚠️ Yes | |

**CaaS Response**: "The official documentation states 100 requests/minute, but engineering discussions indicate the practical limit is closer to 50 requests/minute before performance degradation."

## Trust Gateway

### Problem

Third-party routing services require sending proprietary data through external APIs. No enterprise CISO accepts this data leakage risk.

### Solution: On-Premises Deployment

The Trust Gateway is designed for deployment behind the enterprise firewall:

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTERPRISE NETWORK                        │
│  ┌─────────────┐     ┌─────────────────┐     ┌───────────┐  │
│  │  Internal   │ ──▶ │  Trust Gateway  │ ──▶ │  LLM API  │  │
│  │  Services   │     │  (On-Prem)      │     │ (External)│  │
│  └─────────────┘     └─────────────────┘     └───────────┘  │
│                             │                               │
│                      No PII/proprietary                     │
│                      data leaves network                    │
│                      until sanitized                        │
└─────────────────────────────────────────────────────────────┘
```

### Security Properties

1. **Data Sovereignty**: All processing happens within enterprise boundaries
2. **Audit Logging**: Complete trace of all context assembly decisions
3. **PII Filtering**: Optional sanitization before external API calls
4. **Model Agnostic**: Route to any LLM provider (OpenAI, Anthropic, local)

---

## Implementation

CaaS is implemented in Python 3.8+ with the following dependencies:

- **FastAPI**: REST API server
- **Pydantic**: Data validation and serialization
- **NumPy/scikit-learn**: Vector operations
- **tiktoken**: Token counting

The complete implementation is open-source: https://github.com/imran-siddique/context-as-a-service
