"""Mock factory for automatic mock generation of dataclasses and Pydantic models."""

import enum
import warnings
from dataclasses import MISSING, fields, is_dataclass
from typing import Any, Literal, TypeVar, Union, get_args, get_origin

try:
    from typing import Annotated
except ImportError:
    from typing import Annotated

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


def _handle_unsupported_type(field_type: Any, field_name: str = "") -> Any:
    """Handle unsupported types by attempting to create instances or provide defaults.

    Args:
        field_type: The unsupported type
        field_name: The field name (for context)

    Returns:
        A mock value or None
    """
    type_name = getattr(field_type, "__name__", str(field_type))

    # Special handling for common types
    if type_name == "Path" or "path" in type_name.lower():
        # For pathlib.Path - try to return actual Path object
        try:
            import pathlib
            import tempfile

            # Use tempfile to get secure temporary directory
            temp_dir = tempfile.gettempdir()

            if field_name:
                name_lower = field_name.lower()
                if "dir" in name_lower or "directory" in name_lower:
                    return pathlib.Path(temp_dir) / "mock_directory"
                elif "file" in name_lower:
                    return pathlib.Path(temp_dir) / "mock_file.txt"
            return pathlib.Path(temp_dir) / "mock_path"
        except ImportError:
            import tempfile

            return tempfile.gettempdir() + "/mock_path"

    # Try to instantiate with no arguments
    try:
        instance = field_type()
        return instance
    except Exception:
        pass

    # Try to instantiate with None
    try:
        instance = field_type(None)
        return instance
    except Exception:
        pass

    # Try to instantiate with empty string
    try:
        instance = field_type("")
        return instance
    except Exception:
        pass

    # Try to instantiate with 0
    try:
        instance = field_type(0)
        return instance
    except Exception:
        pass

    # Always issue warning for unsupported types
    warnings.warn(
        f"mocksmith: Unsupported type '{type_name}' for field '{field_name}'. "
        f"Returning None. Consider making this field Optional or providing a mock override.",
        UserWarning,
        stacklevel=4,
    )
    return None


