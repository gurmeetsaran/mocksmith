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
    from db_types.decorators import mockable  # noqa: F401
    from db_types.mock_builder import MockBuilder  # noqa: F401
    from db_types.mock_factory import mock_factory  # noqa: F401

    _mock_exports = ["mockable", "MockBuilder", "mock_factory"]
except ImportError:
    # Mock utilities require faker
    _mock_exports = []

# Import specialized types
try:
    from db_types.specialized import (  # noqa: F401
        URL,
        City,
        Country,
        Email,
        PhoneNumber,
        State,
        ZipCode,
    )

    _specialized_types = [
        "City",
        "Country",
        "Email",
        "PhoneNumber",
        "State",
        "URL",
        "ZipCode",
    ]
except ImportError:
    # Specialized types may not be available in all environments
    _specialized_types = []

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
    *_specialized_types,
    *_mock_exports,
]

__version__ = "0.1.0"
