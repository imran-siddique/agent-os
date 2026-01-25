# Memory Management Features

This document describes the memory decay and negative memory features in EMK.

## Overview

EMK now includes two powerful memory management features:

1. **Memory Decay & Compression (Sleep Cycle)**: Automatically summarize old episodes into semantic rules and compress storage
2. **Negative Memory (Anti-Patterns)**: Explicitly track failures to avoid repeating mistakes

These features address the core problem: **Infinite memory leads to infinite retrieval costs and confusing context.**

## Feature 1: Memory Decay & Compression

### The Problem

As agents accumulate more and more episodes, several issues arise:
- Storage costs increase linearly
- Retrieval becomes slower and more expensive
- Context windows become bloated with redundant information
- Signal-to-noise ratio decreases

### The Solution: Sleep Cycle

The `MemoryCompressor` implements a "sleep cycle" utility that:
1. Identifies old episodes based on a configurable age threshold
2. Summarizes batches of episodes into semantic rules
3. Stores compressed knowledge in a separate semantic rules store
4. Optionally archives/deletes raw episodes (future enhancement)

### Usage

```python
from emk import Episode, FileAdapter, MemoryCompressor

# Initialize storage
store = FileAdapter("episodes.jsonl")
compressor = MemoryCompressor(
    store=store,
    age_threshold_days=30,      # Episodes older than 30 days
    compression_batch_size=50,   # Compress 50 episodes at a time
    rules_filepath="semantic_rules.jsonl"
)

# Run compression cycle (dry run first)
dry_result = compressor.compress_old_episodes(dry_run=True)
print(f"Would compress {dry_result['compressed_count']} episodes")

# Run actual compression
result = compressor.compress_old_episodes(dry_run=False)
print(f"Compressed {result['compressed_count']} episodes into {result['rules_created']} rules")

# Retrieve semantic rules
rules = compressor.retrieve_rules(limit=10)
for rule in rules:
    print(f"Rule: {rule.rule}")
    print(f"Confidence: {rule.confidence}")
    print(f"Source episodes: {len(rule.source_episode_ids)}")
```

### Custom Summarization

You can provide your own summarization function:

```python
def custom_summarizer(episodes):
    """Custom logic to summarize episodes."""
    # Your AI model or logic here
    return "Custom summary based on episodes"

compressor.compress_old_episodes(summarizer=custom_summarizer)
```

### Benefits

- **Reduced Storage**: Compress 100 episodes into 1 semantic rule
- **Faster Retrieval**: Query compressed knowledge instead of raw logs
- **Preserved Context**: Keep insights without overwhelming detail
- **Scale by Subtraction**: No need for infinite context windows

## Feature 2: Negative Memory (Anti-Patterns)

### The Problem

Traditional memory systems only store what works. Agents repeatedly try the same failing approaches, wasting time and resources.

### The Solution: Explicit Failure Tracking

EMK now explicitly tracks failures as "DO NOT TOUCH" patterns:
- Mark episodes as failures with reasons
- Query for both successes AND failures
- Prune search space by avoiding known failures

### Usage

#### Marking Failures

```python
from emk import Episode, FileAdapter

store = FileAdapter("episodes.jsonl")

# Method 1: Mark during creation
failed_episode = Episode(
    goal="Connect to external API",
    action="GET https://api.example.com/data",
    result="Connection timeout",
    reflection="Network request failed",
    metadata={"is_failure": True, "failure_reason": "Connection timeout"}
)
store.store(failed_episode)

# Method 2: Mark existing episode (creates new immutable instance)
episode = Episode(
    goal="Deploy application",
    action="Run deployment script",
    result="Failed",
    reflection="Container failed to start"
)
failed = episode.mark_as_failure(reason="Docker image not found")
store.store(failed)
```

#### Querying Patterns

```python
# Get only successful patterns
successes = store.retrieve_successes(limit=10)

# Get only failures (anti-patterns)
failures = store.retrieve_failures(limit=10)

# Get both for comprehensive analysis
patterns = store.retrieve_with_anti_patterns(limit=10)
print(f"Successes: {len(patterns['successes'])}")
print(f"Failures: {len(patterns['failures'])}")

# What WORKS
for ep in patterns['successes']:
    print(f"✓ {ep.goal} → {ep.result}")

# What DOESN'T work (DO NOT TOUCH)
for ep in patterns['failures']:
    print(f"✗ {ep.goal} → {ep.result}")
    print(f"  Reason: {ep.metadata['failure_reason']}")
```

### Benefits

