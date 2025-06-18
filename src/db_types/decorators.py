"""Decorators for enhancing classes with mock functionality."""

from typing import Callable, Type, TypeVar, Union, overload

from db_types.mock_builder import MockBuilder
from db_types.mock_factory import mock_factory

T = TypeVar("T")


@overload
def mockable(cls: Type[T]) -> Type[T]:
    ...


@overload
def mockable(*, builder: bool = True) -> Callable[[Type[T]], Type[T]]:
    ...


def mockable(cls: Type[T] = None, *, builder: bool = True) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """Decorator that adds mock generation capabilities to a class.
    
    This decorator adds two class methods:
    - mock(**overrides): Generate a mock instance with optional field overrides
    - mock_builder(): Get a type-safe builder for generating mocks
    
    Args:
        cls: The class to decorate (when used without parentheses)
        builder: Whether to add the mock_builder method (default: True)
        
    Returns:
        Decorated class with mock methods
        
    Example:
        @mockable
        @dataclass
        class User:
            name: str
            email: str
            
        # Using mock() method
        user = User.mock(name="John Doe")
        
        # Using builder pattern
        user = User.mock_builder().with_name("John Doe").build()
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Add mock() class method
        @classmethod
        def mock(cls, **overrides):
            """Generate a mock instance with optional field overrides."""
            return mock_factory(cls, **overrides)

        cls.mock = mock

        # Add mock_builder() class method if requested
        if builder:
            @classmethod
            def mock_builder(cls) -> MockBuilder[cls]:
                """Get a type-safe builder for generating mocks."""
                return MockBuilder(cls)

            cls.mock_builder = mock_builder

        return cls

    # Handle both @mockable and @mockable() syntax
    if cls is None:
        return decorator
    else:
        return decorator(cls)
