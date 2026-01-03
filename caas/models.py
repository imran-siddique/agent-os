"""
Data models for Context-as-a-Service.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Detected document types."""
    LEGAL_CONTRACT = "legal_contract"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    SOURCE_CODE = "source_code"
    RESEARCH_PAPER = "research_paper"
    ARTICLE = "article"
    TUTORIAL = "tutorial"
    API_DOCUMENTATION = "api_documentation"
    UNKNOWN = "unknown"


class ContentFormat(str, Enum):
    """Supported content formats."""
    PDF = "pdf"
    HTML = "html"
    CODE = "code"
    MARKDOWN = "markdown"
    TEXT = "text"


class Section(BaseModel):
    """Represents a section of a document."""
    title: str
    content: str
    weight: float = 1.0
    importance_score: float = 0.0
    start_pos: int = 0
    end_pos: int = 0


class Document(BaseModel):
    """Represents a processed document."""
    id: str
    title: str
    content: str
    format: ContentFormat
    detected_type: DocumentType
    sections: List[Section] = []
    metadata: Dict[str, Any] = {}
    weights: Dict[str, float] = {}
    ingestion_timestamp: Optional[str] = None


class ContextRequest(BaseModel):
    """Request for context extraction."""
    document_id: Optional[str] = None
    query: str
    max_tokens: int = Field(default=2000, gt=0, le=10000)
    include_metadata: bool = True


class ContextResponse(BaseModel):
    """Response containing extracted context."""
    document_id: str
    document_type: DocumentType
    context: str
    sections_used: List[str] = []
    total_tokens: int
    weights_applied: Dict[str, float] = {}
    metadata: Dict[str, Any] = {}
