# Metadata Injection - Contextual Enrichment

## The Problem: Context Amnesia

Traditional vector databases and RAG systems suffer from what we call **"Context Amnesia"** - chunks lose their context when separated from their parent documents.

### Example of the Problem

Consider this chunk from a financial report:

```
"It increased by 5%."
```

When this chunk is retrieved by a vector search, the AI sees:
- ❌ What increased? Unknown.
- ❌ Which document is this from? Unknown.
- ❌ Which section or chapter? Unknown.
- ❌ What time period? Unknown.

**The chunk has lost its parents. It has context amnesia.**

The AI might respond: "I see that something increased by 5%, but I don't have enough context to know what."

## The Solution: Metadata Injection

We **enrich every chunk** with its parent metadata before storing/retrieving it:

### Example of the Solution

**Original Chunk:**
```
"It increased by 5%."
```

**Enriched Chunk:**
```
[Document: Q3 Earnings] [Type: Research Paper] [Chapter: Financial Results] [Section: North America Revenue] It increased by 5%.
```

Now the AI can respond: "North America Revenue increased by 5% according to the Q3 Earnings report."

## How It Works

### 1. Hierarchy Tracking During Ingestion

When a document is ingested, the system tracks the hierarchical structure:

```python
# HTML Document
<h1>Q3 2024 Financial Results</h1>     # Level 1: Chapter
<h2>Revenue Analysis</h2>               # Level 2: Parent Section
<h3>North America</h3>                  # Level 3: Section
<p>Revenue increased by 5%.</p>         # Content

# Tracked Hierarchy:
Section {
    title: "North America",
    chapter: "Q3 2024 Financial Results",
    parent_section: "Revenue Analysis",
    content: "Revenue increased by 5%."
}
```

### 2. Metadata Injection During Retrieval

When context is extracted, the `MetadataEnricher` prepends metadata to each chunk:

```python
from caas.enrichment import MetadataEnricher
from caas.storage import ContextExtractor

# Create extractor with enrichment enabled (default)
extractor = ContextExtractor(store, enrich_metadata=True)

# Extract context
context, metadata = extractor.extract_context(doc_id, query="revenue")

# Result: Every chunk includes its metadata
# "[Document: Q3 Earnings] [Chapter: Financial Results] [Section: North America] Revenue increased by 5%."
```

### 3. Metadata Format

The enriched metadata follows this format:

```
[Document: {document_title}] [Type: {document_type}] [Chapter: {h1_title}] [Parent: {h2_title}] [Section: {current_title}] {original_content}
```

**Components:**
- **Document**: The document title (e.g., "Q3 Earnings Report")
- **Type**: The detected document type (e.g., "Research Paper", "Api Documentation")
- **Chapter**: The H1 section title (highest level)
- **Parent**: The H2 section title (if applicable)
- **Section**: The current section title
- **Content**: The original chunk content

## API Usage

### Enabling/Disabling Metadata Enrichment

```python
from caas.storage import DocumentStore, ContextExtractor

store = DocumentStore()

# Option 1: Enable enrichment (default)
extractor_with_metadata = ContextExtractor(store, enrich_metadata=True)

# Option 2: Disable enrichment
extractor_no_metadata = ContextExtractor(store, enrich_metadata=False)

# Extract context
enriched_context, meta = extractor_with_metadata.extract_context(doc_id)
plain_context, meta = extractor_no_metadata.extract_context(doc_id)
```

### Checking if Enrichment is Enabled

```python
context, metadata = extractor.extract_context(doc_id)

if metadata['metadata_enriched']:
    print("Context includes metadata enrichment")
else:
    print("Context is plain (no enrichment)")
```

## Real-World Examples

### Example 1: Financial Report

**Document Structure:**
```
Q3 2024 Earnings Report
├── Financial Performance
│   ├── Revenue
│   │   ├── North America: "Revenue increased by 5%"
│   │   └── Europe: "Revenue grew by 8%"
│   └── Expenses
│       └── Operating Costs: "Costs decreased by 3%"
```

**Without Enrichment:**
```
Query: "revenue performance"
Result: "Revenue increased by 5%. Revenue grew by 8%."
AI: "Revenue increased, but I don't know which regions or time period."
```

**With Enrichment:**
```
Query: "revenue performance"
Result: 
"[Document: Q3 2024 Earnings] [Chapter: Financial Performance] [Section: North America] Revenue increased by 5%.
[Document: Q3 2024 Earnings] [Chapter: Financial Performance] [Section: Europe] Revenue grew by 8%."

AI: "In Q3 2024, North America revenue increased by 5% and Europe revenue grew by 8%."
```

### Example 2: API Documentation

**Document Structure:**
```
Authentication API Guide
├── Authentication
│   ├── JWT Tokens: "Tokens expire after 1 hour"
│   └── OAuth2: "Supports standard OAuth2 flow"
├── Endpoints
│   ├── POST /login: "Authenticates user credentials"
│   └── GET /users: "Returns list of users"
```

**Without Enrichment:**
```
Query: "authentication token"
Result: "Tokens expire after 1 hour."
AI: "The tokens expire after 1 hour, but I don't know what type of tokens or which API."
```

