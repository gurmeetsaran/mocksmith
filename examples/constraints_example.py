"""Example demonstrating constrained numeric types with dataclasses.

This example shows how to use the clean API for constrained numeric types
with Python dataclasses.
"""

from dataclasses import dataclass

from db_types import Integer, NonNegativeInteger, NonPositiveInteger, PositiveInteger
from db_types.dataclass_integration import validate_dataclass


# Example 1: E-commerce Product
@validate_dataclass
@dataclass
class Product:
    id: PositiveInteger()
    price_cents: NonNegativeInteger()  # Price in cents
    quantity_in_stock: NonNegativeInteger()
    discount_percentage: Integer(min_value=0, max_value=100)


# Example 2: Temperature Sensor
@validate_dataclass
@dataclass
class TemperatureReading:
    sensor_id: PositiveInteger()
    temperature_celsius: Integer(min_value=-273, max_value=1000)  # Absolute zero to very hot
    battery_percentage: Integer(min_value=0, max_value=100)


# Example 3: Financial Transaction
@validate_dataclass
@dataclass
class Transaction:
    id: PositiveInteger()
    amount_cents: Integer(min_value=-1000000, max_value=1000000)  # +/- $10,000
    fee_cents: NonNegativeInteger()


# Example 4: Game Score
@validate_dataclass
@dataclass
class GameScore:
    player_id: PositiveInteger()
    score: NonNegativeInteger()
    bonus_multiplier: Integer(min_value=1, max_value=10, multiple_of=1)
    penalty_points: NonPositiveInteger()  # 0 or negative


# Example 5: Age Groups
@validate_dataclass
@dataclass
class Person:
    id: PositiveInteger()
    age_years: Integer(min_value=0, max_value=150)
    years_of_experience: NonNegativeInteger()


# Example 6: Pagination
@validate_dataclass
@dataclass
class PaginationParams:
    page: PositiveInteger()
    page_size: Integer(min_value=1, max_value=100, multiple_of=10)


def main():
    """Demonstrate usage of constrained types."""

    # Valid product
    print("Creating valid product...")
    product = Product(
        id=123, price_cents=2999, quantity_in_stock=50, discount_percentage=15  # $29.99
    )
    print(f"Product: {product}")

    # Temperature reading
    print("\nCreating temperature reading...")
    temp = TemperatureReading(sensor_id=1, temperature_celsius=25, battery_percentage=85)
    print(f"Temperature: {temp}")

    # Game score with penalties
    print("\nCreating game score...")
    score = GameScore(player_id=456, score=1500, bonus_multiplier=3, penalty_points=-50)
    print(f"Game Score: {score}")

    # Pagination
    print("\nCreating pagination params...")
    pagination = PaginationParams(page=2, page_size=20)  # Must be multiple of 10
    print(f"Pagination: {pagination}")

    # Demonstrate validation errors
    print("\n--- Validation Errors ---")

    try:
        Product(id=0, price_cents=100, quantity_in_stock=0, discount_percentage=0)
    except ValueError as e:
        print(f"Product validation error: {e}")

    try:
        TemperatureReading(sensor_id=1, temperature_celsius=-300, battery_percentage=50)
    except ValueError as e:
        print(f"Temperature validation error: {e}")

    try:
        GameScore(player_id=1, score=100, bonus_multiplier=15, penalty_points=0)
    except ValueError as e:
        print(f"Game score validation error: {e}")

    try:
        PaginationParams(page=1, page_size=25)  # Not multiple of 10
    except ValueError as e:
        print(f"Pagination validation error: {e}")


if __name__ == "__main__":
    main()
