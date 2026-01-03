# Context-as-a-Service

A managed pipeline for intelligent context extraction and serving. The service automatically ingests, analyzes, and serves optimized context from various document formats.

## Features

🚀 **Auto-Ingestion**: Support for PDF, HTML, and source code files  
🔍 **Auto-Detection**: Intelligent document type and structure detection  
⚖️ **Auto-Tuning**: Automatic weight optimization based on content analysis  
🎯 **Smart Context**: API for serving perfectly weighted context  
📊 **Corpus Analysis**: Learn from your document corpus to improve over time  

## The Problem

Traditional context extraction systems require manual configuration:
- Manual weight adjustments for different sections
- Static rules that don't adapt to content
- No learning from document patterns
- Poor optimization for different document types

## The Solution

Context-as-a-Service provides a fully automated pipeline:

1. **Ingest** raw data (PDF, Code, HTML)
2. **Auto-Detect** the structure (e.g., "This looks like a Legal Contract")
3. **Auto-Tune** the weights (e.g., "Boost the 'Definitions' section by 2x")
4. **Serve** the perfect context via API

**No manual tuning required** - the service analyzes your corpus and tunes itself.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Start the API Server

```bash
python -m uvicorn caas.api.server:app --reload
```

The API will be available at `http://localhost:8000`

### Using the CLI

```bash
# Ingest a document
python caas/cli.py ingest contract.pdf pdf "Employment Contract"

# Analyze a document
python caas/cli.py analyze <document_id>

# Extract context
python caas/cli.py context <document_id> "termination clause"

# List all documents
python caas/cli.py list
```

## API Endpoints

### Ingest a Document

```bash
POST /ingest
```

Upload a document for automatic processing:

```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@contract.pdf" \
  -F "format=pdf" \
  -F "title=Employment Contract"
```

**Response:**
```json
{
  "document_id": "abc-123",
  "title": "Employment Contract",
  "detected_type": "legal_contract",
  "format": "pdf",
  "sections_found": 12,
  "weights": {
    "Definitions": 2.0,
    "Terms of Employment": 1.8,
    "Termination": 1.5
  },
  "status": "ingested"
}
```

### Get Context

```bash
POST /context/{document_id}
```

Extract optimized context from a document:

```bash
curl -X POST "http://localhost:8000/context/abc-123" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "termination clause",
    "max_tokens": 2000,
    "include_metadata": true
  }'
```

**Response:**
```json
{
  "document_id": "abc-123",
  "document_type": "legal_contract",
  "context": "## Definitions\n...\n## Termination\n...",
  "sections_used": ["Definitions", "Termination", "Notice Period"],
  "total_tokens": 1847,
  "weights_applied": {
    "Definitions": 2.6,
    "Termination": 2.25,
    "Notice Period": 1.5
  }
}
```

### List Documents

```bash
GET /documents
GET /documents?doc_type=legal_contract
```

### Analyze Document

```bash
GET /analyze/{document_id}
```

Get detailed structure and content analysis.

### Analyze Corpus

```bash
GET /corpus/analyze
```

Get insights about your entire document corpus:

```json
{
  "total_documents": 47,
  "document_types": {
    "legal_contract": 12,
    "technical_documentation": 20,
    "source_code": 15
  },
  "common_sections": {
    "introduction": 32,
    "definitions": 15,
    "examples": 28
  },
  "optimization_suggestions": [
    "Consider standardizing section names for better weight optimization"
  ]
}
```

### Search Documents

```bash
GET /search?q=termination
```

## How Auto-Tuning Works

The system automatically optimizes context weights through multiple strategies:

### 1. Document Type Detection

The service analyzes content to detect document types:
- **Legal Contracts**: Looks for "whereas", "party", "hereby", "indemnify"
- **Technical Docs**: Identifies "API", "configuration", "parameters"
- **Research Papers**: Detects "abstract", "methodology", "results"
- **Source Code**: Recognizes programming patterns

### 2. Base Weight Assignment

Each document type has optimized base weights:

```python
Legal Contract:
  - Definitions: 2.0x
  - Terms: 1.8x
  - Termination: 1.5x

Technical Documentation:
  - API Reference: 1.8x
  - Examples: 1.7x
  - Parameters: 1.6x
```

### 3. Content-Based Adjustments

Weights are further adjusted based on:
- **Code Examples**: +20% weight
- **Definitions**: +30% weight  
- **Important Markers**: +15% (words like "critical", "must", "required")
- **Length**: +10% for substantial sections (>500 chars)
- **Position**: +15% for first section, +10% for last

