"""Constrained numeric types with validation rules."""

from typing import Any, Optional

from db_types.types.numeric import BIGINT, INTEGER, SMALLINT


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
                f"min_value ({self.min_value}) is below INTEGER " f"minimum ({self.MIN_VALUE})"
            )

        if self.max_value > self.MAX_VALUE:
            raise ValueError(
                f"max_value ({self.max_value}) exceeds INTEGER " f"maximum ({self.MAX_VALUE})"
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

    def validate(self, value: Any) -> None:
        # First do base validation
        super().validate(value)

        if value is None:
            return

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

        return "".join(parts)


class PositiveInteger(ConstrainedInteger):
    """Integer type that only accepts positive values (> 0)."""

    def __init__(
        self,
        *,
        max_value: Optional[int] = None,
        multiple_of: Optional[int] = None,
    ):
        super().__init__(
            positive=True,
            max_value=max_value,
            multiple_of=multiple_of,
        )

    def __repr__(self) -> str:
        return "PositiveInteger()"


class NegativeInteger(ConstrainedInteger):
    """Integer type that only accepts negative values (< 0)."""

    def __init__(
        self,
        *,
        min_value: Optional[int] = None,
        multiple_of: Optional[int] = None,
    ):
        super().__init__(
            negative=True,
            min_value=min_value,
            multiple_of=multiple_of,
        )

    def __repr__(self) -> str:
        return "NegativeInteger()"


class NonNegativeInteger(ConstrainedInteger):
    """Integer type that accepts zero and positive values (>= 0)."""

    def __init__(
        self,
        *,
        max_value: Optional[int] = None,
        multiple_of: Optional[int] = None,
    ):
        super().__init__(
            min_value=0,
            max_value=max_value,
            multiple_of=multiple_of,
        )

    def __repr__(self) -> str:
        return "NonNegativeInteger()"


class NonPositiveInteger(ConstrainedInteger):
    """Integer type that accepts zero and negative values (<= 0)."""

    def __init__(
        self,
        *,
        min_value: Optional[int] = None,
        multiple_of: Optional[int] = None,
    ):
        super().__init__(
            min_value=min_value,
            max_value=0,
            multiple_of=multiple_of,
        )

    def __repr__(self) -> str:
        return "NonPositiveInteger()"


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
                f"min_value ({self.min_value}) is below BIGINT " f"minimum ({self.MIN_VALUE})"
            )

        if self.max_value > self.MAX_VALUE:
            raise ValueError(
                f"max_value ({self.max_value}) exceeds BIGINT " f"maximum ({self.MAX_VALUE})"
            )

        self.multiple_of = multiple_of
        if multiple_of is not None and multiple_of <= 0:
            raise ValueError("multiple_of must be positive")

    @property
    def sql_type(self) -> str:
        # Add CHECK constraints for SQL
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

    def validate(self, value: Any) -> None:
        # First do base validation
        super().validate(value)

        if value is None:
            return

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
        parts = ["ConstrainedBigInt"]
        attrs = []

        if self.min_value != self.MIN_VALUE:
            attrs.append(f"min_value={self.min_value}")
        if self.max_value != self.MAX_VALUE:
            attrs.append(f"max_value={self.max_value}")
        if self.multiple_of is not None:
            attrs.append(f"multiple_of={self.multiple_of}")

        if attrs:
            parts.append(f"({', '.join(attrs)})")

        return "".join(parts)


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
                f"min_value ({self.min_value}) is below SMALLINT " f"minimum ({self.MIN_VALUE})"
            )

        if self.max_value > self.MAX_VALUE:
            raise ValueError(
                f"max_value ({self.max_value}) exceeds SMALLINT " f"maximum ({self.MAX_VALUE})"
            )

        self.multiple_of = multiple_of
        if multiple_of is not None and multiple_of <= 0:
            raise ValueError("multiple_of must be positive")

    @property
    def sql_type(self) -> str:
        # Add CHECK constraints for SQL
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

    def validate(self, value: Any) -> None:
        # First do base validation
        super().validate(value)

        if value is None:
            return

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
        parts = ["ConstrainedSmallInt"]
        attrs = []

        if self.min_value != self.MIN_VALUE:
            attrs.append(f"min_value={self.min_value}")
        if self.max_value != self.MAX_VALUE:
            attrs.append(f"max_value={self.max_value}")
        if self.multiple_of is not None:
            attrs.append(f"multiple_of={self.multiple_of}")

        if attrs:
            parts.append(f"({', '.join(attrs)})")

        return "".join(parts)
