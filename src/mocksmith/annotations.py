"""Clean annotation helpers for database types.

This module provides clean, easy-to-use type annotations for both
Pydantic models and Python dataclasses.
"""

from decimal import Decimal
from typing import Annotated, Any, Optional, Union

from mocksmith.types.binary import Binary as BinaryImpl
from mocksmith.types.binary import Blob as BlobImpl
from mocksmith.types.binary import VarBinary as VarBinaryImpl
from mocksmith.types.boolean import Boolean as BooleanImpl

# Import factory functions directly
from mocksmith.types.numeric import BigInt as BigIntImpl
from mocksmith.types.numeric import ConstrainedDecimal as ConstrainedDecimalImpl
from mocksmith.types.numeric import ConstrainedFloat as ConstrainedFloatImpl
from mocksmith.types.numeric import ConstrainedMoney as ConstrainedMoneyImpl
from mocksmith.types.numeric import DecimalType as DecimalTypeImpl
from mocksmith.types.numeric import Float as FloatImpl
from mocksmith.types.numeric import Integer as IntegerImpl
from mocksmith.types.numeric import Money as MoneyImpl
from mocksmith.types.numeric import NegativeInteger as NegativeIntegerImpl
from mocksmith.types.numeric import NonNegativeInteger as NonNegativeIntegerImpl
from mocksmith.types.numeric import NonPositiveInteger as NonPositiveIntegerImpl
from mocksmith.types.numeric import PositiveInteger as PositiveIntegerImpl
from mocksmith.types.numeric import SmallInt as SmallIntImpl
from mocksmith.types.numeric import TinyInt as TinyIntImpl
from mocksmith.types.string import CHAR as _CHAR
from mocksmith.types.string import TEXT as _TEXT
from mocksmith.types.string import VARCHAR as _VARCHAR
from mocksmith.types.temporal import Date as DateImpl
from mocksmith.types.temporal import DateTime as DateTimeImpl
from mocksmith.types.temporal import Time as TimeImpl
from mocksmith.types.temporal import Timestamp as TimestampImpl

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
def Varchar(
    length: int,
    *,
    min_length: Optional[int] = None,
    startswith: Optional[str] = None,
    endswith: Optional[str] = None,
    strip_whitespace: bool = False,
    to_lower: bool = False,
    to_upper: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """Variable-length string with maximum length and optional constraints.

    Args:
        length: Maximum length of the string
        min_length: Minimum length of the string
        startswith: String must start with this prefix
        endswith: String must end with this suffix
        strip_whitespace: Whether to strip whitespace
        to_lower: Convert to lowercase
        to_upper: Convert to uppercase
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class User(BaseModel):
            name: Varchar(50, min_length=2)
            email: Varchar(100, to_lower=True, endswith='@example.com')
            username: Varchar(30, min_length=3, to_lower=True)
            order_id: Varchar(20, startswith='ORD-')
    """
    db_type = _VARCHAR(
        length,
        min_length=min_length,
        startswith=startswith,
        endswith=endswith,
        strip_whitespace=strip_whitespace,
        to_lower=to_lower,
        to_upper=to_upper,
        **pydantic_kwargs,
    )
    if _PYDANTIC_AVAILABLE:
        # Include both DBTypeValidator for Pydantic and the raw db_type for dataclasses
        return Annotated[str, _get_validator(db_type), db_type]
    return Annotated[str, db_type]


def Char(
    length: int,
    *,
    startswith: Optional[str] = None,
    endswith: Optional[str] = None,
    strip_whitespace: bool = False,
    to_lower: bool = False,
    to_upper: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """Fixed-length string (padded with spaces) with optional constraints.

    Args:
        length: Fixed length of the string
        startswith: String must start with this prefix
        endswith: String must end with this suffix
        strip_whitespace: Whether to strip whitespace on input
        to_lower: Convert to lowercase
        to_upper: Convert to uppercase
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class Account(BaseModel):
            code: Char(10)
            country: Char(2, to_upper=True)
            product_code: Char(8, startswith='PRD-')
    """
    db_type = _CHAR(
        length,
        startswith=startswith,
        endswith=endswith,
        strip_whitespace=strip_whitespace,
        to_lower=to_lower,
        to_upper=to_upper,
        **pydantic_kwargs,
    )
    if _PYDANTIC_AVAILABLE:
        return Annotated[str, _get_validator(db_type), db_type]
    return Annotated[str, db_type]


def Text(
    *,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    startswith: Optional[str] = None,
    endswith: Optional[str] = None,
    strip_whitespace: bool = False,
    to_lower: bool = False,
    to_upper: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """Variable-length text field with optional constraints.

    Args:
        max_length: Optional maximum length
        min_length: Minimum length of the text
        startswith: Text must start with this prefix
        endswith: Text must end with this suffix
        strip_whitespace: Whether to strip whitespace
        to_lower: Convert to lowercase
        to_upper: Convert to uppercase
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class Article(BaseModel):
            content: Text(min_length=100)
            summary: Text(max_length=500)
            description: Text(strip_whitespace=True)
            review: Text(min_length=50, startswith='Review: ')
    """
    db_type = _TEXT(
        max_length=max_length,
        min_length=min_length,
        startswith=startswith,
        endswith=endswith,
        strip_whitespace=strip_whitespace,
        to_lower=to_lower,
        to_upper=to_upper,
        **pydantic_kwargs,
    )
    if _PYDANTIC_AVAILABLE:
        return Annotated[str, _get_validator(db_type), db_type]
    return Annotated[str, db_type]


# Numeric Types


def DecimalType(
    precision: int,
    scale: int,
    *,
    gt: Optional[Union[int, float, Decimal]] = None,
    ge: Optional[Union[int, float, Decimal]] = None,
    lt: Optional[Union[int, float, Decimal]] = None,
    le: Optional[Union[int, float, Decimal]] = None,
    multiple_of: Optional[Union[int, float, Decimal]] = None,
    strict: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """Fixed-point decimal number with optional constraints.

    Args:
        precision: Total number of digits
        scale: Number of digits after decimal point
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class Invoice(BaseModel):
            amount: DecimalType(10, 2, ge=0)  # Non-negative amount
            discount_rate: DecimalType(5, 4, ge=0, le=1)  # 0.0000 to 1.0000
            price: DecimalType(19, 4, gt=0)  # Positive price
    """
    return DecimalTypeImpl(
        precision,
        scale,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        strict=strict,
        **pydantic_kwargs,
    )


def Money() -> Any:
    """Money type - alias for DECIMAL(19, 4).

    Example:
        class Order(BaseModel):
            total: Money()
            discount: Money()
    """
    return MoneyImpl()


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
    return ConstrainedMoneyImpl(
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
    )


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
    return ConstrainedDecimalImpl(
        precision,
        scale,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
    )


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
    return ConstrainedFloatImpl(
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
    )


def Float(
    *,
    precision: Optional[int] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: bool = False,
    strict: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """Floating-point number with optional constraints.

    Args:
        precision: SQL precision (optional)
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this
        allow_inf_nan: Whether to allow inf/-inf/nan values
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class Measurement(BaseModel):
            temperature: Float(ge=-273.15)  # Above absolute zero
            percentage: Float(ge=0.0, le=100.0)
            probability: Float(ge=0.0, le=1.0)
    """
    return FloatImpl(
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        strict=strict,
        **pydantic_kwargs,
    )


def Double() -> Any:
    """Double precision floating-point.

    Example:
        class Scientific(BaseModel):
            measurement: Double()
            calculation: Double()
    """
    return FloatImpl()


def Real() -> Any:
    """Single precision floating-point (REAL SQL type).

    Note: In Python, this behaves identically to Float() since Python
    only has one float type. The distinction is purely for SQL generation.

    Example:
        class Measurement(BaseModel):
            temperature: Real()
            pressure: Real()
    """
    from mocksmith.types.numeric import REAL

    return REAL


# Constrained Numeric Types
def Integer(
    *,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
    strict: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """32-bit integer with optional constraints.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be divisible by this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class Product(BaseModel):
            id: Integer(gt=0)  # Positive ID
            quantity: Integer(ge=0)  # Non-negative quantity
            discount: Integer(ge=0, le=100)  # Percentage 0-100
            bulk_size: Integer(multiple_of=12)  # Dozen packs
    """
    return IntegerImpl(
        gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of, strict=strict, **pydantic_kwargs
    )


def BigInt(
    *,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
    strict: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """64-bit integer with optional constraints.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be divisible by this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class Transaction(BaseModel):
            id: BigInt(gt=0)  # Positive ID
            timestamp_ms: BigInt(ge=0)  # Unix timestamp in milliseconds
            amount_cents: BigInt(ge=-1000000, le=1000000)
    """
    return BigIntImpl(
        gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of, strict=strict, **pydantic_kwargs
    )


def SmallInt(
    *,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
    strict: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """16-bit integer with optional constraints.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be divisible by this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class Settings(BaseModel):
            retry_count: SmallInt(ge=0, le=10)
            priority: SmallInt(gt=0, le=5)
    """
    return SmallIntImpl(
        gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of, strict=strict, **pydantic_kwargs
    )


def PositiveInteger() -> Any:
    """Integer that only accepts positive values (> 0).

    Example:
        class User(BaseModel):
            id: PositiveInteger()
            age: PositiveInteger()
    """
    return PositiveIntegerImpl()


def NegativeInteger() -> Any:
    """Integer that only accepts negative values (< 0).

    Example:
        class Account(BaseModel):
            overdraft_limit: NegativeInteger()
    """
    return NegativeIntegerImpl()


def NonNegativeInteger() -> Any:
    """Integer that accepts zero and positive values (>= 0).

    Example:
        class Product(BaseModel):
            quantity: NonNegativeInteger()
            views: NonNegativeInteger()
    """
    return NonNegativeIntegerImpl()


def NonPositiveInteger() -> Any:
    """Integer that accepts zero and negative values (<= 0).

    Example:
        class GameScore(BaseModel):
            penalty_points: NonPositiveInteger()
            debt: NonPositiveInteger()
    """
    return NonPositiveIntegerImpl()


def TinyInt(
    *,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
    strict: bool = False,
    **pydantic_kwargs: Any,
) -> Any:
    """8-bit integer with optional constraints.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be divisible by this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Example:
        class Config(BaseModel):
            flag_bits: TinyInt(ge=0, le=127)  # Only positive values
            level: TinyInt(ge=-10, le=10)
    """
    return TinyIntImpl(
        gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of, strict=strict, **pydantic_kwargs
    )


# Temporal Types
def Date() -> Any:
    """Date type (year, month, day).

    Example:
        class Person(BaseModel):
            birth_date: Date()
            hire_date: Date()
    """
    # Use V3 Date type directly
    return DateImpl()


def Time(*, precision: int = 6) -> Any:
    """Time type with optional fractional seconds.

    Example:
        class Schedule(BaseModel):
            start_time: Time()
            end_time: Time(precision=0)  # No fractional seconds
    """
    # Use V3 Time type directly
    return TimeImpl(precision=precision)


def Timestamp(*, precision: int = 6, with_timezone: bool = True) -> Any:
    """Timestamp with optional timezone.

    Example:
        class Event(BaseModel):
            created_at: Timestamp()
            updated_at: Timestamp(with_timezone=False)
            processed_at: Timestamp(precision=3)  # Milliseconds
    """
    # Use V3 Timestamp type directly
    return TimestampImpl(precision=precision, with_timezone=with_timezone)


def DateTime(*, precision: int = 6) -> Any:
    """DateTime type - alias for Timestamp without timezone.

    Example:
        class Log(BaseModel):
            timestamp: DateTime()
            processed: DateTime(precision=0)
    """
    # Use V3 DateTime type directly
    return DateTimeImpl(precision=precision)


# Boolean Type
def Boolean() -> Any:
    """Boolean type that accepts various representations.

    Example:
        class User(BaseModel):
            is_active: Boolean()
            is_verified: Boolean()
    """
    # Use V3 Boolean type directly
    return BooleanImpl()


# Binary Types
def Binary(length: int) -> Any:
    """Fixed-length binary data.

    Example:
        class File(BaseModel):
            hash: Binary(32)  # MD5 hash
            signature: Binary(64)
    """
    # Use V3 Binary type directly
    return BinaryImpl(length)


def VarBinary(max_length: int) -> Any:
    """Variable-length binary data.

    Example:
        class Document(BaseModel):
            thumbnail: VarBinary(1024)
            preview: VarBinary(10240)
    """
    # Use V3 VarBinary type directly
    return VarBinaryImpl(max_length)


def Blob(*, max_length: Optional[int] = None) -> Any:
    """Binary Large Object.

    Example:
        class Media(BaseModel):
            data: Blob()
            thumbnail: Blob(max_length=65536)  # 64KB max
    """
    # Use V3 Blob type directly
    return BlobImpl(max_length)


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
