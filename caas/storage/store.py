"""
Storage module for managing documents and context.
"""

import json
from typing import Dict, Optional, List, Tuple, Any
from pathlib import Path

from caas.models import Document, DocumentType


class DocumentStore:
    """In-memory document store with optional persistence."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize document store.
        
        Args:
            storage_path: Optional path for persistent storage
        """
        self.documents: Dict[str, Document] = {}
        self.storage_path = Path(storage_path) if storage_path else None
        
        if self.storage_path and self.storage_path.exists():
            self._load_from_disk()
    
    def add(self, document: Document) -> str:
        """
        Add a document to the store.
        
        Args:
            document: The document to add
            
        Returns:
            The document ID
        """
        self.documents[document.id] = document
        
        if self.storage_path:
            self._save_to_disk()
        
        return document.id
    
    def get(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            The document if found, None otherwise
        """
        return self.documents.get(document_id)
    
    def list_all(self) -> List[Document]:
        """
        List all documents in the store.
        
        Returns:
            List of all documents
        """
        return list(self.documents.values())
    
    def list_by_type(self, doc_type: DocumentType) -> List[Document]:
        """
        List documents of a specific type.
        
        Args:
            doc_type: The document type to filter by
            
        Returns:
            List of matching documents
        """
        return [
            doc for doc in self.documents.values()
            if doc.detected_type == doc_type
        ]
    
    def delete(self, document_id: str) -> bool:
        """
        Delete a document from the store.
        
        Args:
            document_id: The document ID
            
        Returns:
            True if deleted, False if not found
        """
        if document_id in self.documents:
            del self.documents[document_id]
            
            if self.storage_path:
                self._save_to_disk()
            
            return True
        return False
    
    def search(self, query: str) -> List[Document]:
        """
        Search documents by content or metadata.
        
        Args:
            query: The search query
            
        Returns:
            List of matching documents
        """
        query_lower = query.lower()
        results = []
        
        for doc in self.documents.values():
            # Search in content, title, and section titles
            if (query_lower in doc.content.lower() or
                query_lower in doc.title.lower() or
                any(query_lower in s.title.lower() for s in doc.sections)):
                results.append(doc)
        
        return results
    
    def _save_to_disk(self):
        """Save documents to disk."""
        if not self.storage_path:
            return
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert documents to dict for JSON serialization
        data = {
            doc_id: doc.model_dump()
            for doc_id, doc in self.documents.items()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_from_disk(self):
        """Load documents from disk."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        # Convert dict back to Document objects
        for doc_id, doc_data in data.items():
            self.documents[doc_id] = Document(**doc_data)


class ContextExtractor:
    """Extracts relevant context from documents based on weights."""
    
    def __init__(self, store: DocumentStore):
        """
        Initialize context extractor.
        
        Args:
            store: The document store to use
        """
        self.store = store
    
    def extract_context(
        self,
        document_id: str,
        query: str = "",
        max_tokens: int = 2000
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Extract context from a document.
        
        Args:
            document_id: The document ID
            query: Optional query to focus context extraction
            max_tokens: Maximum tokens to return
            
        Returns:
            Tuple of (context_string, metadata)
        """
        document = self.store.get(document_id)
        if not document:
            return "", {"error": "Document not found"}
        
        # Sort sections by weight (highest first)
        sorted_sections = sorted(
            document.sections,
            key=lambda s: s.weight,
            reverse=True
        )
        
        # If query provided, boost sections matching the query
        if query:
            query_lower = query.lower()
            for section in sorted_sections:
                if query_lower in section.content.lower():
                    section.weight *= 1.5
            
            # Re-sort after query boosting
            sorted_sections.sort(key=lambda s: s.weight, reverse=True)
        
        # Build context string within token limit
        context_parts = []
        sections_used = []
        total_chars = 0
        char_limit = max_tokens * 4  # Approximate: 4 chars per token
        
        for section in sorted_sections:
            section_text = f"\n## {section.title}\n{section.content}\n"
            
            if total_chars + len(section_text) > char_limit:
                # Add partial section if there's room
                remaining = char_limit - total_chars
                if remaining > 100:
                    section_text = section_text[:remaining] + "..."
                    context_parts.append(section_text)
                    sections_used.append(section.title)
                break
            
            context_parts.append(section_text)
            sections_used.append(section.title)
            total_chars += len(section_text)
        
        context = "".join(context_parts)
        
        metadata = {
            "document_id": document_id,
            "document_type": document.detected_type,
            "sections_used": sections_used,
            "weights_applied": {s.title: s.weight for s in sorted_sections},
            "total_sections": len(document.sections),
            "sections_included": len(sections_used),
        }
        
        return context, metadata
