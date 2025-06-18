"""Type-safe builder pattern for mock data generation."""

from dataclasses import fields, is_dataclass
from typing import Any, Dict, Generic, List, Type, TypeVar

T = TypeVar("T")


class MockBuilder(Generic[T]):
    """Type-safe builder for generating mock data with field overrides.
    
    This builder provides IDE support and type checking for field overrides.
    """

    def __init__(self, target_class: Type[T]):
        """Initialize the builder for a specific class.
        
        Args:
            target_class: The class to build mocks for
        """
        self._target_class = target_class
        self._overrides: Dict[str, Any] = {}

        # Dynamically create setter methods for each field
        self._setup_fields()

    def _setup_fields(self) -> None:
        """Set up dynamic setter methods for all fields."""
        if is_dataclass(self._target_class):
            # Handle dataclasses
            for field in fields(self._target_class):
                self._create_setter(field.name, field.type)
        elif hasattr(self._target_class, "model_fields"):  # Pydantic v2
            # Handle Pydantic v2 models
            for field_name, field_info in self._target_class.model_fields.items():
                self._create_setter(field_name, field_info.annotation)
        elif hasattr(self._target_class, "__fields__"):  # Pydantic v1
            # Handle Pydantic v1 models
            for field_name, field in self._target_class.__fields__.items():
                self._create_setter(field_name, field.type_)

    def _create_setter(self, field_name: str, field_type: type) -> None:
        """Create a setter method for a field.
        
        Args:
            field_name: Name of the field
            field_type: Type of the field
        """
        def setter(self, value: Any) -> "MockBuilder[T]":
            """Set the value for this field."""
            self._overrides[field_name] = value
            return self

        # Create method name
        setter_name = f"with_{field_name}"

        # Set the method on the instance
        setter.__name__ = setter_name
        setter.__annotations__ = {"value": field_type, "return": MockBuilder[T]}
        setattr(self, setter_name, setter.__get__(self, MockBuilder))

    def with_values(self, **kwargs: Any) -> "MockBuilder[T]":
        """Set multiple field values at once.
        
        Args:
            **kwargs: Field names and values to set
            
        Returns:
            Self for method chaining
        """
        for key, value in kwargs.items():
            if hasattr(self, f"with_{key}"):
                getattr(self, f"with_{key}")(value)
            else:
                raise AttributeError(f"No field named '{key}' in {self._target_class.__name__}")
        return self

    def build(self) -> T:
        """Build the mock instance with all overrides applied.
        
        Returns:
            Mock instance of the target class
        """
        from db_types.mock_factory import mock_factory
        return mock_factory(self._target_class, **self._overrides)

    def build_many(self, count: int) -> List[T]:
        """Build multiple mock instances with the same overrides.
        
        Args:
            count: Number of instances to build
            
        Returns:
            List of mock instances
        """
        return [self.build() for _ in range(count)]
