"""Additional tests for base.py to improve coverage."""

from unittest.mock import Mock, patch

import pytest

from mocksmith.types.base import PYDANTIC_AVAILABLE, DBType


class ConcreteDBType(DBType[str]):
    """Concrete implementation for testing."""

    @property
    def sql_type(self) -> str:
        return "TEST_TYPE"

    @property
    def python_type(self) -> type[str]:
        return str

    def _serialize(self, value: str) -> str:
        return value.upper()

    def _deserialize(self, value: str) -> str:
        return value.lower()

    def _validate_custom(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Must be string")
        if len(value) > 10:
            raise ValueError("Too long")


class TestDBTypeBase:
    """Test DBType base class functionality."""

    def test_dbtype_mock_without_faker(self):
        """Test DBType.mock when faker is not available."""
        db_type = ConcreteDBType()

        # Mock the faker import to fail
        with patch.object(db_type, "_generate_mock") as mock_generate:
            mock_generate.side_effect = NotImplementedError(
                "ConcreteDBType does not support mock generation"
            )
            with pytest.raises(NotImplementedError, match="does not support mock generation"):
                db_type.mock()

    def test_dbtype_validate_with_pydantic_type_error(self):
        """Test validate when pydantic type adapter raises error."""
        if not PYDANTIC_AVAILABLE:
            pytest.skip("Pydantic not available")

        db_type = ConcreteDBType()

        # Mock get_pydantic_type to return a type that will fail with ValueError
        mock_pydantic_type = Mock()
        mock_adapter = Mock()
        mock_adapter.validate_python.side_effect = ValueError("Pydantic error")

        with patch("mocksmith.types.base.TypeAdapter", return_value=mock_adapter):
            db_type.get_pydantic_type = Mock(return_value=mock_pydantic_type)

            # Should raise the ValueError from pydantic
            with pytest.raises(ValueError, match="Pydantic error"):
                db_type.validate("test")

    def test_dbtype_validate_none_always_valid(self):
        """Test that None is always valid."""
        db_type = ConcreteDBType()
        # Should not raise
        db_type.validate(None)

    def test_dbtype_repr(self):
        """Test __repr__ method."""
        db_type = ConcreteDBType()
        assert repr(db_type) == "ConcreteDBType()"

    def test_dbtype_serialize_deserialize_none(self):
        """Test serialize/deserialize with None."""
        db_type = ConcreteDBType()
        assert db_type.serialize(None) is None
        assert db_type.deserialize(None) is None

    def test_dbtype_get_pydantic_type_not_implemented(self):
        """Test default get_pydantic_type returns None."""
        db_type = ConcreteDBType()
        assert db_type.get_pydantic_type() is None

    def test_dbtype_sql_type_abstract(self):
        """Test sql_type is abstract."""

        class IncompleteDBType(DBType[str]):
            @property
            def python_type(self) -> type[str]:
                return str

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteDBType()

    def test_dbtype_python_type_abstract(self):
        """Test python_type is abstract."""

        class IncompleteDBType(DBType[str]):
            @property
            def sql_type(self) -> str:
                return "TEST"

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteDBType()


class TestDBTypeValidation:
    """Test validation scenarios."""

    def test_validate_with_validation_error_from_pydantic(self):
        """Test handling of ValidationError from pydantic."""
        if not PYDANTIC_AVAILABLE:
            pytest.skip("Pydantic not available")

        from pydantic import ValidationError

        db_type = ConcreteDBType()

        # Create a mock that raises ValidationError
        mock_adapter = Mock()
        # Create a simple ValidationError
        try:
            # Force a validation error
            from pydantic import BaseModel

            class TestModel(BaseModel):
                value: int

            TestModel(value="not_an_int")
        except ValidationError as e:
            mock_error = e

        mock_adapter.validate_python.side_effect = mock_error

        with patch("mocksmith.types.base.TypeAdapter", return_value=mock_adapter):
            db_type.get_pydantic_type = Mock(return_value="mock_type")

            with pytest.raises(ValueError):
                db_type.validate("test")

    def test_validate_falls_back_to_custom(self):
        """Test validation falls back to custom when pydantic not available."""
        db_type = ConcreteDBType()

        # Mock to ensure pydantic is "not available"
        with patch("mocksmith.types.base.PYDANTIC_AVAILABLE", False):
            # Valid value
            db_type.validate("test")

            # Invalid value
            with pytest.raises(ValueError, match="Too long"):
                db_type.validate("this is way too long")


class TestDBTypeFaker:
    """Test faker integration."""

    def test_generate_mock_not_implemented(self):
        """Test when _generate_mock raises NotImplementedError."""

        class NoMockDBType(DBType[str]):
            @property
            def sql_type(self) -> str:
                return "TEST"

            @property
            def python_type(self) -> type[str]:
                return str

            def _serialize(self, value: str) -> str:
                return value

            def _deserialize(self, value: str) -> str:
                return value

            def _validate_custom(self, value: str) -> None:
                pass

            def _generate_mock(self, fake):
                # Override to raise NotImplementedError
                raise NotImplementedError("No mock implementation")

        db_type = NoMockDBType()

        # The mock() method should work but _generate_mock raises
        with pytest.raises(NotImplementedError):
            db_type.mock()

    def test_dbtype_with_faker(self):
        """Test DBType with faker implementation."""

        class MockableDBType(DBType[str]):
            @property
            def sql_type(self) -> str:
                return "TEST"

            @property
            def python_type(self) -> type[str]:
                return str

            def _serialize(self, value: str) -> str:
                return value

            def _deserialize(self, value: str) -> str:
                return value

            def _validate_custom(self, value: str) -> None:
                pass

            def _generate_mock(self, fake):
                return f"mock_{fake.word()}"

        db_type = MockableDBType()

        # Mock faker
        mock_faker = Mock()
        mock_faker.word.return_value = "test"

        # Just call mock and check result contains "mock_"
        result = db_type.mock()
        assert "mock_" in result
