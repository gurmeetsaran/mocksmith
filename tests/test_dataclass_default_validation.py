"""Test that default values are properly validated."""

from dataclasses import dataclass, field
from typing import Optional

import pytest

from mocksmith import Integer, SmallInt, TinyInt
from mocksmith.dataclass_integration import validate_dataclass


class TestDefaultValueValidation:
    """Test that default values in dataclasses are validated."""

    def test_invalid_default_caught_at_instantiation(self):
        """Test that invalid default values are caught when creating an instance."""

        # This creates the class successfully
        @validate_dataclass
        @dataclass
        class InvalidConfig:
            hour: SmallInt(ge=0, le=23) = 24

        # But fails when trying to create an instance
        # Accept both Pydantic and custom error messages
        with pytest.raises(
            ValueError, match="(Input should|Value must) be less than or equal to 23"
        ):
            InvalidConfig()

    def test_invalid_default_integer_constraint(self):
        """Test invalid default with Integer constraints."""

        @validate_dataclass
        @dataclass
        class InvalidPercentage:
            percentage: Integer(ge=0, le=100) = 150

        with pytest.raises(
            ValueError, match="(Input should|Value must) be less than or equal to 100"
        ):
            InvalidPercentage()

    def test_invalid_default_below_minimum(self):
        """Test invalid default below minimum."""

        @validate_dataclass
        @dataclass
        class InvalidNegative:
            level: TinyInt(ge=0, le=10) = -1

        with pytest.raises(
            ValueError, match="(Input should|Value must) be greater than or equal to 0"
        ):
            InvalidNegative()

    def test_valid_defaults_work(self):
        """Test that valid defaults work properly."""

        @validate_dataclass
        @dataclass
        class ValidConfig:
            hour: SmallInt(ge=0, le=23) = 12
            percentage: Integer(ge=0, le=100) = 50
            level: TinyInt(ge=0, le=10) = 5

        # Should create without error
        config = ValidConfig()
        assert config.hour == 12
        assert config.percentage == 50
        assert config.level == 5

    def test_overriding_invalid_default_with_valid_value(self):
        """Test that we can override an invalid default with a valid value."""

        @validate_dataclass
        @dataclass
        class InvalidDefaultConfig:
            value: Integer(ge=0, le=10) = 15  # Invalid default

        # Creating without override should fail
        with pytest.raises(ValueError):
            InvalidDefaultConfig()

        # But we can override with a valid value
        config = InvalidDefaultConfig(value=5)
        assert config.value == 5

    def test_default_factory_validation(self):
        """Test that default_factory values are validated."""

        def invalid_factory():
            return 999  # Out of range

        @validate_dataclass
        @dataclass
        class FactoryConfig:
            value: Integer(ge=0, le=100) = field(default_factory=invalid_factory)

        # Should fail when factory produces invalid value
        with pytest.raises(
            ValueError, match="(Input should|Value must) be less than or equal to 100"
        ):
            FactoryConfig()

    def test_none_default_with_nullable(self):
        """Test that None defaults work with Optional types."""

        @validate_dataclass
        @dataclass
        class NullableConfig:
            value: Optional[Integer(ge=0, le=100)] = None

        # Should work fine
        config = NullableConfig()
        assert config.value is None

        # Can set valid value
        config = NullableConfig(value=50)
        assert config.value == 50

        # Invalid value should fail
        with pytest.raises(ValueError):
            NullableConfig(value=150)

    def test_multiple_invalid_defaults(self):
        """Test class with multiple invalid defaults."""

        @validate_dataclass
        @dataclass
        class MultipleInvalid:
            hour: SmallInt(ge=0, le=23) = 25  # Invalid
            minute: SmallInt(ge=0, le=59) = 60  # Invalid

        # Should fail on first invalid default
        with pytest.raises(ValueError):
            MultipleInvalid()

    def test_class_can_be_defined_with_invalid_defaults(self):
        """Test that a class can be defined even with invalid defaults."""

        # This should not raise - the class definition succeeds
        @validate_dataclass
        @dataclass
        class InvalidButDefinable:
            value: Integer(ge=0, le=10) = 100  # Invalid default

        # But instantiation should fail
        with pytest.raises(
            ValueError, match="(Input should|Value must) be less than or equal to 10"
        ):
            InvalidButDefinable()
