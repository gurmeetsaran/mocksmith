"""Tests for dataclass integration."""

import pytest
from dataclasses import dataclass
from typing import Optional
import sys

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from db_types import VARCHAR, INTEGER, DATE, BOOLEAN
from db_types.dataclass_integration import (
    validate_dataclass, db_field, DBDataclass
)
from datetime import date


class TestDataclassIntegration:
    def test_basic_dataclass(self):
        @validate_dataclass
        @dataclass
        class User:
            name: Annotated[str, VARCHAR(50)]
            age: Annotated[int, INTEGER()]
            active: Annotated[bool, BOOLEAN()]
        
        # Valid data
        user = User(name="John", age=30, active=True)
        assert user.name == "John"
        assert user.age == 30
        assert user.active is True
        
        # Validation should work
        with pytest.raises(ValueError, match="exceeds maximum"):
            User(name="x" * 51, age=30, active=True)
    
    def test_db_field_usage(self):
        @dataclass
        class Product:
            name: str = db_field(VARCHAR(100, nullable=False))
            description: str = db_field(VARCHAR(500), default=None)
            price: int = db_field(INTEGER(), default=0)
        
        # Use validate_dataclass decorator
        Product = validate_dataclass(Product)
        
        # Valid
        product = Product(name="Test Product")
        assert product.name == "Test Product"
        assert product.description is None
        assert product.price == 0
        
        # With all fields
        product2 = Product(name="Another", description="Desc", price=100)
        assert product2.description == "Desc"
        assert product2.price == 100
    
    def test_nullable_handling(self):
        @validate_dataclass
        @dataclass
        class Article:
            title: Annotated[str, VARCHAR(200, nullable=False)]
            subtitle: Annotated[Optional[str], VARCHAR(200, nullable=True)]
        
        # Valid with None
        article = Article(title="Main Title", subtitle=None)
        assert article.subtitle is None
        
        # Invalid with None for non-nullable
        with pytest.raises(ValueError, match="NULL value not allowed"):
            Article(title=None, subtitle="Sub")
    
    def test_numeric_validation(self):
        @validate_dataclass
        @dataclass
        class Account:
            id: Annotated[int, INTEGER()]
            balance: Annotated[int, INTEGER()]
        
        # Valid
        account = Account(id=1, balance=1000)
        assert account.balance == 1000
        
        # Out of range
        with pytest.raises(ValueError, match="out of range"):
            Account(id=1, balance=2147483648)
    
    def test_date_handling(self):
        @validate_dataclass
        @dataclass
        class Event:
            name: Annotated[str, VARCHAR(100)]
            event_date: Annotated[date, DATE()]
        
        # From string
        event = Event(name="Conference", event_date="2023-12-25")
        assert isinstance(event.event_date, date)
        assert event.event_date == date(2023, 12, 25)
        
        # From date object
        event2 = Event(name="Meeting", event_date=date(2023, 6, 15))
        assert event2.event_date == date(2023, 6, 15)
    
    def test_helper_methods(self):
        @validate_dataclass
        @dataclass
        class User:
            name: Annotated[str, VARCHAR(50)]
            age: Annotated[int, INTEGER()]
            active: Annotated[bool, BOOLEAN()]
        
        user = User(name="Alice", age=25, active=True)
        
        # Get DB types
        db_types = user.get_db_types()
        assert "name" in db_types
        assert isinstance(db_types["name"], VARCHAR)
        assert db_types["name"].length == 50
        
        # SQL dict
        sql_dict = user.to_sql_dict()
        assert sql_dict["name"] == "Alice"
        assert sql_dict["age"] == 25
        assert sql_dict["active"] is True
        
        # Validate all
        user.validate_all()  # Should not raise
    
    def test_inheritance(self):
        @validate_dataclass
        @dataclass
        class BaseEntity(DBDataclass):
            id: Annotated[int, INTEGER()]
            created: Annotated[date, DATE()]
        
        @validate_dataclass
        @dataclass
        class User(BaseEntity):
            name: Annotated[str, VARCHAR(100)]
            email: Annotated[str, VARCHAR(200)]
        
        user = User(
            id=1,
            created=date(2023, 1, 1),
            name="Bob",
            email="bob@example.com"
        )
        
        assert user.id == 1
        assert user.name == "Bob"
        
        # Validation should work on all fields
        with pytest.raises(ValueError, match="exceeds maximum"):
            User(
                id=1,
                created=date(2023, 1, 1),
                name="x" * 101,  # Too long
                email="test@example.com"
            )
    
    def test_complex_types(self):
        from decimal import Decimal
        from db_types import DECIMAL, TIMESTAMP
        from datetime import datetime
        
        @validate_dataclass
        @dataclass
        class Invoice:
            number: Annotated[str, VARCHAR(20)]
            amount: Annotated[Decimal, DECIMAL(10, 2)]
            created_at: Annotated[datetime, TIMESTAMP(with_timezone=False)]
        
        invoice = Invoice(
            number="INV-001",
            amount="1234.56",
            created_at="2023-01-01T12:00:00"
        )
        
        assert isinstance(invoice.amount, Decimal)
        assert invoice.amount == Decimal("1234.56")
        assert isinstance(invoice.created_at, datetime)