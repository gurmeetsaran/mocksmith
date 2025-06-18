"""Tests for mock data generation in string types."""

import pytest

from db_types import VARCHAR, CHAR, TEXT


class TestVARCHARMock:
    """Test mock generation for VARCHAR type."""
    
    def test_varchar_mock_respects_length(self):
        """Mock data should respect length constraint."""
        varchar = VARCHAR(10)
        mock_value = varchar.mock()
        
        assert isinstance(mock_value, str)
        assert len(mock_value) <= 10
        
    def test_varchar_mock_various_lengths(self):
        """Test mock generation for different lengths."""
        # Short VARCHAR
        short = VARCHAR(5)
        short_mock = short.mock()
        assert len(short_mock) <= 5
        
        # Medium VARCHAR
        medium = VARCHAR(50)
        medium_mock = medium.mock()
        assert len(medium_mock) <= 50
        
        # Long VARCHAR
        long_var = VARCHAR(500)
        long_mock = long_var.mock()
        assert len(long_mock) <= 500
    
    def test_varchar_mock_generates_different_values(self):
        """Mock should generate different values on each call."""
        varchar = VARCHAR(50)
        values = [varchar.mock() for _ in range(10)]
        
        # Should have at least some unique values
        unique_values = set(values)
        assert len(unique_values) > 5
    
    def test_varchar_mock_validates(self):
        """Generated mock data should pass validation."""
        varchar = VARCHAR(30)
        mock_value = varchar.mock()
        
        # Should not raise
        varchar.validate(mock_value)


class TestCHARMock:
    """Test mock generation for CHAR type."""
    
    def test_char_mock_exact_length(self):
        """CHAR mock should always be exact length."""
        char = CHAR(10)
        mock_value = char.mock()
        
        assert isinstance(mock_value, str)
        assert len(mock_value) == 10  # Exact length
    
    def test_char_mock_padding(self):
        """CHAR should pad short values."""
        char = CHAR(5)
        mock_value = char.mock()
        
        # Should be padded to exact length
        assert len(mock_value) == 5
        
    def test_char_mock_various_lengths(self):
        """Test CHAR mock for different lengths."""
        # Very short CHAR (like country codes)
        short = CHAR(2)
        short_mock = short.mock()
        assert len(short_mock) == 2
        
        # Medium CHAR
        medium = CHAR(20)
        medium_mock = medium.mock()
        assert len(medium_mock) == 20
    
    def test_char_mock_validates(self):
        """Generated mock data should pass validation."""
        char = CHAR(15)
        mock_value = char.mock()
        
        # Should not raise
        char.validate(mock_value.rstrip())  # Remove padding for validation


class TestTEXTMock:
    """Test mock generation for TEXT type."""
    
    def test_text_mock_no_limit(self):
        """TEXT without limit should generate reasonable text."""
        text = TEXT()
        mock_value = text.mock()
        
        assert isinstance(mock_value, str)
        assert len(mock_value) > 0
        assert len(mock_value) <= 1000  # Reasonable default
    
    def test_text_mock_with_limit(self):
        """TEXT with max_length should respect limit."""
        text = TEXT(max_length=100)
        mock_value = text.mock()
        
        assert isinstance(mock_value, str)
        assert len(mock_value) <= 100
    
    def test_text_mock_various_limits(self):
        """Test TEXT mock with various limits."""
        # Small text
        small = TEXT(max_length=50)
        small_mock = small.mock()
        assert len(small_mock) <= 50
        
        # Large text
        large = TEXT(max_length=2000)
        large_mock = large.mock()
        assert len(large_mock) <= 2000
    
    def test_text_mock_validates(self):
        """Generated mock data should pass validation."""
        text = TEXT(max_length=200)
        mock_value = text.mock()
        
        # Should not raise
        text.validate(mock_value)


class TestMockImportError:
    """Test behavior when faker is not installed."""
    
    def test_import_error_message(self, monkeypatch):
        """Should provide helpful error when faker not installed."""
        # Simulate faker not being installed
        import sys
        monkeypatch.setitem(sys.modules, 'faker', None)
        
        varchar = VARCHAR(10)
        with pytest.raises(ImportError) as exc_info:
            varchar.mock()
        
        assert "faker is required" in str(exc_info.value)
        assert "pip install python-db-types[mock]" in str(exc_info.value)