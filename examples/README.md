# Python DB Types Examples

This directory contains example code demonstrating various features of the python-db-types library.

## Basic Usage

- **`dataclass_example.py`** - Basic dataclass integration with database types
- **`pydantic_example.py`** - Basic Pydantic model integration

## Constrained Types

- **`constraints_example.py`** - Using constrained numeric types with dataclasses
- **`pydantic_constraints_example.py`** - Using constrained numeric types with Pydantic
- **`clean_constraints_example.py`** - Demonstrates the enhanced API with `Integer(min_value=x)` syntax

## Running Examples

```bash
# Install the library first
pip install -e ..

# Run any example
python dataclass_example.py
python pydantic_example.py
python constraints_example.py
```

## Key Features Demonstrated

1. **Type Validation** - Automatic validation of values against database constraints
2. **Type Conversion** - Automatic conversion of strings to appropriate types
3. **Constraint Validation** - Min/max values, string lengths, numeric ranges
4. **Clean API** - Same syntax works for both Pydantic and dataclasses
5. **SQL Compatibility** - Generate SQL-compatible representations
