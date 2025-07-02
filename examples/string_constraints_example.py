#!/usr/bin/env python3
"""
Example demonstrating the new string constraint features in mocksmith.

This shows how to use the enhanced VARCHAR, CHAR, and TEXT types with
Pydantic constraint parameters like min_length, pattern, transformations, etc.
"""

from pydantic import BaseModel, ValidationError

from mocksmith import Char, Text, Varchar, mockable

print("=== String Types with Constraints Example ===\n")

# Example 1: User Registration with Validation
print("1. User Registration Model with String Constraints:")


@mockable
class UserRegistration(BaseModel):
    """User registration with various string constraints."""

    # Username: 3-20 chars with transformations
    username: Varchar(20, min_length=3, to_lower=True, strip_whitespace=True)

    # Email: auto-lowercase and trim whitespace, must be company email
    email: Varchar(255, to_lower=True, strip_whitespace=True, endswith="@company.com")

    # Display name: 2-50 chars, no extra constraints
    display_name: Varchar(50, min_length=2)

    # Country code: exactly 2 chars, uppercase
    country_code: Char(2, to_upper=True)

    # Bio: optional text with min/max length
    bio: Text(min_length=10, max_length=500, strip_whitespace=True)

    # Referral code: must start with 'REF-' prefix
    referral_code: Varchar(12, startswith="REF-", to_upper=True)


# Test validation
print("\nValidation examples:")

# Invalid username (too short)
try:
    user = UserRegistration(
        username="ab",  # Too short
        email="test@company.com",
        display_name="Test User",
        country_code="us",
        bio="Short bio",
        referral_code="ref-123456",
    )
except ValidationError as e:
    print(f"✗ Username validation: {e.errors()[0]['msg']}")

# Invalid email domain
try:
    user = UserRegistration(
        username="user_name",
        email="test@example.com",  # Must end with @company.com
        display_name="Test User",
        country_code="us",
        bio="This is my bio",
        referral_code="ref-abc1234",
    )
except ValidationError as e:
    print(f"✗ Email validation: {e.errors()[0]['msg']}")

# Invalid referral code (missing prefix)
try:
    user = UserRegistration(
        username="user_name",
        email="test@company.com",
        display_name="Test User",
        country_code="us",
        bio="This is my bio",
        referral_code="abc1234",  # Missing 'REF-' prefix
    )
except ValidationError as e:
    print(f"✗ Referral validation: {e.errors()[0]['msg']}")

# Valid registration with transformations
user = UserRegistration(
    username="  JOHN_DOE_123  ",  # Will be lowercased and trimmed
    email="  John.Doe@COMPANY.COM  ",  # Will be lowercased and trimmed
    display_name="John Doe",
    country_code="us",  # Will be uppercased
    bio="   I am a software developer interested in databases.   ",  # Will be trimmed
    referral_code="ref-abc1234",  # Will be uppercased to REF-ABC1234
)

print("\n✓ Valid user created:")
print(f"  Username: {user.username}")
print(f"  Email: '{user.email}' (transformed)")
print(f"  Country: '{user.country_code}' (uppercased)")
print(f"  Bio: '{user.bio}' (trimmed)")
print(f"  Referral: {user.referral_code} (uppercased)")

# Example 2: Product Catalog
print("\n\n2. Product Catalog with String Constraints:")


@mockable
class Product(BaseModel):
    """Product with various string validations."""

    # SKU must start with 'PRD-'
    sku: Char(8, startswith="PRD-")

    # Product name
    name: Varchar(100, min_length=3, strip_whitespace=True)

    # Short description
    summary: Varchar(200, min_length=10)

    # Full description must be a review format
    description: Text(min_length=50, max_length=5000, startswith="Product Review: ")

    # Category (normalized to lowercase)
    category: Varchar(50, to_lower=True, strip_whitespace=True)

    # Brand (normalized to uppercase)
    brand: Varchar(50, to_upper=True, strip_whitespace=True)


product = Product(
    sku="PRD-1234",
    name="  Premium Wireless Headphones  ",
    summary="High-quality wireless headphones with noise cancellation",
    description="Product Review: These premium wireless headphones offer exceptional "
    "sound quality with active noise cancellation. "
    + "Features include 30-hour battery life, comfortable over-ear design, "
    "and Bluetooth 5.0 connectivity.",
    category="  Audio Equipment  ",
    brand="  audiophile  ",
)

