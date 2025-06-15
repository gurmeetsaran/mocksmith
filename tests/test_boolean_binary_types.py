"""Tests for boolean and binary database types."""

import pytest

from db_types.types.binary import BINARY, BLOB, VARBINARY
from db_types.types.boolean import BOOLEAN


class TestBOOLEAN:
    def test_creation(self):
        bool_type = BOOLEAN()
        assert bool_type.sql_type == "BOOLEAN"
        assert bool_type.python_type is bool

    def test_validation_success(self):
        bool_type = BOOLEAN()
        bool_type.validate(True)
        bool_type.validate(False)
        bool_type.validate(1)
        bool_type.validate(0)
        bool_type.validate("true")
        bool_type.validate("false")
        bool_type.validate("yes")
        bool_type.validate("no")

    def test_validation_failure(self):
        bool_type = BOOLEAN()

        with pytest.raises(ValueError, match="Expected boolean"):
            bool_type.validate([])

        with pytest.raises(ValueError, match="Invalid boolean string"):
            bool_type.validate("maybe")

    def test_serialize(self):
        bool_type = BOOLEAN()
        assert bool_type.serialize(True) is True
        assert bool_type.serialize(1) is True
        assert bool_type.serialize("yes") is True
        assert bool_type.serialize("true") is True
        assert bool_type.serialize("1") is True

        assert bool_type.serialize(False) is False
        assert bool_type.serialize(0) is False
        assert bool_type.serialize("no") is False
        assert bool_type.serialize("false") is False
        assert bool_type.serialize("0") is False

    def test_deserialize(self):
        bool_type = BOOLEAN()
        assert bool_type.deserialize(1) is True
        assert bool_type.deserialize(0) is False
        assert bool_type.deserialize("true") is True
        assert bool_type.deserialize("false") is False


class TestBINARY:
    def test_creation(self):
        binary = BINARY(10)
        assert binary.length == 10
        assert binary.sql_type == "BINARY(10)"
        assert binary.python_type is bytes

    def test_validation(self):
        binary = BINARY(5)
        binary.validate(b"hello")
        binary.validate(b"hi")
        binary.validate("text")  # will be encoded

        with pytest.raises(ValueError, match="exceeds maximum"):
            binary.validate(b"too long")

    def test_serialize_padding(self):
        binary = BINARY(5)
        result = binary.serialize(b"hi")
        assert result == b"hi\x00\x00\x00"  # padded with null bytes
        assert len(result) == 5

    def test_deserialize_stripping(self):
        binary = BINARY(5)
        result = binary.deserialize(b"hi\x00\x00\x00")
        assert result == b"hi"  # padding removed

    def test_string_encoding(self):
        binary = BINARY(10)
        result = binary.serialize("hello")
        assert result == b"hello\x00\x00\x00\x00\x00"


class TestVARBINARY:
    def test_creation(self):
        varbinary = VARBINARY(100)
        assert varbinary.max_length == 100
        assert varbinary.sql_type == "VARBINARY(100)"

    def test_no_padding(self):
        varbinary = VARBINARY(10)
        result = varbinary.serialize(b"hi")
        assert result == b"hi"  # no padding

    def test_hex_deserialization(self):
        varbinary = VARBINARY(10)
        result = varbinary.deserialize("48656c6c6f")  # "Hello" in hex
        assert result == b"Hello"


class TestBLOB:
    def test_creation(self):
        blob = BLOB()
        assert blob.sql_type == "BLOB"
        assert blob.max_length is None

    def test_with_max_length(self):
        blob = BLOB(max_length=1000)
        blob.validate(b"x" * 1000)

        with pytest.raises(ValueError, match="exceeds maximum"):
            blob.validate(b"x" * 1001)

    def test_large_data(self):
        blob = BLOB()
        large_data = b"x" * 1000000  # 1MB
        assert blob.serialize(large_data) == large_data
        assert blob.deserialize(large_data) == large_data
