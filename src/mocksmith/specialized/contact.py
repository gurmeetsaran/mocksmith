"""Contact information specialized types."""

import re
from typing import Any

from mocksmith.types.string import VARCHAR


class Email(VARCHAR):
    """Email address type with validation."""

    def __init__(self, length: int = 255):
        super().__init__(length)
        # Basic email regex pattern
        self.email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def validate(self, value: Any) -> None:
        """Validate email format in addition to base validation."""
        # First do base VARCHAR validation
        super().validate(value)

        if value is None:
            return

        # Check email format
        if not self.email_pattern.match(value):
            raise ValueError(f"Invalid email format: {value}")

    def _generate_mock(self, fake: Any) -> str:
        """Generate a valid email address."""
        email = fake.email()
        # Ensure it fits within the length constraint
        if len(email) > self.length:
            # Generate a shorter email
            username = fake.user_name()[:10]
            domain = fake.domain_name()
            email = f"{username}@{domain}"
        return email[: self.length]

    def __repr__(self) -> str:
        return f"Email(length={self.length})"


class PhoneNumber(VARCHAR):
    """Phone number type."""

    def __init__(self, length: int = 20):
        super().__init__(length)

    def _generate_mock(self, fake: Any) -> str:
        """Generate a phone number."""
        phone = fake.phone_number()
        return phone[: self.length]

    def __repr__(self) -> str:
        return f"PhoneNumber(length={self.length})"


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
