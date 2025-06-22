"""Numeric database types."""

from decimal import Decimal
from math import isfinite
from typing import Any, Optional, Union

from mocksmith.types.base import DBType


class INTEGER(DBType[int]):
    """32-bit integer type."""

    MIN_VALUE = -2147483648
    MAX_VALUE = 2147483647

    @property
    def sql_type(self) -> str:
        return "INTEGER"

    @property
    def python_type(self) -> type[int]:
        return int

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        if isinstance(value, float) and not value.is_integer():
            raise ValueError(f"Expected integer value, got float {value}")

        int_value = int(value)
        if int_value < self.MIN_VALUE or int_value > self.MAX_VALUE:
            raise ValueError(f"Value {int_value} out of range for INTEGER")

    def _serialize(self, value: Union[int, float]) -> int:
        return int(value)

    def _deserialize(self, value: Any) -> int:
        return int(value)


class BIGINT(DBType[int]):
    """64-bit integer type."""

    MIN_VALUE = -9223372036854775808
    MAX_VALUE = 9223372036854775807

    @property
    def sql_type(self) -> str:
        return "BIGINT"

    @property
    def python_type(self) -> type[int]:
        return int

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        if isinstance(value, float) and not value.is_integer():
            raise ValueError(f"Expected integer value, got float {value}")

        int_value = int(value)
        if int_value < self.MIN_VALUE or int_value > self.MAX_VALUE:
            raise ValueError(f"Value {int_value} out of range for BIGINT")

    def _serialize(self, value: Union[int, float]) -> int:
        return int(value)

    def _deserialize(self, value: Any) -> int:
        return int(value)


class SMALLINT(DBType[int]):
    """16-bit integer type."""

    MIN_VALUE = -32768
    MAX_VALUE = 32767

    @property
    def sql_type(self) -> str:
        return "SMALLINT"

    @property
    def python_type(self) -> type[int]:
        return int

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        if isinstance(value, float) and not value.is_integer():
            raise ValueError(f"Expected integer value, got float {value}")

        int_value = int(value)
        if int_value < self.MIN_VALUE or int_value > self.MAX_VALUE:
            raise ValueError(f"Value {int_value} out of range for SMALLINT")

    def _serialize(self, value: Union[int, float]) -> int:
        return int(value)

    def _deserialize(self, value: Any) -> int:
        return int(value)


class TINYINT(DBType[int]):
    """8-bit integer type."""

    MIN_VALUE = -128
    MAX_VALUE = 127

    @property
    def sql_type(self) -> str:
        return "TINYINT"

    @property
    def python_type(self) -> type[int]:
        return int

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        if isinstance(value, float) and not value.is_integer():
            raise ValueError(f"Expected integer value, got float {value}")

        int_value = int(value)
        if int_value < self.MIN_VALUE or int_value > self.MAX_VALUE:
            raise ValueError(f"Value {int_value} out of range for TINYINT")

    def _serialize(self, value: Union[int, float]) -> int:
        return int(value)

    def _deserialize(self, value: Any) -> int:
        return int(value)


