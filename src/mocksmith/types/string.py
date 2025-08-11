"""String types with V3 pattern - extends Python str type directly."""

from typing import Any, ClassVar, Optional

try:
    from pydantic import GetCoreSchemaHandler  # type: ignore
    from pydantic_core import PydanticCustomError, core_schema  # type: ignore

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    GetCoreSchemaHandler = Any
    core_schema = None
    PydanticCustomError = ValueError


class _VARCHAR(str):
    """Variable-length character string with constraints (internal use only)."""

    SQL_TYPE: ClassVar[str] = "VARCHAR"
    _length: ClassVar[int] = 255
    _min_length: ClassVar[Optional[int]] = None
    _startswith: ClassVar[Optional[str]] = None
    _endswith: ClassVar[Optional[str]] = None
    _strip_whitespace: ClassVar[bool] = False
    _to_lower: ClassVar[bool] = False
    _to_upper: ClassVar[bool] = False

    def __new__(cls, value: Any) -> "_VARCHAR":
        """Create new varchar with validation and transformations."""
        if value is None:
            raise ValueError("Value cannot be None")

        # Convert to string
        str_value = str(value)

        # Apply transformations
        if cls._strip_whitespace:
            str_value = str_value.strip()
        if cls._to_lower:
            str_value = str_value.lower()
        elif cls._to_upper:
            str_value = str_value.upper()

        # Validate length
        if len(str_value) > cls._length:
            raise ValueError(f"String length {len(str_value)} exceeds maximum {cls._length}")

        if cls._min_length is not None and len(str_value) < cls._min_length:
            raise ValueError(
                f"String length {len(str_value)} is less than minimum {cls._min_length}"
            )

        # Validate prefix/suffix
        if cls._startswith and not str_value.startswith(cls._startswith):
            raise ValueError(f"String must start with '{cls._startswith}'")

        if cls._endswith and not str_value.endswith(cls._endswith):
            raise ValueError(f"String must end with '{cls._endswith}'")

        return super().__new__(cls, str_value)

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        return f"VARCHAR({self._length})"

    def serialize(self) -> str:
        """Serialize to string for SQL."""
        return str(self)

    @classmethod
    def validate(cls, value: Any) -> str:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return str(instance)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_varchar(value: Any) -> str:
            """Validate and convert to varchar."""
            try:
                instance = cls(value)
                return str(instance)
            except ValueError as e:
                raise PydanticCustomError("varchar_type", str(e)) from e

        # Build regex pattern if needed
        import re

        pattern = None
        if cls._startswith or cls._endswith:
            if cls._startswith and cls._endswith:
                pattern = f"^{re.escape(cls._startswith)}.*{re.escape(cls._endswith)}$"
            elif cls._startswith:
                pattern = f"^{re.escape(cls._startswith)}.*"
            elif cls._endswith:
                pattern = f".*{re.escape(cls._endswith)}$"

        schema = core_schema.str_schema(  # type: ignore
            max_length=cls._length,
            min_length=cls._min_length,
            pattern=pattern,
            strip_whitespace=cls._strip_whitespace,
            to_lower=cls._to_lower,
            to_upper=cls._to_upper,
        )

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_varchar,
            schema,
        )

    @classmethod
    def mock(cls) -> str:
        """Generate mock varchar value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()

            # Handle startswith/endswith constraints
            if cls._startswith or cls._endswith:
                prefix = cls._startswith or ""
                suffix = cls._endswith or ""
                prefix_suffix_len = len(prefix) + len(suffix)

                if prefix_suffix_len >= cls._length:
                    # No room for random content
                    text = (prefix + suffix)[: cls._length]
                else:
                    # Calculate how many random chars we need
                    min_middle = max(0, (cls._min_length or 1) - prefix_suffix_len)
                    max_middle = cls._length - prefix_suffix_len

                    # Generate middle part
                    middle_chars = fake.random_int(min=min_middle, max=max_middle)
                    middle = fake.pystr(min_chars=middle_chars, max_chars=middle_chars)

                    text = prefix + middle + suffix
            else:
                # Generate based on length
                min_len = cls._min_length or 1

                if cls._length <= 10:
                    text = fake.word()
                elif cls._length <= 30:
                    text = fake.name()
                elif cls._length <= 100:
                    text = fake.sentence(nb_words=6, variable_nb_words=True)
                else:
                    text = fake.text(max_nb_chars=cls._length)

                # Ensure minimum length
                while len(text) < min_len:
                    text += " " + fake.word()

            # Apply transformations
            if cls._strip_whitespace:
                text = text.strip()
            if cls._to_lower:
                text = text.lower()
            elif cls._to_upper:
                text = text.upper()

            # Ensure max length
            if len(text) > cls._length:
                text = text[: cls._length]

            return text
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


class _CHAR(str):
    """Fixed-length character string (internal use only)."""

    SQL_TYPE: ClassVar[str] = "CHAR"
    _length: ClassVar[int] = 1
    _startswith: ClassVar[Optional[str]] = None
    _endswith: ClassVar[Optional[str]] = None
    _strip_whitespace: ClassVar[bool] = False
    _to_lower: ClassVar[bool] = False
    _to_upper: ClassVar[bool] = False

    def __new__(cls, value: Any) -> "_CHAR":
        """Create new char with validation and padding."""
        if value is None:
            raise ValueError("Value cannot be None")

        # Convert to string
        str_value = str(value).rstrip()  # Remove trailing spaces (typical CHAR retrieval)

        # Apply transformations
        if cls._strip_whitespace:
            str_value = str_value.strip()
        if cls._to_lower:
            str_value = str_value.lower()
        elif cls._to_upper:
            str_value = str_value.upper()

        # Validate length (before padding)
        if len(str_value) > cls._length:
            raise ValueError(f"String length {len(str_value)} exceeds maximum {cls._length}")

        # Validate prefix/suffix
        if cls._startswith and not str_value.startswith(cls._startswith):
            raise ValueError(f"String must start with '{cls._startswith}'")

        if cls._endswith and not str_value.endswith(cls._endswith):
            raise ValueError(f"String must end with '{cls._endswith}'")

        # Pad to fixed length
        str_value = str_value.ljust(cls._length)

        return super().__new__(cls, str_value)

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        return f"CHAR({self._length})"

    def serialize(self) -> str:
        """Serialize to string for SQL (with padding)."""
        return str(self).ljust(self._length)

    @classmethod
    def validate(cls, value: Any) -> str:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return str(instance)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_char(value: Any) -> str:
            """Validate and convert to char."""
            try:
                instance = cls(value)
                return str(instance)  # Return with padding as intended
            except ValueError as e:
                raise PydanticCustomError("char_type", str(e)) from e

        # Build regex pattern if needed
        import re

        pattern = None
        if cls._startswith or cls._endswith:
            if cls._startswith and cls._endswith:
                pattern = f"^{re.escape(cls._startswith)}.*{re.escape(cls._endswith)}$"
            elif cls._startswith:
                pattern = f"^{re.escape(cls._startswith)}.*"
            elif cls._endswith:
                pattern = f".*{re.escape(cls._endswith)}$"

        schema = core_schema.str_schema(  # type: ignore
            max_length=cls._length,
            pattern=pattern,
            strip_whitespace=cls._strip_whitespace,
            to_lower=cls._to_lower,
            to_upper=cls._to_upper,
        )

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_char,
            schema,
        )

    @classmethod
    def mock(cls) -> str:
        """Generate mock char value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()

            # Handle startswith/endswith constraints
            if cls._startswith or cls._endswith:
                prefix = cls._startswith or ""
                suffix = cls._endswith or ""
                prefix_suffix_len = len(prefix) + len(suffix)

                if prefix_suffix_len >= cls._length:
                    text = (prefix + suffix)[: cls._length]
                else:
                    # For CHAR, we need exactly self._length characters
                    middle_len = cls._length - prefix_suffix_len
                    middle = fake.pystr(min_chars=middle_len, max_chars=middle_len)
                    text = prefix + middle + suffix
            else:
                # Generate based on length
                if cls._length <= 2:
                    text = fake.country_code()
                elif cls._length <= 10:
                    text = fake.word()
                else:
                    text = fake.text(max_nb_chars=cls._length)

            # Apply transformations
            if cls._strip_whitespace:
                text = text.strip()
            if cls._to_lower:
                text = text.lower()
            elif cls._to_upper:
                text = text.upper()

            # Ensure exact length (CHAR is fixed-length)
            if len(text) > cls._length:
                text = text[: cls._length]
            else:
                text = text.ljust(cls._length)

            return text
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


