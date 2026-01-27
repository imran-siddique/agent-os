"""
Demo script showcasing Structure-Aware Indexing.

This demonstrates how the system prioritizes high-value content
(Tier 1) over low-value content (Tier 3) even when semantic
similarity is the same.
"""

import uuid
from caas.models import ContentFormat
from caas.ingestion import ProcessorFactory
from caas.detection import DocumentTypeDetector
from caas.tuning import WeightTuner
from caas.storage import DocumentStore, ContextExtractor


def demo_structure_aware_indexing():
    """
    Demonstrate the 'Flat Chunk Fallacy' solution.
    
    Shows how structure-aware indexing assigns different weights to
    content based on hierarchical importance, not just semantic similarity.
    """
    
    print("=" * 70)
    print("Structure-Aware Indexing Demo")
    print("Solving the 'Flat Chunk Fallacy'")
    print("=" * 70)
    print()
    
    # Create a source code document with different tier content
    print("Creating a Python authentication module...")
    code_content = b"""
# Copyright 2024 - All rights reserved
# This is example code for demonstration purposes

class Authentication:
    '''
    Main authentication class that handles user login.
    This is the primary API contract for authentication services.
    '''
    
    def login(self, username: str, password: str) -> bool:
        '''Authenticate user with credentials.'''
        # TODO: Add rate limiting
        # FIXME: Improve password hashing
        return self._verify_credentials(username, password)
    
    def _verify_credentials(self, username: str, password: str) -> bool:
        '''Internal helper to verify user credentials.'''
        # Implementation details here
        return True

# NOTE: This is a simplified example
# Disclaimer: Not production-ready code
"""
    
    # Process the document
    processor = ProcessorFactory.get_processor(ContentFormat.CODE)
    doc_id = str(uuid.uuid4())
    metadata = {"id": doc_id, "title": "Authentication Module", "language": "python"}
    document = processor.process(code_content, metadata)
    
    # Detect type and tune weights
    detector = DocumentTypeDetector()
    document.detected_type = detector.detect(document)
    
    tuner = WeightTuner()
    document = tuner.tune(document)
    
    print(f"✓ Processed: {document.title}")
    print(f"✓ Document Type: {document.detected_type}")
    print(f"✓ Found {len(document.sections)} sections\n")
    
    # Show tier classifications and weights
    print("=" * 70)
    print("Section Analysis (with Tier Classification)")
    print("=" * 70)
    
    for section in sorted(document.sections, key=lambda s: s.weight, reverse=True):
        tier_name = section.tier.value if section.tier else "unknown"
        tier_label = {
            "tier_1_high": "Tier 1 (HIGH VALUE)",
            "tier_2_medium": "Tier 2 (MEDIUM VALUE)",
            "tier_3_low": "Tier 3 (LOW VALUE)"
        }.get(tier_name, "Unknown")
        
        print(f"\n{section.title}")
        print(f"  Classification: {tier_label}")
        print(f"  Weight: {section.weight}x")
        print(f"  Content Preview: {section.content[:80]}...")
    
    print("\n" + "=" * 70)
    print("Key Insight: The 'Flat Chunk Fallacy' Solution")
    print("=" * 70)
    print()
    print("❌ OLD APPROACH (Flat Chunks):")
    print("   All sections treated equally → Poor search results")
    print("   Comment 'TODO: Add rate limiting' = Class 'Authentication'")
    print()
    print("✅ NEW APPROACH (Structure-Aware):")
    print("   Content weighted by hierarchical importance")
    print(f"   Class Definition (Tier 1): {max(s.weight for s in document.sections if 'class' in s.title.lower())}x weight")
    print(f"   Comments (Tier 3): Would get ~0.5x weight")
    print()
    print("Result: Class definitions are prioritized 4-8x over comments,")
    print("        even if they mention the same keywords!")
    print("=" * 70)
    
    # Store and demonstrate retrieval
    store = DocumentStore()
    store.add(document)
    
    extractor = ContextExtractor(store)
    context, metadata_result = extractor.extract_context(
        doc_id,
        query="authentication",
        max_tokens=500
    )
    
    print("\nContext Extraction (query: 'authentication')")
    print("=" * 70)
    print(f"Sections used (in order): {metadata_result['sections_used']}")
    print(f"\nExtracted Context:\n{context[:400]}...")
    
    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Summary:")
    print("- Class definitions (Tier 1) get 2.0x base weight")
    print("- Function implementations (Tier 2) get 1.0x base weight")
    print("- Comments and TODOs (Tier 3) get 0.5x base weight")
    print("- Retrieval prioritizes high-tier content automatically")
    print("- No manual configuration needed!")
    print()


if __name__ == "__main__":
    demo_structure_aware_indexing()
