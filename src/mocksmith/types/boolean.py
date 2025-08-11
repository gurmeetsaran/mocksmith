"""Boolean type with V3 pattern - extends Python bool directly."""

from typing import Any, ClassVar

try:
    from pydantic import GetCoreSchemaHandler  # type: ignore
    from pydantic_core import PydanticCustomError, core_schema  # type: ignore

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    GetCoreSchemaHandler = Any
    core_schema = None
    PydanticCustomError = ValueError


class BOOLEAN(int):  # bool inherits from int in Python
    """Boolean type that validates at instantiation.

    Accepts various boolean representations:
    - bool: True/False
    - int: 0/1 (or any int where 0 is False, non-zero is True)
    - str: 'true'/'false', '1'/'0', 't'/'f', 'yes'/'no', 'y'/'n' (case-insensitive)
    """

    SQL_TYPE: ClassVar[str] = "BOOLEAN"

    def __new__(cls, value: Any) -> "BOOLEAN":
        """Create new boolean with validation."""
        if value is None:
            raise ValueError("BOOLEAN cannot be None")

        # Handle string conversion
        if isinstance(value, str):
            lower_val = value.lower().strip()
            if lower_val in ("true", "1", "t", "yes", "y", "on"):
                bool_value = True
            elif lower_val in ("false", "0", "f", "no", "n", "off", ""):
                bool_value = False
            else:
                raise ValueError(
                    f"Invalid boolean string: '{value}'. "
                    f"Expected: true/false, 1/0, t/f, yes/no, y/n, on/off"
                )
        # Handle numeric conversion
        elif isinstance(value, (int, float)):
            bool_value = bool(value)
        # Handle bool directly
        elif isinstance(value, bool):
            bool_value = value
        else:
            # Try to convert using Python's bool()
            try:
                bool_value = bool(value)
            except Exception as e:
                raise ValueError(f"Cannot convert {type(value).__name__} to boolean") from e

        # Create as int subclass (0 or 1)
        return super().__new__(cls, int(bool_value))

    def __bool__(self) -> bool:
        """Return boolean value."""
        return bool(int(self))

    def __str__(self) -> str:
        """String representation."""
        return "true" if self else "false"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"BOOLEAN({bool(self)})"

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        return self.SQL_TYPE

    def serialize(self) -> bool:
        """Serialize to bool for SQL."""
        return bool(self)

    @classmethod
    def validate(cls, value: Any) -> bool:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return bool(instance)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_boolean(value: Any) -> bool:
            """Validate and convert to boolean."""
            try:
                instance = cls(value)
                return bool(instance)
            except ValueError as e:
                raise PydanticCustomError("boolean_type", str(e)) from e

        # Use bool_schema as base but with custom validator
        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_boolean,
            core_schema.union_schema(  # type: ignore
                [  # type: ignore
                    core_schema.bool_schema(),  # type: ignore
                    core_schema.int_schema(),  # type: ignore
                    core_schema.str_schema(),  # type: ignore
                ]
            ),
        )

    @classmethod
    def mock(cls) -> bool:
        """Generate mock boolean value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()
            return fake.boolean()
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


# Factory function for consistency with numeric types
def Boolean() -> type:  # noqa: N802
    """Create a Boolean type for use as type annotation.

    Example:
        class User(BaseModel):
            is_active: Boolean()
            is_verified: Boolean()
    """
    return BOOLEAN


# Aliases
Bool = Boolean
