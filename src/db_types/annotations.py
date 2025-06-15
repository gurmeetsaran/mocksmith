"""Clean annotation helpers for database types.

This module provides clean, easy-to-use type annotations for both
Pydantic models and Python dataclasses.
"""

import sys
from typing import Optional

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from datetime import date, datetime, time
from decimal import Decimal

from db_types.types.binary import BINARY as _BINARY
from db_types.types.binary import BLOB as _BLOB
from db_types.types.binary import VARBINARY as _VARBINARY
from db_types.types.boolean import BOOLEAN as _BOOLEAN
from db_types.types.numeric import BIGINT as _BIGINT
from db_types.types.numeric import DECIMAL as _DECIMAL
from db_types.types.numeric import DOUBLE as _DOUBLE
from db_types.types.numeric import FLOAT as _FLOAT
from db_types.types.numeric import INTEGER as _INTEGER
from db_types.types.numeric import SMALLINT as _SMALLINT
from db_types.types.string import CHAR as _CHAR
from db_types.types.string import TEXT as _TEXT
from db_types.types.string import VARCHAR as _VARCHAR
from db_types.types.temporal import DATE as _DATE
from db_types.types.temporal import TIME as _TIME
from db_types.types.temporal import TIMESTAMP as _TIMESTAMP

# For Pydantic models - check if Pydantic is available
try:
    from db_types.pydantic_integration import DBTypeValidator

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    DBTypeValidator = None


# String Types
def Varchar(length: int) -> type:  # noqa: N802
    """Variable-length string with maximum length.

    Example:
        class User(BaseModel):
            name: Varchar(50)
            email: Varchar(100)
    """
    db_type = _VARCHAR(length)
    if PYDANTIC_AVAILABLE:
        # Include both DBTypeValidator for Pydantic and the raw db_type for dataclasses
        return Annotated[str, DBTypeValidator(db_type), db_type]
    return Annotated[str, db_type]


def Char(length: int) -> type:  # noqa: N802
    """Fixed-length string (padded with spaces).

    Example:
        class Account(BaseModel):
            code: Char(10)
            country: Char(2)
    """
    db_type = _CHAR(length)
    if PYDANTIC_AVAILABLE:
        return Annotated[str, DBTypeValidator(db_type), db_type]
    return Annotated[str, db_type]


def Text(*, max_length: Optional[int] = None) -> type:  # noqa: N802
    """Variable-length text field.

    Example:
        class Article(BaseModel):
            content: Text()
            summary: Text(max_length=500)
    """
    db_type = _TEXT(max_length=max_length)
    if PYDANTIC_AVAILABLE:
        return Annotated[str, DBTypeValidator(db_type), db_type]
    return Annotated[str, db_type]


# Numeric Types
def Integer() -> type:  # noqa: N802
    """32-bit integer (-2,147,483,648 to 2,147,483,647).

    Example:
        class Product(BaseModel):
            quantity: Integer()
            id: Integer()
    """
    db_type = _INTEGER()
    if PYDANTIC_AVAILABLE:
        return Annotated[int, DBTypeValidator(db_type), db_type]
    return Annotated[int, db_type]


def BigInt() -> type:  # noqa: N802
    """64-bit integer.

    Example:
        class Transaction(BaseModel):
            id: BigInt()
            reference_id: BigInt()
    """
    db_type = _BIGINT()
    if PYDANTIC_AVAILABLE:
        return Annotated[int, DBTypeValidator(db_type), db_type]
    return Annotated[int, db_type]


def SmallInt() -> type:  # noqa: N802
    """16-bit integer (-32,768 to 32,767).

    Example:
        class Settings(BaseModel):
            retry_count: SmallInt()
            priority: SmallInt()
    """
    db_type = _SMALLINT()
    if PYDANTIC_AVAILABLE:
        return Annotated[int, DBTypeValidator(db_type), db_type]
    return Annotated[int, db_type]


def DecimalType(precision: int, scale: int) -> type:  # noqa: N802
    """Fixed-point decimal number.

    Args:
        precision: Total number of digits
        scale: Number of digits after decimal point

    Example:
        class Invoice(BaseModel):
            amount: DecimalType(10, 2)  # Up to 99999999.99
            tax_rate: DecimalType(5, 4)  # Up to 9.9999
    """
    db_type = _DECIMAL(precision, scale)
    if PYDANTIC_AVAILABLE:
        return Annotated[Decimal, DBTypeValidator(db_type), db_type]
    return Annotated[Decimal, db_type]


def Money() -> type:  # noqa: N802
    """Money type - alias for DECIMAL(19, 4).

    Example:
        class Order(BaseModel):
            total: Money()
            discount: Money()
    """
    return DecimalType(19, 4)


def Float(*, precision: Optional[int] = None) -> type:  # noqa: N802
    """Floating-point number.

    Example:
        class Measurement(BaseModel):
            temperature: Float()
            pressure: Float(precision=24)
    """
    db_type = _FLOAT(precision=precision)
    if PYDANTIC_AVAILABLE:
        return Annotated[float, DBTypeValidator(db_type), db_type]
    return Annotated[float, db_type]


