"""
Intelligent Document Analyzer Agent

This agent demonstrates how to use multiple Context-as-a-Service modules together
to create an intelligent document analysis system.

Features:
- Ingests and processes documents (HTML, PDF, Code)
- Applies structure-aware indexing (High/Medium/Low tiers)
- Enriches chunks with metadata (solves context amnesia)
- Applies time-based decay (prioritizes recent content)
- Routes queries efficiently (heuristic routing)
- Manages conversation history (sliding window)
- Tracks sources and detects conflicts (pragmatic truth)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid
from datetime import datetime
from typing import List, Dict, Optional

from caas.models import ContentFormat, DocumentType
from caas.ingestion import ProcessorFactory
from caas.detection import DocumentTypeDetector
from caas.tuning import WeightTuner
from caas.storage import DocumentStore, ContextExtractor
from caas.enrichment import MetadataEnricher
from caas.decay import calculate_decay_factor
from caas.routing import HeuristicRouter
from caas.conversation import ConversationManager
from caas.models import SourceType
from caas.pragmatic_truth import SourceDetector, ConflictDetector


class IntelligentDocumentAnalyzer:
    """
    An intelligent agent that combines all CaaS modules to analyze documents.
    """
    
    def __init__(self, max_conversation_turns: int = 10):
        """
        Initialize the analyzer with all required components.
        
        Args:
            max_conversation_turns: Maximum conversation turns to keep (sliding window)
        """
        self.store = DocumentStore()
        self.extractor = ContextExtractor(
            self.store,
            enable_time_decay=True,
            enable_citations=True,
            detect_conflicts=True,
            enrich_metadata=True
        )
        self.enricher = MetadataEnricher()
        self.router = HeuristicRouter()
        self.conversation = ConversationManager(max_turns=max_conversation_turns)
        self.source_detector = SourceDetector()
        self.conflict_detector = ConflictDetector()
        self.detector = DocumentTypeDetector()
        self.tuner = WeightTuner()
        
        print("🤖 Intelligent Document Analyzer initialized")
        print(f"   - Structure-aware indexing: ✅")
        print(f"   - Metadata enrichment: ✅")
        print(f"   - Time-based decay: ✅")
        print(f"   - Heuristic routing: ✅")
        print(f"   - Sliding window (max {max_conversation_turns} turns): ✅")
        print(f"   - Pragmatic truth tracking: ✅")
    
    def ingest_document(
        self,
        content: bytes,
        format: ContentFormat,
        title: str,
        source_type: SourceType = SourceType.OFFICIAL_DOCS
    ) -> str:
        """
        Ingest a document with full processing pipeline.
        
        Args:
            content: Raw document content
            format: Document format (HTML, PDF, CODE)
            title: Document title
            source_type: Type of source for pragmatic truth
            
        Returns:
            Document ID
        """
        print(f"\n📤 Ingesting document: {title}")
        
        # Process document
        processor = ProcessorFactory.get_processor(format)
        doc_id = str(uuid.uuid4())
        metadata = {
            "id": doc_id,
            "title": title,
            "ingestion_timestamp": datetime.utcnow().isoformat()
        }
        document = processor.process(content, metadata)
        
        # Detect type
        document.detected_type = self.detector.detect(document)
        print(f"   ✓ Detected type: {document.detected_type}")
        
        # Apply structure-aware tuning
        document = self.tuner.tune(document)
        print(f"   ✓ Applied structure-aware weights (Tier 1/2/3)")
        
        # Store document
        self.store.add(document)
        
        print(f"   ✓ Document ingested with ID: {doc_id}")
        print(f"   ✓ Sections: {len(document.sections)}")
        print(f"   ✓ Source type: {source_type.value}")
        
        return doc_id
    
    def analyze_query(self, user_query: str) -> Dict:
        """
        Analyze a query and route it appropriately.
        
        Args:
            user_query: User's question or query
            
        Returns:
            Analysis results with routing decision
        """
        print(f"\n🔍 Analyzing query: \"{user_query}\"")
        
        # Route query using heuristic router
        routing_decision = self.router.route(user_query)
        print(f"   ✓ Routing decision: {routing_decision.model_tier.value}")
        print(f"   ✓ Suggested model: {routing_decision.suggested_model}")
        print(f"   ✓ Estimated cost: {routing_decision.estimated_cost}")
        
        return {
            "query": user_query,
            "routing": routing_decision,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def extract_context(
        self,
        document_id: str,
        query: str,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Extract context from document with all enhancements.
        
        Args:
            document_id: Document to extract from
            query: Search query
            max_tokens: Maximum tokens to extract
            
        Returns:
            Extracted context with metadata
        """
        print(f"\n📊 Extracting context from document: {document_id}")
        print(f"   Query: \"{query}\"")
        
        # Extract context with all features enabled
        context, metadata = self.extractor.extract_context(
            document_id=document_id,
            query=query,
            max_tokens=max_tokens
        )
        
        print(f"   ✓ Context extracted: {len(context)} chars")
        print(f"   ✓ Sections used: {len(metadata.get('sections_used', []))}")
        print(f"   ✓ Citations: {len(metadata.get('citations', []))}")
        
        if metadata.get('conflicts'):
            print(f"   ⚠️  Conflicts detected: {len(metadata['conflicts'])}")
        
        return {
            "context": context,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def chat(self, user_message: str, ai_response: str) -> Dict:
        """
        Add a conversation turn (sliding window management).
        
        Args:
            user_message: User's message
            ai_response: AI's response
            
        Returns:
            Conversation statistics
        """
        turn_id = self.conversation.add_turn(user_message, ai_response)
        stats = self.conversation.get_statistics()
        
        print(f"\n💬 Conversation turn added (ID: {turn_id[:8]}...)")
        print(f"   ✓ Current turns: {stats['current_turns']}/{stats['max_turns']}")
        print(f"   ✓ Total ever: {stats['total_turns_ever']}")
        
        if stats['deleted_turns'] > 0:
            print(f"   ✓ Deleted (FIFO): {stats['deleted_turns']}")
        
        return stats
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history (last N turns)."""
        return self.conversation.get_conversation_history()
    
    def analyze_corpus(self) -> Dict:
        """
        Analyze the entire corpus for insights.
        
        Returns:
            Corpus analysis results
        """
        print(f"\n📚 Analyzing corpus...")
        
        all_docs = self.store.list_all()
        doc_types = {}
        for doc in all_docs:
            doc_type = doc.detected_type if doc.detected_type else DocumentType.UNKNOWN
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        analysis = {
            "total_documents": len(all_docs),
            "document_types": doc_types,
            "suggestions": []
        }
        
        print(f"   ✓ Total documents: {analysis['total_documents']}")
        print(f"   ✓ Document types: {len(analysis['document_types'])}")
        
        return analysis


def demo_comprehensive_workflow():
    """Demonstrate a comprehensive workflow using all modules."""
    print("=" * 70)
    print("🤖 Intelligent Document Analyzer - Comprehensive Demo")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = IntelligentDocumentAnalyzer(max_conversation_turns=5)
    
    # Sample documents
    doc1_content = b"""
    <html>
    <head><title>API Authentication Guide</title></head>
    <body>
        <h1>Authentication API</h1>
        <h2>Official Documentation</h2>
        <p>The API officially supports 100 requests per minute.</p>
        <p>Use Bearer tokens for authentication.</p>
        
        <h2>Endpoints</h2>
        <h3>POST /auth/login</h3>
        <p>Authenticate a user and receive a token.</p>
    </body>
    </html>
    """
    
    doc2_content = b"""
    <html>
    <head><title>Team Chat Log</title></head>
    <body>
        <h1>Engineering Chat - Jan 2025</h1>
        <p>@john: FYI, the API crashes after 50 requests. We've hit this multiple times.</p>
        <p>@sarah: Yeah, the official limit is 100, but in practice it's 50.</p>
        <p>@mike: We should update the docs, but for now just stay under 50.</p>
    </body>
    </html>
    """
    
    code_content = b"""
def authenticate_user(username: str, password: str):
    '''Authenticate user with credentials.'''
    # Critical: Always use secure password hashing
    return verify_credentials(username, password)

class AuthenticationService:
    '''Main authentication service.'''
    
    def login(self, username: str, password: str):
        '''Login endpoint.'''
        # TODO: Add rate limiting
        return authenticate_user(username, password)
"""
    
    # 1. Ingest documents with different source types
    doc_id_1 = analyzer.ingest_document(
        doc1_content,
        ContentFormat.HTML,
        "API Authentication - Official Docs",
        SourceType.OFFICIAL_DOCS
    )
    
    doc_id_2 = analyzer.ingest_document(
        doc2_content,
        ContentFormat.HTML,
        "Engineering Chat - API Issues",
        SourceType.TEAM_CHAT
    )
    
    doc_id_3 = analyzer.ingest_document(
        code_content,
        ContentFormat.CODE,
        "Authentication Service Code",
        SourceType.CODE_COMMENTS
    )
    
    # 2. Analyze corpus
    corpus_analysis = analyzer.analyze_corpus()
    
    # 3. Route different types of queries
    print("\n" + "=" * 70)
    print("🎯 Query Routing Examples")
    print("=" * 70)
    
    analyzer.analyze_query("Hi there!")  # Should route to canned
    analyzer.analyze_query("What is authentication?")  # Should route to fast
    analyzer.analyze_query("Analyze the authentication flow and compare with best practices")  # Should route to smart
    
    # 4. Extract context with all features
    print("\n" + "=" * 70)
    print("📊 Context Extraction with Conflict Detection")
    print("=" * 70)
    
    # Query about API limits - should detect conflict between docs and chat
    result = analyzer.extract_context(
        doc_id_1,
        "What is the API rate limit?",
        max_tokens=1000
    )
    
    print("\n--- Context Preview ---")
    print(result['context'][:500] + "...")
    
    # 5. Simulate conversation
    print("\n" + "=" * 70)
    print("💬 Conversation Management (Sliding Window)")
    print("=" * 70)
    
    analyzer.chat(
        "How do I authenticate?",
        "Use the POST /auth/login endpoint with your credentials."
    )
    
    analyzer.chat(
        "What about rate limits?",
        "Officially 100 req/min, but team reports issues at 50."
    )
    
    analyzer.chat(
        "Can you show me code?",
        "Check the AuthenticationService class in the codebase."
    )
    
    # Get conversation history
    history = analyzer.get_conversation_history()
    print(f"\n📝 Conversation history: {len(history)} turns retained")
    
    # 6. Final summary
    print("\n" + "=" * 70)
    print("✅ Demo Complete - All Modules Working Together!")
    print("=" * 70)
    print("\n✨ What we demonstrated:")
    print("   1. Structure-aware indexing (High/Medium/Low tiers)")
    print("   2. Metadata enrichment (no context amnesia)")
    print("   3. Time-based decay (recency is relevance)")
    print("   4. Heuristic routing (fast/smart/canned)")
    print("   5. Sliding window conversation (FIFO, no summarization)")
    print("   6. Pragmatic truth (source tracking & conflict detection)")


if __name__ == "__main__":
    demo_comprehensive_workflow()
