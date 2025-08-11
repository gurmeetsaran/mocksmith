"""Example showing dataclass usage with mocksmith including mocking and specialized types."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum, auto
from typing import Optional

from mocksmith import (  # Basic types with clean syntax; For mocking
    Boolean,
    Date,
    DecimalType,
    Integer,
    Varchar,
    mockable,
)

# Note: validate_dataclass removed - use Pydantic for validation


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
@dataclass
class Customer:
    """Customer model with specialized types."""

    id: Integer()
    name: Varchar(100)
    email: Varchar(255)
    phone: Varchar(50)  # Phone number (faker can generate long formats)
    country: Varchar(50)  # Country name (will be truncated in display)
    city: Varchar(100)
    postal_code: Varchar(20)  # Postal code
    credit_limit: DecimalType(10, 2)
    registered: Date()


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
    """Demonstrate mock generation with specialized types."""
    print("\n\n=== Mock Generation with Specialized Types ===\n")

    # Generate a mock customer
    customer = Customer.mock()
    print("Generated Customer:")
    print(f"  ID: {customer.id}")
    print(f"  Name: {customer.name}")
    print(f"  Email: {customer.email}")
    print(f"  Phone: {customer.phone}")
    print(f"  Country: {customer.country}")
    print(f"  City: {customer.city}")
    print(f"  Postal Code: {customer.postal_code}")
    print(f"  Credit Limit: ${customer.credit_limit}")
    print(f"  Registered: {customer.registered}")

    print("\nNote: Mock data is generated based on field types:")
    print("  • Varchar fields generate random strings of appropriate length")
    print("  • Integer fields generate random integers")
    print("  • Date fields generate random dates")
    print("  • DecimalType fields generate random decimal values")

    # Mock generation with overrides
    print("\nMock with overrides:")
    us_customer = Customer.mock(
        name="John Smith", country="US", city="New York", postal_code="10001"
    )
    print(f"  Name: {us_customer.name}")
    print(f"  Country: {us_customer.country}")
    print(f"  City: {us_customer.city}")
    print(f"  Postal Code: {us_customer.postal_code}")

    # Note about validation
    print("\nNote: Plain dataclasses don't validate.")
    # Creating a customer with invalid data will succeed:
    Customer(
        id=1,
        name="Test",
        email="x" * 300,  # Too long for Varchar(255) but accepted!
        phone="555-1234",
        country="US",
        city="Boston",
        postal_code="02101",
        credit_limit=Decimal("1000.00"),
        registered=datetime.now(timezone.utc).date(),
    )
    print("  ⚠️ Dataclass accepted email with 300 chars (no validation)")
    print("  → Use Pydantic BaseModel for validation")


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


class SubscriptionTier(Enum):
    """Subscription tiers with numeric values."""

    FREE = 0
    BASIC = 1
    PREMIUM = 2
    ENTERPRISE = 3


@mockable
@dataclass
class Employee:
    """Employee model with enum fields."""

    id: Integer()
    name: Varchar(100)
    email: Varchar(255)
    role: UserRole
    status: AccountStatus
    subscription: SubscriptionTier
    department: Optional[str] = None
    hire_date: Date() = None


def demo_enum_mocking():
    """Demonstrate enum support in mock generation."""
    print("\n\n=== Enum Mock Generation ===\n")

    # Generate a single employee
    employee = Employee.mock()
    print("Generated employee:")
    print(f"  ID: {employee.id}")
    print(f"  Name: {employee.name}")
    print(f"  Email: {employee.email}")
    print(f"  Role: {employee.role.value} (enum: {employee.role.name})")
    print(f"  Status: {employee.status.name} (value: {employee.status.value})")
    print(f"  Subscription: {employee.subscription.name} (tier: {employee.subscription.value})")
    print(f"  Department: {employee.department}")
    print(f"  Hire Date: {employee.hire_date}")

    # Generate multiple to show randomness
    print("\nGenerating 10 employees to show enum distribution:")
    employees = [Employee.mock() for _ in range(10)]

    role_counts = {}
    for emp in employees:
        role_counts[emp.role.value] = role_counts.get(emp.role.value, 0) + 1

    print("\nRole distribution:")
    for role, count in sorted(role_counts.items()):
        print(f"  {role}: {count} employees")

    # Using builder pattern with enums
    print("\nUsing builder pattern with specific enum values:")
    admin = (
        Employee.mock_builder()
        .with_name("Admin User")
        .with_role(UserRole.ADMIN)
        .with_status(AccountStatus.ACTIVE)
        .with_subscription(SubscriptionTier.ENTERPRISE)
        .build()
    )
    print(f"Built admin: {admin.name}")
    print(f"  Role: {admin.role.value}")
    print(f"  Status: {admin.status.name}")
    print(f"  Subscription: {admin.subscription.name}")


def show_dataclass_notes():
    """Show important notes about dataclass usage."""
    print("\n\n=== Important Notes for Dataclasses ===\n")

    print("1. CLEAN SYNTAX:")
    print("   • Use Varchar(50), Integer(), etc. for basic types")
    print("   • These work automatically with @mockable decorator")

    print("\n2. SPECIALIZED TYPES:")
    print("   • Use regular types with appropriate constraints")
    print("   • e.g., Varchar(2) for country codes, Varchar(20) for phone")
    print("   • Mock generation creates random data respecting constraints")

    print("\n3. MOCKING:")
    print("   • @mockable adds .mock() and .mock_builder() class methods")
    print("   • All database types are automatically mocked with appropriate data")
    print("   • Enums are automatically supported - random selection from values")

    print("\n4. VALIDATION:")
    print("   • Use Pydantic BaseModel for automatic validation")
    print("   • Each db_type has .validate() method")
    print("   • Types enforce their constraints (length, precision, etc.)")

    print("\n5. ENUM SUPPORT:")
    print("   • Python enums work automatically with @mockable")
    print("   • Mock generation randomly selects from enum values")
    print("   • Works with string, numeric, and auto() enum values")


if __name__ == "__main__":
    demo_basic_mocking()
    demo_specialized_types()
    demo_enum_mocking()
    show_dataclass_notes()