print(f"Product: {product.name.strip()}")
print(f"  SKU: {product.sku}")
print(f"  Category: '{product.category}' (lowercased)")
print(f"  Brand: '{product.brand}' (uppercased)")

# Example 3: Mock Generation
print("\n\n3. Mock Data Generation with Constraints:")

# Generate mock users
print("\nGenerating 3 mock users:")
for i in range(3):
    mock_user = UserRegistration.mock()
    print(f"\nUser {i+1}:")
    print(f"  Username: {mock_user.username}")
    print(f"  Email: {mock_user.email}")
    print(f"  Country: {mock_user.country_code}")
    print(f"  Referral: {mock_user.referral_code}")

    # Verify constraints are respected
    assert len(mock_user.username) >= 3
    assert len(mock_user.username) <= 20
    assert mock_user.email == mock_user.email.lower()
    assert len(mock_user.country_code) == 2
    assert mock_user.country_code == mock_user.country_code.upper()

# Example 4: Using startswith/endswith for easier mock generation
print("\n\n4. Using startswith/endswith Constraints:")


@mockable
class OrderSystem(BaseModel):
    """Example using startswith/endswith for structured data."""

    # Order IDs must start with ORD-
    order_id: Varchar(20, startswith="ORD-")

    # Invoice numbers start with INV- and end with current year
    invoice_number: Varchar(20, startswith="INV-", endswith="-2024")

    # Support ticket with prefix
    ticket_id: Char(10, startswith="TKT-", to_upper=True)

    # Customer notes with standard prefix
    customer_note: Text(max_length=1000, startswith="Customer feedback: ")


# Create sample order
order = OrderSystem(
    order_id="ORD-12345",
    invoice_number="INV-001-2024",
    ticket_id="tkt-abc123",  # Will be uppercased
    customer_note="Customer feedback: Great service and fast delivery!",
)

print(f"Order ID: {order.order_id}")
print(f"Invoice: {order.invoice_number}")
print(f"Ticket: {order.ticket_id}")
print(f"Note: {order.customer_note[:50]}...")

# Generate mock orders
print("\nGenerating 3 mock orders:")
for i in range(3):
    mock_order = OrderSystem.mock()
    print(f"\nMock Order {i+1}:")
    print(f"  Order ID: {mock_order.order_id}")
    print(f"  Invoice: {mock_order.invoice_number}")
    print(f"  Ticket: {mock_order.ticket_id}")

    # Verify constraints
    assert mock_order.order_id.startswith("ORD-")
    assert mock_order.invoice_number.startswith("INV-") and mock_order.invoice_number.endswith(
        "-2024"
    )
    assert mock_order.ticket_id.startswith("TKT-")
    assert mock_order.customer_note.startswith("Customer feedback: ")

# Example 5: Using Pydantic-specific kwargs
print("\n\n5. Advanced: Using Pydantic-specific Parameters:")


class StrictValidation(BaseModel):
    """Example using additional Pydantic parameters."""

    # Strict mode - won't coerce types
    numeric_code: Varchar(10, startswith="ID", strict=True)

    # Using Pydantic's built-in string constraints via kwargs
    # (These are passed through to constr)
    custom_field: Varchar(50, min_length=5)


# This would fail in strict mode (trying to pass int instead of str)
try:
    StrictValidation(numeric_code=12345, custom_field="test")
except ValidationError as e:
    print(f"✗ Strict mode error: {e.errors()[0]['msg']}")

# Valid with string
valid = StrictValidation(numeric_code="ID12345", custom_field="valid_value")
print(f"✓ Strict validation passed: {valid.numeric_code}")

print("\n\n=== Key Features Demonstrated ===")
print("1. min_length/max_length - Control string length")
print("2. startswith/endswith - Simple prefix/suffix constraints")
print("3. to_lower/to_upper - Automatic case conversion")
print("4. strip_whitespace - Remove leading/trailing spaces")
print("5. Works with both Pydantic validation and mock generation")
print("6. Supports additional Pydantic parameters via **kwargs")
print("7. Transformations happen during deserialization (input processing)")
print("8. Mock generation intelligently handles startswith/endswith")
