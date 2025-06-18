"""Example showing Pydantic usage with db_types including specialized types."""

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ValidationError

from db_types import (
    # Basic types with clean syntax for Pydantic
    Varchar, Integer, DecimalType, Boolean, Date,
    # Raw types
    VARCHAR, INTEGER, DECIMAL, DATE,
    # Specialized types
    Email as EMAIL_TYPE,
    CountryCode as COUNTRYCODE_TYPE,
    City as CITY_TYPE,
    ZipCode as ZIPCODE_TYPE,
    PhoneNumber as PHONENUMBER_TYPE,
    # For mocking
    mockable,
)
from db_types.pydantic_integration import DBTypeValidator


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
    email: Annotated[str, DBTypeValidator(EMAIL_TYPE())]
    phone: Annotated[str, DBTypeValidator(PHONENUMBER_TYPE())]
    country: Annotated[str, DBTypeValidator(COUNTRYCODE_TYPE())]
    city: Annotated[str, DBTypeValidator(CITY_TYPE())]
    postal_code: Annotated[str, DBTypeValidator(ZIPCODE_TYPE())]
    
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
        joined=date(2020, 1, 1)
    )
    
    print(f"Created User:")
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
            joined=date.today()
        )
    except ValidationError as e:
        print(f"  ✅ Validation correctly failed for long name")
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
        registered=date.today()
    )
    
    print(f"Created Customer:")
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
            registered=date.today()
        )
    except ValidationError as e:
        print(f"  ✅ Email validation correctly failed")
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
            registered=date.today()
        )
    except ValidationError as e:
        print(f"  ✅ Country validation correctly failed")
        print(f"     Error: {e.errors()[0]['msg']}")


def demo_mock_generation():
    """Demonstrate mock generation for Pydantic models."""
    print("\n\n=== Pydantic Mocking with @mockable ===\n")
    
    print("With @mockable decorator, Pydantic models work just like dataclasses!\n")
    
    # Generate a mock user
    print("Basic model mocking:")
    user = User.mock()
    print(f"  Generated User:")
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
    builder_user = (User.mock_builder()
                    .with_name("Bob Wilson")
                    .with_age(35)
                    .with_is_active(True)
                    .build())
    print(f"    Name: {builder_user.name}")
    print(f"    Age: {builder_user.age}")
    print(f"    Active: {builder_user.is_active}")
    
    # Mock individual fields
    print("\n\nMocking individual fields:")
    print(f"  Name: {VARCHAR(50).mock()}")
    print(f"  Email: {EMAIL_TYPE().mock()}")
    print(f"  Country: {COUNTRYCODE_TYPE().mock()}")
    print(f"  City: {CITY_TYPE().mock()}")
    print(f"  Phone: {PHONENUMBER_TYPE().mock()}")
    
    # Mock Customer with specialized types
    print("\n\nMocking Customer with specialized types:")
    try:
        # Basic mock generation
        mock_customer = Customer.mock()
        print(f"  ✅ Successfully mocked Customer:")
        print(f"     Name: {mock_customer.name}")
        print(f"     Email: {mock_customer.email}")
        print(f"     Country: {mock_customer.country}")
        print(f"     City: {mock_customer.city}")
        print(f"     Phone: {mock_customer.phone}")
        
        # Mock with overrides
        print("\n  With overrides:")
        custom_customer = Customer.mock(
            name="Global Corp Inc.",
            country="US",
            city="New York"
        )
        print(f"     Name: {custom_customer.name}")
        print(f"     Country: {custom_customer.country}")
        print(f"     City: {custom_customer.city}")
        
        # Using builder pattern
        print("\n  Using builder pattern:")
        builder_customer = (Customer.mock_builder()
                          .with_name("Tech Solutions Ltd.")
                          .with_country("GB")
                          .with_city("London")
                          .with_email("contact@techsolutions.co.uk")
                          .build())
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
    
    print("\n2. SPECIALIZED TYPES NEED EXPLICIT SYNTAX:")
    print("   • email: Annotated[str, DBTypeValidator(EMAIL())]")
    print("   • This is because specialized types aren't in annotations.py yet")
    
    print("\n3. MOCKING NOW WORKS WITH @mockable!")
    print("   • Pydantic models support @mockable decorator just like dataclasses")
    print("   • Automatic mock generation with .mock() class method")
    print("   • Type-safe builder pattern with .mock_builder()")
    print("   • Individual type .mock() methods still available")
    
    print("\n4. AUTOMATIC VALIDATION:")
    print("   • Validation happens automatically on model creation")
    print("   • All db_type constraints are enforced")
    print("   • Get detailed error messages with ValidationError")


# Import the raw types for comparison
from db_types import INTEGER, DECIMAL, DATE


if __name__ == "__main__":
    demo_basic_usage()
    demo_specialized_types()
    demo_mock_generation()
    show_pydantic_notes()