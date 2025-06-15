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
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date
from db_types import Varchar, Integer, Date, Boolean, Money, Text, Timestamp

class User(BaseModel):
    # Required fields
    id: Integer()
    username: Varchar(30)
    email: Varchar(255)

    # Optional fields (use Optional[...])
    bio: Optional[Text(max_length=1000)] = None
    phone: Optional[Varchar(20)] = None

    # Fields with defaults
    is_active: Boolean() = True
    balance: Money() = Decimal("0.00")
    joined_date: Date() = Field(default_factory=date.today)
    last_login: Optional[Timestamp()] = None

# Automatic validation and type conversion
user = User(
    id=1,
    username="john_doe",
    email="john@example.com",
    bio="Python developer",
    is_active="yes",  # Converts to True
    balance="1234.56",  # Converts to Decimal
    joined_date="2023-01-15",  # Converts to date
    last_login="2023-12-15T10:30:00Z"  # Converts to datetime
)

print(user.balance)  # Decimal('1234.56')
print(type(user.balance))  # <class 'decimal.Decimal'>
print(user.is_active)  # True

# Validation example
try:
    invalid_user = User(
        id=1,
        username="x" * 31,  # Too long! Exceeds Varchar(30)
        email="test@example.com",
        bio="Test",
        is_active=True,
        balance="99.99",
        joined_date="2023-01-01",
        last_login="2023-01-01T00:00:00Z"
    )
except Exception as e:
    print(f"Validation error: {e}")
```

### With Dataclasses (Same Clean Syntax!)

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from db_types import Varchar, Integer, Date, Boolean, Money, Text
from db_types.dataclass_integration import validate_dataclass

@validate_dataclass
@dataclass
class User:
    # Required fields
    id: Integer()
    username: Varchar(50)
    email: Varchar(100)

    # Optional fields
    bio: Optional[Text()] = None
    age: Optional[Integer()] = None

    # Fields with defaults
    active: Boolean() = True
    balance: Money() = Decimal("0.00")
    joined_date: Date() = date.today()

# Create a user - validation happens automatically
user = User(
    id=1,
    username="john_doe",
    email="john@example.com",
    bio="Python developer",
    age=30,
    active="yes",  # Automatic conversion to True
    balance="1250.50",  # Automatic conversion to Decimal
    joined_date="2023-01-15"  # Automatic conversion to date
)

print(user.active)  # True
print(type(user.balance))  # <class 'decimal.Decimal'>

# This will raise ValueError
try:
    invalid_user = User(
        id=1,
        username="x" * 51,  # Too long! VARCHAR(50) limit exceeded
        email="test@example.com"
    )
except ValueError as e:
    print(f"Validation error: {e}")
    # Output: Validation error: String length 51 exceeds maximum 50

# Convert to SQL-compatible dictionary
sql_data = user.to_sql_dict()
print(sql_data)
# Output: {'id': 1, 'username': 'john_doe', 'email': 'john@example.com',
#          'bio': 'Python developer', 'age': 30, 'active': True,
#          'balance': '1250.50', 'joined_date': '2023-01-15'}
```

### Pydantic Model Examples

```python
from pydantic import BaseModel, Field
from typing import Optional
from db_types import Varchar, Money, Boolean, Timestamp, Text, Integer

# E-commerce Product Model
class Product(BaseModel):
    sku: Varchar(20)
    name: Varchar(100)
    description: Text()
    price: Money()
    cost: Optional[Money()] = None
    in_stock: Boolean() = True
    created_at: Timestamp() = Field(default_factory=datetime.now)

    @property
    def profit_margin(self) -> Optional[Decimal]:
        if self.cost and self.price:
            return (self.price - self.cost) / self.price * 100
        return None

# Create product with validation
product = Product(
    sku="LAPTOP-001",
    name="Business Laptop",
    description="High-performance laptop",
    price="1299.99",  # Automatically converts to Decimal
    cost="850.00"
)

print(f"Profit margin: {product.profit_margin:.2f}%")  # 34.62%

# User Account Model with defaults
class UserAccount(BaseModel):
    user_id: Integer()
    email: Varchar(255)
    username: Varchar(30)
    is_active: Boolean() = True
    is_verified: Boolean() = False
    balance: Money() = Decimal("0.00")
    created_at: Timestamp() = Field(default_factory=datetime.now)

    class Config:
        # JSON serialization settings
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
```

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
- `DecimalType(precision, scale)` → Fixed-point decimal
- `Money()` → Alias for Decimal(19, 4)
- `Float()` → Floating point
- `Double()` → Double precision

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

### Example 1: E-commerce Order System

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
# Output: {
#     'order_id': 1001,
#     'customer_id': 1,
#     'order_date': '2023-12-15T14:30:00',
#     'total_amount': '299.99',
#     'status': 'pending',
#     'notes': 'Rush delivery requested'
# }
```

### Example 2: Financial Transaction System

```python
from dataclasses import dataclass
from typing import Annotated
from datetime import datetime
from decimal import Decimal

