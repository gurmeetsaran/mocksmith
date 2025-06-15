"""Tests for numeric database types."""

from decimal import Decimal

import pytest

from db_types.types.numeric import BIGINT, DECIMAL, DOUBLE, FLOAT, INTEGER, NUMERIC, REAL, SMALLINT


class TestINTEGER:
    def test_creation(self):
        int_type = INTEGER()
        assert int_type.sql_type == "INTEGER"
        assert int_type.python_type is int

    def test_validation_success(self):
        int_type = INTEGER()
        int_type.validate(0)
        int_type.validate(100)
        int_type.validate(-100)
        int_type.validate(2147483647)  # max value
        int_type.validate(-2147483648)  # min value
        int_type.validate(100.0)  # float with no decimal

    def test_validation_failure(self):
        int_type = INTEGER()

        with pytest.raises(ValueError, match="out of range"):
            int_type.validate(2147483648)  # too large

        with pytest.raises(ValueError, match="out of range"):
            int_type.validate(-2147483649)  # too small

        with pytest.raises(ValueError, match="Expected integer"):
            int_type.validate(10.5)  # non-integer float

        with pytest.raises(ValueError, match="Expected numeric"):
            int_type.validate("not a number")

    def test_serialize(self):
        int_type = INTEGER()
        assert int_type.serialize(100) == 100
        assert int_type.serialize(100.0) == 100
        assert int_type.serialize(None) is None


class TestBIGINT:
    def test_range(self):
        bigint = BIGINT()
        bigint.validate(9223372036854775807)  # max
        bigint.validate(-9223372036854775808)  # min

        with pytest.raises(ValueError, match="out of range"):
            bigint.validate(9223372036854775808)


class TestSMALLINT:
    def test_range(self):
        smallint = SMALLINT()
        smallint.validate(32767)  # max
        smallint.validate(-32768)  # min

        with pytest.raises(ValueError, match="out of range"):
            smallint.validate(32768)


class TestDECIMAL:
    def test_creation(self):
        dec = DECIMAL(10, 2)
        assert dec.precision == 10
        assert dec.scale == 2
        assert dec.sql_type == "DECIMAL(10,2)"
        assert dec.python_type == Decimal

    def test_validation_success(self):
        dec = DECIMAL(5, 2)
        dec.validate("123.45")
        dec.validate(123.45)
        dec.validate(Decimal("123.45"))
        dec.validate(123)  # integer is ok

    def test_validation_precision(self):
        dec = DECIMAL(5, 2)

        with pytest.raises(ValueError, match="exceeds precision"):
            dec.validate("12345.67")  # too many total digits

    def test_validation_scale(self):
        dec = DECIMAL(5, 2)

        with pytest.raises(ValueError, match="decimal places, exceeds scale"):
            dec.validate("12.456")  # too many decimal places

    def test_serialize(self):
        dec = DECIMAL(5, 2)
        assert dec.serialize(123.45) == "123.45"
        assert dec.serialize(Decimal("123.45")) == "123.45"

    def test_deserialize(self):
        dec = DECIMAL(5, 2)
        result = dec.deserialize("123.45")
        assert isinstance(result, Decimal)
        assert result == Decimal("123.45")


class TestNUMERIC:
    def test_alias(self):
        num = NUMERIC(10, 2)
        assert num.sql_type == "NUMERIC(10,2)"
        assert isinstance(num, DECIMAL)


class TestFLOAT:
    def test_creation(self):
        float_type = FLOAT()
        assert float_type.sql_type == "FLOAT"
        assert float_type.python_type is float

    def test_with_precision(self):
        float_type = FLOAT(24)
        assert float_type.sql_type == "FLOAT(24)"

    def test_serialize(self):
        float_type = FLOAT()
        assert float_type.serialize(123.45) == 123.45
        assert float_type.serialize(100) == 100.0


class TestREAL:
    def test_creation(self):
        real = REAL()
        assert real.sql_type == "REAL"
        assert real.python_type is float


class TestDOUBLE:
    def test_creation(self):
        double = DOUBLE()
        assert double.sql_type == "DOUBLE PRECISION"
        assert double.python_type is float
