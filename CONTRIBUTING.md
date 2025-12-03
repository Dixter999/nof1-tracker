# Contributing to NOF1 Tracker

Thank you for your interest in contributing to NOF1 Tracker! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- PostgreSQL 16 (or use Docker)
- Git

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/nof1-tracker.git
   cd nof1-tracker
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Start the database**

   ```bash
   docker compose up -d postgres
   ```

6. **Run migrations**

   ```bash
   alembic upgrade head
   ```

7. **Verify setup**

   ```bash
   pytest
   ```

## How to Contribute

### Reporting Bugs

Before submitting a bug report:

1. Check the [existing issues](https://github.com/Dixter999/nof1-tracker/issues) to avoid duplicates
2. Use the bug report template when creating a new issue
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. Check existing issues and discussions for similar suggestions
2. Use the feature request template
3. Clearly describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered

### Contributing Code

1. **Find an issue to work on** or create one for discussion
2. **Comment on the issue** to express your interest
3. **Fork the repository** and create a feature branch
4. **Write tests** for your changes
5. **Implement your changes**
6. **Submit a pull request**

## Pull Request Process

### Branch Naming

Use descriptive branch names:

- `feature/add-model-analytics` - New features
- `fix/leaderboard-parsing-error` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/database-connection` - Code refactoring

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(collector): add support for position tracking
fix(database): handle special characters in passwords
docs(readme): update installation instructions
```

### PR Checklist

Before submitting your PR, ensure:

- [ ] Code follows the project's coding standards
- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black src/ tests/`)
- [ ] Linting passes (`ruff check src/ tests/`)
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated if needed
- [ ] Commit messages follow conventions

### Review Process

1. Submit your PR against the `main` branch
2. Ensure CI checks pass
3. Request review from maintainers
4. Address any feedback
5. Once approved, a maintainer will merge your PR

## Coding Standards

### Python Style

We follow PEP 8 with these tools:

- **Black** for code formatting
- **Ruff** for linting
- **Type hints** for all public functions

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```

### Code Organization

- Keep functions focused and small
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Follow the existing project structure

### Type Hints

```python
def process_trade(trade_data: dict[str, Any], model_id: int) -> Trade:
    """Process and save a trade record.

    Args:
        trade_data: Raw trade data from the API.
        model_id: ID of the model that made the trade.

    Returns:
        The created Trade object.

    Raises:
        ValueError: If trade_data is invalid.
    """
    ...
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nof1_tracker

# Run specific test file
pytest tests/test_database/test_models.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source code structure
- Use descriptive test names
- Include both positive and negative test cases

```python
def test_leaderboard_entry_creation():
    """Test that LeaderboardEntry is created with correct values."""
    entry = LeaderboardEntry(
        model_name="Test Model",
        provider="Test Provider",
        rank=1,
        ...
    )
    assert entry.model_name == "Test Model"
    assert entry.rank == 1
```

### Test Coverage

- Aim for at least 80% code coverage
- Focus on testing business logic
- Include edge cases and error handling

## Documentation

### Code Documentation

- Add docstrings to all public modules, classes, and functions
- Use Google-style docstrings
- Include examples where helpful

### Project Documentation

- Update README.md for user-facing changes
- Update docs/DATABASE.md for schema changes
- Add new documentation files as needed

### API Documentation

When adding new features, document:

- Function signatures and parameters
- Return values and types
- Exceptions that may be raised
- Usage examples

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search closed issues
3. Open a new issue with the "question" label

Thank you for contributing to NOF1 Tracker!
