"""Base database type class."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")

# Try to import Pydantic validators
try:
    from pydantic import TypeAdapter, ValidationError  # type: ignore[import-not-found]

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    ValidationError = ValueError  # type: ignore
    TypeAdapter = None  # type: ignore


class DBType(ABC, Generic[T]):
    """Base class for all database types."""

    def __init__(self):
        self._python_type: Optional[type[T]] = None
        self._type_adapter: Optional[Any] = None

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

    def get_pydantic_type(self) -> Optional[Any]:
        """
        Get the Pydantic type annotation for this type.

        Subclasses should override this to return appropriate Pydantic type
        annotations (constr, conint, etc.) when PYDANTIC_AVAILABLE is True.

        Returns:
            Pydantic type annotation or None
        """
        return None

    def validate(self, value: Any) -> None:
        """
        Validate the value using Pydantic validator if available,
        otherwise fall back to custom validation.

        Args:
            value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        if value is None:
            return

        # Try to use Pydantic TypeAdapter if available
        if PYDANTIC_AVAILABLE and TypeAdapter is not None:
            if self._type_adapter is None:
                pydantic_type = self.get_pydantic_type()
                if pydantic_type is not None:
                    self._type_adapter = TypeAdapter(pydantic_type)

            if self._type_adapter is not None:
                try:
                    # Use TypeAdapter to validate
                    self._type_adapter.validate_python(value)
                except ValidationError as e:
                    # Convert Pydantic validation error to ValueError for consistency
                    errors = e.errors()
                    if errors:
                        msg = errors[0].get("msg", str(e))
                        raise ValueError(msg) from e
                    raise ValueError(str(e)) from e
                except ValueError as e:
                    raise e
                return

        # Fall back to custom validation
        self._validate_custom(value)

    @abstractmethod
    def _validate_custom(self, value: Any) -> None:
        """
        Custom validation logic as fallback when Pydantic is not available.

        This should implement the same validation rules as the Pydantic validator.

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

    def mock(self) -> T:
        """Generate mock data for this type.

        Returns:
            Mock value of the appropriate type

        Raises:
            ImportError: If faker is not installed
        """
        try:
            from faker import Faker  # pyright: ignore[reportMissingImports]

            fake = Faker()
            return self._generate_mock(fake)
        except ImportError as e:
            raise ImportError(
                "faker is required for mock generation. "
                "Install with: pip install python-db-types[mock]"
            ) from e

    def _generate_mock(self, fake: Any) -> T:
        """Generate type-specific mock data.

        Args:
            fake: Faker instance

        Returns:
            Mock value
        """
        # Default implementation based on python_type
        py_type = self.python_type

        if py_type is str:
            return fake.word()
        elif py_type is int:
            return fake.random_int()
        elif py_type is float:
            return fake.random.random() * 1000
        elif py_type is bool:
            return fake.boolean()
        elif py_type.__name__ == "Decimal":
            from decimal import Decimal

            return Decimal(str(fake.pyfloat(left_digits=5, right_digits=2, positive=True)))  # type: ignore[return-value]
        elif py_type.__name__ == "date":
            return fake.date_object()
        elif py_type.__name__ == "time":
            return fake.time_object()
        elif py_type.__name__ == "datetime":
            return fake.date_time()
        elif py_type is bytes:
            return fake.binary(length=10)
        else:
            # Fallback - try to instantiate with a random value
            try:
                if callable(py_type):
                    return py_type(fake.random_int())  # pyright: ignore[reportCallIssue]
                else:
                    raise NotImplementedError(f"No default mock implementation for {py_type}")
            except Exception as e:
                raise NotImplementedError(f"No default mock implementation for {py_type}") from e

    # Support for type annotations
    @classmethod
    def __class_getitem__(cls, params):
        """Support for generic type annotations like VARCHAR[50]."""
        # This is for type hints only, not for instantiation
        return cls