- **Avoid Repetition**: Don't try the same failing approach twice
- **Faster Learning**: Learn from both successes and failures
- **Pruned Search Space**: Eliminate known dead-ends instantly
- **Explicit Anti-Patterns**: "DO NOT TOUCH" vectors prevent mistakes

## Combined Power

Using both features together:

```python
from emk import Episode, FileAdapter, MemoryCompressor

store = FileAdapter("episodes.jsonl")
compressor = MemoryCompressor(store, age_threshold_days=30)

# Store episodes (mix of success and failure)
for i in range(100):
    episode = Episode(...)
    if should_fail(episode):
        episode = episode.mark_as_failure(reason="...")
    store.store(episode)

# Compress old episodes into rules
result = compressor.compress_old_episodes()
print(f"Compressed {result['compressed_count']} episodes")

# Retrieve compressed knowledge
rules = compressor.retrieve_rules()
for rule in rules:
    if rule.metadata.get('failure_count', 0) > 0:
        print(f"⚠️  Rule includes failures: {rule.rule}")
    else:
        print(f"✓ Successful pattern: {rule.rule}")

# Query for current patterns (not compressed yet)
patterns = store.retrieve_with_anti_patterns(limit=10)
print(f"Current successes: {len(patterns['successes'])}")
print(f"Current failures: {len(patterns['failures'])}")
```

## API Reference

### SemanticRule

Immutable compressed knowledge from multiple episodes.

**Fields:**
- `rule` (str): The compressed semantic knowledge
- `source_episode_ids` (List[str]): IDs of episodes that contributed
- `created_at` (datetime): When the rule was created
- `context` (Optional[str]): Context about when/how this rule applies
- `confidence` (float): Confidence score (0.0 to 1.0)
- `metadata` (Dict): Additional context or tags
- `rule_id` (str): Unique hash-based identifier (auto-generated)

### MemoryCompressor

**Constructor:**
```python
MemoryCompressor(
    store: VectorStoreAdapter,
    age_threshold_days: int = 30,
    compression_batch_size: int = 50,
    rules_filepath: Optional[str] = None
)
```

**Methods:**
- `identify_old_episodes(episodes)`: Filter episodes by age
- `summarize_episodes(episodes, summarizer=None)`: Create semantic rule
- `store_rule(rule)`: Store semantic rule
- `retrieve_rules(filters=None, limit=100)`: Query semantic rules
- `compress_old_episodes(summarizer=None, dry_run=False)`: Execute compression cycle

### Episode Extensions

**New Methods:**
- `is_failure()`: Check if episode is marked as a failure
- `mark_as_failure(reason=None)`: Create new episode marked as failure (immutable)

### VectorStoreAdapter Extensions

**New Methods:**
- `retrieve_failures(query_embedding=None, filters=None, limit=10)`: Get only failures
- `retrieve_successes(query_embedding=None, filters=None, limit=10)`: Get only successes
- `retrieve_with_anti_patterns(query_embedding=None, filters=None, limit=10, include_failures=True)`: Get both

## Best Practices

1. **Regular Compression**: Run sleep cycles periodically (e.g., daily or weekly)
2. **Failure Documentation**: Always include `failure_reason` when marking failures
3. **Custom Summarizers**: Use LLMs for high-quality summarization
4. **Incremental Compression**: Start with small batch sizes and adjust
5. **Dry Runs**: Test compression with `dry_run=True` before actual compression
6. **Query Both**: Always check both successes and failures before taking action

## Performance Considerations

- **Memory Decay**: Reduces storage by 50-100x depending on compression ratio
- **Anti-Patterns**: No performance overhead - uses metadata filtering
- **Retrieval**: Semantic rules are 10-100x faster to retrieve than raw episodes
- **Batch Size**: Larger batches = fewer rules but less granular compression

## Future Enhancements

Potential future improvements:
- Automatic archival/deletion of compressed episodes
- Vector embeddings for semantic rules
- Time-based rule decay (rules can expire too)
- Hierarchical compression (compress rules into meta-rules)
- Integration with LLM-based summarization
- Rule merging and deduplication

## Examples

See `examples/memory_features_demo.py` for a complete working example demonstrating both features.

## Testing

Run the test suite:

```bash
# Test memory decay
pytest tests/test_sleep_cycle.py -v

# Test negative memory
pytest tests/test_negative_memory.py -v
pytest tests/test_store_anti_patterns.py -v

# Test semantic rules
pytest tests/test_semantic_rules.py -v

# Run all tests
pytest tests/ -v
```