**With Enrichment:**
```
Query: "authentication token"
Result: "[Document: Authentication API Guide] [Type: Api Documentation] [Chapter: Authentication] [Section: JWT Tokens] Tokens expire after 1 hour."

AI: "In the Authentication API Guide, JWT tokens expire after 1 hour."
```

### Example 3: Source Code Documentation

**Document Structure:**
```python
# auth.py

class UserAuthentication:
    """Main authentication class"""
    
    def validate_credentials(self, username, password):
        """Validates user credentials"""
        return check_password(username, password)
```

**Without Enrichment:**
```
Query: "validate credentials"
Result: "Validates user credentials"
AI: "There's a function that validates credentials, but I don't know which class or file."
```

**With Enrichment:**
```
Query: "validate credentials"
Result: "[Document: auth.py] [Type: Source Code] [Section: class UserAuthentication] def validate_credentials(self, username, password): Validates user credentials"

AI: "The validate_credentials method in the UserAuthentication class (auth.py) validates user credentials."
```

## Benefits

### 1. **Context Preservation**
- Chunks never lose their origin
- Hierarchical relationships maintained
- Document structure preserved in vectors

### 2. **Better AI Responses**
- AI can provide specific answers
- References are accurate and complete
- Users know exactly where information comes from

### 3. **Improved Search Quality**
- Metadata becomes part of searchable content
- More precise retrieval
- Better ranking of results

### 4. **Debugging & Traceability**
- Easy to trace chunks back to source
- Verify accuracy of retrieved content
- Identify which documents need updating

### 5. **Multi-Document Support**
- Clear distinction between documents
- Prevent confusion when similar content exists
- Better cross-document analysis

## Performance Considerations

### Storage Impact

Metadata injection increases chunk size by approximately:
- **Short metadata**: +50-80 characters
- **Medium metadata**: +80-120 characters  
- **Long metadata**: +120-200 characters

Example:
```
Original: "Revenue increased by 5%." (25 chars)
Enriched: "[Document: Q3 Earnings] [Chapter: Revenue] [Section: North America] Revenue increased by 5%." (105 chars)
Increase: ~80 characters (320% increase)
```

### Token Impact

For LLM contexts:
- Original chunk: ~6 tokens
- Enriched chunk: ~25 tokens
- Increase: ~19 tokens per chunk

For a typical RAG query retrieving 10 chunks:
- Without enrichment: ~60 tokens
- With enrichment: ~250 tokens
- Additional tokens: ~190 tokens

This is **negligible** compared to typical context windows (4K-128K tokens).

### Recommendation

✅ **Keep enrichment enabled** for:
- Production RAG systems
- User-facing chatbots
- Documentation search
- Knowledge bases

❌ **Disable enrichment only** when:
- Token count is extremely critical
- You have your own metadata tracking
- Testing raw content extraction

## Technical Details

### Hierarchy Tracking

The system tracks hierarchy during HTML processing:

```python
# In HTMLProcessor
current_h1 = None  # Chapter
current_h2 = None  # Parent section

for header in headers:
    if header.name == 'h1':
        current_h1 = header.text
    elif header.name == 'h2':
        current_h2 = header.text
    elif header.name == 'h3':
        # H3 section has h1 as chapter, h2 as parent
        section = Section(
            title=header.text,
            chapter=current_h1,
            parent_section=current_h2,
            content=extract_content(header)
        )
```

### Metadata Enrichment

The `MetadataEnricher` class handles enrichment:

```python
class MetadataEnricher:
    def get_enriched_chunk(self, section, document_title, document_type):
        parts = []
        parts.append(f"[Document: {document_title}]")
        
        if document_type:
            parts.append(f"[Type: {document_type}]")
        
        if section.chapter:
            parts.append(f"[Chapter: {section.chapter}]")
        
        if section.parent_section:
            parts.append(f"[Parent: {section.parent_section}]")
        
        parts.append(f"[Section: {section.title}]")
        
        return f"{' '.join(parts)} {section.content}"
```

## Best Practices

### 1. Keep Document Titles Descriptive

✅ Good:
```python
document.title = "Q3 2024 Financial Report"
```

❌ Bad:
```python
document.title = "document_123.pdf"
```

### 2. Use Meaningful Section Titles

✅ Good:
```html
<h2>North America Revenue</h2>
```

❌ Bad:
```html
<h2>Section 2.1</h2>
```

### 3. Maintain Proper HTML Hierarchy

✅ Good:
```html
<h1>Main Topic</h1>
<h2>Sub Topic</h2>
<h3>Detail</h3>
```

❌ Bad:
```html
<h1>Main Topic</h1>
<h3>Detail</h3>  <!-- Missing h2 -->
```

### 4. Include Document Type in Metadata

When ingesting documents, provide metadata:

```python
metadata = {
    "id": doc_id,
    "title": "Q3 Earnings Report",
    "format": "pdf",
    "year": "2024",
    "quarter": "Q3"
}
```

## Conclusion

Metadata injection solves the "Context Amnesia" problem by ensuring every chunk carries its full context. This leads to:

- ✅ Better AI understanding
- ✅ More accurate responses
- ✅ Improved user experience
- ✅ Better traceability
- ✅ Enhanced search quality

The feature is **enabled by default** and requires no configuration. The minimal token overhead (19 tokens per chunk) is vastly outweighed by the improved context quality.
