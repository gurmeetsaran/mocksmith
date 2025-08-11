"""Numeric types with SQL-compliant validation and mock generation.

This module provides numeric types that:
1. Validate at instantiation to prevent invalid data
2. Respect SQL type bounds (TINYINT, SMALLINT, INTEGER, BIGINT)
3. Generate correct mock data within constraints
4. Work seamlessly with both Pydantic models and dataclasses
"""

from decimal import Decimal
from typing import Any, ClassVar, Optional, Union

try:
    from pydantic import GetCoreSchemaHandler  # type: ignore
    from pydantic_core import PydanticCustomError, core_schema  # type: ignore

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback for when Pydantic is not available
    GetCoreSchemaHandler = Any
    core_schema = None
    PydanticCustomError = ValueError


class _BaseInteger(int):
    """Base class for all integer types with SQL bounds and constraints."""

    # To be defined by subclasses
    SQL_MIN: ClassVar[int]
    SQL_MAX: ClassVar[int]
    SQL_TYPE: ClassVar[str]

    # Instance constraints (set via factory functions)
    _gt: Optional[int] = None
    _ge: Optional[int] = None
    _lt: Optional[int] = None
    _le: Optional[int] = None
    _multiple_of: Optional[int] = None
    _strict: bool = False

    def __new__(cls, value: Any):
        """Create new integer with validation."""
        # Handle string conversion
        if isinstance(value, str):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValueError(
                    f"{cls.SQL_TYPE} requires numeric value, got string '{value}'"
                ) from None

        # Handle float conversion
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"{cls.SQL_TYPE} requires integer value, got float {value}")
            value = int(value)

        if not isinstance(value, int):
            raise ValueError(f"{cls.SQL_TYPE} requires integer value, got {type(value).__name__}")

        # Check SQL bounds
        if value < cls.SQL_MIN or value > cls.SQL_MAX:
            raise ValueError(
                f"Value {value} out of {cls.SQL_TYPE} range ({cls.SQL_MIN} to {cls.SQL_MAX})"
            )

        # Check custom constraints if they exist
        if cls._gt is not None and value <= cls._gt:
            raise ValueError(f"Value must be greater than {cls._gt}, got {value}")
        if cls._ge is not None and value < cls._ge:
            raise ValueError(f"Value must be greater than or equal to {cls._ge}, got {value}")
        if cls._lt is not None and value >= cls._lt:
            raise ValueError(f"Value must be less than {cls._lt}, got {value}")
        if cls._le is not None and value > cls._le:
            raise ValueError(f"Value must be less than or equal to {cls._le}, got {value}")
        if cls._multiple_of is not None and value % cls._multiple_of != 0:
            raise ValueError(f"Value must be a multiple of {cls._multiple_of}, got {value}")

        return super().__new__(cls, value)

    @classmethod
    def validate(cls, value: Any) -> int:
        """Validate a value without creating an instance."""
        # This method is for compatibility with V1 API
        instance = cls(value)
        return int(instance)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_integer(value: Any) -> int:
            """Validate value meets SQL and custom constraints."""
            # Use the __new__ validation logic
            try:
                instance = cls(value)
                return int(instance)
            except ValueError as e:
                raise PydanticCustomError(f"{cls.SQL_TYPE.lower()}_type", str(e)) from e

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_integer, core_schema.int_schema()  # type: ignore
        )

    @classmethod
    def mock(cls) -> int:
        """Generate mock value respecting all constraints."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None

        # Calculate effective bounds
        min_val = cls.SQL_MIN
        max_val = cls.SQL_MAX

        if cls._gt is not None:
            min_val = max(min_val, cls._gt + 1)
        elif cls._ge is not None:
            min_val = max(min_val, cls._ge)

        if cls._lt is not None:
            max_val = min(max_val, cls._lt - 1)
        elif cls._le is not None:
            max_val = min(max_val, cls._le)

        if min_val > max_val:
            raise ValueError("No valid values exist with given constraints")

        # Use full range - faker can handle large integers
        faker_min = min_val
        faker_max = max_val

        if cls._multiple_of is not None:
            # Adjust min to be a valid multiple
            if faker_min % cls._multiple_of != 0:
                faker_min = faker_min + (cls._multiple_of - faker_min % cls._multiple_of)

            if faker_min > faker_max:
                raise ValueError(f"No valid multiples of {cls._multiple_of} in range")

            return fake.random_int(min=faker_min, max=faker_max, step=cls._multiple_of)
        else:
            return fake.random_int(min=faker_min, max=faker_max)

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility with V1."""
        return self.SQL_TYPE

    def serialize(self) -> int:
        """Serialize to int for SQL."""
        return int(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({int(self)})"


class TINYINT(_BaseInteger):
    """8-bit integer (-128 to 127)."""

    SQL_MIN = -128
    SQL_MAX = 127
    SQL_TYPE = "TINYINT"


class SMALLINT(_BaseInteger):
    """16-bit integer (-32768 to 32767)."""

    SQL_MIN = -32768
    SQL_MAX = 32767
    SQL_TYPE = "SMALLINT"


class INTEGER(_BaseInteger):
    """32-bit integer (-2147483648 to 2147483647)."""

    SQL_MIN = -2147483648
    SQL_MAX = 2147483647
    SQL_TYPE = "INTEGER"


class BIGINT(_BaseInteger):
    """64-bit integer."""

    SQL_MIN = -9223372036854775808
    SQL_MAX = 9223372036854775807
    SQL_TYPE = "BIGINT"


# Factory functions for creating constrained types
def TinyInt(  # noqa: N802
    *,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
    strict: bool = False,
    **kwargs,  # Accept but ignore extra kwargs for compatibility
) -> type:
    """Create a constrained TINYINT type."""
    if not any(
        [gt is not None, ge is not None, lt is not None, le is not None, multiple_of is not None]
    ):
        return TINYINT

    class ConstrainedTinyInt(TINYINT):
        _gt = gt
        _ge = ge
        _lt = lt
        _le = le
        _multiple_of = multiple_of
        _strict = strict

    return ConstrainedTinyInt


def SmallInt(  # noqa: N802
    *,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
    strict: bool = False,
    **kwargs,
) -> type:
    """Create a constrained SMALLINT type."""
    if not any(
        [gt is not None, ge is not None, lt is not None, le is not None, multiple_of is not None]
    ):
        return SMALLINT

    class ConstrainedSmallInt(SMALLINT):
        _gt = gt
        _ge = ge
        _lt = lt
        _le = le
        _multiple_of = multiple_of
        _strict = strict

    return ConstrainedSmallInt


def Integer(  # noqa: N802
    *,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
    strict: bool = False,
    **kwargs,
) -> type:
    """Create a constrained INTEGER type."""
    if not any(
        [gt is not None, ge is not None, lt is not None, le is not None, multiple_of is not None]
    ):
        return INTEGER

    class ConstrainedInteger(INTEGER):
        _gt = gt
        _ge = ge
        _lt = lt
        _le = le
        _multiple_of = multiple_of
        _strict = strict

    return ConstrainedInteger


def BigInt(  # noqa: N802
    *,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
    strict: bool = False,
    **kwargs,
) -> type:
    """Create a constrained BIGINT type."""
    if not any(
        [gt is not None, ge is not None, lt is not None, le is not None, multiple_of is not None]
    ):
        return BIGINT

    class ConstrainedBigInt(BIGINT):
        _gt = gt
        _ge = ge
        _lt = lt
        _le = le
        _multiple_of = multiple_of
        _strict = strict

    return ConstrainedBigInt


# Specialized constraint types for common patterns
def PositiveInteger() -> type:  # noqa: N802
    """Integer that must be positive (> 0)."""
    return Integer(gt=0)


def NonNegativeInteger() -> type:  # noqa: N802
    """Integer that must be non-negative (>= 0)."""
    return Integer(ge=0)


def NegativeInteger() -> type:  # noqa: N802
    """Integer that must be negative (< 0)."""
    return Integer(lt=0)


def NonPositiveInteger() -> type:  # noqa: N802
    """Integer that must be non-positive (<= 0)."""
    return Integer(le=0)


# Decimal/Float types
class DECIMAL(Decimal):
    """Fixed-point decimal type with precision and scale."""

    # Default precision and scale
    _precision: ClassVar[int] = 10
    _scale: ClassVar[int] = 2
    _gt: Optional[Decimal] = None
    _ge: Optional[Decimal] = None
    _lt: Optional[Decimal] = None
    _le: Optional[Decimal] = None
    _multiple_of: Optional[Decimal] = None

    def __new__(cls, value: Any):
        """Create new Decimal with validation."""
        # Convert to Decimal
        if value is None:
            value = 0

        if isinstance(value, str):
            try:
                dec_value = Decimal(value)
            except Exception:
                raise ValueError(f"Invalid decimal value: {value}") from None
        elif isinstance(value, (int, float)):
            dec_value = Decimal(str(value))
        elif isinstance(value, Decimal):
            dec_value = value
        else:
            raise ValueError(f"DECIMAL requires numeric value, got {type(value).__name__}")

        # Check precision/scale
        # Note: as_tuple() returns sign, digits, exponent but we only need to validate
        # the string representation for counting digits

        # Get string representation to count digits properly
        str_val = str(abs(dec_value))
        if "." in str_val:
            integer_part, decimal_part = str_val.split(".")
            integer_digits = len(integer_part)
            decimal_places = len(decimal_part)
        else:
            integer_digits = len(str_val)
            decimal_places = 0

        if integer_digits > (cls._precision - cls._scale):
            raise ValueError(
                f"Too many integer digits. Maximum is {cls._precision - cls._scale}, "
                f"got {integer_digits}"
            )

        if decimal_places > cls._scale:
            # Round to scale
            quantizer = Decimal("0.1") ** cls._scale
            dec_value = dec_value.quantize(quantizer)

        # Check constraints
        if cls._gt is not None and dec_value <= cls._gt:
            raise ValueError(f"Value must be greater than {cls._gt}, got {dec_value}")
        if cls._ge is not None and dec_value < cls._ge:
            raise ValueError(f"Value must be greater than or equal to {cls._ge}, got {dec_value}")
        if cls._lt is not None and dec_value >= cls._lt:
            raise ValueError(f"Value must be less than {cls._lt}, got {dec_value}")
        if cls._le is not None and dec_value > cls._le:
            raise ValueError(f"Value must be less than or equal to {cls._le}, got {dec_value}")
        if cls._multiple_of is not None and dec_value % cls._multiple_of != 0:
            raise ValueError(f"Value must be a multiple of {cls._multiple_of}, got {dec_value}")

        return super().__new__(cls, dec_value)

    @classmethod
    def validate(cls, value: Any) -> Decimal:
        """Validate a value without creating an instance."""
        instance = cls(value)
        return Decimal(instance)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_decimal(value: Any) -> Decimal:
            """Validate value meets precision/scale and constraints."""
            try:
                instance = cls(value)
                return Decimal(instance)
            except ValueError as e:
                raise PydanticCustomError("decimal_type", str(e)) from e

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_decimal, core_schema.decimal_schema()  # type: ignore
        )

    @classmethod
    def mock(cls) -> Decimal:
        """Generate mock decimal value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None

        # Calculate bounds based on precision/scale
        max_int_digits = cls._precision - cls._scale
        if max_int_digits > 0:
            type_max = Decimal("9" * max_int_digits + "." + "9" * cls._scale)
        else:
            type_max = Decimal("0." + "9" * cls._scale)
        type_min = -type_max

        # Apply constraints
        min_val = type_min
        max_val = type_max

        if cls._gt is not None:
            min_val = max(min_val, cls._gt + Decimal("0.0001"))
        elif cls._ge is not None:
            min_val = max(min_val, cls._ge)

        if cls._lt is not None:
            max_val = min(max_val, cls._lt - Decimal("0.0001"))
        elif cls._le is not None:
            max_val = min(max_val, cls._le)

        if cls._multiple_of is not None:
            # Find valid multiples in range
            start_mult = int(min_val / cls._multiple_of)
            if min_val > start_mult * cls._multiple_of:
                start_mult += 1

            end_mult = int(max_val / cls._multiple_of)
            if max_val < end_mult * cls._multiple_of:
                end_mult -= 1

            if start_mult > end_mult:
                raise ValueError(f"No valid multiples of {cls._multiple_of} in range")

            mult = fake.random_int(min=start_mult, max=end_mult)
            return cls._multiple_of * mult
        else:
            value = fake.pydecimal(
                left_digits=max_int_digits if max_int_digits > 0 else None,
                right_digits=cls._scale,
                positive=False,
                min_value=float(min_val),
                max_value=float(max_val),
            )
            return Decimal(str(value))

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        return f"DECIMAL({self._precision},{self._scale})"

    def serialize(self) -> Decimal:
        """Serialize for SQL."""
        return Decimal(self)


# Alias
class NUMERIC(DECIMAL):
    """Alias for DECIMAL."""

    pass


class FLOAT(float):
    """Floating-point type."""

    _gt: Optional[float] = None
    _ge: Optional[float] = None
    _lt: Optional[float] = None
    _le: Optional[float] = None
    _multiple_of: Optional[float] = None

    def __new__(cls, value: Any):
        """Create new float with validation."""
        if isinstance(value, str):
            try:
                float_value = float(value)
            except Exception:
                raise ValueError(f"Invalid float value: {value}") from None
        elif isinstance(value, (int, float, Decimal)):
            float_value = float(value)
        else:
            raise ValueError(f"FLOAT requires numeric value, got {type(value).__name__}")

        # Check for special values
        if not (-3.4e38 <= float_value <= 3.4e38):
            raise ValueError(f"Float value {float_value} out of range")

        # Check constraints
        if cls._gt is not None and float_value <= cls._gt:
            raise ValueError(f"Value must be greater than {cls._gt}, got {float_value}")
        if cls._ge is not None and float_value < cls._ge:
            raise ValueError(f"Value must be greater than or equal to {cls._ge}, got {float_value}")
        if cls._lt is not None and float_value >= cls._lt:
            raise ValueError(f"Value must be less than {cls._lt}, got {float_value}")
        if cls._le is not None and float_value > cls._le:
            raise ValueError(f"Value must be less than or equal to {cls._le}, got {float_value}")
        if cls._multiple_of is not None and float_value % cls._multiple_of != 0:
            raise ValueError(f"Value must be a multiple of {cls._multiple_of}, got {float_value}")

        return super().__new__(cls, float_value)

    @classmethod
    def validate(cls, value: Any) -> float:
        """Validate a value."""
        instance = cls(value)
        return float(instance)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_float(value: Any) -> float:
            """Validate float value."""
            try:
                instance = cls(value)
                return float(instance)
            except ValueError as e:
                raise PydanticCustomError("float_type", str(e)) from e

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_float, core_schema.float_schema()  # type: ignore
        )

    @classmethod
    def mock(cls) -> float:
        """Generate mock float value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None

        min_val = -10000.0
        max_val = 10000.0

        if cls._gt is not None:
            min_val = max(min_val, cls._gt + 0.01)
        elif cls._ge is not None:
            min_val = max(min_val, cls._ge)

        if cls._lt is not None:
            max_val = min(max_val, cls._lt - 0.01)
        elif cls._le is not None:
            max_val = min(max_val, cls._le)

        if cls._multiple_of is not None:
            # For floats with multiple_of, generate integer multiples
            min_mult = int(min_val / cls._multiple_of)
            max_mult = int(max_val / cls._multiple_of)

            if min_mult * cls._multiple_of < min_val:
                min_mult += 1
            if max_mult * cls._multiple_of > max_val:
                max_mult -= 1

            if min_mult > max_mult:
                raise ValueError(f"No valid multiples of {cls._multiple_of} in range")

            mult = fake.random_int(min=min_mult, max=max_mult)
            return float(mult * cls._multiple_of)
        else:
            return fake.pyfloat(min_value=min_val, max_value=max_val)

    @property
    def sql_type(self) -> str:
        """Return SQL type."""
        return "FLOAT"


