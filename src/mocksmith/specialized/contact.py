"""Contact information specialized types."""

from typing import Any

from mocksmith.types.string import VARCHAR


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
