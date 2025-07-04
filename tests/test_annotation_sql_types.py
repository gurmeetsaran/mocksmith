"""Tests for SQL type generation through the annotations API."""

from typing import get_args

from mocksmith import (
    BigInt,
    Binary,
    Blob,
    Boolean,
    Char,
    Date,
    DateTime,
    Double,
    Float,
    Integer,
    Money,
    NegativeInteger,
    NonNegativeInteger,
    NonPositiveInteger,
    PositiveInteger,
    SmallInt,
    Text,
    Time,
    Timestamp,
    TinyInt,
    VarBinary,
    Varchar,
)


def get_db_type_from_annotation(annotation):
    """Extract the database type instance from an annotation."""
    args = get_args(annotation)
    if not args:
        raise ValueError(f"Could not extract db_type from annotation: {annotation}")

    # Skip first arg (the type itself)
    for arg in args[1:]:
        # Direct db_type (has sql_type attribute)
        if hasattr(arg, "sql_type"):
            return arg

    # If we didn't find it directly, check for DBTypeValidator wrapper
    for arg in args[1:]:
        # DBTypeValidator wrapper (has db_type attribute)
        if hasattr(arg, "db_type") and hasattr(arg.db_type, "sql_type"):
            return arg.db_type

    raise ValueError(f"Could not extract db_type from annotation: {annotation}")


class TestAnnotationStringSQLTypes:
    """Test SQL types from string annotations."""

    def test_varchar_annotation_sql_type(self):
        """Test Varchar annotation SQL type."""
        annotation = Varchar(50)
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "VARCHAR(50)"

    def test_char_annotation_sql_type(self):
        """Test Char annotation SQL type."""
        annotation = Char(10)
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "CHAR(10)"

    def test_text_annotation_sql_type(self):
        """Test Text annotation SQL type."""
        annotation = Text()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "TEXT"


class TestAnnotationNumericSQLTypes:
    """Test SQL types from numeric annotations."""

    def test_integer_annotation_sql_types(self):
        """Test Integer annotation SQL types."""
        # Standard integer
        annotation = Integer()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "INTEGER"

        # With constraints
        annotation_constrained = Integer(ge=0, le=100)
        db_type_constrained = get_db_type_from_annotation(annotation_constrained)
        assert db_type_constrained.sql_type == "INTEGER"

    def test_bigint_annotation_sql_types(self):
        """Test BigInt annotation SQL types."""
        # Standard
        annotation = BigInt()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "BIGINT"

        # With positive constraint
        annotation_positive = BigInt(gt=0)
        db_type_positive = get_db_type_from_annotation(annotation_positive)
        assert db_type_positive.sql_type == "BIGINT"

    def test_smallint_annotation_sql_types(self):
        """Test SmallInt annotation SQL types."""
        # Standard
        annotation = SmallInt()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "SMALLINT"

        # With multiple_of constraint
        annotation_mult = SmallInt(multiple_of=5)
        db_type_mult = get_db_type_from_annotation(annotation_mult)
        assert db_type_mult.sql_type == "SMALLINT"

    def test_tinyint_annotation_sql_types(self):
        """Test TinyInt annotation SQL types."""
        # Standard
        annotation = TinyInt()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "TINYINT"

        # With constraints
        annotation_range = TinyInt(ge=0, le=100)
        db_type_range = get_db_type_from_annotation(annotation_range)
        assert db_type_range.sql_type == "TINYINT"

    def test_money_annotation_sql_type(self):
        """Test Money annotation SQL type."""
        annotation = Money()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "DECIMAL(19,4)"

    def test_float_annotation_sql_type(self):
        """Test Float annotation SQL type."""
        annotation = Float()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "FLOAT"

        annotation_precision = Float(precision=24)
        db_type_precision = get_db_type_from_annotation(annotation_precision)
        assert db_type_precision.sql_type == "FLOAT(24)"

    def test_double_annotation_sql_type(self):
        """Test Double annotation SQL type."""
        annotation = Double()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "DOUBLE PRECISION"