# Alias
class DOUBLE(FLOAT):
    """Alias for FLOAT (double precision)."""

    @property
    def sql_type(self) -> str:
        return "DOUBLE"


class REAL(FLOAT):
    """Single precision float."""

    @property
    def sql_type(self) -> str:
        return "REAL"


# Factory functions for Decimal types
def DecimalType(  # noqa: N802
    precision: int = 10,
    scale: int = 2,
    *,
    gt: Optional[Union[Decimal, float, int, str]] = None,
    ge: Optional[Union[Decimal, float, int, str]] = None,
    lt: Optional[Union[Decimal, float, int, str]] = None,
    le: Optional[Union[Decimal, float, int, str]] = None,
    multiple_of: Optional[Union[Decimal, float, int]] = None,
    **kwargs,
) -> type:
    """Create a DECIMAL type with specific precision and scale."""

    class ConstrainedDecimal(DECIMAL):
        _precision = precision
        _scale = scale
        _gt = Decimal(str(gt)) if gt is not None else None
        _ge = Decimal(str(ge)) if ge is not None else None
        _lt = Decimal(str(lt)) if lt is not None else None
        _le = Decimal(str(le)) if le is not None else None
        _multiple_of = Decimal(str(multiple_of)) if multiple_of is not None else None

    return ConstrainedDecimal


