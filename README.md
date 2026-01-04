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
🔥 **Context Triad (Hot, Warm, Cold)**: Intimacy-based three-tier context system that treats context by relevance, not just speed  
💡 **Pragmatic Truth**: Provides REAL answers, not just OFFICIAL ones - with transparent source citations and conflict detection  
⚡ **Heuristic Router**: Lightning-fast query routing using deterministic heuristics (Speed > Smarts) - 0ms routing decisions  
✂️ **Sliding Window Conversation Management**: FIFO approach that keeps recent turns intact instead of lossy summarization (Chopping > Summarizing)

## The Problem

Traditional context extraction systems require manual configuration and suffer from SIX major fallacies:

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

### 4. The "Flat Context Fallacy" (Priority Problem)
- **The Naive Approach**: "Stuff everything into the Context Window until it's full"
- **The Reality**: Not all context is created equal
- Current conversation ≠ User preferences ≠ Historical archives
- No clear prioritization between what's happening NOW vs. what happened LAST YEAR
- **The Problem**: Traditional systems treat all context with the same priority

### 5. The "Official Truth Fallacy" (Source Problem)
- **The Naive Approach**: "The Official Documentation is the source of truth"
- **The Reality**: Official docs are often theoretical; Slack logs contain the actual fix
- Example: Docs say "API limit is 100" but team knows "it crashes after 50"
- Traditional AI only shows official answer (misleading)
- **The Problem**: No distinction between official theory and practical reality

### 6. The "Brutal Squeeze" (Context Management Problem)
- **The Naive Approach**: "Let's ask an AI to summarize the conversation history to save space"
- **The Engineering Reality**: Summarization is a trap
  - It costs money to generate the summary
  - It loses nuance: "I tried X and it failed" becomes "User attempted troubleshooting" (specific error code is lost)
- **My Philosophy**: Chopping (FIFO) is better
  - We prefer a brutal "Sliding Window": Keep the last 10 turns perfectly intact, delete turn 11
  - Why? Users rarely refer back to what they said 20 minutes ago, but they constantly refer to the exact code snippet they pasted 30 seconds ago
  - Summary = Lossy Compression
  - Chopping = Lossless Compression (of the recent past)
- **The Problem**: In a frugal architecture, we value **Recent Precision over Vague History**

## The Solution

Context-as-a-Service provides a fully automated pipeline:

1. **Ingest** raw data (PDF, Code, HTML)
2. **Auto-Detect** the structure (e.g., "This looks like a Legal Contract")
3. **Auto-Tune** the weights (e.g., "Boost the 'Definitions' section by 2x")
4. **Apply Time Decay** (e.g., "Recent content ranks higher than old content")
5. **Track Sources** (e.g., "This is from Slack vs official docs")
6. **Detect Conflicts** (e.g., "Official says X, team says Y")
7. **Manage Conversations** (e.g., "Keep last 10 turns intact, delete older turns via FIFO")
8. **Serve** the perfect context via API with transparent citations

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

### Route Query (Heuristic Router)

```bash
POST /route
```

Route a query to the appropriate model tier using deterministic heuristics:

```bash
curl -X POST "http://localhost:8000/route" \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize this document"}'
```

**Response:**
```json
{
  "model_tier": "smart",
  "reason": "Complex task keywords detected: summarize",
  "confidence": 0.85,
  "query_length": 23,
  "matched_keywords": ["summarize"],
  "suggested_model": "gpt-4o",
  "estimated_cost": "high"
}
```

For greetings, a canned response is also included:

```bash
curl -X POST "http://localhost:8000/route" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hi"}'
```

**Response:**
```json
{
  "model_tier": "canned",
  "reason": "Greeting detected - using canned response for zero cost",
  "confidence": 0.95,
  "query_length": 2,
  "matched_keywords": ["hi"],
  "suggested_model": "canned_response",
  "estimated_cost": "zero",
  "canned_response": "Hello! How can I assist you today?"
}
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

### 4. Context Triad (Solving "Flat Context Fallacy")

The system implements **intimacy-based context layers** that treat context by relevance, not just speed.

#### **The Naive Approach:**
```
"Stuff everything into the Context Window until it's full."
```

#### **The Engineering Reality:**
We need to treat context like a tiered storage system, but defined by **Intimacy**, not just speed.

#### **L1: Hot Context (The Situation)**
**Definition:** What is happening right now?

**Examples:**
- Current conversation messages
- Open VS Code tabs
- Error logs streaming in real-time
- Active debugging session

**Policy:** "Attention Head" - Overrides everything
- Highest priority, always included
- Auto-maintained (limited to 50 most recent items)

#### **L2: Warm Context (The Persona)**
**Definition:** Who am I?

**Examples:**
- LinkedIn profile
- Medium articles
- Coding style preferences
- Favorite libraries and frameworks
- Communication style

**Policy:** "Always On Filter" - Colors how AI speaks to you
- Persistent across sessions
- Should be part of system prompt
- Doesn't need retrieval every time

#### **L3: Cold Context (The Archive)**
**Definition:** What happened last year?

**Examples:**
- Old tickets from previous years
- Closed pull requests
- Historical design documents
- Legacy system documentation

**Policy:** "On Demand Only" - Fetch only when explicitly asked
- **Never** automatically included
- Requires explicit query to access
- Prevents historical data from polluting hot window

#### **Usage Example:**

```python
from caas.triad import ContextTriadManager

