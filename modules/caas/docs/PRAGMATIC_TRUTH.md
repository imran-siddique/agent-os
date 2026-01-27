# Pragmatic Truth: Real > Official

## Overview

The **Pragmatic Truth** feature embodies the philosophy that AI should provide **Real Answers**, not just **Official Ones**. When official documentation conflicts with practical reality (team conversations, logs, runbooks), the system presents both perspectives with full transparency and proper citations.

## The Problem

Traditional knowledge systems treat all information equally, leading to misleading responses:

**The Naive Approach:**
> "The Official Documentation is the source of truth."

**The Engineering Reality:**
Any Senior Engineer knows that "Docs" are often theoretical, while "Slack Logs" contain the actual fix. If the Documentation says "The API limit is 100," but Engineers in Slack are saying "Actually, it crashes after 50," the AI faces a conflict.

**Example Scenario:**
- **Official Docs:** "API supports 100 requests/minute"
- **Team Reality:** "API crashes after 50 requests in production"
- **Traditional AI:** Only shows official docs (misleading)
- **Pragmatic AI:** Shows both with citations (transparent)

## The Solution

The Pragmatic Truth system:

1. **Tracks Source Types** - Distinguishes between official docs and practical sources
2. **Includes Citations** - Every piece of information cites its source
3. **Detects Conflicts** - Identifies when official and practical sources disagree
4. **Presents Both Perspectives** - Shows official answer AND real-world experience
5. **Applies Time Decay** - Recent practical experience weighs more than old docs

### Core Philosophy

> **"Give Justice to the Answer"**
> 
> The AI must provide the Real Answer, not just the Official one. But it cannot hallucinate - it must cite sources: "I found this in a Slack conversation from yesterday." Transparency allows users to trust the "Real" answer over the "Official" one.

## Source Types

The system recognizes multiple source types:

| Source Type | Description | Example |
|------------|-------------|---------|
| `OFFICIAL_DOCS` | Official documentation, specs | API Reference v2.1 |
| `PRACTICAL_LOGS` | Server logs, error logs | Production error logs |
| `TEAM_CHAT` | Slack, Teams conversations | #engineering Slack channel |
| `CODE_COMMENTS` | Inline code comments | TODO, FIXME, HACK comments |
| `TICKET_SYSTEM` | Jira, GitHub issues | GitHub issue #1234 |
| `RUNBOOK` | Operational runbooks | Production troubleshooting guide |
| `WIKI` | Internal wikis | Company knowledge base |
| `MEETING_NOTES` | Meeting decisions | Engineering sync notes |

## Features

### 1. Automatic Source Detection

The system automatically detects source types from document metadata and content:

```python
from caas.pragmatic_truth import SourceDetector

detector = SourceDetector()
source_type = detector.detect_source_type(document)
# Returns: SourceType.TEAM_CHAT
```

### 2. Citation Generation

Every section gets a proper citation with:
- Source type
- Source name
- Timestamp
- URL (if available)
- Brief excerpt

```python
citation = detector.create_citation(document, section)
# Citation(
#   source_type=SourceType.TEAM_CHAT,
#   source_name="Slack #engineering",
#   timestamp="2024-01-02T10:00:00",
#   url="slack://channel/engineering/msg123"
# )
```

### 3. Conflict Detection

Automatically detects when official and practical sources contradict:

```python
from caas.pragmatic_truth import ConflictDetector

detector = ConflictDetector()
conflicts = detector.detect_conflicts(sections, documents)
# Returns list of SourceConflict objects
```

### 4. Transparent Responses

Context responses include citations and conflict warnings:

```
## Rate Limits
The API supports up to 100 requests per minute...

---
### 📚 Sources
1. [Official Docs] API Documentation v2.1 (2023-07-08)

### ⚠️ Conflicting Information Detected

📖 Official Documentation says:
   The API limit is 100 requests per minute...
   Source: [Official Docs] API Documentation v2.1

🔧 Practical Experience shows:
   API crashes after 50 requests in production...
   Source: [Team Chat] Slack #engineering (2024-01-02)

💡 Recommendation: Use practical limit (50/min) as official docs 
   may be outdated. Recent team observations trump old specs.
```

## API Usage

### Ingesting Documents with Source Types

```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@api-docs.pdf" \
  -F "format=pdf" \
  -F "title=API Documentation" \
  -F "source_type=official_docs" \
  -F "source_url=https://api.example.com/docs"
```

### Extracting Context with Citations

```bash
curl -X POST "http://localhost:8000/context/{document_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "rate limit",
    "max_tokens": 2000,
    "enable_citations": true,
    "detect_conflicts": true
  }'
```

**Response:**
```json
{
  "document_id": "abc-123",
  "context": "...",
  "source_citations": [
    {
      "source_type": "official_docs",
      "source_name": "API Documentation v2.1",
      "timestamp": "2023-07-08T00:00:00",
      "url": "https://api.example.com/docs"
    },
    {
      "source_type": "team_chat",
      "source_name": "Slack #engineering",
      "timestamp": "2024-01-02T10:00:00"
    }
  ],
  "source_conflicts": [
    {
      "topic": "rate limit",
      "official_answer": "API limit is 100/min",
      "practical_answer": "API crashes after 50/min",
      "recommendation": "Use practical limit...",
      "conflict_severity": "high"
    }
  ]
}
```

## Python SDK Usage

### Basic Example

