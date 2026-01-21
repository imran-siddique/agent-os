# Software Development Contribution Guide

## Getting Started

Welcome to our project! This guide will help you start contributing.

### Prerequisites

- Python 3.8 or higher
- Git version control
- A GitHub account

### Setting Up Your Environment

```bash
# Clone the repository
git clone https://github.com/company/project.git
cd project

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` for new features
- `bugfix/` for bug fixes
- `docs/` for documentation updates
- `refactor/` for code refactoring

### 2. Make Your Changes

- Write clear, concise commit messages
- Follow the coding style guide (see STYLE_GUIDE.md)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Run linting
black src/ tests/
ruff check src/ tests/

# Check type hints
mypy src/
```

### 4. Submit a Pull Request

1. Push your branch to GitHub
2. Open a pull request against the `main` branch
3. Fill out the PR template completely
4. Request reviews from appropriate team members
5. Address feedback and update your PR

## Code Review Process

### Review Guidelines

- All PRs require at least 2 approvals
- CI checks must pass before merging
- Reviews should be completed within 2 business days
- Be constructive and respectful in feedback

### What Reviewers Look For

- Code correctness and functionality
- Test coverage (minimum 80%)
- Documentation completeness
- Code style consistency
- Security considerations
- Performance implications

## Testing

### Unit Tests

Write unit tests for all new functions and classes:

```python
def test_user_authentication():
    user = User(username="test", password="secure123")
    assert user.is_authenticated() == True
```

### Integration Tests

Test interactions between components:

```python
def test_api_endpoint():
    response = client.get("/api/users")
    assert response.status_code == 200
```

### Test Coverage

Maintain minimum 80% code coverage:

```bash
pytest --cov=src --cov-report=html
```

## Documentation

### Code Documentation

Use docstrings for all public functions and classes:

```python
def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculate the discounted price.
    
    Args:
        price: Original price
        discount_percent: Discount percentage (0-100)
        
    Returns:
        Discounted price
        
    Raises:
        ValueError: If discount_percent is not in valid range
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
```

### README Updates

Update the README when adding:
- New features
- Configuration options
- Installation requirements
- Usage examples

## Release Process

### Version Numbers

We follow Semantic Versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create a git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. GitHub Actions will automatically build and publish

## Getting Help

- Slack: #dev-team channel
- Email: dev-team@company.com
- Office Hours: Tuesdays 2-3 PM EST

## Code of Conduct

Please read and follow our CODE_OF_CONDUCT.md. We are committed to providing a welcoming and inclusive environment for all contributors.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
