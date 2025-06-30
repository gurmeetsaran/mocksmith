"""Constrained numeric types with validation rules."""

from typing import Any, Optional

from mocksmith.types.base import PYDANTIC_AVAILABLE
from mocksmith.types.numeric import BIGINT, INTEGER, SMALLINT, TINYINT

if PYDANTIC_AVAILABLE:
    from pydantic import conint


class ConstrainedInteger(INTEGER):
    """Integer type with customizable constraints."""

    def __init__(
        self,
        *,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        multiple_of: Optional[int] = None,
        positive: bool = False,
        negative: bool = False,
    ):
        super().__init__()

        # Handle positive/negative shortcuts
        if positive and negative:
            raise ValueError("Cannot be both positive and negative")

        if positive:
            min_value = max(1, min_value or 1)
        elif negative:
            max_value = min(-1, max_value or -1)

        # Set bounds
        self.min_value = min_value if min_value is not None else self.MIN_VALUE
        self.max_value = max_value if max_value is not None else self.MAX_VALUE

        # Validate bounds
        if self.min_value > self.max_value:
            raise ValueError(
                f"min_value ({self.min_value}) cannot be greater than "
                f"max_value ({self.max_value})"
            )

        if self.min_value < self.MIN_VALUE:
            raise ValueError(
                f"min_value ({self.min_value}) is below INTEGER minimum ({self.MIN_VALUE})"
            )

        if self.max_value > self.MAX_VALUE:
            raise ValueError(
                f"max_value ({self.max_value}) exceeds INTEGER maximum ({self.MAX_VALUE})"
            )

        self.multiple_of = multiple_of
        if multiple_of is not None and multiple_of <= 0:
            raise ValueError("multiple_of must be positive")

    @property
    def sql_type(self) -> str:
        # Add CHECK constraints for SQL
        constraints = []
        base = "INTEGER"

        if self.min_value != self.MIN_VALUE:
            constraints.append(f">= {self.min_value}")
        if self.max_value != self.MAX_VALUE:
            constraints.append(f"<= {self.max_value}")
        if self.multiple_of is not None:
            constraints.append(f"% {self.multiple_of} = 0")

        if constraints:
            check = " AND ".join(constraints)
            return f"{base} CHECK ({check})"
        return base

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type with constraints if available."""
        if PYDANTIC_AVAILABLE:
            return conint(ge=self.min_value, le=self.max_value, multiple_of=self.multiple_of)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        # First do base validation
        super()._validate_custom(value)

        int_value = int(value)

        # Check custom bounds
        if int_value < self.min_value:
            raise ValueError(f"Value {int_value} is below minimum {self.min_value}")

        if int_value > self.max_value:
            raise ValueError(f"Value {int_value} exceeds maximum {self.max_value}")

        # Check multiple_of
        if self.multiple_of is not None and int_value % self.multiple_of != 0:
            raise ValueError(f"Value {int_value} is not a multiple of {self.multiple_of}")

    def __repr__(self) -> str:
        parts = ["ConstrainedInteger"]
        attrs = []

        if self.min_value != self.MIN_VALUE:
            attrs.append(f"min_value={self.min_value}")
        if self.max_value != self.MAX_VALUE:
            attrs.append(f"max_value={self.max_value}")
        if self.multiple_of is not None:
            attrs.append(f"multiple_of={self.multiple_of}")

        if attrs:
            parts.append(f"({', '.join(attrs)})")
        else:
            parts.append("()")

        return "".join(parts)

    def _generate_mock(self, fake: Any) -> int:
        """Generate mock data respecting constraints."""
        # Adjust bounds for multiple_of
        min_val = self.min_value
        max_val = self.max_value

        if self.multiple_of:
            # Find the smallest valid value >= min_value
            if min_val % self.multiple_of != 0:
                min_val = min_val + (self.multiple_of - min_val % self.multiple_of)

            # Find the largest valid value <= max_value
            if max_val % self.multiple_of != 0:
                max_val = max_val - (max_val % self.multiple_of)

            # Generate a random multiplier
            min_mult = min_val // self.multiple_of
            max_mult = max_val // self.multiple_of

            if min_mult > max_mult:
                raise ValueError("No valid values exist with given constraints")

            multiplier = fake.random_int(min=min_mult, max=max_mult)
            return multiplier * self.multiple_of
        else:
            return fake.random_int(min=min_val, max=max_val)


# Convenience classes for common constraints
class PositiveInteger(ConstrainedInteger):
    """Integer constrained to positive values (> 0)."""

    def __init__(self, **kwargs):
        kwargs["positive"] = True
        super().__init__(**kwargs)


class NonNegativeInteger(ConstrainedInteger):
    """Integer constrained to non-negative values (>= 0)."""

    def __init__(self, **kwargs):
        kwargs["min_value"] = max(0, kwargs.get("min_value", 0))
        super().__init__(**kwargs)


class NegativeInteger(ConstrainedInteger):
    """Integer constrained to negative values (< 0)."""

    def __init__(self, **kwargs):
        kwargs["negative"] = True
        super().__init__(**kwargs)


class NonPositiveInteger(ConstrainedInteger):
    """Integer constrained to non-positive values (<= 0)."""

    def __init__(self, **kwargs):
        kwargs["max_value"] = min(0, kwargs.get("max_value", 0))
        super().__init__(**kwargs)


# Similar constrained types for other integer sizes
class ConstrainedBigInt(BIGINT):
    """BIGINT type with customizable constraints."""

    def __init__(
        self,
        *,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        multiple_of: Optional[int] = None,
        positive: bool = False,
        negative: bool = False,
    ):
        super().__init__()

        if positive and negative:
            raise ValueError("Cannot be both positive and negative")

        if positive:
            min_value = max(1, min_value or 1)
        elif negative:
            max_value = min(-1, max_value or -1)

        self.min_value = min_value if min_value is not None else self.MIN_VALUE
        self.max_value = max_value if max_value is not None else self.MAX_VALUE

        if self.min_value > self.max_value:
            raise ValueError(
                f"min_value ({self.min_value}) cannot be greater than "
                f"max_value ({self.max_value})"
            )

        if self.min_value < self.MIN_VALUE:
            raise ValueError(
                f"min_value ({self.min_value}) is below BIGINT minimum ({self.MIN_VALUE})"
            )

        if self.max_value > self.MAX_VALUE:
            raise ValueError(
                f"max_value ({self.max_value}) exceeds BIGINT maximum ({self.MAX_VALUE})"
            )

        self.multiple_of = multiple_of
        if multiple_of is not None and multiple_of <= 0:
            raise ValueError("multiple_of must be positive")

    @property
    def sql_type(self) -> str:
        constraints = []
        base = "BIGINT"

        if self.min_value != self.MIN_VALUE:
            constraints.append(f">= {self.min_value}")
        if self.max_value != self.MAX_VALUE:
            constraints.append(f"<= {self.max_value}")
        if self.multiple_of is not None:
            constraints.append(f"% {self.multiple_of} = 0")

        if constraints:
            check = " AND ".join(constraints)
            return f"{base} CHECK ({check})"
        return base

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type with constraints if available."""
        if PYDANTIC_AVAILABLE:
            return conint(ge=self.min_value, le=self.max_value, multiple_of=self.multiple_of)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        super()._validate_custom(value)

        int_value = int(value)

        if int_value < self.min_value:
            raise ValueError(f"Value {int_value} is below minimum {self.min_value}")

        if int_value > self.max_value:
            raise ValueError(f"Value {int_value} exceeds maximum {self.max_value}")

        if self.multiple_of is not None and int_value % self.multiple_of != 0:
            raise ValueError(f"Value {int_value} is not a multiple of {self.multiple_of}")


