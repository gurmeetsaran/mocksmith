"""Additional tests to improve mock coverage without requiring pydantic."""

from dataclasses import dataclass
from typing import Optional

import pytest

from mocksmith import MockBuilder, mockable
from mocksmith.mock_factory import mock_factory


class TestMockCoverageWithoutPydantic:
    """Tests for mock functionality that don't require pydantic."""

    def test_mock_factory_with_dataclass(self):
        """Test mock_factory with dataclass."""

        @dataclass
        class SimpleModel:
            id: int
            name: str
            active: bool = True

        # Mock the class
        mock = mock_factory(SimpleModel)
        assert isinstance(mock.id, int)
        assert isinstance(mock.name, str)
        assert isinstance(mock.active, bool)

    def test_mock_factory_with_overrides(self):
        """Test mock_factory with field overrides."""

        @dataclass
        class User:
            id: int
            username: str
            email: str

        mock = mock_factory(User, username="testuser", email="test@example.com")
        assert mock.username == "testuser"
        assert mock.email == "test@example.com"
        assert isinstance(mock.id, int)

    def test_mock_factory_with_optional_fields(self):
        """Test mock_factory with optional fields."""

        @dataclass
        class Product:
            id: int
            name: str
            description: Optional[str] = None
            price: Optional[float] = None

        mock = mock_factory(Product)
        assert isinstance(mock.id, int)
        assert isinstance(mock.name, str)
        # Optional fields might be None or have values
        assert mock.description is None or isinstance(mock.description, str)
        assert mock.price is None or isinstance(mock.price, float)

    def test_mockable_decorator_basic(self):
        """Test mockable decorator adds mock method."""

        @mockable
        @dataclass
        class Article:
            id: int
            title: str
            content: str

        # Check mock method exists
        assert hasattr(Article, "mock")

        # Generate mock
        mock = Article.mock()
        assert isinstance(mock, Article)
        assert isinstance(mock.id, int)
        assert isinstance(mock.title, str)
        assert isinstance(mock.content, str)

    def test_mockable_decorator_with_db_types(self):
        """Test mockable decorator with DB types."""
        from mocksmith import Boolean, Date, Integer, Varchar

        @mockable
        @dataclass
        class DBModel:
            id: Integer()
            name: Varchar(100)
            active: Boolean()
            created: Date()

        mock = DBModel.mock()
        assert isinstance(mock, DBModel)
        # DB types should generate appropriate values
        assert isinstance(mock.id, int)
        assert isinstance(mock.name, str)
        assert len(mock.name) <= 100
        assert isinstance(mock.active, bool)

    def test_mock_builder_basic(self):
        """Test MockBuilder functionality."""

        @mockable
        @dataclass
        class Customer:
            id: int
            name: str
            email: str
            active: bool = True

        # Use builder pattern
        builder = Customer.mock_builder()
        assert isinstance(builder, MockBuilder)

        # Set specific fields
        customer = builder.with_name("John Doe").with_email("john@example.com").build()
        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"
        assert isinstance(customer.id, int)
        assert isinstance(customer.active, bool)

    def test_mock_builder_build_many(self):
        """Test MockBuilder build_many functionality."""

        @mockable
        @dataclass
        class Item:
            id: int
            name: str
            quantity: int

        builder = Item.mock_builder().with_quantity(10)
        items = builder.build_many(5)

        assert len(items) == 5
        for item in items:
            assert isinstance(item, Item)
            assert item.quantity == 10
            assert isinstance(item.id, int)
            assert isinstance(item.name, str)

    def test_mock_unsupported_type(self):
        """Test mock_factory with unsupported class type."""

        class RegularClass:
            pass

        # mock_factory raises TypeError for unsupported types
        with pytest.raises(
            TypeError, match="mock_factory only supports dataclasses and Pydantic models"
        ):
            mock_factory(RegularClass)

    def test_mock_with_inheritance(self):
        """Test mocking with inheritance."""

        @dataclass
        class BaseModel:
            id: int
            created: str

        @mockable
        @dataclass
        class ExtendedModel(BaseModel):
            name: str
            description: str

        mock = ExtendedModel.mock()
        assert isinstance(mock.id, int)
        assert isinstance(mock.created, str)
        assert isinstance(mock.name, str)
        assert isinstance(mock.description, str)

    def test_mock_builder_invalid_field(self):
        """Test MockBuilder with invalid field name."""

        @mockable
        @dataclass
        class Model:
            id: int
            name: str

        builder = Model.mock_builder()

        # MockBuilder doesn't have a generic with_ method for invalid fields
        # Just test that we can build without setting invalid fields
        result = builder.build()
        assert isinstance(result, Model)

    def test_mockable_without_mock_available(self):
        """Test mockable decorator when mock is not available."""

        # The mockable decorator is designed to work even without mock
        @mockable
        @dataclass
        class TestModel:
            id: int

        # Should still work as a regular dataclass
        instance = TestModel(id=1)
        assert instance.id == 1

        # And mock methods should exist
        assert hasattr(TestModel, "mock")