class TestAnnotationConstraintSQLTypes:
    """Test SQL types from constraint annotations."""

    def test_positive_integer_annotation_sql_type(self):
        """Test PositiveInteger annotation SQL type."""
        annotation = PositiveInteger()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "INTEGER"

    def test_negative_integer_annotation_sql_type(self):
        """Test NegativeInteger annotation SQL type."""
        annotation = NegativeInteger()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "INTEGER"

    def test_non_negative_integer_annotation_sql_type(self):
        """Test NonNegativeInteger annotation SQL type."""
        annotation = NonNegativeInteger()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "INTEGER"

    def test_non_positive_integer_annotation_sql_type(self):
        """Test NonPositiveInteger annotation SQL type."""
        annotation = NonPositiveInteger()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "INTEGER"


class TestAnnotationTemporalSQLTypes:
    """Test SQL types from temporal annotations."""

    def test_date_annotation_sql_type(self):
        """Test Date annotation SQL type."""
        annotation = Date()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "DATE"

    def test_time_annotation_sql_type(self):
        """Test Time annotation SQL type."""
        annotation = Time()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "TIME"

        annotation_precision = Time(precision=3)
        db_type_precision = get_db_type_from_annotation(annotation_precision)
        assert db_type_precision.sql_type == "TIME(3)"

    def test_timestamp_annotation_sql_type(self):
        """Test Timestamp annotation SQL type."""
        annotation = Timestamp()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "TIMESTAMP WITH TIME ZONE"

        annotation_no_tz = Timestamp(with_timezone=False)
        db_type_no_tz = get_db_type_from_annotation(annotation_no_tz)
        assert db_type_no_tz.sql_type == "TIMESTAMP"

    def test_datetime_annotation_sql_type(self):
        """Test DateTime annotation SQL type."""
        # DateTime uses Timestamp internally, so it produces TIMESTAMP SQL
        annotation = DateTime()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "TIMESTAMP"  # DateTime is alias for TIMESTAMP without timezone

        # With precision
        annotation_precision = DateTime(precision=3)
        db_type_precision = get_db_type_from_annotation(annotation_precision)
        assert db_type_precision.sql_type == "TIMESTAMP(3)"


class TestAnnotationBooleanSQLTypes:
    """Test SQL types from boolean annotations."""

    def test_boolean_annotation_sql_type(self):
        """Test Boolean annotation SQL type."""
        annotation = Boolean()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "BOOLEAN"


class TestAnnotationBinarySQLTypes:
    """Test SQL types from binary annotations."""

    def test_binary_annotation_sql_type(self):
        """Test Binary annotation SQL type."""
        annotation = Binary(16)
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "BINARY(16)"

    def test_varbinary_annotation_sql_type(self):
        """Test VarBinary annotation SQL type."""
        annotation = VarBinary(100)
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "VARBINARY(100)"

    def test_blob_annotation_sql_type(self):
        """Test Blob annotation SQL type."""
        annotation = Blob()
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "BLOB"


class TestComplexAnnotationScenarios:
    """Test complex scenarios with annotations."""

    def test_integer_constraint_combinations(self):
        """Test various Integer constraint combinations."""
        test_cases = [
            (Integer(), "INTEGER"),
            (Integer(ge=0), "INTEGER"),
            (Integer(le=100), "INTEGER"),
            (Integer(ge=0, le=100), "INTEGER"),
            (Integer(multiple_of=5), "INTEGER"),
            (Integer(gt=0), "INTEGER"),
            (Integer(lt=0), "INTEGER"),
            (
                Integer(ge=10, le=100, multiple_of=10),
                "INTEGER",
            ),
        ]

        for annotation, expected_sql in test_cases:
            db_type = get_db_type_from_annotation(annotation)
            assert db_type.sql_type == expected_sql

    def test_annotation_preserves_all_options(self):
        """Test that annotations preserve all type options."""
        # Complex timestamp
        annotation = Timestamp(precision=3, with_timezone=False)
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.sql_type == "TIMESTAMP(3)"
        assert db_type.precision == 3
        assert db_type.with_timezone is False

        # Constrained integer with all options
        annotation = Integer(ge=1, le=100, multiple_of=5)
        db_type = get_db_type_from_annotation(annotation)
        assert db_type.ge == 1
        assert db_type.le == 100
        assert db_type.multiple_of == 5
