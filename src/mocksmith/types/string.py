"""String database types."""

from typing import Any, Optional

from mocksmith.types.base import PYDANTIC_AVAILABLE, DBType

if PYDANTIC_AVAILABLE:
    from pydantic import constr  # type: ignore[import-not-found]


class VARCHAR(DBType[str]):
    """Variable-length character string with optional constraints.

    Args:
        length: Maximum length of the string
        min_length: Minimum length of the string (optional)
        startswith: String must start with this prefix (optional)
        endswith: String must end with this suffix (optional)
        strip_whitespace: Whether to strip whitespace (default: False)
        to_lower: Convert to lowercase (default: False)
        to_upper: Convert to uppercase (default: False)
        **pydantic_kwargs: Additional Pydantic-specific arguments (e.g., strict)

    Examples:
        # Basic usage
        name: Varchar(50)

        # With prefix/suffix constraints for structured data
        order_id: Varchar(20, startswith='ORD-')
        email: Varchar(100, endswith='@company.com', to_lower=True)
        invoice: Varchar(30, startswith='INV-', endswith='-2024')

        # With transformations
        username: Varchar(50, min_length=3, to_lower=True, strip_whitespace=True)
    """

    def __init__(
        self,
        length: int,
        *,  # Force keyword-only args
        min_length: Optional[int] = None,
        startswith: Optional[str] = None,
        endswith: Optional[str] = None,
        strip_whitespace: bool = False,
        to_lower: bool = False,
        to_upper: bool = False,
        **pydantic_kwargs: Any,
    ):
        super().__init__()
        if length <= 0:
            raise ValueError("VARCHAR length must be positive")
        if min_length is not None:
            if min_length < 0:
                raise ValueError("min_length cannot be negative")
            if min_length > length:
                raise ValueError("min_length cannot exceed length")

        if startswith and len(startswith) >= length:
            raise ValueError(f"startswith '{startswith}' is too long for VARCHAR({length})")
        if endswith and len(endswith) >= length:
            raise ValueError(f"endswith '{endswith}' is too long for VARCHAR({length})")
        if startswith and endswith and len(startswith) + len(endswith) > length:
            raise ValueError(f"startswith + endswith is too long for VARCHAR({length})")

        self.length = length
        self.min_length = min_length
        self.startswith = startswith
        self.endswith = endswith
        self.strip_whitespace = strip_whitespace
        self.to_lower = to_lower
        self.to_upper = to_upper
        self.pydantic_kwargs = pydantic_kwargs

    @property
    def sql_type(self) -> str:
        return f"VARCHAR({self.length})"

    @property
    def python_type(self) -> type[str]:
        return str

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic constr type if available."""
        if PYDANTIC_AVAILABLE:
            # Build pattern from startswith/endswith if present
            pattern = None
            if self.startswith or self.endswith:
                import re

                if self.startswith and self.endswith:
                    pattern = f"^{re.escape(self.startswith)}.*{re.escape(self.endswith)}$"
                elif self.startswith:
                    pattern = f"^{re.escape(self.startswith)}.*"
                elif self.endswith:
                    pattern = f".*{re.escape(self.endswith)}$"

            return constr(
                max_length=self.length,
                min_length=self.min_length,
                pattern=pattern,
                strip_whitespace=self.strip_whitespace,
                to_lower=self.to_lower,
                to_upper=self.to_upper,
                **self.pydantic_kwargs,
            )
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value).__name__}")

        # Apply transformations first
        processed = value
        if self.strip_whitespace:
            processed = processed.strip()
        if self.to_lower:
            processed = processed.lower()
        elif self.to_upper:
            processed = processed.upper()

        # Then validate
        if len(processed) > self.length:
            raise ValueError(f"String length {len(processed)} exceeds maximum {self.length}")

        if self.min_length is not None and len(processed) < self.min_length:
            raise ValueError(
                f"String length {len(processed)} is less than minimum {self.min_length}"
            )

        if self.startswith and not processed.startswith(self.startswith):
            raise ValueError(f"String must start with '{self.startswith}'")

        if self.endswith and not processed.endswith(self.endswith):
            raise ValueError(f"String must end with '{self.endswith}'")

    def _serialize(self, value: str) -> str:
        # Serialization just returns the value as-is
        # (transformations already applied during deserialization)
        return value

    def _deserialize(self, value: Any) -> str:
        # Convert to string first
        result = str(value)
        # Apply transformations during deserialization
        if self.strip_whitespace:
            result = result.strip()
        if self.to_lower:
            result = result.lower()
        elif self.to_upper:
            result = result.upper()
        return result

    def __repr__(self) -> str:
        parts = [f"VARCHAR({self.length}"]
        if self.min_length is not None:
            parts.append(f"min_length={self.min_length}")
        if self.startswith:
            parts.append(f"startswith={self.startswith!r}")
        if self.endswith:
            parts.append(f"endswith={self.endswith!r}")
        if self.strip_whitespace:
            parts.append("strip_whitespace=True")
        if self.to_lower:
            parts.append("to_lower=True")
        if self.to_upper:
            parts.append("to_upper=True")
        if self.pydantic_kwargs:
            parts.extend(f"{k}={v!r}" for k, v in self.pydantic_kwargs.items())

        if len(parts) > 1:
            return f"{parts[0]}, {', '.join(parts[1:])})"
        return parts[0] + ")"

    def _generate_mock(self, fake: Any) -> str:
        """Generate mock VARCHAR data respecting constraints."""
        # Handle startswith/endswith constraints
        if self.startswith or self.endswith:
            prefix = self.startswith or ""
            suffix = self.endswith or ""
            prefix_suffix_len = len(prefix) + len(suffix)

            if prefix_suffix_len >= self.length:
                # No room for random content, just use prefix + suffix
                text = (prefix + suffix)[: self.length]
            else:
                # Calculate how many random chars we need between prefix and suffix
                min_middle = max(0, (self.min_length or 1) - prefix_suffix_len)
                max_middle = self.length - prefix_suffix_len

                # Generate only the middle part
                middle_chars = fake.random_int(min=min_middle, max=max_middle)
                middle = fake.pystr(min_chars=middle_chars, max_chars=middle_chars)

                text = prefix + middle + suffix
        else:
            text = self._generate_default_text(fake)

        # Apply transformations
        if self.strip_whitespace:
            text = text.strip()
        if self.to_lower:
            text = text.lower()
        elif self.to_upper:
            text = text.upper()

        # Ensure min/max length
        if self.min_length and len(text) < self.min_length:
            # Pad with random chars if too short
            padding_needed = self.min_length - len(text)
            text += fake.pystr(min_chars=padding_needed, max_chars=padding_needed)

        # Ensure max length
        if len(text) > self.length:
            text = text[: self.length]

        return text

    def _generate_default_text(self, fake: Any) -> str:
        """Generate default text based on length."""
        min_len = self.min_length or 1

        if self.length <= 10:
            # For short strings, use a single word
            text = fake.word()
        elif self.length <= 30:
            # For medium strings, use a name
            text = fake.name()
        elif self.length <= 100:
            # For longer strings, use a sentence
            text = fake.sentence(nb_words=6, variable_nb_words=True)
        else:
            # For very long strings, use paragraph
            text = fake.text(max_nb_chars=self.length)

        # Ensure minimum length
        while len(text) < min_len:
            text += " " + fake.word()

        return text


class CHAR(DBType[str]):
    """Fixed-length character string with optional constraints.

    CHAR is always padded to the specified length with spaces.

    Args:
        length: Fixed length of the string
        startswith: String must start with this prefix (optional)
        endswith: String must end with this suffix (optional)
        strip_whitespace: Whether to strip whitespace on input (default: False)
        to_lower: Convert to lowercase (default: False)
        to_upper: Convert to uppercase (default: False)
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Examples:
        # Basic usage
        code: Char(10)

        # Country code - always uppercase
        country: Char(2, to_upper=True)

        # Product code with prefix
        product_code: Char(8, startswith='PRD-')
        ticket_id: Char(10, startswith='TKT-', to_upper=True)
    """

    def __init__(
        self,
        length: int,
        *,  # Force keyword-only args
        startswith: Optional[str] = None,
        endswith: Optional[str] = None,
        strip_whitespace: bool = False,
        to_lower: bool = False,
        to_upper: bool = False,
        **pydantic_kwargs: Any,
    ):
        super().__init__()
        if length <= 0:
            raise ValueError("CHAR length must be positive")

        if startswith and len(startswith) >= length:
            raise ValueError(f"startswith '{startswith}' is too long for CHAR({length})")
        if endswith and len(endswith) >= length:
            raise ValueError(f"endswith '{endswith}' is too long for CHAR({length})")
        if startswith and endswith and len(startswith) + len(endswith) > length:
            raise ValueError(f"startswith + endswith is too long for CHAR({length})")

        self.length = length
        self.startswith = startswith
        self.endswith = endswith
        self.strip_whitespace = strip_whitespace
        self.to_lower = to_lower
        self.to_upper = to_upper
        self.pydantic_kwargs = pydantic_kwargs

    @property
    def sql_type(self) -> str:
        return f"CHAR({self.length})"

    @property
    def python_type(self) -> type[str]:
        return str

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic constr type if available."""
        if PYDANTIC_AVAILABLE:
            # Build pattern from startswith/endswith if present
            pattern = None
            if self.startswith or self.endswith:
                import re

                if self.startswith and self.endswith:
                    pattern = f"^{re.escape(self.startswith)}.*{re.escape(self.endswith)}$"
                elif self.startswith:
                    pattern = f"^{re.escape(self.startswith)}.*"
                elif self.endswith:
                    pattern = f".*{re.escape(self.endswith)}$"

            # CHAR allows up to length, but we pad on serialize
            return constr(
                max_length=self.length,
                pattern=pattern,
                strip_whitespace=self.strip_whitespace,
                to_lower=self.to_lower,
                to_upper=self.to_upper,
                **self.pydantic_kwargs,
            )
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value).__name__}")

        # Apply transformations first
        processed = value
        if self.strip_whitespace:
            processed = processed.strip()
        if self.to_lower:
            processed = processed.lower()
        elif self.to_upper:
            processed = processed.upper()

        if len(processed) > self.length:
            raise ValueError(f"String length {len(processed)} exceeds maximum {self.length}")

        if self.startswith and not processed.startswith(self.startswith):
            raise ValueError(f"String must start with '{self.startswith}'")

        if self.endswith and not processed.endswith(self.endswith):
            raise ValueError(f"String must end with '{self.endswith}'")

    def _serialize(self, value: str) -> str:
        # Pad with spaces to match CHAR behavior
        return value.ljust(self.length)

    def _deserialize(self, value: Any) -> str:
        # Convert to string and strip trailing spaces (typical CHAR retrieval)
        result = str(value).rstrip()
        # Apply transformations
        if self.strip_whitespace:
            result = result.strip()
        if self.to_lower:
            result = result.lower()
        elif self.to_upper:
            result = result.upper()
        return result

    def __repr__(self) -> str:
        parts = [f"CHAR({self.length}"]
        if self.startswith:
            parts.append(f"startswith={self.startswith!r}")
        if self.endswith:
            parts.append(f"endswith={self.endswith!r}")
        if self.strip_whitespace:
            parts.append("strip_whitespace=True")
        if self.to_lower:
            parts.append("to_lower=True")
        if self.to_upper:
            parts.append("to_upper=True")
        if self.pydantic_kwargs:
            parts.extend(f"{k}={v!r}" for k, v in self.pydantic_kwargs.items())

        if len(parts) > 1:
            return f"{parts[0]}, {', '.join(parts[1:])})"
        return parts[0] + ")"

    def _generate_mock(self, fake: Any) -> str:
        """Generate mock CHAR data respecting constraints."""
        # Handle startswith/endswith constraints
        if self.startswith or self.endswith:
            prefix = self.startswith or ""
            suffix = self.endswith or ""
            prefix_suffix_len = len(prefix) + len(suffix)

            if prefix_suffix_len >= self.length:
                # No room for random content, just use prefix + suffix
                text = (prefix + suffix)[: self.length]
            else:
                # For CHAR, we need exactly self.length characters
                middle_len = self.length - prefix_suffix_len
                middle = fake.pystr(min_chars=middle_len, max_chars=middle_len)
                text = prefix + middle + suffix
        else:
            text = self._generate_default_char_text(fake)

        # Apply transformations
        if self.strip_whitespace:
            text = text.strip()
        if self.to_lower:
            text = text.lower()
        elif self.to_upper:
            text = text.upper()

        # Ensure exact length (CHAR is fixed-length)
        if len(text) > self.length:
            text = text[: self.length]
        else:
            # Pad with spaces if needed
            text = text.ljust(self.length)

        return text

    def _generate_default_char_text(self, fake: Any) -> str:
        """Generate default CHAR text based on length."""
        if self.length <= 2:
            # For very short CHAR, use country/state codes
            text = fake.country_code()
        elif self.length <= 10:
            # For short CHAR, use a word
            text = fake.word()
        else:
            # For longer CHAR, use appropriate length text
            text = fake.text(max_nb_chars=self.length)
        return text


