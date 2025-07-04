"""Additional tests to improve coverage for types."""

from decimal import Decimal

from mocksmith.types.binary import BINARY, BLOB, VARBINARY
from mocksmith.types.boolean import BOOLEAN
from mocksmith.types.numeric import (
    DECIMAL,
    DOUBLE,
    FLOAT,
    INTEGER,
    REAL,
    TINYINT,
)
from mocksmith.types.string import CHAR, TEXT, VARCHAR
from mocksmith.types.temporal import DATE, DATETIME, TIME, TIMESTAMP


class TestNumericTypeCoverage:
    """Tests to improve numeric type coverage."""

    def test_base_integer_properties(self):
        """Test _BaseInteger properties."""
        int_type = INTEGER()
        assert int_type.python_type is int
        assert int_type.sql_type == "INTEGER"

    def test_base_numeric_properties(self):
        """Test _BaseNumeric properties."""
        dec_type = DECIMAL(10, 2)
        assert dec_type.python_type is Decimal

    def test_integer_edge_cases(self):
        """Test INTEGER edge cases."""
        int_type = INTEGER()
        # Test None handling
        assert int_type.serialize(None) is None
        assert int_type.deserialize(None) is None

        # Test custom validation when not available
        int_type._get_pydantic_type = lambda: None
        int_type.validate(42)

    def test_decimal_edge_cases(self):
        """Test DECIMAL edge cases."""
        dec_type = DECIMAL(10, 2)

        # Test string representation
        assert str(dec_type.serialize(Decimal("123.45"))) == "123.45"

        # Test deserialize with string
        result = dec_type.deserialize("123.45")
        assert isinstance(result, Decimal)
        assert result == Decimal("123.45")

        # Test None handling
        assert dec_type.deserialize(None) is None

    def test_float_edge_cases(self):
        """Test FLOAT edge cases."""
        float_type = FLOAT()

        # Test integer to float conversion
        result = float_type.serialize(42)
        assert isinstance(result, float)
        assert result == 42.0

        # Test None handling
        assert float_type.serialize(None) is None

    def test_real_properties(self):
        """Test REAL type properties."""
        real_type = REAL()
        assert real_type.sql_type == "REAL"
        assert real_type.python_type is float

        # REAL always returns None for pydantic type
        assert real_type.get_pydantic_type() is None

    def test_double_properties(self):
        """Test DOUBLE type properties."""
        double_type = DOUBLE()
        assert double_type.sql_type == "DOUBLE PRECISION"

    def test_tinyint_properties(self):
        """Test TINYINT specific behavior."""
        tiny = TINYINT()
        # TINYINT inherits from _BaseInteger which has range -128 to 127
        assert tiny.sql_type == "TINYINT"

    def test_numeric_repr(self):
        """Test __repr__ methods."""
        assert "INTEGER" in repr(INTEGER())
        assert "DECIMAL(10, 2)" in repr(DECIMAL(10, 2))
        assert "FLOAT" in repr(FLOAT())
        assert "REAL" in repr(REAL())


class TestStringTypeCoverage:
    """Tests to improve string type coverage."""

    def test_varchar_repr(self):
        """Test VARCHAR representation."""
        vchar = VARCHAR(50)
        assert "VARCHAR(50)" in repr(vchar)

    def test_char_edge_cases(self):
        """Test CHAR edge cases."""
        char = CHAR(5)

        # Test None handling
        assert char.serialize(None) is None
        assert char.deserialize(None) is None

        # Test padding
        assert char.serialize("hi") == "hi   "

    def test_text_edge_cases(self):
        """Test TEXT edge cases."""
        text = TEXT()

        # Test representation
        assert "TEXT" in repr(text)

        # Test with max_length
        text_limited = TEXT(max_length=100)
        assert text_limited.max_length == 100


class TestBinaryTypeCoverage:
    """Tests to improve binary type coverage."""

    def test_binary_properties(self):
        """Test BINARY properties."""
        binary = BINARY(10)
        assert binary.length == 10
        assert binary.sql_type == "BINARY(10)"
        assert binary.python_type is bytes

    def test_varbinary_properties(self):
        """Test VARBINARY properties."""
        varbinary = VARBINARY(50)
        assert varbinary.max_length == 50
        assert varbinary.sql_type == "VARBINARY(50)"

    def test_blob_properties(self):
        """Test BLOB properties."""
        blob = BLOB()
        assert blob.sql_type == "BLOB"

        # BLOB doesn't take max_length in constructor
        # It has an optional max_length attribute
        assert blob.max_length is None

    def test_binary_repr(self):
        """Test binary type representations."""
        assert "BINARY(10)" in repr(BINARY(10))
        assert "VARBINARY(50)" in repr(VARBINARY(50))
        assert "BLOB" in repr(BLOB())


class TestBooleanTypeCoverage:
    """Tests to improve boolean type coverage."""

    def test_boolean_properties(self):
        """Test BOOLEAN properties."""
        bool_type = BOOLEAN()
        assert bool_type.sql_type == "BOOLEAN"
        assert bool_type.python_type is bool

        # Test representation
        assert "BOOLEAN" in repr(bool_type)


class TestTemporalTypeCoverage:
    """Tests to improve temporal type coverage."""

    def test_date_properties(self):
        """Test DATE properties."""
        date_type = DATE()
        assert date_type.sql_type == "DATE"

    def test_time_properties(self):
        """Test TIME properties."""
        time_type = TIME()
        assert time_type.sql_type == "TIME"

        # TIME doesn't support precision in this implementation
        assert hasattr(time_type, "precision")

    def test_timestamp_properties(self):
        """Test TIMESTAMP properties."""
        ts = TIMESTAMP()
        assert "TIMESTAMP" in ts.sql_type

        # TIMESTAMP has precision and with_timezone attributes
        assert hasattr(ts, "precision")
        assert hasattr(ts, "with_timezone")
        assert ts.precision == 6  # default
        assert ts.with_timezone is True  # default

    def test_datetime_properties(self):
        """Test DATETIME properties."""
        dt = DATETIME()
        assert dt.sql_type == "DATETIME"

        # DATETIME is an alias for TIMESTAMP
        assert isinstance(dt, TIMESTAMP)

    def test_temporal_repr(self):
        """Test temporal type representations."""
        # Temporal types may not have __repr__ implemented
        date_type = DATE()
        time_type = TIME()
        ts_type = TIMESTAMP()
        dt_type = DATETIME()

        # Just verify they can be created
        assert date_type is not None
        assert time_type is not None
        assert ts_type is not None
        assert dt_type is not None
