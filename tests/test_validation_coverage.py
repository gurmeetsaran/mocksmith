"""Additional tests to improve validation coverage."""

from decimal import Decimal

import pytest

from mocksmith.types.numeric import DECIMAL, FLOAT, INTEGER, REAL
from mocksmith.types.string import TEXT, VARCHAR


class TestValidationCoverage:
    """Tests to improve validation coverage."""

    def test_integer_validation_none(self):
        """Test INTEGER validation with None."""
        int_type = INTEGER()
        # None should be accepted
        int_type.validate(None)

    def test_decimal_validation_none(self):
        """Test DECIMAL validation with None."""
        dec_type = DECIMAL(10, 2)
        # None should be accepted
        dec_type.validate(None)

    def test_float_validation_none(self):
        """Test FLOAT validation with None."""
        float_type = FLOAT()
        # None should be accepted
        float_type.validate(None)

    def test_real_precision_limits(self):
        """Test REAL precision limit validation."""
        real_type = REAL()

        # Valid values within REAL range
        real_type.validate(3.4e38)
        real_type.validate(-3.4e38)
        real_type.validate(1.2e-38)
        real_type.validate(0.0)

        # Values outside REAL range should fail
        with pytest.raises(ValueError, match="exceeds REAL precision"):
            real_type.validate(3.5e38)

        with pytest.raises(ValueError, match="exceeds REAL precision"):
            real_type.validate(-3.5e38)

        with pytest.raises(ValueError, match="too small for REAL precision"):
            real_type.validate(1e-39)

    def test_string_validation_none(self):
        """Test string types validation with None."""
        varchar = VARCHAR(50)
        varchar.validate(None)

        text = TEXT()
        text.validate(None)

    def test_numeric_serialization(self):
        """Test numeric type serialization."""
        # INTEGER
        int_type = INTEGER()
        assert int_type.serialize(42) == 42
        assert int_type.serialize(None) is None

        # DECIMAL
        dec_type = DECIMAL(10, 2)
        assert dec_type.serialize(Decimal("123.45")) == "123.45"
        assert dec_type.serialize(123.45) == "123.45"
        assert dec_type.serialize(None) is None

        # FLOAT
        float_type = FLOAT()
        assert float_type.serialize(123.45) == 123.45
        assert float_type.serialize(None) is None

    def test_numeric_deserialization(self):
        """Test numeric type deserialization."""
        # INTEGER
        int_type = INTEGER()
        assert int_type.deserialize(42) == 42
        assert int_type.deserialize("42") == 42
        assert int_type.deserialize(None) is None

        # DECIMAL
        dec_type = DECIMAL(10, 2)
        result = dec_type.deserialize("123.45")
        assert isinstance(result, Decimal)
        assert result == Decimal("123.45")
        assert dec_type.deserialize(None) is None

    def test_string_serialization(self):
        """Test string type serialization."""
        # VARCHAR
        varchar = VARCHAR(50)
        assert varchar.serialize("hello") == "hello"
        assert varchar.serialize(None) is None

        # CHAR with padding
        from mocksmith.types.string import CHAR

        char = CHAR(10)
        assert char.serialize("hello") == "hello     "  # Padded to 10
        assert char.serialize(None) is None

        # TEXT
        text = TEXT()
        assert text.serialize("long text") == "long text"
        assert text.serialize(None) is None

    def test_string_deserialization(self):
        """Test string type deserialization."""
        # VARCHAR
        varchar = VARCHAR(50)
        assert varchar.deserialize("hello") == "hello"
        assert varchar.deserialize(None) is None

        # CHAR strips trailing spaces
        from mocksmith.types.string import CHAR

        char = CHAR(10)
        assert char.deserialize("hello     ") == "hello"
        assert char.deserialize(None) is None

        # TEXT
        text = TEXT()
        assert text.deserialize("long text") == "long text"
        assert text.deserialize(None) is None
