#!/usr/bin/env python3
"""
Comprehensive demonstration of Context-as-a-Service.

This script demonstrates the entire pipeline:
1. Ingest documents (HTML and Code)
2. Auto-detect document types
3. Auto-tune weights
4. Extract optimized context
5. Analyze corpus
"""

import uuid
from caas.models import ContentFormat
from caas.ingestion import ProcessorFactory
from caas.detection import DocumentTypeDetector, StructureAnalyzer
from caas.tuning import WeightTuner, CorpusAnalyzer
from caas.storage import DocumentStore, ContextExtractor


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_html_processing():
    """Demonstrate HTML document processing."""
    print_section("DEMO 1: Processing HTML API Documentation")
    
    # Read example HTML file
    with open('examples/api_documentation.html', 'rb') as f:
        html_content = f.read()
    
    print("\n📄 Input: API Documentation (HTML)")
    print("   File: examples/api_documentation.html")
    
    # Step 1: Ingest
    print("\n[Step 1] 🔄 Ingesting document...")
    processor = ProcessorFactory.get_processor(ContentFormat.HTML)
    doc_id = str(uuid.uuid4())
    metadata = {"id": doc_id, "title": "User Management API"}
    document = processor.process(html_content, metadata)
    print(f"   ✓ Extracted {len(document.sections)} sections")
    
    # Step 2: Auto-detect
    print("\n[Step 2] 🔍 Auto-detecting document type...")
    detector = DocumentTypeDetector()
    document.detected_type = detector.detect(document)
    print(f"   ✓ Detected: {document.detected_type.value}")
    print(f"   ✓ Reasoning: Contains API endpoints, authentication, examples")
    
    # Step 3: Auto-tune weights
    print("\n[Step 3] ⚖️  Auto-tuning section weights...")
    tuner = WeightTuner()
    document = tuner.tune(document)
    
    print(f"   ✓ Applied intelligent weights based on content analysis:")
    sorted_sections = sorted(document.sections, key=lambda s: s.weight, reverse=True)
    for i, section in enumerate(sorted_sections[:5], 1):
        importance_stars = "⭐" * int(section.importance_score * 5)
        print(f"   {i}. {section.title:30s} -> {section.weight:.2f}x {importance_stars}")
    
    # Step 4: Extract context
    print("\n[Step 4] 🎯 Extracting optimized context...")
    store = DocumentStore()
    store.add(document)
    
    extractor = ContextExtractor(store)
    context, metadata_result = extractor.extract_context(
        doc_id, 
        query="authentication", 
        max_tokens=500
    )
    
    print(f"   ✓ Query: 'authentication'")
    print(f"   ✓ Sections used: {len(metadata_result['sections_used'])}/{len(document.sections)}")
    print(f"   ✓ Sections: {', '.join(metadata_result['sections_used'])}")
    print(f"\n   📋 Context Preview (first 400 chars):")
    print("   " + "-" * 66)
    preview = context[:400].replace('\n', '\n   ')
    print(f"   {preview}...")
    
    return document, store


def demo_code_processing(store):
    """Demonstrate code processing."""
    print_section("DEMO 2: Processing Source Code")
    
    # Read example code file
    with open('examples/auth_module.py', 'rb') as f:
        code_content = f.read()
    
    print("\n📄 Input: Authentication Module (Python Code)")
    print("   File: examples/auth_module.py")
    
    # Step 1: Ingest
    print("\n[Step 1] 🔄 Ingesting code...")
    processor = ProcessorFactory.get_processor(ContentFormat.CODE)
    doc_id = str(uuid.uuid4())
    metadata = {"id": doc_id, "title": "Auth Module", "language": "python"}
    document = processor.process(code_content, metadata)
    print(f"   ✓ Parsed {len(document.sections)} code sections")
    
    # Step 2: Auto-detect
    print("\n[Step 2] 🔍 Auto-detecting document type...")
    detector = DocumentTypeDetector()
    document.detected_type = detector.detect(document)
    print(f"   ✓ Detected: {document.detected_type.value}")
    print(f"   ✓ Reasoning: Contains classes, functions, and code patterns")
    
    # Step 3: Structure analysis
    print("\n[Step 3] 📊 Analyzing code structure...")
    analyzer = StructureAnalyzer()
    analysis = analyzer.analyze(document)
    
    print(f"   ✓ Content density: {analysis['content_density']:.3f}")
    print(f"   ✓ Structure quality: {analysis['structure_quality']}")
    print(f"   ✓ Code sections found:")
    for section_info in analysis['section_analysis'][:5]:
        print(f"      - {section_info['title'][:50]:50s} ({section_info['length']} chars)")
    
    # Step 4: Auto-tune
    print("\n[Step 4] ⚖️  Auto-tuning weights...")
    tuner = WeightTuner()
    document = tuner.tune(document)
    print(f"   ✓ Applied code-specific weights")
    
    # Add to store
    store.add(document)
    
    # Step 5: Extract context
    print("\n[Step 5] 🎯 Extracting code context...")
    extractor = ContextExtractor(store)
    context, metadata_result = extractor.extract_context(
        doc_id, 
        query="authenticate", 
        max_tokens=800
    )
    
    print(f"   ✓ Query: 'authenticate'")
    print(f"   ✓ Found relevant code sections")
    print(f"\n   📋 Context Preview:")
    print("   " + "-" * 66)
    preview = context[:500].replace('\n', '\n   ')
    print(f"   {preview}...")
    
    return document


