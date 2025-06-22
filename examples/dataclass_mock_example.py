"""Example showing dataclass usage with db_types including mocking and specialized types."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from db_types import (  # Basic types with clean syntax; For mocking
    Boolean,
    Date,
    DecimalType,
    Integer,
    Varchar,
    mockable,
)
from db_types.dataclass_integration import validate_dataclass
from db_types.specialized import (  # Specialized types - work directly with dataclasses
    City,
    CountryCode,
    Email,
    PhoneNumber,
    ZipCode,
)


# Example 1: Basic dataclass with db_types
@mockable
@dataclass
class User:
    """Simple user model with clean syntax."""

    id: Integer()
    name: Varchar(50)
    age: Integer()
    balance: DecimalType(10, 2)
    is_active: Boolean()
    joined: Date()


# Example 2: Dataclass with specialized types
@mockable
@validate_dataclass
@dataclass
class Customer:
    """Customer model with specialized types.

    Note: For dataclasses, we can use specialized types directly!
    """

    id: Integer()
    name: Varchar(100)

    # Specialized types - these work out of the box with dataclasses!
    email: Email
    phone: PhoneNumber
    country: CountryCode
    city: City
    postal_code: ZipCode

    # Additional fields
    credit_limit: DecimalType(10, 2)
    registered: Date()

    def __init__(self):
        """Initialize the specialized type instances."""
        self.email = Email()
        self.phone = PhoneNumber()
        self.country = CountryCode()
        self.city = City()
        self.postal_code = ZipCode()


def demo_basic_mocking():
    """Demonstrate basic mocking with dataclasses."""
    print("=== Basic Dataclass Mocking ===\n")

    # Generate a mock user
    user = User.mock()
    print("Generated User:")
    print(f"  ID: {user.id}")
    print(f"  Name: {user.name}")
    print(f"  Age: {user.age}")
    print(f"  Balance: ${user.balance}")
    print(f"  Active: {user.is_active}")
    print(f"  Joined: {user.joined}")

    # Generate with overrides
    print("\nWith overrides:")
    custom_user = User.mock(name="John Doe", age=30, balance=Decimal("1000.00"))
    print(f"  Name: {custom_user.name}")
    print(f"  Age: {custom_user.age}")
    print(f"  Balance: ${custom_user.balance}")

    # Using builder pattern
    print("\nUsing builder pattern:")
    builder_user = (
        User.mock_builder().with_name("Jane Smith").with_age(25).with_is_active(True).build()
    )
    print(f"  Name: {builder_user.name}")
    print(f"  Age: {builder_user.age}")
    print(f"  Active: {builder_user.is_active}")


def demo_specialized_types():
    """Demonstrate specialized types with dataclasses."""
    print("\n\n=== Specialized Types with Dataclasses ===\n")

    # Create a customer template
    customer_template = Customer()

    # Manual creation with validation
    print("Manual creation:")
    try:
        valid_customer = Customer()
        # Set values that will be validated
        valid_customer.id = 12345
        valid_customer.name = "John Doe"
        valid_customer.email.validate("john.doe@example.com")
        valid_customer.country.validate("US")
        valid_customer.city.validate("New York")
        valid_customer.postal_code.validate("10001")
        valid_customer.phone.validate("+1-555-123-4567")
        valid_customer.credit_limit = Decimal("5000.00")
        valid_customer.registered = date(2024, 1, 1)

        print("  ✅ Valid customer created")
        print("  Email validation passed for: john.doe@example.com")
        print("  Country validation passed for: US")

    except ValueError as e:
        print(f"  ❌ Validation failed: {e}")

    # Mock generation for specialized types
    print("\nMock generation for specialized types:")
    print("(Note: Specialized types need direct mocking)")

    print(f"  Email mock: {customer_template.email.mock()}")
    print(f"  Phone mock: {customer_template.phone.mock()}")
    print(f"  Country mock: {customer_template.country.mock()}")
    print(f"  City mock: {customer_template.city.mock()}")
    print(f"  Postal code mock: {customer_template.postal_code.mock()}")

    # Validation example
    print("\nValidation example:")
    try:
        # This will fail - invalid email format
        customer_template.email.validate("invalid-email")
    except ValueError as e:
        print(f"  ✅ Email validation correctly failed: {e}")

    try:
        # This will fail - country code too long
        customer_template.country.validate("USA")  # Should be 2 chars
    except ValueError as e:
        print(f"  ✅ Country validation correctly failed: {e}")


def show_dataclass_notes():
    """Show important notes about dataclass usage."""
    print("\n\n=== Important Notes for Dataclasses ===\n")

    print("1. CLEAN SYNTAX:")
    print("   • Use Varchar(50), Integer(), etc. for basic types")
    print("   • These work automatically with @mockable decorator")

    print("\n2. SPECIALIZED TYPES:")
    print("   • Can use Email, Country, etc. directly")
    print("   • Need to instantiate in __init__ method")
    print("   • Each instance has .mock() and .validate() methods")

    print("\n3. MOCKING:")
    print("   • @mockable adds .mock() and .mock_builder() class methods")
    print("   • Basic types are automatically mocked")
    print("   • Specialized types need manual mocking (for now)")

    print("\n4. VALIDATION:")
    print("   • @validate_dataclass adds automatic validation")
    print("   • Each db_type has .validate() method")
    print("   • Specialized types include format validation (email, URL, etc.)")


if __name__ == "__main__":
    demo_basic_mocking()
    demo_specialized_types()
    show_dataclass_notes()
