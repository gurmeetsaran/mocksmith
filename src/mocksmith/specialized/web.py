"""Web-related specialized types."""

import re
from typing import Any

from mocksmith.types.string import VARCHAR


class URL(VARCHAR):
    """URL type with basic validation."""

    def __init__(self, length: int = 2083):  # Common max URL length
        super().__init__(length)
        # Basic URL pattern
        self.url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

    def validate(self, value: Any) -> None:
        """Validate URL format in addition to base validation."""
        # First do base VARCHAR validation
        super().validate(value)

        if value is None:
            return

        # Check URL format
        if not self.url_pattern.match(value):
            raise ValueError(f"Invalid URL format: {value}")

    def _generate_mock(self, fake: Any) -> str:
        """Generate a valid URL."""
        url = fake.url()
        return url[: self.length]

    def __repr__(self) -> str:
        return f"URL(length={self.length})"
