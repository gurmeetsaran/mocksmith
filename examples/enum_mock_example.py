"""Example demonstrating enum support in mocksmith mock generation.

This example shows how enums are automatically handled when generating
mock data for dataclasses and Pydantic models.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from mocksmith import mockable


# Define some enums for our example
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
    """Subscription tiers with custom values."""

    FREE = 0
    BASIC = 1
    PREMIUM = 2
    ENTERPRISE = 3


@mockable
@dataclass
class User:
    """User model with enum fields."""

    username: str
    email: str
    role: UserRole
    status: AccountStatus
    subscription: SubscriptionTier
    preferred_theme: Optional[str] = None  # Not an enum, just for comparison


def main():
    """Demonstrate enum mocking."""
    print("=== Enum Mock Generation Example ===\n")

    # Generate a single user
    user = User.mock()
    print("Generated user:")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {user.role.value} (type: {type(user.role).__name__})")
    print(f"  Status: {user.status.name} (value: {user.status.value})")
    print(f"  Subscription: {user.subscription.name} (tier: {user.subscription.value})")
    print(f"  Theme: {user.preferred_theme}")

    # Generate multiple users to show randomness
    print("\n=== Random Distribution Demo ===")
    print("Generating 20 users to show enum value distribution:\n")

    users = [User.mock() for _ in range(20)]

    # Count role distribution
    role_counts = {}
    for user in users:
        role_counts[user.role] = role_counts.get(user.role, 0) + 1

    print("Role distribution:")
    for role, count in sorted(role_counts.items(), key=lambda x: x[0].value):
        print(f"  {role.value}: {count} users")

    # Count status distribution
    status_counts = {}
    for user in users:
        status_counts[user.status] = status_counts.get(user.status, 0) + 1

    print("\nStatus distribution:")
    for status, count in sorted(status_counts.items(), key=lambda x: x[0].value):
        print(f"  {status.name}: {count} users")

    # Using the builder pattern with enums
    print("\n=== Builder Pattern with Enums ===")
    admin = (
        User.mock_builder()
        .with_role(UserRole.ADMIN)
        .with_status(AccountStatus.ACTIVE)
        .with_subscription(SubscriptionTier.ENTERPRISE)
        .build()
    )

    print(f"Built admin user: {admin.username}")
    print(f"  Role: {admin.role.value}")
    print(f"  Status: {admin.status.name}")
    print(f"  Subscription: {admin.subscription.name}")


# Pydantic example
try:
    from pydantic import BaseModel

    @mockable
    class Product(BaseModel):
        """Product model using Pydantic."""

        name: str
        category: UserRole  # Reusing enum for demo
        status: AccountStatus
        tier: Optional[SubscriptionTier] = None

    def pydantic_example():
        """Show enum support with Pydantic."""
        print("\n\n=== Pydantic Enum Example ===")

        product = Product.mock()
        print(f"Generated product: {product.name}")
        print(f"  Category: {product.category.value}")
        print(f"  Status: {product.status.name}")
        print(f"  Tier: {product.tier.name if product.tier else 'None'}")

        # Validation still works
        try:
            # This would fail - can't assign string to enum field
            Product(
                name="Test",
                category="admin",  # Should be UserRole.ADMIN
                status=AccountStatus.ACTIVE,
            )
            print("\nERROR: Should have failed validation!")
        except Exception as e:
            print(f"\nValidation correctly failed: {type(e).__name__}")

    # Run Pydantic example if available
    pydantic_example()

except ImportError:
    print("\n(Pydantic not installed, skipping Pydantic example)")


if __name__ == "__main__":
    main()
