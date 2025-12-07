"""Tests for string database types using V3 pattern."""

import pytest

from mocksmith import Char, Text, Varchar


class TestVARCHAR:
    def test_creation(self):
        # V3: Create a type class with factory function
        VarcharType = Varchar(50)
        assert VarcharType._length == 50
        assert VarcharType.SQL_TYPE == "VARCHAR"

        # Create an instance
        value = VarcharType("test")
        assert isinstance(value, str)
        assert value == "test"
        assert value.sql_type == "VARCHAR(50)"

    def test_startswith_endswith_length_validation(self):
        # Test that startswith/endswith can't be longer than the field
        with pytest.raises(ValueError, match=r"startswith .* is too long"):
            Varchar(5, startswith="TOOLONG")

        with pytest.raises(ValueError, match=r"endswith .* is too long"):
            Varchar(5, endswith="TOOLONG")

        with pytest.raises(ValueError, match="startswith \\+ endswith is too long"):
            Varchar(10, startswith="START", endswith="FINISH")

    def test_startswith_endswith_constraints(self):
        # Test startswith constraint
        VarcharType = Varchar(20, startswith="ORD-")
        # Valid value
        value = VarcharType("ORD-12345")
        assert value == "ORD-12345"
        # Invalid value
        with pytest.raises(ValueError, match="String must start with"):
            VarcharType("INV-12345")

        # Test endswith constraint
        EmailType = Varchar(50, endswith="@example.com")
        # Valid value
        email = EmailType("user@example.com")
        assert email == "user@example.com"
        # Invalid value
        with pytest.raises(ValueError, match="String must end with"):
            EmailType("user@other.com")

        # Test both startswith and endswith
        InvoiceType = Varchar(20, startswith="INV-", endswith="-2024")
        # Valid value
        invoice = InvoiceType("INV-001-2024")
        assert invoice == "INV-001-2024"
        # Invalid prefix
        with pytest.raises(ValueError, match="String must start with"):
            InvoiceType("ORD-001-2024")
        # Invalid suffix
        with pytest.raises(ValueError, match="String must end with"):
            InvoiceType("INV-001-2023")

    def test_validation_success(self):
        VarcharType = Varchar(10)
        # Valid values should work
        value1 = VarcharType("hello")
        assert value1 == "hello"
        value2 = VarcharType("")
        assert value2 == ""
        # None is not allowed in V3 - types extend native Python types
        with pytest.raises(ValueError, match="Value cannot be None"):
            VarcharType(None)

    def test_validation_failure(self):
        VarcharType = Varchar(5)
        # String too long
        with pytest.raises(ValueError, match=r"String length.*exceeds maximum"):
            VarcharType("too long string")

        # Numbers are converted to string in V3
        value = VarcharType(123)
        assert value == "123"
        assert isinstance(value, str)

    def test_nullable_serialization(self):
        # V3: None values are not allowed - types extend native Python types
        VarcharType = Varchar(10)
        with pytest.raises(ValueError, match="Value cannot be None"):
            VarcharType(None)

    def test_serialize(self):
        VarcharType = Varchar(10)
        value = VarcharType("hello")
        # V3: The value IS a string, serialize method for compatibility
        assert value.serialize() == "hello"
        assert str(value) == "hello"

    def test_deserialize(self):
        VarcharType = Varchar(10)
        # V3: No separate deserialize - just create instance
        value1 = VarcharType("hello")
        assert value1 == "hello"
        # Numbers are converted to string
        value2 = VarcharType(123)
        assert value2 == "123"

    def test_transformations(self):
        # Test to_lower transformation
        LowerType = Varchar(20, to_lower=True)
        value = LowerType("HELLO WORLD")
        assert value == "hello world"

        # Test to_upper transformation
        UpperType = Varchar(20, to_upper=True)
        value = UpperType("hello world")
        assert value == "HELLO WORLD"

        # Test strip_whitespace
        StripType = Varchar(20, strip_whitespace=True)
        value = StripType("  hello  ")
        assert value == "hello"

    def test_min_length(self):
        # Test min_length constraint
        MinType = Varchar(20, min_length=5)

        # Valid length
        value = MinType("hello")
        assert value == "hello"

        # Too short
        with pytest.raises(ValueError, match=r"String length.*is less than minimum"):
            MinType("hi")


