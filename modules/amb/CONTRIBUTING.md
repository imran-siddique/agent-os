# Contributing to AMB

Thank you for your interest in contributing to AMB (Agent Message Bus)! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/imran-siddique/amb.git
   cd amb
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode with all dependencies:
   ```bash
   pip install -e ".[dev,all]"
   ```

4. Verify installation:
   ```bash
   pytest tests/ -v
   ```

## Code Style

We use the following tools to maintain code quality:

- **Ruff** for linting and formatting
- **MyPy** for type checking
- **pytest** for testing

### Running Checks

```bash
# Run linter
ruff check amb_core/ tests/

# Run formatter
ruff format amb_core/ tests/

# Run type checker
mypy amb_core/

# Run tests with coverage
pytest tests/ -v --cov=amb_core --cov-report=term-missing
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Write Code

- Follow the existing code style
- Add type hints to all functions
- Write Google-style docstrings
- Keep the API minimal and consistent

### 3. Write Tests

- Add tests for new functionality in `tests/`
- Ensure all tests pass before submitting

### 4. Update Documentation

- Update docstrings for any API changes
- Update README.md if adding new features
- Add examples for new functionality

### 5. Submit a Pull Request

1. Push your branch to GitHub
2. Open a Pull Request against `main`
3. Fill in the PR template
4. Wait for CI checks to pass
5. Request a review

## Pull Request Guidelines

- Keep PRs focused and atomic
- Write clear commit messages
- Update the changelog if applicable
- Ensure CI passes before requesting review

## Code Structure

```
amb_core/
├── __init__.py          # Public API exports
├── models.py            # Message and MessagePriority
├── broker.py            # BrokerAdapter ABC
├── bus.py               # MessageBus facade
├── memory_broker.py     # In-memory implementation
├── hf_utils.py          # Hugging Face utilities
└── adapters/
    ├── __init__.py
    ├── redis_broker.py
    ├── rabbitmq_broker.py
    └── kafka_broker.py
```

## Adding a New Broker Adapter

1. Create a new file in `amb_core/adapters/`
2. Implement the `BrokerAdapter` interface
3. Add lazy import in `amb_core/adapters/__init__.py`
4. Add optional dependency in `pyproject.toml`
5. Add tests in `tests/`
6. Update documentation

## Running Experiments

```bash
# Run benchmark suite
python experiments/reproduce_results.py --seed 42 --iterations 1000
```

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions

Thank you for contributing! 🎉
