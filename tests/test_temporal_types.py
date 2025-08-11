"""Tests for V3 temporal database types."""

from datetime import date, datetime, time, timezone

import pytest

from mocksmith.types.temporal import _DATE as DATE
from mocksmith.types.temporal import _DATETIME as DATETIME
from mocksmith.types.temporal import _TIME as TIME
from mocksmith.types.temporal import _TIMESTAMP as TIMESTAMP
from mocksmith.types.temporal import (
    Date,
    DateTime,
    Time,
    Timestamp,
)


class TestDATE:
    def test_direct_instantiation(self):
        # Test with components
        d1 = DATE(2024, 3, 15)
        assert d1.year == 2024
        assert d1.month == 3
        assert d1.day == 15
        assert str(d1) == "2024-03-15"

        # Test with string
        d2 = DATE("2024-03-15")
        assert d2 == d1

        # Test with date object
        d3 = DATE(date(2024, 3, 15))
        assert d3 == d1

        # Test with datetime object
        d4 = DATE(datetime(2024, 3, 15, 14, 30, 45))  # noqa: DTZ001
        assert d4 == d1

    def test_factory_function(self):
        DateType = Date()
        assert DateType == DATE

        # Can use the returned class
        d = DateType(2024, 3, 15)
        assert d.year == 2024

    def test_validation_failure(self):
        with pytest.raises(ValueError, match="Value cannot be None"):
            DATE(None)

        with pytest.raises(ValueError, match="Invalid date string"):
            DATE("not a date")

        with pytest.raises(ValueError, match="Invalid date components"):
            DATE(2024, 13, 1)  # Invalid month

    def test_serialize(self):
        d = DATE(2024, 3, 15)
        assert d.serialize() == "2024-03-15"

    def test_sql_type(self):
        d = DATE(2024, 1, 1)
        assert d.sql_type == "DATE"

    def test_validate_class_method(self):
        result = DATE.validate("2024-03-15")
        assert isinstance(result, date)
        assert result == date(2024, 3, 15)

    def test_mock_generation(self):
        mocked = DATE.mock()
        assert isinstance(mocked, date)


class TestTIME:
    def test_direct_instantiation(self):
        # Test with components
        t1 = TIME(14, 30, 45)
        assert t1.hour == 14
        assert t1.minute == 30
        assert t1.second == 45

        # Test with string
        t2 = TIME("14:30:45")
        assert t2 == t1

        # Test with time object
        t3 = TIME(time(14, 30, 45))
        assert t3 == t1

        # Test with datetime object
        t4 = TIME(datetime(2024, 3, 15, 14, 30, 45))  # noqa: DTZ001
        assert t4.hour == 14
        assert t4.minute == 30

    def test_factory_function(self):
        # Default precision
        TimeType = Time()
        t = TimeType(14, 30, 45, 123456)
        assert t.microsecond == 123456

        # With precision
        TimeType2 = Time(precision=3)
        t2 = TimeType2(14, 30, 45, 123456)
        assert t2.microsecond == 123000  # Truncated to milliseconds

    def test_precision_truncation(self):
        TimeType = Time(precision=0)
        t = TimeType(14, 30, 45, 123456)
        assert t.microsecond == 0

        TimeType2 = Time(precision=3)
        t2 = TimeType2("14:30:45.123456")
        assert t2.microsecond == 123000

    def test_sql_type(self):
        TimeType = Time(precision=3)
        t = TimeType(14, 30, 45)
        assert t.sql_type == "TIME(3)"

        TimeType2 = Time()
        t2 = TimeType2(14, 30, 45)
        assert t2.sql_type == "TIME"

    def test_mock_generation(self):
        TimeType = Time()
        mocked = TimeType.mock()
        assert isinstance(mocked, time)


class TestDATETIME:
    def test_direct_instantiation(self):
        # Test with components
        dt1 = DATETIME(2024, 3, 15, 14, 30, 45)
        assert dt1.year == 2024
        assert dt1.hour == 14
        assert dt1.tzinfo is None  # DATETIME has no timezone

        # Test with string
        dt2 = DATETIME("2024-03-15T14:30:45")
        assert dt2 == dt1

        # Test with datetime object
        dt3 = DATETIME(datetime(2024, 3, 15, 14, 30, 45))  # noqa: DTZ001
        assert dt3 == dt1

        # Test with date object (time defaults to 00:00:00)
        dt4 = DATETIME(date(2024, 3, 15))
        assert dt4.date() == date(2024, 3, 15)
        assert dt4.time() == time(0, 0, 0)

    def test_factory_function(self):
        DateTimeType = DateTime()
        dt = DateTimeType(2024, 3, 15, 14, 30, 45)
        assert dt.year == 2024

        # With precision
        DateTimeType2 = DateTime(precision=3)
        dt2 = DateTimeType2(2024, 3, 15, 14, 30, 45, 123456)
        assert dt2.microsecond == 123000

    def test_no_timezone_allowed(self):
        # DATETIME should reject timezone
        with pytest.raises(ValueError, match="DATETIME type does not support timezone"):
            DATETIME(2024, 3, 15, 14, 30, 45, tzinfo=timezone.utc)

    def test_sql_type(self):
        DateTimeType = DateTime(precision=3)
        dt = DateTimeType(2024, 3, 15)
        assert dt.sql_type == "DATETIME(3)"

    def test_mock_generation(self):
        DateTimeType = DateTime()
        mocked = DateTimeType.mock()
        assert isinstance(mocked, datetime)
        assert mocked.tzinfo is None  # Should not have timezone


