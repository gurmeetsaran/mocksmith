"""Tests for the clean annotations API."""

from dataclasses import dataclass
from typing import get_args, get_origin

import pytest

from mocksmith import BigInt, Integer, PositiveInteger, SmallInt
from mocksmith.dataclass_integration import validate_dataclass
from mocksmith.types.numeric import INTEGER


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
        # No constraints
        assert db_type.gt is None
        assert db_type.ge is None
        assert db_type.lt is None
        assert db_type.le is None

    def test_integer_with_constraints(self):
        """Test Integer with constraints."""
        annotation = Integer(ge=0, le=100)

        # Get the db_type
        db_type = get_db_type_from_annotation(annotation)

        assert db_type is not None
        assert isinstance(db_type, INTEGER)
        # Check constraints are set correctly
        assert db_type.ge == 0
        assert db_type.le == 100

    def test_integer_positive_shortcut(self):
        """Test positive integer using gt=0."""
        annotation = Integer(gt=0)

        # Get the db_type
        db_type = get_db_type_from_annotation(annotation)

        assert db_type is not None
        assert isinstance(db_type, INTEGER)
        assert db_type.gt == 0  # positive=True sets gt=0

    def test_positive_integer_helper(self):
        """Test PositiveInteger() helper function."""
        annotation = PositiveInteger()

        # Get the db_type
        db_type = get_db_type_from_annotation(annotation)

        assert db_type is not None
        assert isinstance(db_type, INTEGER)
        assert db_type.gt == 0  # PositiveInteger sets gt=0

    def test_integration_with_dataclass(self):
        """Test annotations work with dataclasses."""

        @validate_dataclass
        @dataclass
        class TestModel:
            regular_int: Integer()
            positive_int: Integer(gt=0)
            bounded_int: Integer(ge=0, le=100)
            multiple_int: Integer(multiple_of=5)

        # Valid instance
        model = TestModel(regular_int=42, positive_int=1, bounded_int=50, multiple_int=15)

        assert model.regular_int == 42
        assert model.positive_int == 1
        assert model.bounded_int == 50
        assert model.multiple_int == 15

        # Test validation
        with pytest.raises(ValueError, match="greater than 0"):
            TestModel(
                regular_int=42, positive_int=0, bounded_int=50, multiple_int=15  # Should fail
            )

        with pytest.raises(ValueError, match="less than or equal to 100"):
            TestModel(
                regular_int=42, positive_int=1, bounded_int=101, multiple_int=15  # Should fail
            )

        with pytest.raises(ValueError, match="multiple of 5"):
            TestModel(
                regular_int=42, positive_int=1, bounded_int=50, multiple_int=13  # Should fail
            )

    def test_bigint_and_smallint_support_constraints(self):
        """Test BigInt and SmallInt also support constraints."""

        @validate_dataclass
        @dataclass
        class TestSizes:
            big: BigInt(gt=0)
            small: SmallInt(ge=0, le=100)

        model = TestSizes(big=123456789, small=50)
        assert model.big == 123456789
        assert model.small == 50

        # Test BigInt constraint
        with pytest.raises(ValueError, match="greater than 0"):
            TestSizes(big=0, small=50)

        # Test SmallInt constraint
        with pytest.raises(ValueError, match="less than or equal to 100"):
            TestSizes(big=1, small=101)
