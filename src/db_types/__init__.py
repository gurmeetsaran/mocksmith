"""Specialized database types with validation for Python."""

from db_types.annotations import (
    BigInt,
    Binary,
    Blob,
    Boolean,
    Char,
    Date,
    DateTime,
    DecimalType,
    Double,
    Float,
    Integer,
    Money,
    NegativeInteger,
    NonNegativeInteger,
    NonPositiveInteger,
    Numeric,
    PositiveInteger,
    Real,
    SmallInt,
    Text,
    Time,
    Timestamp,
    TinyInt,
    VarBinary,
    Varchar,
)
from db_types.types.base import DBType
from db_types.types.binary import BINARY, BLOB, VARBINARY
from db_types.types.boolean import BOOLEAN
from db_types.types.constraints import (
    ConstrainedBigInt,
    ConstrainedInteger,
    ConstrainedSmallInt,
    ConstrainedTinyInt,
)
from db_types.types.numeric import (
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
from db_types.types.string import CHAR, TEXT, VARCHAR
from db_types.types.temporal import DATE, DATETIME, TIME, TIMESTAMP

# Import mock utilities
try:
    from db_types.decorators import mockable
    from db_types.mock_builder import MockBuilder
    from db_types.mock_factory import mock_factory

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
    "ConstrainedBigInt",
    "ConstrainedInteger",
    "ConstrainedSmallInt",
    "ConstrainedTinyInt",
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
    "NonPositiveInteger",
    "Numeric",
    "PositiveInteger",
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

__version__ = "0.1.0"
