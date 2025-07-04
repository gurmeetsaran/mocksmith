"""Numeric database types."""

from decimal import Decimal
from math import isfinite
from typing import Any, Optional, TypeVar, Union

from mocksmith.types.base import PYDANTIC_AVAILABLE, DBType

if PYDANTIC_AVAILABLE:
    from pydantic import condecimal, confloat, conint  # type: ignore[import-not-found]

T = TypeVar("T", Decimal, float)


class _BaseInteger(DBType[int]):
    """Base class for all integer types with constraint support.

    This provides common functionality for all integer types (TINYINT, SMALLINT, INTEGER, BIGINT).
    Subclasses only need to define MIN_VALUE, MAX_VALUE, and sql_type.
    """

    MIN_VALUE: int  # To be defined by subclasses
    MAX_VALUE: int  # To be defined by subclasses
    SQL_TYPE: str  # To be defined by subclasses

    def __init__(
        self,
        *,
        gt: Optional[int] = None,
        ge: Optional[int] = None,
        lt: Optional[int] = None,
        le: Optional[int] = None,
        multiple_of: Optional[int] = None,
        strict: bool = False,
        **pydantic_kwargs: Any,
    ):
        super().__init__()
        # Validate bounds against type limits
        type_name = self.__class__.__name__
        if ge is not None and ge < self.MIN_VALUE:
            raise ValueError(f"ge={ge} is below {type_name} minimum {self.MIN_VALUE}")
        if le is not None and le > self.MAX_VALUE:
            raise ValueError(f"le={le} exceeds {type_name} maximum {self.MAX_VALUE}")
        if gt is not None and gt >= self.MAX_VALUE:
            raise ValueError(f"gt={gt} leaves no valid {type_name} values")
        if lt is not None and lt <= self.MIN_VALUE:
            raise ValueError(f"lt={lt} leaves no valid {type_name} values")

        self.gt = gt
        self.ge = ge
        self.lt = lt
        self.le = le
        self.multiple_of = multiple_of
        self.strict = strict
        self.pydantic_kwargs = pydantic_kwargs

    @property
    def python_type(self) -> type[int]:
        return int

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type if available."""
        if PYDANTIC_AVAILABLE:
            # Apply INTEGER bounds and user constraints
            kwargs = {"strict": self.strict, **self.pydantic_kwargs}

            # Set bounds - user constraints take precedence
            if self.gt is not None:
                kwargs["gt"] = self.gt
            elif self.ge is not None:
                kwargs["ge"] = max(self.ge, self.MIN_VALUE)
            else:
                kwargs["ge"] = self.MIN_VALUE

            if self.lt is not None:
                kwargs["lt"] = self.lt
            elif self.le is not None:
                kwargs["le"] = min(self.le, self.MAX_VALUE)
            else:
                kwargs["le"] = self.MAX_VALUE

            if self.multiple_of is not None:
                kwargs["multiple_of"] = self.multiple_of

            return conint(**kwargs)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        if self.strict and not isinstance(value, int):
            raise ValueError(f"Expected int, got {type(value).__name__}")

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        if isinstance(value, float) and not value.is_integer():
            raise ValueError(f"Expected integer value, got float {value}")

        int_value = int(value)

        # Check type bounds
        if int_value < self.MIN_VALUE or int_value > self.MAX_VALUE:
            raise ValueError(f"Value {int_value} out of range for {self.__class__.__name__}")

        # Check user constraints
        if self.gt is not None and int_value <= self.gt:
            raise ValueError(f"Value must be greater than {self.gt}")
        if self.ge is not None and int_value < self.ge:
            raise ValueError(f"Value must be greater than or equal to {self.ge}")
        if self.lt is not None and int_value >= self.lt:
            raise ValueError(f"Value must be less than {self.lt}")
        if self.le is not None and int_value > self.le:
            raise ValueError(f"Value must be less than or equal to {self.le}")
        if self.multiple_of is not None and int_value % self.multiple_of != 0:
            raise ValueError(f"Value must be a multiple of {self.multiple_of}")

    def _serialize(self, value: Union[int, float]) -> int:
        return int(value)

    def _deserialize(self, value: Any) -> int:
        return int(value)

    @property
    def sql_type(self) -> str:
        """Return SQL type name."""
        return self.SQL_TYPE

    def __repr__(self) -> str:
        parts = [f"{self.__class__.__name__}("]
        params = []
        if self.gt is not None:
            params.append(f"gt={self.gt}")
        if self.ge is not None:
            params.append(f"ge={self.ge}")
        if self.lt is not None:
            params.append(f"lt={self.lt}")
        if self.le is not None:
            params.append(f"le={self.le}")
        if self.multiple_of is not None:
            params.append(f"multiple_of={self.multiple_of}")
        if self.strict:
            params.append("strict=True")
        if self.pydantic_kwargs:
            params.extend(f"{k}={v!r}" for k, v in self.pydantic_kwargs.items())

        return parts[0] + ", ".join(params) + ")"

    def _generate_mock(self, fake: Any) -> int:
        """Generate mock integer data respecting constraints."""
        # Determine effective bounds
        min_val = self.MIN_VALUE
        max_val = self.MAX_VALUE

        if self.gt is not None:
            min_val = max(min_val, self.gt + 1)
        elif self.ge is not None:
            min_val = max(min_val, self.ge)

        if self.lt is not None:
            max_val = min(max_val, self.lt - 1)
        elif self.le is not None:
            max_val = min(max_val, self.le)

        if min_val > max_val:
            raise ValueError("No valid values exist with given constraints")

        # For very large ranges, limit to reasonable values for faker
        # Faker can handle up to ~10^15 reliably
        faker_min = int(max(min_val, -1e15) if min_val < -1e15 else min_val)
        faker_max = int(min(max_val, 1e15) if max_val > 1e15 else max_val)

        if self.multiple_of is not None:
            # Adjust min to be a valid multiple
            if faker_min % self.multiple_of != 0:
                faker_min = faker_min + (self.multiple_of - faker_min % self.multiple_of)

            if faker_min > faker_max:
                raise ValueError(f"No valid multiples of {self.multiple_of} in range")

            # Use faker's step parameter for multiple_of
            return fake.random_int(min=faker_min, max=faker_max, step=self.multiple_of)
        else:
            return fake.random_int(min=faker_min, max=faker_max)


class _BaseNumeric(DBType[T]):
    """Base class for numeric types with constraint support.

    This provides common functionality for DECIMAL and FLOAT types.
    Subclasses need to implement specific validation and bounds calculation.
    """

    def __init__(
        self,
        *,
        gt: Optional[T] = None,
        ge: Optional[T] = None,
        lt: Optional[T] = None,
        le: Optional[T] = None,
        multiple_of: Optional[T] = None,
        strict: bool = False,
        **pydantic_kwargs: Any,
    ):
        super().__init__()
        self.gt = gt
        self.ge = ge
        self.lt = lt
        self.le = le
        self.multiple_of = multiple_of
        self.strict = strict
        self.pydantic_kwargs = pydantic_kwargs

    def _check_constraints(self, value: T, type_name: str) -> None:
        """Check user-defined constraints."""
        if self.gt is not None and value <= self.gt:
            raise ValueError(f"Value must be greater than {self.gt}")
        if self.ge is not None and value < self.ge:
            raise ValueError(f"Value must be greater than or equal to {self.ge}")
        if self.lt is not None and value >= self.lt:
            raise ValueError(f"Value must be less than {self.lt}")
        if self.le is not None and value > self.le:
            raise ValueError(f"Value must be less than or equal to {self.le}")

    def _get_effective_bounds(self, type_min: T, type_max: T) -> tuple[T, T]:
        """Calculate effective bounds based on type limits and user constraints."""
        min_val = type_min
        max_val = type_max

        if self.gt is not None:
            min_val = max(min_val, self._get_next_value(self.gt, True))
        elif self.ge is not None:
            min_val = max(min_val, self.ge)

        if self.lt is not None:
            max_val = min(max_val, self._get_next_value(self.lt, False))
        elif self.le is not None:
            max_val = min(max_val, self.le)

        if min_val > max_val:
            raise ValueError("No valid values exist with given constraints")

        return min_val, max_val

    def _get_next_value(self, value: T, increment: bool) -> T:
        """Get next representable value. Subclasses should override for type-specific logic."""
        raise NotImplementedError

    def __repr__(self) -> str:
        """Generate string representation with constraints."""
        class_name = self.__class__.__name__
        params = self._get_repr_params()

        constraint_params = []
        if self.gt is not None:
            constraint_params.append(f"gt={self.gt}")
        if self.ge is not None:
            constraint_params.append(f"ge={self.ge}")
        if self.lt is not None:
            constraint_params.append(f"lt={self.lt}")
        if self.le is not None:
            constraint_params.append(f"le={self.le}")
        if self.multiple_of is not None:
            constraint_params.append(f"multiple_of={self.multiple_of}")
        if self.strict:
            constraint_params.append("strict=True")
        if self.pydantic_kwargs:
            constraint_params.extend(f"{k}={v!r}" for k, v in self.pydantic_kwargs.items())

        all_params = params + constraint_params
        if all_params:
            return f"{class_name}({', '.join(all_params)})"
        return f"{class_name}()"

    def _get_repr_params(self) -> list[str]:
        """Get type-specific parameters for repr. Override in subclasses."""
        return []


class INTEGER(_BaseInteger):
    """32-bit integer type with optional constraints.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Examples:
        # Basic usage
        user_id: Integer()

        # With constraints
        positive_id: Integer(gt=0)
        small_count: Integer(ge=0, le=1000)
    """

    MIN_VALUE = -2147483648
    MAX_VALUE = 2147483647
    SQL_TYPE = "INTEGER"


class BIGINT(_BaseInteger):
    """64-bit integer type with optional constraints.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Examples:
        # Basic usage
        user_id: BigInt()

        # With constraints
        timestamp_ms: BigInt(gt=0)
        sequence_num: BigInt(ge=1, le=1000000)
    """

    MIN_VALUE = -9223372036854775808
    MAX_VALUE = 9223372036854775807
    SQL_TYPE = "BIGINT"


class SMALLINT(_BaseInteger):
    """16-bit integer type with optional constraints.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Examples:
        # Basic usage
        status_code: SmallInt()

        # With constraints
        priority: SmallInt(ge=1, le=10)
        level: SmallInt(gt=0, lt=100)
    """

    MIN_VALUE = -32768
    MAX_VALUE = 32767
    SQL_TYPE = "SMALLINT"


class TINYINT(_BaseInteger):
    """8-bit integer type with optional constraints.

    Args:
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Examples:
        # Basic usage
        flag: TinyInt()

        # With constraints
        percentage: TinyInt(ge=0, le=100)
        small_count: TinyInt(ge=0, lt=50)
    """

    MIN_VALUE = -128
    MAX_VALUE = 127
    SQL_TYPE = "TINYINT"


class DECIMAL(_BaseNumeric[Decimal]):
    """Fixed-point decimal type with optional constraints.

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

    Examples:
        # Basic usage
        price: DecimalType(10, 2)  # Up to 99999999.99

        # With constraints
        percentage: DecimalType(5, 2, ge=0, le=100)  # 0.00 to 100.00
        positive_amount: DecimalType(19, 4, gt=0)  # Positive money
    """

    def __init__(
        self,
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
    ):
        if precision <= 0:
            raise ValueError("Precision must be positive")
        if scale < 0:
            raise ValueError("Scale cannot be negative")
        if scale > precision:
            raise ValueError("Scale cannot exceed precision")

        self.precision = precision
        self.scale = scale

        # Convert to Decimal type
        super().__init__(
            gt=Decimal(str(gt)) if gt is not None else None,
            ge=Decimal(str(ge)) if ge is not None else None,
            lt=Decimal(str(lt)) if lt is not None else None,
            le=Decimal(str(le)) if le is not None else None,
            multiple_of=Decimal(str(multiple_of)) if multiple_of is not None else None,
            strict=strict,
            **pydantic_kwargs,
        )

    @property
    def sql_type(self) -> str:
        return f"DECIMAL({self.precision},{self.scale})"

    @property
    def python_type(self) -> type[Decimal]:
        return Decimal

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic condecimal type if available."""
        if PYDANTIC_AVAILABLE:
            kwargs = {
                "max_digits": self.precision,
                "decimal_places": self.scale,
                "strict": self.strict,
                **self.pydantic_kwargs,
            }

            # Calculate max value based on precision and scale
            max_digits = self.precision - self.scale
            if max_digits > 0:
                max_value = Decimal("9" * max_digits + "." + "9" * self.scale)
            else:
                max_value = Decimal("0." + "9" * self.scale)
            min_value = -max_value

            # Apply user constraints or type limits
            if self.gt is not None:
                kwargs["gt"] = self.gt
            elif self.ge is not None:
                kwargs["ge"] = max(self.ge, min_value)
            else:
                kwargs["ge"] = min_value

            if self.lt is not None:
                kwargs["lt"] = self.lt
            elif self.le is not None:
                kwargs["le"] = min(self.le, max_value)
            else:
                kwargs["le"] = max_value

            if self.multiple_of is not None:
                kwargs["multiple_of"] = self.multiple_of

            return condecimal(**kwargs)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        if self.strict and not isinstance(value, Decimal):
            raise ValueError(f"Expected Decimal, got {type(value).__name__}")

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

        # Check user constraints
        self._check_constraints(dec_value, "DECIMAL")
        if self.multiple_of is not None and dec_value % self.multiple_of != 0:
            raise ValueError(f"Value must be a multiple of {self.multiple_of}")

    def _serialize(self, value: Union[int, float, Decimal]) -> str:
        return str(Decimal(str(value)))

    def _deserialize(self, value: Any) -> Decimal:
        return Decimal(str(value))

    def _get_repr_params(self) -> list[str]:
        """Get DECIMAL-specific parameters for repr."""
        return [str(self.precision), str(self.scale)]

    def _get_next_value(self, value: Decimal, increment: bool) -> Decimal:
        """Get next representable Decimal value based on scale."""
        epsilon = Decimal(f"0.{'0' * (self.scale - 1)}1") if self.scale > 0 else Decimal("1")
        return value + epsilon if increment else value - epsilon

    def _generate_mock(self, fake: Any) -> Decimal:
        """Generate mock DECIMAL data respecting constraints."""
        # Calculate type bounds
        max_int_digits = self.precision - self.scale
        if max_int_digits > 0:
            type_max = Decimal("9" * max_int_digits + "." + "9" * self.scale)
        else:
            type_max = Decimal("0." + "9" * self.scale)
        type_min = -type_max

        # Use base class to get effective bounds
        min_val, max_val = self._get_effective_bounds(type_min, type_max)

        if self.multiple_of is not None:
            # Find valid multiples in range
            start_mult = int(min_val / self.multiple_of)
            if min_val > start_mult * self.multiple_of:
                start_mult += 1

            end_mult = int(max_val / self.multiple_of)
            if max_val < end_mult * self.multiple_of:
                end_mult -= 1

            if start_mult > end_mult:
                raise ValueError(f"No valid multiples of {self.multiple_of} in range")

            mult = fake.random_int(min=start_mult, max=end_mult)
            return self.multiple_of * mult
        else:
            # Use faker's pydecimal with min/max values
            value = fake.pydecimal(
                left_digits=max_int_digits if max_int_digits > 0 else None,
                right_digits=self.scale,
                positive=False,  # We handle sign via min_value/max_value
                min_value=float(min_val),
                max_value=float(max_val),
            )
            return value


