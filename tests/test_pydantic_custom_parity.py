"""Test that custom validation matches Pydantic validation behavior."""

import sys
from decimal import Decimal

import pytest

# Check if pydantic is available
try:
    import pydantic  # noqa: F401

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

# Skip entire module if pydantic is not available
pytestmark = pytest.mark.skipif(
    not PYDANTIC_AVAILABLE, reason="Pydantic not installed - skipping parity tests"
)

# Temporarily disable Pydantic to test custom validation
original_modules = sys.modules.copy()


class MockPydanticUnavailable:
    """Context manager to simulate Pydantic being unavailable."""

    def __enter__(self):
        # Remove pydantic from sys.modules
        pydantic_modules = [key for key in sys.modules.keys() if key.startswith("pydantic")]
        for module in pydantic_modules:
            sys.modules.pop(module, None)

        # Force PYDANTIC_AVAILABLE to False
        import mocksmith.types.base

        mocksmith.types.base.PYDANTIC_AVAILABLE = False

        # Reload numeric module to pick up the change
        import importlib

        import mocksmith.types.numeric

        importlib.reload(mocksmith.types.numeric)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)

        # Restore PYDANTIC_AVAILABLE
        import mocksmith.types.base

        mocksmith.types.base.PYDANTIC_AVAILABLE = True

        # Reload to restore normal behavior
        import importlib

        import mocksmith.types.numeric

        importlib.reload(mocksmith.types.numeric)


# Import after defining the mock to test custom validation behavior
from mocksmith.types.boolean import BOOLEAN  # noqa: E402
from mocksmith.types.numeric import DECIMAL, FLOAT, INTEGER, REAL  # noqa: E402
from mocksmith.types.string import VARCHAR  # noqa: E402


