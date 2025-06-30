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
            hour: SmallInt(min_value=0, max_value=23) = 24

        # But fails when trying to create an instance
        with pytest.raises(ValueError, match="Input should be less than or equal to 23"):
            InvalidConfig()

    def test_invalid_default_integer_constraint(self):
        """Test invalid default with Integer constraints."""

        @validate_dataclass
        @dataclass
        class InvalidPercentage:
            percentage: Integer(min_value=0, max_value=100) = 150

        with pytest.raises(ValueError, match="Input should be less than or equal to 100"):
            InvalidPercentage()

    def test_invalid_default_below_minimum(self):
        """Test invalid default below minimum."""

        @validate_dataclass
        @dataclass
        class InvalidNegative:
            level: TinyInt(min_value=0, max_value=10) = -1

        with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
            InvalidNegative()

    def test_valid_defaults_work(self):
        """Test that valid defaults work correctly."""

        @validate_dataclass
        @dataclass
        class ValidConfig:
            hour: SmallInt(min_value=0, max_value=23) = 12
            percentage: Integer(min_value=0, max_value=100) = 75
            level: TinyInt(min_value=0, max_value=5) = 3

        # Should create instance successfully
        config = ValidConfig()
        assert config.hour == 12
        assert config.percentage == 75
        assert config.level == 3

    def test_overriding_invalid_default_with_valid_value(self):
        """Test that we can override an invalid default with a valid value."""

        @validate_dataclass
        @dataclass
        class ConfigWithBadDefault:
            hour: SmallInt(min_value=0, max_value=23) = 24

        # Can't create with default
        with pytest.raises(ValueError):
            ConfigWithBadDefault()

        # But can create with valid override
        config = ConfigWithBadDefault(hour=12)
        assert config.hour == 12

    def test_default_factory_validation(self):
        """Test that default_factory values are validated when created."""

        def invalid_factory():
            return 150  # Invalid for 0-100 range

        @validate_dataclass
        @dataclass
        class ConfigWithFactory:
            # This will be validated when the factory is called
            value: Integer(min_value=0, max_value=100) = field(default_factory=invalid_factory)

        with pytest.raises(ValueError, match="Input should be less than or equal to 100"):
            ConfigWithFactory()

    def test_none_default_with_nullable(self):
        """Test that None defaults work with nullable fields."""

        @validate_dataclass
        @dataclass
        class NullableConfig:
            optional_hour: Optional[SmallInt(min_value=0, max_value=23)] = None

        config = NullableConfig()
        assert config.optional_hour is None

    def test_multiple_invalid_defaults(self):
        """Test multiple fields with invalid defaults."""

        @validate_dataclass
        @dataclass
        class MultipleInvalid:
            hour: SmallInt(min_value=0, max_value=23) = 24
            percentage: Integer(min_value=0, max_value=100) = 150
            level: TinyInt(min_value=1, max_value=5) = 0

        # Should fail on the first invalid field during instantiation
        with pytest.raises(ValueError):
            MultipleInvalid()

    def test_class_can_be_defined_with_invalid_defaults(self):
        """Demonstrate that class definition succeeds even with invalid defaults."""

        # This succeeds - the class is created
        @validate_dataclass
        @dataclass
        class BadDefaultsClass:
            value: Integer(min_value=0, max_value=10) = 100

        # We can even inspect the class
        assert BadDefaultsClass.__name__ == "BadDefaultsClass"
        assert hasattr(BadDefaultsClass, "__dataclass_fields__")

        # But instantiation fails
        with pytest.raises(ValueError, match="Input should be less than or equal to 10"):
            BadDefaultsClass()
