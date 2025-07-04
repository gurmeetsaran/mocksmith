"""Additional tests for annotations.py to improve coverage."""

from mocksmith.annotations import (
    BigInt,
    Char,
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedMoney,
    Date,
    DateTime,
    DecimalType,
    Double,
    Float,
    Integer,
    Money,
    NegativeInteger,
    NonNegativeInteger,
    NonNegativeMoney,
    NonPositiveInteger,
    Numeric,
    PositiveInteger,
    PositiveMoney,
    SmallInt,
    Text,
    Time,
    Timestamp,
    TinyInt,
    Varchar,
)


class TestAnnotationFunctions:
    """Test annotation functions can be called."""

    def test_integer_annotations(self):
        """Test integer annotation functions."""
        # Basic integer types
        assert Integer() is not None
        assert Integer(gt=0, le=100) is not None
        assert BigInt() is not None
        assert SmallInt() is not None
        assert TinyInt() is not None

        # Constrained integer shortcuts
        assert PositiveInteger() is not None
        assert NegativeInteger() is not None
        assert NonNegativeInteger() is not None
        assert NonPositiveInteger() is not None

    def test_decimal_annotations(self):
        """Test decimal annotation functions."""
        assert DecimalType(10, 2) is not None
        assert DecimalType(10, 2, gt=0) is not None
        assert Numeric(10, 2) is not None
        assert ConstrainedDecimal(10, 2, gt=0, le=9999.99) is not None

    def test_money_annotations(self):
        """Test money annotation functions."""
        assert Money() is not None
        assert ConstrainedMoney(gt=0, le=1000000) is not None
        assert PositiveMoney() is not None
        assert NonNegativeMoney() is not None

    def test_float_annotations(self):
        """Test float annotation functions."""
        assert Float() is not None
        assert Float(precision=24) is not None
        assert Float(gt=0.0, lt=100.0) is not None
        assert ConstrainedFloat(gt=0.0, lt=100.0) is not None
        assert Double() is not None

    def test_string_annotations(self):
        """Test string annotation functions."""
        assert Varchar(50) is not None
        assert Varchar(50, min_length=5) is not None
        assert Varchar(50, startswith="PRE-") is not None
        assert Char(10) is not None
        assert Text() is not None
        assert Text(max_length=1000) is not None

    def test_temporal_annotations(self):
        """Test temporal annotation functions."""
        assert Date() is not None
        assert Time() is not None
        assert Time(precision=3) is not None
        assert Timestamp() is not None
        assert Timestamp(precision=6, with_timezone=False) is not None
        assert DateTime() is not None
        assert DateTime(precision=0) is not None

    def test_annotation_with_complex_constraints(self):
        """Test annotations with multiple constraints."""
        # String with multiple constraints
        varchar_complex = Varchar(
            50,
            min_length=5,
            startswith="PRE-",
            endswith="-SUF",
            strip_whitespace=True,
            to_lower=True,
        )
        assert varchar_complex is not None

        # Decimal with constraints
        decimal_complex = ConstrainedDecimal(10, 2, gt=0, le=9999.99)
        assert decimal_complex is not None
