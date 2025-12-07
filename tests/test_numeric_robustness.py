"""Comprehensive test cases demonstrating the robustness of numeric type implementation.

This test file specifically validates:
1. The critical bug fix: TinyInt(gt=5) no longer generates values > 127
2. SQL bounds enforcement for all integer types
3. Instantiation validation (new feature)
4. Edge cases and boundary conditions
5. Constraint validation with various combinations
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated

import pytest

from mocksmith import (
    BigInt,
    ConstrainedMoney,
    DecimalType,
    Float,
    Integer,
    NegativeInteger,
    NonNegativeInteger,
    NonNegativeMoney,
    PositiveInteger,
    PositiveMoney,
    SmallInt,
    TinyInt,
    mock_factory,
)
from mocksmith.types.numeric import _INTEGER as INTEGER
from mocksmith.types.numeric import _SMALLINT as SMALLINT
from mocksmith.types.numeric import _TINYINT as TINYINT


class TestCriticalBugFix:
    """Test that the critical bug (values exceeding SQL bounds) is fixed."""

    def test_tinyint_mock_never_exceeds_127(self):
        """CRITICAL: TinyInt with gt=5 must never generate values > 127.

        This was the original bug reported by the user:
        'when i use this Annotated[int, TinyInt(gt=5)] then it generate value greater than 128'
        """
        # Create constrained TinyInt as reported in the bug
        my_tiny_int = TinyInt(gt=5)

        # Generate many values to ensure none exceed bounds
        for _ in range(1000):
            value = my_tiny_int.mock()
            assert value > 5, f"Value {value} should be greater than 5"
            assert value <= 127, f"CRITICAL BUG: Value {value} exceeds TINYINT max of 127!"
            assert value >= -128, f"Value {value} below TINYINT min of -128"

    def test_tinyint_with_high_lower_bound(self):
        """Test TinyInt with constraint near its maximum."""
        my_tiny_int = TinyInt(gt=100, le=127)

        for _ in range(100):
            value = my_tiny_int.mock()
            assert 100 < value <= 127, f"Value {value} not in range (100, 127]"

    def test_smallint_bounds_respected(self):
        """Test SmallInt never exceeds its SQL bounds."""
        my_small_int = SmallInt(gt=30000)

        for _ in range(100):
            value = my_small_int.mock()
            assert value > 30000, f"Value {value} should be greater than 30000"
            assert value <= 32767, f"Value {value} exceeds SMALLINT max of 32767"

    def test_integer_bounds_respected(self):
        """Test Integer respects 32-bit bounds."""
        my_integer = Integer(gt=2000000000)  # Near max

        for _ in range(100):
            value = my_integer.mock()
            assert value > 2000000000
            assert value <= 2147483647, f"Value {value} exceeds INTEGER max"

    def test_bigint_bounds_respected(self):
        """Test BigInt respects 64-bit bounds."""
        my_big_int = BigInt(gt=9000000000000000000)  # Near max

        for _ in range(100):
            value = my_big_int.mock()
            assert value > 9000000000000000000
            assert value <= 9223372036854775807, f"Value {value} exceeds BIGINT max"


class TestInstantiationValidation:
    """Test the new instantiation validation feature.

    User requirement: 'one test case i would like to add is that when we
    instantiate type with invalid data then also it should fail.
    previously in v1, it was possible to pass invalid data'
    """

    def test_tinyint_instantiation_validates_constraints(self):
        """Test that TinyInt validates constraints at instantiation."""
        my_tiny_int = TinyInt(gt=10, lt=50)

        # Valid values should work
        assert my_tiny_int(20) == 20
        assert my_tiny_int(11) == 11
        assert my_tiny_int(49) == 49

        # Invalid values should raise ValueError immediately
        with pytest.raises(ValueError, match="must be greater than 10"):
            my_tiny_int(10)  # Not greater than 10

        with pytest.raises(ValueError, match="must be greater than 10"):
            my_tiny_int(5)

        with pytest.raises(ValueError, match="must be less than 50"):
            my_tiny_int(50)  # Not less than 50

        with pytest.raises(ValueError, match="must be less than 50"):
            my_tiny_int(100)

    def test_instantiation_validates_sql_bounds(self):
        """Test that instantiation enforces SQL type bounds."""
        my_tiny_int = TinyInt(gt=0)

        # Within bounds
        assert my_tiny_int(100) == 100
        assert my_tiny_int(127) == 127

        # Exceeds SQL bounds
        with pytest.raises(ValueError, match="out of TINYINT range"):
            my_tiny_int(128)  # Exceeds max

        with pytest.raises(ValueError, match="out of TINYINT range"):
            my_tiny_int(200)

        with pytest.raises(ValueError, match="out of TINYINT range"):
            my_tiny_int(-129)  # Below min

    def test_decimal_instantiation_validation(self):
        """Test Decimal type instantiation validation."""
        my_money = ConstrainedMoney(gt=0, le=1000)

        # Valid values
        assert my_money("500.50") == Decimal("500.50")
        assert my_money(1000) == Decimal("1000")

        # Invalid values
        with pytest.raises(ValueError, match="must be greater than 0"):
            my_money(0)

        with pytest.raises(ValueError, match="must be greater than 0"):
            my_money("-10.50")

        with pytest.raises(ValueError, match="must be less than or equal to 1000"):
            my_money(1000.01)

    def test_float_instantiation_validation(self):
        """Test Float type instantiation validation."""
        my_float = Float(ge=0.0, lt=1.0)

        # Valid values
        assert my_float(0.0) == 0.0
        assert my_float(0.5) == 0.5
        assert my_float(0.999) == 0.999

        # Invalid values
        with pytest.raises(ValueError, match=r"must be less than 1.0"):
            my_float(1.0)

        with pytest.raises(ValueError, match=r"must be greater than or equal to 0.0"):
            my_float(-0.001)

    def test_string_to_numeric_conversion(self):
        """Test that string values are properly converted and validated."""
        my_int = Integer(gt=0, le=100)

        # Valid string conversions
        assert my_int("50") == 50
        assert my_int("1") == 1
        assert my_int("100") == 100

        # Invalid string values
        with pytest.raises(ValueError, match="requires numeric value"):
            my_int("not_a_number")

        with pytest.raises(ValueError, match="must be greater than 0"):
            my_int("0")

        with pytest.raises(ValueError, match="must be less than or equal to 100"):
            my_int("101")


class TestEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions."""

    def test_zero_constraint_values(self):
        """Test constraints with value 0 (previously buggy due to falsy check)."""
        # gt=0 should create a positive constraint
        pos_int = Integer(gt=0)
        assert pos_int(1) == 1
        with pytest.raises(ValueError, match="must be greater than 0"):
            pos_int(0)

        # ge=0 should allow 0
        non_neg_int = Integer(ge=0)
        assert non_neg_int(0) == 0
        assert non_neg_int(1) == 1
        with pytest.raises(ValueError):
            non_neg_int(-1)

        # lt=0 should create a negative constraint
        neg_int = Integer(lt=0)
        assert neg_int(-1) == -1
        with pytest.raises(ValueError, match="must be less than 0"):
            neg_int(0)

        # le=0 should allow 0
        non_pos_int = Integer(le=0)
        assert non_pos_int(0) == 0
        assert non_pos_int(-1) == -1
        with pytest.raises(ValueError):
            non_pos_int(1)

    def test_boundary_values(self):
        """Test exact boundary values for each SQL type."""
        # TINYINT boundaries
        assert TINYINT(-128) == -128
        assert TINYINT(127) == 127
        with pytest.raises(ValueError):
            TINYINT(-129)
        with pytest.raises(ValueError):
            TINYINT(128)

        # SMALLINT boundaries
        assert SMALLINT(-32768) == -32768
        assert SMALLINT(32767) == 32767
        with pytest.raises(ValueError):
            SMALLINT(-32769)
        with pytest.raises(ValueError):
            SMALLINT(32768)

        # INTEGER boundaries
        assert INTEGER(-2147483648) == -2147483648
        assert INTEGER(2147483647) == 2147483647
        with pytest.raises(ValueError):
            INTEGER(-2147483649)
        with pytest.raises(ValueError):
            INTEGER(2147483648)

    def test_multiple_of_constraint(self):
        """Test the multiple_of constraint."""
        mult_of_5 = Integer(multiple_of=5, ge=0, le=100)

        # Valid multiples
        assert mult_of_5(0) == 0
        assert mult_of_5(5) == 5
        assert mult_of_5(50) == 50
        assert mult_of_5(100) == 100

        # Invalid values
        with pytest.raises(ValueError, match="must be a multiple of 5"):
            mult_of_5(7)
        with pytest.raises(ValueError, match="must be a multiple of 5"):
            mult_of_5(99)

    def test_conflicting_constraints(self):
        """Test that conflicting constraints are handled properly."""
        # Impossible constraint: gt=100 but SQL max is 127
        impossible_tiny = TinyInt(gt=200)

        # Should not be able to generate valid mock
        with pytest.raises(ValueError, match="No valid values"):
            impossible_tiny.mock()

        # Conflicting gt and lt
        conflicting = Integer(gt=100, lt=50)
        with pytest.raises(ValueError, match="No valid values"):
            conflicting.mock()

    def test_decimal_precision_and_scale(self):
        """Test Decimal precision and scale enforcement."""
        # DECIMAL(5,2) means max 999.99
        small_decimal = DecimalType(5, 2, ge=0)

        # Valid values
        assert small_decimal("999.99") == Decimal("999.99")
        assert small_decimal("0.01") == Decimal("0.01")
        assert small_decimal(100) == Decimal("100")

        # Too many integer digits
        with pytest.raises(ValueError, match="Too many integer digits"):
            small_decimal("1000.00")  # Would need 4 integer digits

        # Automatic rounding of decimal places
        result = small_decimal("10.999")  # Should round to 11.00
        assert result == Decimal("11.00")