from db_types import *
from db_types.dataclass_integration import validate_dataclass

@validate_dataclass
@dataclass
class Account:
    account_number: Annotated[str, CHAR(10)]  # Fixed-length account number
    balance: Annotated[Decimal, DECIMAL(15, 2)]  # Up to 15 digits, 2 decimal places
    currency: Annotated[str, CHAR(3)]  # ISO currency code
    is_active: Annotated[bool, BOOLEAN()]

@validate_dataclass
@dataclass
class Transaction:
    transaction_id: Annotated[int, BIGINT()]
    from_account: Annotated[str, CHAR(10)]
    to_account: Annotated[str, CHAR(10)]
    amount: Annotated[Decimal, DECIMAL(15, 2)]
    timestamp: Annotated[datetime, TIMESTAMP(precision=3)]  # Millisecond precision
    description: Annotated[str, VARCHAR(200)]

# Example usage
account = Account(
    account_number="ACC1234567",  # Will be padded to 10 chars
    balance=Decimal("10000.50"),
    currency="USD",
    is_active=True
)

transaction = Transaction(
    transaction_id=789456123,
    from_account="ACC1234567",
    to_account="ACC9876543",
    amount=Decimal("500.00"),
    timestamp=datetime(2023, 12, 15, 10, 30, 45, 123000),
    description="Monthly rent payment"
)

# Validate specific constraints
try:
    invalid_transaction = Transaction(
        transaction_id=1,
        from_account="SHORT",  # Will be padded to 10 chars
        to_account="ACC9876543",
        amount=Decimal("1234567890123.99"),  # Exceeds DECIMAL(15,2)
        timestamp=datetime.now(),
        description="Test"
    )
except ValueError as e:
    print(f"Validation failed: {e}")
```

### Example 3: User Authentication System

```python
from dataclasses import dataclass
from typing import Annotated, Optional
from datetime import datetime
import hashlib

from db_types import *
from db_types.dataclass_integration import validate_dataclass

@validate_dataclass
@dataclass
class UserAuth:
    user_id: Annotated[int, INTEGER()]
    username: Annotated[str, VARCHAR(30)]
    email: Annotated[str, VARCHAR(255)]
    password_hash: Annotated[str, CHAR(64)]  # SHA-256 hash
    is_verified: Annotated[bool, BOOLEAN()]
    last_login: Annotated[Optional[datetime], TIMESTAMP()]
    failed_attempts: Annotated[int, SMALLINT()]
    metadata: Annotated[Optional[bytes], BLOB()]

def hash_password(password: str) -> str:
    """Create SHA-256 hash of password"""
    return hashlib.sha256(password.encode()).hexdigest()

# Create a new user
user = UserAuth(
    user_id=1,
    username="john_doe",
    email="john@example.com",
    password_hash=hash_password("secure_password123"),
    is_verified=True,
    last_login=datetime.now(),
    failed_attempts=0,
    metadata=b'{"preferences": "dark_mode"}'
)

# Test various boolean representations
user2 = UserAuth(
    user_id=2,
    username="jane_doe",
    email="jane@example.com",
    password_hash=hash_password("another_password"),
    is_verified="yes",  # Automatically converted to True
    last_login=None,
    failed_attempts=0,
    metadata=None
)

print(user2.is_verified)  # Output: True
```

### Example 4: Using with SQL Testing Library

```python
from dataclasses import dataclass
from typing import Annotated
from datetime import date
from decimal import Decimal

from db_types import *
from db_types.dataclass_integration import validate_dataclass

# Define your table schema
@validate_dataclass
@dataclass
class Employee:
    id: Annotated[int, INTEGER()]
    name: Annotated[str, VARCHAR(100)]
    department: Annotated[str, VARCHAR(50)]
    salary: Annotated[Decimal, DECIMAL(10, 2)]
    hire_date: Annotated[date, DATE()]
    is_active: Annotated[bool, BOOLEAN()]

# This can be used with sql-testing-library to create mock tables
employees = [
    Employee(1, "Alice Johnson", "Engineering", Decimal("95000.00"), date(2020, 1, 15), True),
    Employee(2, "Bob Smith", "Sales", Decimal("75000.00"), date(2021, 3, 20), True),
    Employee(3, "Charlie Brown", "HR", Decimal("65000.00"), date(2019, 11, 1), False),
]

# Convert to SQL-compatible format for insertion
sql_data = [emp.to_sql_dict() for emp in employees]
```

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

## Integration with SQL Testing Library

This library is designed to work seamlessly with `sql-testing-library` for creating mock database tables with proper type validation:

```python
# Your models with python-db-types ensure data integrity
# when used in SQL testing scenarios
from sql_testing_library import create_table

# The validation ensures your test data matches production constraints
create_table("employees", sql_data)  # Data is already validated!
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/python-db-types.git
cd python-db-types

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run specific test file
pytest tests/test_string_types.py -v

# Type checking
mypy src

# Linting
ruff check src tests

# Run the example
python examples/basic_usage.py
```

## License

MIT
