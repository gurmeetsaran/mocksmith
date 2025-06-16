"""Tests for SQL type generation across all database types."""

from db_types.types.binary import BINARY, BLOB, VARBINARY
from db_types.types.boolean import BOOLEAN
from db_types.types.constraints import (
    ConstrainedBigInt,
    ConstrainedInteger,
    ConstrainedSmallInt,
    NegativeInteger,
    NonNegativeInteger,
    NonPositiveInteger,
    PositiveInteger,
)
from db_types.types.numeric import BIGINT, DECIMAL, DOUBLE, FLOAT, INTEGER, NUMERIC, REAL, SMALLINT
from db_types.types.string import CHAR, TEXT, VARCHAR
from db_types.types.temporal import DATE, DATETIME, TIME, TIMESTAMP


class TestStringSQLTypes:
    """Test SQL type generation for string types."""

    def test_varchar_sql_type(self):
        """Test VARCHAR SQL type generation."""
        varchar = VARCHAR(50)
        assert varchar.sql_type == "VARCHAR(50)"

        varchar2 = VARCHAR(255)
        assert varchar2.sql_type == "VARCHAR(255)"

    def test_char_sql_type(self):
        """Test CHAR SQL type generation."""
        char = CHAR(10)
        assert char.sql_type == "CHAR(10)"

        char2 = CHAR(5)
        assert char2.sql_type == "CHAR(5)"

    def test_text_sql_type(self):
        """Test TEXT SQL type generation."""
        text = TEXT()
        assert text.sql_type == "TEXT"

        text_with_max = TEXT(max_length=1000)
        assert text_with_max.sql_type == "TEXT"


class TestNumericSQLTypes:
    """Test SQL type generation for numeric types."""

    def test_integer_sql_type(self):
        """Test INTEGER SQL type generation."""
        integer = INTEGER()
        assert integer.sql_type == "INTEGER"

    def test_bigint_sql_type(self):
        """Test BIGINT SQL type generation."""
        bigint = BIGINT()
        assert bigint.sql_type == "BIGINT"

    def test_smallint_sql_type(self):
        """Test SMALLINT SQL type generation."""
        smallint = SMALLINT()
        assert smallint.sql_type == "SMALLINT"

    def test_decimal_sql_type(self):
        """Test DECIMAL SQL type generation."""
        decimal = DECIMAL(10, 2)
        assert decimal.sql_type == "DECIMAL(10,2)"

        decimal2 = DECIMAL(19, 4)
        assert decimal2.sql_type == "DECIMAL(19,4)"

    def test_numeric_sql_type(self):
        """Test NUMERIC SQL type generation."""
        numeric = NUMERIC(10, 2)
        assert numeric.sql_type == "NUMERIC(10,2)"

    def test_float_sql_type(self):
        """Test FLOAT SQL type generation."""
        float_type = FLOAT()
        assert float_type.sql_type == "FLOAT"

        float_with_precision = FLOAT(precision=24)
        assert float_with_precision.sql_type == "FLOAT(24)"

    def test_real_sql_type(self):
        """Test REAL SQL type generation."""
        real = REAL()
        assert real.sql_type == "REAL"

    def test_double_sql_type(self):
        """Test DOUBLE SQL type generation."""
        double = DOUBLE()
        assert double.sql_type == "DOUBLE PRECISION"


class TestTemporalSQLTypes:
    """Test SQL type generation for temporal types."""

    def test_date_sql_type(self):
        """Test DATE SQL type generation."""
        date = DATE()
        assert date.sql_type == "DATE"

    def test_time_sql_type(self):
        """Test TIME SQL type generation."""
        # Default precision 6 is not shown in SQL
        time = TIME()
        assert time.sql_type == "TIME"

        time_no_precision = TIME(precision=0)
        assert time_no_precision.sql_type == "TIME(0)"

        time_precision_3 = TIME(precision=3)
        assert time_precision_3.sql_type == "TIME(3)"

        # Explicit precision 6 also not shown
        time_precision_6 = TIME(precision=6)
        assert time_precision_6.sql_type == "TIME"

    def test_timestamp_sql_type(self):
        """Test TIMESTAMP SQL type generation."""
        # Default: with timezone, precision 6 (not shown)
        timestamp = TIMESTAMP()
        assert timestamp.sql_type == "TIMESTAMP WITH TIME ZONE"

        # Without timezone, precision 6 (not shown)
        timestamp_no_tz = TIMESTAMP(with_timezone=False)
        assert timestamp_no_tz.sql_type == "TIMESTAMP"

        # Different precision
        timestamp_precision_0 = TIMESTAMP(precision=0)
        assert timestamp_precision_0.sql_type == "TIMESTAMP(0) WITH TIME ZONE"

        # Both options
        timestamp_custom = TIMESTAMP(precision=3, with_timezone=False)
        assert timestamp_custom.sql_type == "TIMESTAMP(3)"

    def test_datetime_sql_type(self):
        """Test DATETIME SQL type generation."""
        # DATETIME has its own SQL type representation
        datetime = DATETIME()
        assert datetime.sql_type == "DATETIME"

        datetime_precision_0 = DATETIME(precision=0)
        assert datetime_precision_0.sql_type == "DATETIME(0)"

        datetime_precision_3 = DATETIME(precision=3)
        assert datetime_precision_3.sql_type == "DATETIME(3)"


