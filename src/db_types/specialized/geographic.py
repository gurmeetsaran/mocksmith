"""Geographic specialized types."""

from typing import Any

from db_types.types.string import CHAR, VARCHAR


class CountryCode(CHAR):
    """ISO 3166-1 alpha-2 country code (2 characters)."""

    def __init__(self):
        super().__init__(2)

    def _generate_mock(self, fake: Any) -> str:
        """Generate a country code."""
        return fake.country_code()

    def __repr__(self) -> str:
        return "CountryCode()"


class State(VARCHAR):
    """State or province name."""

    def __init__(self, length: int = 50):
        super().__init__(length)

    def _generate_mock(self, fake: Any) -> str:
        """Generate a state/province name."""
        # Try to get state name, fallback to generic word if not available
        try:
            state = fake.state()
            return state[: self.length]
        except AttributeError:
            # Fallback for locales without states
            return fake.city()[: self.length]

    def __repr__(self) -> str:
        return f"State(length={self.length})"


class City(VARCHAR):
    """City name."""

    def __init__(self, length: int = 100):
        super().__init__(length)

    def _generate_mock(self, fake: Any) -> str:
        """Generate a city name."""
        city = fake.city()
        return city[: self.length]

    def __repr__(self) -> str:
        return f"City(length={self.length})"


class ZipCode(VARCHAR):
    """Postal/ZIP code."""

    def __init__(self, length: int = 10):
        super().__init__(length)

    def _generate_mock(self, fake: Any) -> str:
        """Generate a postal code."""
        postcode = fake.postcode()
        return postcode[: self.length]

    def __repr__(self) -> str:
        return f"ZipCode(length={self.length})"
