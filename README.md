# python-db-types

[![CI](https://github.com/gurmeetsaran/python-db-types/actions/workflows/ci.yml/badge.svg)](https://github.com/gurmeetsaran/python-db-types/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/gurmeetsaran/python-db-types/branch/main/graph/badge.svg)](https://codecov.io/gh/gurmeetsaran/python-db-types)
[![PyPI version](https://badge.fury.io/py/python-db-types.svg)](https://badge.fury.io/py/python-db-types)
[![Python Versions](https://img.shields.io/pypi/pyversions/python-db-types.svg)](https://pypi.org/project/python-db-types/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

Specialized database types with validation for Python dataclasses and Pydantic models.

## Features

- **Type-safe database columns**: Define database columns with proper validation
- **Serialization/Deserialization**: Automatic conversion between Python and SQL types
- **Dataclass Integration**: Full support for Python dataclasses with validation
- **Pydantic Integration**: First-class Pydantic support with automatic validation
- **Clean API**: Simple, intuitive interface for both Pydantic AND dataclasses - just `name: Varchar(50)`
- **Comprehensive Types**: STRING (VARCHAR, CHAR, TEXT), NUMERIC (INTEGER, DECIMAL, FLOAT), TEMPORAL (DATE, TIME, TIMESTAMP), and more

## Why python-db-types?

### Before (Traditional Approach)
```python
from typing import Annotated
from pydantic import BaseModel, Field, validator
from decimal import Decimal

class Product(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    price: Annotated[Decimal, Field(decimal_places=2, max_digits=10)]
    in_stock: bool = True

    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price must be non-negative')
        return v
```

### After (With python-db-types)
```python
from pydantic import BaseModel
from db_types import Varchar, Money, Boolean

class Product(BaseModel):
    name: Varchar(100)         # Enforces VARCHAR(100) constraint
    price: Money()             # Decimal with proper precision
    in_stock: Boolean() = True # Flexible boolean parsing
```

✨ **Benefits:**
- Same clean syntax for both Pydantic and dataclasses
- Automatic SQL constraint validation
- Type conversion (string "99.99" → Decimal)
- Better IDE support and type hints
- Write once, use with either framework

## Installation

```bash
pip install python-db-types
```

For Pydantic support:
```bash
pip install "python-db-types[pydantic]"
```

## Quick Start

### Clean Interface (Works with both Pydantic and Dataclasses!) ✨

```python
from pydantic import BaseModel
from db_types import Varchar, Integer, Boolean, Money

class User(BaseModel):
    id: Integer()
    username: Varchar(50)
    email: Varchar(255)
    is_active: Boolean() = True
    balance: Money() = "0.00"

# Automatic validation and type conversion
user = User(
    id=1,
    username="john_doe",
    email="john@example.com",
    is_active="yes",      # Converts to True
    balance="1234.56"     # Converts to Decimal('1234.56')
)
```

The same syntax works with dataclasses! See full examples:
- [`examples/pydantic_example.py`](examples/pydantic_example.py) - Comprehensive Pydantic examples with all features
- [`examples/dataclass_example.py`](examples/dataclass_example.py) - Comprehensive dataclass examples with all features

### Common Use Cases

**E-commerce Product Model:**

```python
from pydantic import BaseModel
from db_types import Varchar, Text, Money, Boolean, Timestamp

class Product(BaseModel):
    sku: Varchar(20)
    name: Varchar(100)
    description: Text()
    price: Money()
    in_stock: Boolean() = True
    created_at: Timestamp()
```

**User Account with Constraints:**

```python
from db_types import Integer, PositiveInteger, NonNegativeInteger

class UserAccount(BaseModel):
    user_id: PositiveInteger()
    age: Integer(min_value=13, max_value=120)
    balance_cents: NonNegativeInteger()
```

See complete working examples:
- [`examples/`](examples/) - All example files with detailed documentation
- [`examples/pydantic_example.py`](examples/pydantic_example.py) - All features including constraints
- [`examples/dataclass_example.py`](examples/dataclass_example.py) - All features including constraints

## Clean Annotation Interface

The library provides a clean, Pythonic interface for defining database types that works with both Pydantic and dataclasses:

```python
# Works with Pydantic
from pydantic import BaseModel
from db_types import Varchar, Integer, Money, Date, Boolean, Text

class Product(BaseModel):
    sku: Varchar(20)
    name: Varchar(100)
    description: Text()
    price: Money()  # Alias for Decimal(19, 4)
    in_stock: Boolean()

# Also works with dataclasses!
from dataclasses import dataclass
from db_types.dataclass_integration import validate_dataclass

@validate_dataclass
@dataclass
class Product:
    sku: Varchar(20)
    name: Varchar(100)
    description: Text()
    price: Money() = Decimal("0.00")
    in_stock: Boolean() = True

# Instead of the verbose way:
# from typing import Annotated
# from db_types.types.string import VARCHAR
# from db_types.types.numeric import DECIMAL
# class Product:
#     sku: Annotated[str, VARCHAR(20)]
#     name: Annotated[str, VARCHAR(100)]
#     price: Annotated[Decimal, DECIMAL(19, 4)]
```

### Available Clean Types:

**String Types:**
- `Varchar(length)` → Variable-length string
- `Char(length)` → Fixed-length string
- `Text()` → Large text field
- `String` → Alias for Varchar

**Numeric Types:**
- `Integer()` → 32-bit integer
- `BigInt()` → 64-bit integer
- `SmallInt()` → 16-bit integer
- `TinyInt()` → 8-bit integer
- `DecimalType(precision, scale)` → Fixed-point decimal
- `Numeric(precision, scale)` → Alias for DecimalType
- `Money()` → Alias for Decimal(19, 4)
- `Float()` → Floating point (generates FLOAT SQL type)
- `Real()` → Floating point (generates REAL SQL type, typically single precision in SQL)
- `Double()` → Double precision

**Constrained Numeric Types:**
- `PositiveInteger()` → Integer > 0
- `NegativeInteger()` → Integer < 0
- `NonNegativeInteger()` → Integer ≥ 0
- `NonPositiveInteger()` → Integer ≤ 0
- `ConstrainedInteger(min_value=x, max_value=y, multiple_of=z)` → Custom constraints
- `ConstrainedBigInt(...)` → Constrained 64-bit integer
- `ConstrainedSmallInt(...)` → Constrained 16-bit integer
- `ConstrainedTinyInt(...)` → Constrained 8-bit integer

**Temporal Types:**
- `Date()` → Date only
- `Time()` → Time only
- `Timestamp()` → Date and time with timezone
- `DateTime()` → Date and time without timezone

**Other Types:**
- `Boolean()` / `Bool()` → Boolean with flexible parsing
- `Binary(length)` → Fixed binary
- `VarBinary(max_length)` → Variable binary
- `Blob()` → Large binary object

## Pydantic Integration Features

### Optional Fields Pattern

Python's `Optional` type indicates fields that can be None:

```python
from typing import Optional
from pydantic import BaseModel
from db_types import Varchar, Integer, Text

class Example(BaseModel):
    # Required field
    required_field: Varchar(50)

    # Optional field (can be None)
    optional_field: Optional[Varchar(50)] = None

    # Field with default value
    status: Varchar(20) = "active"
```

**Best Practice**: For optional fields, use `Optional[Type]` with `= None`:
```python
bio: Optional[Text()] = None           # Clear and explicit
phone: Optional[Varchar(20)] = None    # Optional field with no default
```

### Automatic Type Conversion

```python
from pydantic import BaseModel
from db_types import Money, Boolean, Date, Timestamp

class Order(BaseModel):
    # String to Decimal conversion
    total: Money()

    # Flexible boolean parsing
    is_paid: Boolean()

    # String to date conversion
    order_date: Date()

    # String to datetime conversion
    created_at: Timestamp()

# All these string values are automatically converted
order = Order(
    total="99.99",           # → Decimal('99.99')
    is_paid="yes",           # → True
    order_date="2023-12-15", # → date(2023, 12, 15)
    created_at="2023-12-15T10:30:00"  # → datetime
)
```

### Field Validation with Pydantic

```python
from pydantic import BaseModel, field_validator
from db_types import Varchar, Integer, Money

class Product(BaseModel):
    name: Varchar(50)
    price: Money()
    quantity: Integer()

    @field_validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @field_validator('quantity')
    def quantity_non_negative(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v
```

### Model Configuration

```python
from pydantic import BaseModel, ConfigDict
from db_types import Varchar, Money, Timestamp

class StrictModel(BaseModel):
    model_config = ConfigDict(
        # Validate on assignment
        validate_assignment=True,
        # Use Enum values
        use_enum_values=True,
        # Custom JSON encoders
        json_encoders={
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    )

    name: Varchar(100)
    price: Money()
    updated_at: Timestamp()
```

## Working Examples

For complete working examples, see the [`examples/`](examples/) directory:

- [`dataclass_example.py`](examples/dataclass_example.py) - Comprehensive dataclass examples including:
  - All data types (String, Numeric, Date/Time, Binary, Boolean)
  - Constrained numeric types (PositiveInteger, NonNegativeInteger, etc.)
  - Custom constraints (min_value, max_value, multiple_of)
  - TINYINT usage for small bounded values
  - REAL vs FLOAT distinction
  - SQL serialization
  - Validation and error handling

- [`pydantic_example.py`](examples/pydantic_example.py) - Comprehensive Pydantic examples including:
  - All data types with automatic validation
  - Field validators and computed properties
  - Constrained types with complex business logic
  - JSON serialization with custom encoders
  - Model configuration and validation on assignment
  - TINYINT and REAL type usage
  - Boolean type conversions

### Example: E-commerce Order System

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from db_types import Varchar, Integer, Date, DecimalType, Text, BigInt, Timestamp
from db_types.dataclass_integration import validate_dataclass

@validate_dataclass
@dataclass
class Customer:
    customer_id: Integer()
    first_name: Varchar(50)
    last_name: Varchar(50)
    email: Varchar(100)
    phone: Optional[Varchar(20)]
    date_of_birth: Optional[Date()]

@validate_dataclass
@dataclass
class Order:
    order_id: BigInt()
    customer_id: Integer()
    order_date: Timestamp(with_timezone=False)
    total_amount: DecimalType(12, 2)
    status: Varchar(20)
    notes: Optional[Text()]

# Create instances
customer = Customer(
    customer_id=1,
    first_name="Jane",
    last_name="Smith",
    email="jane.smith@email.com",
    phone="+1-555-0123",
    date_of_birth=date(1990, 5, 15)
)

order = Order(
    order_id=1001,
    customer_id=1,
    order_date=datetime(2023, 12, 15, 14, 30, 0),
    total_amount=Decimal("299.99"),
    status="pending",
    notes="Rush delivery requested"
)

# Convert to SQL-ready format
print(order.to_sql_dict())
```

For more complete examples including financial systems, authentication, and SQL testing integration,
see the [`examples/`](examples/) directory.

### Default Value Validation in Dataclasses

When using `@validate_dataclass`, default values are validated when an instance is created, not when the class is defined:

```python
@validate_dataclass
@dataclass
class Config:
    # This class definition succeeds even with invalid default
    hour: SmallInt(min_value=0, max_value=23) = 24

# But creating an instance fails with validation error
try:
    config = Config()  # Raises ValueError: Value 24 exceeds maximum 23
except ValueError as e:
    print(f"Validation error: {e}")

# You can override with valid values
config = Config(hour=12)  # Works fine
```

This behavior is consistent with Python's normal evaluation of default values and ensures that validation runs for all values, including defaults.

## Advanced Features

### Custom Validation

```python
@validate_dataclass
@dataclass
class CustomProduct:
    sku: Annotated[str, VARCHAR(20)]  # Required field
    name: Annotated[str, VARCHAR(100)]  # Required field
    description: Annotated[Optional[str], VARCHAR(500)]  # Optional field
```

### Working with Different Types

```python
# Integer types with range validation
small_value = SMALLINT()
small_value.validate(32767)  # OK
# small_value.validate(32768)  # Raises ValueError - out of range

# Decimal with precision
money = DECIMAL(19, 4)
money.validate("12345.6789")  # OK
# money.validate("12345.67890")  # Raises ValueError - too many decimal places

# Time with precision
timestamp = TIMESTAMP(precision=0)  # No fractional seconds
timestamp.validate("2023-12-15T10:30:45.123456")  # Microseconds will be truncated

# Boolean accepts various formats
bool_type = BOOLEAN()
bool_type.deserialize("yes")    # True
bool_type.deserialize("1")      # True
bool_type.deserialize("false")  # False
bool_type.deserialize(0)        # False
```

### Constrained Numeric Types

The library provides specialized numeric types with built-in constraints for common validation scenarios:

```python
from db_types import Integer, PositiveInteger, NonNegativeInteger

# Enhanced Integer functions - no constraints = standard type
id: Integer()                    # Standard 32-bit integer
quantity: Integer(min_value=0)   # With constraints (same as NonNegativeInteger)
discount: Integer(min_value=0, max_value=100)  # Percentage 0-100
price: Integer(positive=True)    # Same as PositiveInteger()

# Specialized constraint types
id: PositiveInteger()            # > 0
quantity: NonNegativeInteger()   # >= 0
```

For complete examples with both dataclasses and Pydantic, see:
- [`examples/dataclass_example.py`](examples/dataclass_example.py) - All constraint examples with dataclasses
- [`examples/pydantic_example.py`](examples/pydantic_example.py) - All constraint examples with Pydantic

**Available Constraint Options:**

```python
# Enhanced Integer functions - no constraints = standard type
Integer()                   # Standard 32-bit integer
Integer(min_value=0)        # With constraints
Integer(positive=True)      # Shortcut for > 0
BigInt()                    # Standard 64-bit integer
BigInt(min_value=0, max_value=1000000)  # With constraints
SmallInt()                  # Standard 16-bit integer
SmallInt(multiple_of=10)    # With constraints

# Specialized constraint types
PositiveInteger()           # > 0
NegativeInteger()           # < 0
NonNegativeInteger()        # >= 0
NonPositiveInteger()        # <= 0

# Full constraint options
Integer(
    min_value=10,          # Minimum allowed value
    max_value=100,         # Maximum allowed value
    multiple_of=5,         # Must be divisible by this
    positive=True,         # Shortcut for min_value=1
    negative=True,         # Shortcut for max_value=-1
)
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-db-types.git
cd python-db-types
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Set up pre-commit hooks:
```bash
poetry run pre-commit install
```

5. Run tests:
```bash
make test
```

### Development Commands

- `make lint` - Run linting (ruff + pyright)
- `make format` - Format code (black + isort + ruff fix)
- `make test` - Run tests
- `make test-cov` - Run tests with coverage
- `make check-all` - Run all checks (lint + format check + tests)
- `make check-consistency` - Verify pre-commit, Makefile, and CI are in sync

### Ensuring Consistency

To ensure your development environment matches CI/CD:

```bash
# Check that pre-commit hooks match Makefile and GitHub Actions
make check-consistency
```

This will verify that all tools (black, isort, ruff, pyright) are configured consistently across:
- Pre-commit hooks (`.pre-commit-config.yaml`)
- Makefile commands
- GitHub Actions workflows

## License

MIT
