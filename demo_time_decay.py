"""
Demonstration of the Time-Based Decay Function

"The Half-Life of Truth" - Mathematical gravity that pulls old data down.

This demo shows how the decay function prioritizes recent documents over old ones,
even when the old documents have higher similarity scores.
"""

import uuid
from datetime import datetime, timedelta
from caas.models import Document, ContentFormat, DocumentType, Section
from caas.storage import DocumentStore, ContextExtractor
from caas.decay import calculate_decay_factor


def demo_decay_principle():
    """Demonstrate the core decay principle."""
    print("\n" + "="*70)
    print("THE HALF-LIFE OF TRUTH - Time-Based Decay Demonstration")
    print("="*70)
    
    print("\n📅 Core Principle:")
    print("   'Recency is Relevance' - We don't cut off old data, we apply gravity.")
    print("   Formula: Score = Similarity × (1 / (1 + time_elapsed))")
    
    print("\n🎯 The Challenge:")
    print("   In a living system like software documentation, the truth moves:")
    print("   - 'How to reset the server' in 2021 ≠ 2025")
    print("   - If AI retrieves the 2021 answer (better word match), it fails")
    print("   - We need to prioritize 'What happened latest' over 'What matched best'")
    
    print("\n" + "-"*70)
    print("EXAMPLE: Yesterday's 80% Match vs Last Year's 95% Match")
    print("-"*70)
    
    # Calculate decay factors
    ref_time = datetime.utcnow()
    
    # Recent document (yesterday)
    recent_time = (ref_time - timedelta(days=1)).isoformat()
    recent_decay = calculate_decay_factor(recent_time, ref_time, decay_rate=1.0)
    recent_similarity = 0.80
    recent_score = recent_similarity * recent_decay
    
    # Old document (last year)
    old_time = (ref_time - timedelta(days=365)).isoformat()
    old_decay = calculate_decay_factor(old_time, ref_time, decay_rate=1.0)
    old_similarity = 0.95
    old_score = old_similarity * old_decay
    
    print(f"\n📄 Recent Document (Yesterday):")
    print(f"   Base Similarity:  {recent_similarity:.1%}")
    print(f"   Decay Factor:     {recent_decay:.3f}")
    print(f"   Final Score:      {recent_score:.3f}")
    
    print(f"\n📄 Old Document (Last Year):")
    print(f"   Base Similarity:  {old_similarity:.1%}")
    print(f"   Decay Factor:     {old_decay:.3f}")
    print(f"   Final Score:      {old_score:.3f}")
    
    print(f"\n{'='*70}")
    if recent_score > old_score:
        print("✅ WINNER: Recent Document!")
        print(f"   {recent_score:.3f} > {old_score:.3f}")
        print("   Even with lower similarity, the recent document wins!")
    else:
        print("❌ Old Document won (this shouldn't happen)")
    
    print("="*70)


def demo_search_with_decay():
    """Demonstrate search with time-based decay."""
    print("\n" + "="*70)
    print("SEARCH DEMONSTRATION - Time Decay in Action")
    print("="*70)
    
    store = DocumentStore()
    current_time = datetime.utcnow()
    
    # Create documents about "server reset" from different time periods
    documents = [
        {
            "title": "Server Reset Guide 2026 (Latest)",
            "content": "Modern server reset using cloud-native tools. Reset the server with kubectl.",
            "age_days": 1,
            "description": "Yesterday"
        },
        {
            "title": "Server Reset Guide 2024",
            "content": "Server reset procedures updated for Docker. How to reset the server container.",
            "age_days": 365,
            "description": "1 year ago"
        },
        {
            "title": "Server Reset Guide 2021 (Legacy)",
            "content": "Legacy server reset using manual processes. Server reset steps. Old reset method.",
            "age_days": 365 * 3,
            "description": "3 years ago"
        }
    ]
    
    print("\n📚 Document Corpus:")
    for doc_info in documents:
        doc = Document(
            id=str(uuid.uuid4()),
            title=doc_info["title"],
            content=doc_info["content"],
            format=ContentFormat.TEXT,
            detected_type=DocumentType.TECHNICAL_DOCUMENTATION,
            sections=[
                Section(
                    title="Introduction",
                    content=doc_info["content"],
                    weight=1.0
                )
            ],
            ingestion_timestamp=(current_time - timedelta(days=doc_info["age_days"])).isoformat()
        )
        store.add(doc)
        print(f"   • {doc_info['title']} ({doc_info['description']})")
    
    # Search without decay
    print("\n" + "-"*70)
    print("🔍 Search Results: 'server reset' (WITHOUT time decay)")
    print("-"*70)
    results_no_decay = store.search("server reset", enable_time_decay=False)
    for i, doc in enumerate(results_no_decay, 1):
        score = doc.metadata.get('_search_score', 0)
        print(f"{i}. {doc.title}")
        print(f"   Score: {score:.3f}")
    
    # Search with decay
    print("\n" + "-"*70)
    print("🔍 Search Results: 'server reset' (WITH time decay)")
    print("-"*70)
    results_with_decay = store.search("server reset", enable_time_decay=True)
    for i, doc in enumerate(results_with_decay, 1):
        score = doc.metadata.get('_search_score', 0)
        decay = doc.metadata.get('_decay_factor', 1.0)
        age_days = (current_time - datetime.fromisoformat(doc.ingestion_timestamp)).days
        print(f"{i}. {doc.title}")
        print(f"   Score: {score:.3f} | Decay: {decay:.3f} | Age: {age_days} days")
    
    print("\n✅ Notice: With time decay enabled, the most recent document ranks first,")
    print("   even though older documents may have more keyword matches!")


