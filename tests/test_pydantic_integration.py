"""Tests for Pydantic integration."""

from typing import Annotated, Optional

import pytest

from mocksmith import BOOLEAN, DATE, INTEGER, VARCHAR
from mocksmith.pydantic_integration import PYDANTIC_AVAILABLE, DBModel, DBTypeValidator

if not PYDANTIC_AVAILABLE:
    pytest.skip("Pydantic not installed", allow_module_level=True)

from datetime import date

from pydantic import BaseModel, ValidationError


class TestPydanticIntegration:
    def test_basic_model(self):
        class User(BaseModel):
            name: Annotated[str, DBTypeValidator(VARCHAR(50))]
            age: Annotated[int, DBTypeValidator(INTEGER())]
            active: Annotated[bool, DBTypeValidator(BOOLEAN())]

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
            name: Annotated[str, DBTypeValidator(VARCHAR(100))]
            description: Optional[Annotated[str, DBTypeValidator(VARCHAR(500))]]

        # Valid with null
        product = Product(name="Test", description=None)
        assert product.description is None

        # Note: Pydantic's required field validation happens before our validator,
        # so we cannot test name=None here as it will raise ValidationError
        # from Pydantic's required field check, not from our nullable validation

    def test_numeric_validation(self):
        class Account(BaseModel):
            balance: Annotated[int, DBTypeValidator(INTEGER())]
            small_val: Annotated[int, DBTypeValidator(INTEGER())]  # Using INTEGER for simplicity

        # Valid
        account = Account(balance=1000, small_val=100)
        assert account.balance == 1000

        # Out of range
        with pytest.raises(ValidationError):
            Account(balance=2147483648, small_val=100)  # Too large for INTEGER

    def test_date_handling(self):
        class Event(BaseModel):
            name: Annotated[str, DBTypeValidator(VARCHAR(100))]
            event_date: Annotated[date, DBTypeValidator(DATE())]

        # From string
        event = Event(name="Conference", event_date="2023-12-25")
        assert isinstance(event.event_date, date)
        assert event.event_date == date(2023, 12, 25)

        # From date object
        event2 = Event(name="Meeting", event_date=date(2023, 6, 15))
        assert event2.event_date == date(2023, 6, 15)

    def test_serialization(self):
        class User(BaseModel):
            name: Annotated[str, DBTypeValidator(VARCHAR(50))]
            joined: Annotated[date, DBTypeValidator(DATE())]
            active: Annotated[bool, DBTypeValidator(BOOLEAN())]

        user = User(name="Alice", joined=date(2023, 1, 1), active=True)

        # Pydantic serialization
        data = user.model_dump()
        assert data["name"] == "Alice"
        assert data["joined"] == "2023-01-01"  # Date is serialized to string
        assert data["active"] is True

    def test_db_model_base(self):
        class User(DBModel):
            name: Annotated[str, DBTypeValidator(VARCHAR(50))]
            age: Annotated[int, DBTypeValidator(INTEGER())]

        user = User(name="Bob", age=25)

        # Get DB types
        db_types = user.get_db_types()
        assert "name" in db_types
        assert isinstance(db_types["name"], VARCHAR)
        assert db_types["name"].length == 50

        # SQL dict
        sql_dict = user.to_sql_dict()
        assert sql_dict["name"] == "Bob"
        assert sql_dict["age"] == 25

    def test_annotated_fields_with_defaults(self):
        class Product(BaseModel):
            name: Annotated[str, DBTypeValidator(VARCHAR(100))]
            price: Optional[Annotated[int, DBTypeValidator(INTEGER())]] = None

        # Test creation with defaults
        product = Product(name="Test Product")
        assert product.name == "Test Product"
        assert product.price is None

        # Test with values
        product2 = Product(name="Another Product", price=100)
        assert product2.name == "Another Product"
        assert product2.price == 100

    def test_complex_validation(self):
        from decimal import Decimal

        from mocksmith import DECIMAL

        class Invoice(BaseModel):
            number: Annotated[str, DBTypeValidator(VARCHAR(20))]
            amount: Annotated[Decimal, DBTypeValidator(DECIMAL(10, 2))]
            paid: Annotated[bool, DBTypeValidator(BOOLEAN())]

        # Valid decimal
        invoice = Invoice(number="INV-001", amount="1234.56", paid=False)
        assert isinstance(invoice.amount, Decimal)
        assert invoice.amount == Decimal("1234.56")

        # Too many decimal places
        with pytest.raises(ValidationError):
            Invoice(number="INV-002", amount="1234.567", paid=False)

        # Too many total digits (DECIMAL(10,2) allows max 8 integer digits + 2 decimal)
        with pytest.raises(ValidationError):
            Invoice(number="INV-003", amount="123456789.00", paid=False)