```python
from caas.storage import DocumentStore, ContextExtractor

store = DocumentStore()

# Create extractor with Pragmatic Truth enabled
extractor = ContextExtractor(
    store,
    enable_citations=True,      # Include source citations
    detect_conflicts=True,      # Detect source conflicts
    enable_time_decay=True      # Prioritize recent info
)

# Extract context
context, metadata = extractor.extract_context(
    document_id="doc-123",
    query="server restart",
    max_tokens=2000
)

# Check for citations
print(f"Citations: {len(metadata['citations'])}")

# Check for conflicts
if metadata['conflicts']:
    print("⚠️ Conflicts detected between sources!")
    for conflict in metadata['conflicts']:
        print(f"  Topic: {conflict['topic']}")
        print(f"  Severity: {conflict['conflict_severity']}")
```

### Advanced: Multi-Source Context

```python
from caas.models import Document, Section, SourceCitation, SourceType

# Add official documentation
official_doc = Document(
    id="doc-official",
    title="Official API Guide",
    sections=[
        Section(
            title="Rate Limits",
            content="API supports 100 req/min",
            source_citation=SourceCitation(
                source_type=SourceType.OFFICIAL_DOCS,
                source_name="API Docs v2.1",
                timestamp="2023-06-01T00:00:00"
            )
        )
    ]
)

# Add team knowledge
slack_doc = Document(
    id="doc-slack",
    title="Team Discussions",
    sections=[
        Section(
            title="Real API Limits",
            content="API actually crashes after 50 req/min",
            source_citation=SourceCitation(
                source_type=SourceType.TEAM_CHAT,
                source_name="Slack #engineering",
                timestamp="2024-01-02T10:00:00"
            )
        )
    ]
)

store.add(official_doc)
store.add(slack_doc)

# Search prioritizes recent practical info
results = store.search(
    "rate limit",
    enable_time_decay=True  # Recent info ranks higher
)
```

## Configuration

### Enable/Disable Features

```python
# Disable citations (faster, less verbose)
extractor = ContextExtractor(
    store,
    enable_citations=False,
    detect_conflicts=False
)

# Enable only citations, not conflict detection
extractor = ContextExtractor(
    store,
    enable_citations=True,
    detect_conflicts=False
)
```

### Time Decay for Practical Truth

```python
# Aggressive time decay (prioritize recent info heavily)
extractor = ContextExtractor(
    store,
    enable_time_decay=True,
    decay_rate=2.0  # Higher = faster decay
)

# Conservative time decay
extractor = ContextExtractor(
    store,
    enable_time_decay=True,
    decay_rate=0.5  # Lower = slower decay
)
```

## Example Scenario

### Scenario: Server Restart Procedures

**Official Documentation (6 months old):**
```
To restart the server, use: service restart
```

**Team Slack (2 days ago):**
```
FYI: 'service restart' doesn't work properly.
Team uses: killall -9 server && ./start.sh
This has been our workaround for months.
```

**Pragmatic AI Response:**
```
📖 Official Documentation says:
   To restart the server, use: service restart
   Source: [Official Docs] Admin Guide (2023-07-01)

🔧 However, team experience shows:
   'service restart' doesn't work properly. The team uses 
   'killall -9 server && ./start.sh' as a workaround.
   Source: [Team Chat] Slack #ops (2024-01-02)

💡 Recommendation:
   Use the team's workaround until the official method is fixed.
   The practical solution is more recent (2 days vs 6 months)
   and reflects actual operational practice.
```

## Benefits

1. **Transparency** - Users know where information comes from
2. **Trustworthiness** - Both official and practical perspectives shown
3. **Time-Awareness** - Recent practical info weighs more than old docs
4. **Conflict Resolution** - Automatically detects and flags disagreements
5. **Pragmatism** - Provides answers that work in practice, not just theory

## Best Practices

### For Document Ingestion

1. **Always specify source_type** when ingesting documents
2. **Include timestamps** for accurate time decay
3. **Add source URLs** for traceability
4. **Use descriptive titles** that indicate the source

### For Context Extraction

1. **Enable citations** by default for transparency
2. **Enable conflict detection** when multiple sources exist
3. **Use time decay** to prioritize recent information
4. **Review conflicts** before making critical decisions

### For Teams

1. **Document practical workarounds** in team channels
2. **Update official docs** when practical and official diverge
3. **Tag source types** explicitly in metadata
4. **Track timestamps** for all knowledge artifacts

## Implementation Details

### Source Detection Algorithm

1. Check explicit metadata (`source_type` field)
2. Analyze document title for keywords
3. Analyze content for source indicators
4. Score each source type based on pattern matches
5. Return highest-scoring type

### Conflict Detection Algorithm

1. Group sections by source type (official vs practical)
2. Find sections with overlapping topics (word overlap)
3. Look for conflicting language patterns
4. Calculate severity based on keywords
5. Generate conflict objects with recommendations

### Citation Formatting

Citations follow this format:
```
[Source Type] Source Name (Timestamp) <URL>
```

Example:
```
[Team Chat] Slack #engineering (2024-01-02) <slack://channel/123>
```

## Testing

Run the test suite:

```bash
# Run Pragmatic Truth tests
python test_pragmatic_truth.py

# Run demo
python demo_pragmatic_truth.py
```

## Future Enhancements

1. **LLM-based conflict detection** - Use language models for smarter conflict detection
2. **Confidence scoring** - Assign confidence scores to sources
3. **Source reliability tracking** - Track which sources are most reliable over time
4. **Automated doc updates** - Suggest updates to official docs based on practical sources
5. **Multi-language support** - Handle citations in multiple languages

## Conclusion

The Pragmatic Truth feature transforms the system from a simple RAG into a **pragmatic engineering assistant** that:

- Respects official documentation
- Prioritizes practical reality
- Maintains full transparency
- Applies engineering judgment
- Adapts over time

It embodies the principle: **Real > Official**, but with **Justice** (proper citation and context).

---

**"The best documentation is the one that works in practice."**
