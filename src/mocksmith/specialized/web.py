"""Web-related specialized types."""

import ipaddress
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


class IPAddress(VARCHAR):
    """IP address type that accepts both IPv4 and IPv6 addresses."""

    def __init__(self):
        # IPv6 max length is 39 chars (8 groups of 4 hex digits + 7 colons)
        # But with IPv4 mapped IPv6 it can be up to 45 chars
        super().__init__(45)

    def validate(self, value: Any) -> None:
        """Validate IP address format."""
        if value is None:
            return

        # Convert to string if needed
        value_str = str(value)

        # Validate using ipaddress module
        try:
            ipaddress.ip_address(value_str)
        except ValueError as e:
            raise ValueError(f"Invalid IP address format: {value}") from e

    def _generate_mock(self, fake: Any) -> str:
        """Generate a random IP address (IPv4 or IPv6)."""
        # 80% chance of IPv4, 20% chance of IPv6
        if fake.boolean(chance_of_getting_true=80):
            return fake.ipv4()
        else:
            return fake.ipv6()

    def __repr__(self) -> str:
        return "IPAddress()"


class IPv4Address(VARCHAR):
    """IPv4 address type with validation."""

    def __init__(self):
        # IPv4 max length is 15 chars (xxx.xxx.xxx.xxx)
        super().__init__(15)

    def validate(self, value: Any) -> None:
        """Validate IPv4 address format."""
        if value is None:
            return

        # Convert to string if needed
        value_str = str(value)

        # Validate using ipaddress module
        try:
            ipaddress.IPv4Address(value_str)
        except ValueError as e:
            raise ValueError(f"Invalid IPv4 address format: {value}") from e

    def _generate_mock(self, fake: Any) -> str:
        """Generate a random IPv4 address."""
        return fake.ipv4()

    def __repr__(self) -> str:
        return "IPv4Address()"


class IPv6Address(VARCHAR):
    """IPv6 address type with validation."""

    def __init__(self):
        # IPv6 max length is 39 chars (8 groups of 4 hex digits + 7 colons)
        super().__init__(39)

    def validate(self, value: Any) -> None:
        """Validate IPv6 address format."""
        if value is None:
            return

        # Convert to string if needed
        value_str = str(value)

        # Validate using ipaddress module
        try:
            ipaddress.IPv6Address(value_str)
        except ValueError as e:
            raise ValueError(f"Invalid IPv6 address format: {value}") from e

    def _generate_mock(self, fake: Any) -> str:
        """Generate a random IPv6 address."""
        return fake.ipv6()

    def __repr__(self) -> str:
        return "IPv6Address()"
