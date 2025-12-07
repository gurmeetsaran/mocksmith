"""Tests for V3 boolean and binary database types."""

import pytest

from mocksmith import Binary, Blob, Boolean, VarBinary
from mocksmith.types.binary import _BINARY as BINARY
from mocksmith.types.binary import _BLOB as BLOB
from mocksmith.types.binary import _VARBINARY as VARBINARY
from mocksmith.types.boolean import _BOOLEAN as BOOLEAN


class TestBOOLEAN:
    def test_creation(self):
        # Test direct instantiation
        bool_val = BOOLEAN(True)
        assert bool_val == 1  # True is stored as 1
        assert bool(bool_val) is True
        assert str(bool_val) == "true"

        bool_val2 = BOOLEAN(False)
        assert bool_val2 == 0  # False is stored as 0
        assert bool(bool_val2) is False
        assert str(bool_val2) == "false"

    def test_factory_function(self):
        # Test factory function returns the class
        BoolType = Boolean()
        assert BoolType == BOOLEAN

        # Can use the returned class to create instances
        val = BoolType(True)
        assert bool(val) is True

    def test_validation_success(self):
        # Test various valid inputs
        assert bool(BOOLEAN(True)) is True
        assert bool(BOOLEAN(False)) is False
        assert bool(BOOLEAN(1)) is True
        assert bool(BOOLEAN(0)) is False
        assert bool(BOOLEAN("true")) is True
        assert bool(BOOLEAN("false")) is False
        assert bool(BOOLEAN("yes")) is True
        assert bool(BOOLEAN("no")) is False
        assert bool(BOOLEAN("1")) is True
        assert bool(BOOLEAN("0")) is False
        assert bool(BOOLEAN("t")) is True
        assert bool(BOOLEAN("f")) is False
        assert bool(BOOLEAN("y")) is True
        assert bool(BOOLEAN("n")) is False
        assert bool(BOOLEAN("on")) is True
        assert bool(BOOLEAN("off")) is False

    def test_validation_failure(self):
        with pytest.raises(ValueError, match="Value cannot be None"):
            BOOLEAN(None)

        with pytest.raises(ValueError, match="Invalid boolean string"):
            BOOLEAN("maybe")

    def test_serialize(self):
        # Test serialize method
        val = BOOLEAN(True)
        assert val.serialize() is True

        val2 = BOOLEAN(False)
        assert val2.serialize() is False

    def test_validate_class_method(self):
        # Test the validate class method (for compatibility)
        assert BOOLEAN.validate(True) is True
        assert BOOLEAN.validate(False) is False
        assert BOOLEAN.validate("yes") is True
        assert BOOLEAN.validate("no") is False

    def test_repr(self):
        val = BOOLEAN(True)
        assert repr(val) == "BOOLEAN(True)"

        val2 = BOOLEAN(False)
        assert repr(val2) == "BOOLEAN(False)"

    def test_mock_generation(self):
        # Test mock generation
        mocked = BOOLEAN.mock()
        assert isinstance(mocked, bool)
        assert mocked in [True, False]


class TestBINARY:
    def test_direct_instantiation(self):
        # Test direct BINARY instantiation
        binary = BINARY(b"hello")
        assert binary == b"hello"
        assert isinstance(binary, bytes)

        # Test string conversion
        binary2 = BINARY("hello")
        assert binary2 == b"hello"

        # Test hex string
        binary3 = BINARY("0x48656c6c6f")
        assert binary3 == b"Hello"

    def test_factory_function(self):
        # Test factory function
        BinaryType = Binary(10)

        # Create instance with the type
        val = BinaryType(b"test")
        assert val == b"test\x00\x00\x00\x00\x00\x00"  # Padded to 10 bytes
        assert len(val) == 10

    def test_length_validation(self):
        BinaryType = Binary(5)

        # Valid lengths
        val = BinaryType(b"hi")
        assert val == b"hi\x00\x00\x00"

        # Too long should fail
        with pytest.raises(ValueError, match=r"Binary data length .* exceeds fixed length"):
            BinaryType(b"too long")

    def test_serialize(self):
        BinaryType = Binary(5)
        val = BinaryType(b"hi")
        assert val.serialize() == b"hi\x00\x00\x00"

    def test_string_encoding(self):
        BinaryType = Binary(10)
        val = BinaryType("hello")
        assert val == b"hello\x00\x00\x00\x00\x00"

    def test_repr(self):
        val = BINARY(b"test")
        assert repr(val) == "_BINARY(0x74657374)"  # Internal class name

    def test_mock_generation(self):
        BinaryType = Binary(10)
        mocked = BinaryType.mock()
        assert isinstance(mocked, bytes)
        assert len(mocked) == 10


