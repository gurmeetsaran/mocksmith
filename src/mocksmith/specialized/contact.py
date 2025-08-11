"""Contact information specialized types using V3 pattern."""

from typing import Optional

from mocksmith.types.string import Varchar


def PhoneNumber(length: int = 20) -> type:  # noqa: N802
    """Phone number type.

    Example:
        class Customer(BaseModel):
            phone: PhoneNumber()
            mobile: PhoneNumber(15)
    """
    VarcharType = Varchar(length)  # noqa: N806

    class PhoneNumberType(VarcharType):
        @classmethod
        def mock(cls) -> str:
            """Generate a phone number."""
            try:
                from faker import Faker  # type: ignore

                fake = Faker()
                phone = fake.phone_number()
                return phone[: cls._length]
            except ImportError:
                raise ImportError("faker library is required for mock generation") from None

    return PhoneNumberType


def Email(  # noqa: N802
    length: int = 100, *, to_lower: bool = True, domain: Optional[str] = None
) -> type:
    """Email address type.

    Example:
        class User(BaseModel):
            email: Email()
            work_email: Email(domain='company.com')
    """
    endswith = f"@{domain}" if domain else None
    VarcharType = Varchar(length, to_lower=to_lower, endswith=endswith)  # noqa: N806

    class EmailType(VarcharType):
        @classmethod
        def mock(cls) -> str:
            """Generate an email address."""
            try:
                from faker import Faker  # type: ignore

                fake = Faker()

                if cls._endswith and cls._endswith.startswith("@"):
                    # Generate email with specific domain
                    domain = cls._endswith[1:]
                    username = fake.user_name()
                    email = f"{username}@{domain}"
                else:
                    email = fake.email()

                # Apply transformations
                if cls._to_lower:
                    email = email.lower()
                elif cls._to_upper:
                    email = email.upper()

                # Ensure max length
                if len(email) > cls._length:
                    # Truncate username part if too long
                    at_index = email.index("@")
                    domain_part = email[at_index:]
                    max_username_len = cls._length - len(domain_part)
                    username = email[:at_index][:max_username_len]
                    email = username + domain_part

                return email
            except ImportError:
                raise ImportError("faker library is required for mock generation") from None

    return EmailType
