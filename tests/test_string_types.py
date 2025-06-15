"""Tests for string database types."""

import pytest

from db_types.types.string import CHAR, TEXT, VARCHAR


class TestVARCHAR:
    def test_creation(self):
        vchar = VARCHAR(50)
        assert vchar.length == 50
        assert vchar.sql_type == "VARCHAR(50)"
        assert vchar.python_type is str

    def test_validation_success(self):
        vchar = VARCHAR(10)
        vchar.validate("hello")
        vchar.validate("")
        vchar.validate(None)  # nullable by default

    def test_validation_failure(self):
        vchar = VARCHAR(5)
        with pytest.raises(ValueError, match="exceeds maximum"):
            vchar.validate("too long string")

        with pytest.raises(ValueError, match="Expected string"):
            vchar.validate(123)

    def test_nullable_serialization(self):
        # NULL values are now allowed by default
        vchar = VARCHAR(10)
        assert vchar.serialize(None) is None

    def test_serialize(self):
        vchar = VARCHAR(10)
        assert vchar.serialize("hello") == "hello"
        assert vchar.serialize(None) is None

    def test_deserialize(self):
        vchar = VARCHAR(10)
        assert vchar.deserialize("hello") == "hello"
        assert vchar.deserialize(None) is None


class TestCHAR:
    def test_creation(self):
        char = CHAR(10)
        assert char.length == 10
        assert char.sql_type == "CHAR(10)"

    def test_serialize_padding(self):
        char = CHAR(5)
        assert char.serialize("hi") == "hi   "  # Padded to 5 chars
        assert char.serialize("hello") == "hello"

    def test_deserialize_stripping(self):
        char = CHAR(5)
        assert char.deserialize("hi   ") == "hi"  # Trailing spaces stripped
        assert char.deserialize("hello") == "hello"

    def test_validation(self):
        char = CHAR(3)
        char.validate("abc")

        with pytest.raises(ValueError, match="exceeds maximum"):
            char.validate("abcd")


class TestTEXT:
    def test_creation(self):
        text = TEXT()
        assert text.sql_type == "TEXT"
        assert text.max_length is None

    def test_with_max_length(self):
        text = TEXT(max_length=1000)
        text.validate("x" * 1000)

        with pytest.raises(ValueError, match="exceeds maximum"):
            text.validate("x" * 1001)

    def test_serialize_deserialize(self):
        text = TEXT()
        long_text = "x" * 10000
        assert text.serialize(long_text) == long_text
        assert text.deserialize(long_text) == long_text