class TestConstraintCombinations:
    """Test various combinations of constraints."""

    def test_all_constraint_types_together(self):
        """Test using all constraint types simultaneously."""
        complex_int = Integer(
            gt=10,  # Greater than 10
            le=100,  # Less than or equal to 100
            multiple_of=3,  # Must be divisible by 3
        )

        # Valid values
        assert complex_int(12) == 12  # 12 > 10, 12 <= 100, 12 % 3 == 0
        assert complex_int(99) == 99  # 99 > 10, 99 <= 100, 99 % 3 == 0

        # Invalid values
        with pytest.raises(ValueError):
            complex_int(9)  # Not greater than 10
        with pytest.raises(ValueError):
            complex_int(102)  # Greater than 100
        with pytest.raises(ValueError):
            complex_int(11)  # Not a multiple of 3

    def test_narrow_range_constraints(self):
        """Test very narrow constraint ranges."""
        # Only values 126 and 127 are valid
        narrow_tiny = TinyInt(gt=125, le=127)

        values = set()
        for _ in range(50):
            values.add(narrow_tiny.mock())

        # Should only generate 126 and 127
        assert values == {126, 127}

    def test_single_valid_value(self):
        """Test constraint that allows only one value."""
        # Only 100 is valid
        single_value = Integer(ge=100, le=100)

        assert single_value(100) == 100
        with pytest.raises(ValueError):
            single_value(99)
        with pytest.raises(ValueError):
            single_value(101)

        # Mock should always return 100
        for _ in range(10):
            assert single_value.mock() == 100


