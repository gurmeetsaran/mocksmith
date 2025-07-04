"""Tests for string database types."""

import pytest

from mocksmith.types.string import CHAR, TEXT, VARCHAR


class TestVARCHAR:
    def test_creation(self):
        vchar = VARCHAR(50)
        assert vchar.length == 50
        assert vchar.sql_type == "VARCHAR(50)"
        assert vchar.python_type is str

    def test_startswith_endswith_length_validation(self):
        # Test that startswith/endswith can't be longer than the field
        with pytest.raises(ValueError, match="startswith .* is too long"):
            VARCHAR(5, startswith="TOOLONG")

        with pytest.raises(ValueError, match="endswith .* is too long"):
            VARCHAR(5, endswith="TOOLONG")

        with pytest.raises(ValueError, match="startswith \\+ endswith is too long"):
            VARCHAR(10, startswith="START", endswith="FINISH")

    def test_startswith_endswith_constraints(self):
        # Test startswith constraint
        vchar = VARCHAR(20, startswith="ORD-")
        vchar.validate("ORD-12345")
        with pytest.raises(
            ValueError,
            match=(
                "(String should match pattern|String must start with|String must end with|"
                "Text must start with|Text must end with)"
            ),
        ):
            vchar.validate("INV-12345")

        # Test endswith constraint
        vchar = VARCHAR(50, endswith="@example.com")
        vchar.validate("user@example.com")
        with pytest.raises(
            ValueError,
            match=(
                "(String should match pattern|String must start with|String must end with|"
                "Text must start with|Text must end with)"
            ),
        ):
            vchar.validate("user@other.com")

        # Test both startswith and endswith
        vchar = VARCHAR(20, startswith="INV-", endswith="-2024")
        vchar.validate("INV-001-2024")
        with pytest.raises(
            ValueError,
            match=(
                "(String should match pattern|String must start with|String must end with|"
                "Text must start with|Text must end with)"
            ),
        ):
            vchar.validate("ORD-001-2024")
        with pytest.raises(
            ValueError,
            match=(
                "(String should match pattern|String must start with|String must end with|"
                "Text must start with|Text must end with)"
            ),
        ):
            vchar.validate("INV-001-2023")

    def test_validation_success(self):
        vchar = VARCHAR(10)
        vchar.validate("hello")
        vchar.validate("")
        vchar.validate(None)  # nullable by default

    def test_validation_failure(self):
        vchar = VARCHAR(5)
        with pytest.raises(
            ValueError,
            match=(
                "(String should have at most|String length.*exceeds maximum|"
                "Text length.*exceeds maximum)"
            ),
        ):
            vchar.validate("too long string")

        with pytest.raises(ValueError, match="Input should be a valid string"):
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

    def test_startswith_endswith_length_validation(self):
        # Test that startswith/endswith can't be longer than the field
        with pytest.raises(ValueError, match="startswith .* is too long"):
            CHAR(5, startswith="TOOLONG")

        with pytest.raises(ValueError, match="endswith .* is too long"):
            CHAR(5, endswith="TOOLONG")

    def test_startswith_endswith_constraints(self):
        # Test startswith constraint
        char = CHAR(8, startswith="PRD-")
        char.validate("PRD-1234")
        with pytest.raises(
            ValueError,
            match=(
                "(String should match pattern|String must start with|String must end with|"
                "Text must start with|Text must end with)"
            ),
        ):
            char.validate("ABC-1234")

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

        with pytest.raises(
            ValueError,
            match=(
                "(String should have at most|String length.*exceeds maximum|"
                "Text length.*exceeds maximum)"
            ),
        ):
            char.validate("abcd")


class TestTEXT:
    def test_creation(self):
        text = TEXT()
        assert text.sql_type == "TEXT"
        assert text.max_length is None

    def test_startswith_endswith_length_validation(self):
        # Test that startswith/endswith can't be longer than max_length
        with pytest.raises(ValueError, match="startswith .* is too long"):
            TEXT(max_length=5, startswith="TOOLONG")

        with pytest.raises(ValueError, match="endswith .* is too long"):
            TEXT(max_length=5, endswith="TOOLONG")

    def test_startswith_endswith_constraints(self):
        # Test startswith constraint
        text = TEXT(startswith="Review: ")
        text.validate("Review: Great product!")
        with pytest.raises(
            ValueError,
            match=(
                "(String should match pattern|String must start with|String must end with|"
                "Text must start with|Text must end with)"
            ),
        ):
            text.validate("This is a great product!")

        # Test endswith constraint
        text = TEXT(endswith=" - END")
        text.validate("This is the content - END")
        with pytest.raises(
            ValueError,
            match=(
                "(String should match pattern|String must start with|String must end with|"
                "Text must start with|Text must end with)"
            ),
        ):
            text.validate("This is the content")

        # Test both with length constraints
        text = TEXT(min_length=20, max_length=100, startswith="Note: ")
        text.validate("Note: This is a valid note with enough content.")
        with pytest.raises(
            ValueError,
            match=(
                "(String should have at least|String length.*is less than minimum|"
                "Text length.*is less than minimum)"
            ),
        ):
            text.validate("Note: Too short")

    def test_with_max_length(self):
        text = TEXT(max_length=1000)
        text.validate("x" * 1000)

        with pytest.raises(
            ValueError,
            match=(
                "(String should have at most|String length.*exceeds maximum|"
                "Text length.*exceeds maximum)"
            ),
        ):
            text.validate("x" * 1001)

    def test_serialize_deserialize(self):
        text = TEXT()
        long_text = "x" * 10000
        assert text.serialize(long_text) == long_text
        assert text.deserialize(long_text) == long_text
