"""Pydantic integration for database types.

Note: With V3 pattern, all types extend native Python types and have their own
__get_pydantic_core_schema__ methods, so DBTypeValidator is no longer needed.
This file is kept for backward compatibility but most functionality is deprecated.
"""

# pyright: reportOptionalMemberAccess=false

from typing import Any

try:
    from pydantic import BaseModel  # type: ignore[import-not-found]

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None


if PYDANTIC_AVAILABLE:
    # DBModel base class for models using database types
    class DBModel(BaseModel):  # type: ignore
        """Base Pydantic model with database type support.

        Note: With V3 pattern, database types work directly with Pydantic
        without needing special handling. This class is kept for backward
        compatibility.
        """

        class Config:
            arbitrary_types_allowed = True
            validate_assignment = True

else:
    # Dummy implementation when Pydantic is not available
    DBModel = None


# Deprecated classes - kept for backward compatibility but do nothing
class DBTypeAnnotation:
    """Deprecated: V3 types handle Pydantic integration directly."""

    pass


class DBTypeValidator:
    """Deprecated: V3 types handle Pydantic integration directly.

    This class is kept for backward compatibility but does nothing.
    All V3 types have their own __get_pydantic_core_schema__ methods.
    """

    def __init__(self, db_type: Any):
        # Silently ignore - V3 types don't need this
        pass


__all__ = [
    "PYDANTIC_AVAILABLE",
    "DBModel",
    "DBTypeAnnotation",  # Deprecated
    "DBTypeValidator",  # Deprecated
]
