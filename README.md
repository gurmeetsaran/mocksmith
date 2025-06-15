# Python Database Types

Specialized database types with validation for Python. Supports both standard Python and Pydantic models.

## Features

- ✅ Strict type validation matching database constraints
- ✅ Integer types: TinyInt, SmallInt, Int, BigInt (signed & unsigned)
- ✅ Decimal types with precision and scale: Decimal[10,2]
- ✅ String types with length limits: VarChar[50], Char[10]
- ✅ Temporal types: Date, Time, DateTime with timezone support
- ✅ Seamless Pydantic integration
- ✅ Clear error messages for validation failures

## Installation

```bash
pip install python-db-types

# With Pydantic support
pip install python-db-types[pydantic]
```

## Quick Start

```python
from db_types import TinyInt, VarChar, Decimal

# Basic usage
age = TinyInt(25)  # Valid: -128 to 127
name = VarChar[50]("John Doe")  # Max 50 characters
price = Decimal[10, 2]("99.99")  # 10 digits total, 2 decimal places

# With Pydantic
from pydantic import BaseModel
from db_types.pydantic import SmallInt, Money, VarChar

class Product(BaseModel):
    id: SmallInt
    name: VarChar[100]
    price: Money  # Decimal[19,4]
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

# Type checking
mypy src

# Linting
ruff check src tests
```