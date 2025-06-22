"""String database types."""

from typing import Any, Optional

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
    def python_type(self) -> type[str]:
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

    def _generate_mock(self, fake: Any) -> str:
        """Generate mock VARCHAR data."""
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

        # Ensure the text fits within the length constraint
        return text[: self.length]


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
    def python_type(self) -> type[str]:
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

    def _generate_mock(self, fake: Any) -> str:
        """Generate mock CHAR data."""
        # CHAR is fixed-length, so we generate appropriate data
        if self.length <= 2:
            # For very short CHAR, use country/state codes
            text = fake.country_code()
        elif self.length <= 10:
            # For short CHAR, use a word
            text = fake.word()
        else:
            # For longer CHAR, use appropriate length text
            text = fake.text(max_nb_chars=self.length)

        # Ensure exact length (CHAR is fixed-length)
        if len(text) > self.length:
            return text[: self.length]
        else:
            # Pad with spaces if needed
            return text.ljust(self.length)


class TEXT(DBType[str]):
    """Variable-length text with no specific upper limit."""

    def __init__(self, max_length: Optional[int] = None):
        super().__init__()
        self.max_length = max_length

    @property
    def sql_type(self) -> str:
        return "TEXT"

    @property
    def python_type(self) -> type[str]:
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

    def _generate_mock(self, fake: Any) -> str:
        """Generate mock TEXT data."""
        if self.max_length:
            if self.max_length <= 200:
                # For smaller text, use paragraph
                text = fake.paragraph(nb_sentences=3)
            else:
                # For larger text, use multiple paragraphs
                text = fake.text(max_nb_chars=min(self.max_length, 1000))

            # Ensure it fits within max_length
            return text[: self.max_length]
        else:
            # No limit, generate a reasonable amount of text
            return fake.text(max_nb_chars=500)
