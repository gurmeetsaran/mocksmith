"""Test that Numeric alias works correctly."""

from decimal import Decimal
from typing import get_args

import pytest
from pydantic import BaseModel

from db_types import DecimalType, Numeric, Real


class TestNumericAlias:
    """Test that Numeric and Real aliases work correctly."""

    def test_numeric_is_alias_for_decimal(self):
        """Test that Numeric is an alias for DecimalType."""
        # Create annotations
        numeric_type = Numeric(10, 2)
        decimal_type = DecimalType(10, 2)

        # Extract the db_type from annotations
        numeric_args = get_args(numeric_type)
        decimal_args = get_args(decimal_type)

        # Both should have the same structure
        assert len(numeric_args) == len(decimal_args)

        # Find the db_type in the args
        numeric_db_type = None
        decimal_db_type = None

        for arg in numeric_args[1:]:
            if hasattr(arg, "sql_type"):
                numeric_db_type = arg
            elif hasattr(arg, "db_type") and hasattr(arg.db_type, "sql_type"):
                numeric_db_type = arg.db_type

        for arg in decimal_args[1:]:
            if hasattr(arg, "sql_type"):
                decimal_db_type = arg
            elif hasattr(arg, "db_type") and hasattr(arg.db_type, "sql_type"):
                decimal_db_type = arg.db_type

        # Both should generate the same SQL type
        assert numeric_db_type is not None
        assert decimal_db_type is not None
        assert numeric_db_type.sql_type == decimal_db_type.sql_type
        assert numeric_db_type.sql_type == "DECIMAL(10,2)"

    def test_uppercase_numeric_alias(self):
        """Test that NUMERIC is an alias for DecimalType."""
        # NUMERIC should be the same function as DecimalType in annotations module
        from db_types.annotations import NUMERIC as NUMERIC_FUNC
        from db_types.annotations import DecimalType as DECIMAL_FUNC  # noqa: N814

        assert NUMERIC_FUNC is DECIMAL_FUNC

    def test_real_generates_real_sql_type(self):
        """Test that Real generates REAL SQL type."""
        # Create annotation
        real_type = Real()

        # Extract the db_type from annotation
        real_args = get_args(real_type)

        # Find the db_type in the args
        real_db_type = None

        for arg in real_args[1:]:
            if hasattr(arg, "sql_type"):
                real_db_type = arg
            elif hasattr(arg, "db_type") and hasattr(arg.db_type, "sql_type"):
                real_db_type = arg.db_type

        # Should generate REAL SQL type
        assert real_db_type is not None
        assert real_db_type.sql_type == "REAL"

    def test_uppercase_real_alias(self):
        """Test that REAL is an alias for Real."""
        # REAL should be the same function as Real in annotations module
        from db_types.annotations import REAL as REAL_FUNC
        from db_types.annotations import Real as Real_FUNC

        assert REAL_FUNC is Real_FUNC

    def test_numeric_in_pydantic_model(self):
        """Test that Numeric works in Pydantic models."""

        class Invoice(BaseModel):
            amount: Numeric(10, 2)
            tax_amount: Numeric(8, 4)

        invoice = Invoice(amount="1234.56", tax_amount="123.4567")

        assert invoice.amount == Decimal("1234.56")
        assert invoice.tax_amount == Decimal("123.4567")

        # Test validation
        with pytest.raises(ValueError):
            Invoice(amount="12345678901.00", tax_amount="0.00")  # Too many digits

    def test_real_in_pydantic_model(self):
        """Test that Real works in Pydantic models."""

        class Measurement(BaseModel):
            temperature: Real()
            pressure: Real()

        measurement = Measurement(temperature=98.6, pressure="1013.25")

        assert measurement.temperature == 98.6
        assert measurement.pressure == 1013.25