class TEXT(DBType[str]):
    """Variable-length text with no specific upper limit.

    TEXT is typically used for large text content like descriptions, articles, etc.

    Args:
        max_length: Optional maximum length (database-specific)
        min_length: Minimum length of the text (optional)
        startswith: Text must start with this prefix (optional)
        endswith: Text must end with this suffix (optional)
        strip_whitespace: Whether to strip whitespace (default: False)
        to_lower: Convert to lowercase (default: False)
        to_upper: Convert to uppercase (default: False)
        **pydantic_kwargs: Additional Pydantic-specific arguments

    Examples:
        # Basic usage - unlimited length
        description: Text()

        # With max length constraint
        bio: Text(max_length=5000)

        # Ensure minimum content
        article: Text(min_length=100, max_length=10000)

        # With prefix for structured content
        review: Text(min_length=50, startswith='Review: ')
        feedback: Text(startswith='Customer feedback: ', max_length=1000)
    """

    def __init__(
        self,
        max_length: Optional[int] = None,
        *,  # Force keyword-only args
        min_length: Optional[int] = None,
        startswith: Optional[str] = None,
        endswith: Optional[str] = None,
        strip_whitespace: bool = False,
        to_lower: bool = False,
        to_upper: bool = False,
        **pydantic_kwargs: Any,
    ):
        super().__init__()
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

        self.max_length = max_length
        self.min_length = min_length
        self.startswith = startswith
        self.endswith = endswith
        self.strip_whitespace = strip_whitespace
        self.to_lower = to_lower
        self.to_upper = to_upper
        self.pydantic_kwargs = pydantic_kwargs

    @property
    def sql_type(self) -> str:
        # Most databases don't support CHECK constraints on TEXT
        # but we return basic type
        return "TEXT"

    @property
    def python_type(self) -> type[str]:
        return str

    def get_pydantic_type(self) -> Optional[Any]:
        """Return Pydantic constr type if available."""
        if PYDANTIC_AVAILABLE:
            # Build pattern from startswith/endswith if present
            pattern = None
            if self.startswith or self.endswith:
                import re

                if self.startswith and self.endswith:
                    pattern = f"^{re.escape(self.startswith)}.*{re.escape(self.endswith)}$"
                elif self.startswith:
                    pattern = f"^{re.escape(self.startswith)}.*"
                elif self.endswith:
                    pattern = f".*{re.escape(self.endswith)}$"

            # Only apply constraints if we have them
            kwargs = {
                "strip_whitespace": self.strip_whitespace,
                "to_lower": self.to_lower,
                "to_upper": self.to_upper,
                **self.pydantic_kwargs,
            }
            if self.max_length is not None:
                kwargs["max_length"] = self.max_length
            if self.min_length is not None:
                kwargs["min_length"] = self.min_length
            if pattern is not None:
                kwargs["pattern"] = pattern

            # Only create constr if we have constraints
            if any(k in kwargs for k in ["max_length", "min_length", "pattern"]) or kwargs:
                return constr(**kwargs)
        return None

    def _validate_custom(self, value: Any) -> None:
        """Fallback validation when Pydantic is not available."""
        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value).__name__}")

        # Apply transformations first
        processed = value
        if self.strip_whitespace:
            processed = processed.strip()
        if self.to_lower:
            processed = processed.lower()
        elif self.to_upper:
            processed = processed.upper()

        if self.max_length and len(processed) > self.max_length:
            raise ValueError(f"Text length {len(processed)} exceeds maximum {self.max_length}")

        if self.min_length is not None and len(processed) < self.min_length:
            raise ValueError(f"Text length {len(processed)} is less than minimum {self.min_length}")

        if self.startswith and not processed.startswith(self.startswith):
            raise ValueError(f"Text must start with '{self.startswith}'")

        if self.endswith and not processed.endswith(self.endswith):
            raise ValueError(f"Text must end with '{self.endswith}'")

    def _serialize(self, value: str) -> str:
        # Serialization just returns the value as-is
        # (transformations already applied during deserialization)
        return value

    def _deserialize(self, value: Any) -> str:
        # Convert to string first
        result = str(value)
        # Apply transformations during deserialization
        if self.strip_whitespace:
            result = result.strip()
        if self.to_lower:
            result = result.lower()
        elif self.to_upper:
            result = result.upper()
        return result

    def __repr__(self) -> str:
        parts = ["TEXT("]
        params = []
        if self.max_length is not None:
            params.append(f"max_length={self.max_length}")
        if self.min_length is not None:
            params.append(f"min_length={self.min_length}")
        if self.startswith:
            params.append(f"startswith={self.startswith!r}")
        if self.endswith:
            params.append(f"endswith={self.endswith!r}")
        if self.strip_whitespace:
            params.append("strip_whitespace=True")
        if self.to_lower:
            params.append("to_lower=True")
        if self.to_upper:
            params.append("to_upper=True")
        if self.pydantic_kwargs:
            params.extend(f"{k}={v!r}" for k, v in self.pydantic_kwargs.items())

        return parts[0] + ", ".join(params) + ")"

    def _generate_mock(self, fake: Any) -> str:
        """Generate mock TEXT data respecting constraints."""
        # Handle startswith/endswith constraints
        if self.startswith or self.endswith:
            prefix = self.startswith or ""
            suffix = self.endswith or ""
            prefix_suffix_len = len(prefix) + len(suffix)

            # Determine target length
            if self.max_length and self.min_length:
                target_length = fake.random_int(min=self.min_length, max=self.max_length)
            elif self.max_length:
                target_length = fake.random_int(
                    min=max(prefix_suffix_len + 10, 50), max=self.max_length
                )
            elif self.min_length:
                target_length = fake.random_int(min=self.min_length, max=self.min_length + 500)
            else:
                target_length = fake.random_int(min=200, max=1000)

            # Calculate middle content length
            middle_length = target_length - prefix_suffix_len

            if middle_length <= 0:
                text = (prefix + suffix)[:target_length]
            elif middle_length <= 50:
                # Short text - use pystr for random chars
                middle = fake.pystr(min_chars=middle_length, max_chars=middle_length)
                text = prefix + middle + suffix
            else:
                # Longer text - use meaningful content
                middle = fake.text(max_nb_chars=middle_length * 2)  # Generate extra to trim
                middle = middle.strip()
                if len(middle) > middle_length:
                    middle = middle[:middle_length].rstrip()
                elif len(middle) < middle_length:
                    # Pad with random chars to reach exact length
                    padding_needed = middle_length - len(middle)
                    middle = (
                        middle
                        + " "
                        + fake.pystr(min_chars=padding_needed - 1, max_chars=padding_needed - 1)
                    )
                text = prefix + middle + suffix
        else:
            # Determine target length
            if self.max_length and self.min_length:
                # Generate between min and max
                target_length = fake.random_int(min=self.min_length, max=self.max_length)
            elif self.max_length:
                # Generate up to max
                target_length = fake.random_int(min=10, max=self.max_length)
            elif self.min_length:
                # Generate at least min
                target_length = fake.random_int(min=self.min_length, max=self.min_length + 500)
            else:
                # Default reasonable length
                target_length = 500

            # Generate text
            if target_length <= 200:
                # For smaller text, use paragraph
                text = fake.paragraph(nb_sentences=3)
            else:
                # For larger text, use multiple paragraphs
                text = fake.text(max_nb_chars=target_length)

            # Ensure min length by adding more content if needed
            while self.min_length and len(text) < self.min_length:
                text += " " + fake.paragraph()

        # Apply transformations
        if self.strip_whitespace:
            text = text.strip()
        if self.to_lower:
            text = text.lower()
        elif self.to_upper:
            text = text.upper()

        # Ensure max length
        if self.max_length and len(text) > self.max_length:
            text = text[: self.max_length]

        return text
