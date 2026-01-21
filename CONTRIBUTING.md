# Contributing to Context-as-a-Service

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and collaborative. We're here to build something great together.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/<your-username>/context-as-a-service.git
cd context-as-a-service
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Tests

```bash
python run_tests.py
```

## Project Structure

```
context-as-a-service/
├── caas/                    # Main package
│   ├── __init__.py
│   ├── models.py           # Data models
│   ├── cli.py              # CLI tool
│   ├── api/                # REST API
│   ├── ingestion/          # Document processors
│   ├── detection/          # Type detection
│   ├── tuning/             # Weight tuning
│   ├── storage/            # Document storage
│   ├── enrichment.py       # Metadata enrichment
│   ├── decay.py            # Time-based decay
│   ├── triad.py            # Context Triad (Hot/Warm/Cold)
│   ├── pragmatic_truth.py  # Source tracking
│   ├── routing/            # Heuristic routing
│   ├── conversation.py     # Conversation management
│   └── gateway/            # Trust Gateway
├── tests/                  # Test suite
├── examples/               # Example usage
│   ├── agents/            # Sample agent implementations
│   └── *.py               # Demo scripts
├── docs/                   # Documentation (markdown files)
├── run_tests.py           # Test runner
├── TESTING.md             # Testing guide
├── CONTRIBUTING.md        # This file
└── README.md              # Project overview
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write clear, documented code
- Follow existing code style
- Add docstrings to functions and classes
- Use type hints where appropriate

### 3. Add Tests

For any new functionality, add tests in `tests/`:

```python
"""
Test description.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from caas.module import NewFeature


def test_new_feature():
    """Test the new feature."""
    print("\n=== Testing New Feature ===")
    
    feature = NewFeature()
    result = feature.do_something()
    
    assert result is not None
    print("✓ Feature working correctly")
```

### 4. Run Tests

```bash
python run_tests.py
```

### 5. Commit Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: brief description

- Detailed point 1
- Detailed point 2
- Closes #123"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names

### Docstrings

Use Google-style docstrings:

```python
def extract_context(document_id: str, query: str, max_tokens: int = 2000) -> Tuple[str, Dict]:
    """
    Extract context from a document.
    
    Args:
        document_id: ID of document to extract from
        query: Search query
        max_tokens: Maximum tokens to extract
        
    Returns:
        Tuple of (context_string, metadata_dict)
        
    Raises:
        ValueError: If document not found
        
    Example:
        >>> context, metadata = extractor.extract_context("doc-123", "authentication")
        >>> print(len(context))
        1847
    """
    # Implementation
```

### Type Hints

Use type hints for function signatures:

```python
from typing import List, Dict, Optional

def process_documents(
    docs: List[Document],
    max_count: Optional[int] = None
) -> Dict[str, Any]:
    ...
```

## Testing Guidelines

### Test Coverage

- Write tests for all new features
- Test edge cases and error conditions
- Aim for clear, readable test code

### Test Structure

```python
def test_feature_name():
    """Test description."""
    print("\n=== Testing Feature ===")
    
    # Setup
    component = Component()
    
    # Execute
    result = component.method()
    
    # Assert
    assert result == expected_value
    print("✓ Test passed")
```

### Running Tests

```bash
# All tests
python run_tests.py

# Specific test
python -m tests.test_module_name
```

## Areas for Contribution

### High Priority

1. **Additional Document Processors**
   - Support for more file formats (DOCX, Markdown, etc.)
   - Better code language support
   - Improved structure detection

2. **Enhanced Detection**
   - Better document type classification
   - More sophisticated pattern matching
   - Machine learning-based detection

3. **Performance Optimization**
   - Faster document processing
   - Efficient storage mechanisms
   - Caching strategies

### Medium Priority

4. **API Enhancements**
   - Additional endpoints
   - WebSocket support for real-time updates
   - GraphQL API option

5. **CLI Improvements**
   - Interactive mode
   - Better output formatting
   - Progress indicators

6. **Documentation**
   - More examples
   - Tutorials
   - Video guides

### Lower Priority

7. **UI/Dashboard**
   - Web-based interface
   - Visualization of document structures
   - Analytics dashboard

8. **Integrations**
   - Slack bot
   - VS Code extension
   - Zapier integration

## Module-Specific Guidelines

### Ingestion Module (`caas/ingestion/`)

When adding new processors:
- Inherit from base `Processor` class
- Implement `process()` method
- Track document hierarchy
- Extract meaningful sections

### Detection Module (`caas/detection/`)

When adding detection patterns:
- Add patterns to appropriate category
- Test with diverse documents
- Consider false positives/negatives

### Tuning Module (`caas/tuning/`)

When adding tuning rules:
- Add to `TYPE_SPECIFIC_WEIGHTS`
- Document reasoning
- Test with real documents

## Documentation

### Inline Documentation

- Add docstrings to all public functions/classes
- Include examples in docstrings
- Explain complex algorithms

### README Updates

Update README.md when:
- Adding new features
- Changing API
- Updating installation process

### Architecture Documentation

Document architectural decisions in:
- Code comments for complex logic
- Separate docs for major changes
- Examples for new patterns

## Pull Request Process

1. **Before Submitting**
   - Run all tests
   - Update documentation
   - Add examples if needed
   - Rebase on latest main

2. **PR Description**
   - Describe what and why
   - Link related issues
   - Show before/after examples
   - List breaking changes

3. **Review Process**
   - Address review comments
   - Keep discussions focused
   - Be open to suggestions

4. **After Merge**
   - Delete your branch
   - Update your fork
   - Celebrate! 🎉

## Questions or Issues?

- **Bug reports**: Open an issue with reproduction steps
- **Feature requests**: Open an issue with use case description
- **Questions**: Start a discussion or open an issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Context-as-a-Service! 🚀