class TestTIMESTAMP:
    def test_direct_instantiation(self):
        # Test with components (defaults to UTC)
        ts1 = TIMESTAMP(2024, 3, 15, 14, 30, 45)
        assert ts1.year == 2024
        assert ts1.tzinfo == timezone.utc  # Default timezone

        # Test with string
        ts2 = TIMESTAMP("2024-03-15T14:30:45+00:00")
        assert ts2.tzinfo is not None

        # Test with datetime object
        dt_with_tz = datetime(2024, 3, 15, 14, 30, 45, tzinfo=timezone.utc)
        ts3 = TIMESTAMP(dt_with_tz)
        assert ts3.tzinfo == timezone.utc

    def test_factory_function(self):
        # With timezone (default)
        TimestampType = Timestamp()
        ts = TimestampType(2024, 3, 15)
        assert ts.tzinfo == timezone.utc

        # Without timezone
        TimestampType2 = Timestamp(with_timezone=False)
        ts2 = TimestampType2(2024, 3, 15)
        assert ts2.tzinfo is None

        # With precision
        TimestampType3 = Timestamp(precision=3)
        ts3 = TimestampType3(2024, 3, 15, 14, 30, 45, 123456)
        assert ts3.microsecond == 123000

    def test_timezone_handling(self):
        # With timezone
        TimestampType = Timestamp(with_timezone=True)
        ts = TimestampType(2024, 3, 15)
        assert ts.tzinfo == timezone.utc

        # Without timezone
        TimestampType2 = Timestamp(with_timezone=False)
        ts2 = TimestampType2(2024, 3, 15)
        assert ts2.tzinfo is None

    def test_sql_type(self):
        TimestampType = Timestamp(precision=3, with_timezone=True)
        ts = TimestampType(2024, 3, 15)
        assert ts.sql_type == "TIMESTAMP(3) WITH TIME ZONE"

        TimestampType2 = Timestamp(with_timezone=False)
        ts2 = TimestampType2(2024, 3, 15)
        assert ts2.sql_type == "TIMESTAMP"

    def test_mock_generation(self):
        # With timezone
        TimestampType = Timestamp(with_timezone=True)
        mocked = TimestampType.mock()
        assert isinstance(mocked, datetime)
        assert mocked.tzinfo is not None

        # Without timezone
        TimestampType2 = Timestamp(with_timezone=False)
        mocked2 = TimestampType2.mock()
        assert isinstance(mocked2, datetime)
        assert mocked2.tzinfo is None


class TestPydanticIntegration:
    """Test integration with Pydantic models."""

    def test_temporal_types_with_pydantic(self):
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("Pydantic not available")

        DateType = Date()
        TimeType = Time()
        DateTimeType = DateTime()
        TimestampType = Timestamp()

        class Event(BaseModel):
            event_date: DateType
            start_time: TimeType
            created_at: DateTimeType
            updated_at: TimestampType

        # Test with various inputs
        event = Event(
            event_date="2024-03-15",
            start_time="14:30:00",
            created_at="2024-03-15T14:30:00",
            updated_at="2024-03-15T14:30:00Z",
        )

        assert event.event_date == date(2024, 3, 15)
        assert event.start_time == time(14, 30, 0)
        assert event.created_at == datetime(2024, 3, 15, 14, 30, 0)  # noqa: DTZ001
        assert event.updated_at.tzinfo is not None

    def test_temporal_precision_with_pydantic(self):
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("Pydantic not available")

        TimeType = Time(precision=0)
        DateTimeType = DateTime(precision=3)

        class Schedule(BaseModel):
            meeting_time: TimeType
            deadline: DateTimeType

        schedule = Schedule(
            meeting_time="14:30:45.123456",  # Will be truncated
            deadline="2024-03-15T14:30:45.123456",  # Will be truncated to milliseconds
        )

        assert schedule.meeting_time.microsecond == 0
        assert schedule.deadline.microsecond == 123000
