"""
Demo: Pragmatic Truth (Real > Official)

Demonstrates how the system handles conflicts between official documentation
and practical reality, providing transparent citations and both perspectives.
"""

import uuid
from datetime import datetime, timedelta

from caas.models import (
    ContentFormat,
    DocumentType,
    SourceType,
    SourceCitation,
    Section,
    Document,
)
from caas.storage import DocumentStore, ContextExtractor
from caas.pragmatic_truth import CitationFormatter


def create_official_api_doc() -> Document:
    """Create an official API documentation document."""
    doc_id = str(uuid.uuid4())
    return Document(
        id=doc_id,
        title="API Documentation v2.1 - Rate Limits",
        content="Official documentation for API rate limits.",
        format=ContentFormat.HTML,
        detected_type=DocumentType.API_DOCUMENTATION,
        sections=[
            Section(
                title="Rate Limits",
                content=(
                    "The API supports up to 100 requests per minute per API key. "
                    "This limit is enforced at the gateway level and is documented "
                    "in the official specification. Exceeding this limit will result "
                    "in HTTP 429 (Too Many Requests) responses."
                ),
                weight=1.8,
                source_citation=SourceCitation(
                    source_type=SourceType.OFFICIAL_DOCS,
                    source_name="API Documentation v2.1",
                    source_url="https://api.example.com/docs/rate-limits",
                    timestamp=(datetime.utcnow() - timedelta(days=180)).isoformat()
                )
            ),
            Section(
                title="Error Handling",
                content=(
                    "When rate limits are exceeded, the API returns a 429 status code "
                    "with a Retry-After header indicating when requests can resume."
                ),
                weight=1.5,
                source_citation=SourceCitation(
                    source_type=SourceType.OFFICIAL_DOCS,
                    source_name="API Documentation v2.1",
                    source_url="https://api.example.com/docs/errors",
                    timestamp=(datetime.utcnow() - timedelta(days=180)).isoformat()
                )
            ),
        ],
        metadata={"source_type": "official_docs"},
        ingestion_timestamp=(datetime.utcnow() - timedelta(days=180)).isoformat()
    )


def create_slack_conversation() -> Document:
    """Create a document from Slack team conversations."""
    doc_id = str(uuid.uuid4())
    return Document(
        id=doc_id,
        title="Slack #engineering - API Stability Issues",
        content="Team conversation about API rate limit issues.",
        format=ContentFormat.TEXT,
        detected_type=DocumentType.UNKNOWN,
        sections=[
            Section(
                title="Real Rate Limit Issue",
                content=(
                    "Hey team, just a heads up - the API actually crashes after about "
                    "50 requests per minute, not 100 like the docs say. We've hit this "
                    "in production multiple times this week. The official limit is 100, "
                    "but in practice the server becomes unstable around 50-60. "
                    "Use 50 as your actual limit until this is fixed."
                ),
                weight=2.0,  # High weight because it's recent practical info
                source_citation=SourceCitation(
                    source_type=SourceType.TEAM_CHAT,
                    source_name="Slack #engineering",
                    source_url="slack://channel/engineering/msg456789",
                    timestamp=(datetime.utcnow() - timedelta(days=2)).isoformat(),
                    excerpt="API crashes after 50 requests, not 100..."
                )
            ),
            Section(
                title="Workaround",
                content=(
                    "For now, we're using a circuit breaker pattern with a 45 req/min "
                    "limit in our client library. It's not ideal, but it prevents the "
                    "crashes. Filed ticket #3421 to get this fixed on the backend."
                ),
                weight=1.7,
                source_citation=SourceCitation(
                    source_type=SourceType.TEAM_CHAT,
                    source_name="Slack #engineering",
                    source_url="slack://channel/engineering/msg456790",
                    timestamp=(datetime.utcnow() - timedelta(days=2)).isoformat()
                )
            ),
        ],
        metadata={"source_type": "team_chat"},
        ingestion_timestamp=(datetime.utcnow() - timedelta(days=2)).isoformat()
    )


def create_runbook() -> Document:
    """Create an operational runbook document."""
    doc_id = str(uuid.uuid4())
    return Document(
        id=doc_id,
        title="Production Runbook - API Issues",
        content="Operational procedures for handling API issues.",
        format=ContentFormat.MARKDOWN,
        detected_type=DocumentType.TUTORIAL,
        sections=[
            Section(
                title="Rate Limit Troubleshooting",
                content=(
                    "If experiencing 429 errors:\n"
                    "1. Check current request rate (should be under 50/min, NOT 100)\n"
                    "2. Implement exponential backoff\n"
                    "3. The documented limit of 100/min causes server instability\n"
                    "4. Keep traffic under 50/min for reliable operation"
                ),
                weight=1.9,
                source_citation=SourceCitation(
                    source_type=SourceType.RUNBOOK,
                    source_name="Production Runbook",
                    source_url="https://wiki.company.com/runbooks/api",
                    timestamp=(datetime.utcnow() - timedelta(days=30)).isoformat()
                )
            ),
        ],
        metadata={"source_type": "runbook"},
        ingestion_timestamp=(datetime.utcnow() - timedelta(days=30)).isoformat()
    )