class TestCHAR:
    def test_creation(self):
        # V3: Create a type class with factory function
        CharType = Char(10)
        assert CharType._length == 10
        assert CharType.SQL_TYPE == "CHAR"

        # Create an instance - CHAR pads to fixed length
        value = CharType("test")
        assert isinstance(value, str)
        assert value == "test      "  # Padded to 10 chars
        assert value.sql_type == "CHAR(10)"

    def test_startswith_endswith_length_validation(self):
        # Test that startswith/endswith can't be longer than the field
        with pytest.raises(ValueError, match=r"startswith .* is too long"):
            Char(5, startswith="TOOLONG")

        with pytest.raises(ValueError, match=r"endswith .* is too long"):
            Char(5, endswith="TOOLONG")

    def test_startswith_endswith_constraints(self):
        # Test startswith constraint
        CharType = Char(8, startswith="PRD-")
        # Valid value - will be padded
        value = CharType("PRD-1234")
        assert value == "PRD-1234"
        # Invalid value
        with pytest.raises(ValueError, match="String must start with"):
            CharType("ABC-1234")

    def test_serialize_padding(self):
        CharType = Char(5)
        value1 = CharType("hi")
        assert value1 == "hi   "  # Padded to 5 chars
        assert value1.serialize() == "hi   "  # serialize maintains padding

        value2 = CharType("hello")
        assert value2 == "hello"
        assert value2.serialize() == "hello"

    def test_deserialize_stripping(self):
        CharType = Char(5)
        # V3: CHAR automatically handles padding on creation
        value1 = CharType("hi   ")  # Input with trailing spaces
        assert value1 == "hi   "  # CHAR maintains fixed length

        value2 = CharType("hello")
        assert value2 == "hello"

    def test_validation(self):
        CharType = Char(3)
        # Valid value
        value = CharType("abc")
        assert value == "abc"

        # Too long
        with pytest.raises(ValueError, match=r"String length.*exceeds maximum"):
            CharType("abcd")

    def test_transformations(self):
        # Test to_upper transformation
        UpperType = Char(5, to_upper=True)
        value = UpperType("abc")
        assert value == "ABC  "  # Uppercased and padded

        # Test to_lower transformation
        LowerType = Char(5, to_lower=True)
        value = LowerType("ABC")
        assert value == "abc  "  # Lowercased and padded


class TestTEXT:
    def test_creation(self):
        # V3: Create a type class with factory function
        TextType = Text()
        assert TextType._max_length is None
        assert TextType.SQL_TYPE == "TEXT"

        # Create an instance
        value = TextType("long text content")
        assert isinstance(value, str)
        assert value == "long text content"
        assert value.sql_type == "TEXT"

    def test_startswith_endswith_length_validation(self):
        # Test that startswith/endswith can't be longer than max_length
        with pytest.raises(ValueError, match=r"startswith .* is too long"):
            Text(max_length=5, startswith="TOOLONG")

        with pytest.raises(ValueError, match=r"endswith .* is too long"):
            Text(max_length=5, endswith="TOOLONG")

    def test_startswith_endswith_constraints(self):
        # Test startswith constraint
        ReviewType = Text(startswith="Review: ")
        # Valid value
        review = ReviewType("Review: Great product!")
        assert review == "Review: Great product!"
        # Invalid value
        with pytest.raises(ValueError, match="Text must start with"):
            ReviewType("This is a great product!")

        # Test endswith constraint
        EndType = Text(endswith=" - END")
        # Valid value
        content = EndType("This is the content - END")
        assert content == "This is the content - END"
        # Invalid value
        with pytest.raises(ValueError, match="Text must end with"):
            EndType("This is the content")

        # Test both with length constraints
        NoteType = Text(min_length=20, max_length=100, startswith="Note: ")
        # Valid value
        note = NoteType("Note: This is a valid note with enough content.")
        assert note.startswith("Note: ")
        # Too short
        with pytest.raises(ValueError, match=r"Text length.*is less than minimum"):
            NoteType("Note: Too short")

    def test_with_max_length(self):
        LimitedText = Text(max_length=1000)
        # Valid length
        value = LimitedText("x" * 1000)
        assert len(value) == 1000

        # Too long
        with pytest.raises(ValueError, match=r"Text length.*exceeds maximum"):
            LimitedText("x" * 1001)

    def test_serialize_deserialize(self):
        TextType = Text()
        long_text = "x" * 10000
        value = TextType(long_text)
        assert value == long_text
        assert value.serialize() == long_text
        # V3: No separate deserialize - just create instance
        value2 = TextType(long_text)
        assert value2 == long_text

    def test_min_length(self):
        # Test min_length constraint
        MinText = Text(min_length=100)

        # Valid length
        long_text = "x" * 100
        value = MinText(long_text)
        assert len(value) == 100

        # Too short
        with pytest.raises(ValueError, match=r"Text length.*is less than minimum"):
            MinText("too short")

    def test_transformations(self):
        # Test to_lower transformation
        LowerText = Text(to_lower=True)
        value = LowerText("HELLO WORLD")
        assert value == "hello world"

        # Test to_upper transformation
        UpperText = Text(to_upper=True)
        value = UpperText("hello world")
        assert value == "HELLO WORLD"

        # Test strip_whitespace
        StripText = Text(strip_whitespace=True)
        value = StripText("  hello world  ")
        assert value == "hello world"

    def test_combined_constraints(self):
        # Test multiple constraints together
        ComplexText = Text(
            min_length=50,
            max_length=200,
            startswith="ARTICLE: ",
            to_upper=True,
            strip_whitespace=True,
        )

        # Valid value
        content = (
            "  article: This is a long enough article content that meets all the requirements.  "
        )
        value = ComplexText(content)
        assert value.startswith("ARTICLE: ")
        assert value == value.upper()
        assert 50 <= len(value) <= 200