def _generate_pydantic_type_mock(field_type: Any, field_name: str = "") -> Any:
    """Generate mock data for Pydantic built-in types.

    Args:
        field_type: The Pydantic type
        field_name: The field name (for context)

    Returns:
        Mock value appropriate for the Pydantic type
    """
    fake = _get_faker()
    from decimal import Decimal

    type_name = field_type.__name__ if hasattr(field_type, "__name__") else str(field_type)

    # Network types
    if type_name == "HttpUrl":
        return fake.url()
    elif type_name == "AnyHttpUrl":
        return fake.url()
    elif type_name == "EmailStr":
        return fake.email()
    elif type_name == "IPvAnyAddress":
        return fake.ipv4() if fake.boolean(chance_of_getting_true=80) else fake.ipv6()
    elif type_name == "IPvAnyInterface":
        ip = fake.ipv4() if fake.boolean(chance_of_getting_true=80) else fake.ipv6()
        prefix = "/24" if "." in ip else "/64"
        return f"{ip}{prefix}"
    elif type_name == "IPvAnyNetwork":
        if fake.boolean(chance_of_getting_true=80):
            return f"{fake.ipv4()}/24"
        else:
            return f"{fake.ipv6()}/64"
    elif type_name in ["IPv4Address", "IPv4Interface", "IPv4Network"]:
        if type_name == "IPv4Address":
            return fake.ipv4()
        elif type_name == "IPv4Interface":
            return f"{fake.ipv4()}/24"
        else:  # IPv4Network
            return f"{fake.ipv4()}/24"
    elif type_name in ["IPv6Address", "IPv6Interface", "IPv6Network"]:
        if type_name == "IPv6Address":
            return fake.ipv6()
        elif type_name == "IPv6Interface":
            return f"{fake.ipv6()}/64"
        else:  # IPv6Network
            return f"{fake.ipv6()}/64"

    # Numeric types
    elif type_name == "PositiveInt":
        return fake.random_int(min=1, max=10000)
    elif type_name == "NegativeInt":
        return fake.random_int(min=-10000, max=-1)
    elif type_name == "NonNegativeInt":
        return fake.random_int(min=0, max=10000)
    elif type_name == "NonPositiveInt":
        return fake.random_int(min=-10000, max=0)
    elif type_name == "PositiveFloat":
        return fake.pyfloat(min_value=0.01, max_value=10000)
    elif type_name == "NegativeFloat":
        return fake.pyfloat(min_value=-10000, max_value=-0.01)
    elif type_name == "NonNegativeFloat":
        return fake.pyfloat(min_value=0, max_value=10000)
    elif type_name == "NonPositiveFloat":
        return fake.pyfloat(min_value=-10000, max_value=0)

    # String types
    elif type_name == "UUID1":
        return str(fake.uuid4())  # Using uuid4 as faker doesn't have uuid1
    elif type_name == "UUID3":
        return str(fake.uuid4())  # Using uuid4 as faker doesn't have uuid3
    elif type_name == "UUID4":
        return str(fake.uuid4())
    elif type_name == "UUID5":
        return str(fake.uuid4())  # Using uuid4 as faker doesn't have uuid5
    elif type_name == "SecretStr":
        return fake.password()
    elif type_name == "Json":
        return fake.json()

    # Date/time types
    elif type_name == "FutureDate":
        return fake.future_date()
    elif type_name == "PastDate":
        return fake.past_date()
    elif type_name == "FutureDatetime":
        return fake.future_datetime()
    elif type_name == "PastDatetime":
        return fake.past_datetime()

    # For constrained types (constr, conint, etc.)
    elif hasattr(field_type, "__supertype__"):
        base_type = field_type.__supertype__
        if base_type is str:
            # Handle constr
            min_length = getattr(field_type, "min_length", 1)
            max_length = getattr(field_type, "max_length", 50)
            return fake.pystr(min_chars=min_length, max_chars=max_length)
        elif base_type is int:
            # Handle conint
            gt = getattr(field_type, "gt", None)
            ge = getattr(field_type, "ge", None)
            lt = getattr(field_type, "lt", None)
            le = getattr(field_type, "le", None)

            min_val = -10000
            max_val = 10000

            if gt is not None:
                min_val = gt + 1
            elif ge is not None:
                min_val = ge

            if lt is not None:
                max_val = lt - 1
            elif le is not None:
                max_val = le

            return fake.random_int(min=min_val, max=max_val)
        elif base_type is float:
            # Handle confloat
            gt = getattr(field_type, "gt", None)
            ge = getattr(field_type, "ge", None)
            lt = getattr(field_type, "lt", None)
            le = getattr(field_type, "le", None)

            min_val = -10000.0
            max_val = 10000.0

            if gt is not None:
                min_val = gt + 0.01
            elif ge is not None:
                min_val = ge

            if lt is not None:
                max_val = lt - 0.01
            elif le is not None:
                max_val = le

            return fake.pyfloat(min_value=min_val, max_value=max_val)
        elif base_type is Decimal:
            # Handle condecimal
            gt = getattr(field_type, "gt", None)
            ge = getattr(field_type, "ge", None)
            lt = getattr(field_type, "lt", None)
            le = getattr(field_type, "le", None)
            max_digits = getattr(field_type, "max_digits", None)
            decimal_places = getattr(field_type, "decimal_places", None)

            min_val = -10000.0
            max_val = 10000.0

            if gt is not None:
                min_val = float(gt) + 0.01
            elif ge is not None:
                min_val = float(ge)

            if lt is not None:
                max_val = float(lt) - 0.01
            elif le is not None:
                max_val = float(le)

            # Generate decimal with constraints
            if decimal_places is not None:
                float_val = fake.pyfloat(
                    min_value=min_val,
                    max_value=max_val,
                    right_digits=decimal_places,
                )
                # Round to the correct number of decimal places
                quantizer = Decimal("0.1") ** decimal_places
                dec_val = Decimal(str(float_val)).quantize(quantizer)

                # Ensure we respect max_digits constraint
                if max_digits is not None:
                    integer_digits = max_digits - decimal_places
                    max_integer_value = 10**integer_digits - 1

                    if abs(dec_val) > max_integer_value:
                        if dec_val > 0:
                            dec_val = Decimal(str(max_integer_value))
                        else:
                            dec_val = Decimal(str(-max_integer_value))

                return dec_val
            else:
                float_val = fake.pyfloat(min_value=min_val, max_value=max_val)
                return Decimal(str(float_val))

    # Default: return None for unknown Pydantic types
    return None


