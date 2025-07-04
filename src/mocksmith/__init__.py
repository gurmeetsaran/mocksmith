"""Specialized database types with validation for Python."""

__version__ = "3.0.3"

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
from mocksmith.types.base import DBType
from mocksmith.types.binary import BINARY, BLOB, VARBINARY
from mocksmith.types.boolean import BOOLEAN
from mocksmith.types.numeric import (
    BIGINT,
    DECIMAL,
    DOUBLE,
    FLOAT,
    INTEGER,
    NUMERIC,
    REAL,
    SMALLINT,
    TINYINT,
)
from mocksmith.types.string import CHAR, TEXT, VARCHAR
from mocksmith.types.temporal import DATE, DATETIME, TIME, TIMESTAMP

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

# Core exports
__all__ = [
    "BIGINT",
    "BINARY",
    "BLOB",
    "BOOLEAN",
    "CHAR",
    "DATE",
    "DATETIME",
    "DECIMAL",
    "DOUBLE",
    "FLOAT",
    "INTEGER",
    "NUMERIC",
    "REAL",
    "SMALLINT",
    "TEXT",
    "TIME",
    "TIMESTAMP",
    "TINYINT",
    "VARBINARY",
    "VARCHAR",
    "BigInt",
    "Binary",
    "Blob",
    "Boolean",
    "Char",
    "ConstrainedDecimal",
    "ConstrainedFloat",
    "ConstrainedMoney",
    "DBType",
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