def demo_context_extraction():
    """Demonstrate context extraction with time decay."""
    print("\n" + "="*70)
    print("CONTEXT EXTRACTION - Time-Weighted Relevance")
    print("="*70)
    
    store = DocumentStore()
    current_time = datetime.utcnow()
    
    # Create a semi-recent document
    doc = Document(
        id=str(uuid.uuid4()),
        title="Authentication API Guide",
        content="Complete guide to authentication endpoints.",
        format=ContentFormat.HTML,
        detected_type=DocumentType.API_DOCUMENTATION,
        sections=[
            Section(
                title="JWT Authentication",
                content="Use JWT tokens for secure authentication. Token expires in 24 hours.",
                weight=2.0,
                importance_score=0.9
            ),
            Section(
                title="OAuth2 Flow",
                content="OAuth2 authorization flow with PKCE. Recommended for web apps.",
                weight=1.8,
                importance_score=0.8
            ),
            Section(
                title="API Keys",
                content="Legacy API keys for backward compatibility. Not recommended for new apps.",
                weight=1.0,
                importance_score=0.4
            )
        ],
        ingestion_timestamp=(current_time - timedelta(days=7)).isoformat()
    )
    
    store.add(doc)
    
    print(f"\n📄 Document: {doc.title}")
    print(f"   Age: 7 days old")
    print(f"   Sections: {len(doc.sections)}")
    
    # Extract without decay
    print("\n" + "-"*70)
    print("📝 Context Extraction WITHOUT time decay:")
    print("-"*70)
    extractor_no_decay = ContextExtractor(store, enable_time_decay=False)
    _, metadata_no_decay = extractor_no_decay.extract_context(doc.id, "authentication")
    
    print(f"Decay Factor: {metadata_no_decay['decay_factor']:.3f}")
    print("Section Weights:")
    for section, weight in metadata_no_decay['weights_applied'].items():
        print(f"   • {section}: {weight:.3f}")
    
    # Extract with decay
    print("\n" + "-"*70)
    print("📝 Context Extraction WITH time decay:")
    print("-"*70)
    extractor_with_decay = ContextExtractor(store, enable_time_decay=True)
    _, metadata_with_decay = extractor_with_decay.extract_context(doc.id, "authentication")
    
    print(f"Decay Factor: {metadata_with_decay['decay_factor']:.3f}")
    print("Section Weights (after decay):")
    for section, weight in metadata_with_decay['weights_applied'].items():
        print(f"   • {section}: {weight:.3f}")
    
    print("\n✅ Notice: Weights are reduced based on document age, ensuring")
    print("   that fresher documents get prioritized in multi-document scenarios!")


def main():
    """Run all demonstrations."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*20 + "TIME-BASED DECAY DEMO" + " "*27 + "║")
    print("║" + " "*15 + "'The Half-Life of Truth'" + " "*29 + "║")
    print("╚" + "="*68 + "╝")
    
    demo_decay_principle()
    demo_search_with_decay()
    demo_context_extraction()
    
    print("\n" + "="*70)
    print("🎉 DEMONSTRATION COMPLETE")
    print("="*70)
    print("\n💡 Key Takeaways:")
    print("   1. Time decay applies 'mathematical gravity' to old data")
    print("   2. Recent content beats old content, even with lower similarity")
    print("   3. We don't delete history - it's still searchable, just deprioritized")
    print("   4. In living systems: Recency IS Relevance")
    print("\n   Formula: Score = Similarity × (1 / (1 + days_elapsed))")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