manager = ContextTriadManager()

# Add hot context (current situation)
manager.add_hot_context(
    "User debugging: NullPointerException at line 145",
    metadata={"source": "error_log"},
    priority=3.0
)

# Add warm context (user persona)
manager.add_warm_context(
    "Senior Python developer, prefers type hints",
    metadata={"category": "Profile"},
    priority=2.0
)

# Add cold context (historical archive)
manager.add_cold_context(
    "Ticket #1234: Fixed similar bug in 2023",
    metadata={"date": "2023-06-15"},
    priority=1.0
)

# Get context (Hot + Warm by default, Cold excluded)
result = manager.get_full_context(
    include_hot=True,
    include_warm=True,
    include_cold=False  # Cold requires explicit query
)

# Access cold context with explicit query
result = manager.get_full_context(
    include_cold=True,
    cold_query="NullPointerException"  # Required for cold context
)
```

**Why This Matters:**
Traditional systems treat current errors the same as year-old tickets. The Context Triad ensures the right context is available at the right time with the right priority. Current situation (hot) always takes precedence, user persona (warm) is always on, and historical data (cold) never pollutes the working context unless explicitly requested.

**See [CONTEXT_TRIAD.md](CONTEXT_TRIAD.md) for detailed documentation.**

### 5. Pragmatic Truth (Solving "Official Truth Fallacy")

The system implements **transparent source tracking** that distinguishes between official documentation and practical reality.

#### **The Naive Approach:**
```
"The Official Documentation is the source of truth."
```

#### **The Engineering Reality:**
We need to present BOTH official answers and practical experience with full transparency.

#### **Example: API Rate Limits**

**Official Documentation says:**
> "The API supports 100 requests per minute."
> Source: [Official Docs] API Documentation v2.1 (2023-07-08)

**Team Experience shows:**
> "Actually, the API crashes after 50 requests. We've hit this multiple times."
> Source: [Team Chat] Slack #engineering (2024-01-02)

**AI Response:**
> "Officially, the docs say the limit is 100. However, looking at recent team discussions and production logs, the real limit appears to be 50 before instability occurs."

#### **Source Types:**
- `OFFICIAL_DOCS` - Official documentation, specs
- `TEAM_CHAT` - Slack, Teams conversations
- `PRACTICAL_LOGS` - Server logs, error logs
- `RUNBOOK` - Operational runbooks
- `TICKET_SYSTEM` - Jira, GitHub issues
- `CODE_COMMENTS` - Inline code comments
- `WIKI` - Internal wikis
- `MEETING_NOTES` - Meeting decisions

#### **Features:**
1. **Source Detection** - Automatically identifies source types
2. **Citation Tracking** - Every section cites its source with timestamp
3. **Conflict Detection** - Identifies when official and practical sources disagree
4. **Transparent Responses** - Shows both perspectives with recommendations
5. **Time Priority** - Recent practical experience weighs more than old docs

#### **Usage Example:**

```python
from caas.storage import ContextExtractor

extractor = ContextExtractor(
    store,
    enable_citations=True,      # Include source citations
    detect_conflicts=True,      # Detect conflicts between sources
    enable_time_decay=True      # Prioritize recent information
)

context, metadata = extractor.extract_context(
    document_id="doc-123",
    query="server restart",
    max_tokens=2000
)

# Check citations
print(f"Sources: {len(metadata['citations'])}")

# Check conflicts
if metadata['conflicts']:
    print("⚠️ Conflict detected between official and practical sources!")
