"""Pydantic integration for database types."""
# pyright: reportOptionalMemberAccess=false

from typing import Any, Callable, Dict, Type

try:
    from pydantic import BaseModel
    from pydantic_core import core_schema

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None
    core_schema = None

from db_types.types.base import DBType

if PYDANTIC_AVAILABLE and core_schema is not None:
    assert core_schema is not None  # Type assertion for pyright

    class DBTypeAnnotation:
        """Custom Pydantic annotation for database types."""

        @classmethod
        def __get_pydantic_core_schema__(
            cls, source: Type[Any], handler: Callable[[Any], core_schema.CoreSchema]
        ) -> core_schema.CoreSchema:
            """Generate Pydantic core schema for DBType validation."""
            if hasattr(source, "__args__") and len(source.__args__) > 0:
                db_type_instance = source.__args__[0]
            else:
                # Fallback for direct DBType instances
                db_type_instance = source

            def validate(value: Any) -> Any:
                """Validate and deserialize value."""
                return db_type_instance.deserialize(value)

            def serialize(value: Any) -> Any:
                """Serialize value."""
                return db_type_instance.serialize(value)

            return core_schema.no_info_after_validator_function(
                validate,
                core_schema.any_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    serialize,
                    return_schema=core_schema.any_schema(),
                ),
            )

    class DBTypeValidator:
        """Validator class for DBType fields in Pydantic models."""

        def __init__(self, db_type: DBType):
            self.db_type = db_type

        def __get_pydantic_core_schema__(
            self, source: Type[Any], handler: Callable[[Any], core_schema.CoreSchema]
        ) -> core_schema.CoreSchema:
            """Generate Pydantic core schema."""

            def validate(value: Any) -> Any:
                return self.db_type.deserialize(value)

            def serialize(value: Any) -> Any:
                return self.db_type.serialize(value)

            return core_schema.no_info_after_validator_function(
                validate,
                core_schema.any_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    serialize,
                    return_schema=core_schema.any_schema(),
                ),
            )

    # Example base model with DB type support
    class DBModel(BaseModel):  # type: ignore
        """Base Pydantic model with database type support."""

        class Config:
            arbitrary_types_allowed = True
            validate_assignment = True

        @classmethod
        def get_db_types(cls) -> Dict[str, DBType]:
            """Get all database type fields in the model.

            Returns:
                Dictionary mapping field names to DBType instances
            """
            db_types = {}
            for field_name, field_info in cls.model_fields.items():
                # Check if field has DBType annotation
                if hasattr(field_info, "metadata"):
                    for metadata in field_info.metadata:
                        if isinstance(metadata, DBTypeValidator):
                            db_types[field_name] = metadata.db_type
                            break
            return db_types

        def to_sql_dict(self) -> Dict[str, Any]:
            """Convert model to dictionary with SQL-compatible values.

            Returns:
                Dictionary with serialized values
            """
            result = {}
            db_types = self.get_db_types()

            for field_name, value in self.model_dump().items():
                if field_name in db_types:
                    result[field_name] = db_types[field_name].serialize(value)
                else:
                    result[field_name] = value

            return result

else:
    # Dummy implementations when Pydantic is not available
    DBTypeAnnotation = None
    DBTypeValidator = None
    DBModel = None


__all__ = [
    "PYDANTIC_AVAILABLE",
    "DBModel",
    "DBTypeAnnotation",
    "DBTypeValidator",
]
