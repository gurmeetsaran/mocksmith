"""Geographic specialized types using V3 pattern."""

from mocksmith.types.string import Char, Varchar


def CountryCode() -> type:  # noqa: N802
    """ISO 3166-1 alpha-2 country code (2 characters).

    Example:
        class Address(BaseModel):
            country: CountryCode()
    """
    CharType = Char(2, to_upper=True)  # noqa: N806

    class CountryCodeType(CharType):
        @classmethod
        def mock(cls) -> str:
            """Generate a country code."""
            try:
                from faker import Faker  # type: ignore

                fake = Faker()
                return fake.country_code().upper()
            except ImportError:
                raise ImportError("faker library is required for mock generation") from None

    return CountryCodeType


def State(length: int = 50) -> type:  # noqa: N802
    """State or province name.

    Example:
        class Address(BaseModel):
            state: State()
            province: State(100)
    """
    VarcharType = Varchar(length)  # noqa: N806

    class StateType(VarcharType):
        @classmethod
        def mock(cls) -> str:
            """Generate a state/province name."""
            try:
                from faker import Faker  # type: ignore

                fake = Faker()
                # Try to get state name, fallback to generic word if not available
                try:
                    state = fake.state()
                    return state[: cls._length]
                except AttributeError:
                    # Fallback for locales without states
                    return fake.city()[: cls._length]
            except ImportError:
                raise ImportError("faker library is required for mock generation") from None

    return StateType


def City(length: int = 100) -> type:  # noqa: N802
    """City name.

    Example:
        class Address(BaseModel):
            city: City()
            hometown: City(50)
    """
    VarcharType = Varchar(length)  # noqa: N806

    class CityType(VarcharType):
        @classmethod
        def mock(cls) -> str:
            """Generate a city name."""
            try:
                from faker import Faker  # type: ignore

                fake = Faker()
                city = fake.city()
                return city[: cls._length]
            except ImportError:
                raise ImportError("faker library is required for mock generation") from None

    return CityType


def ZipCode(length: int = 10) -> type:  # noqa: N802
    """Postal/ZIP code.

    Example:
        class Address(BaseModel):
            zip_code: ZipCode()
            postal_code: ZipCode(6)
    """
    VarcharType = Varchar(length)  # noqa: N806

    class ZipCodeType(VarcharType):
        @classmethod
        def mock(cls) -> str:
            """Generate a postal code."""
            try:
                from faker import Faker  # type: ignore

                fake = Faker()
                postcode = fake.postcode()
                return postcode[: cls._length]
            except ImportError:
                raise ImportError("faker library is required for mock generation") from None

    return ZipCodeType
