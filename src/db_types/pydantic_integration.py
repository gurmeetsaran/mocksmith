"""Pydantic integration for database types."""

import sys
from typing import Any, Callable, Type

try:
    from pydantic import BaseModel, Field, field_serializer, field_validator
    from pydantic.fields import FieldInfo
    from pydantic_core import core_schema
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None
    Field = None
    field_validator = None
    field_serializer = None
    FieldInfo = None
    core_schema = None

from db_types.types.base import DBType

if PYDANTIC_AVAILABLE:
    class DBTypeAnnotation:
        """Custom Pydantic annotation for database types."""

        @classmethod
        def __get_pydantic_core_schema__(
            cls,
            source: Type[Any],
            handler: Callable[[Any], core_schema.CoreSchema]
        ) -> core_schema.CoreSchema:
            """Generate Pydantic core schema for DBType validation."""
            if hasattr(source, '__args__') and len(source.__args__) > 0:
                db_type_instance = source.__args__[0]
            else:
                # Fallback for direct DBType instances
                db_type_instance = source

            python_type = db_type_instance.python_type

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


    def create_db_field(db_type: DBType, **field_kwargs) -> FieldInfo:
        """Create a Pydantic field with database type validation.
        
        Args:
            db_type: Database type instance
            **field_kwargs: Additional field arguments
            
        Returns:
            Pydantic FieldInfo
        """
        # No automatic defaults - let user control this

        # Add description
        if 'description' not in field_kwargs:
            field_kwargs['description'] = f"Database type: {db_type.sql_type}"

        return Field(**field_kwargs)


    class DBTypeValidator:
        """Validator class for DBType fields in Pydantic models."""

        def __init__(self, db_type: DBType):
            self.db_type = db_type

        def __get_pydantic_core_schema__(
            self,
            source: Type[Any],
            handler: Callable[[Any], core_schema.CoreSchema]
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


    # Convenience function for creating annotated types
    def Annotated(db_type: DBType):
        """Create an annotated type for Pydantic models.
        
        Usage:
            from pydantic import BaseModel
            from db_types import VARCHAR
            from db_types.pydantic_integration import Annotated
            
            class User(BaseModel):
                name: Annotated[VARCHAR(50)]
                email: Annotated[VARCHAR(100)]
        """
        if sys.version_info >= (3, 9):
            from typing import Annotated as TypeAnnotated
        else:
            from typing_extensions import Annotated as TypeAnnotated

        return TypeAnnotated[db_type.python_type, DBTypeValidator(db_type)]


    # Example base model with DB type support
    class DBModel(BaseModel):
        """Base Pydantic model with database type support."""

        class Config:
            arbitrary_types_allowed = True
            validate_assignment = True

        @classmethod
        def get_db_types(cls) -> dict[str, DBType]:
            """Get all database type fields in the model.
            
            Returns:
                Dictionary mapping field names to DBType instances
            """
            db_types = {}
            for field_name, field_info in cls.model_fields.items():
                # Check if field has DBType annotation
                if hasattr(field_info, 'metadata'):
                    for metadata in field_info.metadata:
                        if isinstance(metadata, DBTypeValidator):
                            db_types[field_name] = metadata.db_type
                            break
            return db_types

        def to_sql_dict(self) -> dict[str, Any]:
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
    create_db_field = None
    DBTypeValidator = None
    Annotated = None
    DBModel = None


__all__ = [
    'PYDANTIC_AVAILABLE',
    'Annotated',
    'DBModel',
    'DBTypeAnnotation',
    'DBTypeValidator',
    'create_db_field',
]