def _generate_pydantic_annotated_mock(field_type: Any, field_name: str = "") -> Any:
    """Generate mock data for Pydantic v2 Annotated types.

    Args:
        field_type: The Annotated type with Pydantic constraints
        field_name: The field name (for context)

    Returns:
        Mock value that satisfies the constraints
    """
    fake = _get_faker()
    from decimal import Decimal

    # Get the base type and metadata
    args = get_args(field_type)
    if not args:
        # Handle our MockAnnotated type
        if hasattr(field_type, "__args__"):
            args = field_type.__args__
        else:
            return None

    base_type = args[0]
    metadata = getattr(field_type, "__metadata__", ())

    # Handle UUID types
    if base_type.__name__ == "UUID":
        return str(fake.uuid4())

    # Handle numeric constraints
    if base_type in (int, float, Decimal):
        min_val = None
        max_val = None
        max_digits = None
        decimal_places = None

        for m in metadata:
            # Handle Interval constraints (from conint, confloat, condecimal)
            if hasattr(m, "ge") and m.ge is not None:
                min_val = m.ge
            elif hasattr(m, "gt") and m.gt is not None:
                if base_type is int:
                    min_val = m.gt + 1
                elif base_type is Decimal:
                    min_val = Decimal(str(m.gt)) + Decimal("0.01")
                else:
                    min_val = m.gt + 0.01

            if hasattr(m, "le") and m.le is not None:
                max_val = m.le
            elif hasattr(m, "lt") and m.lt is not None:
                if base_type is int:
                    max_val = m.lt - 1
                elif base_type is Decimal:
                    max_val = Decimal(str(m.lt)) - Decimal("0.01")
                else:
                    max_val = m.lt - 0.01

            # Handle Lt, Le, Gt, Ge constraints (e.g., NegativeFloat)
            if hasattr(m, "__class__") and m.__class__.__name__ == "Lt" and hasattr(m, "lt"):
                if base_type is int:
                    max_val = m.lt - 1
                elif base_type is Decimal:
                    max_val = Decimal(str(m.lt)) - Decimal("0.01")
                else:
                    max_val = m.lt - 0.01
            elif hasattr(m, "__class__") and m.__class__.__name__ == "Le" and hasattr(m, "le"):
                max_val = m.le
            elif hasattr(m, "__class__") and m.__class__.__name__ == "Gt" and hasattr(m, "gt"):
                if base_type is int:
                    min_val = m.gt + 1
                elif base_type is Decimal:
                    min_val = Decimal(str(m.gt)) + Decimal("0.01")
                else:
                    min_val = m.gt + 0.01
            elif hasattr(m, "__class__") and m.__class__.__name__ == "Ge" and hasattr(m, "ge"):
                min_val = m.ge

            # Handle decimal-specific constraints
            if base_type is Decimal:
                if hasattr(m, "max_digits") and m.max_digits is not None:
                    max_digits = m.max_digits
                if hasattr(m, "decimal_places") and m.decimal_places is not None:
                    decimal_places = m.decimal_places

        # Set defaults if not specified
        if min_val is None:
            min_val = -10000 if base_type is int else -10000.0
        if max_val is None:
            max_val = 10000 if base_type is int else 10000.0

        # Ensure min_val <= max_val
        if min_val > max_val:
            # If constraints are impossible, adjust max to be at least min
            if base_type is int:
                max_val = int(min_val) + 1
            elif base_type is Decimal:
                max_val = Decimal(str(min_val)) + Decimal("0.01")
            else:
                max_val = float(min_val) + 0.01

        if base_type is int:
            return fake.random_int(min=int(min_val), max=int(max_val))
        elif base_type is Decimal:
            # Generate decimal with constraints
            if decimal_places is not None:
                # Generate a float and round to decimal places
                float_val = fake.pyfloat(
                    min_value=float(min_val) if min_val is not None else -10000.0,
                    max_value=float(max_val) if max_val is not None else 10000.0,
                    right_digits=decimal_places,
                )
                # Round to the correct number of decimal places
                quantizer = Decimal("0.1") ** decimal_places
                dec_val = Decimal(str(float_val)).quantize(quantizer)

                # Ensure we respect max_digits constraint
                if max_digits is not None:
                    # Calculate max allowed integer digits
                    integer_digits = max_digits - (decimal_places or 0)
                    max_integer_value = 10**integer_digits - 1

                    # Clamp the value to respect max_digits
                    if abs(dec_val) > max_integer_value:
                        if dec_val > 0:
                            dec_val = Decimal(str(max_integer_value))
                        else:
                            dec_val = Decimal(str(-max_integer_value))

                return dec_val
            else:
                # No decimal places specified, generate as float and convert
                float_val = fake.pyfloat(
                    min_value=float(min_val) if min_val is not None else -10000.0,
                    max_value=float(max_val) if max_val is not None else 10000.0,
                )
                return Decimal(str(float_val))
        else:
            return fake.pyfloat(min_value=float(min_val), max_value=float(max_val))

    # Handle string constraints
    elif base_type is str:
        min_length = None
        max_length = None
        pattern = None

        for m in metadata:
            # Handle StringConstraints from Pydantic
            if hasattr(m, "__class__") and m.__class__.__name__ == "StringConstraints":
                if m.min_length is not None:
                    min_length = m.min_length
                if m.max_length is not None:
                    max_length = m.max_length
                if m.pattern is not None:
                    pattern = m.pattern
            # Handle annotated_types constraints
            elif hasattr(m, "min_length"):
                min_length = m.min_length
            elif hasattr(m, "max_length"):
                max_length = m.max_length
            elif hasattr(m, "pattern"):
                pattern = m.pattern

        # Generate string with constraints
        if pattern:
            # Handle some common patterns
            if pattern == r"^[A-Z]{3}[0-9]{3}$":
                # Generate 3 uppercase letters + 3 digits
                letters = "".join(
                    fake.random_element("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3)
                )
                digits = "".join(fake.random_element("0123456789") for _ in range(3))
                return letters + digits
            # For other patterns, fall back to basic string generation
            # TODO: Add more pattern support or use a regex generator

        if min_length is None:
            min_length = 1
        if max_length is None:
            max_length = 50

        return fake.pystr(min_chars=min_length, max_chars=max_length)

    # Fall back to basic type generation
    return _generate_field_mock(base_type, field_name)


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

        # Check if field.type is Annotated and has DBType in metadata
        mock_value = None
        origin = get_origin(field.type)
        if origin is Annotated:
            # Get metadata from the Annotated type
            metadata = getattr(field.type, "__metadata__", ())
            for metadata_item in metadata:
                # Check if metadata item has db_type attribute (from DBTypeValidator)
                if hasattr(metadata_item, "db_type") and isinstance(metadata_item.db_type, DBType):
                    mock_value = metadata_item.db_type.mock()
                    break
                # Also check if metadata item IS a DBType directly (for dataclasses)
                elif isinstance(metadata_item, DBType):
                    mock_value = metadata_item.mock()
                    break
                # Handle mock providers with mock() method
                elif hasattr(metadata_item, "mock") and callable(metadata_item.mock):
                    mock_value = metadata_item.mock()
                    break

        # If no DBType found, use regular generation
        if mock_value is None:
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
                # Check if metadata item has db_type attribute (from DBTypeValidator)
                if hasattr(metadata_item, "db_type") and isinstance(metadata_item.db_type, DBType):
                    mock_value = metadata_item.db_type.mock()
                    break
                # Also check if metadata item IS a DBType directly (for dataclasses)
                elif isinstance(metadata_item, DBType):
                    mock_value = metadata_item.mock()
                    break
                # Handle mock providers with mock() method
                elif hasattr(metadata_item, "mock") and callable(metadata_item.mock):
                    mock_value = metadata_item.mock()
                    break

        # If no DBType found in metadata, check for Pydantic constraints
        if mock_value is None:
            # Check if field has Pydantic constraint metadata
            if hasattr(field_info, "metadata") and field_info.metadata:
                # Check for Pydantic-specific metadata
                has_pydantic_metadata = False
                for m in field_info.metadata:
                    if m is not None and hasattr(m, "__module__"):
                        module = getattr(m, "__module__", "")
                        if "pydantic" in module or "annotated_types" in module:
                            has_pydantic_metadata = True
                            break
                    # Also check for specific constraint types
                    if hasattr(m, "__class__") and m.__class__.__name__ in [
                        "Interval",
                        "Lt",
                        "Le",
                        "Gt",
                        "Ge",
                        "StringConstraints",
                    ]:
                        has_pydantic_metadata = True
                        break

                if has_pydantic_metadata:
                    # Create a mock Annotated type for the handler
                    class MockAnnotated:
                        __metadata__ = field_info.metadata
                        __origin__ = Annotated

                    # Add the args
                    MockAnnotated.__args__ = (field_info.annotation, *field_info.metadata)

                    # Try to generate with Pydantic annotated handler
                    pydantic_mock = _generate_pydantic_annotated_mock(MockAnnotated, field_name)
                    if pydantic_mock is not None:
                        mock_value = pydantic_mock

            # If still no mock value, use standard generation
            if mock_value is None:
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
        _depth: Recursion depth for nested types

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

    # Handle Literal types
    if origin is Literal:
        # Get all literal values and pick one randomly
        literal_values = list(get_args(field_type))
        return _get_faker().random_element(literal_values)

    # Handle custom types with mock() class method
    if hasattr(field_type, "mock") and callable(field_type.mock):
        return field_type.mock()

    # Handle nested dataclasses
    if is_dataclass(field_type):
        # Recursively generate mock for nested dataclass
        return mock_factory(field_type)

    # Handle Pydantic built-in types (v2 uses Annotated)
    if hasattr(field_type, "__module__") and "pydantic" in field_type.__module__:
        return _generate_pydantic_type_mock(field_type, field_name)

    # Check if it's an Annotated type with Pydantic constraints
    if origin is not None and hasattr(field_type, "__metadata__"):
        # Check for Pydantic metadata markers
        for metadata in field_type.__metadata__:
            if metadata is not None and hasattr(metadata, "__module__"):
                module = getattr(metadata, "__module__", "")
                if "pydantic" in module or "annotated_types" in module:
                    # This is a Pydantic constrained type
                    return _generate_pydantic_annotated_mock(field_type, field_name)

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
                # Handle mock providers with mock() method
                elif hasattr(item, "mock") and callable(item.mock):
                    return item.mock()

            # If no DBType found, continue with the actual type
            field_type = actual_type

    # Handle DBType classes directly
    if isinstance(field_type, type):
        try:
            if issubclass(field_type, DBType):
                # Need to instantiate it first - this won't work for types requiring args
                # Users should use instances or Annotated types instead
                raise TypeError(
                    f"Cannot mock {field_type.__name__} class directly. "
                    "Use an instance (e.g., VARCHAR(50)) or Annotated type instead."
                )
        except TypeError:
            # Not a class (e.g., generic alias like set[str])
            pass

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

    # Handle Set types
    if origin is set:
        inner_type = get_args(field_type)[0] if get_args(field_type) else str
        count = _get_faker().random_int(min=1, max=5)
        # Generate more items than needed to ensure uniqueness
        items = []
        attempts = 0
        while len(items) < count and attempts < count * 3:
            item = _generate_field_mock(inner_type, field_name, _depth + 1)
            if item not in items:
                items.append(item)
            attempts += 1
        return set(items)

    # Handle FrozenSet types
    if origin is frozenset:
        inner_type = get_args(field_type)[0] if get_args(field_type) else str
        count = _get_faker().random_int(min=1, max=5)
        items = []
        attempts = 0
        while len(items) < count and attempts < count * 3:
            item = _generate_field_mock(inner_type, field_name, _depth + 1)
            if item not in items:
                items.append(item)
            attempts += 1
        return frozenset(items)

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
    elif field_type.__name__ == "UUID":
        # Handle uuid.UUID type
        return str(_get_faker().uuid4())
    else:
        # Unknown/unsupported type
        return _handle_unsupported_type(field_type, field_name)
