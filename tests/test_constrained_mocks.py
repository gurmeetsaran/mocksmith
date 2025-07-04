#!/usr/bin/env python3
"""Test cases for constrained type mock generation."""

from decimal import Decimal

import pytest

from mocksmith import (
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedMoney,
    NonNegativeMoney,
    PositiveMoney,
    mockable,
)

# Try to import pydantic, but tests should work without it
try:
    from pydantic import BaseModel, ValidationError, condecimal, confloat, conint

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    ValidationError = ValueError  # Use ValueError when pydantic not available


# Skip pydantic-specific tests if not available
pytestmark = pytest.mark.skipif(
    not PYDANTIC_AVAILABLE, reason="These tests require pydantic for BaseModel support"
)


class TestConstrainedMoneyMocks:
    """Test mock generation for constrained money types."""

    def test_positive_money_mock(self):
        """Test that PositiveMoney generates values > 0."""

        @mockable
        class Product(BaseModel):
            price: PositiveMoney()

        for _ in range(20):
            product = Product.mock()
            assert isinstance(product.price, Decimal)
            assert product.price > 0
            # Check decimal places (exponent is negative for decimal places)
            exponent = product.price.as_tuple().exponent
            assert isinstance(exponent, int) and exponent >= -4  # Max 4 decimal places

    def test_non_negative_money_mock(self):
        """Test that NonNegativeMoney generates values >= 0."""

        @mockable
        class Account(BaseModel):
            balance: NonNegativeMoney()

        for _ in range(20):
            account = Account.mock()
            assert isinstance(account.balance, Decimal)
            assert account.balance >= 0
            exponent = account.balance.as_tuple().exponent
            assert isinstance(exponent, int) and exponent >= -4

    def test_constrained_money_range(self):
        """Test ConstrainedMoney with specific range."""

        @mockable
        class Discount(BaseModel):
            amount: ConstrainedMoney(ge=0, le=100)
            percentage: ConstrainedMoney(gt=0, lt=50)

        for _ in range(20):
            discount = Discount.mock()
            assert 0 <= discount.amount <= 100
            assert 0 < discount.percentage < 50

    def test_constrained_money_validation(self):
        """Test that constraints are enforced during validation."""

        class Price(BaseModel):
            amount: ConstrainedMoney(gt=0, le=1000)

        # Valid values
        Price(amount=Decimal("10.50"))
        Price(amount=Decimal("1000.00"))

        # Invalid - should raise ValidationError
        with pytest.raises(ValidationError):
            Price(amount=Decimal("0"))  # Not greater than 0

        with pytest.raises(ValidationError):
            Price(amount=Decimal("1000.01"))  # Greater than 1000


class TestConstrainedDecimalMocks:
    """Test mock generation for constrained decimal types."""

    def test_constrained_decimal_basic(self):
        """Test basic decimal constraints."""

        @mockable
        class Measurement(BaseModel):
            value: ConstrainedDecimal(10, 2, ge=0, le=100)

        for _ in range(20):
            m = Measurement.mock()
            assert isinstance(m.value, Decimal)
            assert 0 <= m.value <= 100
            # Check decimal places
            str_val = str(m.value)
            if "." in str_val:
                decimal_places = len(str_val.split(".")[1])
                assert decimal_places <= 2

    def test_constrained_decimal_precision(self):
        """Test decimal with high precision."""

        @mockable
        class Precise(BaseModel):
            value: ConstrainedDecimal(20, 10, gt=0, lt=1)

        for _ in range(10):
            p = Precise.mock()
            assert 0 < p.value < 1
            # Check it generates with appropriate precision
            str_val = str(p.value)
            if "." in str_val:
                decimal_places = len(str_val.split(".")[1])
                assert decimal_places <= 10


class TestConstrainedFloatMocks:
    """Test mock generation for constrained float types."""

    def test_constrained_float_basic(self):
        """Test basic float constraints."""

        @mockable
        class Data(BaseModel):
            temperature: ConstrainedFloat(ge=-273.15, le=1000)
            ratio: ConstrainedFloat(ge=0, le=1)

        for _ in range(20):
            d = Data.mock()
            assert -273.15 <= d.temperature <= 1000
            assert 0 <= d.ratio <= 1

        # Test validation
        with pytest.raises(ValidationError):
            Data(temperature=-300, ratio=0.5)  # Below absolute zero

        with pytest.raises(ValidationError):
            Data(temperature=20, ratio=1.5)  # Ratio > 1

    def test_constrained_float_infinity(self):
        """Test float constraints with infinity handling."""

        @mockable
        class Scientific(BaseModel):
            normal: ConstrainedFloat()
            ratio: ConstrainedFloat(ge=0, le=1)

        # Normal values should work
        Scientific(normal=1.0, ratio=0.5)

        # Out of range should fail
        with pytest.raises(ValidationError):
            Scientific(normal=1.0, ratio=1.5)  # ratio > 1


class TestMixedConstraints:
    """Test models with mixed constraint types."""

    def test_mixed_numeric_constraints(self):
        """Test model with various numeric constraints."""

        @mockable
        class Model(BaseModel):
            money: PositiveMoney()
            percent: ConstrainedFloat(ge=0, le=100)
            count: conint(ge=0, le=1000)

        for _ in range(10):
            m = Model.mock()
            assert m.money > 0
            assert 0 <= m.percent <= 100
            assert 0 <= m.count <= 1000

        # Test validation
        with pytest.raises(ValidationError):
            Model(money=Decimal("-10"), percent=50, count=100)

        with pytest.raises(ValidationError):
            Model(money=Decimal("10"), percent=150, count=100)

    def test_complex_business_model(self):
        """Test realistic business model with constraints."""

        @mockable
        class Order(BaseModel):
            subtotal: NonNegativeMoney()
            tax: ConstrainedMoney(ge=0, le=1000)
            discount: ConstrainedMoney(ge=0, le=1000)
            total: PositiveMoney()

        for _ in range(10):
            order = Order.mock()
            assert order.subtotal >= 0
            assert 0 <= order.tax <= 1000
            assert 0 <= order.discount <= 1000
            assert order.total > 0

    def test_pydantic_compatibility(self):
        """Test that our types work with pydantic's constraint types."""

        @mockable
        class Mixed(BaseModel):
            quantity: conint(ge=1, le=100)
            rating: confloat(ge=0.0, le=5.0)
            price: ConstrainedMoney(gt=0, le=1000)
            precise: condecimal(max_digits=10, decimal_places=4)

        for _ in range(10):
            m = Mixed.mock()
            assert 1 <= m.quantity <= 100
            assert 0.0 <= m.rating <= 5.0
            assert 0 < m.price <= 1000
            assert isinstance(m.precise, Decimal)
