#!/usr/bin/env python3
"""
Example demonstrating the enhanced numeric constraint features in mocksmith.

This shows how to use the full Pydantic constraint parameters with numeric types
like INTEGER, FLOAT, DECIMAL, etc.
"""

from decimal import Decimal

from pydantic import BaseModel, ValidationError

from mocksmith import (
    BigInt,
    DecimalType,
    Float,
    Integer,
    SmallInt,
    TinyInt,
    mockable,
)

print("=== Numeric Types with Constraints Example ===\n")

# Example 1: Product Inventory System
print("1. Product Inventory Model with Numeric Constraints:")


@mockable
class Product(BaseModel):
    """Product with various numeric constraints."""

    # Product ID must be positive
    id: Integer(gt=0)

    # Quantity in stock (non-negative)
    quantity: Integer(ge=0)

    # Reorder level (1-1000)
    reorder_level: SmallInt(ge=1, le=1000)

    # Discount percentage (0-100)
    discount_percent: TinyInt(ge=0, le=100)

    # Price with decimal constraints
    price: DecimalType(10, 2, gt=0)  # Positive price up to 99999999.99

    # Weight in kg (positive float)
    weight_kg: Float(gt=0.0, le=1000.0)

    # Temperature range for storage
    min_temp_celsius: Float(ge=-30.0, le=50.0)
    max_temp_celsius: Float(ge=-30.0, le=50.0)


# Test validation
print("\nValidation examples:")

# Invalid: negative product ID
try:
    product = Product(
        id=-1,
        quantity=100,
        reorder_level=10,
        discount_percent=15,
        price=Decimal("29.99"),
        weight_kg=2.5,
        min_temp_celsius=2.0,
        max_temp_celsius=8.0,
    )
except ValidationError as e:
    print(f"✗ Product ID validation: {e.errors()[0]['msg']}")

# Invalid: discount > 100%
try:
    product = Product(
        id=1001,
        quantity=100,
        reorder_level=10,
        discount_percent=150,  # Invalid: > 100
        price=Decimal("29.99"),
        weight_kg=2.5,
        min_temp_celsius=2.0,
        max_temp_celsius=8.0,
    )
except ValidationError as e:
    print(f"✗ Discount validation: {e.errors()[0]['msg']}")

# Invalid: negative price
try:
    product = Product(
        id=1001,
        quantity=100,
        reorder_level=10,
        discount_percent=15,
        price=Decimal("-10.00"),  # Invalid: negative
        weight_kg=2.5,
        min_temp_celsius=2.0,
        max_temp_celsius=8.0,
    )
except ValidationError as e:
    print(f"✗ Price validation: {e.errors()[0]['msg']}")

# Valid product
product = Product(
    id=1001,
    quantity=50,
    reorder_level=10,
    discount_percent=15,
    price=Decimal("29.99"),
    weight_kg=2.5,
    min_temp_celsius=2.0,
    max_temp_celsius=8.0,
)

print("\n✓ Valid product created:")
print(f"  Product #{product.id}")
print(f"  Price: ${product.price}")
print(f"  Discount: {product.discount_percent}%")
print(f"  Weight: {product.weight_kg}kg")
print(f"  Storage: {product.min_temp_celsius}°C to {product.max_temp_celsius}°C")

# Example 2: Financial Transactions
print("\n\n2. Financial Transaction Model:")


@mockable
class Transaction(BaseModel):
    """Financial transaction with precise constraints."""

    # Transaction ID (positive big integer)
    transaction_id: BigInt(gt=0)

    # Amount in cents (can be negative for refunds)
    amount_cents: BigInt(ge=-1000000000, le=1000000000)  # ±$10,000,000

    # Exchange rate (positive, 6 decimal places)
    exchange_rate: DecimalType(10, 6, gt=0)

    # Transaction fee percentage (0-5%)
    fee_percentage: DecimalType(5, 4, ge=0, le=0.05)

    # Risk score (0.0 to 1.0)
    risk_score: Float(ge=0.0, le=1.0)

    # Processing time in milliseconds
    processing_time_ms: Integer(gt=0, le=60000)  # Max 60 seconds


# Create a valid transaction
transaction = Transaction(
    transaction_id=1234567890,
    amount_cents=15000,  # $150.00
    exchange_rate=Decimal("1.234567"),
    fee_percentage=Decimal("0.0295"),  # 2.95%
    risk_score=0.15,
    processing_time_ms=250,
)

print(f"Transaction #{transaction.transaction_id}")
print(f"  Amount: ${transaction.amount_cents / 100:.2f}")
print(f"  Exchange rate: {transaction.exchange_rate}")
print(f"  Fee: {transaction.fee_percentage * 100}%")
print(f"  Risk score: {transaction.risk_score}")
print(f"  Processing time: {transaction.processing_time_ms}ms")

# Example 3: Scientific Measurements
print("\n\n3. Scientific Measurement Model:")


@mockable
class Measurement(BaseModel):
    """Scientific measurements with constraints."""

    # Sample ID (positive, multiples of 1000)
    sample_id: Integer(gt=0, multiple_of=1000)

    # Temperature in Kelvin (absolute zero is 0)
    temperature_k: Float(ge=0.0, le=10000.0)

    # Pressure in pascals (positive)
    pressure_pa: Float(gt=0.0)

    # pH level (0-14)
    ph_level: Float(ge=0.0, le=14.0)

    # Concentration (positive, high precision)
    concentration_mol_l: DecimalType(12, 9, gt=0)

    # Measurement iterations (positive, multiples of 5)
    iterations: SmallInt(gt=0, multiple_of=5, le=1000)