class TestSpecializedTypes:
    """Test specialized constraint types."""

    def test_positive_types(self):
        """Test positive-only types."""
        pos_int = PositiveInteger()

        # Valid
        assert pos_int(1) == 1
        assert pos_int(1000000) == 1000000

        # Invalid
        with pytest.raises(ValueError, match="must be greater than 0"):
            pos_int(0)
        with pytest.raises(ValueError):
            pos_int(-1)

        # Mock generation
        for _ in range(50):
            value = pos_int.mock()
            assert value > 0

    def test_non_negative_types(self):
        """Test non-negative types (includes 0)."""
        non_neg_int = NonNegativeInteger()

        # Valid
        assert non_neg_int(0) == 0
        assert non_neg_int(1000000) == 1000000

        # Invalid
        with pytest.raises(ValueError, match="must be greater than or equal to 0"):
            non_neg_int(-1)

        # Mock generation
        for _ in range(50):
            value = non_neg_int.mock()
            assert value >= 0

    def test_negative_types(self):
        """Test negative-only types."""
        neg_int = NegativeInteger()

        # Valid
        assert neg_int(-1) == -1
        assert neg_int(-1000000) == -1000000

        # Invalid
        with pytest.raises(ValueError, match="must be less than 0"):
            neg_int(0)
        with pytest.raises(ValueError):
            neg_int(1)

        # Mock generation
        for _ in range(50):
            value = neg_int.mock()
            assert value < 0

    def test_money_types(self):
        """Test money-specific types."""
        # Positive money
        pos_money = PositiveMoney()

        assert pos_money("0.01") == Decimal("0.01")
        assert pos_money(100) == Decimal("100")

        with pytest.raises(ValueError, match="must be greater than 0"):
            pos_money(0)

        # Non-negative money
        non_neg_money = NonNegativeMoney()

        assert non_neg_money(0) == Decimal("0")
        assert non_neg_money("100.50") == Decimal("100.50")

        with pytest.raises(ValueError, match="must be greater than or equal to 0"):
            non_neg_money(-0.01)


