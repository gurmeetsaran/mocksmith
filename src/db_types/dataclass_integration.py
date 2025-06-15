"""Dataclass integration for database types."""

import sys
from dataclasses import Field, dataclass, field, fields
from typing import Any, Dict, Type, TypeVar, Union, get_args, get_origin, get_type_hints

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from db_types.types.base import DBType

T = TypeVar('T')


class DBTypeDescriptor:
    """Descriptor for database type fields in dataclasses."""

    def __init__(self, db_type: DBType, field_name: str):
        self.db_type = db_type
        self.field_name = field_name
        self.private_name = f'_{field_name}'

    def __get__(self, obj: Any, objtype: Type[Any] = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj: Any, value: Any) -> None:
        # Validate and deserialize
        deserialized = self.db_type.deserialize(value)
        setattr(obj, self.private_name, deserialized)

    def __delete__(self, obj: Any) -> None:
        delattr(obj, self.private_name)


def db_field(db_type: DBType, **kwargs) -> Field:
    """Create a dataclass field with database type validation.
    
    Args:
        db_type: Database type instance
        **kwargs: Additional field arguments
        
    Returns:
        Dataclass field
    """
    # No automatic defaults - let user control this

    # Store db_type in metadata
    metadata = kwargs.get('metadata', {})
    metadata['db_type'] = db_type
    kwargs['metadata'] = metadata

    return field(**kwargs)


def validate_dataclass(cls: Type[T]) -> Type[T]:
    """Decorator to add database type validation to a dataclass.
    
    Usage:
        @validate_dataclass
        @dataclass
        class User:
            name: Annotated[str, VARCHAR(50)]
            age: Annotated[int, INTEGER()]
    """
    if not hasattr(cls, '__dataclass_fields__'):
        raise TypeError(f"{cls.__name__} must be a dataclass")

    # Get type hints with annotations
    hints = get_type_hints(cls, include_extras=True)

    # Process each field
    for field_name, field_type in hints.items():
        if field_name not in cls.__dataclass_fields__:
            continue

        db_type = None
        
        # Handle Optional[T] which is Union[T, None]
        if get_origin(field_type) is Union:
            # Get the non-None type from Optional
            args = get_args(field_type)
            for arg in args:
                if arg is not type(None):
                    field_type = arg
                    break

        # Check if field has Annotated type with DBType
        if get_origin(field_type) is Annotated:
            args = get_args(field_type)
            for arg in args[1:]:  # Skip the first arg which is the type
                if isinstance(arg, DBType):
                    db_type = arg
                    break
                # Handle case where DBTypeValidator is present (when Pydantic is installed)
                elif hasattr(arg, 'db_type') and isinstance(getattr(arg, 'db_type'), DBType):
                    db_type = arg.db_type
                    break

        # Check metadata for db_field usage
        field_obj = cls.__dataclass_fields__[field_name]
        if 'db_type' in field_obj.metadata:
            db_type = field_obj.metadata['db_type']

        # If we found a DBType, add descriptor
        if db_type:
            descriptor = DBTypeDescriptor(db_type, field_name)
            setattr(cls, field_name, descriptor)

            # Store original init BEFORE dataclass modifies it
            if not hasattr(cls, '_original_init_stored'):
                cls._original_init_stored = True
                original_init = cls.__init__
                
                def new_init(self, *args, **kwargs):
                    # Call original dataclass __init__ first
                    original_init(self, *args, **kwargs)
                    
                    # Then validate through descriptors
                    for field_name in self.__dataclass_fields__:
                        if hasattr(type(self), field_name):
                            descriptor = getattr(type(self), field_name)
                            if isinstance(descriptor, DBTypeDescriptor):
                                # Get the value set by dataclass init
                                value = getattr(self, descriptor.private_name, None)
                                # Validate it through the descriptor
                                setattr(self, field_name, value)
                
                cls.__init__ = new_init

    # Add helper methods
    def get_db_types(self) -> Dict[str, DBType]:
        """Get all database type fields."""
        result = {}
        for field_name in self.__dataclass_fields__:
            descriptor = getattr(type(self), field_name, None)
            if isinstance(descriptor, DBTypeDescriptor):
                result[field_name] = descriptor.db_type
        return result

    def to_sql_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with SQL-compatible values."""
        result = {}
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            descriptor = getattr(type(self), field_name, None)

            if isinstance(descriptor, DBTypeDescriptor):
                result[field_name] = descriptor.db_type.serialize(value)
            else:
                result[field_name] = value

        return result

    def validate_all(self) -> None:
        """Validate all fields."""
        for field_name in self.__dataclass_fields__:
            descriptor = getattr(type(self), field_name, None)
            if isinstance(descriptor, DBTypeDescriptor):
                value = getattr(self, field_name)
                descriptor.db_type.validate(value)

    cls.get_db_types = get_db_types
    cls.to_sql_dict = to_sql_dict
    cls.validate_all = validate_all

    return cls


# Base dataclass with DB type support
@dataclass
class DBDataclass:
    """Base dataclass with database type support."""

    def __post_init__(self):
        """Validate all fields after initialization."""
        if hasattr(self, 'validate_all'):
            self.validate_all()

    def get_db_types(self) -> Dict[str, DBType]:
        """Get all database type fields."""
        return {}

    def to_sql_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with SQL-compatible values."""
        return {}

    def validate_all(self) -> None:
        """Validate all fields."""
        pass


__all__ = [
    'DBDataclass',
    'DBTypeDescriptor',
    'db_field',
    'validate_dataclass',
]
