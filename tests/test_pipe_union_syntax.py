"""Tests for Python 3.10+ pipe union syntax (X | Y) with mockable annotations."""

# ruff: noqa: E402
import sys

import pytest

# Skip all tests if Python < 3.10 (pipe syntax not available)
if sys.version_info < (3, 10):
    pytest.skip("Pipe union syntax requires Python 3.10+", allow_module_level=True)

# Skip Pydantic tests if not installed
pydantic = pytest.importorskip("pydantic", minversion="2.0")

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel

from mocksmith import BigInt, DateTime, Integer, Timestamp, Varchar, mockable


class TestPipeUnionSyntax:
    """Test that mockable annotations work with Python 3.10+ pipe union syntax."""

    def test_pydantic_optional_with_pipe_syntax(self):
        """Test optional fields using pipe syntax in Pydantic models."""

        @mockable
        class UserModel(BaseModel):
            name: Annotated[str, Varchar(50)]  # Required
            email: Annotated[str, Varchar(100)] | None  # Optional with pipe
            age: Annotated[int, Integer()] | None  # Optional integer

        # Generate multiple instances
        has_email_none = False
        has_email_value = False
        has_age_none = False
        has_age_value = False

        for _ in range(30):
            user = UserModel.mock()

            # Required field should always have value
            assert user.name is not None
            assert isinstance(user.name, str)
            assert len(user.name) <= 50

            # Optional fields should sometimes be None
            if user.email is None:
                has_email_none = True
            else:
                has_email_value = True
                assert isinstance(user.email, str)
                assert len(user.email) <= 100

            if user.age is None:
                has_age_none = True
            else:
                has_age_value = True
                assert isinstance(user.age, int)

            if all([has_email_none, has_email_value, has_age_none, has_age_value]):
                break

        # Should see both None and non-None values
        assert has_email_value, "Should generate some non-None email values"
        assert has_age_value, "Should generate some non-None age values"

    def test_dataclass_optional_with_pipe_syntax(self):
        """Test optional fields using pipe syntax in dataclasses."""

        @mockable
        @dataclass
        class Product:
            name: Annotated[str, Varchar(100)]
            description: Annotated[str, Varchar(500)] | None
            price: Annotated[int, Integer(ge=0)] | None

        # Generate multiple instances
        has_description_none = False
        has_description_value = False

        for _ in range(30):
            product = Product.mock()

            # Required field
            assert product.name is not None
            assert isinstance(product.name, str)
            assert len(product.name) <= 100

            # Optional fields
            if product.description is None:
                has_description_none = True
            else:
                has_description_value = True
                assert isinstance(product.description, str)
                assert len(product.description) <= 500

            if product.price is not None:
                assert isinstance(product.price, int)
                assert product.price >= 0

            if has_description_none and has_description_value:
                break

        assert has_description_value, "Should generate some non-None description values"

    def test_temporal_types_with_pipe_syntax(self):
        """Test temporal types with pipe syntax."""

        @mockable
        class EventModel(BaseModel):
            name: str
            created_at: DateTime() | None
            updated_at: Timestamp() | None

        # Generate instances
        has_created_none = False
        has_created_value = False

        for _ in range(20):
            event = EventModel.mock()

            assert event.name is not None

            if event.created_at is None:
                has_created_none = True
            else:
                has_created_value = True
                assert isinstance(event.created_at, datetime)
                assert event.created_at.tzinfo is None  # DateTime has no timezone

            if event.updated_at is not None:
                assert isinstance(event.updated_at, datetime)
                # Timestamp should have timezone
                assert event.updated_at.tzinfo is not None

            if has_created_none and has_created_value:
                break

        assert has_created_value, "Should generate some non-None created_at values"

    def test_bigint_with_pipe_syntax(self):
        """Test BigInt type with pipe syntax."""

        @mockable
        @dataclass
        class Transaction:
            amount: Annotated[int, Integer()]
            transaction_id: Annotated[int, BigInt()] | None

        # Generate instances
        for _ in range(10):
            txn = Transaction.mock()

            assert isinstance(txn.amount, int)

            if txn.transaction_id is not None:
                assert isinstance(txn.transaction_id, int)
                # BigInt should generate large values
                assert (
                    -9223372036854775808 <= txn.transaction_id <= 9223372036854775807
                ), "BigInt value out of range"

    def test_simple_type_with_pipe_syntax(self):
        """Test simple factory types (no Annotated) with pipe syntax."""

        @mockable
        class SimpleModel(BaseModel):
            # Simple types without Annotated - just the factory function
            user_id: BigInt() | None
            created_at: DateTime() | None
            updated_at: Timestamp() | None
            age: Integer() | None

        # Generate instances
        has_user_id_none = False
        has_user_id_value = False
        has_created_none = False
        has_created_value = False

        for _ in range(30):
            model = SimpleModel.mock()

            # Check BigInt
            if model.user_id is None:
                has_user_id_none = True
            else:
                has_user_id_value = True
                assert isinstance(model.user_id, int)
                # Verify it's in BigInt range
                assert -9223372036854775808 <= model.user_id <= 9223372036854775807

            # Check DateTime
            if model.created_at is None:
                has_created_none = True
            else:
                has_created_value = True
                assert isinstance(model.created_at, datetime)
                assert model.created_at.tzinfo is None  # No timezone for DateTime

            # Check Timestamp
            if model.updated_at is not None:
                assert isinstance(model.updated_at, datetime)
                assert model.updated_at.tzinfo is not None  # Has timezone

            # Check Integer
            if model.age is not None:
                assert isinstance(model.age, int)

            if all([has_user_id_none, has_user_id_value, has_created_none, has_created_value]):
                break

        # Verify we get both None and non-None values
        assert has_user_id_value, "Should generate some non-None user_id values"
        assert has_created_value, "Should generate some non-None created_at values"

    def test_mixed_optional_syntax(self):
        """Test mixing typing.Optional and pipe syntax in same model."""
        from typing import Optional

        @mockable
        class MixedModel(BaseModel):
            field1: Optional[Annotated[str, Varchar(50)]]  # Old style
            field2: Annotated[str, Varchar(50)] | None  # New style
            field3: Annotated[str, Varchar(50)]  # Required

        # Both optional syntaxes should work
        model = MixedModel.mock()

        # Required field always has value
        assert model.field3 is not None

        # Optional fields can be None
        if model.field1 is not None:
            assert len(model.field1) <= 50
        if model.field2 is not None:
            assert len(model.field2) <= 50

    def test_builder_with_pipe_syntax(self):
        """Test builder pattern with pipe syntax optional fields."""

        @mockable
        class UserModel(BaseModel):
            name: Annotated[str, Varchar(50)]
            email: Annotated[str, Varchar(100)] | None

        # Build with explicit None
        user1 = UserModel.mock_builder().with_name("John").with_email(None).build()
        assert user1.name == "John"
        assert user1.email is None

        # Build with value
        user2 = UserModel.mock_builder().with_name("Jane").with_email("jane@example.com").build()
        assert user2.name == "Jane"
        assert user2.email == "jane@example.com"

        # Build without specifying optional field
        user3 = UserModel.mock_builder().with_name("Bob").build()
        assert user3.name == "Bob"
        # email will be randomly generated (can be None or a value)
