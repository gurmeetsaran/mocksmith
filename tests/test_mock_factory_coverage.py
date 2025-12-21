"""Additional tests for mock_factory to improve coverage without pydantic."""

import warnings
from dataclasses import dataclass
from typing import Optional

from mocksmith import Integer, Varchar
from mocksmith.mock_factory import _handle_unsupported_type, mock_factory


class TestMockFactoryInternals:
    """Test internal functions of mock_factory."""

    def test_handle_unsupported_type_with_warning(self):
        """Test _handle_unsupported_type issues warning."""

        class CustomType:
            """A custom type that can't be mocked."""

            def __init__(self, required_arg):
                # This will fail all instantiation attempts
                if required_arg is None or required_arg == "" or required_arg == 0:
                    raise ValueError("Cannot instantiate with default values")
                self.value = required_arg

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = _handle_unsupported_type(CustomType, "test_field")

            # Should return None
            assert result is None

            # Should issue a warning
            assert len(w) == 1
            assert "Unsupported type" in str(w[0].message)
            assert "CustomType" in str(w[0].message)
            assert "test_field" in str(w[0].message)

    def test_handle_unsupported_type_path_handling(self):
        """Test _handle_unsupported_type with Path-like types."""

        # Mock a Path-like class
        class MockPath:
            __name__ = "Path"

        # Test with "dir" in field name
        result = _handle_unsupported_type(MockPath, "config_dir")
        # Should create a path-like result
        assert result is not None
        assert "mock_directory" in str(result) or "mock_path" in str(result)

        # Test with "file" in field name
        result = _handle_unsupported_type(MockPath, "log_file")
        assert result is not None
        assert "mock_file" in str(result) or "mock_path" in str(result)

    def test_handle_unsupported_type_no_pathlib(self):
        """Test _handle_unsupported_type when pathlib import fails."""

        class MockPath:
            __name__ = "Path"

        # Can't easily test ImportError case since pathlib is builtin
        # Just test that it handles Path types
        result = _handle_unsupported_type(MockPath, "test_path")
        assert result is not None

    def test_handle_unsupported_type_instantiation_attempts(self):
        """Test _handle_unsupported_type tries various instantiation methods."""

        class TypeWithNoArgs:
            def __init__(self):
                self.value = "no_args"

        class TypeWithNone:
            def __init__(self, val):
                if val is None:
                    self.value = "none"
                else:
                    raise ValueError("Must be None")

        class TypeWithEmptyString:
            def __init__(self, val):
                if val == "":
                    self.value = "empty"
                else:
                    raise ValueError("Must be empty string")

        class TypeWithZero:
            def __init__(self, val):
                if val == 0:
                    self.value = "zero"
                else:
                    raise ValueError("Must be zero")

        # Test type that works with no args
        result = _handle_unsupported_type(TypeWithNoArgs, "field1")
        assert result.value == "no_args"

        # Test type that works with None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = _handle_unsupported_type(TypeWithNone, "field2")
            assert result.value == "none"

        # Test type that works with empty string
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = _handle_unsupported_type(TypeWithEmptyString, "field3")
            assert result.value == "empty"

        # Test type that works with zero
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = _handle_unsupported_type(TypeWithZero, "field4")
            assert result.value == "zero"

    def test_mock_dataclass_with_missing_default(self):
        """Test mocking dataclass with fields that have MISSING default."""

        @dataclass
        class ModelWithDefaults:
            required: int
            optional: Optional[str] = None

        mock = mock_factory(ModelWithDefaults)
        assert isinstance(mock.required, int)
        # Optional field might be None
        assert mock.optional is None or isinstance(mock.optional, str)


class TestMockFactoryEdgeCases:
    """Test edge cases in mock factory."""

    def test_mock_factory_with_annotated_db_type(self):
        """Test mock_factory with Annotated types containing database types."""

        # V3 types work differently - Integer() returns a class for type annotation
        @dataclass
        class AnnotatedModel:
            id: Integer()
            name: Varchar(50)

        mock = mock_factory(AnnotatedModel)
        assert isinstance(mock.id, int)
        assert isinstance(mock.name, str)
        assert len(mock.name) <= 50

    def test_mock_factory_field_with_none_mock(self):
        """Test when a mock provider returns None."""

        class NullMockProvider:
            """A mock provider that always returns None for mock."""

            def mock(self):
                return None

        from typing import Annotated

        @dataclass
        class ModelWithNullType:
            nullable: Annotated[Optional[str], NullMockProvider()]

        # Should handle None gracefully
        mock = mock_factory(ModelWithNullType)
        assert mock.nullable is None