class DECIMAL(DBType[Decimal]):
    """Fixed-point decimal type."""

    def __init__(self, precision: int, scale: int):
        super().__init__()
        if precision <= 0:
            raise ValueError("Precision must be positive")
        if scale < 0:
            raise ValueError("Scale cannot be negative")
        if scale > precision:
            raise ValueError("Scale cannot exceed precision")

        self.precision = precision
        self.scale = scale

    @property
    def sql_type(self) -> str:
        return f"DECIMAL({self.precision},{self.scale})"

    @property
    def python_type(self) -> type[Decimal]:
        return Decimal

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float, Decimal, str)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        try:
            dec_value = Decimal(str(value))
        except Exception as e:
            raise ValueError(f"Cannot convert {value} to Decimal: {e}") from e

        # Check precision and scale
        _, digits, exponent = dec_value.as_tuple()

        # Calculate decimal places
        # Handle special values (Infinity, NaN)
        if isinstance(exponent, str):
            # Special values like 'F' (Infinity), 'n' (NaN)
            raise ValueError(f"Special value not allowed: {dec_value}")
        decimal_places = -exponent if exponent < 0 else 0
        if decimal_places > self.scale:
            raise ValueError(
                f"Value has {decimal_places} decimal places, exceeds scale {self.scale}"
            )

        # Check total significant digits
        # For DECIMAL(10,2), we can have at most 10 total digits
        total_digits = len(digits)
        if total_digits > self.precision:
            raise ValueError(f"Value has {total_digits} digits, exceeds precision {self.precision}")

        # Also check that integer part doesn't exceed precision - scale
        # For DECIMAL(10,2), integer part can have at most 8 digits
        integer_digits = total_digits - decimal_places
        max_integer_digits = self.precision - self.scale
        if integer_digits > max_integer_digits:
            raise ValueError(
                f"Integer part has {integer_digits} digits, exceeds maximum {max_integer_digits}"
            )

    def _serialize(self, value: Union[int, float, Decimal, str]) -> str:
        return str(Decimal(str(value)))

    def _deserialize(self, value: Any) -> Decimal:
        return Decimal(str(value))

    def __repr__(self) -> str:
        return f"DECIMAL({self.precision},{self.scale})"


class NUMERIC(DECIMAL):
    """Alias for DECIMAL."""

    @property
    def sql_type(self) -> str:
        return f"NUMERIC({self.precision},{self.scale})"


class FLOAT(DBType[float]):
    """Floating-point number type."""

    def __init__(self, precision: Optional[int] = None):
        super().__init__()
        self.precision = precision

    @property
    def sql_type(self) -> str:
        if self.precision:
            return f"FLOAT({self.precision})"
        return "FLOAT"

    @property
    def python_type(self) -> type[float]:
        return float

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

    def _serialize(self, value: Union[int, float]) -> float:
        return float(value)

    def _deserialize(self, value: Any) -> float:
        return float(value)


class REAL(DBType[float]):
    """Single precision floating-point number.

    Note: In Python, this behaves identically to FLOAT since Python
    only has one float type. The distinction is purely for SQL generation
    where REAL typically indicates single precision (32-bit) vs FLOAT/DOUBLE
    for double precision (64-bit) in many databases.
    """

    # Single precision float limits (32-bit IEEE 754)
    # Note: Using slightly smaller bounds to avoid edge cases
    MAX_VALUE = 3.4028235e38
    MIN_VALUE = -3.4028235e38
    MIN_POSITIVE = 1.175494e-38

    @property
    def sql_type(self) -> str:
        return "REAL"

    @property
    def python_type(self) -> type[float]:
        return float

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        # Check if value fits within single precision range
        float_value = float(value)

        # Handle special float values
        if not isfinite(float_value):
            # Allow inf, -inf, and nan as they can be represented in single precision
            return

        if float_value != 0:  # Skip zero check
            abs_value = abs(float_value)
            if abs_value > self.MAX_VALUE:
                raise ValueError(
                    f"Value {value} exceeds REAL precision range " f"(max ±{self.MAX_VALUE:.2e})"
                )
            if abs_value < self.MIN_POSITIVE:
                raise ValueError(
                    f"Value {value} is too small for REAL precision "
                    f"(min positive {self.MIN_POSITIVE:.2e})"
                )

    def _serialize(self, value: Union[int, float]) -> float:
        return float(value)

    def _deserialize(self, value: Any) -> float:
        return float(value)


class DOUBLE(DBType[float]):
    """Double precision floating-point number."""

    @property
    def sql_type(self) -> str:
        return "DOUBLE PRECISION"

    @property
    def python_type(self) -> type[float]:
        return float

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

    def _serialize(self, value: Union[int, float]) -> float:
        return float(value)

    def _deserialize(self, value: Any) -> float:
        return float(value)
