# Context-as-a-Service

A managed pipeline for intelligent context extraction and serving. The service automatically ingests, analyzes, and serves optimized context from various document formats.

## Features

🚀 **Auto-Ingestion**: Support for PDF, HTML, and source code files  
🔍 **Auto-Detection**: Intelligent document type and structure detection  
⚖️ **Auto-Tuning**: Automatic weight optimization based on content analysis  
🎯 **Smart Context**: API for serving perfectly weighted context  
📊 **Corpus Analysis**: Learn from your document corpus to improve over time  
🏗️ **Structure-Aware Indexing**: Three-tier hierarchical approach (High/Medium/Low value) that solves the "Flat Chunk Fallacy"  
🧬 **Metadata Injection**: Enriches chunks with contextual metadata to eliminate "context amnesia"  
⏰ **Time-Based Decay**: Prioritizes recent content over old using "The Half-Life of Truth" principle  

## The Problem

Traditional context extraction systems require manual configuration and suffer from THREE major fallacies:

### 1. The "Flat Chunk Fallacy" (Structure Problem)
- **Flat Chunk Approach**: Treating all content equally (e.g., splitting every 500 words and embedding)
- Manual weight adjustments for different sections
- Static rules that don't adapt to content
- No learning from document patterns
- Poor optimization for different document types
- **The Reality**: A class definition has different value than a TODO comment, but flat approaches treat them the same

### 2. The "Context Amnesia" Problem (Metadata Problem)
- **Isolated Chunks**: Chunks lose their context when separated from parent documents
- Example: "It increased by 5%." - What increased? Nobody knows.
- **The Reality**: A chunk without metadata is meaningless. Without knowing it's from "Q3 Earnings > Revenue > North America", the AI can't understand what increased.

### 3. The "Time-Blind Retrieval" Problem (Temporal Problem)
- **The Naive Approach**: "Relevance = Vector Similarity"
- **The Reality**: In software, truth is a moving target
- Example: "How to reset the server" in 2021 ≠ 2025
- If AI retrieves the 2021 answer because wording matches better, it fails
- **The Problem**: Traditional systems don't consider when information was created

## The Solution

Context-as-a-Service provides a fully automated pipeline:

1. **Ingest** raw data (PDF, Code, HTML)
2. **Auto-Detect** the structure (e.g., "This looks like a Legal Contract")
3. **Auto-Tune** the weights (e.g., "Boost the 'Definitions' section by 2x")
4. **Apply Time Decay** (e.g., "Recent content ranks higher than old content")
5. **Serve** the perfect context via API

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

### 1. Structure-Aware Indexing (Solving the "Flat Chunk Fallacy")

The system implements **hierarchical structure-aware indexing** that assigns content to three tiers based on importance:

#### **Tier 1 - High Value Content (2.0x base weight)**
- Titles and Headers (H1, H2)
- Class Definitions and Interfaces
- API Contracts and Endpoint Definitions
- Main abstracts and conclusions
- Critical sections (Definitions, Authentication, Authorization)

#### **Tier 2 - Medium Value Content (1.0x base weight)**
- Body text and paragraphs
- Function logic and implementations
- Method descriptions
- Standard documentation sections

#### **Tier 3 - Low Value Content (0.5x base weight)**
- Comments and inline documentation
- Footnotes and disclaimers
- TODO/FIXME markers
- Acknowledgments and copyright notices

**Why This Matters:**
Traditional "flat chunk" approaches treat all content equally, assuming a random paragraph on page 50 has the same value as critical API definitions. Our structure-aware approach ensures that when you search for information, a `public class Authentication` definition will rank higher than a `// TODO: fix this later` comment, even if they have similar semantic similarity to your query.

**Example:**
```python
# Both sections mention "authentication" with similar frequency
# But they get vastly different weights:

Section: "Authentication API Contract"     # Tier 1
Weight: 5.0x  (boosted as High Value)

Section: "// TODO: improve authentication" # Tier 3  
Weight: 0.5x  (demoted as Low Value)
```

### 2. Metadata Injection (Solving "Context Amnesia")

The system **enriches every chunk** with its parent metadata to maintain context:

#### **The Problem:**
```
Original Chunk: "It increased by 5%."
AI Response: "What increased? I don't know."
```

The chunk has lost its parents. It has **context amnesia**.