class ConstrainedSmallInt(SMALLINT):
    """SMALLINT type with customizable constraints."""

    def __init__(
        self,
        *,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        multiple_of: Optional[int] = None,
        positive: bool = False,
        negative: bool = False,
    ):
        super().__init__()

        if positive and negative:
            raise ValueError("Cannot be both positive and negative")

        if positive:
            min_value = max(1, min_value or 1)
        elif negative:
            max_value = min(-1, max_value or -1)

        self.min_value = min_value if min_value is not None else self.MIN_VALUE
        self.max_value = max_value if max_value is not None else self.MAX_VALUE

        if self.min_value > self.max_value:
            raise ValueError(
                f"min_value ({self.min_value}) cannot be greater than "
                f"max_value ({self.max_value})"
            )

        if self.min_value < self.MIN_VALUE:
            raise ValueError(
                f"min_value ({self.min_value}) is below SMALLINT minimum ({self.MIN_VALUE})"
            )

        if self.max_value > self.MAX_VALUE:
            raise ValueError(
                f"max_value ({self.max_value}) exceeds SMALLINT maximum ({self.MAX_VALUE})"
            )

        self.multiple_of = multiple_of
        if multiple_of is not None and multiple_of <= 0:
            raise ValueError("multiple_of must be positive")

    @property
    def sql_type(self) -> str:
        constraints = []
        base = "SMALLINT"

        if self.min_value != self.MIN_VALUE:
            constraints.append(f">= {self.min_value}")
        if self.max_value != self.MAX_VALUE:
            constraints.append(f"<= {self.max_value}")
        if self.multiple_of is not None:
            constraints.append(f"% {self.multiple_of} = 0")

        if constraints:
            check = " AND ".join(constraints)
            return f"{base} CHECK ({check})"
        return base

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type with constraints if available."""
        if PYDANTIC_AVAILABLE:
            return conint(ge=self.min_value, le=self.max_value, multiple_of=self.multiple_of)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        super()._validate_custom(value)

        int_value = int(value)

        if int_value < self.min_value:
            raise ValueError(f"Value {int_value} is below minimum {self.min_value}")

        if int_value > self.max_value:
            raise ValueError(f"Value {int_value} exceeds maximum {self.max_value}")

        if self.multiple_of is not None and int_value % self.multiple_of != 0:
            raise ValueError(f"Value {int_value} is not a multiple of {self.multiple_of}")


class ConstrainedTinyInt(TINYINT):
    """TINYINT type with customizable constraints."""

    def __init__(
        self,
        *,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        multiple_of: Optional[int] = None,
        positive: bool = False,
        negative: bool = False,
    ):
        super().__init__()

        if positive and negative:
            raise ValueError("Cannot be both positive and negative")

        if positive:
            min_value = max(1, min_value or 1)
        elif negative:
            max_value = min(-1, max_value or -1)

        self.min_value = min_value if min_value is not None else self.MIN_VALUE
        self.max_value = max_value if max_value is not None else self.MAX_VALUE

        if self.min_value > self.max_value:
            raise ValueError(
                f"min_value ({self.min_value}) cannot be greater than "
                f"max_value ({self.max_value})"
            )

        if self.min_value < self.MIN_VALUE:
            raise ValueError(
                f"min_value ({self.min_value}) is below TINYINT minimum ({self.MIN_VALUE})"
            )

        if self.max_value > self.MAX_VALUE:
            raise ValueError(
                f"max_value ({self.max_value}) exceeds TINYINT maximum ({self.MAX_VALUE})"
            )

        self.multiple_of = multiple_of
        if multiple_of is not None and multiple_of <= 0:
            raise ValueError("multiple_of must be positive")

    @property
    def sql_type(self) -> str:
        constraints = []
        base = "TINYINT"

        if self.min_value != self.MIN_VALUE:
            constraints.append(f">= {self.min_value}")
        if self.max_value != self.MAX_VALUE:
            constraints.append(f"<= {self.max_value}")
        if self.multiple_of is not None:
            constraints.append(f"% {self.multiple_of} = 0")

        if constraints:
            check = " AND ".join(constraints)
            return f"{base} CHECK ({check})"
        return base

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic conint type with constraints if available."""
        if PYDANTIC_AVAILABLE:
            return conint(ge=self.min_value, le=self.max_value, multiple_of=self.multiple_of)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        super()._validate_custom(value)

        int_value = int(value)

        if int_value < self.min_value:
            raise ValueError(f"Value {int_value} is below minimum {self.min_value}")

        if int_value > self.max_value:
            raise ValueError(f"Value {int_value} exceeds maximum {self.max_value}")

        if self.multiple_of is not None and int_value % self.multiple_of != 0:
            raise ValueError(f"Value {int_value} is not a multiple of {self.multiple_of}")