def Numeric(precision: int = 10, scale: int = 2, **kwargs) -> type:  # noqa: N802
    """Alias for DecimalType."""
    return DecimalType(precision, scale, **kwargs)


def Money(**kwargs) -> type:  # noqa: N802
    """Money type: DECIMAL(19,4)."""
    return DecimalType(19, 4, **kwargs)


def PositiveMoney(**kwargs) -> type:  # noqa: N802
    """Positive money: DECIMAL(19,4) with gt=0."""
    return DecimalType(19, 4, gt=0, **kwargs)


def NonNegativeMoney(**kwargs) -> type:  # noqa: N802
    """Non-negative money: DECIMAL(19,4) with ge=0."""
    return DecimalType(19, 4, ge=0, **kwargs)


def ConstrainedMoney(**kwargs) -> type:  # noqa: N802
    """Constrained money type."""
    return DecimalType(19, 4, **kwargs)


def ConstrainedDecimal(precision: int = 10, scale: int = 2, **kwargs) -> type:  # noqa: N802
    """Constrained decimal type."""
    return DecimalType(precision, scale, **kwargs)


def Float(  # noqa: N802
    *,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    **kwargs,
) -> type:
    """Create a constrained FLOAT type."""
    if not any(
        [gt is not None, ge is not None, lt is not None, le is not None, multiple_of is not None]
    ):
        return FLOAT

    class ConstrainedFloat(FLOAT):
        _gt = gt
        _ge = ge
        _lt = lt
        _le = le
        _multiple_of = multiple_of

    return ConstrainedFloat


def Double(**kwargs) -> type:  # noqa: N802
    """Create a DOUBLE type."""
    return Float(**kwargs)


def Real(**kwargs) -> type:  # noqa: N802
    """Create a REAL type."""
    if not any(kwargs.get(k) for k in ["gt", "ge", "lt", "le", "multiple_of"]):
        return REAL

    class ConstrainedReal(REAL):
        _gt = kwargs.get("gt")
        _ge = kwargs.get("ge")
        _lt = kwargs.get("lt")
        _le = kwargs.get("le")
        _multiple_of = kwargs.get("multiple_of")

    return ConstrainedReal


def ConstrainedFloat(**kwargs) -> type:  # noqa: N802
    """Constrained float type."""
    return Float(**kwargs)