#### **The Solution:**
```
Enriched Chunk: "[Document: Q3 Earnings] [Chapter: Revenue] [Section: North America] It increased by 5%."
AI Response: "North America revenue increased by 5% in Q3."
```

Now the vector **carries the weight of its context**. When the AI retrieves it, it knows exactly what increased.

#### **How It Works:**

1. **Hierarchy Tracking**: The system tracks document hierarchy (H1 → H2 → H3 → H4)
2. **Metadata Injection**: When extracting context, metadata is prepended to each chunk
3. **Smart Formatting**: Metadata includes: Document Title, Document Type, Chapter, Section
4. **Toggleable**: Can be enabled/disabled per request

**Example Transformation:**

```python
# HTML Document Structure
<h1>Q3 2024 Financial Results</h1>
<h2>Revenue Analysis</h2>
<h3>North America</h3>
<p>Revenue in North America increased by 5%.</p>

# Without Metadata Injection:
"Revenue in North America increased by 5%."

# With Metadata Injection:
"[Document: Q3 Earnings Report] [Type: Research Paper] [Chapter: Q3 2024 Financial Results] [Section: North America] Revenue in North America increased by 5%."
```

**Benefits:**
- ✅ **Context Preservation**: Chunks never lose their origin
- ✅ **Better AI Responses**: AI can understand what each chunk refers to
- ✅ **Improved Search**: Metadata becomes part of searchable content
- ✅ **Hierarchical Understanding**: Maintains document structure in vectors

### 3. Time-Based Decay (Solving "Time-Blind Retrieval")

The system implements **"The Half-Life of Truth"** - mathematical gravity that pulls old data down.

#### **The Problem:**
```
Naive Approach: "Relevance = Vector Similarity"

The Reality: In software, the truth is a moving target.
- "How to reset the server" in 2021 ≠ 2025
- If AI retrieves 2021 answer (better word match), it fails
```

#### **The Solution:**
```
Formula: Score = Similarity × (1 / (1 + days_elapsed))

Result: A document from Yesterday with 80% match 
        beats a document from Last Year with 95% match.
```

**We believe in the Decay Function:**
- We don't "cut off" old data (history is useful for debugging)
- We apply mathematical "Gravity" that pulls old data down
- We prioritize "What happened latest" over "What matched best"
- In a living system: **Recency IS Relevance**

**Example:**

```python
# Recent document (Yesterday)
Base Similarity:  80%
Decay Factor:     0.500  (1 / (1 + 1 day))
Final Score:      0.400  (0.80 × 0.500)

# Old document (Last Year)
Base Similarity:  95%
Decay Factor:     0.003  (1 / (1 + 365 days))
Final Score:      0.003  (0.95 × 0.003)

Winner: Recent document (0.400 > 0.003) ✅
```

**Decay Curve:**
- **Day 0 (Today)**: Factor = 1.0 (no decay)
- **Day 1 (Yesterday)**: Factor = 0.5 (50% weight)
- **Day 7 (Week ago)**: Factor = 0.125 (12.5% weight)
- **Day 30 (Month ago)**: Factor = 0.032 (3.2% weight)
- **Day 365 (Year ago)**: Factor = 0.003 (0.3% weight)

**Benefits:**
- ✅ **Temporal Relevance**: Recent content automatically ranks higher
- ✅ **No History Loss**: Old documents remain searchable, just deprioritized
- ✅ **Living Documentation**: System adapts as documentation evolves
- ✅ **Configurable**: Decay rate can be adjusted (faster/slower decay)

**Configuration:**
```python
# Enable/disable time decay in search
results = store.search(
    "server reset",
    enable_time_decay=True,  # Default: True
    decay_rate=1.0           # Default: 1.0 (higher = faster decay)
)

# Configure for context extraction
extractor = ContextExtractor(
    store,
    enable_time_decay=True,  # Default: True
    decay_rate=1.0           # Default: 1.0
)
```

**Why This Matters:**
Traditional RAG systems treat a 3-year-old document the same as yesterday's update. Our time decay ensures that when you ask "How do I deploy?", you get the current process, not the legacy one that happened to have better keyword matches.

### 4. Document Type Detection

The service analyzes content to detect document types:
- **Legal Contracts**: Looks for "whereas", "party", "hereby", "indemnify"
- **Technical Docs**: Identifies "API", "configuration", "parameters"
- **Research Papers**: Detects "abstract", "methodology", "results"
- **Source Code**: Recognizes programming patterns

