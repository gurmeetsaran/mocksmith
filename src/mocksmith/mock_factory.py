"""Mock factory for automatic mock generation of dataclasses and Pydantic models."""

import enum
from dataclasses import MISSING, fields, is_dataclass
from typing import Any, TypeVar, Union, get_args, get_origin

from mocksmith.types.base import DBType

T = TypeVar("T")

# Create a singleton Faker instance to avoid repeated instantiation
try:
    from faker import Faker  # pyright: ignore[reportMissingImports]

    _fake = Faker()
except ImportError:
    _fake = None  # type: ignore[assignment]


def _get_faker() -> Any:
    """Get the Faker instance, raising an error if not available."""
    if _fake is None:
        raise ImportError(
            "faker library is required for mock generation. "
            "Install with: pip install mocksmith[mock]"
        )
    return _fake


def mock_factory(cls: type[T], **overrides: Any) -> T:
    """Generate a mock instance of a class with all fields populated.

    Args:
        cls: The class to generate a mock for
        **overrides: Field values to override in the mock

    Returns:
        Mock instance with all fields populated

    Raises:
        TypeError: If the class type is not supported
    """
    if is_dataclass(cls):
        return _mock_dataclass(cls, overrides)
    elif hasattr(cls, "model_fields"):  # Pydantic v2
        return _mock_pydantic_model(cls, overrides)
    elif hasattr(cls, "__fields__"):  # Pydantic v1
        return _mock_pydantic_model_v1(cls, overrides)
    else:
        raise TypeError(f"mock_factory only supports dataclasses and Pydantic models, got {cls}")


def _mock_dataclass(cls: type[T], overrides: dict[str, Any]) -> T:
    """Generate mock for a dataclass."""
    mock_data = {}

    for field in fields(cls):
        # Use override if provided
        if field.name in overrides:
            mock_data[field.name] = overrides[field.name]
            continue

        # Skip optional fields with defaults if they return None
        mock_value = _generate_field_mock(field.type, field.name)

        # Only include the field if it's required or has a non-None value
        if field.default is not MISSING and mock_value is None:
            # Field has a default and mock returned None, skip it
            continue

        mock_data[field.name] = mock_value

    return cls(**mock_data)


def _mock_pydantic_model(cls: type[T], overrides: dict[str, Any]) -> T:
    """Generate mock for a Pydantic v2 model."""
    mock_data = {}

    for field_name, field_info in cls.model_fields.items():
        # Use override if provided
        if field_name in overrides:
            mock_data[field_name] = overrides[field_name]
            continue

        # Check for DBTypeValidator in metadata first
        mock_value = None
        if hasattr(field_info, "metadata"):
            for metadata_item in field_info.metadata:
                if hasattr(metadata_item, "db_type") and isinstance(metadata_item.db_type, DBType):
                    mock_value = metadata_item.db_type.mock()
                    break

        # If no DBType found in metadata, use standard generation
        if mock_value is None:
            # Get the field type from annotation
            field_type = field_info.annotation
            mock_value = _generate_field_mock(field_type, field_name)

        mock_data[field_name] = mock_value

    return cls(**mock_data)


def _mock_pydantic_model_v1(cls: type[T], overrides: dict[str, Any]) -> T:
    """Generate mock for a Pydantic v1 model."""
    mock_data = {}

    for field_name, field in cls.__fields__.items():
        # Use override if provided
        if field_name in overrides:
            mock_data[field_name] = overrides[field_name]
            continue

        # Get the field type
        field_type = field.type_
        mock_data[field_name] = _generate_field_mock(field_type, field_name)

    return cls(**mock_data)


