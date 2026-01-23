# emk - Episodic Memory Kernel

[![PyPI](https://img.shields.io/pypi/v/emk)](https://pypi.org/project/emk/)
[![Python](https://img.shields.io/pypi/pyversions/emk)](https://pypi.org/project/emk/)
[![License](https://img.shields.io/github/license/imran-siddique/emk)](LICENSE)

**"The Hard Drive"** - An immutable, append-only ledger of agent experiences.

## Overview

`emk` (Episodic Memory Kernel) is a Layer 1 primitive for storing agent experiences as structured episodes. Unlike context construction systems (like `caas`), `emk` is the permanent record. It provides a simple, immutable storage layer for agent experiences following the pattern: **Goal → Action → Result → Reflection**.

## Core Value Proposition

- **Immutable Storage**: Episodes are append-only; no modifications allowed
- **Structured Memory**: Each episode captures the complete experience cycle
- **Flexible Retrieval**: Support for both simple file-based and vector-based retrieval
- **Minimal Dependencies**: Core functionality requires only `pydantic` and `numpy`
- **Not "Smart"**: Does not summarize or interpret - just stores and retrieves

## Installation

```bash
# Basic installation
pip install emk

# With ChromaDB support for vector search
pip install emk[chromadb]

# Development installation
pip install emk[dev]
```

## Quick Start

### Basic Usage with FileAdapter

```python
from emk import Episode, FileAdapter

# Create a memory store
store = FileAdapter("agent_memories.jsonl")

# Create and store an episode
episode = Episode(
    goal="Retrieve user preferences",
    action="Query database for user_id=123",
    result="Successfully retrieved preferences",
    reflection="Database query was efficient and returned expected data",
    metadata={"user_id": "123", "query_time_ms": 45}
)

# Store the episode
episode_id = store.store(episode)
print(f"Stored episode: {episode_id}")

# Retrieve recent episodes
recent = store.retrieve(limit=10)
for ep in recent:
    print(f"{ep.goal} -> {ep.result}")

# Retrieve by ID
specific = store.get_by_id(episode_id)
print(f"Retrieved: {specific.goal}")

# Filter by metadata
user_episodes = store.retrieve(filters={"user_id": "123"})
```

### Using ChromaDB for Vector Search

```python
from emk import Episode, ChromaDBAdapter
import numpy as np

# Create a vector store
store = ChromaDBAdapter(
    collection_name="agent_episodes",
    persist_directory="./chroma_data"
)

# Create an episode with embedding
episode = Episode(
    goal="Learn Python syntax",
    action="Read Python documentation",
    result="Understood basic syntax",
    reflection="Need more practice with decorators"
)

# Create a simple embedding (in practice, use a real embedding model)
embedding = np.random.rand(384)

# Store with embedding
store.store(episode, embedding=embedding)

# Query by similarity
query_embedding = np.random.rand(384)
similar = store.retrieve(query_embedding=query_embedding, limit=5)
```

### Using the Indexer

```python
from emk import Episode, Indexer

episode = Episode(
    goal="Implement user authentication",
    action="Created JWT-based auth system",
    result="Users can now login securely",
    reflection="Should add rate limiting next"
)

# Generate searchable tags
tags = Indexer.generate_episode_tags(episode)
print(f"Tags: {tags}")

# Create search text for embedding
search_text = Indexer.create_search_text(episode)
print(f"Search text: {search_text}")

# Enrich metadata with indexing info
enriched = Indexer.enrich_metadata(episode, auto_tags=True)
print(f"Enriched metadata: {enriched}")
```

## Architecture

### The Schema

The `Episode` class defines the core data structure:

```python
class Episode:
    goal: str                    # The agent's intended objective
    action: str                  # The action taken
    result: str                  # The outcome
    reflection: str              # Analysis or learning
    timestamp: datetime          # Auto-generated
    metadata: Dict[str, Any]     # Additional context
    episode_id: str              # Unique hash-based ID
```

### The Store

Three storage implementations:

1. **VectorStoreAdapter** (Abstract Interface)
   - Defines the contract for all storage implementations
   - Methods: `store()`, `retrieve()`, `get_by_id()`

2. **FileAdapter** (Simple JSONL)
   - Local file-based storage
   - No external dependencies
   - Perfect for logging and simple use cases

3. **ChromaDBAdapter** (Vector Search)
   - Requires optional `chromadb` dependency
   - Supports embedding-based similarity search
   - Ideal for semantic retrieval

### The Indexer

Utilities for tagging and indexing episodes:

- `extract_tags()`: Extract searchable tags from text
- `generate_episode_tags()`: Auto-generate tags from episodes
- `enrich_metadata()`: Add indexing metadata
- `create_search_text()`: Generate text for embeddings

## Design Principles

### ✅ What emk Does

- Stores episodes immutably
- Provides simple retrieval interfaces
- Indexes episodes for efficient search
- Maintains historical records

### ❌ What emk Does NOT Do

- Does not summarize memories (that's for agents or `caas`)
- Does not overwrite data (append-only)
- Does not depend on other agent systems
- Does not make "smart" decisions

### Dependency Rules

**Allowed:**
- `numpy` (for vectors)
- `pydantic` (for schemas)
- `chromadb` (optional extra)

**Strictly Forbidden:**
- `caas` (caas depends on emk, not the other way)
- `agent-control-plane` (memory store is agnostic)
- Any "smart" processing libraries

## Development

```bash
# Clone the repository
git clone https://github.com/imran-siddique/emk.git
cd emk

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=emk --cov-report=html

# Format code
black emk tests

# Lint code
ruff check emk tests
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_schema.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=emk
```

## Use Cases

### 1. Agent Learning History

```python
store = FileAdapter("agent_learning.jsonl")

episode = Episode(
    goal="Solve user query about weather",
    action="Called weather API",
    result="Provided accurate forecast",
    reflection="API response format changed - need to update parser"
)
store.store(episode)
```

### 2. Debugging Agent Behavior

```python
# Store all agent actions for debugging
episode = Episode(
    goal="Process payment",
    action="Called payment gateway",
    result="Payment failed",
    reflection="Gateway timeout - need retry logic",
    metadata={"error_code": "TIMEOUT", "amount": 50.00}
)
store.store(episode)

# Later, retrieve failed episodes
failed = store.retrieve(filters={"error_code": "TIMEOUT"})
```

### 3. Building Agent Memory

```python
# Store experiences for later retrieval by reasoning systems
store = ChromaDBAdapter("agent_memory")

# When agent learns something
episode = Episode(
    goal="Understand user preference",
    action="Analyzed past interactions",
    result="User prefers concise responses",
    reflection="Should adjust response length in future"
)
store.store(episode)

# Later, retrieve relevant experiences
relevant = store.retrieve(query_embedding=current_context_embedding)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Roadmap

- [ ] Additional storage backends (SQLite, PostgreSQL)
- [ ] Advanced filtering and query capabilities
- [ ] Batch operations for efficiency
- [ ] Export/import utilities
- [ ] Performance optimizations for large datasets

## Links

- **Repository**: https://github.com/imran-siddique/emk
- **PyPI**: https://pypi.org/project/emk/
- **Issues**: https://github.com/imran-siddique/emk/issues