```

**Why This Matters:**
Traditional RAG systems treat all sources equally, leading to misleading responses when official documentation is outdated. Our Pragmatic Truth approach ensures users get the real answer with full transparency about sources and conflicts. When a 2-day-old Slack conversation contradicts 6-month-old docs, the AI shows both and recommends the practical approach.

**See [PRAGMATIC_TRUTH.md](PRAGMATIC_TRUTH.md) for detailed documentation.**

### 6. Heuristic Router (Speed > Smarts)

The system implements **deterministic heuristic routing** for instant query classification without LLM overhead.

#### **The Naive Approach:**
```
"Let's use a small LLM (like GPT-3.5) to classify the user's intent, 
and then route it to the right model."
```

#### **The Engineering Reality:**
This is "Model-on-Model" overhead. Even a small LLM takes 500ms+ to think. You are adding latency just to decide where to send the traffic. We need to be **Fast, even if we are occasionally Wrong**.

#### **My Philosophy:**
Use **Deterministic Heuristics, not AI Classifiers**. We can solve 80% of routing with simple logic that takes 0ms:

**Rule 1**: Is the query length < 50 characters? → Send to **Fast Model** (GPT-4o-mini)  
**Rule 2**: Does it contain keywords like "Summary", "Analyze", "Compare"? → Send to **Smart Model** (GPT-4o)  
**Rule 3**: Is it a greeting ("Hi", "Thanks")? → Send to **Canned Response** (Zero Cost)

The goal isn't 100% routing accuracy. The goal is **instant response time** for the trivial stuff, preserving the "Big Brain" budget for the hard stuff.

#### **Model Tiers:**

**🎯 CANNED (Zero Cost, 0ms latency)**
- Pre-defined responses for greetings
- Examples: "Hi", "Thanks", "Bye", "Ok"
- Cost: $0.00 per request
- Response: Instant (no API call)

**⚡ FAST (Low Cost, ~200ms latency)**
- Fast model like GPT-4o-mini
- For: Short queries, simple questions
- Cost: ~$0.0001 per request (100x cheaper than GPT-4o)
- Examples: "What is Python?", "How to install?"

**🧠 SMART (High Cost, ~500ms+ latency)**
- Smart model like GPT-4o
- For: Complex tasks, long queries
- Cost: ~$0.01 per request
- Examples: "Summarize this document", "Analyze the performance"

#### **Usage Example:**

```python
from caas.routing import HeuristicRouter

router = HeuristicRouter()

# Short query → FAST
decision = router.route("What is Python?")
print(decision.model_tier)  # ModelTier.FAST
print(decision.suggested_model)  # "gpt-4o-mini"
print(decision.estimated_cost)  # "low"

# Smart keyword → SMART
decision = router.route("Summarize this document")
print(decision.model_tier)  # ModelTier.SMART
print(decision.suggested_model)  # "gpt-4o"
print(decision.estimated_cost)  # "high"

# Greeting → CANNED
decision = router.route("Hi")
print(decision.model_tier)  # ModelTier.CANNED
response = router.get_canned_response("Hi")
print(response)  # "Hello! How can I assist you today?"
```

#### **API Endpoint:**

```bash
curl -X POST "http://localhost:8000/route" \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize this document"}'
```

**Response:**
```json
{
  "model_tier": "smart",
  "reason": "Complex task keywords detected: summarize",
  "confidence": 0.85,
  "query_length": 23,
  "matched_keywords": ["summarize"],
  "suggested_model": "gpt-4o",
  "estimated_cost": "high"
}
```

#### **Why This Matters:**
Traditional systems use AI classifiers for routing, adding 500ms+ latency before the actual AI call. Our heuristic router makes routing decisions in **< 1ms**, preserving the "Big Brain" budget for the actual AI work. For greetings, we skip the AI entirely and return canned responses for zero cost.

**Cost Savings Example:**
- 1000 daily greetings with AI classifier: $10/day
- 1000 daily greetings with heuristic router: $0/day
- **Annual savings**: $3,650

**See [HEURISTIC_ROUTER.md](HEURISTIC_ROUTER.md) for detailed documentation.**

### 7. Sliding Window Conversation Management (Solving "The Brutal Squeeze")

The system implements **FIFO (First In First Out) sliding window** for conversation history instead of lossy summarization.

#### **The Naive Approach:**
```
"The context is too long. Let's ask an AI to summarize the conversation history to save space."
```

#### **The Engineering Reality:**
Summarization is a trap:
- It **costs money** to generate the summary
- It **loses nuance**: "I tried X and it failed with error code 500" becomes "User attempted troubleshooting" (ERROR CODE LOST!)
- It creates **vague history** instead of precise details

#### **My Philosophy: Chopping > Summarizing**

We prefer a brutal **"Sliding Window"** approach:
- Keep the last 10 turns **perfectly intact**
- Delete turn 11 (FIFO - First In First Out)
- **No summarization** = **No AI cost** = **No information loss**

#### **Why This Works:**

Users rarely refer back to what they said 20 minutes ago. But they **constantly** refer to the exact code snippet they pasted 30 seconds ago.

**Summary = Lossy Compression**  
**Chopping = Lossless Compression** (of the recent past)

In a frugal architecture, we value **Recent Precision over Vague History**.

#### **Example:**

```python
# Turn 1 (20 minutes ago)
User: "I tried X and it failed with error code 500"
AI: "Let me help you debug that..."

