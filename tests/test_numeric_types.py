"""Tests for numeric database types V3 implementation."""

from decimal import Decimal

import pytest

from mocksmith.types.numeric import _BIGINT as BIGINT
from mocksmith.types.numeric import _DECIMAL as DECIMAL
from mocksmith.types.numeric import _DOUBLE as DOUBLE
from mocksmith.types.numeric import _FLOAT as FLOAT
from mocksmith.types.numeric import _INTEGER as INTEGER
from mocksmith.types.numeric import _NUMERIC as NUMERIC
from mocksmith.types.numeric import _REAL as REAL
from mocksmith.types.numeric import _SMALLINT as SMALLINT
from mocksmith.types.numeric import _TINYINT as TINYINT
from mocksmith.types.numeric import (
    DecimalType,
    Float,
    Integer,
    Money,
    NonNegativeInteger,
    NonNegativeMoney,
    PositiveInteger,
    PositiveMoney,
    TinyInt,
)


class TestINTEGER:
    def test_creation(self):
        # INTEGER is a class that extends int
        value = INTEGER(42)
        assert value == 42
        assert isinstance(value, int)
        assert value.sql_type == "INTEGER"

    def test_factory_function(self):
        # Integer() returns a class for use as type annotation
        IntType = Integer()
        assert IntType == INTEGER
        assert IntType.SQL_TYPE == "INTEGER"
        assert IntType.SQL_MIN == -2147483648
        assert IntType.SQL_MAX == 2147483647

    def test_factory_with_constraints(self):
        # Integer with constraints returns a different class
        PositiveInt = Integer(gt=0)
        assert PositiveInt != INTEGER
        assert PositiveInt._gt == 0

        ConstrainedInt = Integer(ge=10, le=100, multiple_of=5)
        assert ConstrainedInt._ge == 10
        assert ConstrainedInt._le == 100
        assert ConstrainedInt._multiple_of == 5

    def test_validation_success(self):
        # Creating instances validates the value
        assert INTEGER(0) == 0
        assert INTEGER(100) == 100
        assert INTEGER(-100) == -100
        assert INTEGER(2147483647) == 2147483647  # max value
        assert INTEGER(-2147483648) == -2147483648  # min value
        assert INTEGER(100.0) == 100  # float with no decimal

    def test_validation_with_constraints(self):
        # Test gt constraint
        PositiveInt = Integer(gt=0)
        assert PositiveInt(1) == 1
        assert PositiveInt(100) == 100

        with pytest.raises(ValueError, match="greater than 0"):
            PositiveInt(0)
        with pytest.raises(ValueError, match="greater than 0"):
            PositiveInt(-1)

        # Test ge constraint
        NonNegInt = Integer(ge=0)
        assert NonNegInt(0) == 0
        assert NonNegInt(100) == 100

        with pytest.raises(ValueError, match="greater than or equal to 0"):
            NonNegInt(-1)

        # Test lt constraint
        SmallInt = Integer(lt=100)
        assert SmallInt(99) == 99
        assert SmallInt(0) == 0

        with pytest.raises(ValueError, match="less than 100"):
            SmallInt(100)

        # Test le constraint
        MaxInt = Integer(le=100)
        assert MaxInt(100) == 100
        assert MaxInt(0) == 0

        with pytest.raises(ValueError, match="less than or equal to 100"):
            MaxInt(101)

        # Test multiple_of constraint
        EvenInt = Integer(multiple_of=2)
        assert EvenInt(2) == 2
        assert EvenInt(100) == 100

        with pytest.raises(ValueError, match="multiple of 2"):
            EvenInt(3)

    def test_validation_failure(self):
        # Out of range
        with pytest.raises(ValueError, match="out of INTEGER range"):
            INTEGER(2147483648)  # max + 1
        with pytest.raises(ValueError, match="out of INTEGER range"):
            INTEGER(-2147483649)  # min - 1

        # Invalid types
        with pytest.raises(ValueError):
            INTEGER("not a number")
        with pytest.raises(ValueError):
            INTEGER([1, 2, 3])
        with pytest.raises(ValueError):
            INTEGER(None)

    def test_serialize(self):
        value = INTEGER(100)
        assert value.serialize() == 100
        assert int(value) == 100


