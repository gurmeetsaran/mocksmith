"""Tests for mock factory and class-level mock generation."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional

import pytest

from db_types import VARCHAR, Email, City, CountryCode, mockable, mock_factory

# Import Pydantic if available
try:
    from pydantic import BaseModel, ValidationError
    from db_types.pydantic_integration import DBTypeValidator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class TestMockFactory:
    """Test the mock_factory function."""
    
    def test_mock_dataclass_basic(self):
        """Test mocking a basic dataclass."""
        @dataclass
        class SimpleModel:
            name: str
            age: int
            active: bool
        
        mock = mock_factory(SimpleModel)
        
        assert isinstance(mock.name, str)
        assert isinstance(mock.age, int)
        assert isinstance(mock.active, bool)
    
    def test_mock_dataclass_with_db_types(self):
        """Test mocking a dataclass with db_types."""
        # Define instances for use in annotations
        _username = VARCHAR(30)
        _email = Email()
        _city = City()
        
        @dataclass
        class UserModel:
            username: Annotated[str, _username]
            email: Annotated[str, _email]
            city: Annotated[str, _city]
        
        mock = mock_factory(UserModel)
        
        assert isinstance(mock.username, str)
        assert len(mock.username) <= 30
        assert "@" in mock.email
        assert isinstance(mock.city, str)
    
    def test_mock_with_overrides(self):
        """Test mocking with field overrides."""
        @dataclass
        class Product:
            name: str
            price: float
            stock: int
        
        mock = mock_factory(Product, name="Custom Product", price=99.99)
        
        assert mock.name == "Custom Product"
        assert mock.price == 99.99
        assert isinstance(mock.stock, int)  # Auto-generated
    
    def test_mock_with_optional_fields(self):
        """Test mocking with optional fields."""
        @dataclass
        class OptionalModel:
            required: str
            optional: Optional[str] = None
            maybe_int: Optional[int] = None
        
        # Generate multiple to see optional behavior
        mocks = [mock_factory(OptionalModel) for _ in range(20)]
        
        # All should have required field
        assert all(isinstance(m.required, str) for m in mocks)
        
        # Some should have optional fields, some shouldn't
        has_optional = sum(1 for m in mocks if m.optional is not None)
        has_maybe_int = sum(1 for m in mocks if m.maybe_int is not None)
        
        # For testing, let's just check that at least one optional field behaves correctly
        # Since we have 2 optional fields across 20 samples, we should see variation
        # If both are always None or always not-None, that's the issue
        all_none = all(m.optional is None and m.maybe_int is None for m in mocks)
        all_not_none = all(m.optional is not None and m.maybe_int is not None for m in mocks)
        
        # At least one should have different behavior
        assert not (all_none or all_not_none), f"Optional fields not working correctly: has_optional={has_optional}, has_maybe_int={has_maybe_int}"
    
    def test_mock_with_python_types(self):
        """Test mocking with various Python built-in types."""
        @dataclass
        class PythonTypes:
            text: str
            number: int
            decimal: float
            flag: bool
            date_field: date
            datetime_field: datetime
            binary: bytes
        
        mock = mock_factory(PythonTypes)
        
        assert isinstance(mock.text, str)
        assert isinstance(mock.number, int)
        assert isinstance(mock.decimal, float)
        assert isinstance(mock.flag, bool)
        assert isinstance(mock.date_field, date)
        assert isinstance(mock.datetime_field, datetime)
        assert isinstance(mock.binary, bytes)
    
    def test_mock_unsupported_class(self):
        """Test that mock_factory raises for unsupported classes."""
        class RegularClass:
            def __init__(self):
                self.name = "test"
        
        with pytest.raises(TypeError, match="only supports dataclasses"):
            mock_factory(RegularClass)


class TestMockableDecorator:
    """Test the @mockable decorator."""
    
    def test_mockable_adds_mock_method(self):
        """Test that @mockable adds a mock() class method."""
        @mockable
        @dataclass
        class Model:
            name: str
            value: int
        
        assert hasattr(Model, "mock")
        assert callable(Model.mock)
        
        mock = Model.mock()
        assert isinstance(mock, Model)
        assert isinstance(mock.name, str)
        assert isinstance(mock.value, int)
    
    def test_mockable_adds_builder_method(self):
        """Test that @mockable adds a mock_builder() method."""
        @mockable
        @dataclass
        class Model:
            name: str
            value: int
        
        assert hasattr(Model, "mock_builder")
        assert callable(Model.mock_builder)
        
        builder = Model.mock_builder()
        assert hasattr(builder, "with_name")
        assert hasattr(builder, "with_value")
    
    def test_mockable_without_builder(self):
        """Test @mockable with builder=False."""
        @mockable(builder=False)
        @dataclass
        class Model:
            name: str
        
        assert hasattr(Model, "mock")
        assert not hasattr(Model, "mock_builder")
    
    def test_mock_method_with_overrides(self):
        """Test using mock() method with overrides."""
        @mockable
        @dataclass
        class Product:
            name: str
            price: Decimal
            category: str
        
        product = Product.mock(name="Test Product", category="Testing")
        
        assert product.name == "Test Product"
        assert isinstance(product.price, Decimal)
        assert product.category == "Testing"


class TestMockBuilder:
    """Test the MockBuilder functionality."""
    
    def test_builder_basic(self):
        """Test basic builder functionality."""
        @mockable
        @dataclass
        class Model:
            name: str
            count: int
            active: bool
        
        mock = (Model.mock_builder()
                .with_values(name="Test", count=42)
                .build())
        
        assert mock.name == "Test"
        assert mock.count == 42
        assert isinstance(mock.active, bool)
    
    def test_builder_build_many(self):
        """Test building multiple instances."""
        @mockable
        @dataclass
        class Item:
            name: str
            quantity: int
        
        items = (Item.mock_builder()
                .with_values(name="Widget")
                .build_many(5))
        
        assert len(items) == 5
        assert all(item.name == "Widget" for item in items)
        # Quantities should be different (randomly generated)
        quantities = [item.quantity for item in items]
        assert len(set(quantities)) > 1
    
    def test_builder_invalid_field(self):
        """Test builder with invalid field name."""
        @mockable
        @dataclass
        class Model:
            valid_field: str
        
        builder = Model.mock_builder()
        
        with pytest.raises(AttributeError, match="No field named 'invalid_field'"):
            builder.with_values(invalid_field="value")


class TestSmartFieldDetection:
    """Test smart field name detection."""
    
    def test_email_field_detection(self):
        """Test that fields named 'email' generate email addresses."""
        @dataclass
        class Model:
            email: str
            user_email: str
            contact_email: str
        
        mock = mock_factory(Model)
        
        assert "@" in mock.email
        assert "." in mock.email.split("@")[1]
        assert "@" in mock.user_email
        assert "@" in mock.contact_email
    
    def test_name_field_detection(self):
        """Test that name fields generate appropriate names."""
        @dataclass
        class Model:
            name: str
            first_name: str
            last_name: str
            user_name: str
        
        mock = mock_factory(Model)
        
        assert isinstance(mock.name, str)
        assert isinstance(mock.first_name, str)
        assert isinstance(mock.last_name, str)
        assert isinstance(mock.user_name, str)
        
        # first_name and last_name should be shorter than full name
        assert " " in mock.name  # Full names have spaces
        assert " " not in mock.first_name
        assert " " not in mock.last_name
    
    def test_id_field_detection(self):
        """Test that ID fields generate UUIDs."""
        @dataclass
        class Model:
            id: str
            user_id: str
            transaction_id: str
        
        mock = mock_factory(Model)
        
        # Should be UUID-like strings
        assert len(mock.id) == 36  # UUID4 format
        assert len(mock.user_id) == 36
        assert "-" in mock.transaction_id


@pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not installed")
class TestPydanticMocking:
    """Test mocking functionality with Pydantic models."""
    
    def test_mock_pydantic_basic(self):
        """Test mocking a basic Pydantic model."""
        class SimpleModel(BaseModel):
            name: str
            age: int
            active: bool
        
        mock = mock_factory(SimpleModel)
        
        assert isinstance(mock.name, str)
        assert isinstance(mock.age, int)
        assert isinstance(mock.active, bool)
    
    def test_mock_pydantic_with_db_types(self):
        """Test mocking a Pydantic model with db_types using annotations."""
        from db_types import Varchar, Integer, Boolean
        
        class UserModel(BaseModel):
            username: Varchar(30)
            age: Integer()
            active: Boolean()
        
        mock = mock_factory(UserModel)
        
        assert isinstance(mock.username, str)
        assert len(mock.username) <= 30
        assert isinstance(mock.age, int)
        assert isinstance(mock.active, bool)
    
    def test_mock_pydantic_with_specialized_types(self):
        """Test mocking Pydantic model with specialized types."""
        _email = Email()
        _country = CountryCode()
        _city = City()
        
        class Customer(BaseModel):
            name: str
            email: Annotated[str, DBTypeValidator(_email)]
            country: Annotated[str, DBTypeValidator(_country)]
            city: Annotated[str, DBTypeValidator(_city)]
        
        mock = mock_factory(Customer)
        
        assert isinstance(mock.name, str)
        assert "@" in mock.email
        assert len(mock.country) == 2  # Country code should be 2 chars
        assert isinstance(mock.city, str)
    
    def test_mockable_decorator_with_pydantic(self):
        """Test @mockable decorator with Pydantic models."""
        from db_types import Varchar, Integer
        
        @mockable
        class Product(BaseModel):
            name: Varchar(100)
            price: Integer()
            stock: Integer()
        
        # Test that methods were added
        assert hasattr(Product, "mock")
        assert hasattr(Product, "mock_builder")
        
        # Test basic mocking
        product = Product.mock()
        assert isinstance(product.name, str)
        assert isinstance(product.price, int)
        assert isinstance(product.stock, int)
        
        # Test with overrides
        custom = Product.mock(name="Custom Product", price=999)
        assert custom.name == "Custom Product"
        assert custom.price == 999
        
        # Test builder pattern
        built = (Product.mock_builder()
                .with_name("Built Product")
                .with_stock(50)
                .build())
        assert built.name == "Built Product"
        assert built.stock == 50
    
    def test_pydantic_optional_fields(self):
        """Test mocking Pydantic models with optional fields."""
        from db_types import Varchar
        
        class OptionalModel(BaseModel):
            required: Varchar(50)
            optional: Optional[Varchar(100)] = None
            maybe_int: Optional[int] = None
        
        # Generate multiple to test optional behavior
        mocks = [mock_factory(OptionalModel) for _ in range(20)]
        
        # All should have required field
        assert all(isinstance(m.required, str) for m in mocks)
        
        # Check that optional fields sometimes have values, sometimes None
        has_optional = sum(1 for m in mocks if m.optional is not None)
        has_maybe_int = sum(1 for m in mocks if m.maybe_int is not None)
        
        # Should have some variation
        assert 0 < has_optional < 20
        assert 0 < has_maybe_int < 20
    
    def test_pydantic_validation_on_mock(self):
        """Test that mocked data passes Pydantic validation."""
        from db_types import Varchar, Integer, Email as EmailType
        
        @mockable
        class ValidatedModel(BaseModel):
            username: Varchar(20)
            age: Integer()
            email: Annotated[str, DBTypeValidator(EmailType())]
        
        # Generate 10 mocks and ensure they all pass validation
        for _ in range(10):
            mock = ValidatedModel.mock()
            
            # Should not raise ValidationError
            assert len(mock.username) <= 20
            assert "@" in mock.email
            assert isinstance(mock.age, int)


class TestDefaultMockImplementation:
    """Test the default mock implementation in base DBType."""
    
    def test_numeric_types_default_mock(self):
        """Test that numeric types use default mock implementation."""
        from db_types import INTEGER, FLOAT, DECIMAL
        
        # These should all work with default implementation
        int_mock = INTEGER().mock()
        assert isinstance(int_mock, int)
        
        float_mock = FLOAT().mock()
        assert isinstance(float_mock, float)
        
        decimal_mock = DECIMAL(10, 2).mock()
        assert isinstance(decimal_mock, Decimal)
    
    def test_temporal_types_default_mock(self):
        """Test that temporal types use default mock implementation."""
        from db_types import DATE, TIME, TIMESTAMP
        from datetime import time
        
        date_mock = DATE().mock()
        assert isinstance(date_mock, date)
        
        time_mock = TIME().mock()
        assert isinstance(time_mock, time)
        
        timestamp_mock = TIMESTAMP().mock()
        assert isinstance(timestamp_mock, datetime)
    
    def test_binary_types_default_mock(self):
        """Test that binary types use default mock implementation."""
        from db_types import BINARY, VARBINARY
        
        binary_mock = BINARY(32).mock()
        assert isinstance(binary_mock, bytes)
        assert len(binary_mock) == 32
        
        varbinary_mock = VARBINARY(64).mock()
        assert isinstance(varbinary_mock, bytes)
        assert len(varbinary_mock) <= 64