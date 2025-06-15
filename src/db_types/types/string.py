"""String database types."""

from typing import Any, Optional, Type

from db_types.types.base import DBType


class VARCHAR(DBType[str]):
    """Variable-length character string."""

    def __init__(self, length: int):
        super().__init__()
        if length <= 0:
            raise ValueError("VARCHAR length must be positive")
        self.length = length

    @property
    def sql_type(self) -> str:
        return f"VARCHAR({self.length})"

    @property
    def python_type(self) -> Type[str]:
        return str

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value).__name__}")

        if len(value) > self.length:
            raise ValueError(f"String length {len(value)} exceeds maximum {self.length}")

    def _serialize(self, value: str) -> str:
        return value

    def _deserialize(self, value: Any) -> str:
        return str(value)

    def __repr__(self) -> str:
        return f"VARCHAR({self.length})"


class CHAR(DBType[str]):
    """Fixed-length character string."""

    def __init__(self, length: int):
        super().__init__()
        if length <= 0:
            raise ValueError("CHAR length must be positive")
        self.length = length

    @property
    def sql_type(self) -> str:
        return f"CHAR({self.length})"

    @property
    def python_type(self) -> Type[str]:
        return str

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value).__name__}")

        if len(value) > self.length:
            raise ValueError(f"String length {len(value)} exceeds maximum {self.length}")

    def _serialize(self, value: str) -> str:
        # Pad with spaces to match CHAR behavior
        return value.ljust(self.length)

    def _deserialize(self, value: Any) -> str:
        # Strip trailing spaces to match typical CHAR retrieval
        return str(value).rstrip()

    def __repr__(self) -> str:
        return f"CHAR({self.length})"


class TEXT(DBType[str]):
    """Variable-length text with no specific upper limit."""

    def __init__(self, max_length: Optional[int] = None):
        super().__init__()
        self.max_length = max_length

    @property
    def sql_type(self) -> str:
        return "TEXT"

    @property
    def python_type(self) -> Type[str]:
        return str

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value).__name__}")

        if self.max_length and len(value) > self.max_length:
            raise ValueError(f"Text length {len(value)} exceeds maximum {self.max_length}")

    def _serialize(self, value: str) -> str:
        return value

    def _deserialize(self, value: Any) -> str:
        return str(value)

    def __repr__(self) -> str:
        if self.max_length:
            return f"TEXT(max_length={self.max_length})"
        return "TEXT()"