class TestBIGINT:
    def test_range(self):
        # Test BIGINT specific range
        value = BIGINT(9223372036854775807)  # max
        assert value == 9223372036854775807

        value = BIGINT(-9223372036854775808)  # min
        assert value == -9223372036854775808

        with pytest.raises(ValueError):
            BIGINT(9223372036854775808)  # overflow


class TestSMALLINT:
    def test_range(self):
        # Test SMALLINT specific range
        value = SMALLINT(32767)  # max
        assert value == 32767

        value = SMALLINT(-32768)  # min
        assert value == -32768

        with pytest.raises(ValueError, match="out of SMALLINT range"):
            SMALLINT(32768)  # overflow


class TestTINYINT:
    def test_range(self):
        # Test TINYINT specific range
        value = TINYINT(127)  # max
        assert value == 127

        value = TINYINT(-128)  # min
        assert value == -128

        with pytest.raises(ValueError, match="out of TINYINT range"):
            TINYINT(128)  # overflow

    def test_sql_type(self):
        value = TINYINT(10)
        assert value.sql_type == "TINYINT"

    def test_python_type(self):
        value = TINYINT(10)
        assert isinstance(value, int)

    def test_float_conversion(self):
        # Should accept floats that are whole numbers
        value = TINYINT(10.0)
        assert value == 10

        with pytest.raises(ValueError, match="requires integer value"):
            TINYINT(10.5)

    def test_serialization(self):
        value = TINYINT(10)
        assert value.serialize() == 10

    def test_deserialization(self):
        # The class itself acts as deserializer
        value = TINYINT("10")
        assert value == 10
        assert isinstance(value, int)


class TestDECIMAL:
    def test_creation(self):
        value = DECIMAL("123.45")
        assert value == Decimal("123.45")
        assert isinstance(value, Decimal)

    def test_factory_function(self):
        # DecimalType returns a class with specific precision/scale
        Money = DecimalType(10, 2)
        assert Money._precision == 10
        assert Money._scale == 2

    def test_creation_with_constraints(self):
        PositiveMoney = DecimalType(10, 2, gt=0)
        assert PositiveMoney._gt == Decimal("0")

        BoundedMoney = DecimalType(10, 2, ge=10, le=1000)
        assert BoundedMoney._ge == Decimal("10")
        assert BoundedMoney._le == Decimal("1000")

    def test_validation_success(self):
        MoneyType = DecimalType(10, 2)

        value = MoneyType("123.45")
        assert value == Decimal("123.45")

        value = MoneyType(100)
        assert value == Decimal("100")

        value = MoneyType(0.5)
        assert value == Decimal("0.5")

    def test_validation_with_constraints(self):
        PositiveMoney = DecimalType(10, 2, gt=0)

        value = PositiveMoney("10.50")
        assert value == Decimal("10.50")

        with pytest.raises(ValueError, match="greater than 0"):
            PositiveMoney("0")

        with pytest.raises(ValueError, match="greater than 0"):
            PositiveMoney("-10")

    def test_validation_precision(self):
        SmallDecimal = DecimalType(5, 2)  # max 999.99

        value = SmallDecimal("999.99")
        assert value == Decimal("999.99")

        with pytest.raises(ValueError, match="Too many integer digits"):
            SmallDecimal("1000.00")  # too many integer digits

    def test_validation_scale(self):
        TwoDecimals = DecimalType(10, 2)

        # Should round to 2 decimal places
        value = TwoDecimals("123.456")
        assert value == Decimal("123.46")  # rounded

        value = TwoDecimals("123.45")
        assert value == Decimal("123.45")

    def test_serialize(self):
        value = DECIMAL("123.45")
        assert value.serialize() == Decimal("123.45")

    def test_deserialize(self):
        value = DECIMAL("123.45")
        assert value == Decimal("123.45")


