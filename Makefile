.PHONY: test test-cov test-pydantic test-all lint format check-all check-consistency

# Run tests without coverage
test:
	poetry run pytest -v

# Run tests with coverage (full suite)
test-cov:
	poetry run pytest -v --cov=db_types --cov-report=term-missing --cov-fail-under=59

# Run only pydantic integration tests
test-pydantic:
	poetry run pytest tests/test_pydantic_integration.py -v

# Run all tests with coverage report
test-all:
	poetry run pytest -v --cov=db_types --cov-report=term-missing --cov-report=html --cov-fail-under=59
	@echo "Coverage report generated in htmlcov/index.html"

# Run linting
lint:
	poetry run ruff check src tests
	poetry run pyright

# Format code
format:
	poetry run black src tests
	poetry run isort src tests
	poetry run ruff check --fix src tests

# Run all checks (lint, format check, type check, tests with coverage)
check-all:
	poetry run black --check src tests
	poetry run isort --check-only src tests
	poetry run ruff check src tests
	poetry run pyright
	poetry run pytest -v --cov=db_types --cov-report=term-missing --cov-fail-under=59

# Check consistency between pre-commit, Makefile, and GitHub Actions
check-consistency:
	@python scripts/check_consistency.py