class TestBooleanSQLTypes:
    """Test SQL type generation for boolean types."""

    def test_boolean_sql_type(self):
        """Test BOOLEAN SQL type generation."""
        boolean = BOOLEAN()
        assert boolean.sql_type == "BOOLEAN"


class TestBinarySQLTypes:
    """Test SQL type generation for binary types."""

    def test_binary_sql_type(self):
        """Test BINARY SQL type generation."""
        binary = BINARY(16)
        assert binary.sql_type == "BINARY(16)"

        binary2 = BINARY(32)
        assert binary2.sql_type == "BINARY(32)"

    def test_varbinary_sql_type(self):
        """Test VARBINARY SQL type generation."""
        varbinary = VARBINARY(100)
        assert varbinary.sql_type == "VARBINARY(100)"

        varbinary2 = VARBINARY(255)
        assert varbinary2.sql_type == "VARBINARY(255)"

    def test_blob_sql_type(self):
        """Test BLOB SQL type generation."""
        blob = BLOB()
        assert blob.sql_type == "BLOB"

        blob_with_max = BLOB(max_length=65536)
        assert blob_with_max.sql_type == "BLOB"


class TestConstrainedSQLTypes:
    """Test SQL type generation for constrained types."""

    def test_constrained_integer_sql_types(self):
        """Test ConstrainedInteger SQL type generation with CHECK constraints."""
        # No constraints
        basic = ConstrainedInteger()
        assert basic.sql_type == "INTEGER"

        # Min constraint only
        min_only = ConstrainedInteger(min_value=0)
        assert min_only.sql_type == "INTEGER CHECK (>= 0)"

        # Max constraint only
        max_only = ConstrainedInteger(max_value=100)
        assert max_only.sql_type == "INTEGER CHECK (<= 100)"

        # Both min and max
        min_max = ConstrainedInteger(min_value=0, max_value=100)
        assert min_max.sql_type == "INTEGER CHECK (>= 0 AND <= 100)"

        # Multiple of constraint
        multiple = ConstrainedInteger(multiple_of=5)
        assert multiple.sql_type == "INTEGER CHECK (% 5 = 0)"

        # All constraints
        all_constraints = ConstrainedInteger(min_value=0, max_value=100, multiple_of=10)
        assert all_constraints.sql_type == "INTEGER CHECK (>= 0 AND <= 100 AND % 10 = 0)"

    def test_positive_integer_sql_type(self):
        """Test PositiveInteger SQL type generation."""
        pos_int = PositiveInteger()
        assert pos_int.sql_type == "INTEGER CHECK (>= 1)"

    def test_negative_integer_sql_type(self):
        """Test NegativeInteger SQL type generation."""
        neg_int = NegativeInteger()
        assert neg_int.sql_type == "INTEGER CHECK (<= -1)"

    def test_non_negative_integer_sql_type(self):
        """Test NonNegativeInteger SQL type generation."""
        non_neg = NonNegativeInteger()
        assert non_neg.sql_type == "INTEGER CHECK (>= 0)"

    def test_non_positive_integer_sql_type(self):
        """Test NonPositiveInteger SQL type generation."""
        non_pos = NonPositiveInteger()
        assert non_pos.sql_type == "INTEGER CHECK (<= 0)"

    def test_constrained_bigint_sql_types(self):
        """Test ConstrainedBigInt SQL type generation."""
        # Basic
        basic = ConstrainedBigInt()
        assert basic.sql_type == "BIGINT"

        # With constraints
        constrained = ConstrainedBigInt(min_value=1000000, max_value=9999999)
        assert constrained.sql_type == "BIGINT CHECK (>= 1000000 AND <= 9999999)"

        # Positive shortcut
        positive = ConstrainedBigInt(positive=True)
        assert positive.sql_type == "BIGINT CHECK (>= 1)"

    def test_constrained_smallint_sql_types(self):
        """Test ConstrainedSmallInt SQL type generation."""
        # Basic
        basic = ConstrainedSmallInt()
        assert basic.sql_type == "SMALLINT"

        # With constraints
        constrained = ConstrainedSmallInt(min_value=-100, max_value=100, multiple_of=10)
        assert constrained.sql_type == "SMALLINT CHECK (>= -100 AND <= 100 AND % 10 = 0)"

        # Negative shortcut
        negative = ConstrainedSmallInt(negative=True)
        assert negative.sql_type == "SMALLINT CHECK (<= -1)"