def demo_pragmatic_truth():
    """Demonstrate the Pragmatic Truth feature."""
    print("=" * 80)
    print("DEMO: Pragmatic Truth (Real > Official)")
    print("=" * 80)
    print()
    print("Scenario: API Rate Limits")
    print("-" * 80)
    print("Official docs say: 100 requests/minute")
    print("Team experience shows: Crashes after 50 requests/minute")
    print()
    print("The system should present BOTH with proper citations.")
    print("=" * 80)
    print()
    
    # Create document store
    store = DocumentStore()
    
    # Add documents from different sources
    print("📥 Ingesting documents from multiple sources...")
    official_doc = create_official_api_doc()
    store.add(official_doc)
    print(f"  ✓ Official Documentation (6 months old)")
    
    slack_doc = create_slack_conversation()
    store.add(slack_doc)
    print(f"  ✓ Slack Conversation (2 days old)")
    
    runbook_doc = create_runbook()
    store.add(runbook_doc)
    print(f"  ✓ Production Runbook (1 month old)")
    print()
    
    # Scenario 1: Extract from official docs only
    print("=" * 80)
    print("Scenario 1: Query Official Documentation Only")
    print("=" * 80)
    extractor = ContextExtractor(
        store,
        enrich_metadata=False,
        enable_citations=True,
        detect_conflicts=False
    )
    
    context, metadata = extractor.extract_context(
        official_doc.id,
        query="rate limit",
        max_tokens=1000
    )
    
    print("RESPONSE:")
    print("-" * 80)
    print(context)
    print()
    
    # Scenario 2: Query with conflict detection across all sources
    print("=" * 80)
    print("Scenario 2: Search Across All Sources (with Time Decay & Conflict Detection)")
    print("=" * 80)
    
    # Search for relevant documents
    results = store.search("rate limit", enable_time_decay=True)
    print(f"Found {len(results)} relevant documents:")
    for doc in results:
        decay = doc.metadata.get('_decay_factor', 1.0)
        score = doc.metadata.get('_search_score', 0)
        print(f"  - {doc.title}")
        print(f"    Score: {score:.3f}, Decay Factor: {decay:.3f}")
    print()
    
    # Extract context from most recent (Slack conversation)
    if results:
        most_recent_doc = results[0]  # Time decay ensures recent docs rank higher
        extractor_with_conflicts = ContextExtractor(
            store,
            enrich_metadata=False,
            enable_citations=True,
            detect_conflicts=True
        )
        
        # Temporarily combine sections from all docs for conflict detection
        # In a real system, you'd have a multi-document context extractor
        combined_sections = []
        for doc in results[:2]:  # Top 2 docs
            combined_sections.extend(doc.sections)
        
        context, metadata = extractor_with_conflicts.extract_context(
            most_recent_doc.id,
            query="rate limit",
            max_tokens=2000
        )
        
        print("RESPONSE WITH PRAGMATIC TRUTH:")
        print("-" * 80)
        print(context)
        print()
    
    # Scenario 3: Show how AI should respond
    print("=" * 80)
    print("Scenario 3: Ideal AI Response (Pragmatic Truth)")
    print("=" * 80)
    print()
    print("🤖 AI Response:")
    print("-" * 80)
    print("""
**Rate Limit Information**

📖 **Official Documentation says:**
The API limit is 100 requests per minute per API key, as documented in the 
official specification.
Source: [Official Docs] API Documentation v2.1 (2023-07-08) <https://api.example.com/docs/rate-limits>

🔧 **However, team experience shows:**
The API actually crashes after about 50 requests per minute in production, not 100. 
This has been observed multiple times and confirmed by the engineering team.
Source: [Team Chat] Slack #engineering (2024-01-02) <slack://channel/engineering/msg456789>

💡 **Recommendation:**
Use 50 requests/minute as your practical limit, not the official 100. The official 
documentation may be outdated or optimistic. The production runbook also recommends 
staying under 50/min for reliable operation.

**Why trust the practical limit?**
1. Recent observations (2 days ago) vs old docs (6 months ago)
2. Multiple engineers confirmed the issue
3. Production runbook updated to reflect reality
4. Time-based decay prioritizes recent practical experience

**Action Items:**
- Configure your client with a 45-50 req/min limit
- Implement circuit breaker pattern
- Monitor ticket #3421 for backend fix
    """)
    print("-" * 80)
    print()
    
    print("=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print("  1. ✓ System tracks source types (official, chat, logs, etc.)")
    print("  2. ✓ Citations are transparent and include timestamps")
    print("  3. ✓ Conflicts are detected and presented clearly")
    print("  4. ✓ Time decay prioritizes recent information")
    print("  5. ✓ Both perspectives are shown with recommendations")
    print()
    print("This is Pragmatic Truth: Real > Official, but with full transparency.")
    print("=" * 80)


if __name__ == "__main__":
    demo_pragmatic_truth()