def Double() -> type:  # noqa: N802
    """Double precision floating-point.

    Example:
        class Scientific(BaseModel):
            measurement: Double()
            calculation: Double()
    """
    db_type = _DOUBLE()
    if PYDANTIC_AVAILABLE:
        return Annotated[float, DBTypeValidator(db_type), db_type]
    return Annotated[float, db_type]


# Temporal Types
def Date() -> type:  # noqa: N802
    """Date type (year, month, day).

    Example:
        class Person(BaseModel):
            birth_date: Date()
            hire_date: Date()
    """
    db_type = _DATE()
    if PYDANTIC_AVAILABLE:
        return Annotated[date, DBTypeValidator(db_type), db_type]
    return Annotated[date, db_type]


def Time(*, precision: int = 6) -> type:  # noqa: N802
    """Time type with optional fractional seconds.

    Example:
        class Schedule(BaseModel):
            start_time: Time()
            end_time: Time(precision=0)  # No fractional seconds
    """
    db_type = _TIME(precision=precision)
    if PYDANTIC_AVAILABLE:
        return Annotated[time, DBTypeValidator(db_type), db_type]
    return Annotated[time, db_type]


def Timestamp(*, precision: int = 6, with_timezone: bool = True) -> type:  # noqa: N802
    """Timestamp with optional timezone.

    Example:
        class Event(BaseModel):
            created_at: Timestamp()
            updated_at: Timestamp(with_timezone=False)
            processed_at: Timestamp(precision=3)  # Milliseconds
    """
    db_type = _TIMESTAMP(precision=precision, with_timezone=with_timezone)
    if PYDANTIC_AVAILABLE:
        return Annotated[datetime, DBTypeValidator(db_type), db_type]
    return Annotated[datetime, db_type]


def DateTime(*, precision: int = 6) -> type:  # noqa: N802
    """DateTime type - alias for Timestamp without timezone.

    Example:
        class Log(BaseModel):
            timestamp: DateTime()
            processed: DateTime(precision=0)
    """
    return Timestamp(precision=precision, with_timezone=False)


# Boolean Type
def Boolean() -> type:  # noqa: N802
    """Boolean type that accepts various representations.

    Example:
        class User(BaseModel):
            is_active: Boolean()
            is_verified: Boolean()
    """
    db_type = _BOOLEAN()
    if PYDANTIC_AVAILABLE:
        return Annotated[bool, DBTypeValidator(db_type), db_type]
    return Annotated[bool, db_type]


# Binary Types
def Binary(length: int) -> type:  # noqa: N802
    """Fixed-length binary data.

    Example:
        class File(BaseModel):
            hash: Binary(32)  # MD5 hash
            signature: Binary(64)
    """
    db_type = _BINARY(length)
    if PYDANTIC_AVAILABLE:
        return Annotated[bytes, DBTypeValidator(db_type), db_type]
    return Annotated[bytes, db_type]


def VarBinary(max_length: int) -> type:  # noqa: N802
    """Variable-length binary data.

    Example:
        class Document(BaseModel):
            thumbnail: VarBinary(1024)
            preview: VarBinary(10240)
    """
    db_type = _VARBINARY(max_length)
    if PYDANTIC_AVAILABLE:
        return Annotated[bytes, DBTypeValidator(db_type), db_type]
    return Annotated[bytes, db_type]


def Blob(*, max_length: Optional[int] = None) -> type:  # noqa: N802
    """Binary Large Object.

    Example:
        class Media(BaseModel):
            data: Blob()
            thumbnail: Blob(max_length=65536)  # 64KB max
    """
    db_type = _BLOB(max_length=max_length)
    if PYDANTIC_AVAILABLE:
        return Annotated[bytes, DBTypeValidator(db_type), db_type]
    return Annotated[bytes, db_type]


# Aliases for common use cases
String = Varchar  # Alias for VARCHAR
Int = Integer  # Alias for INTEGER
Bool = Boolean  # Alias for BOOLEAN


# For users who prefer uppercase
VARCHAR = Varchar
CHAR = Char
TEXT = Text
INTEGER = Integer
BIGINT = BigInt
SMALLINT = SmallInt
DECIMAL = DecimalType
FLOAT = Float
DOUBLE = Double
REAL = Float
DATE = Date
TIME = Time
TIMESTAMP = Timestamp
DATETIME = DateTime
BOOLEAN = Boolean
BINARY = Binary
VARBINARY = VarBinary
BLOB = Blob


__all__ = [
    # Lowercase functions (preferred)
    "Varchar",
    "Char",
    "Text",
    "Integer",
    "BigInt",
    "SmallInt",
    "DecimalType",
    "Money",
    "Float",
    "Double",
    "Date",
    "Time",
    "Timestamp",
    "DateTime",
    "Boolean",
    "Binary",
    "VarBinary",
    "Blob",
    # Aliases
    "String",
    "Int",
    "Bool",
    # Uppercase (compatibility)
    "VARCHAR",
    "CHAR",
    "TEXT",
    "INTEGER",
    "BIGINT",
    "SMALLINT",
    "DECIMAL",
    "FLOAT",
    "DOUBLE",
    "REAL",
    "DATE",
    "TIME",
    "TIMESTAMP",
    "DATETIME",
    "BOOLEAN",
    "BINARY",
    "VARBINARY",
    "BLOB",
]
