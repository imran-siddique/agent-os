# Testing Guide

This guide explains how to test the Context-as-a-Service codebase.

## Quick Start

Run all tests:

```bash
python run_tests.py
```

Run a specific test:

```bash
python -m tests.test_functionality
```

## Test Organization

Tests are organized in the `tests/` directory:

```
tests/
├── __init__.py
├── conftest.py                      # pytest configuration
├── test_functionality.py            # Basic functionality tests
├── test_structure_aware_indexing.py # Structure-aware indexing tests
├── test_metadata_injection.py       # Metadata enrichment tests
├── test_time_decay.py              # Time-based decay tests
├── test_context_triad.py           # Context Triad (Hot/Warm/Cold) tests
├── test_pragmatic_truth.py         # Pragmatic Truth (source tracking) tests
├── test_heuristic_router.py        # Heuristic Router tests
├── test_conversation_manager.py    # Conversation Manager tests
└── test_trust_gateway.py           # Trust Gateway tests
```

## Test Coverage

### Core Functionality
- **test_functionality.py**: Tests basic document processing, detection, and tuning
- **test_structure_aware_indexing.py**: Tests 3-tier content classification (High/Medium/Low)

### Advanced Features
- **test_metadata_injection.py**: Tests metadata enrichment for context preservation
- **test_time_decay.py**: Tests time-based relevance decay ("The Half-Life of Truth")
- **test_context_triad.py**: Tests Hot/Warm/Cold context management
- **test_pragmatic_truth.py**: Tests source tracking and conflict detection
- **test_heuristic_router.py**: Tests deterministic query routing (Speed > Smarts)
- **test_conversation_manager.py**: Tests sliding window conversation management (FIFO)
- **test_trust_gateway.py**: Tests enterprise security gateway

## Running Tests

### All Tests
```bash
python run_tests.py
```

### Individual Module Tests
```bash
python -m tests.test_functionality
python -m tests.test_heuristic_router
python -m tests.test_trust_gateway
```

### Using pytest (optional)
If you have pytest installed:

```bash
pytest tests/
pytest tests/test_functionality.py
pytest tests/ -v  # verbose output
pytest tests/ -k "decay"  # run tests matching "decay"
```

## Test Structure

Each test file follows a similar structure:

```python
"""
Test description
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from caas.module import Component


def test_feature():
    """Test a specific feature."""
    print("\n=== Testing Feature ===")
    
    # Setup
    component = Component()
    
    # Execute
    result = component.do_something()
    
    # Assert
    assert result is not None
    print("✓ Feature working correctly")


if __name__ == "__main__":
    print("=" * 60)
    print("Module Tests")
    print("=" * 60)
    
    try:
        test_feature()
        # ... more tests ...
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

## Example Agents

The `examples/agents/` directory contains sample agents that demonstrate how to use multiple modules together:

### Intelligent Document Analyzer
Demonstrates using 6+ modules together:
- Structure-aware indexing
- Metadata enrichment
- Time-based decay
- Heuristic routing
- Conversation management
- Pragmatic truth tracking

```bash
PYTHONPATH=. python examples/agents/intelligent_document_analyzer.py
```

### Enterprise Security Agent
Demonstrates security-focused usage:
- Trust Gateway (on-prem deployment)
- Data classification
- Audit trail
- Compliance reporting
- Secure conversation management

```bash
PYTHONPATH=. python examples/agents/enterprise_security_agent.py
```

## Continuous Integration

To set up CI testing, add this to your `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py
```

## Writing New Tests

When adding new functionality:

1. Create a test file in `tests/test_<module>.py`
2. Import your module with the path fix:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   ```
3. Write test functions with descriptive names
4. Use print statements for clear output
5. Assert expected behavior
6. Add to `run_tests.py` TEST_FILES list

## Best Practices

- **Test naming**: Use descriptive names like `test_decay_calculation()` not `test1()`
- **Print output**: Use `print()` statements to show what's being tested
- **Assertions**: Always include assertions to verify correctness
- **Documentation**: Add docstrings explaining what each test verifies
- **Independence**: Tests should not depend on other tests
- **Cleanup**: Clean up any resources (files, connections) after tests

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'caas'`:

```bash
# Use module syntax
python -m tests.test_functionality

# Or set PYTHONPATH
PYTHONPATH=. python tests/test_functionality.py
```

### Test Timeout
Tests have a 60-second timeout. If a test times out:
- Check for infinite loops
- Verify external dependencies are available
- Consider breaking into smaller tests

## Demo Files

The `examples/` directory contains demonstration scripts:

```bash
PYTHONPATH=. python examples/demo_time_decay.py
PYTHONPATH=. python examples/demo_heuristic_router.py
PYTHONPATH=. python examples/demo_trust_gateway.py
```

These demos show real-world usage examples and can serve as integration tests.

## Code Coverage (Optional)

To measure code coverage:

```bash
pip install coverage
coverage run run_tests.py
coverage report
coverage html  # generates htmlcov/index.html
```

## Performance Testing

For performance testing:

```bash
pip install pytest-benchmark
pytest tests/ --benchmark-only
```

## Questions?

For questions about testing, see:
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [README.md](README.md) - Project overview
- GitHub Issues - Report bugs or ask questions
