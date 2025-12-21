"""Example showing Pydantic usage with mocksmith including specialized types."""

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum, auto
from typing import Annotated, Optional

from pydantic import (
    UUID4,
    BaseModel,
    EmailStr,
    HttpUrl,
    IPvAnyAddress,
    PositiveInt,
    SecretStr,
    ValidationError,
    conint,
    constr,
)

from mocksmith import (  # Basic types with clean syntax for Pydantic
    Boolean,
    Date,
    DecimalType,
    Integer,
    Varchar,
    mockable,
)
from mocksmith.pydantic_integration import DBTypeValidator
from mocksmith.specialized import City as CityType
from mocksmith.specialized import CountryCode as CountryCodeType
from mocksmith.specialized import PhoneNumber as PhoneNumberType
from mocksmith.specialized import ZipCode as ZipCodeType


# Example 1: Basic Pydantic model with clean syntax
@mockable
class User(BaseModel):
    """Simple user model using clean syntax.

    These annotation functions work seamlessly with Pydantic!
    """

    id: Integer()
    name: Varchar(50)
    age: Integer()
    balance: DecimalType(10, 2)
    is_active: Boolean()
    joined: Date()


# Example 2: Pydantic model with specialized types
@mockable
class Customer(BaseModel):
    """Customer model with specialized types.

    Note: For Pydantic, specialized types need DBTypeValidator wrapper.
    """

    id: Integer()
    name: Varchar(100)

    # Specialized types - need explicit Annotated with DBTypeValidator for Pydantic
    email: EmailStr  # Now using Pydantic's built-in EmailStr
    phone: Annotated[str, DBTypeValidator(PhoneNumberType())]
    country: Annotated[str, DBTypeValidator(CountryCodeType())]
    city: Annotated[str, DBTypeValidator(CityType())]
    postal_code: Annotated[str, DBTypeValidator(ZipCodeType())]

    # Additional fields with clean syntax
    credit_limit: DecimalType(10, 2)
    registered: Date()


def demo_basic_usage():
    """Demonstrate basic Pydantic usage."""
    print("=== Basic Pydantic Usage (Validation) ===\n")

    # Create a valid user
    user = User(
        id=1,
        name="John Doe",
        age=30,
        balance=Decimal("1000.00"),
        is_active=True,
        joined=date(2020, 1, 1),
    )

    print("Created User:")
    print(f"  ID: {user.id}")
    print(f"  Name: {user.name}")
    print(f"  Age: {user.age}")
    print(f"  Balance: ${user.balance}")
    print(f"  Active: {user.is_active}")
    print(f"  Joined: {user.joined}")

    # Validation happens automatically
    print("\nValidation examples:")
    try:
        # This will fail - name too long
        User(
            id=2,
            name="x" * 100,  # Exceeds Varchar(50)
            age=25,
            balance=Decimal("500.00"),
            is_active=True,
            joined=date(2024, 1, 1),
        )
    except ValidationError as e:
        print("  ✅ Validation correctly failed for long name")
        print(f"     Error: {e.errors()[0]['msg']}")


def demo_specialized_types():
    """Demonstrate specialized types with Pydantic."""
    print("\n\n=== Specialized Types with Pydantic ===\n")

    # Create a valid customer
    customer = Customer(
        id=12345,
        name="Jane Smith",
        email="jane.smith@example.com",
        phone="+1-555-987-6543",
        country="US",
        city="San Francisco",
        postal_code="94105",
        credit_limit=Decimal("10000.00"),
        registered=date(2024, 1, 1),
    )

    print("Created Customer:")
    print(f"  Name: {customer.name}")
    print(f"  Email: {customer.email}")
    print(f"  Phone: {customer.phone}")
    print(f"  Country: {customer.country}")
    print(f"  City: {customer.city}")
    print(f"  Postal: {customer.postal_code}")

    # Validation examples
    print("\nValidation examples:")

    # Invalid email
    try:
        Customer(
            id=2,
            name="Test User",
            email="invalid-email",  # Will fail EMAIL validation
            phone="+1-555-123-4567",
            country="US",
            city="New York",
            postal_code="10001",
            credit_limit=Decimal("5000.00"),
            registered=date(2024, 1, 1),
        )
    except ValidationError as e:
        print("  ✅ Email validation correctly failed")
        print(f"     Error: {e.errors()[0]['msg']}")

    # Invalid country code
    try:
        Customer(
            id=3,
            name="Test User",
            email="test@example.com",
            phone="+1-555-123-4567",
            country="USA",  # Should be 2 chars
            city="New York",
            postal_code="10001",
            credit_limit=Decimal("5000.00"),
            registered=date(2024, 1, 1),
        )
    except ValidationError as e:
        print("  ✅ Country validation correctly failed")
        print(f"     Error: {e.errors()[0]['msg']}")


