# Testing Guidelines

## Test Coverage

The project currently maintains a test coverage of ~66%. All tests run on Python 3.9 and above.

The main areas with lower coverage are:

### annotations.py (0% coverage)
The `annotations.py` file contains helper functions that create type annotations for use with Pydantic and dataclasses. These functions return `Annotated` types which are primarily used at type-checking time rather than runtime, making them challenging to test directly.

To properly test these annotations, you would need to:
1. Create Pydantic models using the annotations
2. Test validation and serialization behavior
3. Verify type hints are correctly applied

### Why 80% coverage is challenging

1. **Type Annotation Functions**: The annotation helper functions (VARCHAR, INTEGER, etc.) are designed to work with Python's type system and Pydantic's validation. They return `Annotated` types that are processed by Pydantic at model definition time.

2. **Edge Cases**: Some code paths handle rare edge cases (like special decimal values, binary format conversions) that are important for robustness but less critical for typical usage.

3. **Integration-Heavy Code**: Much of the code is designed to integrate with external libraries (Pydantic, dataclasses) making isolated unit testing more complex.


## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=db_types --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_numeric_types.py -v

# Run pydantic integration tests
poetry run pytest tests/test_pydantic_integration.py -v
```

## Test Structure

- `test_boolean_binary_types.py` - Tests for BOOLEAN, BINARY, VARBINARY, and BLOB types
- `test_dataclass_integration.py` - Tests for dataclass integration
- `test_numeric_types.py` - Tests for INTEGER, BIGINT, DECIMAL, FLOAT, etc.
- `test_pydantic_integration.py` - Tests for Pydantic model integration
- `test_string_types.py` - Tests for VARCHAR, CHAR, TEXT types
- `test_temporal_types.py` - Tests for DATE, TIME, TIMESTAMP, DATETIME types

## Future Improvements

To reach higher coverage, consider:
1. Adding integration tests that use the annotation functions with real Pydantic models
2. Testing more edge cases in binary and numeric type conversions
3. Adding property-based tests for validation logic
4. Creating end-to-end tests that demonstrate full workflows