# With Summarization (Lossy):
"User attempted troubleshooting"  # ❌ Error code lost!

# With Sliding Window (Lossless):
After 10 new turns, this turn is deleted entirely.
But turns 2-11 are PERFECTLY intact with all details.
```

#### **Cost Comparison:**

**Summarization Approach:**
- Summarize every 10 turns
- Cost per summary: $0.01 (GPT-4o call)
- 1000 conversations × 2 summaries = $20
- Information loss: ⚠️ HIGH

**Sliding Window Approach:**
- Keep last 10 turns intact
- Delete older turns (FIFO)
- Cost: $0.00 (no AI calls)
- Information loss: ✅ ZERO (what's kept is perfect)

**Annual Savings:** $240

#### **Usage Example:**

```python
from caas.conversation import ConversationManager

# Create manager with sliding window
manager = ConversationManager(max_turns=10)

# Add conversation turns
turn_id = manager.add_turn(
    user_message="How do I fix error 500?",
    ai_response="Check your database connection..."
)

# Get conversation history (last 10 turns, perfectly intact)
history = manager.get_conversation_history()

# Get statistics
stats = manager.get_statistics()
print(f"Current turns: {stats['current_turns']}")
print(f"Total ever: {stats['total_turns_ever']}")
print(f"Deleted: {stats['deleted_turns']}")
```

#### **API Endpoints:**

```bash
# Add a conversation turn
curl -X POST "http://localhost:8000/conversation/turn" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "How do I fix error 500?",
    "ai_response": "Check your database connection..."
  }'

# Get conversation history
curl "http://localhost:8000/conversation"

# Get conversation statistics
curl "http://localhost:8000/conversation/stats"

# Get recent N turns
curl "http://localhost:8000/conversation/recent?n=5"

# Clear conversation
curl -X DELETE "http://localhost:8000/conversation"
```

**Response Example:**
```json
{
  "status": "success",
  "turn_id": "abc-123",
  "statistics": {
    "current_turns": 10,
    "max_turns": 10,
    "total_turns_ever": 15,
    "deleted_turns": 5
  }
}
```

#### **Why This Matters:**

Traditional systems use AI to summarize conversation history, which:
1. Costs money ($0.01 per summary)
2. Loses critical details (error codes, exact wording)
3. Creates vague summaries that aren't useful

Our sliding window approach:
1. Costs $0 (no AI calls)
2. Keeps recent turns PERFECTLY intact
3. Provides exact details users actually need

**Philosophy:** In a frugal architecture, **Recent Precision > Vague History**.

### 8. Document Type Detection

The service analyzes content to detect document types:
- **Legal Contracts**: Looks for "whereas", "party", "hereby", "indemnify"
- **Technical Docs**: Identifies "API", "configuration", "parameters"
- **Research Papers**: Detects "abstract", "methodology", "results"
- **Source Code**: Recognizes programming patterns

### 9. Base Weight Assignment

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

### 9. Content-Based Adjustments

Weights are further adjusted based on:
- **Code Examples**: +20% weight
- **Definitions**: +30% weight  
- **Important Markers**: +15% (words like "critical", "must", "required")
- **Length**: +10% for substantial sections (>500 chars)
- **Position**: +15% for first section, +10% for last

### 10. Query Boosting

When a query is provided, sections matching the query get +50% weight boost.

### 11. Corpus Learning

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
│   ├── models.py           # Data models (includes ContentTier, Section with hierarchy, SourceType)
│   ├── enrichment.py       # Metadata enrichment for contextual injection
│   ├── decay.py            # Time-based decay calculations
│   ├── pragmatic_truth.py  # Source tracking, citations, and conflict detection
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
│   │   └── store.py        # Context extraction with time decay and citations
│   ├── triad.py            # Context Triad manager (Hot, Warm, Cold)
│   └── api/                # REST API
│       ├── __init__.py
│       └── server.py
├── examples/               # Example documents
├── test_functionality.py   # Basic functionality tests
├── test_structure_aware_indexing.py  # Structure-aware indexing tests
├── test_metadata_injection.py  # Metadata injection/enrichment tests
├── test_time_decay.py      # Time-based decay tests
├── test_context_triad.py   # Context Triad tests
├── test_pragmatic_truth.py # Pragmatic Truth tests
├── demo_time_decay.py      # Time decay demonstration
├── demo_context_triad.py   # Context Triad demonstration
├── demo_pragmatic_truth.py # Pragmatic Truth demonstration
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

# Run context triad tests
python test_context_triad.py

# Run pragmatic truth tests
python test_pragmatic_truth.py

# Run heuristic router tests
python test_heuristic_router.py

# Run time decay demonstration
python demo_time_decay.py

# Run context triad demonstration
python demo_context_triad.py

# Run pragmatic truth demonstration
python demo_pragmatic_truth.py

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