class _TEXT(str):
    """Variable-length text (internal use only)."""

    SQL_TYPE: ClassVar[str] = "TEXT"
    _max_length: ClassVar[Optional[int]] = None
    _min_length: ClassVar[Optional[int]] = None
    _startswith: ClassVar[Optional[str]] = None
    _endswith: ClassVar[Optional[str]] = None
    _strip_whitespace: ClassVar[bool] = False
    _to_lower: ClassVar[bool] = False
    _to_upper: ClassVar[bool] = False

    def __new__(cls, value: Any) -> "_TEXT":
        """Create new text with validation."""
        if value is None:
            raise ValueError("Value cannot be None")

        # Convert to string
        str_value = str(value)

        # Apply transformations
        if cls._strip_whitespace:
            str_value = str_value.strip()
        if cls._to_lower:
            str_value = str_value.lower()
        elif cls._to_upper:
            str_value = str_value.upper()

        # Validate length
        if cls._max_length and len(str_value) > cls._max_length:
            raise ValueError(f"Text length {len(str_value)} exceeds maximum {cls._max_length}")

        if cls._min_length is not None and len(str_value) < cls._min_length:
            raise ValueError(f"Text length {len(str_value)} is less than minimum {cls._min_length}")

        # Validate prefix/suffix
        if cls._startswith and not str_value.startswith(cls._startswith):
            raise ValueError(f"Text must start with '{cls._startswith}'")

        if cls._endswith and not str_value.endswith(cls._endswith):
            raise ValueError(f"Text must end with '{cls._endswith}'")

        return super().__new__(cls, str_value)

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        return "TEXT"

    def serialize(self) -> str:
        """Serialize to string for SQL."""
        return str(self)

    @classmethod
    def validate(cls, value: Any) -> str:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return str(instance)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_text(value: Any) -> str:
            """Validate and convert to text."""
            try:
                instance = cls(value)
                return str(instance)
            except ValueError as e:
                raise PydanticCustomError("text_type", str(e)) from e

        # Build regex pattern if needed
        import re

        pattern = None
        if cls._startswith or cls._endswith:
            if cls._startswith and cls._endswith:
                pattern = f"^{re.escape(cls._startswith)}.*{re.escape(cls._endswith)}$"
            elif cls._startswith:
                pattern = f"^{re.escape(cls._startswith)}.*"
            elif cls._endswith:
                pattern = f".*{re.escape(cls._endswith)}$"

        kwargs = {
            "strip_whitespace": cls._strip_whitespace,
            "to_lower": cls._to_lower,
            "to_upper": cls._to_upper,
        }
        if cls._max_length is not None:
            kwargs["max_length"] = cls._max_length
        if cls._min_length is not None:
            kwargs["min_length"] = cls._min_length
        if pattern is not None:
            kwargs["pattern"] = pattern

        schema = core_schema.str_schema(**kwargs)  # type: ignore

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_text,
            schema,
        )

    @classmethod
    def mock(cls) -> str:
        """Generate mock text value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()

            # Handle startswith/endswith constraints
            if cls._startswith or cls._endswith:
                prefix = cls._startswith or ""
                suffix = cls._endswith or ""
                prefix_suffix_len = len(prefix) + len(suffix)

                # Determine target length
                if cls._max_length and cls._min_length:
                    target_length = fake.random_int(min=cls._min_length, max=cls._max_length)
                elif cls._max_length:
                    target_length = fake.random_int(
                        min=max(prefix_suffix_len + 10, 50), max=cls._max_length
                    )
                elif cls._min_length:
                    target_length = fake.random_int(min=cls._min_length, max=cls._min_length + 500)
                else:
                    target_length = fake.random_int(min=200, max=1000)

                # Calculate middle content length
                middle_length = target_length - prefix_suffix_len

                if middle_length <= 0:
                    text = (prefix + suffix)[:target_length]
                elif middle_length <= 50:
                    middle = fake.pystr(min_chars=middle_length, max_chars=middle_length)
                    text = prefix + middle + suffix
                else:
                    middle = fake.text(max_nb_chars=middle_length * 2)
                    middle = middle.strip()
                    if len(middle) > middle_length:
                        middle = middle[:middle_length].rstrip()
                    elif len(middle) < middle_length:
                        padding_needed = middle_length - len(middle)
                        middle = (
                            middle
                            + " "
                            + fake.pystr(min_chars=padding_needed - 1, max_chars=padding_needed - 1)
                        )
                    text = prefix + middle + suffix
            else:
                # Determine target length
                if cls._max_length and cls._min_length:
                    target_length = fake.random_int(min=cls._min_length, max=cls._max_length)
                elif cls._max_length:
                    target_length = fake.random_int(min=10, max=cls._max_length)
                elif cls._min_length:
                    target_length = fake.random_int(min=cls._min_length, max=cls._min_length + 500)
                else:
                    target_length = 500

                # Generate text
                if target_length <= 200:
                    text = fake.paragraph(nb_sentences=3)
                else:
                    text = fake.text(max_nb_chars=target_length)

                # Ensure min length
                while cls._min_length and len(text) < cls._min_length:
                    text += " " + fake.paragraph()

            # Apply transformations
            if cls._strip_whitespace:
                text = text.strip()
            if cls._to_lower:
                text = text.lower()
            elif cls._to_upper:
                text = text.upper()

            # Ensure max length
            if cls._max_length and len(text) > cls._max_length:
                text = text[: cls._max_length]

            return text
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


# Factory functions
def Varchar(  # noqa: N802
    length: int,
    *,
    min_length: Optional[int] = None,
    startswith: Optional[str] = None,
    endswith: Optional[str] = None,
    strip_whitespace: bool = False,
    to_lower: bool = False,
    to_upper: bool = False,
) -> type:
    """Create a VARCHAR type with constraints.

    Example:
        class User(BaseModel):
            username: Varchar(30, min_length=3)
            email: Varchar(100, endswith='@example.com')
    """
    if length <= 0:
        raise ValueError("Length must be positive")
    if min_length is not None:
        if min_length < 0:
            raise ValueError("min_length cannot be negative")
        if min_length > length:
            raise ValueError("min_length cannot exceed length")

    if startswith and len(startswith) >= length:
        raise ValueError(f"startswith '{startswith}' is too long for length {length}")
    if endswith and len(endswith) >= length:
        raise ValueError(f"endswith '{endswith}' is too long for length {length}")
    if startswith and endswith and len(startswith) + len(endswith) > length:
        raise ValueError(f"startswith + endswith is too long for length {length}")

    class ConstrainedVarchar(_VARCHAR):
        _length = length
        _min_length = min_length
        _startswith = startswith
        _endswith = endswith
        _strip_whitespace = strip_whitespace
        _to_lower = to_lower
        _to_upper = to_upper
        SQL_TYPE = "VARCHAR"

    return ConstrainedVarchar


def Char(  # noqa: N802
    length: int,
    *,
    startswith: Optional[str] = None,
    endswith: Optional[str] = None,
    strip_whitespace: bool = False,
    to_lower: bool = False,
    to_upper: bool = False,
) -> type:
    """Create a CHAR type with fixed length.

    Example:
        class Account(BaseModel):
            code: Char(10)
            country: Char(2, to_upper=True)
    """
    if length <= 0:
        raise ValueError("Length must be positive")

    if startswith and len(startswith) >= length:
        raise ValueError(f"startswith '{startswith}' is too long for length {length}")
    if endswith and len(endswith) >= length:
        raise ValueError(f"endswith '{endswith}' is too long for length {length}")
    if startswith and endswith and len(startswith) + len(endswith) > length:
        raise ValueError(f"startswith + endswith is too long for length {length}")

    class ConstrainedChar(_CHAR):
        _length = length
        _startswith = startswith
        _endswith = endswith
        _strip_whitespace = strip_whitespace
        _to_lower = to_lower
        _to_upper = to_upper
        SQL_TYPE = "CHAR"

    return ConstrainedChar


def Text(  # noqa: N802
    *,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    startswith: Optional[str] = None,
    endswith: Optional[str] = None,
    strip_whitespace: bool = False,
    to_lower: bool = False,
    to_upper: bool = False,
) -> type:
    """Create a TEXT type with optional constraints.

    Example:
        class Article(BaseModel):
            content: Text(min_length=100)
            summary: Text(max_length=500)
    """
    if max_length is not None and max_length <= 0:
        raise ValueError("max_length must be positive")
    if min_length is not None:
        if min_length < 0:
            raise ValueError("min_length cannot be negative")
        if max_length is not None and min_length > max_length:
            raise ValueError("min_length cannot exceed max_length")

    if startswith and max_length and len(startswith) >= max_length:
        raise ValueError(f"startswith '{startswith}' is too long for max_length {max_length}")
    if endswith and max_length and len(endswith) >= max_length:
        raise ValueError(f"endswith '{endswith}' is too long for max_length {max_length}")
    if startswith and endswith and max_length and len(startswith) + len(endswith) > max_length:
        raise ValueError(f"startswith + endswith is too long for max_length {max_length}")

    class ConstrainedText(_TEXT):
        _max_length = max_length
        _min_length = min_length
        _startswith = startswith
        _endswith = endswith
        _strip_whitespace = strip_whitespace
        _to_lower = to_lower
        _to_upper = to_upper
        SQL_TYPE = "TEXT"

    return ConstrainedText
