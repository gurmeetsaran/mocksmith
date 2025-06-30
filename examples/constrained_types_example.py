#!/usr/bin/env python3
"""Example of using constrained types with mocksmith."""

from decimal import Decimal

from pydantic import BaseModel, ValidationError

from mocksmith import (
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedMoney,
    NonNegativeMoney,
    PositiveMoney,
    mockable,
)


def main():
    """Demonstrate constrained types functionality."""

    print("=== Constrained Types Example ===\n")

    # 1. Basic constrained types
    print("1. Basic Constrained Types:")

    class Product(BaseModel):
        name: str
        price: PositiveMoney()  # Must be > 0
        cost: PositiveMoney()  # Must be > 0
        discount: ConstrainedMoney(ge=0, le=50)  # 0-50 range
        tax_rate: ConstrainedFloat(ge=0.0, le=0.25)  # 0-25%

    # Valid product
    product = Product(name="Widget", price="19.99", cost="10.00", discount="5.00", tax_rate=0.08)
    print(f"✓ Valid product: {product.name}")
    print(f"  Price: ${product.price} (type: {type(product.price).__name__})")
    print(f"  Discount: ${product.discount}")
    print(f"  Tax rate: {product.tax_rate * 100:.1f}%")

    # Try invalid values
    try:
        Product(name="Bad", price="0.00", cost="10.00", discount="5.00", tax_rate=0.08)
    except ValidationError as e:
        print("\n✗ Validation error for zero price:")
        print(f"  {e.errors()[0]['msg']}")

    # 2. Mock generation with constraints
    print("\n\n2. Mock Generation with Constraints:")

    @mockable
    class Order(BaseModel):
        order_id: int
        subtotal: PositiveMoney()
        discount: ConstrainedMoney(ge=0, le=100)
        tax: NonNegativeMoney()
        shipping: ConstrainedMoney(ge=0, le=50)

        @property
        def total(self) -> Decimal:
            return self.subtotal - self.discount + self.tax + self.shipping

    print("Generating 5 random orders:")
    for _ in range(5):
        order = Order.mock()
        print(f"\nOrder {order.order_id}:")
        print(f"  Subtotal: ${order.subtotal:.2f}")
        print(f"  Discount: ${order.discount:.2f}")
        print(f"  Tax: ${order.tax:.2f}")
        print(f"  Shipping: ${order.shipping:.2f}")
        print(f"  Total: ${order.total:.2f}")

    # 3. Complex constraints
    print("\n\n3. Complex Constraints:")

    @mockable
    class ScientificData(BaseModel):
        # Precise decimal constraints
        measurement: ConstrainedDecimal(10, 4, ge=-1000, le=1000)
        # Percentage as decimal (0-100%)
        concentration: ConstrainedDecimal(5, 2, ge=0, le=100)
        # Temperature in Celsius
        temperature: ConstrainedFloat(ge=-273.15, le=1000)
        # Probability (0-1)
        probability: ConstrainedFloat(ge=0.0, le=1.0)

    data = ScientificData.mock()
    print(f"Scientific measurement: {data.measurement}")
    print(f"Concentration: {data.concentration}%")
    print(f"Temperature: {data.temperature:.2f}°C")
    print(f"Probability: {data.probability:.4f}")

    # 4. Builder pattern with constraints
    print("\n\n4. Builder Pattern with Constraints:")

    custom_order = (
        Order.mock_builder()
        .with_subtotal("100.00")
        .with_discount("25.00")
        .with_tax("8.00")
        .with_shipping("10.00")
        .build()
    )

    print(f"Custom order total: ${custom_order.total:.2f}")
    print(
        f"  (Subtotal: ${custom_order.subtotal} - Discount: ${custom_order.discount} "
        f"+ Tax: ${custom_order.tax} + Shipping: ${custom_order.shipping})"
    )

    # 5. Validation examples
    print("\n\n5. Validation Examples:")

    class Account(BaseModel):
        balance: NonNegativeMoney()  # >= 0
        credit_limit: PositiveMoney()  # > 0
        interest_rate: ConstrainedFloat(ge=0.0, le=0.30)  # 0-30%

    # Valid account
    account = Account(balance="1000.00", credit_limit="5000.00", interest_rate=0.15)
    print(
        f"✓ Valid account - Balance: ${account.balance}, "
        f"Credit: ${account.credit_limit}, Rate: {account.interest_rate * 100}%"
    )

    # Invalid - negative balance
    try:
        Account(balance="-100.00", credit_limit="5000.00", interest_rate=0.15)
    except ValidationError:
        print("✗ Correctly rejected negative balance")

    # Invalid - interest rate too high
    try:
        Account(balance="1000.00", credit_limit="5000.00", interest_rate=0.50)
    except ValidationError:
        print("✗ Correctly rejected 50% interest rate (max 30%)")

    print("\n=== End of Example ===")


if __name__ == "__main__":
    main()
