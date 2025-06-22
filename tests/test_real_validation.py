"""Test REAL type validation for single precision range."""

import pytest
from pydantic import BaseModel, ValidationError

from mocksmith import Real
from mocksmith.types.numeric import REAL


class TestREALValidation:
    """Test that REAL enforces single precision float limits."""

    def test_real_accepts_valid_values(self):
        """Test that REAL accepts values within single precision range."""
        real_type = REAL()

        # Test normal values
        real_type.validate(0)
        real_type.validate(1.0)
        real_type.validate(-1.0)
        real_type.validate(1234.5678)
        real_type.validate(3.4e38)  # Near max
        real_type.validate(-3.4e38)  # Near min
        real_type.validate(1.2e-38)  # Small positive

    def test_real_rejects_too_large_values(self):
        """Test that REAL rejects values exceeding single precision range."""
        real_type = REAL()

        # Value too large for single precision
        with pytest.raises(ValueError, match="exceeds REAL precision range"):
            real_type.validate(1e39)

        with pytest.raises(ValueError, match="exceeds REAL precision range"):
            real_type.validate(-1e39)

    def test_real_rejects_too_small_values(self):
        """Test that REAL rejects values too small for single precision."""
        real_type = REAL()

        # Value too small (underflow)
        with pytest.raises(ValueError, match="too small for REAL precision"):
            real_type.validate(1e-39)

        with pytest.raises(ValueError, match="too small for REAL precision"):
            real_type.validate(-1e-39)

    def test_real_in_pydantic_model(self):
        """Test REAL validation in Pydantic models."""

        class Measurement(BaseModel):
            temperature: Real()
            pressure: Real()

        # Valid values
        m = Measurement(temperature=25.5, pressure=1013.25)
        assert m.temperature == 25.5
        assert m.pressure == 1013.25

        # Value too large
        with pytest.raises(ValidationError) as exc_info:
            Measurement(temperature=1e39, pressure=1013.25)
        assert "exceeds REAL precision range" in str(exc_info.value)

        # Value too small
        with pytest.raises(ValidationError) as exc_info:
            Measurement(temperature=25.5, pressure=1e-39)
        assert "too small for REAL precision" in str(exc_info.value)

    def test_real_zero_handling(self):
        """Test that REAL properly handles zero."""
        real_type = REAL()
        real_type.validate(0)
        real_type.validate(0.0)
        real_type.validate(-0.0)

    def test_real_edge_cases(self):
        """Test REAL with edge case values."""
        real_type = REAL()

        # Just within bounds
        real_type.validate(3.4e38)
        real_type.validate(-3.4e38)
        real_type.validate(1.2e-38)

        # Special float values
        real_type.validate(float("inf"))  # This might need special handling
        real_type.validate(float("-inf"))
        # NaN would fail isinstance check

    def test_double_precision_values_in_real(self):
        """Test that REAL rejects values that require double precision."""
        real_type = REAL()

        # This number requires double precision to represent accurately
        # Single precision would lose significant digits
        with pytest.raises(ValueError, match="exceeds REAL precision range"):
            real_type.validate(1.7976931348623157e308)  # Max double