class TestNUMERIC:
    def test_alias(self):
        # NUMERIC is an alias for DECIMAL
        value = NUMERIC("123.45")
        assert isinstance(value, DECIMAL)
        assert value == Decimal("123.45")


class TestFLOAT:
    def test_creation(self):
        value = FLOAT(123.45)
        assert value == 123.45
        assert isinstance(value, float)

    def test_factory_function(self):
        FloatType = Float()
        assert FloatType == FLOAT

        PositiveFloat = Float(gt=0)
        assert PositiveFloat != FLOAT
        assert PositiveFloat._gt == 0

    def test_with_precision(self):
        # FLOAT doesn't have precision parameter in V3
        # It uses constraints instead
        BoundedFloat = Float(ge=-100.0, le=100.0)
        value = BoundedFloat(50.5)
        assert value == 50.5

    def test_creation_with_constraints(self):
        PositiveFloat = Float(gt=0)
        value = PositiveFloat(10.5)
        assert value == 10.5

        with pytest.raises(ValueError, match="greater than 0"):
            PositiveFloat(0)

        with pytest.raises(ValueError, match="greater than 0"):
            PositiveFloat(-10.5)

    def test_validation_with_constraints(self):
        BoundedFloat = Float(ge=-100, le=100)

        assert BoundedFloat(0) == 0
        assert BoundedFloat(100) == 100
        assert BoundedFloat(-100) == -100

        with pytest.raises(ValueError):
            BoundedFloat(101)
        with pytest.raises(ValueError):
            BoundedFloat(-101)

    def test_serialize(self):
        value = FLOAT(123.45)
        assert value == 123.45
        assert float(value) == 123.45


class TestREAL:
    def test_creation(self):
        value = REAL(123.45)
        assert value == 123.45
        assert isinstance(value, float)
        assert value.sql_type == "REAL"


class TestDOUBLE:
    def test_creation(self):
        value = DOUBLE(123.45)
        assert value == 123.45
        assert isinstance(value, float)
        assert value.sql_type == "DOUBLE"


class TestSpecializedTypes:
    def test_positive_integer(self):
        PosInt = PositiveInteger()
        value = PosInt(10)
        assert value == 10

        with pytest.raises(ValueError, match="greater than 0"):
            PosInt(0)

    def test_non_negative_integer(self):
        NonNegInt = NonNegativeInteger()
        value = NonNegInt(0)
        assert value == 0

        value = NonNegInt(10)
        assert value == 10

        with pytest.raises(ValueError, match="greater than or equal to 0"):
            NonNegInt(-1)

    def test_money_types(self):
        # Money type has 19,4 precision/scale
        MoneyType = Money()
        value = MoneyType("12345.6789")
        assert value == Decimal("12345.6789")

        # PositiveMoney must be > 0
        PosMoney = PositiveMoney()
        value = PosMoney("100.50")
        assert value == Decimal("100.50")

        with pytest.raises(ValueError, match="greater than 0"):
            PosMoney("0")

        # NonNegativeMoney must be >= 0
        NonNegMoney = NonNegativeMoney()
        value = NonNegMoney("0")
        assert value == Decimal("0")

        with pytest.raises(ValueError, match="greater than or equal to 0"):
            NonNegMoney("-10")


class TestMockGeneration:
    def test_integer_mock(self):
        IntType = Integer()
        value = IntType.mock()
        assert isinstance(value, int)
        assert IntType.SQL_MIN <= value <= IntType.SQL_MAX

    def test_constrained_mock(self):
        SmallPosInt = Integer(gt=0, le=100)
        for _ in range(10):
            value = SmallPosInt.mock()
            assert 1 <= value <= 100

    def test_tinyint_mock(self):
        TinyType = TinyInt()
        for _ in range(10):
            value = TinyType.mock()
            assert -128 <= value <= 127

    def test_decimal_mock(self):
        MoneyType = DecimalType(10, 2)
        value = MoneyType.mock()
        assert isinstance(value, Decimal)
        # Check it has at most 2 decimal places
        assert value.as_tuple().exponent >= -2

    def test_float_mock(self):
        FloatType = Float()
        value = FloatType.mock()
        assert isinstance(value, float)
