"""Tests for constrained numeric types."""

import pytest

from db_types.types.constraints import (
    ConstrainedBigInt,
    ConstrainedInteger,
    ConstrainedSmallInt,
    ConstrainedTinyInt,
    NegativeInteger,
    NonNegativeInteger,
    NonPositiveInteger,
    PositiveInteger,
)


class TestConstrainedInteger:
    """Test ConstrainedInteger type."""

    def test_min_max_constraints(self):
        """Test min and max value constraints."""
        constrained = ConstrainedInteger(min_value=10, max_value=100)

        # Valid values
        constrained.validate(10)
        constrained.validate(50)
        constrained.validate(100)

        # Invalid values
        with pytest.raises(ValueError, match="below minimum"):
            constrained.validate(9)

        with pytest.raises(ValueError, match="exceeds maximum"):
            constrained.validate(101)

    def test_multiple_of_constraint(self):
        """Test multiple_of constraint."""
        constrained = ConstrainedInteger(multiple_of=5)

        # Valid values
        constrained.validate(0)
        constrained.validate(5)
        constrained.validate(10)
        constrained.validate(-5)
        constrained.validate(-10)

        # Invalid values
        with pytest.raises(ValueError, match="not a multiple of"):
            constrained.validate(3)

        with pytest.raises(ValueError, match="not a multiple of"):
            constrained.validate(7)

    def test_positive_constraint(self):
        """Test positive constraint."""
        constrained = ConstrainedInteger(positive=True)

        # Valid values
        constrained.validate(1)
        constrained.validate(100)

        # Invalid values
        with pytest.raises(ValueError, match="below minimum"):
            constrained.validate(0)

        with pytest.raises(ValueError, match="below minimum"):
            constrained.validate(-1)

    def test_negative_constraint(self):
        """Test negative constraint."""
        constrained = ConstrainedInteger(negative=True)

        # Valid values
        constrained.validate(-1)
        constrained.validate(-100)

        # Invalid values
        with pytest.raises(ValueError, match="exceeds maximum"):
            constrained.validate(0)

        with pytest.raises(ValueError, match="exceeds maximum"):
            constrained.validate(1)

    def test_combined_constraints(self):
        """Test combining multiple constraints."""
        constrained = ConstrainedInteger(min_value=10, max_value=100, multiple_of=10)

        # Valid values
        constrained.validate(10)
        constrained.validate(20)
        constrained.validate(100)

        # Invalid values
        with pytest.raises(ValueError, match="not a multiple of"):
            constrained.validate(15)

        with pytest.raises(ValueError, match="below minimum"):
            constrained.validate(0)

    def test_invalid_constraint_combinations(self):
        """Test invalid constraint combinations."""
        # positive and negative together
        with pytest.raises(ValueError, match="Cannot be both positive and negative"):
            ConstrainedInteger(positive=True, negative=True)

        # min > max
        with pytest.raises(ValueError, match="cannot be greater than max_value"):
            ConstrainedInteger(min_value=100, max_value=10)

        # negative multiple_of
        with pytest.raises(ValueError, match="must be positive"):
            ConstrainedInteger(multiple_of=-5)

    def test_sql_type_generation(self):
        """Test SQL type with CHECK constraints."""
        # Basic
        basic = ConstrainedInteger()
        assert basic.sql_type == "INTEGER"

        # With min/max
        minmax = ConstrainedInteger(min_value=10, max_value=100)
        assert ">= 10" in minmax.sql_type
        assert "<= 100" in minmax.sql_type

        # With multiple_of
        mult = ConstrainedInteger(multiple_of=5)
        assert "% 5 = 0" in mult.sql_type

    def test_repr(self):
        """Test string representation."""
        basic = ConstrainedInteger()
        assert repr(basic) == "ConstrainedInteger"

        with_constraints = ConstrainedInteger(min_value=10, max_value=100, multiple_of=5)
        repr_str = repr(with_constraints)
        assert "min_value=10" in repr_str
        assert "max_value=100" in repr_str
        assert "multiple_of=5" in repr_str


class TestPositiveInteger:
    """Test PositiveInteger type."""

    def test_positive_only(self):
        """Test that only positive values are accepted."""
        pos_int = PositiveInteger()

        # Valid values
        pos_int.validate(1)
        pos_int.validate(100)
        pos_int.validate(2147483647)  # Max INTEGER

        # Invalid values
        with pytest.raises(ValueError, match="below minimum"):
            pos_int.validate(0)

        with pytest.raises(ValueError, match="below minimum"):
            pos_int.validate(-1)

    def test_with_max_value(self):
        """Test PositiveInteger with max_value."""
        pos_int = PositiveInteger(max_value=50)

        pos_int.validate(1)
        pos_int.validate(50)

        with pytest.raises(ValueError, match="exceeds maximum"):
            pos_int.validate(51)

    def test_with_multiple_of(self):
        """Test PositiveInteger with multiple_of."""
        pos_int = PositiveInteger(multiple_of=3)

        pos_int.validate(3)
        pos_int.validate(6)
        pos_int.validate(9)

        with pytest.raises(ValueError, match="not a multiple of"):
            pos_int.validate(4)


