"""Test REAL type validation for single precision range."""

import pytest

from mocksmith import Real
from mocksmith.types.numeric import REAL

# Import pydantic if available for testing with models
try:
    from pydantic import BaseModel, ValidationError

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    ValidationError = ValueError


class TestREALValidation:
    """Test that REAL enforces single precision float limits."""

    def test_real_accepts_valid_values(self):
        """Test that REAL accepts values within single precision range."""
        real_type = REAL()

        # Test normal values
        real_type.validate(0)
        real_type.validate(1.0)
        real_type.validate(-1.0)
        real_type.validate(123.456)
        real_type.validate(-123.456)

        # Test near limits (but still valid)
        real_type.validate(3.4e38)  # Near max
        real_type.validate(-3.4e38)  # Near min
        real_type.validate(1.2e-38)  # Just above MIN_POSITIVE

    def test_real_rejects_out_of_range_values(self):
        """Test that REAL rejects values outside single precision range."""
        real_type = REAL()

        # Test values that exceed REAL max
        with pytest.raises(ValueError, match="exceeds REAL precision"):
            real_type.validate(3.5e38)

        # Test values that exceed REAL min (negative)
        with pytest.raises(ValueError, match="exceeds REAL precision"):
            real_type.validate(-3.5e38)

        # Test values below MIN_POSITIVE (but not zero)
        with pytest.raises(ValueError, match="too small for REAL precision"):
            real_type.validate(1e-39)

        with pytest.raises(ValueError, match="too small for REAL precision"):
            real_type.validate(1e-45)  # Way below MIN_POSITIVE

    def test_real_accepts_zero(self):
        """Test that REAL accepts zero despite MIN_POSITIVE constraint."""
        real_type = REAL()
        real_type.validate(0.0)
        real_type.validate(0)
        real_type.validate(-0.0)

    def test_real_type_conversion(self):
        """Test that REAL handles type conversion properly."""
        real_type = REAL()

        # Integer to float conversion should work
        real_type.validate(42)

        # String should fail
        with pytest.raises(ValueError):
            real_type.validate("123.45")

        # Other types should fail
        with pytest.raises(ValueError):
            real_type.validate([1.0])

    def test_real_mock_generation(self):
        """Test that REAL generates valid mock values."""
        real_type = REAL()

        for _ in range(100):
            value = real_type.mock()
            assert isinstance(value, float)
            # Value should be within REAL range
            assert -3.4e38 <= value <= 3.4e38
            # If positive and very small, should be above MIN_POSITIVE
            if 0 < value < 1:
                assert value >= 1.18e-38

    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Requires pydantic")
    def test_real_in_pydantic_model(self):
        """Test REAL type in pydantic model."""

        class Measurement(BaseModel):
            temperature: Real()
            pressure: Real()
            ratio: Real()

        # Valid values
        m = Measurement(temperature=20.5, pressure=101325.0, ratio=0.75)
        assert m.temperature == 20.5
        assert m.pressure == 101325.0
        assert m.ratio == 0.75

        # Test validation
        with pytest.raises(ValidationError):
            Measurement(temperature=3.5e38, pressure=1.0, ratio=0.5)  # temperature too large

    def test_real_special_values(self):
        """Test REAL with special float values."""
        real_type = REAL()

        # REAL accepts infinity and NaN by default since it doesn't have allow_inf_nan parameter
        real_type.validate(float("inf"))
        real_type.validate(float("-inf"))
        real_type.validate(float("nan"))

    def test_real_precision_edge_cases(self):
        """Test edge cases around REAL precision limits."""
        real_type = REAL()

        # Test values just at the boundary - using looser bounds for the test
        real_type.validate(3.4e38)  # Near REAL max
        real_type.validate(-3.4e38)  # Near REAL min
        real_type.validate(1.18e-38)  # Near MIN_POSITIVE

        # Test values clearly outside the boundary
        with pytest.raises(ValueError):
            real_type.validate(4e38)  # Clearly over max

        with pytest.raises(ValueError):
            real_type.validate(-4e38)  # Clearly under min

        with pytest.raises(ValueError):
            real_type.validate(1e-40)  # Clearly under MIN_POSITIVE
