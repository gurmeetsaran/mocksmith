"""Specialized database types with validation for Python."""

from db_types.types.base import DBType
from db_types.types.binary import BINARY, BLOB, VARBINARY
from db_types.types.boolean import BOOLEAN
from db_types.types.numeric import (
    BIGINT,
    DECIMAL,
    DOUBLE,
    FLOAT,
    INTEGER,
    NUMERIC,
    REAL,
    SMALLINT,
)
from db_types.types.string import (
    CHAR,
    TEXT,
    VARCHAR,
)
from db_types.types.temporal import (
    DATE,
    DATETIME,
    TIME,
    TIMESTAMP,
)

__all__ = [
    "BIGINT",
    "BINARY",
    "BLOB",
    "BOOLEAN",
    "CHAR",
    "DATE",
    "DATETIME",
    "DBType",
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
    "VARBINARY",
    "VARCHAR",
]

__version__ = "0.1.0"

# Import clean annotation helpers for easier access
from db_types.annotations import (
    Varchar, Char, Text, String,
    Integer, BigInt, SmallInt, DecimalType, Money, Int,
    Float, Double,
    Date, Time, Timestamp, DateTime,
    Boolean, Bool,
    Binary, VarBinary, Blob,
)

