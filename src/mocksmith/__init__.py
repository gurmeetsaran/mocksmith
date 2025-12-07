"""Specialized database types with validation for Python."""

__version__ = "6.1.0"

from mocksmith.annotations import (
    BigInt,
    Binary,
    Blob,
    Boolean,
    Char,
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedMoney,
    Date,
    DateTime,
    DecimalType,
    Double,
    Float,
    Integer,
    Money,
    NegativeInteger,
    NonNegativeInteger,
    NonNegativeMoney,
    NonPositiveInteger,
    Numeric,
    PositiveInteger,
    PositiveMoney,
    Real,
    SmallInt,
    Text,
    Time,
    Timestamp,
    TinyInt,
    VarBinary,
    Varchar,
)

# V3 Pattern: Direct class imports are removed to prevent misuse
# Users MUST use factory functions (Varchar, Integer, etc.) from annotations
# The old pattern VARCHAR(30) would create an instance "30", not a type!
# This breaking change prevents subtle bugs and confusion.

# Import mock utilities
try:
    from mocksmith.decorators import mockable
    from mocksmith.mock_builder import MockBuilder
    from mocksmith.mock_factory import mock_factory

    MOCK_AVAILABLE = True
except ImportError:
    MOCK_AVAILABLE = False
    mockable = None  # type: ignore
    MockBuilder = None  # type: ignore
    mock_factory = None  # type: ignore

# Core exports - Factory functions only (V3 pattern)
__all__ = [
    # Factory functions (recommended)
    "BigInt",
    "Binary",
    "Blob",
    "Boolean",
    "Char",
    "ConstrainedDecimal",
    "ConstrainedFloat",
    "ConstrainedMoney",
    "Date",
    "DateTime",
    "DecimalType",
    "Double",
    "Float",
    "Integer",
    "Money",
    "NegativeInteger",
    "NonNegativeInteger",
    "NonNegativeMoney",
    "NonPositiveInteger",
    "Numeric",
    "PositiveInteger",
    "PositiveMoney",
    "Real",
    "SmallInt",
    "Text",
    "Time",
    "Timestamp",
    "TinyInt",
    "VarBinary",
    "Varchar",
]

# Add mock utilities if available
if MOCK_AVAILABLE:
    __all__.extend(["MockBuilder", "mock_factory", "mockable"])
