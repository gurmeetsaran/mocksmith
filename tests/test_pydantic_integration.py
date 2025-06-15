"""Tests for Pydantic integration."""

import pytest
from typing import Optional
from db_types import VARCHAR, INTEGER, DATE, BOOLEAN
from db_types.pydantic_integration import (
    PYDANTIC_AVAILABLE, DBModel, Annotated, create_db_field
)

if not PYDANTIC_AVAILABLE:
    pytest.skip("Pydantic not installed", allow_module_level=True)

from pydantic import BaseModel, ValidationError
from datetime import date


class TestPydanticIntegration:
    def test_basic_model(self):
        class User(BaseModel):
            name: Annotated[VARCHAR(50)]
            age: Annotated[INTEGER()]
            active: Annotated[BOOLEAN()]
        
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
            name: Annotated[VARCHAR(100, nullable=False)]
            description: Annotated[VARCHAR(500, nullable=True)]
        
        # Valid with null
        product = Product(name="Test", description=None)
        assert product.description is None
        
        # Invalid with null for non-nullable
        with pytest.raises(ValidationError):
            Product(name=None, description="Test")
    
    def test_numeric_validation(self):
        class Account(BaseModel):
            balance: Annotated[INTEGER()]
            small_val: Annotated[INTEGER()]  # Using INTEGER for simplicity
        
        # Valid
        account = Account(balance=1000, small_val=100)
        assert account.balance == 1000
        
        # Out of range
        with pytest.raises(ValidationError):
            Account(balance=2147483648, small_val=100)  # Too large for INTEGER
    
    def test_date_handling(self):
        class Event(BaseModel):
            name: Annotated[VARCHAR(100)]
            event_date: Annotated[DATE()]
        
        # From string
        event = Event(name="Conference", event_date="2023-12-25")
        assert isinstance(event.event_date, date)
        assert event.event_date == date(2023, 12, 25)
        
        # From date object
        event2 = Event(name="Meeting", event_date=date(2023, 6, 15))
        assert event2.event_date == date(2023, 6, 15)
    
    def test_serialization(self):
        class User(BaseModel):
            name: Annotated[VARCHAR(50)]
            joined: Annotated[DATE()]
            active: Annotated[BOOLEAN()]
        
        user = User(
            name="Alice",
            joined=date(2023, 1, 1),
            active=True
        )
        
        # Pydantic serialization
        data = user.model_dump()
        assert data["name"] == "Alice"
        assert data["joined"] == date(2023, 1, 1)
        assert data["active"] is True
    
    def test_db_model_base(self):
        class User(DBModel):
            name: Annotated[VARCHAR(50)]
            age: Annotated[INTEGER()]
        
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
    
    def test_create_db_field(self):
        class Product(BaseModel):
            name: str = create_db_field(VARCHAR(100), description="Product name")
            price: Optional[int] = create_db_field(INTEGER(), default=None)
        
        # Check field info
        assert Product.model_fields["name"].description == "Product name"
        assert Product.model_fields["price"].default is None
    
    def test_complex_validation(self):
        from decimal import Decimal
        from db_types import DECIMAL
        
        class Invoice(BaseModel):
            number: Annotated[VARCHAR(20)]
            amount: Annotated[DECIMAL(10, 2)]
            paid: Annotated[BOOLEAN()]
        
        # Valid decimal
        invoice = Invoice(number="INV-001", amount="1234.56", paid=False)
        assert isinstance(invoice.amount, Decimal)
        assert invoice.amount == Decimal("1234.56")
        
        # Too many decimal places
        with pytest.raises(ValidationError):
            Invoice(number="INV-002", amount="1234.567", paid=False)
        
        # Too many total digits
        with pytest.raises(ValidationError):
            Invoice(number="INV-003", amount="12345678.90", paid=False)