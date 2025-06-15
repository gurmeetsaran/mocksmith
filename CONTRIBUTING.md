# Contributing to python-db-types

Thank you for your interest in contributing to python-db-types! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/yourusername/python-db-types.git
   cd python-db-types
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev,pydantic]"
   ```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=db_types --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_string_types.py -v
```

## Code Quality

Before submitting a PR, ensure your code passes all quality checks:

```bash
# Format code
black src tests
isort src tests

# Lint
ruff check src tests

# Type check
mypy src

# Run all tests
pytest
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (formatting, missing semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding or updating tests
- **build**: Changes that affect the build system or dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Scopes (optional)

- **core**: Core functionality
- **types**: Type implementations (string, numeric, etc.)
- **pydantic**: Pydantic integration
- **dataclass**: Dataclass integration
- **tests**: Test-related changes
- **docs**: Documentation
- **deps**: Dependencies

### Examples

```bash
# Feature
feat(types): add support for JSON type
feat(pydantic): add custom validators for email type

# Bug fix
fix(numeric): correct decimal precision validation
fix: handle None values in serialize method

# Documentation
docs: update README with dataclass examples
docs(api): add type hints to all public methods

# Refactoring
refactor(types): extract common validation logic
refactor: simplify base type implementation

# Tests
test(types): add edge cases for VARCHAR validation
test: increase coverage for temporal types

# Other
chore: update dependencies
ci: add Python 3.12 to test matrix
```

### Pull Request Titles

PR titles must follow the same conventional commit format as they will become the merge commit message.

✅ Good PR titles:
- `feat: add support for UUID type`
- `fix(pydantic): correct validation for nullable fields`
- `docs: add migration guide from v1 to v2`

❌ Bad PR titles:
- `Add UUID type`
- `Fix bug`
- `Update docs`

## Pull Request Process

1. Create a new branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. Make your changes and commit using conventional commits

3. Push to your fork and create a PR

4. Ensure all CI checks pass

5. Wait for code review

## Code Style Guidelines

- Follow PEP 8 with a line length of 100 characters
- Use type hints for all function signatures
- Add docstrings to all public functions and classes
- Keep functions focused and small
- Write descriptive variable names

## Testing Guidelines

- Write tests for all new functionality
- Maintain or increase code coverage (minimum 80%)
- Test edge cases and error conditions
- Use descriptive test names that explain what is being tested

## Questions?

Feel free to open an issue for any questions about contributing!
