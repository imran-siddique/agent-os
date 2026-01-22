# Contributing to CMVK

Thank you for your interest in contributing to the Cross-Model Verification Kernel! This document provides guidelines and instructions for contributing.

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/cross-model-verification-kernel.git
cd cross-model-verification-kernel
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
# or
pip install -e ".[all]"  # includes notebooks, sandbox, etc.
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

This will automatically run linting and formatting checks before each commit.

## Code Standards

### Style

- **Formatter**: [Black](https://black.readthedocs.io/) with 100 character line length
- **Linter**: [Ruff](https://docs.astral.sh/ruff/) for fast, comprehensive linting
- **Import Sorting**: [isort](https://pycqa.github.io/isort/) with Black-compatible profile
- **Type Hints**: Required for all public functions

### Running Checks Manually

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Run linter
ruff check src/ tests/ --fix

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/cross_model_verification_kernel --cov-report=html

# Run specific test file
pytest tests/test_kernel.py -v

# Run tests matching a pattern
pytest tests/ -k "test_verification" -v

# Skip slow/integration tests
pytest tests/ -m "not slow and not integration"
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_kernel_rejects_same_model_generator_verifier`
- Use pytest fixtures for common setup
- Mock external API calls (don't make real API calls in tests)

Example:

```python
import pytest
from unittest.mock import MagicMock

from cross_model_verification_kernel import VerificationKernel

def test_kernel_initialization():
    """Test that kernel initializes with valid configuration."""
    generator = MagicMock()
    verifier = MagicMock()
    
    kernel = VerificationKernel(generator=generator, verifier=verifier)
    
    assert kernel.generator == generator
    assert kernel.verifier == verifier
```

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(kernel): add strategy banning mechanism
fix(verifier): handle empty response from Gemini API
docs(readme): update installation instructions
test(agents): add unit tests for AnthropicVerifier
```

## Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation if needed

3. **Run Checks**
   ```bash
   pre-commit run --all-files
   pytest tests/ -v
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   git push origin feat/your-feature-name
   ```

5. **Open a Pull Request**
   - Provide a clear description of changes
   - Link any related issues
   - Ensure CI passes

## Areas for Contribution

### High Priority

- **New Model Providers**: Add support for LLaMA, Mistral, Cohere, etc.
- **Enhanced Prompts**: Improve adversarial verification prompts
- **Bug Fixes**: Check open issues for bugs

### Research Extensions

- **New Datasets**: Add support for other benchmarks (MBPP, LogicGrids, etc.)
- **Ablation Studies**: Run experiments with different configurations
- **Graph Memory Improvements**: Better state management algorithms

### Documentation

- **Tutorials**: Step-by-step guides for common use cases
- **API Reference**: Docstrings and type hints
- **Examples**: More example scripts

## Project Structure

```
src/cross_model_verification_kernel/
├── __init__.py          # Package exports
├── __main__.py          # python -m support
├── cli.py               # CLI commands
├── core/
│   ├── kernel.py        # Main verification loop
│   ├── graph_memory.py  # Graph of Truth
│   └── types.py         # Data classes
├── agents/
│   ├── base.py          # Abstract base class
│   ├── generator_openai.py
│   ├── verifier_gemini.py
│   └── verifier_anthropic.py
├── tools/
│   ├── sandbox.py       # Code execution
│   └── visualizer.py    # Trace replay
└── datasets/
    └── humaneval_loader.py
```

## Questions?

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🚀
