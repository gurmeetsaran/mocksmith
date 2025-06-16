"""Base database type class."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class DBType(ABC, Generic[T]):
    """Base class for all database types."""

    def __init__(self):
        self._python_type: Optional[type[T]] = None

    @property
    @abstractmethod
    def sql_type(self) -> str:
        """Return SQL type representation."""
        pass

    @property
    @abstractmethod
    def python_type(self) -> type[T]:
        """Return the corresponding Python type."""
        pass

    @abstractmethod
    def validate(self, value: Any) -> None:
        """Validate the value against type constraints.

        Args:
            value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        pass

    def serialize(self, value: Any) -> Any:
        """Serialize Python value to database-compatible format.

        Args:
            value: Python value to serialize

        Returns:
            Serialized value
        """
        if value is None:
            return None

        self.validate(value)
        return self._serialize(value)

    def deserialize(self, value: Any) -> Optional[T]:
        """Deserialize database value to Python type.

        Args:
            value: Database value to deserialize

        Returns:
            Python value
        """
        if value is None:
            return None

        deserialized = self._deserialize(value)
        self.validate(deserialized)
        return deserialized

    @abstractmethod
    def _serialize(self, value: T) -> Any:
        """Internal serialization method."""
        pass

    @abstractmethod
    def _deserialize(self, value: Any) -> T:
        """Internal deserialization method."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    # Support for type annotations
    @classmethod
    def __class_getitem__(cls, params):
        """Support for generic type annotations like VARCHAR[50]."""
        # This is for type hints only, not for instantiation
        return cls
