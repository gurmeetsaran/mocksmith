"""Tests for mock data generation in string types using V3 pattern."""

import pytest

from mocksmith import Char, Text, Varchar


class TestVARCHARMock:
    """Test mock generation for VARCHAR type."""

    def test_varchar_mock_respects_length(self):
        """Mock data should respect length constraint."""
        VarcharType = Varchar(10)
        mock_value = VarcharType.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) <= 10

    def test_varchar_mock_various_lengths(self):
        """Test mock generation for different lengths."""
        # Short VARCHAR
        ShortType = Varchar(5)
        short_mock = ShortType.mock()
        assert len(short_mock) <= 5

        # Medium VARCHAR
        MediumType = Varchar(50)
        medium_mock = MediumType.mock()
        assert len(medium_mock) <= 50

        # Long VARCHAR
        LongType = Varchar(500)
        long_mock = LongType.mock()
        assert len(long_mock) <= 500

    def test_varchar_mock_generates_different_values(self):
        """Mock should generate different values on each call."""
        VarcharType = Varchar(50)
        values = [VarcharType.mock() for _ in range(10)]

        # Should have at least some unique values
        unique_values = set(values)
        assert len(unique_values) > 5

    def test_varchar_mock_validates(self):
        """Generated mock data should pass validation."""
        VarcharType = Varchar(30)
        mock_value = VarcharType.mock()

        # Should not raise - create instance with mock value
        instance = VarcharType(mock_value)
        assert instance == mock_value

    def test_varchar_mock_with_constraints(self):
        """Mock should respect constraints."""
        # Test with min_length
        MinType = Varchar(50, min_length=10)
        mock_value = MinType.mock()
        assert 10 <= len(mock_value) <= 50

        # Test with startswith
        PrefixType = Varchar(30, startswith="PRD-")
        mock_value = PrefixType.mock()
        assert mock_value.startswith("PRD-")
        assert len(mock_value) <= 30

        # Test with endswith
        SuffixType = Varchar(30, endswith=".com")
        mock_value = SuffixType.mock()
        assert mock_value.endswith(".com")
        assert len(mock_value) <= 30

        # Test with both
        BothType = Varchar(20, startswith="ID-", endswith="-2024")
        mock_value = BothType.mock()
        assert mock_value.startswith("ID-")
        assert mock_value.endswith("-2024")
        assert len(mock_value) <= 20

    def test_varchar_mock_with_transformations(self):
        """Mock should apply transformations."""
        # Test to_lower
        LowerType = Varchar(20, to_lower=True)
        mock_value = LowerType.mock()
        assert mock_value == mock_value.lower()

        # Test to_upper
        UpperType = Varchar(20, to_upper=True)
        mock_value = UpperType.mock()
        assert mock_value == mock_value.upper()


class TestCHARMock:
    """Test mock generation for CHAR type."""

    def test_char_mock_exact_length(self):
        """CHAR mock should always be exact length."""
        CharType = Char(10)
        mock_value = CharType.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) == 10  # Exact length

    def test_char_mock_padding(self):
        """CHAR should pad short values."""
        CharType = Char(5)
        mock_value = CharType.mock()

        # Should be padded to exact length
        assert len(mock_value) == 5

    def test_char_mock_various_lengths(self):
        """Test CHAR mock for different lengths."""
        # Very short CHAR (like country codes)
        ShortType = Char(2)
        short_mock = ShortType.mock()
        assert len(short_mock) == 2

        # Medium CHAR
        MediumType = Char(20)
        medium_mock = MediumType.mock()
        assert len(medium_mock) == 20

    def test_char_mock_validates(self):
        """Generated mock data should pass validation."""
        CharType = Char(15)
        mock_value = CharType.mock()

        # Should not raise - create instance with mock value
        # Note: mock already returns padded value
        instance = CharType(mock_value.rstrip())
        assert len(instance) == 15  # Should be padded

    def test_char_mock_with_constraints(self):
        """Mock should respect constraints."""
        # Test with startswith
        PrefixType = Char(10, startswith="CC-")
        mock_value = PrefixType.mock()
        assert mock_value.startswith("CC-")
        assert len(mock_value) == 10  # Exact length

        # Test with endswith
        SuffixType = Char(8, endswith="-X")
        mock_value = SuffixType.mock()
        assert mock_value.rstrip().endswith("-X")  # Check before padding
        assert len(mock_value) == 8  # Exact length

    def test_char_mock_with_transformations(self):
        """Mock should apply transformations."""
        # Test to_upper
        UpperType = Char(5, to_upper=True)
        mock_value = UpperType.mock()
        assert mock_value.rstrip() == mock_value.rstrip().upper()
        assert len(mock_value) == 5


class TestTEXTMock:
    """Test mock generation for TEXT type."""

    def test_text_mock_no_limit(self):
        """TEXT without limit should generate reasonable text."""
        TextType = Text()
        mock_value = TextType.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) > 0
        assert len(mock_value) <= 1000  # Reasonable default

    def test_text_mock_with_limit(self):
        """TEXT with max_length should respect limit."""
        TextType = Text(max_length=100)
        mock_value = TextType.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) <= 100

    def test_text_mock_various_limits(self):
        """Test TEXT mock with various limits."""
        # Small text
        SmallType = Text(max_length=50)
        small_mock = SmallType.mock()
        assert len(small_mock) <= 50

        # Large text
        LargeType = Text(max_length=2000)
        large_mock = LargeType.mock()
        assert len(large_mock) <= 2000

    def test_text_mock_validates(self):
        """Generated mock data should pass validation."""
        TextType = Text(max_length=200)
        mock_value = TextType.mock()

        # Should not raise - create instance with mock value
        instance = TextType(mock_value)
        assert instance == mock_value

    def test_text_mock_with_min_length(self):
        """Mock should respect min_length."""
        MinType = Text(min_length=100)
        mock_value = MinType.mock()
        assert len(mock_value) >= 100

        # With both min and max
        RangeType = Text(min_length=50, max_length=200)
        mock_value = RangeType.mock()
        assert 50 <= len(mock_value) <= 200

    def test_text_mock_with_constraints(self):
        """Mock should respect constraints."""
        # Test with startswith
        PrefixType = Text(startswith="Article: ")
        mock_value = PrefixType.mock()
        assert mock_value.startswith("Article: ")

        # Test with endswith
        SuffixType = Text(endswith=" - END")
        mock_value = SuffixType.mock()
        assert mock_value.endswith(" - END")

        # Test with both and length limits
        ComplexType = Text(
            min_length=50, max_length=100, startswith="Report: ", endswith=" - Complete"
        )
        mock_value = ComplexType.mock()
        assert mock_value.startswith("Report: ")
        assert mock_value.endswith(" - Complete")
        assert 50 <= len(mock_value) <= 100

    def test_text_mock_with_transformations(self):
        """Mock should apply transformations."""
        # Test to_lower
        LowerType = Text(to_lower=True)
        mock_value = LowerType.mock()
        assert mock_value == mock_value.lower()

        # Test to_upper
        UpperType = Text(to_upper=True)
        mock_value = UpperType.mock()
        assert mock_value == mock_value.upper()


class TestMockImportError:
    """Test behavior when faker is not installed."""

    def test_import_error_message(self, monkeypatch):
        """Should provide helpful error when faker not installed."""
        # Simulate faker not being installed
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "faker" or name.startswith("faker."):
                raise ImportError("No module named 'faker'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        VarcharType = Varchar(10)
        with pytest.raises(ImportError) as exc_info:
            VarcharType.mock()

        assert "faker library is required for mock generation" in str(exc_info.value)
