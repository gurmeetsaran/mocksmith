"""Tests for the clean annotations API."""

from dataclasses import dataclass
from typing import get_args, get_origin

import pytest

from db_types import BigInt, Integer, PositiveInteger, SmallInt
from db_types.dataclass_integration import validate_dataclass
from db_types.types.constraints import ConstrainedInteger
from db_types.types.constraints import PositiveInteger as _PositiveInteger
from db_types.types.numeric import INTEGER


def get_db_type_from_annotation(annotation):
    """Extract the database type instance from an annotation."""
    args = get_args(annotation)
    if args:
        # Find the db_type in the annotation args
        for arg in args[1:]:  # Skip first arg (the type itself)
            # Direct db_type
            if hasattr(arg, "sql_type"):
                return arg
            # DBTypeValidator that wraps db_type (when Pydantic is available)
            if hasattr(arg, "db_type"):
                return arg.db_type
    return None


class TestAnnotationsAPI:
    """Test the clean annotations API."""

    def test_integer_without_constraints(self):
        """Test Integer() returns standard INTEGER type."""
        annotation = Integer()

        # Check it's an Annotated type
        assert get_origin(annotation) is not None

        # Get the db_type
        db_type = get_db_type_from_annotation(annotation)

        assert db_type is not None
        assert isinstance(db_type, INTEGER)
        assert not isinstance(db_type, ConstrainedInteger)

    def test_integer_with_constraints(self):
        """Test Integer with constraints returns ConstrainedInteger."""
        annotation = Integer(min_value=0, max_value=100)

        # Get the db_type
        db_type = get_db_type_from_annotation(annotation)

        assert db_type is not None
        assert isinstance(db_type, ConstrainedInteger)
        assert db_type.min_value == 0
        assert db_type.max_value == 100

    def test_integer_positive_shortcut(self):
        """Test Integer(positive=True) works correctly."""
        annotation = Integer(positive=True)

        # Get the db_type
        db_type = get_db_type_from_annotation(annotation)

        assert db_type is not None
        assert db_type.min_value == 1

    def test_positive_integer_helper(self):
        """Test PositiveInteger() helper function."""
        annotation = PositiveInteger()

        # Get the db_type
        db_type = get_db_type_from_annotation(annotation)

        assert db_type is not None
        assert isinstance(db_type, _PositiveInteger)

    def test_integration_with_dataclass(self):
        """Test annotations work with dataclasses."""

        @validate_dataclass
        @dataclass
        class TestModel:
            regular_int: Integer()
            positive_int: Integer(positive=True)
            bounded_int: Integer(min_value=0, max_value=100)
            multiple_int: Integer(multiple_of=5)

        # Valid instance
        model = TestModel(regular_int=42, positive_int=1, bounded_int=50, multiple_int=15)

        assert model.regular_int == 42
        assert model.positive_int == 1
        assert model.bounded_int == 50
        assert model.multiple_int == 15

        # Test validation
        with pytest.raises(ValueError, match="below minimum"):
            TestModel(
                regular_int=42, positive_int=0, bounded_int=50, multiple_int=15  # Should fail
            )

        with pytest.raises(ValueError, match="exceeds maximum"):
            TestModel(
                regular_int=42, positive_int=1, bounded_int=101, multiple_int=15  # Should fail
            )

        with pytest.raises(ValueError, match="not a multiple"):
            TestModel(
                regular_int=42, positive_int=1, bounded_int=50, multiple_int=13  # Should fail
            )

    def test_bigint_and_smallint_support_constraints(self):
        """Test BigInt and SmallInt also support constraints."""

        @validate_dataclass
        @dataclass
        class TestSizes:
            big: BigInt(positive=True)
            small: SmallInt(min_value=0, max_value=100)

        model = TestSizes(big=123456789, small=50)
        assert model.big == 123456789
        assert model.small == 50

        # Test BigInt constraint
        with pytest.raises(ValueError, match="below minimum"):
            TestSizes(big=0, small=50)

        # Test SmallInt constraint
        with pytest.raises(ValueError, match="exceeds maximum"):
            TestSizes(big=1, small=101)