class TestDataclassAndPydanticIntegration:
    """Test integration with dataclasses and Pydantic models."""

    def test_dataclass_with_constraints(self):
        """Test that constrained types work in dataclasses."""

        @dataclass
        class Product:
            id: Annotated[int, PositiveInteger()]
            stock: Annotated[int, TinyInt(ge=0, le=100)]
            price: Annotated[Decimal, ConstrainedMoney(gt=0, le=9999.99)]
            discount_percent: Annotated[int, TinyInt(ge=0, le=90)]

        # Create with valid values
        product = Product(id=12345, stock=50, price=Decimal("299.99"), discount_percent=25)

        assert product.id == 12345
        assert product.stock == 50
        assert product.price == Decimal("299.99")
        assert product.discount_percent == 25

        # Test mock generation
        mock_product = mock_factory(Product)

        # All constraints should be respected
        assert mock_product.id > 0
        assert 0 <= mock_product.stock <= 100
        assert -128 <= mock_product.stock <= 127  # TINYINT bounds
        assert mock_product.price > 0
        assert mock_product.price <= Decimal("9999.99")
        assert 0 <= mock_product.discount_percent <= 90
        assert -128 <= mock_product.discount_percent <= 127  # TINYINT bounds

    def test_pydantic_model_validation(self):
        """Test that types work with Pydantic validation."""
        try:
            from pydantic import BaseModel, ValidationError
        except ImportError:
            pytest.skip("Pydantic not installed")

        class Order(BaseModel):
            quantity: PositiveInteger()
            unit_price: ConstrainedMoney(gt=0, le=1000)
            discount: TinyInt(ge=0, le=100)

        # Valid order
        order = Order(quantity=5, unit_price="99.99", discount=10)

        assert order.quantity == 5
        assert order.unit_price == Decimal("99.99")
        assert order.discount == 10

        # Invalid values should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Order(
                quantity=0,  # Not positive
                unit_price="1001",  # Exceeds max
                discount=150,  # Exceeds both constraint and TINYINT max
            )

        errors = exc_info.value.errors()
        assert len(errors) == 3  # All three fields should have errors

    def test_nested_model_with_constraints(self):
        """Test nested models with constrained types."""

        @dataclass
        class Address:
            zip_code: Annotated[int, Integer(ge=10000, le=99999)]
            apartment: Annotated[int, SmallInt(ge=1, le=9999)]

        @dataclass
        class Customer:
            id: Annotated[int, PositiveInteger()]
            age: Annotated[int, TinyInt(ge=18, le=120)]
            balance: Annotated[Decimal, NonNegativeMoney()]
            address: Address

        # Test mock generation with nested models
        customer = mock_factory(Customer)

        # Check customer fields
        assert customer.id > 0
        assert 18 <= customer.age <= 120
        assert customer.balance >= 0

        # Check nested address fields
        assert 10000 <= customer.address.zip_code <= 99999
        assert 1 <= customer.address.apartment <= 9999


class TestMockGenerationStatistics:
    """Test that mock generation produces well-distributed values."""

    def test_distribution_across_range(self):
        """Test that mock values are distributed across the valid range."""
        my_int = Integer(ge=1, le=10)

        # Generate many values
        values = [my_int.mock() for _ in range(1000)]

        # Check that we get all possible values (1-10)
        unique_values = set(values)
        assert unique_values == set(range(1, 11))

        # Check reasonable distribution (no value should dominate)
        from collections import Counter

        counts = Counter(values)
        for value, count in counts.items():
            # Each value should appear roughly 100 times (±50%)
            assert 50 <= count <= 150, f"Value {value} appeared {count} times (poor distribution)"

    def test_extreme_bounds_generation(self):
        """Test mock generation with extreme bounds."""
        # Near TINYINT maximum
        high_tiny = TinyInt(ge=120, le=127)
        values = {high_tiny.mock() for _ in range(100)}
        assert values.issubset(set(range(120, 128)))

        # Near TINYINT minimum
        low_tiny = TinyInt(ge=-128, le=-120)
        values = {low_tiny.mock() for _ in range(100)}
        assert values.issubset(set(range(-128, -119)))

    def test_decimal_mock_generation(self):
        """Test that decimal mock generation works correctly."""
        my_decimal = DecimalType(10, 2, ge=Decimal("0.01"), le=Decimal("999.99"))

        for _ in range(100):
            value = my_decimal.mock()
            assert value >= Decimal("0.01")
            assert value <= Decimal("999.99")

            # Check scale (max 2 decimal places)
            str_val = str(value)
            if "." in str_val:
                decimal_places = len(str_val.split(".")[1])
                assert decimal_places <= 2


if __name__ == "__main__":
    # Run a quick smoke test
    print("Running numeric robustness tests...")

    # Test 1: Critical bug fix
    test = TestCriticalBugFix()
    test.test_tinyint_mock_never_exceeds_127()
    print("✓ Critical bug fix verified: TinyInt respects SQL bounds")

    # Test 2: Instantiation validation
    test2 = TestInstantiationValidation()
    test2.test_tinyint_instantiation_validates_constraints()
    print("✓ Instantiation validation works correctly")

    # Test 3: Edge cases
    test3 = TestEdgeCasesAndBoundaries()
    test3.test_zero_constraint_values()
    print("✓ Edge cases handled properly")

    print("\nAll smoke tests passed! Run pytest for comprehensive testing.")