class TestNegativeInteger:
    """Test NegativeInteger type."""

    def test_negative_only(self):
        """Test that only negative values are accepted."""
        neg_int = NegativeInteger()

        # Valid values
        neg_int.validate(-1)
        neg_int.validate(-100)
        neg_int.validate(-2147483648)  # Min INTEGER

        # Invalid values
        with pytest.raises(ValueError, match="exceeds maximum"):
            neg_int.validate(0)

        with pytest.raises(ValueError, match="exceeds maximum"):
            neg_int.validate(1)

    def test_with_min_value(self):
        """Test NegativeInteger with min_value."""
        neg_int = NegativeInteger(min_value=-50)

        neg_int.validate(-1)
        neg_int.validate(-50)

        with pytest.raises(ValueError, match="below minimum"):
            neg_int.validate(-51)


class TestNonNegativeInteger:
    """Test NonNegativeInteger type."""

    def test_non_negative(self):
        """Test that zero and positive values are accepted."""
        non_neg = NonNegativeInteger()

        # Valid values
        non_neg.validate(0)
        non_neg.validate(1)
        non_neg.validate(100)

        # Invalid values
        with pytest.raises(ValueError, match="below minimum"):
            non_neg.validate(-1)


class TestNonPositiveInteger:
    """Test NonPositiveInteger type."""

    def test_non_positive(self):
        """Test that zero and negative values are accepted."""
        non_pos = NonPositiveInteger()

        # Valid values
        non_pos.validate(0)
        non_pos.validate(-1)
        non_pos.validate(-100)

        # Invalid values
        with pytest.raises(ValueError, match="exceeds maximum"):
            non_pos.validate(1)


class TestConstrainedBigInt:
    """Test ConstrainedBigInt type."""

    def test_bigint_range(self):
        """Test that BIGINT range is respected."""
        big = ConstrainedBigInt()

        # Valid BIGINT values
        big.validate(9223372036854775807)  # Max BIGINT
        big.validate(-9223372036854775808)  # Min BIGINT

    def test_constraints_within_bigint_range(self):
        """Test constraints work with large numbers."""
        big = ConstrainedBigInt(
            min_value=1000000000000,  # 1 trillion
            max_value=9000000000000,  # 9 trillion
            multiple_of=1000000000,  # 1 billion
        )

        # Valid values
        big.validate(1000000000000)
        big.validate(2000000000000)

        # Invalid values - not a multiple of 1 billion
        with pytest.raises(ValueError, match="not a multiple of"):
            big.validate(1000000000500)  # 1 trillion + 500


class TestConstrainedSmallInt:
    """Test ConstrainedSmallInt type."""

    def test_smallint_range(self):
        """Test that SMALLINT range is respected."""
        small = ConstrainedSmallInt()

        # Valid SMALLINT values
        small.validate(32767)  # Max SMALLINT
        small.validate(-32768)  # Min SMALLINT

    def test_constraints_within_smallint_range(self):
        """Test constraints work within SMALLINT range."""
        small = ConstrainedSmallInt(min_value=-100, max_value=100, multiple_of=10)

        # Valid values
        small.validate(0)
        small.validate(10)
        small.validate(-10)
        small.validate(100)
        small.validate(-100)

        # Invalid values
        with pytest.raises(ValueError, match="not a multiple of"):
            small.validate(15)

        with pytest.raises(ValueError, match="exceeds maximum"):
            small.validate(110)

    def test_bounds_exceed_smallint(self):
        """Test error when bounds exceed SMALLINT range."""
        # Max value too large
        with pytest.raises(ValueError, match="exceeds SMALLINT maximum"):
            ConstrainedSmallInt(max_value=40000)

        # Min value too small
        with pytest.raises(ValueError, match="below SMALLINT minimum"):
            ConstrainedSmallInt(min_value=-40000)


class TestConstrainedTinyInt:
    """Test ConstrainedTinyInt type."""

    def test_tinyint_range(self):
        """Test that TINYINT range is respected."""
        tiny = ConstrainedTinyInt()

        # Valid TINYINT values
        tiny.validate(127)  # Max TINYINT
        tiny.validate(-128)  # Min TINYINT

    def test_constraints_within_tinyint_range(self):
        """Test constraints work within TINYINT range."""
        tiny = ConstrainedTinyInt(min_value=-10, max_value=10, multiple_of=5)

        # Valid values
        tiny.validate(0)
        tiny.validate(5)
        tiny.validate(-5)
        tiny.validate(10)
        tiny.validate(-10)

        # Invalid values
        with pytest.raises(ValueError, match="not a multiple of"):
            tiny.validate(3)

        with pytest.raises(ValueError, match="exceeds maximum"):
            tiny.validate(15)

    def test_bounds_exceed_tinyint(self):
        """Test error when bounds exceed TINYINT range."""
        # Max value too large
        with pytest.raises(ValueError, match="exceeds TINYINT maximum"):
            ConstrainedTinyInt(max_value=200)

        # Min value too small
        with pytest.raises(ValueError, match="below TINYINT minimum"):
            ConstrainedTinyInt(min_value=-200)

    def test_positive_tinyint(self):
        """Test positive TINYINT values."""
        tiny = ConstrainedTinyInt(positive=True)
        assert tiny.min_value == 1
        assert tiny.max_value == 127

        tiny.validate(1)
        tiny.validate(100)

        with pytest.raises(ValueError, match="below minimum"):
            tiny.validate(0)

    def test_negative_tinyint(self):
        """Test negative TINYINT values."""
        tiny = ConstrainedTinyInt(negative=True)
        assert tiny.min_value == -128
        assert tiny.max_value == -1

        tiny.validate(-1)
        tiny.validate(-100)

        with pytest.raises(ValueError, match="exceeds maximum"):
            tiny.validate(0)
