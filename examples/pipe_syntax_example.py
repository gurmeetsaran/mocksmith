"""Example demonstrating pipe syntax (|) for optional fields with mockable annotations."""

from typing import Annotated

from pydantic import BaseModel

from mocksmith import BigInt, DateTime, Integer, Timestamp, Varchar, mockable


@mockable
class User(BaseModel):
    """User model with pipe syntax for optional fields."""

    # Required fields
    username: Annotated[str, Varchar(50)]
    email: Annotated[str, Varchar(100)]

    # Optional fields using pipe syntax (Python 3.10+)
    user_id: BigInt() | None  # Simple type without Annotated
    full_name: Annotated[str, Varchar(100)] | None  # With Annotated
    age: Annotated[int, Integer(ge=0, le=120)] | None  # With constraints
    created_at: DateTime() | None  # DateTime type
    last_login: Timestamp() | None  # Timestamp with timezone


def main():
    print("Generating mock users with pipe syntax...\n")
    print("=" * 70)

    # Generate 5 mock users
    for i in range(1, 6):
        user = User.mock()

        print(f"\nUser #{i}:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  User ID: {user.user_id}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Age: {user.age}")
        print(f"  Created At: {user.created_at}")
        print(f"  Last Login: {user.last_login}")

        # Verify types
        assert isinstance(user.username, str)
        assert isinstance(user.email, str)
        assert user.user_id is None or isinstance(user.user_id, int)
        assert user.full_name is None or isinstance(user.full_name, str)
        assert user.age is None or (isinstance(user.age, int) and 0 <= user.age <= 120)

    print("\n" + "=" * 70)
    print("\n✅ All mocks generated successfully!")
    print("   Note: Optional fields (|None) randomly generate None or valid values")


if __name__ == "__main__":
    main()
