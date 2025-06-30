"""Numeric database types."""

from decimal import Decimal
from math import isfinite
from typing import Any, Optional, Union

from mocksmith.types.base import PYDANTIC_AVAILABLE, DBType

if PYDANTIC_AVAILABLE:
    from pydantic import condecimal, confloat, conint


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

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type if available."""
        if PYDANTIC_AVAILABLE:
            return conint(ge=self.MIN_VALUE, le=self.MAX_VALUE)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
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

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type if available."""
        if PYDANTIC_AVAILABLE:
            return conint(ge=self.MIN_VALUE, le=self.MAX_VALUE)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
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

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type if available."""
        if PYDANTIC_AVAILABLE:
            return conint(ge=self.MIN_VALUE, le=self.MAX_VALUE)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
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

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type if available."""
        if PYDANTIC_AVAILABLE:
            return conint(ge=self.MIN_VALUE, le=self.MAX_VALUE)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
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

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic condecimal type if available."""
        if PYDANTIC_AVAILABLE:
            # Calculate max value based on precision and scale
            max_digits = self.precision - self.scale
            max_value = Decimal("9" * max_digits + "." + "9" * self.scale)
            min_value = -max_value

            return condecimal(
                ge=min_value, le=max_value, max_digits=self.precision, decimal_places=self.scale
            )
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        if not isinstance(value, (int, float, Decimal, str)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        try:
            dec_value = Decimal(str(value))
        except Exception as e:
            raise ValueError(f"Cannot convert {value} to Decimal") from e

        # Check if value has too many digits
        _, digits, exponent = dec_value.as_tuple()

        # Handle special values (Infinity, NaN)
        if isinstance(exponent, str):
            # Special values like 'F' (Infinity), 'n' (NaN)
            raise ValueError(f"Special value not allowed: {dec_value}")

        # Calculate total digits and decimal places
        if exponent >= 0:
            # No decimal places
            total_digits = len(digits) + exponent
            decimal_places = 0
        else:
            # Has decimal places
            total_digits = max(len(digits), -exponent)
            decimal_places = -exponent

        if total_digits - decimal_places > self.precision - self.scale:
            raise ValueError(f"Value {value} has too many digits before decimal point")

        if decimal_places > self.scale:
            raise ValueError(
                f"Value {value} has too many decimal places ({decimal_places} > {self.scale})"
            )

    def _serialize(self, value: Union[int, float, Decimal]) -> str:
        return str(Decimal(str(value)))

    def _deserialize(self, value: Any) -> Decimal:
        return Decimal(str(value))

    def __repr__(self) -> str:
        return f"DECIMAL({self.precision}, {self.scale})"

    def _generate_mock(self, fake: Any) -> Decimal:
        """Generate mock DECIMAL data."""
        # Generate appropriate decimal based on precision and scale
        max_int_digits = self.precision - self.scale

        # Generate integer part
        if max_int_digits > 0:
            max_int_value = 10**max_int_digits - 1
            int_part = fake.random_int(min=0, max=max_int_value)
        else:
            int_part = 0

        # Generate decimal part
        if self.scale > 0:
            dec_part = fake.random_int(min=0, max=10**self.scale - 1)
            dec_str = f"{int_part}.{str(dec_part).zfill(self.scale)}"
        else:
            dec_str = str(int_part)

        return Decimal(dec_str)


class NUMERIC(DECIMAL):
    """Alias for DECIMAL."""

    @property
    def sql_type(self) -> str:
        return f"NUMERIC({self.precision},{self.scale})"


class FLOAT(DBType[float]):
    """Double-precision floating-point type."""

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

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic confloat type if available."""
        if PYDANTIC_AVAILABLE:
            # Just ensure it's a valid float
            return confloat()
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        float_value = float(value)
        if not isfinite(float_value):
            raise ValueError(f"Value must be finite, got {float_value}")

    def _serialize(self, value: Union[int, float]) -> float:
        return float(value)

    def _deserialize(self, value: Any) -> float:
        return float(value)


class DOUBLE(FLOAT):
    """Alias for FLOAT (double-precision)."""

    @property
    def sql_type(self) -> str:
        return "DOUBLE PRECISION"


class REAL(DBType[float]):
    """Single-precision floating-point type."""

    # Single precision float range (approximate)
    MIN_VALUE = -3.4028235e38
    MAX_VALUE = 3.4028235e38
    MIN_POSITIVE = 1.175494e-38

    @property
    def sql_type(self) -> str:
        return "REAL"

    @property
    def python_type(self) -> type[float]:
        return float

    def get_pydantic_type(self) -> Optional[Any]:
        """Return None to force custom validation for REAL."""
        # We need custom validation to handle MIN_POSITIVE and special error messages
        return None

    def validate(self, value: Any) -> None:
        """Override validate to always use custom validation."""
        if value is None:
            return
        self._validate_custom(value)

    def _validate_custom(self, value: Any) -> None:
        """Custom validation for REAL type."""
        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

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
