"""Example demonstrating the clean API for constrained numeric types."""

from dataclasses import dataclass

from pydantic import BaseModel

from db_types import (
    BigInt,
    Integer,
    NonNegativeInteger,
    NonPositiveInteger,
    PositiveInteger,
    SmallInt,
    TinyInt,
)
from db_types.dataclass_integration import validate_dataclass


# Example 1: Using the enhanced Integer() function with constraints
@validate_dataclass
@dataclass
class ProductInventory:
    # Standard integer types
    product_id: Integer()  # Regular 32-bit integer
    warehouse_id: BigInt()  # Regular 64-bit integer

    # Using constraints with the same function
    quantity: Integer(min_value=0)  # Non-negative
    reorder_level: Integer(min_value=1, max_value=1000)

    # Percentage must be 0-100 and multiple of 5
    discount_percentage: Integer(min_value=0, max_value=100, multiple_of=5)

    # Using positive shortcut
    min_order_quantity: Integer(positive=True)


# Example 2: Pydantic model with clean constraint API
class UserProfile(BaseModel):
    # Clean constraint types
    user_id: PositiveInteger()
    age: Integer(min_value=13, max_value=120)

    # Financial fields
    credit_score: Integer(min_value=300, max_value=850)
    debt_amount: NonPositiveInteger()  # 0 or negative
    savings: NonNegativeInteger()

    # Preferences
    notification_hour: SmallInt(min_value=0, max_value=23)
    timezone_offset: SmallInt(min_value=-12, max_value=14)


# Example 3: E-commerce with various constraints
@validate_dataclass
@dataclass
class OrderItem:
    # IDs are always positive
    order_id: BigInt(positive=True)
    product_id: Integer(positive=True)

    # Quantities and amounts
    quantity: Integer(min_value=1)
    unit_price_cents: Integer(positive=True)
    discount_amount_cents: NonNegativeInteger()

    # Tax must be in 0.25% increments (stored as basis points)
    tax_rate_basis_points: Integer(min_value=0, max_value=10000, multiple_of=25)


# Example 4: Game mechanics
class GameCharacter(BaseModel):
    # Basic info
    character_id: PositiveInteger()
    level: Integer(min_value=1, max_value=100)

    # Stats can go negative with debuffs
    health: Integer(min_value=-100, max_value=9999)
    mana: NonNegativeInteger()

    # Experience and currency
    experience_points: NonNegativeInteger()
    gold: NonNegativeInteger()
    debt: NonPositiveInteger()  # Can owe money

    # Modifiers
    strength_modifier: Integer(min_value=-10, max_value=10)
    defense_modifier: Integer(min_value=-10, max_value=10)


# Example 5: API Rate Limiting
@validate_dataclass
@dataclass
class RateLimitRule:
    rule_id: Integer(positive=True)

    # Requests per time window
    requests_per_minute: Integer(min_value=1, max_value=10000, multiple_of=10)
    requests_per_hour: Integer(min_value=1, max_value=100000, multiple_of=100)

    # Burst settings
    burst_size: SmallInt(min_value=1, max_value=1000)

    # Penalties
    cooldown_seconds: Integer(min_value=0, max_value=3600, multiple_of=30)
    penalty_multiplier: SmallInt(min_value=1, max_value=10)


# Example 6: Configuration with TINYINT
@validate_dataclass
@dataclass
class SystemConfig:
    config_id: Integer(positive=True)

    # Small bounded values perfect for TINYINT
    log_level: TinyInt(min_value=0, max_value=5)  # 0=DEBUG, 5=CRITICAL
    max_retries: TinyInt(min_value=0, max_value=10)
    thread_pool_size: TinyInt(min_value=1, max_value=100)

    # Percentage values
    cpu_threshold_percent: TinyInt(min_value=0, max_value=100)
    memory_threshold_percent: TinyInt(min_value=0, max_value=100)

    # Priority levels
    priority: TinyInt(min_value=-5, max_value=5)  # -5=lowest, 5=highest


def main():
    """Demonstrate the clean API for constrained types."""

    # Example 1: Product inventory
    print("=== Product Inventory ===")
    inventory = ProductInventory(
        product_id=12345,
        warehouse_id=9876543210,
        quantity=50,
        reorder_level=10,
        discount_percentage=15,  # Valid: multiple of 5
        min_order_quantity=5,
    )
    print(f"Inventory: {inventory}")

    # Example 2: User profile
    print("\n=== User Profile ===")
    user = UserProfile(
        user_id=1001,
        age=25,
        credit_score=720,
        debt_amount=0,  # No debt
        savings=50000,
        notification_hour=9,  # 9 AM
        timezone_offset=-5,  # EST
    )
    print(f"User: {user}")

    # Example 3: Order item
    print("\n=== Order Item ===")
    item = OrderItem(
        order_id=789456123,
        product_id=456,
        quantity=3,
        unit_price_cents=2999,  # $29.99
        discount_amount_cents=500,  # $5.00
        tax_rate_basis_points=875,  # 8.75%
    )
    print(f"Order Item: {item}")

    # Example 4: Game character
    print("\n=== Game Character ===")
    character = GameCharacter(
        character_id=42,
        level=15,
        health=100,
        mana=50,
        experience_points=15420,
        gold=1250,
        debt=-100,  # Owes 100 gold
        strength_modifier=3,
        defense_modifier=-1,
    )
    print(f"Character: {character}")

    # Example 6: System configuration
    print("\n=== System Configuration ===")
    config = SystemConfig(
        config_id=1,
        log_level=2,  # INFO level
        max_retries=3,
        thread_pool_size=8,
        cpu_threshold_percent=80,
        memory_threshold_percent=90,
        priority=0,  # Normal priority
    )
    print(f"Config: {config}")

    # Demonstrate validation errors
    print("\n=== Validation Errors ===")

    # Try invalid discount percentage (not multiple of 5)
    try:
        ProductInventory(
            product_id=1,
            warehouse_id=1,
            quantity=10,
            reorder_level=5,
            discount_percentage=17,  # Invalid: not multiple of 5
            min_order_quantity=1,
        )
    except ValueError as e:
        print(f"Discount error: {e}")

    # Try invalid age
    try:
        UserProfile(
            user_id=1,
            age=10,  # Too young (min is 13)
            credit_score=700,
            debt_amount=0,
            savings=0,
            notification_hour=12,
            timezone_offset=0,
        )
    except Exception as e:
        print(f"Age error: {str(e).split(';')[0]}")  # First validation error

    # Try negative quantity
    try:
        OrderItem(
            order_id=1,
            product_id=1,
            quantity=0,  # Invalid: min is 1
            unit_price_cents=100,
            discount_amount_cents=0,
            tax_rate_basis_points=0,
        )
    except ValueError as e:
        print(f"Quantity error: {e}")

    # Try invalid log level
    try:
        SystemConfig(
            config_id=1,
            log_level=10,  # Invalid: max is 5
            max_retries=3,
            thread_pool_size=8,
            cpu_threshold_percent=80,
            memory_threshold_percent=90,
            priority=0,
        )
    except ValueError as e:
        print(f"Log level error: {e}")


if __name__ == "__main__":
    main()