class TestVARBINARY:
    def test_direct_instantiation(self):
        varbinary = VARBINARY(b"hello")
        assert varbinary == b"hello"
        assert isinstance(varbinary, bytes)

    def test_factory_function(self):
        VarBinaryType = VarBinary(100)

        val = VarBinaryType(b"test")
        assert val == b"test"  # No padding for VARBINARY

    def test_max_length_validation(self):
        VarBinaryType = VarBinary(10)

        # Valid length
        val = VarBinaryType(b"hello")
        assert val == b"hello"

        # Too long should fail
        with pytest.raises(ValueError, match=r"Binary data length .* exceeds maximum length"):
            VarBinaryType(b"this is too long")

    def test_no_padding(self):
        VarBinaryType = VarBinary(10)
        val = VarBinaryType(b"hi")
        assert val == b"hi"  # No padding

    def test_hex_conversion(self):
        val = VARBINARY("48656c6c6f")  # "Hello" in hex
        assert val == b"Hello"

    def test_mock_generation(self):
        VarBinaryType = VarBinary(100)
        mocked = VarBinaryType.mock()
        assert isinstance(mocked, bytes)
        assert 1 <= len(mocked) <= 100


class TestBLOB:
    def test_direct_instantiation(self):
        blob = BLOB(b"data")
        assert blob == b"data"
        assert isinstance(blob, bytes)

    def test_factory_function_no_limit(self):
        BlobType = Blob()

        # Can handle large data
        large_data = b"x" * 100000
        val = BlobType(large_data)
        assert val == large_data

    def test_factory_function_with_limit(self):
        BlobType = Blob(max_length=1000)

        # Valid size
        val = BlobType(b"x" * 1000)
        assert len(val) == 1000

        # Too large should fail
        with pytest.raises(ValueError, match=r"Binary data length .* exceeds maximum length"):
            BlobType(b"x" * 1001)

    def test_large_data(self):
        blob = BLOB(b"x" * 1000000)  # 1MB
        assert blob == b"x" * 1000000
        assert blob.serialize() == b"x" * 1000000

    def test_mock_generation(self):
        # Without max_length
        BlobType = Blob()
        mocked = BlobType.mock()
        assert isinstance(mocked, bytes)
        assert 100 <= len(mocked) <= 1000  # Default range

        # With max_length
        BlobType2 = Blob(max_length=500)
        mocked2 = BlobType2.mock()
        assert isinstance(mocked2, bytes)
        assert 1 <= len(mocked2) <= 100  # Limited range


class TestPydanticIntegration:
    """Test integration with Pydantic models."""

    def test_boolean_with_pydantic(self):
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("Pydantic not available")

        BoolType = Boolean()

        class User(BaseModel):
            is_active: BoolType
            is_verified: BoolType

        # Test with various inputs
        user = User(is_active=True, is_verified="false")
        assert user.is_active is True
        assert user.is_verified is False

        user2 = User(is_active="yes", is_verified=0)
        assert user2.is_active is True
        assert user2.is_verified is False

    def test_binary_with_pydantic(self):
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("Pydantic not available")

        BinaryType = Binary(32)
        VarBinaryType = VarBinary(100)

        class Document(BaseModel):
            hash: BinaryType  # Fixed 32 bytes
            thumbnail: VarBinaryType  # Up to 100 bytes

        # Test with various inputs
        doc = Document(hash="0x" + "a" * 64, thumbnail=b"small image data")  # 32 bytes in hex
        assert len(doc.hash) == 32
        assert doc.thumbnail == b"small image data"