def demo_mock_generation():
    """Demonstrate mock generation for Pydantic models."""
    print("\n\n=== Pydantic Mocking with @mockable ===\n")

    print("With @mockable decorator, Pydantic models work just like dataclasses!\n")

    # Generate a mock user
    print("Basic model mocking:")
    user = User.mock()
    print("  Generated User:")
    print(f"    ID: {user.id}")
    print(f"    Name: {user.name}")
    print(f"    Age: {user.age}")
    print(f"    Balance: ${user.balance}")
    print(f"    Active: {user.is_active}")
    print(f"    Joined: {user.joined}")

    # Generate with overrides
    print("\n  With overrides:")
    custom_user = User.mock(name="Alice Johnson", age=28)
    print(f"    Name: {custom_user.name}")
    print(f"    Age: {custom_user.age}")

    # Using builder pattern
    print("\n  Using builder pattern:")
    builder_user = (
        User.mock_builder().with_name("Bob Wilson").with_age(35).with_is_active(True).build()
    )
    print(f"    Name: {builder_user.name}")
    print(f"    Age: {builder_user.age}")
    print(f"    Active: {builder_user.is_active}")

    # Mock individual fields
    print("\n\nMocking individual fields:")
    print(f"  Name: {Varchar(50).mock()}")
    # Note: Email type was removed - use Pydantic's EmailStr instead
    print(f"  Country: {CountryCodeType().mock()}")
    print(f"  City: {CityType().mock()}")
    print(f"  Phone: {PhoneNumberType().mock()}")

    # Mock Customer with specialized types
    print("\n\nMocking Customer with specialized types:")
    try:
        # Basic mock generation
        mock_customer = Customer.mock()
        print("  ✅ Successfully mocked Customer:")
        print(f"     Name: {mock_customer.name}")
        print(f"     Email: {mock_customer.email}")
        print(f"     Country: {mock_customer.country}")
        print(f"     City: {mock_customer.city}")
        print(f"     Phone: {mock_customer.phone}")

        # Mock with overrides
        print("\n  With overrides:")
        custom_customer = Customer.mock(name="Global Corp Inc.", country="US", city="New York")
        print(f"     Name: {custom_customer.name}")
        print(f"     Country: {custom_customer.country}")
        print(f"     City: {custom_customer.city}")

        # Using builder pattern
        print("\n  Using builder pattern:")
        builder_customer = (
            Customer.mock_builder()
            .with_name("Tech Solutions Ltd.")
            .with_country("GB")
            .with_city("London")
            .with_email("contact@techsolutions.co.uk")
            .build()
        )
        print(f"     Name: {builder_customer.name}")
        print(f"     Email: {builder_customer.email}")
        print(f"     Country: {builder_customer.country}")
        print(f"     City: {builder_customer.city}")

    except Exception as e:
        print(f"  ❌ Mock generation failed: {e}")


def show_pydantic_notes():
    """Show important notes about Pydantic usage."""
    print("\n\n=== Important Notes for Pydantic ===\n")

    print("1. CLEAN SYNTAX FOR BASIC TYPES:")
    print("   • Use Varchar(50), Integer(), etc. - works automatically!")
    print("   • The annotation functions handle DBTypeValidator wrapping")

    print("\n2. USE PYDANTIC BUILT-IN TYPES WHERE AVAILABLE:")
    print("   • email: EmailStr  # Pydantic's built-in email type")
    print("   • For other specialized types like PhoneNumber, use DBTypeValidator")

    print("\n3. MOCKING NOW WORKS WITH @mockable!")
    print("   • Pydantic models support @mockable decorator just like dataclasses")
    print("   • Automatic mock generation with .mock() class method")
    print("   • Type-safe builder pattern with .mock_builder()")
    print("   • Individual type .mock() methods still available")

    print("\n4. AUTOMATIC VALIDATION:")
    print("   • Validation happens automatically on model creation")
    print("   • All db_type constraints are enforced")
    print("   • Get detailed error messages with ValidationError")

    print("\n5. ENUM SUPPORT:")
    print("   • Python enums work automatically with @mockable")
    print("   • Mock generation randomly selects from enum values")
    print("   • Pydantic validates enum field assignments")

    print("\n6. PYDANTIC BUILT-IN TYPES:")
    print("   • Full support for HttpUrl, EmailStr, IPvAnyAddress, UUID4, etc.")
    print("   • Constraint types: conint, constr with min/max/pattern")
    print("   • Numeric constraints: PositiveInt, NegativeFloat, etc.")
    print("   • All constraints respected during mock generation")