# Test multiple_of constraint
print("\nMultiple-of constraint example:")
try:
    # Invalid: not a multiple of 1000
    measurement = Measurement(
        sample_id=1234,
        temperature_k=293.15,
        pressure_pa=101325.0,
        ph_level=7.0,
        concentration_mol_l=Decimal("0.001234567"),
        iterations=10,
    )
except ValidationError as e:
    print(f"✗ Sample ID validation: {e.errors()[0]['msg']}")

# Valid measurement
measurement = Measurement(
    sample_id=5000,  # Multiple of 1000
    temperature_k=293.15,  # ~20°C
    pressure_pa=101325.0,  # 1 atm
    ph_level=7.0,  # Neutral
    concentration_mol_l=Decimal("0.001234567"),
    iterations=25,  # Multiple of 5
)

print("\n✓ Valid measurement created:")
print(f"  Sample #{measurement.sample_id}")
print(f"  Temperature: {measurement.temperature_k}K ({measurement.temperature_k - 273.15:.1f}°C)")
print(f"  Pressure: {measurement.pressure_pa:.0f} Pa")
print(f"  pH: {measurement.ph_level}")
print(f"  Concentration: {measurement.concentration_mol_l} mol/L")
print(f"  Iterations: {measurement.iterations}")

# Example 4: Mock Generation
print("\n\n4. Mock Data Generation with Constraints:")

# Generate mock products
print("\nGenerating 3 mock products:")
for i in range(3):
    mock_product = Product.mock()
    print(f"\nProduct {i+1}:")
    print(f"  ID: {mock_product.id} (guaranteed > 0)")
    print(f"  Quantity: {mock_product.quantity} (guaranteed >= 0)")
    print(f"  Discount: {mock_product.discount_percent}% (guaranteed 0-100)")
    print(f"  Price: ${mock_product.price} (guaranteed > 0)")
    print(f"  Weight: {mock_product.weight_kg:.2f}kg (guaranteed 0-1000)")

    # Verify constraints are respected
    assert mock_product.id > 0
    assert mock_product.quantity >= 0
    assert 0 <= mock_product.discount_percent <= 100
    assert mock_product.price > 0
    assert 0 < mock_product.weight_kg <= 1000

# Generate mock measurements
print("\n\nGenerating 3 mock measurements:")
for i in range(3):
    mock_measurement = Measurement.mock()
    print(f"\nMeasurement {i+1}:")
    print(f"  Sample ID: {mock_measurement.sample_id} (multiple of 1000)")
    print(f"  Temperature: {mock_measurement.temperature_k:.1f}K")
    print(f"  pH: {mock_measurement.ph_level:.1f} (0-14)")
    print(f"  Iterations: {mock_measurement.iterations} (multiple of 5)")

    # Verify constraints
    assert mock_measurement.sample_id > 0 and mock_measurement.sample_id % 1000 == 0
    assert 0 <= mock_measurement.temperature_k <= 10000
    assert 0 <= mock_measurement.ph_level <= 14
    assert mock_measurement.iterations > 0 and mock_measurement.iterations % 5 == 0

# Example 5: Strict Mode
print("\n\n5. Strict Mode Example:")


class StrictNumbers(BaseModel):
    """Example using strict mode - no type coercion."""

    # Strict integer - won't accept floats
    count: Integer(strict=True, gt=0)

    # Strict float - won't accept integers
    ratio: Float(strict=True, ge=0.0, le=1.0)

    # Strict decimal - won't accept floats/ints
    amount: DecimalType(10, 2, strict=True, gt=0)


# Test strict mode
print("\nStrict mode validation:")
try:
    # Invalid: passing string to strict integer
    StrictNumbers(count="10", ratio=0.5, amount=Decimal("10.00"))
except ValidationError as e:
    print(f"✗ Strict integer error: {e.errors()[0]['msg']}")

try:
    # Invalid: passing string to strict float
    StrictNumbers(count=10, ratio="0.5", amount=Decimal("10.00"))
except ValidationError as e:
    print(f"✗ Strict float error: {e.errors()[0]['msg']}")

# Valid strict numbers
strict = StrictNumbers(count=10, ratio=0.5, amount=Decimal("10.00"))
print(
    f"\n✓ Valid strict numbers: count={strict.count}, ratio={strict.ratio}, amount={strict.amount}"
)

# Note: In Pydantic v2, strict mode primarily prevents string coercion,
# numeric types (int/float) may still be coerced between each other

print("\n\n=== Key Features Demonstrated ===")
print("1. gt/ge/lt/le - Comprehensive bounds checking")
print("2. multiple_of - Value must be divisible by specified number")
print("3. strict - No type coercion when True")
print("4. Works with INTEGER, BIGINT, SMALLINT, TINYINT")
print("5. Works with FLOAT and DECIMAL types")
print("6. Mock generation respects all constraints")
print("7. Clear validation error messages")
print("8. Supports additional Pydantic parameters via **kwargs")