### 5. Base Weight Assignment

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

### 6. Content-Based Adjustments

Weights are further adjusted based on:
- **Code Examples**: +20% weight
- **Definitions**: +30% weight  
- **Important Markers**: +15% (words like "critical", "must", "required")
- **Length**: +10% for substantial sections (>500 chars)
- **Position**: +15% for first section, +10% for last

### 7. Query Boosting

When a query is provided, sections matching the query get +50% weight boost.

### 8. Corpus Learning

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
│  - PDF         - Pattern Match - Tier Classifier   │
│  - HTML        - Structure    - Structure Parser   │
│  - Code        - Analysis     - Query Boost        │
│  - Hierarchy   - Section Link - Metadata Tracking  │
└─────────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│              Storage & Extraction                    │
│       (Structure-Aware + Metadata-Enriched)         │
│  ┌──────────────┐        ┌──────────────┐          │
│  │ Document     │        │   Context    │          │
│  │ Store        │◀───────│  Extractor   │          │
│  └──────────────┘        └──────────────┘          │
│                                │                     │
│                                ▼                     │
│                      ┌──────────────────┐           │
│                      │ Metadata Enricher│           │
│                      └──────────────────┘           │
│                                                      │
│  Prioritizes: Tier 1 > Tier 2 > Tier 3             │
│  Enriches: [Document] [Chapter] [Section] Content  │
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

### Metadata Enrichment

Metadata enrichment is **enabled by default**. To disable it:

```python
from caas.storage import ContextExtractor, DocumentStore

store = DocumentStore()
# Disable metadata enrichment
extractor = ContextExtractor(store, enrich_metadata=False)
```

### Time-Based Decay

Time-based decay is **enabled by default** and can be configured:

```python
from caas.storage import ContextExtractor, DocumentStore

store = DocumentStore()

# Configure decay for context extraction
extractor = ContextExtractor(
    store, 
    enable_time_decay=True,  # Enable/disable (default: True)
    decay_rate=1.0           # Adjust decay speed (default: 1.0)
)

# Configure decay for search
results = store.search(
    "your query",
    enable_time_decay=True,  # Enable/disable (default: True)
    decay_rate=1.0           # Adjust decay speed (default: 1.0)
)
```

**Decay Rate Guide:**
- `decay_rate=0.1`: Slow decay (yesterday = 0.91x, week = 0.59x)
- `decay_rate=1.0`: Standard decay (yesterday = 0.5x, week = 0.125x) ← **Default**
- `decay_rate=2.0`: Fast decay (yesterday = 0.33x, week = 0.067x)

### Custom Tuning Rules

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
│   ├── models.py           # Data models (includes ContentTier, Section with hierarchy)
│   ├── enrichment.py       # Metadata enrichment for contextual injection
│   ├── decay.py            # Time-based decay calculations
│   ├── cli.py              # CLI tool
│   ├── ingestion/          # Document processors
│   │   ├── __init__.py
│   │   ├── processors.py   # Processors with hierarchy tracking
│   │   └── structure_parser.py  # Tier-based structure parser
│   ├── detection/          # Type & structure detection
│   │   ├── __init__.py
│   │   └── detector.py
│   ├── tuning/             # Auto-weight tuning
│   │   ├── __init__.py
│   │   └── tuner.py
│   ├── storage/            # Document storage
│   │   ├── __init__.py
│   │   └── store.py        # Context extraction with time decay
│   └── api/                # REST API
│       ├── __init__.py
│       └── server.py
├── examples/               # Example documents
├── test_functionality.py   # Basic functionality tests
├── test_structure_aware_indexing.py  # Structure-aware indexing tests
├── test_metadata_injection.py  # Metadata injection/enrichment tests
├── test_time_decay.py      # Time-based decay tests
├── demo_time_decay.py      # Time decay demonstration
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

```bash
# Run basic functionality tests
python test_functionality.py

# Run structure-aware indexing tests
python test_structure_aware_indexing.py

# Run metadata injection tests
python test_metadata_injection.py

# Run time-based decay tests
python test_time_decay.py

# Run time decay demonstration
python demo_time_decay.py

# Install dev dependencies (if needed)
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