# Example 3: Enums for mock generation
class UserRole(Enum):
    """User roles in the system."""

    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"


class AccountStatus(Enum):
    """Account status using auto() values."""

    ACTIVE = auto()
    SUSPENDED = auto()
    PENDING = auto()
    CLOSED = auto()


@mockable
class Employee(BaseModel):
    """Employee model with enum fields."""

    id: Integer()
    name: Varchar(100)
    email: EmailStr
    role: UserRole
    status: AccountStatus
    department: Optional[str] = None
    hire_date: Date()


# Example 4: Pydantic built-in types
@mockable
class ServerConfig(BaseModel):
    """Server configuration using Pydantic built-in types."""

    # Network types
    hostname: constr(min_length=1, max_length=253)
    ip_address: IPvAnyAddress
    port: conint(ge=1, le=65535)
    api_url: HttpUrl

    # Numeric types
    max_connections: PositiveInt
    cpu_limit: conint(ge=1, le=100)  # Percentage

    # String types
    server_id: UUID4
    api_key: SecretStr

    # Optional fields
    backup_url: Optional[HttpUrl] = None


def demo_enum_mocking():
    """Demonstrate enum support in Pydantic mock generation."""
    print("\n\n=== Enum Mock Generation (Pydantic) ===\n")

    # Generate an employee
    employee = Employee.mock()
    print("Generated employee:")
    print(f"  ID: {employee.id}")
    print(f"  Name: {employee.name}")
    print(f"  Email: {employee.email}")
    print(f"  Role: {employee.role.value} (enum: {employee.role.name})")
    print(f"  Status: {employee.status.name} (value: {employee.status.value})")
    print(f"  Department: {employee.department}")
    print(f"  Hire Date: {employee.hire_date}")

    # Validation still works
    print("\nValidation with enums:")
    try:
        # This should fail - can't assign string to enum
        Employee(
            id=1,
            name="Test User",
            email="test@example.com",
            role="admin",  # Should be UserRole.ADMIN
            status=AccountStatus.ACTIVE,
            hire_date=datetime.now(timezone.utc).date(),
        )
        print("  ERROR: Should have failed validation!")
    except ValidationError:
        print("  ✅ Validation correctly enforces enum types")


def demo_pydantic_builtin_types():
    """Demonstrate Pydantic built-in types support."""
    print("\n\n=== Pydantic Built-in Types ===\n")

    # Generate server config
    server = ServerConfig.mock()
    print("Generated server config:")
    print(f"  Hostname: {server.hostname}")
    print(f"  IP: {server.ip_address}")
    print(f"  Port: {server.port}")
    print(f"  API URL: {server.api_url}")
    print(f"  Max Connections: {server.max_connections}")
    print(f"  CPU Limit: {server.cpu_limit}%")
    print(f"  Server ID: {server.server_id}")
    print(f"  API Key: {'*' * 8} (hidden)")
    print(f"  Backup URL: {server.backup_url}")

    # Builder pattern with constraints
    print("\nUsing builder with Pydantic types:")
    custom_server = (
        ServerConfig.mock_builder()
        .with_hostname("api.example.com")
        .with_port(443)
        .with_api_url("https://api.example.com")
        .build()
    )
    print(f"  Custom hostname: {custom_server.hostname}")
    print(f"  Custom port: {custom_server.port}")
    print(f"  Custom URL: {custom_server.api_url}")

    # Validation example
    print("\nPydantic constraint validation:")
    try:
        # This should fail - port out of range
        ServerConfig.mock(port=70000)  # > 65535
    except ValidationError:
        print("  ✅ Validation correctly failed: port > 65535")


if __name__ == "__main__":
    demo_basic_usage()
    demo_specialized_types()
    demo_mock_generation()
    demo_enum_mocking()
    demo_pydantic_builtin_types()
    show_pydantic_notes()
