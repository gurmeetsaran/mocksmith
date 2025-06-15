"""Numeric database types."""

from decimal import Decimal
from typing import Optional, Type, Union

from db_types.types.base import DBType


class INTEGER(DBType[int]):
    """32-bit integer type."""

    MIN_VALUE = -2147483648
    MAX_VALUE = 2147483647

    @property
    def sql_type(self) -> str:
        return "INTEGER"

    @property
    def python_type(self) -> Type[int]:
        return int

    def validate(self, value: any) -> None:
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

    def _deserialize(self, value: any) -> int:
        return int(value)


class BIGINT(DBType[int]):
    """64-bit integer type."""

    MIN_VALUE = -9223372036854775808
    MAX_VALUE = 9223372036854775807

    @property
    def sql_type(self) -> str:
        return "BIGINT"

    @property
    def python_type(self) -> Type[int]:
        return int

    def validate(self, value: any) -> None:
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

    def _deserialize(self, value: any) -> int:
        return int(value)


class SMALLINT(DBType[int]):
    """16-bit integer type."""

    MIN_VALUE = -32768
    MAX_VALUE = 32767

    @property
    def sql_type(self) -> str:
        return "SMALLINT"

    @property
    def python_type(self) -> Type[int]:
        return int

    def validate(self, value: any) -> None:
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

    def _deserialize(self, value: any) -> int:
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
    def python_type(self) -> Type[Decimal]:
        return Decimal

    def validate(self, value: any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float, Decimal, str)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        try:
            dec_value = Decimal(str(value))
        except Exception as e:
            raise ValueError(f"Cannot convert {value} to Decimal: {e}")

        # Check precision and scale
        sign, digits, exponent = dec_value.as_tuple()

        # Total digits
        total_digits = len(digits)
        if total_digits > self.precision:
            raise ValueError(f"Value has {total_digits} digits, exceeds precision {self.precision}")

        # Decimal places
        decimal_places = -exponent if exponent < 0 else 0
        if decimal_places > self.scale:
            raise ValueError(f"Value has {decimal_places} decimal places, exceeds scale {self.scale}")

    def _serialize(self, value: Union[int, float, Decimal, str]) -> str:
        return str(Decimal(str(value)))

    def _deserialize(self, value: any) -> Decimal:
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
    def python_type(self) -> Type[float]:
        return float

    def validate(self, value: any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

    def _serialize(self, value: Union[int, float]) -> float:
        return float(value)

    def _deserialize(self, value: any) -> float:
        return float(value)


class REAL(DBType[float]):
    """Single precision floating-point number."""

    @property
    def sql_type(self) -> str:
        return "REAL"

    @property
    def python_type(self) -> Type[float]:
        return float

    def validate(self, value: any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

    def _serialize(self, value: Union[int, float]) -> float:
        return float(value)

    def _deserialize(self, value: any) -> float:
        return float(value)


class DOUBLE(DBType[float]):
    """Double precision floating-point number."""

    @property
    def sql_type(self) -> str:
        return "DOUBLE PRECISION"

    @property
    def python_type(self) -> Type[float]:
        return float

    def validate(self, value: any) -> None:
        if value is None:
            return

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

    def _serialize(self, value: Union[int, float]) -> float:
        return float(value)

    def _deserialize(self, value: any) -> float:
        return float(value)
