"""Tests for temporal database types."""

import pytest
from datetime import date, time, datetime, timezone
from db_types.types.temporal import DATE, TIME, TIMESTAMP, DATETIME


class TestDATE:
    def test_creation(self):
        date_type = DATE()
        assert date_type.sql_type == "DATE"
        assert date_type.python_type == date
    
    def test_validation_success(self):
        date_type = DATE()
        date_type.validate(date(2023, 1, 1))
        date_type.validate(datetime(2023, 1, 1, 12, 0))
        date_type.validate("2023-01-01")
    
    def test_validation_failure(self):
        date_type = DATE()
        
        with pytest.raises(ValueError, match="Expected date"):
            date_type.validate(123)
        
        with pytest.raises(ValueError, match="Invalid date"):
            date_type.validate("not a date")
    
    def test_serialize(self):
        date_type = DATE()
        assert date_type.serialize(date(2023, 1, 1)) == "2023-01-01"
        assert date_type.serialize(datetime(2023, 1, 1, 12, 0)) == "2023-01-01"
        assert date_type.serialize("2023-01-01") == "2023-01-01"
    
    def test_deserialize(self):
        date_type = DATE()
        result = date_type.deserialize("2023-01-01")
        assert isinstance(result, date)
        assert result == date(2023, 1, 1)
        
        # From datetime
        result = date_type.deserialize(datetime(2023, 1, 1, 12, 0))
        assert result == date(2023, 1, 1)


class TestTIME:
    def test_creation(self):
        time_type = TIME()
        assert time_type.sql_type == "TIME"
        assert time_type.precision == 6
    
    def test_with_precision(self):
        time_type = TIME(precision=3)
        assert time_type.sql_type == "TIME(3)"
    
    def test_validation(self):
        time_type = TIME()
        time_type.validate(time(12, 30, 45))
        time_type.validate("12:30:45")
        time_type.validate(datetime.now())
    
    def test_precision_truncation(self):
        time_type = TIME(precision=0)
        result = time_type.serialize(time(12, 30, 45, 123456))
        assert result == "12:30:45"  # microseconds truncated
        
        time_type = TIME(precision=3)
        result = time_type.serialize(time(12, 30, 45, 123456))
        assert result == "12:30:45.123000"  # truncated to milliseconds


class TestTIMESTAMP:
    def test_creation(self):
        ts = TIMESTAMP()
        assert ts.sql_type == "TIMESTAMP WITH TIME ZONE"
        assert ts.with_timezone is True
        assert ts.precision == 6
    
    def test_without_timezone(self):
        ts = TIMESTAMP(with_timezone=False)
        assert ts.sql_type == "TIMESTAMP"
    
    def test_timezone_validation(self):
        ts = TIMESTAMP(with_timezone=True)
        
        # Should fail with naive datetime
        with pytest.raises(ValueError, match="timezone-aware"):
            ts.validate(datetime(2023, 1, 1, 12, 0))
        
        # Should succeed with aware datetime
        ts.validate(datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc))
    
    def test_serialize(self):
        ts = TIMESTAMP(with_timezone=False)
        dt = datetime(2023, 1, 1, 12, 30, 45, 123456)
        assert ts.serialize(dt) == "2023-01-01T12:30:45.123456"
        
        # From date
        assert ts.serialize(date(2023, 1, 1)) == "2023-01-01T00:00:00"
    
    def test_precision(self):
        ts = TIMESTAMP(precision=2)
        dt = datetime(2023, 1, 1, 12, 30, 45, 123456)
        result = ts.serialize(dt)
        assert result == "2023-01-01T12:30:45.120000"


class TestDATETIME:
    def test_alias(self):
        dt = DATETIME()
        assert dt.sql_type == "DATETIME"
        assert dt.with_timezone is False
        assert isinstance(dt, TIMESTAMP)