class NUMERIC(DECIMAL):
    """Alias for DECIMAL."""

    @property
    def sql_type(self) -> str:
        return f"NUMERIC({self.precision},{self.scale})"


class FLOAT(_BaseNumeric[float]):
    """Double-precision floating-point type with optional constraints.

    Args:
        precision: SQL precision (optional)
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        multiple_of: Value must be a multiple of this
        allow_inf_nan: Whether to allow inf/-inf/nan values (default: False)
        strict: In strict mode, types won't be coerced
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Examples:
        # Basic usage
        temperature: Float()

        # With constraints
        percentage: Float(ge=0.0, le=100.0)
        probability: Float(ge=0.0, le=1.0)
        positive_value: Float(gt=0.0)
    """

    def __init__(
        self,
        precision: Optional[int] = None,
        *,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = None,
        allow_inf_nan: bool = False,
        strict: bool = False,
        **pydantic_kwargs: Any,
    ):
        self.precision = precision
        self.allow_inf_nan = allow_inf_nan
        super().__init__(
            gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of, strict=strict, **pydantic_kwargs
        )

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
            kwargs = {
                "strict": self.strict,
                "allow_inf_nan": self.allow_inf_nan,
                **self.pydantic_kwargs,
            }

            if self.gt is not None:
                kwargs["gt"] = self.gt
            if self.ge is not None:
                kwargs["ge"] = self.ge
            if self.lt is not None:
                kwargs["lt"] = self.lt
            if self.le is not None:
                kwargs["le"] = self.le
            if self.multiple_of is not None:
                kwargs["multiple_of"] = self.multiple_of

            return confloat(**kwargs)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        if self.strict and not isinstance(value, float):
            raise ValueError(f"Expected float, got {type(value).__name__}")

        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value).__name__}")

        float_value = float(value)

        if not self.allow_inf_nan and not isfinite(float_value):
            raise ValueError(f"Value must be finite, got {float_value}")

        if isfinite(float_value):  # Only check constraints for finite values
            self._check_constraints(float_value, "FLOAT")
            if self.multiple_of is not None:
                # For floats, check if value/multiple_of is close to an integer
                quotient = float_value / self.multiple_of
                if not abs(quotient - round(quotient)) < 1e-9:
                    raise ValueError(f"Value must be a multiple of {self.multiple_of}")

    def _serialize(self, value: Union[int, float]) -> float:
        return float(value)

    def _deserialize(self, value: Any) -> float:
        return float(value)

    def _get_repr_params(self) -> list[str]:
        """Get FLOAT-specific parameters for repr."""
        params = []
        if self.precision is not None:
            params.append(str(self.precision))
        if self.allow_inf_nan:
            # Add to constraint params instead
            if not hasattr(self, "_extra_params"):
                self._extra_params = []
            self._extra_params.append("allow_inf_nan=True")
        return params

    def __repr__(self) -> str:
        """Override to include allow_inf_nan."""
        class_name = self.__class__.__name__
        params = self._get_repr_params()

        constraint_params = []
        if self.gt is not None:
            constraint_params.append(f"gt={self.gt}")
        if self.ge is not None:
            constraint_params.append(f"ge={self.ge}")
        if self.lt is not None:
            constraint_params.append(f"lt={self.lt}")
        if self.le is not None:
            constraint_params.append(f"le={self.le}")
        if self.multiple_of is not None:
            constraint_params.append(f"multiple_of={self.multiple_of}")
        if self.allow_inf_nan:
            constraint_params.append("allow_inf_nan=True")
        if self.strict:
            constraint_params.append("strict=True")
        if self.pydantic_kwargs:
            constraint_params.extend(f"{k}={v!r}" for k, v in self.pydantic_kwargs.items())

        all_params = params + constraint_params
        if all_params:
            return f"{class_name}({', '.join(all_params)})"
        return f"{class_name}()"

    def _get_next_value(self, value: float, increment: bool) -> float:
        """Get next representable float value."""
        import math

        return math.nextafter(value, float("inf") if increment else float("-inf"))

    def _generate_mock(self, fake: Any) -> float:
        """Generate mock FLOAT data respecting constraints."""
        # Use base class to get effective bounds
        min_val, max_val = self._get_effective_bounds(float("-inf"), float("inf"))

        # Handle infinity cases - faker needs finite bounds
        if min_val == float("-inf"):
            min_val = -1e10
        if max_val == float("inf"):
            max_val = 1e10

        if self.multiple_of is not None:
            # For floats with multiple_of, generate integer multiples
            min_mult = int(min_val / self.multiple_of)
            max_mult = int(max_val / self.multiple_of)

            # Adjust bounds to ensure we're within range
            if min_mult * self.multiple_of < min_val:
                min_mult += 1
            if max_mult * self.multiple_of > max_val:
                max_mult -= 1

            if min_mult > max_mult:
                raise ValueError(f"No valid multiples of {self.multiple_of} in range")

            mult = fake.random_int(min=min_mult, max=max_mult)
            return float(mult * self.multiple_of)
        else:
            # Use faker's pyfloat with min/max values
            return fake.pyfloat(min_value=min_val, max_value=max_val)


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
