#!/usr/bin/env python3
"""Test cases for constrained type mock generation."""

from decimal import Decimal

import pytest
from pydantic import BaseModel, ValidationError, condecimal, confloat, conint

from mocksmith import (
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedMoney,
    NonNegativeMoney,
    PositiveMoney,
    mockable,
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
            value: PositiveMoney()

        # Valid
        price = Price(value="10.50")
        assert price.value == Decimal("10.50")

        # Invalid - should raise ValidationError
        with pytest.raises(ValidationError):
            Price(value="0.00")  # Not positive

        with pytest.raises(ValidationError):
            Price(value="-10.00")  # Negative


class TestConstrainedDecimalMocks:
    """Test mock generation for constrained decimal types."""

    def test_constrained_decimal_basic(self):
        """Test basic ConstrainedDecimal mock generation."""

        @mockable
        class Measurement(BaseModel):
            weight: ConstrainedDecimal(10, 2, gt=0)
            temperature: ConstrainedDecimal(5, 2, ge=-273.15, le=100)

        for _ in range(20):
            m = Measurement.mock()
            assert isinstance(m.weight, Decimal)
            assert isinstance(m.temperature, Decimal)
            assert m.weight > 0
            assert -273.15 <= m.temperature <= 100
            # Check decimal places
            weight_exp = m.weight.as_tuple().exponent
            temp_exp = m.temperature.as_tuple().exponent
            assert isinstance(weight_exp, int) and weight_exp >= -2
            assert isinstance(temp_exp, int) and temp_exp >= -2

    def test_constrained_decimal_precision(self):
        """Test that decimal precision constraints are respected."""

        @mockable
        class Precise(BaseModel):
            # Max 5 total digits, 3 decimal places -> max integer part is 99
            small: ConstrainedDecimal(5, 3, ge=0)
            # Max 10 total digits, 2 decimal places -> max integer part is 99999999
            large: ConstrainedDecimal(10, 2, ge=0)

        for _ in range(10):
            p = Precise.mock()
            # Check total digits
            assert abs(p.small) < 100  # Max 99.999
            assert abs(p.large) < 100000000  # Max 99999999.99

    def test_constrained_decimal_validation(self):
        """Test decimal constraint validation."""

        class Data(BaseModel):
            value: ConstrainedDecimal(10, 2, ge=0, le=1000)

        # Valid
        data = Data(value="500.25")
        assert data.value == Decimal("500.25")

        # Invalid - out of range
        with pytest.raises(ValidationError):
            Data(value="1001.00")

        with pytest.raises(ValidationError):
            Data(value="-1.00")


class TestConstrainedFloatMocks:
    """Test mock generation for constrained float types."""

    def test_constrained_float_basic(self):
        """Test basic ConstrainedFloat mock generation."""

        @mockable
        class Scientific(BaseModel):
            probability: ConstrainedFloat(ge=0.0, le=1.0)
            temperature: ConstrainedFloat(gt=-273.15)
            ratio: ConstrainedFloat(gt=0, lt=100)

        for _ in range(20):
            s = Scientific.mock()
            assert isinstance(s.probability, float)
            assert isinstance(s.temperature, float)
            assert isinstance(s.ratio, float)
            assert 0.0 <= s.probability <= 1.0
            assert s.temperature > -273.15
            assert 0 < s.ratio < 100

    def test_constrained_float_validation(self):
        """Test float constraint validation."""

        class Model(BaseModel):
            percentage: ConstrainedFloat(ge=0, le=100)

        # Valid
        model = Model(percentage=50.5)
        assert model.percentage == 50.5

        # Invalid
        with pytest.raises(ValidationError):
            Model(percentage=101.0)

        with pytest.raises(ValidationError):
            Model(percentage=-1.0)


class TestMixedConstrainedTypes:
    """Test models with multiple constrained types."""

    def test_complex_model(self):
        """Test a model with various constrained types."""

        @mockable
        class Order(BaseModel):
            # Money types
            subtotal: PositiveMoney()
            discount: ConstrainedMoney(ge=0, le=50)
            tax: NonNegativeMoney()
            shipping: ConstrainedMoney(ge=0, le=25)

            # Decimal types
            weight_kg: ConstrainedDecimal(10, 3, gt=0, le=1000)
            volume_m3: ConstrainedDecimal(8, 4, gt=0)

            # Float types
            discount_rate: ConstrainedFloat(ge=0.0, le=0.5)
            priority: ConstrainedFloat(ge=0.0, le=1.0)

            # Regular Pydantic constraints
            quantity: conint(ge=1, le=100)
            rating: confloat(ge=0.0, le=5.0)

        for _ in range(10):
            order = Order.mock()

            # Money assertions
            assert order.subtotal > 0
            assert 0 <= order.discount <= 50
            assert order.tax >= 0
            assert 0 <= order.shipping <= 25

            # Decimal assertions
            assert 0 < order.weight_kg <= 1000
            weight_exp = order.weight_kg.as_tuple().exponent
            assert isinstance(weight_exp, int) and weight_exp >= -3
            assert order.volume_m3 > 0
            volume_exp = order.volume_m3.as_tuple().exponent
            assert isinstance(volume_exp, int) and volume_exp >= -4

            # Float assertions
            assert 0.0 <= order.discount_rate <= 0.5
            assert 0.0 <= order.priority <= 1.0

            # Pydantic constraint assertions
            assert 1 <= order.quantity <= 100
            assert 0.0 <= order.rating <= 5.0

    def test_mock_with_overrides(self):
        """Test that mock overrides work with constrained types."""

        @mockable
        class Product(BaseModel):
            price: PositiveMoney()
            discount: ConstrainedMoney(ge=0, le=100)
            weight: ConstrainedDecimal(10, 2, gt=0)

        product = Product.mock(price="99.99", discount="25.00", weight="10.5")

        assert product.price == Decimal("99.99")
        assert product.discount == Decimal("25.00")
        assert product.weight == Decimal("10.5")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_tight_constraints(self):
        """Test very tight constraint ranges."""

        @mockable
        class Tight(BaseModel):
            # Very narrow range
            narrow_float: ConstrainedFloat(ge=0.999, le=1.001)
            # Small positive range
            small_positive: ConstrainedMoney(gt=0, le=0.10)

        # Should generate without errors
        for _ in range(5):
            tight = Tight.mock()
            assert 0.999 <= tight.narrow_float <= 1.001
            assert 0 < tight.small_positive <= Decimal("0.10")

    def test_large_values(self):
        """Test large value constraints."""

        @mockable
        class Large(BaseModel):
            big_money: ConstrainedMoney(ge=1_000_000, le=10_000_000)
            big_decimal: ConstrainedDecimal(15, 2, ge=1_000_000)

        for _ in range(5):
            large = Large.mock()
            assert 1_000_000 <= large.big_money <= 10_000_000
            assert large.big_decimal >= 1_000_000

    def test_negative_ranges(self):
        """Test negative value constraints."""

        @mockable
        class Negative(BaseModel):
            debt: ConstrainedMoney(lt=0, ge=-10000)
            temperature: ConstrainedFloat(ge=-50, le=-10)

        for _ in range(10):
            neg = Negative.mock()
            assert -10000 <= neg.debt < 0
            assert -50 <= neg.temperature <= -10


class TestPydanticCompatibility:
    """Test compatibility with Pydantic's native constraint types."""

    def test_pydantic_v2_constraints(self):
        """Test that Pydantic v2 native constraints work."""

        @mockable
        class PydanticModel(BaseModel):
            # Native Pydantic constraints
            age: conint(ge=0, le=120)
            score: confloat(ge=0.0, le=100.0)
            price: condecimal(max_digits=10, decimal_places=2, ge=0)

        for _ in range(10):
            model = PydanticModel.mock()
            assert 0 <= model.age <= 120
            assert 0.0 <= model.score <= 100.0
            assert model.price >= 0
            assert isinstance(model.price, Decimal)

    def test_mixed_mocksmith_and_pydantic(self):
        """Test mixing mocksmith and Pydantic constraints."""

        @mockable
        class Mixed(BaseModel):
            # Mocksmith constraints
            price: PositiveMoney()
            weight: ConstrainedDecimal(10, 2, gt=0)

            # Pydantic constraints
            quantity: conint(ge=1)
            discount: confloat(ge=0.0, le=1.0)

        for _ in range(10):
            mixed = Mixed.mock()
            assert mixed.price > 0
            assert mixed.weight > 0
            assert mixed.quantity >= 1
            assert 0.0 <= mixed.discount <= 1.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
