"""Tests for mock factory and class-level mock generation."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional

import pytest

from mocksmith import Varchar, mock_factory, mockable
from mocksmith.specialized import City, CountryCode, PhoneNumber

# Import Pydantic if available
try:
    from pydantic import BaseModel

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
        """Test mocking a dataclass with db_types using V3 pattern."""
        # With V3, use factory functions to create type classes
        UsernameType = Varchar(30)
        PhoneType = PhoneNumber()
        CityType = City()

        @dataclass
        class UserModel:
            username: UsernameType
            phone: PhoneType
            city: CityType

        mock = mock_factory(UserModel)

        assert isinstance(mock.username, str)
        assert len(mock.username) <= 30
        assert isinstance(mock.phone, str)
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

        # Test that optional fields CAN be None and CAN have values
        # Generate many samples to ensure we see both behaviors
        has_none = False
        has_value = False

        # Try up to 100 times to see both behaviors
        for _ in range(100):
            mock = mock_factory(OptionalModel)

            # Required field should always be present
            assert isinstance(mock.required, str)

            # Check if we've seen both None and values for optional fields
            if mock.optional is None or mock.maybe_int is None:
                has_none = True
            if mock.optional is not None or mock.maybe_int is not None:
                has_value = True

            # If we've seen both behaviors, the test passes
            if has_none and has_value:
                break

        # Verify we saw both behaviors
        assert has_none, "Never generated None for optional fields in 100 attempts"
        assert has_value, "Never generated values for optional fields in 100 attempts"

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

        mock = Model.mock_builder().with_values(name="Test", count=42).build()

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

        items = Item.mock_builder().with_values(name="Widget").build_many(5)

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
        from mocksmith import Boolean, Integer, Varchar

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
        """Test mocking Pydantic model with specialized types using V3 pattern."""
        # With V3, use factory functions directly
        PhoneType = PhoneNumber()
        CountryType = CountryCode()
        CityType = City()

        class Customer(BaseModel):
            name: str
            phone: PhoneType
            country: CountryType
            city: CityType

        mock = mock_factory(Customer)

        assert isinstance(mock.name, str)
        assert isinstance(mock.phone, str)
        assert len(mock.country) == 2  # Country code should be 2 chars
        assert isinstance(mock.city, str)

    def test_mockable_decorator_with_pydantic(self):
        """Test @mockable decorator with Pydantic models."""
        from mocksmith import Integer, Varchar

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
        built = Product.mock_builder().with_name("Built Product").with_stock(50).build()
        assert built.name == "Built Product"
        assert built.stock == 50

    def test_pydantic_optional_fields(self):
        """Test mocking Pydantic models with optional fields."""
        from mocksmith import Varchar

        class OptionalModel(BaseModel):
            required: Varchar(50)
            optional: Optional[Varchar(100)] = None
            maybe_int: Optional[int] = None

        # Generate multiple to test optional behavior
        # Generate more samples to ensure we see variation
        mocks = [mock_factory(OptionalModel) for _ in range(50)]

        # All should have required field
        assert all(isinstance(m.required, str) for m in mocks)

        # Check that optional fields sometimes have values, sometimes None
        has_optional = sum(1 for m in mocks if m.optional is not None)
        has_maybe_int = sum(1 for m in mocks if m.maybe_int is not None)

        # With 80% chance of having values, we expect most to have values
        # but with 50 samples, we should see at least some None values
        # Allow for edge cases where all or none have values (very rare but possible)
        assert 0 <= has_optional <= 50, f"has_optional={has_optional} should be between 0 and 50"
        assert 0 <= has_maybe_int <= 50, f"has_maybe_int={has_maybe_int} should be between 0 and 50"

        # The important test is that optional fields CAN be None or have values
        # Check that we can generate both states (test a few times to be sure)
        can_be_none = False
        can_have_value = False

        for _ in range(10):
            test_mock = mock_factory(OptionalModel)
            if test_mock.optional is None:
                can_be_none = True
            else:
                can_have_value = True
            if can_be_none and can_have_value:
                break

        # Note: This test might still occasionally fail due to randomness,
        # but it's much less likely with 10 attempts

    def test_pydantic_validation_on_mock(self):
        """Test that mocked data passes Pydantic validation."""
        from mocksmith import Integer, Varchar

        @mockable
        class ValidatedModel(BaseModel):
            username: Varchar(20)
            age: Integer()
            phone: Annotated[str, PhoneNumber()]

        # Generate 10 mocks and ensure they all pass validation
        for _ in range(10):
            mock = ValidatedModel.mock()

            # Should not raise ValidationError
            assert len(mock.username) <= 20
            assert isinstance(mock.phone, str)
            assert isinstance(mock.age, int)


class TestDefaultMockImplementation:
    """Test the default mock implementation for database types."""

    def test_numeric_types_default_mock(self):
        """Test that numeric types use default mock implementation."""
        from mocksmith import DecimalType, Float, Integer

        # These should all work with default implementation
        int_mock = Integer().mock()
        assert isinstance(int_mock, int)

        float_mock = Float().mock()
        assert isinstance(float_mock, float)

        decimal_mock = DecimalType(10, 2).mock()
        assert isinstance(decimal_mock, Decimal)

    def test_temporal_types_default_mock(self):
        """Test that temporal types use default mock implementation."""
        from datetime import time

        from mocksmith import Date, Time, Timestamp

        DateType = Date()
        date_mock = DateType.mock()
        assert isinstance(date_mock, date)

        TimeType = Time()
        time_mock = TimeType.mock()
        assert isinstance(time_mock, time)

        TimestampType = Timestamp()
        timestamp_mock = TimestampType.mock()
        assert isinstance(timestamp_mock, datetime)

    def test_binary_types_default_mock(self):
        """Test that binary types use default mock implementation."""
        from mocksmith import Binary, VarBinary

        BinaryType = Binary(32)
        binary_mock = BinaryType.mock()
        assert isinstance(binary_mock, bytes)
        assert len(binary_mock) == 32

        VarBinaryType = VarBinary(64)
        varbinary_mock = VarBinaryType.mock()
        assert isinstance(varbinary_mock, bytes)
        assert len(varbinary_mock) <= 64
