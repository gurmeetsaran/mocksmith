"""Tests for Pydantic integration."""

from typing import Optional

import pytest

from mocksmith import Boolean, Date, DecimalType, Integer, PositiveInteger, Varchar

try:
    from pydantic import BaseModel, ValidationError

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    pytest.skip("Pydantic not installed", allow_module_level=True)

from datetime import date
from decimal import Decimal


class TestPydanticIntegration:
    def test_basic_model(self):
        class User(BaseModel):
            name: Varchar(50)
            age: Integer()
            active: Boolean()

        # Valid data
        user = User(name="John", age=30, active=True)
        assert user.name == "John"
        assert user.age == 30
        assert user.active is True

        # Validation should work
        with pytest.raises(ValidationError):
            User(name="x" * 51, age=30, active=True)  # name too long

    def test_nullable_fields(self):
        class Product(BaseModel):
            name: Varchar(100)
            description: Optional[Varchar(500)] = None

        # Valid with null
        product = Product(name="Test", description=None)
        assert product.description is None

        # Valid with value
        product2 = Product(name="Test", description="A product description")
        assert product2.description == "A product description"

    def test_numeric_validation(self):
        class Account(BaseModel):
            balance: Integer()
            small_val: Integer()

        # Valid
        account = Account(balance=1000, small_val=100)
        assert account.balance == 1000

        # Out of range
        with pytest.raises(ValidationError):
            Account(balance=2147483648, small_val=100)  # Too large for INTEGER

    def test_date_handling(self):
        class Event(BaseModel):
            name: Varchar(100)
            event_date: Date()

        # From string
        event = Event(name="Conference", event_date="2023-12-25")
        assert isinstance(event.event_date, date)
        assert event.event_date == date(2023, 12, 25)

        # From date object
        event2 = Event(name="Meeting", event_date=date(2023, 6, 15))
        assert event2.event_date == date(2023, 6, 15)

    def test_serialization(self):
        class User(BaseModel):
            name: Varchar(50)
            joined: Date()
            active: Boolean()

        user = User(name="Alice", joined=date(2023, 1, 1), active=True)

        # Pydantic serialization - our DBTypeValidator serializes dates to strings
        data = user.model_dump()
        assert data["name"] == "Alice"
        assert data["joined"] == "2023-01-01"  # DBTypeValidator serializes to ISO string
        assert data["active"] is True

    def test_db_model_base(self):
        """Test model with database types."""

        class User(BaseModel):
            name: Varchar(50)
            age: Integer()

        user = User(name="Bob", age=25)

        # Check values
        assert user.name == "Bob"
        assert user.age == 25

        # Check that validation works
        with pytest.raises(ValidationError):
            User(name="x" * 51, age=25)  # name too long

    def test_annotated_fields_with_defaults(self):
        class Product(BaseModel):
            name: Varchar(100)
            price: Optional[Integer()] = None

        # Test creation with defaults
        product = Product(name="Test Product")
        assert product.name == "Test Product"
        assert product.price is None

        # Test with values
        product2 = Product(name="Another Product", price=100)
        assert product2.name == "Another Product"
        assert product2.price == 100

    def test_complex_validation(self):
        class Invoice(BaseModel):
            number: Varchar(20)
            amount: DecimalType(10, 2)
            paid: Boolean()

        # Valid decimal
        invoice = Invoice(number="INV-001", amount="1234.56", paid=False)
        assert isinstance(invoice.amount, Decimal)
        assert invoice.amount == Decimal("1234.56")

        # Too many decimal places (will be rounded)
        invoice2 = Invoice(number="INV-002", amount="1234.567", paid=False)
        assert invoice2.amount == Decimal("1234.57")  # Rounded

        # Too many total digits (DECIMAL(10,2) allows max 8 integer digits + 2 decimal)
        with pytest.raises(ValidationError):
            Invoice(number="INV-003", amount="123456789.00", paid=False)

    def test_constrained_numeric_types(self):
        """Test the new constrained numeric types."""
        from mocksmith import NonNegativeInteger, PositiveInteger, TinyInt

        class GameStats(BaseModel):
            player_id: PositiveInteger()
            score: NonNegativeInteger()
            level: TinyInt(ge=1, le=100)

        # Valid
        stats = GameStats(player_id=42, score=1000, level=10)
        assert stats.player_id == 42
        assert stats.score == 1000
        assert stats.level == 10

        # Invalid player_id (must be positive)
        with pytest.raises(ValidationError):
            GameStats(player_id=0, score=100, level=5)

        # Invalid score (must be non-negative)
        with pytest.raises(ValidationError):
            GameStats(player_id=1, score=-10, level=5)

        # Invalid level (exceeds TinyInt max of 127)
        with pytest.raises(ValidationError):
            GameStats(player_id=1, score=100, level=150)

    def test_money_types(self):
        """Test money types with decimal precision."""
        from mocksmith import Money, PositiveMoney

        class Order(BaseModel):
            total: PositiveMoney()
            discount: Money()

        # Valid
        order = Order(total="99.99", discount="10.50")
        assert order.total == Decimal("99.99")
        assert order.discount == Decimal("10.50")

        # Invalid total (must be positive)
        with pytest.raises(ValidationError):
            Order(total="0.00", discount="5.00")

        # Negative discount is allowed for Money
        order2 = Order(total="100.00", discount="-5.00")
        assert order2.discount == Decimal("-5.00")

    def test_string_type_conversion(self):
        """Test that string values are properly converted."""

        class TestModel(BaseModel):
            int_field: Integer()
            bool_field: Boolean()
            decimal_field: DecimalType(10, 2)

        # String conversions
        model = TestModel(int_field="42", bool_field="yes", decimal_field="123.45")

        assert model.int_field == 42
        assert model.bool_field is True
        assert model.decimal_field == Decimal("123.45")

        # Boolean conversion variations
        model2 = TestModel(int_field=10, bool_field="false", decimal_field="0.00")
        assert model2.bool_field is False

    def test_integration_with_pydantic_validators(self):
        """Test that our types work with Pydantic's validators."""
        from pydantic import field_validator

        class Product(BaseModel):
            name: Varchar(100)
            price: PositiveInteger()

            @field_validator("price")
            @classmethod
            def price_must_be_reasonable(cls, v):
                if v > 1000000:
                    raise ValueError("Price too high")
                return v

        # Valid
        product = Product(name="Widget", price=100)
        assert product.price == 100

        # Our validation (must be positive)
        with pytest.raises(ValidationError):
            Product(name="Widget", price=0)

        # Pydantic validator
        with pytest.raises(ValidationError) as exc_info:
            Product(name="Widget", price=2000000)
        assert "Price too high" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