def _generate_field_mock(field_type: Any, field_name: str = "", _depth: int = 0) -> Any:
    """Generate mock value for a field based on its type.

    Args:
        field_type: The type annotation of the field
        field_name: The name of the field (used for smart generation)

    Returns:
        Mock value appropriate for the field type
    """
    # Get origin for type checking
    origin = get_origin(field_type)

    # Handle Optional types (Union with None) FIRST
    if origin is Union:
        args = get_args(field_type)
        if type(None) in args:
            # It's an Optional type
            inner_type = next(arg for arg in args if arg is not type(None))
            # For optional fields, sometimes return None
            if _get_faker().boolean(chance_of_getting_true=80):  # 80% chance of having a value
                return _generate_field_mock(inner_type, field_name, _depth + 1)
            return None

    # Handle Enum types
    if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
        # Get all enum values and pick one randomly
        enum_values = list(field_type)
        return _get_faker().random_element(enum_values)

    # Handle Annotated types (e.g., Annotated[str, VARCHAR(50)])
    if hasattr(field_type, "__metadata__"):  # It's an Annotated type
        # Get the actual type and metadata
        args = get_args(field_type)
        if args:
            actual_type = args[0]
            metadata = getattr(field_type, "__metadata__", ())

            # Look for DBType in metadata
            for item in metadata:
                if isinstance(item, DBType):
                    return item.mock()
                # Handle DBTypeValidator wrapper
                elif hasattr(item, "db_type") and isinstance(item.db_type, DBType):
                    return item.db_type.mock()

            # If no DBType found, continue with the actual type
            field_type = actual_type

    # Handle DBType classes directly
    if isinstance(field_type, type) and issubclass(field_type, DBType):
        # Need to instantiate it first - this won't work for types requiring args
        # Users should use instances or Annotated types instead
        raise TypeError(
            f"Cannot mock {field_type.__name__} class directly. "
            "Use an instance (e.g., VARCHAR(50)) or Annotated type instead."
        )

    # Handle DBType instances
    if isinstance(field_type, DBType):
        return field_type.mock()

    # Handle List types
    if origin is list:
        inner_type = get_args(field_type)[0] if get_args(field_type) else str
        count = _get_faker().random_int(min=1, max=5)
        return [_generate_field_mock(inner_type, field_name, _depth + 1) for _ in range(count)]

    # Handle Dict types
    if origin is dict:
        key_type, value_type = get_args(field_type) if get_args(field_type) else (str, str)
        count = _get_faker().random_int(min=1, max=3)
        return {
            _generate_field_mock(key_type, f"{field_name}_key", _depth + 1): _generate_field_mock(
                value_type, f"{field_name}_value", _depth + 1
            )
            for _ in range(count)
        }

    # Smart generation based on field name (only if we don't have a DBType)
    if field_name and not _depth:  # Only do smart generation at top level
        name_lower = field_name.lower()

        # Common patterns
        if field_type is str:
            if "email" in name_lower:
                return _get_faker().email()
            elif "phone" in name_lower:
                return _get_faker().phone_number()
            elif "url" in name_lower or "website" in name_lower:
                return _get_faker().url()
            elif "address" in name_lower:
                return _get_faker().address()
            elif "city" in name_lower:
                return _get_faker().city()
            elif "country" in name_lower:
                return _get_faker().country()
            elif "name" in name_lower:
                if "first" in name_lower:
                    return _get_faker().first_name()
                elif "last" in name_lower:
                    return _get_faker().last_name()
                elif "user" in name_lower:
                    return _get_faker().user_name()
                else:
                    return _get_faker().name()
            elif "description" in name_lower or "bio" in name_lower:
                return _get_faker().text(max_nb_chars=200)
            elif "title" in name_lower:
                return _get_faker().sentence(nb_words=4).rstrip(".")
            elif "password" in name_lower:
                return _get_faker().password()
            elif "token" in name_lower or "key" in name_lower:
                return _get_faker().sha256()
            elif "id" in name_lower and name_lower.endswith("id"):
                return _get_faker().uuid4()

    # Default generation for standard Python types

    if field_type is str:
        return _get_faker().word()
    elif field_type is int:
        return _get_faker().random_int()
    elif field_type is float:
        return _get_faker().random.random() * 100
    elif field_type is bool:
        return _get_faker().boolean()
    elif field_type.__name__ == "date":
        return _get_faker().date_object()
    elif field_type.__name__ == "datetime":
        return _get_faker().date_time()
    elif field_type.__name__ == "time":
        return _get_faker().time_object()
    elif field_type.__name__ == "Decimal":
        from decimal import Decimal

        return Decimal(str(_get_faker().pyfloat(left_digits=5, right_digits=2)))
    elif field_type is bytes:
        return _get_faker().binary(length=32)
    else:
        # Unknown type - return None
        return None
