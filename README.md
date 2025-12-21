# mocksmith

[![Unit Tests](https://github.com/gurmeetsaran/mocksmith/actions/workflows/ci.yml/badge.svg)](https://github.com/gurmeetsaran/mocksmith/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/gurmeetsaran/mocksmith/branch/main/graph/badge.svg)](https://codecov.io/gh/gurmeetsaran/mocksmith)
[![PyPI version](https://badge.fury.io/py/mocksmith.svg)](https://badge.fury.io/py/mocksmith)
[![Python Versions](https://img.shields.io/pypi/pyversions/mocksmith.svg)](https://pypi.org/project/mocksmith/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Type-safe data validation with automatic mock generation for Python dataclasses and Pydantic models. Build robust data models with database-aware validation and generate realistic test data with a single decorator.

## Features

- **Type-safe database columns**: Define database columns with proper validation
- **SQL-compliant validation**: All numeric types strictly enforce SQL bounds (TINYINT: -128 to 127, etc.)
- **Instantiation validation**: Types validate at creation time, preventing invalid data from being created
- **Serialization/Deserialization**: Automatic conversion between Python and SQL types
- **Dataclass Integration**: Full support for Python dataclasses with validation
- **Pydantic Integration**: First-class Pydantic support with automatic validation
- **Clean API**: Simple, intuitive interface for both Pydantic AND dataclasses - just `name: Varchar(50)`
- **Comprehensive Types**: STRING (VARCHAR, CHAR, TEXT), NUMERIC (INTEGER, DECIMAL, FLOAT), TEMPORAL (DATE, TIME, TIMESTAMP), and more
- **Mock Data Generation**: Built-in mock/fake data generation that respects all SQL bounds and constraints
- **Constrained Types**: Support for min/max constraints on numeric types - `price: PositiveMoney()`, `age: Integer(ge=0, le=120)`

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
    price: Money()             # Decimal(19,4) - use PositiveMoney() for price > 0
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
# Standard installation (includes mock generation)
pip install mocksmith

# With Pydantic validation support (recommended)
pip install "mocksmith[pydantic]"
```

**Requirements:**
- Python 3.8+ (Python 3.10+ recommended for pipe union syntax support)
- Faker (included in standard installation)
- Pydantic 2.0+ (optional, for enhanced validation)

The standard installation includes Faker for mock data generation and custom validation logic. Adding Pydantic provides better performance and integration with Pydantic types.

## Import Structure

The library organizes types into two categories:

### Core Database Types
Core database types are available through factory functions from the main package:

```python
from mocksmith import (
    # String types - Factory functions only
    Varchar, Char, Text,
    # Numeric types - Factory functions only
    Integer, DecimalType, Float,
    BigInt, SmallInt, TinyInt,
    Double, Real, Numeric,
    # Temporal types - Factory functions only
    Date, Time, DateTime, Timestamp,
    # Other types - Factory functions only
    Boolean, Binary, VarBinary, Blob,
    # Constrained types
    PositiveInteger, NonNegativeInteger, NegativeInteger, NonPositiveInteger,
    Money, PositiveMoney, NonNegativeMoney, ConstrainedMoney,
    ConstrainedDecimal, ConstrainedFloat
)
```

**⚠️ Breaking Change:** Direct class imports (VARCHAR, INTEGER, etc.) have been removed to prevent confusion. Use factory functions (Varchar, Integer, etc.) exclusively.

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
    PhoneNumber,  # Phone numbers
)
```

**Note**: For email and web types, use Pydantic's built-in types instead:
- Email → Use `pydantic.EmailStr`
- URL → Use `pydantic.HttpUrl` or `pydantic.AnyUrl`
- IP addresses → Use `pydantic.IPvAnyAddress`, `pydantic.IPv4Address`, or `pydantic.IPv6Address`

This separation keeps the main namespace clean and makes it clear which types are fundamental database types versus application-specific types.

## Quick Start

### Clean Interface (Works with both Pydantic and Dataclasses!) ✨

```python
from pydantic import BaseModel
from mocksmith import Varchar, Integer, Boolean, Money

class User(BaseModel):
    id: Integer()
    username: Varchar(50)  # Creates a type class with length 50
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
- [`examples/constrained_types_example.py`](examples/constrained_types_example.py) - Constrained types with validation and mock generation

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
    age: Integer(ge=13, le=120)
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
from mocksmith.specialized import PhoneNumber, CountryCode

@mockable
@dataclass
class Address:
    street: Varchar(100)
    city: Varchar(50)
    zip_code: Integer(ge=10000, le=99999)

@mockable
@dataclass
class User:
    id: Integer()
    username: Varchar(50)
    phone: PhoneNumber()
    country: CountryCode()
    birth_date: Date()
    address: Address  # Nested dataclass!

# Generate mock instances
user = User.mock()
print(user.username)  # "Christina Wells"
print(user.phone)     # "(555) 123-4567"
print(user.country)   # "US"
print(user.address.city)  # "New York"  # Nested fields are mocked too!

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
- Generates appropriate mock data for each type
- Supports specialized types with realistic data
- Works with both dataclasses and Pydantic models
- Automatically handles Python Enum types with random value selection
- Supports nested dataclasses - automatically generates mock data for nested structures
- **Python 3.10+ pipe syntax support** - `field: Type() | None` works seamlessly with mocking

### Optional Fields with Pipe Syntax (Python 3.10+)

MockSmith fully supports Python 3.10+ pipe union syntax for optional fields:

```python
from mocksmith import Varchar, Integer, BigInt, DateTime, Timestamp, mockable
from pydantic import BaseModel

@mockable
class User(BaseModel):
    # Required fields
    username: Varchar(50)

    # Optional fields using pipe syntax - both work identically!
    email: Varchar(100) | None          # With Annotated
    user_id: BigInt() | None            # Simple type
    age: Integer(ge=0, le=120) | None   # With constraints
    created_at: DateTime() | None       # Temporal type
    last_login: Timestamp() | None      # With timezone

# Mock generation handles optional fields automatically
user = User.mock()
# Optional fields will randomly be None or have valid values (~20% None, ~80% value)
print(user.user_id)     # Could be: 7786676712978416482 or None
print(user.last_login)  # Could be: 2021-05-04 02:28:37+00:00 or None
```

**Note:** Both `Optional[Type()]` and `Type() | None` syntaxes work identically. Choose based on your Python version and style preference.

See mock examples:
- [`examples/dataclass_mock_example.py`](examples/dataclass_mock_example.py) - Complete mock examples with dataclasses including enum support
- [`examples/pydantic_mock_example.py`](examples/pydantic_mock_example.py) - Complete mock examples with Pydantic including enum support and built-in types
- [`examples/pipe_syntax_example.py`](examples/pipe_syntax_example.py) - Python 3.10+ pipe syntax examples with optional fields

## Type Usage Patterns

**Important:** MockSmith uses factory functions exclusively. The old pattern of importing classes directly (VARCHAR, INTEGER, etc.) is no longer supported.

### Correct Pattern

```python
from mocksmith import Varchar, Integer, Boolean  # Factory functions

# Factory functions create type classes for use in annotations
UsernameType = Varchar(30, min_length=3)  # Returns a type class

class User(BaseModel):
    username: UsernameType  # Use the type class
    # Or inline:
    email: Varchar(100, to_lower=True)  # Factory function inline
    age: Integer(gt=0, le=120)
    active: Boolean()
```

### What Changed from V2

```python
# ❌ OLD PATTERN (NO LONGER WORKS - REMOVED)
from mocksmith import VARCHAR  # This import fails now
varchar_type = VARCHAR(30)  # Would create instance "30" - WRONG!

# ✅ NEW PATTERN (THE ONLY WAY)
from mocksmith import Varchar  # Factory function
UsernameType = Varchar(30)  # Creates type class - CORRECT!
```

### With Pydantic (Full Validation)

```python
from typing import Optional
from pydantic import BaseModel
from mocksmith import Integer, Varchar, Money, Boolean, PositiveInteger, NonNegativeInteger
from decimal import Decimal

# Pattern 1: Direct usage (Recommended - cleanest syntax)
class Product(BaseModel):
    id: Integer()
    name: Varchar(100)
    price: Money()
    in_stock: Boolean() = True

# Pattern 2: With constraints
class ConstrainedModel(BaseModel):
    age: Integer(ge=0, le=120)  # Age between 0-120
    quantity: Integer(gt=0)      # Positive quantity
    discount: Integer(ge=0, le=100, multiple_of=5)  # 0-100%, multiples of 5

# Pattern 3: Factory functions with constraints
class ConstrainedProduct(BaseModel):
    sku: Varchar(20, to_upper=True)  # Auto uppercase
    name: Varchar(100, min_length=3)
    price: DecimalType(10, 2, gt=0)  # precision=10, scale=2, >0

# Pattern 4: Constrained types (common patterns)
class UserAccount(BaseModel):
    user_id: PositiveInteger()       # > 0
    balance: NonNegativeInteger()    # >= 0

# Pattern 5: Optional fields
class OptionalModel(BaseModel):
    required_field: Varchar(50)
    optional_field: Optional[Varchar(50)] = None  # Can be None (traditional syntax)
    optional_new: Varchar(50) | None = None       # Can be None (Python 3.10+ pipe syntax)
    with_default: Boolean() = True                # Has default value

# All patterns can be mixed in the same model!
```

### With Dataclasses (Type Hints Only, No Validation)

```python
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from mocksmith import Integer, Varchar, Money, Text

@dataclass
class Product:
    # Same syntax works, but NO validation occurs!
    id: Integer()
    name: Varchar(100)
    price: Money() = Decimal("0.00")
    optional_field: Optional[Text()] = None

# WARNING: Dataclasses don't validate!
product = Product(
    id=999999999999,    # Accepts invalid values!
    name="x" * 1000,    # No length check!
    price="invalid"     # No type check!
)
```

### Important Notes

✅ **DO USE:**
- `field: Varchar(50)` - Factory functions for type creation
- `field: Integer(gt=0)` - Factory functions with constraints
- `field: Optional[Varchar(50)] = None` - For nullable fields (traditional syntax)
- `field: Varchar(50) | None` - For nullable fields (Python 3.10+ pipe syntax)
- Pydantic `BaseModel` when you need validation
- Constrained types like `PositiveInteger()` for common patterns

❌ **DON'T USE (Removed):**
- `from mocksmith import VARCHAR` - Direct class imports removed
- `VARCHAR(30)` - Would create instance "30", not a type!
- Plain dataclasses if you need validation (use Pydantic instead)

### Type Validation Features

All numeric types enforce SQL bounds and validate at instantiation:
- **TinyInt**: -128 to 127 (8-bit)
- **SmallInt**: -32,768 to 32,767 (16-bit)
- **Integer**: -2,147,483,648 to 2,147,483,647 (32-bit)
- **BigInt**: -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 (64-bit)

Optional fields properly handle None values with both traditional and modern syntax:
```python
from typing import Optional

class User(BaseModel):
    name: Varchar(50)                        # Required
    nickname: Optional[Varchar(30)] = None   # Optional (traditional syntax)
    bio: Varchar(200) | None = None          # Optional (Python 3.10+ pipe syntax)

user = User(name="John", nickname=None, bio=None)  # ✓ Valid

# Both syntaxes work the same way - choose based on your Python version
# Python 3.10+ supports both, but pipe syntax is more concise
```

### Literal Type Support

MockSmith types work seamlessly with Python's `Literal` type for strict value constraints:

```python
from typing import Literal
from pydantic import BaseModel
from mocksmith import Varchar, Integer, mockable

@mockable
class ServerConfig(BaseModel):
    environment: Literal["dev", "staging", "prod"]
    status_code: Literal[200, 301, 404, 500]
    port: Integer(ge=1024, le=65535)
    log_level: Literal[0, 1, 2, 3, 4, 5]  # 0=OFF, 5=TRACE

# Validation enforces Literal constraints
config = ServerConfig(
    environment="prod",      # ✓ Valid
    status_code=200,        # ✓ Valid
    port=8080,              # ✓ Valid (within range)
    log_level=2             # ✓ Valid
)

# Mock generation respects Literal values
mock = ServerConfig.mock()
# mock.environment will be one of: "dev", "staging", "prod"
# mock.status_code will be one of: 200, 301, 404, 500
```

## Clean Annotation Interface

The library provides a clean, Pythonic interface for defining database types:

### Available Clean Types:

**String Types:**
- `Varchar(length)` → Variable-length string
- `Char(length)` → Fixed-length string
- `Text()` → Large text field
- `String` → Alias for Varchar

**Numeric Types:**
- `Integer()` → 32-bit integer (-2,147,483,648 to 2,147,483,647)
- `BigInt()` → 64-bit integer (-9,223,372,036,854,775,808 to 9,223,372,036,854,775,807)
- `SmallInt()` → 16-bit integer (-32,768 to 32,767)
- `TinyInt()` → 8-bit integer (-128 to 127)
- `DecimalType(precision, scale)` → Fixed-point decimal
- `Numeric(precision, scale)` → Alias for DecimalType
- `Money()` → Alias for Decimal(19, 4)
- `Float()` → Floating point (generates FLOAT SQL type)
- `Real()` → Floating point (generates REAL SQL type, typically single precision in SQL)
- `Double()` → Double precision

All numeric types:
- Enforce SQL bounds at instantiation (e.g., `TinyInt(200)` raises ValueError)
- Generate mock data within valid ranges (e.g., `TinyInt(gt=5)` generates 6-127, not > 127)
- Support constraints (gt, ge, lt, le, multiple_of)

**Constrained Numeric Types:**
- `PositiveInteger()` → Integer > 0
- `NegativeInteger()` → Integer < 0
- `NonNegativeInteger()` → Integer ≥ 0
- `NonPositiveInteger()` → Integer ≤ 0
- `ConstrainedInteger(ge=x, le=y, multiple_of=z)` → Custom constraints
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

### Pydantic Built-in Types Support

Mocksmith now supports automatic mock generation for Pydantic's built-in types:

```python
from pydantic import BaseModel, EmailStr, HttpUrl, IPvAnyAddress, conint, constr
from mocksmith import mockable

@mockable
class ServerConfig(BaseModel):
    hostname: constr(min_length=1, max_length=253)
    ip_address: IPvAnyAddress
    port: conint(ge=1, le=65535)
    api_url: HttpUrl
    admin_email: EmailStr

# Generate mock with Pydantic types
config = ServerConfig.mock()
print(config.ip_address)  # IPv4Address('192.168.1.100')
print(config.api_url)     # https://example.com
print(config.admin_email) # user@example.com
```

**Tip**: For types that have Pydantic equivalents, prefer using Pydantic's built-in types:
- Use `EmailStr` instead of `mocksmith.specialized.Email`
- Use `HttpUrl` or `AnyUrl` instead of `mocksmith.specialized.URL`
- Use `IPvAnyAddress`, `IPv4Address`, or `IPv6Address` for IP addresses

### Using Pydantic Types in Dataclasses

While Pydantic types can be used as type annotations in dataclasses, there are important limitations:

```python
from dataclasses import dataclass
from pydantic import EmailStr, HttpUrl, conint

@dataclass
class ServerConfig:
    hostname: str
    email: EmailStr  # Works as type hint only
    port: conint(ge=1, le=65535)  # No validation!

# This creates an instance WITHOUT validation
server = ServerConfig(
    hostname="api.example.com",
    email="invalid-email",  # Not validated!
    port=99999  # Out of range but accepted!
)
```

**Key Points**:
- Pydantic types in dataclasses serve as type hints only
- No automatic validation occurs
- Mock generation works but produces regular Python types (str, int, etc.)
- For validation, use Pydantic's BaseModel instead

See the Pydantic types limitations section in [`examples/dataclass_example.py`](examples/dataclass_example.py) for a complete comparison.

### Supported Pydantic Types for Mock Generation

The `@mockable` decorator supports automatic mock generation for the following Pydantic types:

#### Network Types
- `HttpUrl` - Generates valid HTTP/HTTPS URLs
- `AnyHttpUrl` - Generates any HTTP scheme URLs
- `EmailStr` - Generates valid email addresses
- `IPvAnyAddress` - Generates IPv4 or IPv6 addresses (80% IPv4, 20% IPv6)
- `IPvAnyInterface` - Generates IP addresses with CIDR notation
- `IPvAnyNetwork` - Generates IP network addresses

#### Numeric Types
- `PositiveInt` - Integers > 0
- `NegativeInt` - Integers < 0
- `NonNegativeInt` - Integers >= 0
- `NonPositiveInt` - Integers <= 0
- `PositiveFloat` - Floats > 0
- `NegativeFloat` - Floats < 0
- `NonNegativeFloat` - Floats >= 0
- `NonPositiveFloat` - Floats <= 0

#### String/Identifier Types
- `UUID1`, `UUID3`, `UUID4`, `UUID5` - Generates UUIDs (currently all as UUID4)
- `SecretStr` - Generates password-like strings
- `Json` - Generates valid JSON strings

#### Date/Time Types
- `FutureDate` - Generates dates in the future
- `PastDate` - Generates dates in the past
- `FutureDatetime` - Generates datetimes in the future
- `PastDatetime` - Generates datetimes in the past

#### Constraint Types
- `conint(ge=1, le=100)` - Integers with min/max constraints
- `confloat(ge=0.0, le=1.0)` - Floats with min/max constraints
- `constr(min_length=1, max_length=50)` - Strings with length constraints
- `constr(pattern=r"^[A-Z]{3}[0-9]{3}$")` - Strings matching regex patterns (limited support)
- `conlist(item_type, min_length=1, max_length=10)` - Lists with constraints

#### Example Usage

```python
from pydantic import BaseModel, EmailStr, HttpUrl, conint, PositiveInt
from mocksmith import mockable

@mockable
class UserProfile(BaseModel):
    user_id: PositiveInt
    email: EmailStr
    website: HttpUrl
    age: conint(ge=18, le=120)

# Generate mock data
user = UserProfile.mock()
print(user.email)     # "john.doe@example.com"
print(user.website)   # "https://example.com"
print(user.age)       # 42 (between 18-120)
```

**Note**: When using Pydantic types in dataclasses (not BaseModel), the types work as annotations only without validation. The mock generation still works but produces regular Python types.

### Handling Unsupported Types

When `@mockable` encounters an unsupported type, it attempts to handle it intelligently:

1. **Common types** (Path, Set, FrozenSet) - Now supported with appropriate mock values
2. **Auto-instantiable types** - Tries to create instances with `()`, `None`, `""`, or `0`
3. **Truly unsupported types** - Returns `None` with a warning to help identify gaps in type support

#### Newly Supported Types
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Set, FrozenSet
from mocksmith import mockable

@mockable
@dataclass
class Config:
    config_path: Path        # ✓ Generates Path('/tmp/mock_file.txt')
    data_dir: Path          # ✓ Smart naming: Path('/tmp/mock_directory')
    tags: Set[str]          # ✓ Generates {'tag1', 'tag2', ...}
    frozen_tags: FrozenSet[int]  # ✓ Generates frozenset({1, 2, 3})

config = Config.mock()
# All fields get appropriate mock values!
```

#### Warning System
```python
class CustomType:
    def __init__(self, required_arg):
        # Cannot be auto-instantiated
        pass

@mockable
@dataclass
class Example:
    name: str                              # ✓ Supported
    custom_required: CustomType            # ⚠️ Warning issued, returns None
    custom_optional: Optional[CustomType] = None  # ⚠️ Warning issued (if attempted), returns None

# Console output:
# UserWarning: mocksmith: Unsupported type 'CustomType' for field 'custom_required'.
# Returning None. Consider making this field Optional or providing a mock override.
```

**Important Notes**:
- **All unsupported types trigger warnings** - This helps identify gaps in mocksmith's type support
- **Warnings help improve mocksmith** - If you encounter warnings, please file an issue on GitHub
- **Optional fields** - May show warnings ~80% of the time (when generation is attempted)
- **Override unsupported types** - Use `mock()` with overrides: `Example.mock(custom_required=CustomType('value'))`
- **Pydantic models** - Make unsupported fields `Optional` to avoid validation errors

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
    created_at: Timestamp(with_timezone=False)

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

- [`constrained_types_example.py`](examples/constrained_types_example.py) - Constrained types with validation:
  - PositiveMoney, NonNegativeMoney, ConstrainedMoney usage
  - ConstrainedDecimal with precision and range constraints
  - ConstrainedFloat for percentages and probabilities
  - Mock generation respecting all constraints
  - Validation examples showing error handling
  - Builder pattern with constrained types

### Example: E-commerce Order System

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from mocksmith import Varchar, Integer, Date, DecimalType, Text, BigInt, Timestamp
@dataclass
class Customer:
    customer_id: Integer()
    first_name: Varchar(50)
    last_name: Varchar(50)
    email: Varchar(100)
    phone: Optional[Varchar(20)]
    date_of_birth: Optional[Date()]

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

### Validation in Dataclasses

Plain dataclasses don't provide validation for mocksmith types. For validation, use Pydantic BaseModel:

```python
from pydantic import BaseModel
from mocksmith import SmallInt

class Config(BaseModel):  # Use BaseModel for validation
    hour: SmallInt(ge=0, le=23)

# Validation happens automatically
try:
    config = Config(hour=24)  # Raises ValidationError
except ValidationError as e:
    print(f"Validation error: {e}")

config = Config(hour=12)  # Works fine
```

## Advanced Features

### Custom Validation with Pydantic

```python
from pydantic import BaseModel

class CustomProduct(BaseModel):
    sku: Varchar(20)  # Required field
    name: Varchar(100)  # Required field
    description: Optional[Varchar(500)] = None  # Optional field
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

**Important:** All numeric types in mocksmith strictly enforce SQL bounds and validate at instantiation time. For example, `TinyInt` enforces the TINYINT range of -128 to 127, preventing invalid data from being created or generated.

The library provides specialized numeric types with built-in constraints for common validation scenarios:

```python
from mocksmith import Integer, PositiveInteger, NonNegativeInteger

# Enhanced Integer functions - no constraints = standard type
id: Integer()                    # Standard 32-bit integer
quantity: Integer(ge=0)   # With constraints (same as NonNegativeInteger)
discount: Integer(ge=0, le=100)  # Percentage 0-100
price: Integer(gt=0)    # Same as PositiveInteger()

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
Integer(ge=0)        # With constraints
Integer(gt=0)      # Shortcut for > 0
BigInt()                    # Standard 64-bit integer
BigInt(ge=0, le=1000000)  # With constraints
SmallInt()                  # Standard 16-bit integer
SmallInt(multiple_of=10)    # With constraints

# Specialized constraint types
PositiveInteger()           # > 0
NegativeInteger()           # < 0
NonNegativeInteger()        # >= 0
NonPositiveInteger()        # <= 0

# Full constraint options
Integer(
    gt=10,             # Value must be greater than 10
    ge=10,             # Value must be greater than or equal to 10
    lt=100,            # Value must be less than 100
    le=100,            # Value must be less than or equal to 100
    multiple_of=5,     # Must be divisible by this
)
```

### Constrained Money and Decimal Types

mocksmith provides constrained versions of Money and Decimal types using Pydantic's constraint system:

```python
from mocksmith import (
    ConstrainedMoney, PositiveMoney, NonNegativeMoney,
    ConstrainedDecimal, ConstrainedFloat
)

# Money with constraints
price: PositiveMoney()                          # > 0
balance: NonNegativeMoney()                     # >= 0
discount: ConstrainedMoney(ge=0, le=100)        # 0-100 range
payment: ConstrainedMoney(gt=0, le=10000)       # 0 < payment <= 10000

# Decimal with precision and constraints
weight: ConstrainedDecimal(10, 2, gt=0)         # Positive weight, max 10 digits, 2 decimal places
temperature: ConstrainedDecimal(5, 2, ge=-273.15)  # Above absolute zero

# Float with constraints
percentage: ConstrainedFloat(ge=0.0, le=1.0)    # 0-1 range
rate: ConstrainedFloat(gt=0, lt=0.5)            # 0 < rate < 0.5
```

These constrained types:
- Work seamlessly with Pydantic validation
- Generate appropriate mock data respecting constraints
- Provide the same clean API as other mocksmith types
- Fall back gracefully if Pydantic is not available

**Example Usage:**

```python
from pydantic import BaseModel
from mocksmith import mockable, PositiveMoney, NonNegativeMoney, ConstrainedMoney, ConstrainedFloat

@mockable
class Order(BaseModel):
    subtotal: PositiveMoney()                    # Must be > 0
    discount: ConstrainedMoney(ge=0, le=50)      # 0-50 range
    tax: NonNegativeMoney()                      # >= 0
    discount_rate: ConstrainedFloat(ge=0, le=0.3)  # 0-30%

# Validation works
order = Order(
    subtotal="100.00",    # ✓ Converts to Decimal
    discount="25.00",     # ✓ Within 0-50 range
    tax="8.50",          # ✓ Non-negative
    discount_rate=0.15   # ✓ 15% is within 0-30%
)

# Mock generation respects constraints
mock_order = Order.mock()
assert mock_order.subtotal > 0
assert 0 <= mock_order.discount <= 50
assert mock_order.tax >= 0
assert 0 <= mock_order.discount_rate <= 0.3
```

## Migration Guide

### Breaking Changes

This version introduces critical breaking changes to simplify the architecture:

1. **Direct class imports are removed** - `from mocksmith import VARCHAR` no longer works
2. **Only factory functions are available** - Use `Varchar()`, not `VARCHAR()`
3. **DBTypeValidator is removed** - Types work directly with Pydantic
4. **DBType base class is removed** - V3 pattern is now the only supported approach
   - All types now inherit from native Python types (str, int, Decimal, etc.)
   - Mock factory uses duck typing - any object with a `.mock()` method works as a mock provider
   - If you subclassed `DBType`, migrate to V3 pattern (inherit from native types, implement `__get_pydantic_core_schema__`)

### Why This Change?

In previous versions, importing and using `VARCHAR(30)` would create a type class. In the new simplified pattern, this would create a string instance with value "30" - highly confusing! To prevent this dangerous ambiguity, direct class access has been removed entirely.

### Migration Steps

```python
# ❌ OLD V2 CODE (No longer works)
from mocksmith import VARCHAR, INTEGER, BOOLEAN
from mocksmith.pydantic_integration import DBTypeValidator
from typing import Annotated

class User(BaseModel):
    username: Annotated[str, DBTypeValidator(VARCHAR(30))]
    age: Annotated[int, DBTypeValidator(INTEGER())]
    active: Annotated[bool, DBTypeValidator(BOOLEAN())]

# ✅ NEW CODE (Clean and simple)
from mocksmith import Varchar, Integer, Boolean

class User(BaseModel):
    username: Varchar(30)  # Direct usage!
    age: Integer()
    active: Boolean()
```

### Common Migration Patterns

| Old Pattern | New Pattern |
|----------------|----------------|
| `from mocksmith import VARCHAR` | `from mocksmith import Varchar` |
| `from mocksmith.types.string import VARCHAR` | Not available - use factory functions |
| `Annotated[str, DBTypeValidator(VARCHAR(30))]` | `Varchar(30)` |
| `VARCHAR(30)` (creates type) | `Varchar(30)` (creates type) |
| `INTEGER()` | `Integer()` |
| `DECIMAL(10, 2)` | `DecimalType(10, 2)` |
| `BOOLEAN()` | `Boolean()` |
| `DATE()` | `Date()` |
| `TIMESTAMP()` | `Timestamp()` |

### Benefits

1. **Cleaner API** - No more `DBTypeValidator` or `Annotated` boilerplate
2. **Type safety** - Factory functions always return type classes
3. **No confusion** - Can't accidentally create instances when you mean types
4. **Better IDE support** - Direct type usage improves autocomplete
5. **Simpler codebase** - V3 pattern only, duck typing for extensibility
6. **More Pythonic** - Any object with a `.mock()` method can provide mocks (no inheritance required)

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
