"""Clean annotation helpers for database types.

This module provides clean, easy-to-use type annotations for both
Pydantic models and Python dataclasses.
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Annotated, Any, Optional, Union

from mocksmith.types.binary import BINARY as _BINARY
from mocksmith.types.binary import BLOB as _BLOB
from mocksmith.types.binary import VARBINARY as _VARBINARY
from mocksmith.types.boolean import BOOLEAN as _BOOLEAN
from mocksmith.types.constraints import ConstrainedBigInt as _ConstrainedBigInt
from mocksmith.types.constraints import ConstrainedInteger as _ConstrainedInteger
from mocksmith.types.constraints import ConstrainedSmallInt as _ConstrainedSmallInt
from mocksmith.types.constraints import ConstrainedTinyInt as _ConstrainedTinyInt
from mocksmith.types.constraints import NegativeInteger as _NegativeInteger
from mocksmith.types.constraints import NonNegativeInteger as _NonNegativeInteger
from mocksmith.types.constraints import NonPositiveInteger as _NonPositiveInteger
from mocksmith.types.constraints import PositiveInteger as _PositiveInteger
from mocksmith.types.numeric import BIGINT as _BIGINT
from mocksmith.types.numeric import DECIMAL as _DECIMAL
from mocksmith.types.numeric import DOUBLE as _DOUBLE
from mocksmith.types.numeric import FLOAT as _FLOAT
from mocksmith.types.numeric import INTEGER as _INTEGER
from mocksmith.types.numeric import REAL as _REAL
from mocksmith.types.numeric import SMALLINT as _SMALLINT
from mocksmith.types.numeric import TINYINT as _TINYINT
from mocksmith.types.string import CHAR as _CHAR
from mocksmith.types.string import TEXT as _TEXT
from mocksmith.types.string import VARCHAR as _VARCHAR
from mocksmith.types.temporal import DATE as _DATE
from mocksmith.types.temporal import TIME as _TIME
from mocksmith.types.temporal import TIMESTAMP as _TIMESTAMP

# For Pydantic models - check if Pydantic is available
try:
    from mocksmith.pydantic_integration import DBTypeValidator as _DBTypeValidator

    _PYDANTIC_AVAILABLE = True

    def _get_validator(db_type: Any) -> Any:
        if _DBTypeValidator is not None:
            return _DBTypeValidator(db_type)
        return None

except ImportError:
    _PYDANTIC_AVAILABLE = False
    _DBTypeValidator = None  # type: ignore

    def _get_validator(db_type: Any) -> Any:  # type: ignore
        return None


# String Types
def Varchar(length: int) -> Any:
    """Variable-length string with maximum length.

    Example:
        class User(BaseModel):
            name: Varchar(50)
            email: Varchar(100)
    """
    db_type = _VARCHAR(length)
    if _PYDANTIC_AVAILABLE:
        # Include both DBTypeValidator for Pydantic and the raw db_type for dataclasses
        return Annotated[str, _get_validator(db_type), db_type]
    return Annotated[str, db_type]


def Char(length: int) -> Any:
    """Fixed-length string (padded with spaces).

    Example:
        class Account(BaseModel):
            code: Char(10)
            country: Char(2)
    """
    db_type = _CHAR(length)
    if _PYDANTIC_AVAILABLE:
        return Annotated[str, _get_validator(db_type), db_type]
    return Annotated[str, db_type]


def Text(*, max_length: Optional[int] = None) -> Any:
    """Variable-length text field.

    Example:
        class Article(BaseModel):
            content: Text()
            summary: Text(max_length=500)
    """
    db_type = _TEXT(max_length=max_length)
    if _PYDANTIC_AVAILABLE:
        return Annotated[str, _get_validator(db_type), db_type]
    return Annotated[str, db_type]


# Numeric Types


def DecimalType(precision: int, scale: int) -> Any:
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
    if _PYDANTIC_AVAILABLE:
        return Annotated[Decimal, _get_validator(db_type), db_type]
    return Annotated[Decimal, db_type]


def Money() -> Any:
    """Money type - alias for DECIMAL(19, 4).

    Example:
        class Order(BaseModel):
            total: Money()
            discount: Money()
    """
    return DecimalType(19, 4)


def ConstrainedMoney(
    *,
    gt: Optional[Union[int, float, Decimal]] = None,
    ge: Optional[Union[int, float, Decimal]] = None,
    lt: Optional[Union[int, float, Decimal]] = None,
    le: Optional[Union[int, float, Decimal]] = None,
    multiple_of: Optional[Union[int, float, Decimal]] = None,
) -> Any:
    """Money type with constraints using Pydantic's condecimal.

    This provides a Money type (DECIMAL(19,4)) with additional validation constraints.
    Works seamlessly with Pydantic models and mocksmith's mock generation.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this

    Example:
        class Product(BaseModel):
            price: ConstrainedMoney(gt=0)  # Positive money
            discount: ConstrainedMoney(ge=0, le=100)  # 0-100

        # Or use shortcuts:
        class Order(BaseModel):
            total: PositiveMoney()  # Same as ConstrainedMoney(gt=0)
            balance: NonNegativeMoney()  # Same as ConstrainedMoney(ge=0)
    """
    try:
        from pydantic import condecimal

        return condecimal(
            max_digits=19,
            decimal_places=4,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
        )
    except ImportError:
        # Fallback to regular Money if Pydantic not available
        return DecimalType(19, 4)


def PositiveMoney() -> Any:
    """Money type that only accepts positive values (> 0).

    Shortcut for ConstrainedMoney(gt=0).

    Example:
        class Product(BaseModel):
            price: PositiveMoney()
            cost: PositiveMoney()
    """
    return ConstrainedMoney(gt=0)


def NonNegativeMoney() -> Any:
    """Money type that accepts zero and positive values (>= 0).

    Shortcut for ConstrainedMoney(ge=0).

    Example:
        class Account(BaseModel):
            balance: NonNegativeMoney()
            credit_limit: NonNegativeMoney()
    """
    return ConstrainedMoney(ge=0)


def ConstrainedDecimal(
    precision: int,
    scale: int,
    *,
    gt: Optional[Union[int, float, Decimal]] = None,
    ge: Optional[Union[int, float, Decimal]] = None,
    lt: Optional[Union[int, float, Decimal]] = None,
    le: Optional[Union[int, float, Decimal]] = None,
    multiple_of: Optional[Union[int, float, Decimal]] = None,
) -> Any:
    """Decimal type with constraints using Pydantic's condecimal.

    Args:
        precision: Total number of digits
        scale: Number of decimal places
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this

    Example:
        class Measurement(BaseModel):
            weight: ConstrainedDecimal(10, 2, gt=0)  # Positive weight
            temperature: ConstrainedDecimal(5, 2, ge=-273.15)  # Above absolute zero
    """
    try:
        from pydantic import condecimal

        return condecimal(
            max_digits=precision,
            decimal_places=scale,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
        )
    except ImportError:
        # Fallback to regular DecimalType if Pydantic not available
        return DecimalType(precision, scale)


def ConstrainedFloat(
    *,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
) -> Any:
    """Float type with constraints using Pydantic's confloat.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this

    Example:
        class Scientific(BaseModel):
            probability: ConstrainedFloat(ge=0.0, le=1.0)  # 0-1 range
            temperature: ConstrainedFloat(gt=-273.15)  # Above absolute zero
    """
    try:
        from pydantic import confloat

        return confloat(gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of)
    except ImportError:
        # Fallback to regular Float if Pydantic not available
        return Float()


def Float(*, precision: Optional[int] = None) -> Any:
    """Floating-point number.

    Example:
        class Measurement(BaseModel):
            temperature: Float()
            pressure: Float(precision=24)
    """
    db_type = _FLOAT(precision=precision)
    if _PYDANTIC_AVAILABLE:
        return Annotated[float, _get_validator(db_type), db_type]
    return Annotated[float, db_type]


def Double() -> Any:
    """Double precision floating-point.

    Example:
        class Scientific(BaseModel):
            measurement: Double()
            calculation: Double()
    """
    db_type = _DOUBLE()
    if _PYDANTIC_AVAILABLE:
        return Annotated[float, _get_validator(db_type), db_type]
    return Annotated[float, db_type]


def Real() -> Any:
    """Single precision floating-point (REAL SQL type).

    Note: In Python, this behaves identically to Float() since Python
    only has one float type. The distinction is purely for SQL generation.

    Example:
        class Measurement(BaseModel):
            temperature: Real()
            pressure: Real()
    """
    db_type = _REAL()
    if _PYDANTIC_AVAILABLE:
        return Annotated[float, _get_validator(db_type), db_type]
    return Annotated[float, db_type]


# Constrained Numeric Types
def Integer(
    *,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    multiple_of: Optional[int] = None,
    positive: bool = False,
    negative: bool = False,
) -> Any:
    """Integer with optional constraints.

    When called without arguments, returns standard INTEGER.
    With arguments, returns ConstrainedInteger.

    Args:
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        multiple_of: Value must be divisible by this
        positive: Shortcut for min_value=1
        negative: Shortcut for max_value=-1

    Example:
        class Product(BaseModel):
            id: Integer(positive=True)  # Same as PositiveInteger()
            quantity: Integer(min_value=0)  # Same as NonNegativeInteger()
            discount: Integer(min_value=0, max_value=100)
            bulk_size: Integer(multiple_of=12)
    """
    # If no constraints, return standard INTEGER
    if (
        all(x is None for x in [min_value, max_value, multiple_of])
        and not positive
        and not negative
    ):
        db_type = _INTEGER()
    else:
        db_type = _ConstrainedInteger(
            min_value=min_value,
            max_value=max_value,
            multiple_of=multiple_of,
            positive=positive,
            negative=negative,
        )

    if _PYDANTIC_AVAILABLE:
        return Annotated[int, _get_validator(db_type), db_type]
    return Annotated[int, db_type]


def BigInt(
    *,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    multiple_of: Optional[int] = None,
    positive: bool = False,
    negative: bool = False,
) -> Any:
    """64-bit integer with optional constraints.

    When called without arguments, returns standard BIGINT.
    With arguments, returns ConstrainedBigInt.

    Example:
        class Transaction(BaseModel):
            id: BigInt(positive=True)
            amount_cents: BigInt(min_value=-1000000, max_value=1000000)
    """
    # If no constraints, return standard BIGINT
    if (
        all(x is None for x in [min_value, max_value, multiple_of])
        and not positive
        and not negative
    ):
        db_type = _BIGINT()
    else:
        db_type = _ConstrainedBigInt(
            min_value=min_value,
            max_value=max_value,
            multiple_of=multiple_of,
            positive=positive,
            negative=negative,
        )

    if _PYDANTIC_AVAILABLE:
        return Annotated[int, _get_validator(db_type), db_type]
    return Annotated[int, db_type]


def SmallInt(
    *,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    multiple_of: Optional[int] = None,
    positive: bool = False,
    negative: bool = False,
) -> Any:
    """16-bit integer with optional constraints.

    When called without arguments, returns standard SMALLINT.
    With arguments, returns ConstrainedSmallInt.

    Example:
        class Settings(BaseModel):
            retry_count: SmallInt(min_value=0, max_value=10)
            priority: SmallInt(positive=True)
    """
    # If no constraints, return standard SMALLINT
    if (
        all(x is None for x in [min_value, max_value, multiple_of])
        and not positive
        and not negative
    ):
        db_type = _SMALLINT()
    else:
        db_type = _ConstrainedSmallInt(
            min_value=min_value,
            max_value=max_value,
            multiple_of=multiple_of,
            positive=positive,
            negative=negative,
        )

    if _PYDANTIC_AVAILABLE:
        return Annotated[int, _get_validator(db_type), db_type]
    return Annotated[int, db_type]


def PositiveInteger() -> Any:
    """Integer that only accepts positive values (> 0).

    Example:
        class User(BaseModel):
            id: PositiveInteger()
            age: PositiveInteger()
    """
    db_type = _PositiveInteger()
    if _PYDANTIC_AVAILABLE:
        return Annotated[int, _get_validator(db_type), db_type]
    return Annotated[int, db_type]


def NegativeInteger() -> Any:
    """Integer that only accepts negative values (< 0).

    Example:
        class Account(BaseModel):
            overdraft_limit: NegativeInteger()
    """
    db_type = _NegativeInteger()
    if _PYDANTIC_AVAILABLE:
        return Annotated[int, _get_validator(db_type), db_type]
    return Annotated[int, db_type]


def NonNegativeInteger() -> Any:
    """Integer that accepts zero and positive values (>= 0).

    Example:
        class Product(BaseModel):
            quantity: NonNegativeInteger()
            views: NonNegativeInteger()
    """
    db_type = _NonNegativeInteger()
    if _PYDANTIC_AVAILABLE:
        return Annotated[int, _get_validator(db_type), db_type]
    return Annotated[int, db_type]


def NonPositiveInteger() -> Any:
    """Integer that accepts zero and negative values (<= 0).

    Example:
        class GameScore(BaseModel):
            penalty_points: NonPositiveInteger()
            debt: NonPositiveInteger()
    """
    db_type = _NonPositiveInteger()
    if _PYDANTIC_AVAILABLE:
        return Annotated[int, _get_validator(db_type), db_type]
    return Annotated[int, db_type]


def TinyInt(
    *,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    multiple_of: Optional[int] = None,
    positive: bool = False,
    negative: bool = False,
) -> Any:
    """8-bit integer with optional constraints.

    When called without arguments, returns standard TINYINT.
    With arguments, returns ConstrainedTinyInt.

    Example:
        class Config(BaseModel):
            flag_bits: TinyInt(min_value=0, max_value=127)  # Only positive values
            level: TinyInt(min_value=-10, max_value=10)
    """
    # If no constraints, return standard TINYINT
    if (
        all(x is None for x in [min_value, max_value, multiple_of])
        and not positive
        and not negative
    ):
        db_type = _TINYINT()
    else:
        db_type = _ConstrainedTinyInt(
            min_value=min_value,
            max_value=max_value,
            multiple_of=multiple_of,
            positive=positive,
            negative=negative,
        )

    if _PYDANTIC_AVAILABLE:
        return Annotated[int, _get_validator(db_type), db_type]
    return Annotated[int, db_type]


# Temporal Types
def Date() -> Any:
    """Date type (year, month, day).

    Example:
        class Person(BaseModel):
            birth_date: Date()
            hire_date: Date()
    """
    db_type = _DATE()
    if _PYDANTIC_AVAILABLE:
        return Annotated[date, _get_validator(db_type), db_type]
    return Annotated[date, db_type]


def Time(*, precision: int = 6) -> Any:
    """Time type with optional fractional seconds.

    Example:
        class Schedule(BaseModel):
            start_time: Time()
            end_time: Time(precision=0)  # No fractional seconds
    """
    db_type = _TIME(precision=precision)
    if _PYDANTIC_AVAILABLE:
        return Annotated[time, _get_validator(db_type), db_type]
    return Annotated[time, db_type]


def Timestamp(*, precision: int = 6, with_timezone: bool = True) -> Any:
    """Timestamp with optional timezone.

    Example:
        class Event(BaseModel):
            created_at: Timestamp()
            updated_at: Timestamp(with_timezone=False)
            processed_at: Timestamp(precision=3)  # Milliseconds
    """
    db_type = _TIMESTAMP(precision=precision, with_timezone=with_timezone)
    if _PYDANTIC_AVAILABLE:
        return Annotated[datetime, _get_validator(db_type), db_type]
    return Annotated[datetime, db_type]


def DateTime(*, precision: int = 6) -> Any:
    """DateTime type - alias for Timestamp without timezone.

    Example:
        class Log(BaseModel):
            timestamp: DateTime()
            processed: DateTime(precision=0)
    """
    return Timestamp(precision=precision, with_timezone=False)


# Boolean Type
def Boolean() -> Any:
    """Boolean type that accepts various representations.

    Example:
        class User(BaseModel):
            is_active: Boolean()
            is_verified: Boolean()
    """
    db_type = _BOOLEAN()
    if _PYDANTIC_AVAILABLE:
        return Annotated[bool, _get_validator(db_type), db_type]
    return Annotated[bool, db_type]


# Binary Types
def Binary(length: int) -> Any:
    """Fixed-length binary data.

    Example:
        class File(BaseModel):
            hash: Binary(32)  # MD5 hash
            signature: Binary(64)
    """
    db_type = _BINARY(length)
    if _PYDANTIC_AVAILABLE:
        return Annotated[bytes, _get_validator(db_type), db_type]
    return Annotated[bytes, db_type]


def VarBinary(max_length: int) -> Any:
    """Variable-length binary data.

    Example:
        class Document(BaseModel):
            thumbnail: VarBinary(1024)
            preview: VarBinary(10240)
    """
    db_type = _VARBINARY(max_length)
    if _PYDANTIC_AVAILABLE:
        return Annotated[bytes, _get_validator(db_type), db_type]
    return Annotated[bytes, db_type]


def Blob(*, max_length: Optional[int] = None) -> Any:
    """Binary Large Object.

    Example:
        class Media(BaseModel):
            data: Blob()
            thumbnail: Blob(max_length=65536)  # 64KB max
    """
    db_type = _BLOB(max_length=max_length)
    if _PYDANTIC_AVAILABLE:
        return Annotated[bytes, _get_validator(db_type), db_type]
    return Annotated[bytes, db_type]


# Aliases for common use cases
String = Varchar  # Alias for VARCHAR
Int = Integer  # Alias for INTEGER
Bool = Boolean  # Alias for BOOLEAN
Numeric = DecimalType  # Alias for DECIMAL


# For users who prefer uppercase
VARCHAR = Varchar
CHAR = Char
TEXT = Text
INTEGER = Integer
BIGINT = BigInt
SMALLINT = SmallInt
TINYINT = TinyInt
DECIMAL = DecimalType
NUMERIC = DecimalType
FLOAT = Float
DOUBLE = Double
REAL = Real
DATE = Date
TIME = Time
TIMESTAMP = Timestamp
DATETIME = DateTime
BOOLEAN = Boolean
BINARY = Binary
VARBINARY = VarBinary
BLOB = Blob


__all__ = [
    "BIGINT",
    "BINARY",
    "BLOB",
    "BOOLEAN",
    "CHAR",
    "DATE",
    "DATETIME",
    "DECIMAL",
    "DOUBLE",
    "FLOAT",
    "INTEGER",
    "NUMERIC",
    "REAL",
    "SMALLINT",
    "TEXT",
    "TIME",
    "TIMESTAMP",
    "TINYINT",
    "VARBINARY",
    "VARCHAR",
    "BigInt",
    "Binary",
    "Blob",
    "Bool",
    "Boolean",
    "Char",
    "ConstrainedDecimal",
    "ConstrainedFloat",
    "ConstrainedMoney",
    "Date",
    "DateTime",
    "DecimalType",
    "Double",
    "Float",
    "Int",
    "Integer",
    "Money",
    "NegativeInteger",
    "NonNegativeInteger",
    "NonNegativeMoney",
    "NonPositiveInteger",
    "Numeric",
    "PositiveInteger",
    "PositiveMoney",
    "Real",
    "SmallInt",
    "String",
    "Text",
    "Time",
    "Timestamp",
    "TinyInt",
    "VarBinary",
    "Varchar",
]