class TestComplexSQLTypes:
    """Test complex SQL type scenarios."""

    def test_decimal_with_different_scales(self):
        """Test DECIMAL with various precision and scale combinations."""
        test_cases = [
            (DECIMAL(5, 0), "DECIMAL(5,0)"),  # No decimal places
            (DECIMAL(10, 2), "DECIMAL(10,2)"),  # Money-like
            (DECIMAL(19, 4), "DECIMAL(19,4)"),  # High precision money
            (DECIMAL(38, 10), "DECIMAL(38,10)"),  # Very high precision
        ]

        for decimal_type, expected_sql in test_cases:
            assert decimal_type.sql_type == expected_sql

    def test_timestamp_variations(self):
        """Test all TIMESTAMP variations."""
        test_cases = [
            (TIMESTAMP(), "TIMESTAMP WITH TIME ZONE"),
            (TIMESTAMP(precision=0), "TIMESTAMP(0) WITH TIME ZONE"),
            (TIMESTAMP(precision=3), "TIMESTAMP(3) WITH TIME ZONE"),
            # Default precision not shown
            (TIMESTAMP(precision=6), "TIMESTAMP WITH TIME ZONE"),
            (TIMESTAMP(with_timezone=False), "TIMESTAMP"),
            (TIMESTAMP(precision=0, with_timezone=False), "TIMESTAMP(0)"),
            (TIMESTAMP(precision=3, with_timezone=False), "TIMESTAMP(3)"),
            # Default precision not shown
            (TIMESTAMP(precision=6, with_timezone=False), "TIMESTAMP"),
        ]

        for timestamp_type, expected_sql in test_cases:
            assert (
                timestamp_type.sql_type == expected_sql
            ), f"Expected {expected_sql}, got {timestamp_type.sql_type}"

    def test_constrained_integer_edge_cases(self):
        """Test edge cases for constrained integer SQL generation."""
        # Only positive flag
        pos = ConstrainedInteger(positive=True)
        assert pos.sql_type == "INTEGER CHECK (>= 1)"

        # Only negative flag
        neg = ConstrainedInteger(negative=True)
        assert neg.sql_type == "INTEGER CHECK (<= -1)"

        # Multiple of with min/max
        mult_bounded = ConstrainedInteger(min_value=10, max_value=100, multiple_of=5)
        assert mult_bounded.sql_type == "INTEGER CHECK (>= 10 AND <= 100 AND % 5 = 0)"

        # Positive with additional max constraint
        pos_max = ConstrainedInteger(positive=True, max_value=50)
        assert pos_max.sql_type == "INTEGER CHECK (>= 1 AND <= 50)"


class TestSQLTypeInheritance:
    """Test that SQL type generation works correctly with inheritance."""

    def test_numeric_alias_sql_type(self):
        """Test that NUMERIC (alias of DECIMAL) generates correct SQL."""
        numeric = NUMERIC(10, 2)
        decimal = DECIMAL(10, 2)

        assert numeric.sql_type == "NUMERIC(10,2)"
        assert decimal.sql_type == "DECIMAL(10,2)"
        assert numeric.sql_type != decimal.sql_type  # Different SQL despite same behavior

    def test_datetime_alias_sql_type(self):
        """Test that DATETIME generates its own SQL type."""
        datetime = DATETIME()

        # DATETIME has its own representation, different from TIMESTAMP
        assert datetime.sql_type == "DATETIME"

        # Even though internally it extends TIMESTAMP, it has different SQL
        timestamp_no_tz = TIMESTAMP(with_timezone=False)
        assert datetime.sql_type != timestamp_no_tz.sql_type
        assert timestamp_no_tz.sql_type == "TIMESTAMP"
