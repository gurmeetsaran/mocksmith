# Python DB Types Examples

This directory contains comprehensive example code demonstrating all features of the python-db-types library.

## Example Files

### dataclass_example.py
Comprehensive dataclass integration examples including:
- **Basic Usage**: All data types (String, Numeric, Date/Time, Binary, Boolean)
- **Constrained Types**: PositiveInteger, NonNegativeInteger, and custom constraints
- **TINYINT**: 8-bit integer for small bounded values (percentages, levels, flags)
- **REAL vs FLOAT**: Different SQL type generation for floating-point numbers
- **SQL Serialization**: Convert instances to SQL-ready format
- **Validation**: Automatic validation with detailed error messages
- **Type Conversion**: Automatic conversion from strings to proper types

### pydantic_example.py
Comprehensive Pydantic integration examples including:
- **All Data Types**: With automatic validation and conversion
- **Field Validators**: Custom validation logic with @field_validator
- **Computed Properties**: Dynamic properties based on other fields
- **Constrained Types**: Complex business logic with constraints
- **JSON Serialization**: Custom encoders for dates, decimals, and binary data
- **Model Configuration**: Validation on assignment and other settings
- **TINYINT and REAL**: Special numeric types with proper validation
- **Boolean Conversions**: Flexible parsing of various boolean formats

## Key Demonstrations

Each example file contains multiple model classes demonstrating real-world use cases:

1. **Employee Management System** - Complete employee model with all field types
2. **E-commerce Orders** - Product inventory and order processing with constraints
3. **User Accounts** - User profiles with age restrictions and preferences
4. **Game Characters** - Complex stats system with positive/negative modifiers
5. **System Configuration** - Using TINYINT for configuration values
6. **Scientific Measurements** - Floating-point precision with REAL vs FLOAT
7. **API Rate Limiting** - Configuration with precise numeric constraints

## Running Examples

```bash
# Install the library first (from the project root)
pip install -e .

# Or install with Pydantic support
pip install -e ".[pydantic]"

# Run the examples
python examples/dataclass_example.py
python examples/pydantic_example.py
```

## Features Highlighted

### Type Safety
- Automatic validation against SQL constraints
- Type conversion with error handling
- Range validation for numeric types
- Length validation for string types

### Clean API
- Same intuitive syntax for both Pydantic and dataclasses
- No need for complex type annotations
- Clear, readable field definitions

### SQL Compatibility
- Generate proper SQL type definitions
- Serialize to SQL-compatible formats
- Handle NULL/NOT NULL constraints
- Support for all standard SQL types

### Advanced Features
- Constrained numeric types (min/max values, multiples)
- Optional fields with proper NULL handling
- Default values with validation
- Custom validators for business logic
- JSON serialization for APIs

## Type Reference

### String Types
- `Varchar(n)` - Variable-length string with max length
- `Char(n)` - Fixed-length string (padded)
- `Text()` - Large text field

### Numeric Types
- `Integer()` - 32-bit integer
- `BigInt()` - 64-bit integer
- `SmallInt()` - 16-bit integer
- `TinyInt()` - 8-bit integer
- `DecimalType(p, s)` - Fixed-point decimal
- `Numeric(p, s)` - Alias for DecimalType
- `Money()` - Alias for Decimal(19, 4)
- `Float()` - Floating point (FLOAT SQL type)
- `Real()` - Single precision (REAL SQL type)
- `Double()` - Double precision

### Constrained Types
- `PositiveInteger()` - Must be > 0
- `NonNegativeInteger()` - Must be >= 0
- `NegativeInteger()` - Must be < 0
- `NonPositiveInteger()` - Must be <= 0

### Date/Time Types
- `Date()` - Date only
- `Time()` - Time only
- `Timestamp()` - Date and time with timezone
- `DateTime()` - Date and time without timezone

### Other Types
- `Boolean()` - Flexible boolean parsing
- `Binary(n)` - Fixed-length binary
- `VarBinary(n)` - Variable-length binary
- `Blob()` - Large binary object