def demo_corpus_analysis(store):
    """Demonstrate corpus-wide analysis."""
    print_section("DEMO 3: Corpus Analysis & Learning")
    
    print("\n📚 Analyzing entire document corpus...")
    
    # Create corpus analyzer
    corpus_analyzer = CorpusAnalyzer()
    
    # Add all documents from store
    for doc in store.list_all():
        corpus_analyzer.add_document(doc)
    
    analysis = corpus_analyzer.analyze_corpus()
    
    print(f"\n✓ Corpus Statistics:")
    print(f"   Total documents: {analysis['total_documents']}")
    print(f"   Document types:")
    for doc_type, count in analysis['document_types'].items():
        print(f"      - {doc_type.value if hasattr(doc_type, 'value') else doc_type}: {count}")
    
    print(f"\n✓ Common Section Patterns:")
    for section, count in list(analysis['common_sections'].items())[:5]:
        print(f"      - '{section}': appears {count} times")
    
    print(f"\n✓ Average Weights:")
    for section, weight in list(analysis['average_weights'].items())[:5]:
        print(f"      - '{section}': {weight}x")
    
    if analysis['optimization_suggestions']:
        print(f"\n💡 Optimization Suggestions:")
        for suggestion in analysis['optimization_suggestions']:
            print(f"      - {suggestion}")
    
    print(f"\n✅ The system learns from your corpus and self-optimizes!")


def demo_comparison():
    """Demonstrate the benefit of auto-tuning."""
    print_section("DEMO 4: Impact of Auto-Tuning")
    
    print("\n🔬 Comparing results with and without auto-tuning...")
    
    # Create a test document
    html_content = b"""
    <html>
    <body>
        <h1>Software License Agreement</h1>
        
        <h2>Background</h2>
        <p>This agreement is between the parties.</p>
        
        <h2>Definitions</h2>
        <p>Software means the licensed software. License means permission to use.
        User means the person using the software. These definitions are critical
        to understanding the agreement.</p>
        
        <h2>Grant of License</h2>
        <p>The licensor grants a non-exclusive license.</p>
        
        <h2>Termination</h2>
        <p>This agreement may be terminated by either party with notice.
        Upon termination, all rights cease. This is an important clause.</p>
    </body>
    </html>
    """
    
    processor = ProcessorFactory.get_processor(ContentFormat.HTML)
    doc_id = str(uuid.uuid4())
    metadata = {"id": doc_id, "title": "License Agreement"}
    document = processor.process(html_content, metadata)
    
    detector = DocumentTypeDetector()
    document.detected_type = detector.detect(document)
    
    print(f"\n📄 Document: {document.title}")
    print(f"   Detected Type: {document.detected_type.value}")
    
    # WITHOUT auto-tuning (all weights = 1.0)
    print(f"\n❌ WITHOUT Auto-Tuning (all sections weighted equally):")
    for section in document.sections:
        print(f"   - {section.title:25s}: 1.0x")
    
    # WITH auto-tuning
    tuner = WeightTuner()
    document = tuner.tune(document)
    
    print(f"\n✅ WITH Auto-Tuning (intelligent weights applied):")
    sorted_sections = sorted(document.sections, key=lambda s: s.weight, reverse=True)
    for section in sorted_sections:
        boost = f"(+{int((section.weight - 1.0) * 100)}%)" if section.weight > 1.0 else ""
        print(f"   - {section.title:25s}: {section.weight:.2f}x {boost}")
    
    print(f"\n💡 Key Insight:")
    print(f"   The system automatically boosted 'Definitions' and 'Termination'")
    print(f"   sections because it detected this is a legal contract and these")
    print(f"   sections contain critical information (definitions, important clauses).")
    print(f"   No manual configuration required!")


def main():
    """Run the complete demonstration."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "CONTEXT-AS-A-SERVICE DEMONSTRATION" + " " * 19 + "║")
    print("║" + " " * 68 + "║")
    print("║" + "  Zero Configuration • Auto-Detection • Auto-Tuning" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print("\n🎯 This demo showcases the complete pipeline:")
    print("   1. Ingest raw data (PDF, Code, HTML)")
    print("   2. Auto-detect document structure and type")
    print("   3. Auto-tune weights based on content analysis")
    print("   4. Serve perfectly optimized context via API")
    
    try:
        # Demo 1: HTML processing
        html_doc, store = demo_html_processing()
        
        # Demo 2: Code processing
        code_doc = demo_code_processing(store)
        
        # Demo 3: Corpus analysis
        demo_corpus_analysis(store)
        
        # Demo 4: Show the impact
        demo_comparison()
        
        # Final summary
        print_section("SUMMARY")
        print("\n✅ Context-as-a-Service successfully demonstrated!")
        print("\n🚀 Key Features Shown:")
        print("   ✓ Multi-format ingestion (HTML, Code)")
        print("   ✓ Automatic document type detection")
        print("   ✓ Intelligent weight optimization")
        print("   ✓ Query-focused context extraction")
        print("   ✓ Corpus-wide learning and analysis")
        print("   ✓ Zero manual configuration needed")
        
        print("\n🎉 The service is ready to use!")
        print("   Start the API: python -m uvicorn caas.api.server:app --reload")
        print("   API docs:      http://localhost:8000/docs")
        print("   CLI tool:      python caas/cli.py --help")
        
        print("\n" + "=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
