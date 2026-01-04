"""
REST API for Context-as-a-Service.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from caas.models import (
    Document,
    DocumentType,
    ContentFormat,
    ContextRequest,
    ContextResponse,
)
from caas.ingestion import ProcessorFactory
from caas.detection import DocumentTypeDetector, StructureAnalyzer
from caas.tuning import WeightTuner, CorpusAnalyzer
from caas.storage import DocumentStore, ContextExtractor


# Initialize FastAPI app
app = FastAPI(
    title="Context-as-a-Service",
    description="Intelligent context extraction and serving",
    version="0.1.0"
)

# Initialize components
document_store = DocumentStore()
detector = DocumentTypeDetector()
structure_analyzer = StructureAnalyzer()
weight_tuner = WeightTuner()
corpus_analyzer = CorpusAnalyzer()
# Note: context_extractor is created per-request with user-specified decay settings


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Context-as-a-Service",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "ingest": "/ingest",
            "documents": "/documents",
            "context": "/context/{document_id}",
            "analyze": "/analyze/{document_id}",
            "corpus": "/corpus/analyze",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    format: ContentFormat = Form(...),
    title: Optional[str] = Form(None)
):
    """
    Ingest a document for processing.
    
    The service will:
    1. Process the raw content
    2. Auto-detect the document type and structure
    3. Auto-tune weights for sections
    4. Store the processed document
    
    Args:
        file: The file to ingest
        format: The file format (pdf, html, code)
        title: Optional title for the document
    
    Returns:
        Processed document information
    """
    try:
        # Read file content
        content = await file.read()
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Process the document
        processor = ProcessorFactory.get_processor(format)
        metadata = {
            "id": doc_id,
            "title": title or file.filename,
            "filename": file.filename,
        }
        
        document = processor.process(content, metadata)
        
        # Auto-detect document type
        detected_type = detector.detect(document)
        document.detected_type = detected_type
        
        # Auto-tune weights
        document = weight_tuner.tune(document)
        
        # Add timestamp
        document.ingestion_timestamp = datetime.utcnow().isoformat()
        
        # Store document
        document_store.add(document)
        
        # Add to corpus analyzer
        corpus_analyzer.add_document(document)
        
        return {
            "document_id": document.id,
            "title": document.title,
            "detected_type": document.detected_type,
            "format": document.format,
            "sections_found": len(document.sections),
            "weights": document.weights,
            "status": "ingested"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/documents")
async def list_documents(doc_type: Optional[DocumentType] = None):
    """
    List all documents or filter by type.
    
    Args:
        doc_type: Optional document type filter
    
    Returns:
        List of documents
    """
    if doc_type:
        documents = document_store.list_by_type(doc_type)
    else:
        documents = document_store.list_all()
    
    return {
        "total": len(documents),
        "documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "type": doc.detected_type,
                "format": doc.format,
                "sections": len(doc.sections),
                "timestamp": doc.ingestion_timestamp,
            }
            for doc in documents
        ]
    }


@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Get detailed information about a specific document.
    
    Args:
        document_id: The document ID
    
    Returns:
        Document details
    """
    document = document_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "title": document.title,
        "type": document.detected_type,
        "format": document.format,
        "sections": [
            {
                "title": s.title,
                "weight": s.weight,
                "importance": s.importance_score,
                "length": len(s.content),
            }
            for s in document.sections
        ],
        "metadata": document.metadata,
        "weights": document.weights,
        "timestamp": document.ingestion_timestamp,
    }


@app.post("/context/{document_id}")
async def get_context(document_id: str, request: ContextRequest):
    """
    Get optimized context from a document.
    
    This endpoint returns the most relevant context based on:
    - Auto-tuned section weights
    - Time-based decay (prioritizes recent content)
    - Optional query for focused extraction
    - Token limits
    
    Time Decay Formula: Score = Base_Weight * (1 / (1 + days_elapsed * decay_rate))
    Result: Recent documents rank higher than old documents, even with lower similarity.
    
    Args:
        document_id: The document ID
        request: Context request parameters (includes enable_time_decay, decay_rate)
    
    Returns:
        Optimized context with time-weighted relevance
    """
    document = document_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Create context extractor with requested decay settings
    extractor = ContextExtractor(
        document_store,
        enrich_metadata=request.include_metadata,
        enable_time_decay=request.enable_time_decay,
        decay_rate=request.decay_rate
    )
    
    # Extract context
    context, metadata = extractor.extract_context(
        document_id,
        request.query,
        request.max_tokens
    )
    
    # Estimate tokens (rough approximation)
    estimated_tokens = len(context) // 4
    
    response = ContextResponse(
        document_id=document_id,
        document_type=document.detected_type,
        context=context,
        sections_used=metadata.get("sections_used", []),
        total_tokens=estimated_tokens,
        weights_applied=metadata.get("weights_applied", {}),
        metadata=metadata if request.include_metadata else {}
    )
    
    return response


@app.get("/analyze/{document_id}")
async def analyze_document(document_id: str):
    """
    Analyze a document's structure and content.
    
    Args:
        document_id: The document ID
    
    Returns:
        Analysis results
    """
    document = document_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Perform structure analysis
    structure = detector.detect_structure(document)
    analysis = structure_analyzer.analyze(document)
    
    return {
        "document_id": document_id,
        "structure": structure,
        "analysis": analysis,
    }


@app.get("/corpus/analyze")
async def analyze_corpus():
    """
    Analyze the entire corpus of documents.
    
    Returns insights about:
    - Document type distribution
    - Common section patterns
    - Average weights
    - Optimization suggestions
    
    Returns:
        Corpus analysis results
    """
    analysis = corpus_analyzer.analyze_corpus()
    return analysis


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document.
    
    Args:
        document_id: The document ID
    
    Returns:
        Deletion status
    """
    success = document_store.delete(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"status": "deleted", "document_id": document_id}


@app.get("/search")
async def search_documents(
    q: str,
    enable_time_decay: bool = True,
    decay_rate: float = 1.0
):
    """
    Search documents by content or metadata with time-based decay ranking.
    
    When time decay is enabled (default):
    - Recent documents are ranked higher than old documents
    - Formula: relevance_score = match_score * decay_factor
    - Example: Yesterday's 80% match beats Last Year's 95% match
    
    Args:
        q: The search query
        enable_time_decay: Apply time-based decay to ranking (default: True)
        decay_rate: Rate of decay, higher = faster decay (default: 1.0)
    
    Returns:
        Matching documents sorted by time-weighted relevance
    """
    results = document_store.search(
        q,
        enable_time_decay=enable_time_decay,
        decay_rate=decay_rate
    )
    
    return {
        "query": q,
        "enable_time_decay": enable_time_decay,
        "decay_rate": decay_rate,
        "total_results": len(results),
        "documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "type": doc.detected_type,
                "format": doc.format,
                "search_score": doc.metadata.get('_search_score', 0),
                "decay_factor": doc.metadata.get('_decay_factor', 1.0),
                "ingestion_timestamp": doc.ingestion_timestamp,
            }
            for doc in results
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
