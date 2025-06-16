"""Example demonstrating constrained numeric types with Pydantic.

This example shows how to use the clean API for constrained numeric types
with Pydantic models.
"""

from typing import Optional

from pydantic import BaseModel, ValidationError

from db_types import Integer, NonNegativeInteger, NonPositiveInteger, PositiveInteger


# Example 1: User Account
class UserAccount(BaseModel):
    user_id: PositiveInteger()
    age: Integer(min_value=13, max_value=120)
    credit_balance: NonNegativeInteger()  # In cents
    loyalty_points: NonNegativeInteger()


# Example 2: Stock Trading
class StockOrder(BaseModel):
    order_id: PositiveInteger()
    quantity: PositiveInteger()
    price_cents: PositiveInteger()
    stop_loss_offset: Optional[NonPositiveInteger()]  # Negative or 0


# Example 3: Survey Response
class SurveyResponse(BaseModel):
    response_id: PositiveInteger()
    satisfaction_score: Integer(min_value=1, max_value=5)
    nps_score: Integer(min_value=0, max_value=10)


# Example 4: API Rate Limiting
class RateLimitConfig(BaseModel):
    requests_per_minute: Integer(min_value=1, max_value=1000, multiple_of=10)
    burst_size: Integer(min_value=1, max_value=100)
    cooldown_seconds: Integer(min_value=0, max_value=300, multiple_of=5)


def main():
    """Demonstrate Pydantic models with constrained types."""

    # Valid user account
    print("Creating valid user account...")
    user = UserAccount(user_id=12345, age=25, credit_balance=5000, loyalty_points=1500)  # $50.00
    print(f"User: {user}")
    print(f"JSON: {user.model_dump_json()}")

    # Stock order with optional stop loss
    print("\nCreating stock order...")
    order = StockOrder(
        order_id=789,
        quantity=100,
        price_cents=15050,  # $150.50
        stop_loss_offset=-500,  # $5.00 below
    )
    print(f"Order: {order}")

    # Survey response
    print("\nCreating survey response...")
    survey = SurveyResponse(response_id=456, satisfaction_score=4, nps_score=8)
    print(f"Survey: {survey}")

    # Rate limit config
    print("\nCreating rate limit config...")
    rate_limit = RateLimitConfig(requests_per_minute=100, burst_size=20, cooldown_seconds=30)
    print(f"Rate Limit: {rate_limit}")

    # Demonstrate validation errors
    print("\n--- Validation Errors ---")

    # Age too young
    try:
        UserAccount(user_id=1, age=10, credit_balance=0, loyalty_points=0)
    except ValidationError as e:
        print(f"User validation error: {e.errors()[0]['msg']}")

    # Negative credit balance
    try:
        UserAccount(user_id=1, age=20, credit_balance=-100, loyalty_points=0)
    except ValidationError as e:
        print(f"Credit validation error: {e.errors()[0]['msg']}")

    # Invalid satisfaction score
    try:
        SurveyResponse(response_id=1, satisfaction_score=6, nps_score=5)
    except ValidationError as e:
        print(f"Survey validation error: {e.errors()[0]['msg']}")

    # Invalid rate limit (not multiple of 10)
    try:
        RateLimitConfig(requests_per_minute=55, burst_size=10, cooldown_seconds=30)
    except ValidationError as e:
        print(f"Rate limit validation error: {e.errors()[0]['msg']}")

    # Invalid cooldown (not multiple of 5)
    try:
        RateLimitConfig(requests_per_minute=100, burst_size=10, cooldown_seconds=33)
    except ValidationError as e:
        print(f"Cooldown validation error: {e.errors()[0]['msg']}")


if __name__ == "__main__":
    main()
