# mocksmith

[![Unit Tests](https://github.com/gurmeetsaran/mocksmith/actions/workflows/ci.yml/badge.svg)](https://github.com/gurmeetsaran/mocksmith/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/gurmeetsaran/mocksmith/branch/main/graph/badge.svg)](https://codecov.io/gh/gurmeetsaran/mocksmith)
[![PyPI version](https://badge.fury.io/py/mocksmith.svg)](https://badge.fury.io/py/mocksmith)
[![Python Versions](https://img.shields.io/pypi/pyversions/mocksmith.svg)](https://pypi.org/project/mocksmith/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Type-safe data validation with automatic mock generation for Python dataclasses and Pydantic models. Build robust data models with database-aware validation and generate realistic test data with a single decorator.

## Features

- **Type-safe database columns**: Define database columns with proper validation
- **Serialization/Deserialization**: Automatic conversion between Python and SQL types
- **Dataclass Integration**: Full support for Python dataclasses with validation
- **Pydantic Integration**: First-class Pydantic support with automatic validation
- **Clean API**: Simple, intuitive interface for both Pydantic AND dataclasses - just `name: Varchar(50)`
- **Comprehensive Types**: STRING (VARCHAR, CHAR, TEXT), NUMERIC (INTEGER, DECIMAL, FLOAT), TEMPORAL (DATE, TIME, TIMESTAMP), and more
- **Mock Data Generation**: Built-in mock/fake data generation for testing with `@mockable` decorator

## Why mocksmith?

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

### After (With mocksmith)
```python
from pydantic import BaseModel
from mocksmith import Varchar, Money, Boolean

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
pip install mocksmith
```

For Pydantic support:
```bash
pip install "mocksmith[pydantic]"
```

For mock data generation:
```bash
pip install "mocksmith[mock]"
```

## Import Structure

The library organizes types into two categories:

### Core Database Types
Core database types are available directly from the main package:

```python
from mocksmith import (
    # String types
    VARCHAR, CHAR, TEXT, Varchar, Char, Text,
    # Numeric types
    INTEGER, DECIMAL, FLOAT, Integer, DecimalType, Float,
    # Temporal types
    DATE, TIME, TIMESTAMP, Date, Time, Timestamp,
    # Other types
    BOOLEAN, BINARY, Boolean, Binary
)
```

### Specialized Types
Specialized types for common use cases are available from the `specialized` submodule:

```python
from mocksmith.specialized import (
    # Geographic types
    CountryCode,  # ISO 3166-1 alpha-2 country codes
    City,         # City names
    State,        # State/province names
    ZipCode,      # Postal codes

    # Contact types
    Email,        # Email addresses with validation
    PhoneNumber,  # Phone numbers

    # Web types
    URL,          # URLs with validation
    IPAddress,    # IPv4 or IPv6 addresses
    IPv4Address,  # IPv4 addresses only
    IPv6Address,  # IPv6 addresses only
)
```

This separation keeps the main namespace clean and makes it clear which types are fundamental database types versus application-specific types.

## Quick Start

### Clean Interface (Works with both Pydantic and Dataclasses!) ✨

```python
from pydantic import BaseModel
from mocksmith import Varchar, Integer, Boolean, Money

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
- [`examples/pydantic_mock_example.py`](examples/pydantic_mock_example.py) - Mock data generation with Pydantic models
- [`examples/dataclass_mock_example.py`](examples/dataclass_mock_example.py) - Mock data generation with dataclasses

### Common Use Cases

**E-commerce Product Model:**

```python
from pydantic import BaseModel
from mocksmith import Varchar, Text, Money, Boolean, Timestamp

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
from mocksmith import Integer, PositiveInteger, NonNegativeInteger

class UserAccount(BaseModel):
    user_id: PositiveInteger()
    age: Integer(min_value=13, max_value=120)
    balance_cents: NonNegativeInteger()
```

See complete working examples:
- [`examples/`](examples/) - All example files with detailed documentation
- [`examples/pydantic_example.py`](examples/pydantic_example.py) - All features including constraints
- [`examples/dataclass_example.py`](examples/dataclass_example.py) - All features including constraints

## Mock Data Generation

Generate realistic test data automatically with the `@mockable` decorator:

```python
from dataclasses import dataclass
from mocksmith import Varchar, Integer, Date, mockable
from mocksmith.specialized import Email, CountryCode

@mockable
@dataclass
class User:
    id: Integer()
    username: Varchar(50)
    email: Email
    country: CountryCode
    birth_date: Date()

# Generate mock instances
user = User.mock()
print(user.username)  # "Christina Wells"
print(user.email)     # "michael23@example.com"
print(user.country)   # "US"

# With overrides
user = User.mock(username="test_user", country="GB")

# Using builder pattern
user = (User.mock_builder()
        .with_username("john_doe")
        .with_country("CA")
        .build())
```

The same `@mockable` decorator works with Pydantic models! Mock generation:
- Respects all field constraints (length, format, etc.)
- Generates appropriate data based on field names (e.g., 'email' generates valid emails)
- Supports specialized types with realistic data
- Works with both dataclasses and Pydantic models
- Automatically handles Python Enum types with random value selection

See mock examples:
- [`examples/dataclass_mock_example.py`](examples/dataclass_mock_example.py) - Complete mock examples with dataclasses
- [`examples/pydantic_mock_example.py`](examples/pydantic_mock_example.py) - Complete mock examples with Pydantic
- [`examples/enum_mock_example.py`](examples/enum_mock_example.py) - Enum support in mock generation
- [`examples/ip_address_example.py`](examples/ip_address_example.py) - IP address validation and generation

## Clean Annotation Interface

The library provides a clean, Pythonic interface for defining database types that works with both Pydantic and dataclasses:

```python
# Works with Pydantic
from pydantic import BaseModel
from mocksmith import Varchar, Integer, Money, Date, Boolean, Text

class Product(BaseModel):
    sku: Varchar(20)
    name: Varchar(100)
    description: Text()
    price: Money()  # Alias for Decimal(19, 4)
    in_stock: Boolean()

# Also works with dataclasses!
from dataclasses import dataclass
from mocksmith.dataclass_integration import validate_dataclass

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
# from mocksmith.types.string import VARCHAR
# from mocksmith.types.numeric import DECIMAL
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
from mocksmith import Varchar, Integer, Text

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
from mocksmith import Money, Boolean, Date, Timestamp

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
from mocksmith import Varchar, Integer, Money

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
from mocksmith import Varchar, Money, Timestamp

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

- [`dataclass_mock_example.py`](examples/dataclass_mock_example.py) - Mock data generation examples:
  - Using `@mockable` decorator with dataclasses
  - Generating mock instances with `.mock()`
  - Override specific fields
  - Type-safe builder pattern
  - Specialized types (Email, CountryCode, etc.)

- [`pydantic_mock_example.py`](examples/pydantic_mock_example.py) - Mock data generation with Pydantic:
  - Using `@mockable` decorator with Pydantic models
  - Same mock API as dataclasses
  - Automatic validation of generated data
  - Specialized types with DBTypeValidator
  - Model configuration and validation on assignment
  - TINYINT and REAL type usage
  - Boolean type conversions

### Example: E-commerce Order System

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from mocksmith import Varchar, Integer, Date, DecimalType, Text, BigInt, Timestamp
from mocksmith.dataclass_integration import validate_dataclass

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
from mocksmith import Integer, PositiveInteger, NonNegativeInteger

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
git clone https://github.com/gurmeetsaran/mocksmith.git
cd mocksmith
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