class TestPydanticCustomParity:
    """Test that custom validation matches Pydantic validation behavior."""

    def test_integer_validation_parity(self):
        """Test INTEGER validation with and without Pydantic."""
        int_type = INTEGER(gt=0, le=100, multiple_of=5)

        # Test with Pydantic (default)
        valid_values = [5, 10, 50, 100]
        invalid_values = [
            (0, "greater than 0"),  # Not greater than 0
            (-5, "greater than 0"),  # Negative
            (
                101,
                "multiple of 5|less than or equal to 100",
            ),  # Too large (pydantic checks multiple_of first)
            (7, "multiple of 5"),  # Not multiple of 5
            (10.5, "integer"),  # Float with decimal
            ("not a number", "valid integer|numeric"),  # String (pydantic vs custom message)
        ]

        # Test valid values with Pydantic
        for value in valid_values:
            int_type.validate(value)  # Should not raise

        # Test invalid values with Pydantic
        for value, expected_error in invalid_values:
            with pytest.raises(ValueError, match=expected_error):
                int_type.validate(value)

        # Now test without Pydantic (using custom validation)
        with MockPydanticUnavailable():
            int_type_custom = INTEGER(gt=0, le=100, multiple_of=5)

            # Test valid values with custom validation
            for value in valid_values:
                int_type_custom.validate(value)  # Should not raise

            # Test invalid values with custom validation
            for value, expected_error in invalid_values:
                with pytest.raises(ValueError, match=expected_error):
                    int_type_custom.validate(value)

    def test_decimal_validation_parity(self):
        """Test DECIMAL validation with and without Pydantic."""
        dec_type = DECIMAL(10, 2, ge=Decimal("0"), le=Decimal("1000"))

        valid_values = [
            "0",
            "0.00",
            "100.50",
            "1000",
            "1000.00",
            500,  # Integer
            123.45,  # Float
            Decimal("999.99"),
        ]

        invalid_values = [
            ("-1", "greater than or equal to 0"),  # Negative
            ("1000.01", "less than or equal to 1000"),  # Too large
            ("123.456", "decimal places"),  # Too many decimals
            (
                "12345678901.00",
                "too many digits|no more than 10 digits",
            ),  # Too many total digits (pydantic vs custom)
            ("not a number", "Cannot convert|valid decimal"),  # Invalid string (custom vs pydantic)
        ]

        # Test with Pydantic
        for value in valid_values:
            dec_type.validate(value)  # Should not raise

        for value, expected_error in invalid_values:
            with pytest.raises(ValueError, match=expected_error):
                dec_type.validate(value)

        # Test without Pydantic
        with MockPydanticUnavailable():
            dec_type_custom = DECIMAL(10, 2, ge=Decimal("0"), le=Decimal("1000"))

            for value in valid_values:
                dec_type_custom.validate(value)  # Should not raise

            for value, expected_error in invalid_values:
                with pytest.raises(ValueError, match=expected_error):
                    dec_type_custom.validate(value)

    def test_float_validation_parity(self):
        """Test FLOAT validation with and without Pydantic."""
        float_type = FLOAT(ge=0.0, le=1.0, allow_inf_nan=False)

        valid_values = [0.0, 0.5, 1.0, 0, 1]  # Including integers

        invalid_values = [
            (-0.1, "greater than or equal to 0"),
            (1.1, "less than or equal to 1"),
            (float("inf"), "finite"),
            (float("nan"), "finite"),
            ("not a number", "numeric|valid number"),
        ]

        # Test with Pydantic
        for value in valid_values:
            float_type.validate(value)

        for value, expected_error in invalid_values:
            with pytest.raises(ValueError, match=expected_error):
                float_type.validate(value)

        # Test without Pydantic
        with MockPydanticUnavailable():
            float_type_custom = FLOAT(ge=0.0, le=1.0, allow_inf_nan=False)

            for value in valid_values:
                float_type_custom.validate(value)

            for value, expected_error in invalid_values:
                with pytest.raises(ValueError, match=expected_error):
                    float_type_custom.validate(value)

    def test_varchar_validation_parity(self):
        """Test VARCHAR validation with and without Pydantic."""
        varchar_type = VARCHAR(10, min_length=2)

        valid_values = ["ab", "hello", "1234567890"]  # Strings only for parity

        invalid_values = [
            ("a", "at least 2 characters|less than minimum"),  # Too short (pydantic vs custom)
            (
                "12345678901",
                "at most 10 characters|exceeds maximum",
            ),  # Too long (pydantic vs custom)
            ("", "at least 2 characters|less than minimum"),  # Empty (pydantic vs custom)
            (123, "string|int"),  # Type error (pydantic vs custom)
        ]

        # Test with Pydantic
        for value in valid_values:
            varchar_type.validate(value)

        for value, expected_error in invalid_values:
            with pytest.raises(ValueError, match=expected_error):
                varchar_type.validate(value)

        # None should not raise
        varchar_type.validate(None)

        # Test without Pydantic
        with MockPydanticUnavailable():
            varchar_type_custom = VARCHAR(10, min_length=2)

            for value in valid_values:
                varchar_type_custom.validate(value)

            for value, expected_error in invalid_values[:-1]:  # Skip None
                with pytest.raises(ValueError, match=expected_error):
                    varchar_type_custom.validate(value)

            # None should not raise
            varchar_type_custom.validate(None)

    def test_boolean_validation_parity(self):
        """Test BOOLEAN validation with and without Pydantic."""
        bool_type = BOOLEAN()

        valid_values = [
            True,
            False,
            1,
            0,
            "true",
            "false",
            "yes",
            "no",
            "1",
            "0",
        ]

        invalid_values = [
            ("maybe", "boolean"),
            ("", "boolean"),
            ([], "boolean"),
        ]

        # Test with Pydantic
        for value in valid_values:
            bool_type.validate(value)

        # Value 2 is accepted by both (truthy in Python)
        bool_type.validate(2)

        for value, expected_error in invalid_values:
            with pytest.raises(ValueError, match=expected_error):
                bool_type.validate(value)

        # Test without Pydantic
        with MockPydanticUnavailable():
            bool_type_custom = BOOLEAN()

            for value in valid_values:
                bool_type_custom.validate(value)

            # Value 2 is accepted by both (truthy in Python)
            bool_type_custom.validate(2)

            for value, expected_error in invalid_values:
                with pytest.raises(ValueError, match=expected_error):
                    bool_type_custom.validate(value)

    def test_real_always_uses_custom(self):
        """Test that REAL type always uses custom validation."""
        real_type = REAL()

        # REAL has special validation for MIN_POSITIVE
        valid_values = [
            0.0,
            1.0,
            -1.0,
            3.4e38,  # Near max
            -3.4e38,  # Near min
            1.2e-38,  # Just above MIN_POSITIVE
        ]

        invalid_values = [
            (3.5e38, "exceeds REAL precision"),  # Too large
            (-3.5e38, "exceeds REAL precision"),  # Too small negative
            (1e-39, "too small for REAL precision"),  # Below MIN_POSITIVE
            ("not a number", "numeric|valid number"),
        ]

        # REAL always uses custom validation, even with Pydantic available
        for value in valid_values:
            real_type.validate(value)

        for value, expected_error in invalid_values:
            with pytest.raises(ValueError, match=expected_error):
                real_type.validate(value)

        # Should behave the same without Pydantic
        with MockPydanticUnavailable():
            real_type_custom = REAL()

            for value in valid_values:
                real_type_custom.validate(value)

            for value, expected_error in invalid_values:
                with pytest.raises(ValueError, match=expected_error):
                    real_type_custom.validate(value)

    def test_strict_mode_parity(self):
        """Test strict mode validation with and without Pydantic."""
        # Strict integer - no type coercion
        strict_int = INTEGER(strict=True)

        # With Pydantic
        strict_int.validate(100)  # Should pass
        with pytest.raises(ValueError, match="int"):
            strict_int.validate("100")  # String not allowed in strict mode

        # Without Pydantic
        with MockPydanticUnavailable():
            strict_int_custom = INTEGER(strict=True)

            strict_int_custom.validate(100)  # Should pass
            with pytest.raises(ValueError, match="int"):
                strict_int_custom.validate("100")  # String not allowed

    def test_edge_cases_parity(self):
        """Test edge cases behave the same with both validation methods."""
        # Test integer with exact bounds
        int_exact = INTEGER(ge=10, le=10)  # Only 10 is valid

        # With Pydantic
        int_exact.validate(10)
        with pytest.raises(ValueError):
            int_exact.validate(9)
        with pytest.raises(ValueError):
            int_exact.validate(11)

        # Without Pydantic
        with MockPydanticUnavailable():
            int_exact_custom = INTEGER(ge=10, le=10)

            int_exact_custom.validate(10)
            with pytest.raises(ValueError):
                int_exact_custom.validate(9)
            with pytest.raises(ValueError):
                int_exact_custom.validate(11)

        # Test decimal with scale = 0 (integer decimal)
        dec_int = DECIMAL(5, 0)  # Max 99999, no decimals

        # With Pydantic
        dec_int.validate(12345)
        dec_int.validate("12345")
        with pytest.raises(ValueError, match="decimal places"):
            dec_int.validate("123.45")

        # Without Pydantic
        with MockPydanticUnavailable():
            dec_int_custom = DECIMAL(5, 0)

            dec_int_custom.validate(12345)
            dec_int_custom.validate("12345")
            with pytest.raises(ValueError, match="decimal places"):
                dec_int_custom.validate("123.45")


if __name__ == "__main__":
    # Run a quick test
    test = TestPydanticCustomParity()
    test.test_integer_validation_parity()
    test.test_decimal_validation_parity()
    test.test_float_validation_parity()
    test.test_varchar_validation_parity()
    test.test_boolean_validation_parity()
    test.test_real_always_uses_custom()
    test.test_strict_mode_parity()
    test.test_edge_cases_parity()
    print("All parity tests passed! ✅")
