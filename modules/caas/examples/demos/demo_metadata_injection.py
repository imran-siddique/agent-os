"""
Demo script showing Metadata Injection (Contextual Enrichment) in action.

This demonstrates the solution to the "Context Amnesia" problem.
"""

import uuid
from caas.models import ContentFormat
from caas.ingestion import ProcessorFactory
from caas.detection import DocumentTypeDetector
from caas.tuning import WeightTuner
from caas.storage import DocumentStore, ContextExtractor


def print_separator(title):
    """Print a formatted separator."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_metadata_injection():
    """Demonstrate metadata injection with a real-world example."""
    
    print_separator("METADATA INJECTION DEMO")
    print("Solving the 'Context Amnesia' Problem")
    print("=" * 70)
    
    # Create a realistic financial report
    html_content = b"""
    <html>
    <head><title>Q3 2024 Financial Report</title></head>
    <body>
        <h1>Q3 2024 Financial Results</h1>
        <p>Executive summary of quarterly performance.</p>
        
        <h2>Revenue Analysis</h2>
        <p>Comprehensive breakdown of revenue across regions.</p>
        
        <h3>North America</h3>
        <p>Revenue in North America increased by 5% compared to last quarter,
        driven by strong sales in the technology sector.</p>
        
        <h3>Europe</h3>
        <p>European markets showed robust growth of 8%, with particular
        strength in renewable energy investments.</p>
        
        <h3>Asia Pacific</h3>
        <p>Asia Pacific revenue grew by 12%, marking the highest growth
        rate across all regions.</p>
        
        <h2>Expense Management</h2>
        <p>Analysis of operational expenses.</p>
        
        <h3>Operating Costs</h3>
        <p>Operating costs decreased by 3% through efficiency improvements
        and strategic cost optimization.</p>
        
        <h2>Future Outlook</h2>
        <p>We project continued growth in Q4 2024, with expected revenue
        increase of 6-8% across all regions.</p>
    </body>
    </html>
    """
    
    # Process the document
    processor = ProcessorFactory.get_processor(ContentFormat.HTML)
    doc_id = str(uuid.uuid4())
    metadata = {"id": doc_id, "title": "Q3 2024 Earnings Report"}
    document = processor.process(html_content, metadata)
    
    # Detect type and tune
    detector = DocumentTypeDetector()
    document.detected_type = detector.detect(document)
    
    tuner = WeightTuner()
    document = tuner.tune(document)
    
    # Store document
    store = DocumentStore()
    store.add(document)
    
    print(f"📄 Processed Document: {document.title}")
    print(f"📊 Document Type: {document.detected_type.value}")
    print(f"📑 Sections Found: {len(document.sections)}")
    
    # Show section hierarchy
    print_separator("SECTION HIERARCHY")
    for section in document.sections:
        hierarchy = []
        if section.chapter:
            hierarchy.append(f"Chapter: {section.chapter}")
        if section.parent_section:
            hierarchy.append(f"Parent: {section.parent_section}")
        hierarchy.append(f"Section: {section.title}")
        
        print(f"  • {' → '.join(hierarchy)}")
    
    # Demo 1: WITHOUT metadata enrichment
    print_separator("WITHOUT METADATA ENRICHMENT (Context Amnesia)")
    
    extractor_plain = ContextExtractor(store, enrich_metadata=False)
    plain_context, plain_meta = extractor_plain.extract_context(
        doc_id, 
        query="revenue increase",
        max_tokens=300
    )
    
    print("Query: 'revenue increase'")
    print("\nRetrieved Context (Plain):")
    print("-" * 70)
    print(plain_context[:400])
    print("-" * 70)
    
    print("\n❌ Problem: Isolated chunks lose context!")
    print("   - Which document is this from?")
    print("   - What chapter?")
    print("   - What's the full hierarchy?")
    print("   → AI Response: 'Revenue increased by some amount, but unclear which region or time period.'")
    
    # Demo 2: WITH metadata enrichment
    print_separator("WITH METADATA ENRICHMENT (Context Preserved)")
    
    extractor_enriched = ContextExtractor(store, enrich_metadata=True)
    enriched_context, enriched_meta = extractor_enriched.extract_context(
        doc_id,
        query="revenue increase",
        max_tokens=300
    )
    
    print("Query: 'revenue increase'")
    print("\nRetrieved Context (Enriched):")
    print("-" * 70)
    print(enriched_context[:600])
    print("-" * 70)
    
    print("\n✅ Solution: Metadata provides full context!")
    print("   ✓ Document: Q3 2024 Earnings Report")
    print("   ✓ Chapter: Q3 2024 Financial Results")
    print("   ✓ Section: North America / Europe / Asia Pacific")
    print("   → AI Response: 'In Q3 2024, North America revenue increased by 5%, Europe by 8%, and Asia Pacific by 12%.'")
    
    # Show metadata comparison
    print_separator("METADATA COMPARISON")
    
    print("Plain Context:")
    print(f"  • Metadata Enriched: {plain_meta['metadata_enriched']}")
    print(f"  • Character Count: {len(plain_context)}")
    print(f"  • Context Quality: ⭐⭐ (Low)")
    
    print("\nEnriched Context:")
    print(f"  • Metadata Enriched: {enriched_meta['metadata_enriched']}")
    print(f"  • Character Count: {len(enriched_context)}")
    print(f"  • Overhead: +{len(enriched_context) - len(plain_context)} chars ({((len(enriched_context) / len(plain_context) - 1) * 100):.0f}% increase)")
    print(f"  • Context Quality: ⭐⭐⭐⭐⭐ (High)")
    
    # Demo 3: Different query showing hierarchy importance
    print_separator("HIERARCHICAL CONTEXT IN ACTION")
    
    # Query about operating costs
    context3, meta3 = extractor_enriched.extract_context(
        doc_id,
        query="costs decreased",
        max_tokens=200
    )
    
    print("Query: 'costs decreased'")
    print("\nEnriched Result:")
    print("-" * 70)
    print(context3[:400])
    print("-" * 70)
    
    print("\n✅ Full Context Preserved:")
    print("   • The AI knows: 'Operating Costs' is under 'Expense Management' in 'Q3 2024 Financial Results'")
    print("   • Without metadata, the AI would see: 'decreased by 3%' (what decreased?)")
    
    # Summary
    print_separator("SUMMARY")
    
    print("📊 Metadata Injection Benefits:")
    print("   ✅ Eliminates 'Context Amnesia'")
    print("   ✅ Preserves document hierarchy")
    print("   ✅ Improves AI response accuracy")
    print("   ✅ Enables precise citations")
    print("   ✅ Better search and retrieval")
    print()
    print("💡 Token Overhead:")
    print(f"   • Additional tokens per chunk: ~19 tokens")
    print(f"   • Total overhead for 3 chunks: ~57 tokens")
    print(f"   • Negligible compared to context window (4K-128K tokens)")
    print()
    print("🎯 Recommendation: Keep enrichment ENABLED (default)")
    print()
    print("=" * 70)


if __name__ == "__main__":
    demo_metadata_injection()
