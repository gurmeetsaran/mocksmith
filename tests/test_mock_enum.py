"""Tests for enum support in mock generation."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from mocksmith.mock_factory import mock_factory


class Color(Enum):
    """Example color enum."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Status(Enum):
    """Example status enum with auto values."""

    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()


class Priority(Enum):
    """Example priority enum with integer values."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TestEnumMocking:
    """Test enum mocking functionality."""

    def test_enum_with_dataclass(self):
        """Test that enums work in dataclasses."""

        @dataclass
        class Task:
            title: str
            status: Status
            priority: Priority
            color: Color

        # Generate multiple mocks to ensure randomness
        mocks = [mock_factory(Task) for _ in range(20)]

        # Check all have valid enum values
        for mock in mocks:
            assert isinstance(mock.title, str)
            assert isinstance(mock.status, Status)
            assert isinstance(mock.priority, Priority)
            assert isinstance(mock.color, Color)

        # Check we get different values (statistically should happen)
        statuses = {mock.status for mock in mocks}
        priorities = {mock.priority for mock in mocks}
        colors = {mock.color for mock in mocks}

        # With 20 samples, we should see multiple different values
        assert len(statuses) > 1, "Should generate different status values"
        assert len(priorities) > 1, "Should generate different priority values"
        assert len(colors) > 1, "Should generate different color values"

    def test_optional_enum(self):
        """Test that optional enums work correctly."""

        @dataclass
        class Configuration:
            name: str
            environment: Optional[Color] = None
            level: Optional[Priority] = None

        # Generate multiple to test optional behavior
        has_env_none = False
        has_env_value = False
        has_level_none = False
        has_level_value = False

        for _ in range(50):
            mock = mock_factory(Configuration)
            assert isinstance(mock.name, str)

            if mock.environment is None:
                has_env_none = True
            else:
                assert isinstance(mock.environment, Color)
                has_env_value = True

            if mock.level is None:
                has_level_none = True
            else:
                assert isinstance(mock.level, Priority)
                has_level_value = True

            # Stop early if we've seen both behaviors
            if all([has_env_none, has_env_value, has_level_none, has_level_value]):
                break

        # We should see both None and values for optional enums
        assert has_env_none, "Optional enum should sometimes be None"
        assert has_env_value, "Optional enum should sometimes have value"

    def test_enum_value_distribution(self):
        """Test that enum values are picked with reasonable distribution."""

        @dataclass
        class SingleEnum:
            color: Color

        # Generate many samples
        samples = [mock_factory(SingleEnum).color for _ in range(100)]

        # Count occurrences
        color_counts = {color: samples.count(color) for color in Color}

        # Each color should appear at least once in 100 samples
        for color, count in color_counts.items():
            assert count > 0, f"{color} never appeared in 100 samples"

        # No color should dominate too much (basic randomness check)
        for color, count in color_counts.items():
            assert count < 80, f"{color} appeared {count} times, seems not random"


# Test with Pydantic if available
try:
    from pydantic import BaseModel

    class TestEnumWithPydantic:
        """Test enum support with Pydantic models."""

        def test_pydantic_enum_model(self):
            """Test that enums work in Pydantic models."""

            class Order(BaseModel):
                order_id: str
                status: Status
                priority: Priority
                color: Optional[Color] = None

            # Generate multiple orders
            orders = [mock_factory(Order) for _ in range(10)]

            for order in orders:
                assert isinstance(order.order_id, str)
                assert isinstance(order.status, Status)
                assert isinstance(order.priority, Priority)
                assert order.color is None or isinstance(order.color, Color)

                # Verify Pydantic validation works
                assert order.status in Status
                assert order.priority in Priority
                if order.color is not None:
                    assert order.color in Color

except ImportError:
    # Pydantic not installed, skip these tests
    pass