### 4. Query Boosting

When a query is provided, sections matching the query get +50% weight boost.

### 5. Corpus Learning

The system analyzes patterns across all documents to:
- Identify common section structures
- Calculate average optimal weights
- Provide optimization suggestions

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                         │
│              (FastAPI REST API)                     │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│                Processing Pipeline                   │
│                                                      │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│  │ Ingest  │──▶│ Detect  │──▶│  Tune   │          │
│  └─────────┘   └─────────┘   └─────────┘          │
│      │              │              │                │
│      ▼              ▼              ▼                │
│  Processors    Type Detector  Weight Tuner         │
│  - PDF         - Pattern Match - Type Rules        │
│  - HTML        - Structure    - Content Analysis   │
│  - Code        - Analysis     - Query Boost        │
└─────────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│              Storage & Extraction                    │
│                                                      │
│  ┌──────────────┐        ┌──────────────┐          │
│  │ Document     │        │   Context    │          │
│  │ Store        │◀───────│  Extractor   │          │
│  └──────────────┘        └──────────────┘          │
└─────────────────────────────────────────────────────┘
```

## Supported Document Types

- ✅ **Legal Contract**: Auto-detects clauses, definitions, terms
- ✅ **Technical Documentation**: Identifies API refs, configs, examples  
- ✅ **Source Code**: Extracts classes, functions, modules
- ✅ **Research Paper**: Recognizes abstract, methodology, results
- ✅ **Tutorial**: Detects steps, exercises, examples
- ✅ **API Documentation**: Finds endpoints, auth, request/response

## Examples

### Example 1: Legal Contract

```python
# The service automatically detects this is a legal contract
# and boosts "Definitions" section by 2x
```

**Input**: Employment contract PDF  
**Auto-Detection**: Legal Contract  
**Auto-Tuning**: Definitions (2.0x), Termination (1.5x), Terms (1.8x)  
**Result**: Context focused on critical legal sections

### Example 2: Technical Documentation

```python
# Detects technical content and prioritizes examples
```

**Input**: API documentation HTML  
**Auto-Detection**: API Documentation  
**Auto-Tuning**: Endpoints (1.8x), Examples (1.7x), Auth (1.9x)  
**Result**: Developer-focused context with code examples

### Example 3: Source Code

```python
# Recognizes code structure and emphasizes key functions
```

**Input**: Python source file  
**Auto-Detection**: Source Code  
**Auto-Tuning**: Classes (1.6x), Main functions (1.8x), APIs (1.7x)  
**Result**: Code context highlighting important implementations

## Configuration

The service works out-of-the-box with sensible defaults. No configuration required!

For custom tuning rules, modify `caas/tuning/tuner.py`:

```python
TYPE_SPECIFIC_WEIGHTS = {
    DocumentType.LEGAL_CONTRACT: {
        "definitions": 2.0,  # Adjust as needed
        "terms": 1.8,
        ...
    }
}
```

## Development

### Project Structure

```
context-as-a-service/
├── caas/
│   ├── __init__.py
│   ├── models.py           # Data models
│   ├── cli.py              # CLI tool
│   ├── ingestion/          # Document processors
│   │   ├── __init__.py
│   │   └── processors.py
│   ├── detection/          # Type & structure detection
│   │   ├── __init__.py
│   │   └── detector.py
│   ├── tuning/             # Auto-weight tuning
│   │   ├── __init__.py
│   │   └── tuner.py
│   ├── storage/            # Document storage
│   │   ├── __init__.py
│   │   └── store.py
│   └── api/                # REST API
│       ├── __init__.py
│       └── server.py
├── examples/               # Example documents
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when available)
pytest
```

## Use Cases

### 1. Legal Document Analysis
Automatically extract key clauses from contracts with proper emphasis on definitions and terms.

### 2. Technical Documentation Search
Serve developers with perfectly weighted API references and code examples.

### 3. Code Context for AI
Provide AI coding assistants with optimally weighted source code context.

### 4. Research Paper Summarization
Extract key findings with proper emphasis on methodology and results.

### 5. Knowledge Base Retrieval
Intelligently serve content from diverse document types with appropriate weighting.

## API Documentation

Full interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

Contributions welcome! Areas for enhancement:
- Additional document type detectors
- More sophisticated weight tuning algorithms
- Support for more file formats
- Machine learning-based optimization

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [context-as-a-service/issues](https://github.com/imran-siddique/context-as-a-service/issues)
- Documentation: See `/docs` endpoint when running the service

---

**Context-as-a-Service** - Intelligent context extraction, zero configuration needed.
