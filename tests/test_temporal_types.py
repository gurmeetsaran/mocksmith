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


class TestDateConstraints:
    """Test Date type with ge, le, gt, lt constraints."""

    def test_date_with_ge_constraint(self):
        """Test Date with ge (greater than or equal) constraint."""

        cutoff = date(2020, 1, 1)
        ConstrainedDate = Date(ge=cutoff)

        # Valid: on cutoff
        d1 = ConstrainedDate(cutoff)
        assert d1 == cutoff

        # Valid: after cutoff
        d2 = ConstrainedDate(date(2023, 5, 15))
        assert d2 == date(2023, 5, 15)

        # Invalid: before cutoff
        with pytest.raises(ValueError, match="Date must be on or after 2020-01-01"):
            ConstrainedDate(date(2019, 12, 31))

    def test_date_with_gt_constraint(self):
        """Test Date with gt (greater than) constraint."""
        cutoff = date(2022, 6, 1)
        ConstrainedDate = Date(gt=cutoff)

        # Valid: after cutoff
        d1 = ConstrainedDate(date(2022, 6, 2))
        assert d1 == date(2022, 6, 2)

        # Invalid: on cutoff (must be strictly greater)
        with pytest.raises(ValueError, match="Date must be after 2022-06-01"):
            ConstrainedDate(cutoff)

        # Invalid: before cutoff
        with pytest.raises(ValueError, match="Date must be after 2022-06-01"):
            ConstrainedDate(date(2022, 5, 31))

    def test_date_with_le_constraint(self):
        """Test Date with le (less than or equal) constraint."""
        cutoff = date(2025, 12, 31)
        ConstrainedDate = Date(le=cutoff)

        # Valid: on cutoff
        d1 = ConstrainedDate(cutoff)
        assert d1 == cutoff

        # Valid: before cutoff
        d2 = ConstrainedDate(date(2023, 1, 1))
        assert d2 == date(2023, 1, 1)

        # Invalid: after cutoff
        with pytest.raises(ValueError, match="Date must be on or before 2025-12-31"):
            ConstrainedDate(date(2026, 1, 1))

    def test_date_with_lt_constraint(self):
        """Test Date with lt (less than) constraint."""
        cutoff = date(2024, 1, 1)
        ConstrainedDate = Date(lt=cutoff)

        # Valid: before cutoff
        d1 = ConstrainedDate(date(2023, 12, 31))
        assert d1 == date(2023, 12, 31)

        # Invalid: on cutoff (must be strictly less)
        with pytest.raises(ValueError, match="Date must be before 2024-01-01"):
            ConstrainedDate(cutoff)

        # Invalid: after cutoff
        with pytest.raises(ValueError, match="Date must be before 2024-01-01"):
            ConstrainedDate(date(2024, 1, 2))

    def test_date_with_range_constraints(self):
        """Test Date with both ge and le constraints (range)."""
        start = date(2020, 1, 1)
        end = date(2025, 12, 31)
        ConstrainedDate = Date(ge=start, le=end)

        # Valid: within range
        d1 = ConstrainedDate(date(2023, 6, 15))
        assert d1 == date(2023, 6, 15)

        # Valid: on boundaries
        d2 = ConstrainedDate(start)
        assert d2 == start
        d3 = ConstrainedDate(end)
        assert d3 == end

        # Invalid: before start
        with pytest.raises(ValueError, match="Date must be on or after 2020-01-01"):
            ConstrainedDate(date(2019, 12, 31))

        # Invalid: after end
        with pytest.raises(ValueError, match="Date must be on or before 2025-12-31"):
            ConstrainedDate(date(2026, 1, 1))

    def test_date_with_strict_range(self):
        """Test Date with gt and lt constraints (exclusive range)."""
        start = date(2020, 1, 1)
        end = date(2025, 12, 31)
        ConstrainedDate = Date(gt=start, lt=end)

        # Valid: strictly between
        d1 = ConstrainedDate(date(2023, 6, 15))
        assert d1 == date(2023, 6, 15)

        # Invalid: on start boundary
        with pytest.raises(ValueError, match="Date must be after 2020-01-01"):
            ConstrainedDate(start)

        # Invalid: on end boundary
        with pytest.raises(ValueError, match="Date must be before 2025-12-31"):
            ConstrainedDate(end)

    def test_date_constraint_with_string_input(self):
        """Test that constraints work with string date input."""
        ConstrainedDate = Date(ge=date(2020, 1, 1), le=date(2025, 12, 31))

        # Valid string
        d1 = ConstrainedDate("2023-06-15")
        assert d1 == date(2023, 6, 15)

        # Invalid string (before range)
        with pytest.raises(ValueError, match="Date must be on or after 2020-01-01"):
            ConstrainedDate("2019-12-31")

    def test_date_constraint_with_datetime_input(self):
        """Test that constraints work with datetime input."""
        cutoff = date(2020, 1, 1)
        ConstrainedDate = Date(ge=cutoff)

        # Valid datetime
        d1 = ConstrainedDate(datetime(2023, 6, 15, 14, 30))  # noqa: DTZ001
        assert d1 == date(2023, 6, 15)

        # Invalid datetime
        with pytest.raises(ValueError, match="Date must be on or after 2020-01-01"):
            ConstrainedDate(datetime(2019, 12, 31, 23, 59))  # noqa: DTZ001

    def test_date_mock_with_ge_constraint(self):
        """Test that mock generation respects ge constraint."""
        cutoff = date(2020, 1, 1)
        ConstrainedDate = Date(ge=cutoff)

        # Generate 10 mocks, all should be >= cutoff
        for _ in range(10):
            mock_date = ConstrainedDate.mock()
            assert mock_date >= cutoff, f"Mock {mock_date} is before {cutoff}"

    def test_date_mock_with_le_constraint(self):
        """Test that mock generation respects le constraint."""
        cutoff = date(2025, 12, 31)
        ConstrainedDate = Date(le=cutoff)

        # Generate 10 mocks, all should be <= cutoff
        for _ in range(10):
            mock_date = ConstrainedDate.mock()
            assert mock_date <= cutoff, f"Mock {mock_date} is after {cutoff}"

    def test_date_mock_with_lt_constraint(self):
        """Test that mock generation respects lt constraint."""
        cutoff = date.today()  # noqa: DTZ011
        ConstrainedDate = Date(lt=cutoff)

        # Generate 10 mocks, all should be < cutoff (in the past)
        for _ in range(10):
            mock_date = ConstrainedDate.mock()
            assert mock_date < cutoff, f"Mock {mock_date} is not before {cutoff}"

    def test_date_mock_with_gt_constraint(self):
        """Test that mock generation respects gt constraint."""
        cutoff = date(2020, 1, 1)
        ConstrainedDate = Date(gt=cutoff)

        # Generate 10 mocks, all should be > cutoff
        for _ in range(10):
            mock_date = ConstrainedDate.mock()
            assert mock_date > cutoff, f"Mock {mock_date} is not after {cutoff}"

    def test_date_mock_with_range_constraints(self):
        """Test that mock generation respects both ge and le constraints."""
        start = date(2020, 1, 1)
        end = date(2020, 12, 31)
        ConstrainedDate = Date(ge=start, le=end)

        # Generate 20 mocks, all should be within range
        for _ in range(20):
            mock_date = ConstrainedDate.mock()
            assert start <= mock_date <= end, f"Mock {mock_date} is outside range [{start}, {end}]"

    def test_date_mock_with_strict_range(self):
        """Test mock generation with gt and lt (exclusive bounds)."""
        start = date(2020, 1, 1)
        end = date(2020, 12, 31)
        ConstrainedDate = Date(gt=start, lt=end)

        # Generate 20 mocks, all should be strictly between bounds
        for _ in range(20):
            mock_date = ConstrainedDate.mock()
            assert (
                start < mock_date < end
            ), f"Mock {mock_date} is not strictly between {start} and {end}"

    def test_date_mock_with_invalid_range(self):
        """Test that mock raises error for impossible date range."""
        # gt > lt makes no valid dates possible
        ConstrainedDate = Date(gt=date(2025, 1, 1), lt=date(2020, 1, 1))

        with pytest.raises(ValueError, match="Invalid date range"):
            ConstrainedDate.mock()

    def test_date_unconstrained_mock(self):
        """Test that unconstrained Date mock still works."""
        UnconstrainedDate = Date()

        # Should generate valid dates
        for _ in range(5):
            mock_date = UnconstrainedDate.mock()
            assert isinstance(mock_date, date)

    def test_date_constraint_combinations(self):
        """Test various constraint combinations."""
        # Only ge
        d1 = Date(ge=date(2020, 1, 1))
        assert d1(date(2020, 1, 1)) == date(2020, 1, 1)

        # Only le
        d2 = Date(le=date(2025, 12, 31))
        assert d2(date(2025, 12, 31)) == date(2025, 12, 31)

        # ge and lt
        d3 = Date(ge=date(2020, 1, 1), lt=date(2025, 12, 31))
        assert d3(date(2023, 6, 15)) == date(2023, 6, 15)

        # gt and le
        d4 = Date(gt=date(2020, 1, 1), le=date(2025, 12, 31))
        assert d4(date(2023, 6, 15)) == date(2023, 6, 15)


class TestDateConstraintsWithPydantic:
    """Test Date constraints with Pydantic integration."""

    def test_pydantic_model_with_date_constraints(self):
        """Test Date constraints work in Pydantic models."""
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("Pydantic not available")

        class Employee(BaseModel):
            name: str
            hire_date: Date(ge=date(2020, 1, 1))
            birth_date: Date(lt=date.today())  # noqa: DTZ011

        # Valid employee
        emp = Employee(
            name="John Doe",
            hire_date=date(2023, 5, 15),
            birth_date=date(1990, 3, 20),
        )
        assert emp.hire_date == date(2023, 5, 15)
        assert emp.birth_date == date(1990, 3, 20)

        # Invalid hire_date (before 2020)
        with pytest.raises(ValueError, match="Date must be on or after 2020-01-01"):
            Employee(
                name="Jane Doe",
                hire_date=date(2019, 12, 31),
                birth_date=date(1990, 1, 1),
            )

        # Invalid birth_date (in future)
        with pytest.raises(ValueError, match="Date must be before"):
            from datetime import timedelta

            Employee(
                name="Future Baby",
                hire_date=date(2023, 1, 1),
                birth_date=date.today() + timedelta(days=1),  # noqa: DTZ011
            )

    def test_pydantic_with_date_range(self):
        """Test Date with range constraints in Pydantic."""
        try:
            from pydantic import BaseModel, ValidationError
        except ImportError:
            pytest.skip("Pydantic not available")

        class Project(BaseModel):
            name: str
            start_date: Date(ge=date(2020, 1, 1), le=date(2030, 12, 31))

        # Valid project
        proj = Project(name="Project X", start_date=date(2025, 6, 15))
        assert proj.start_date == date(2025, 6, 15)

        # Invalid: too early
        with pytest.raises(ValidationError):
            Project(name="Old Project", start_date=date(2019, 1, 1))

        # Invalid: too late
        with pytest.raises(ValidationError):
            Project(name="Future Project", start_date=date(2031, 1, 1))

    def test_mock_generation_with_pydantic_and_constraints(self):
        """Test that mockable decorator works with constrained dates."""
        try:
            from pydantic import BaseModel

            from mocksmith import mockable
        except ImportError:
            pytest.skip("Pydantic not available")

        @mockable
        class Person(BaseModel):
            name: str
            birth_date: Date(ge=date(1900, 1, 1), lt=date.today())  # noqa: DTZ011

        # Generate 10 mocks
        for _ in range(10):
            person = Person.mock()
            assert isinstance(person.birth_date, date)
            assert date(1900, 1, 1) <= person.birth_date < date.today()  # noqa: DTZ011

    def test_date_constraints_with_string_input(self):
        """Test constraints work with ISO format string input."""
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("Pydantic not available")

        class Event(BaseModel):
            event_date: Date(ge=date(2020, 1, 1), le=date(2025, 12, 31))

        # Valid string
        evt = Event(event_date="2023-06-15")
        assert evt.event_date == date(2023, 6, 15)

        # Invalid string
        with pytest.raises(ValueError, match="Date must be on or after"):
            Event(event_date="2019-12-31")

    def test_date_boundary_edge_cases(self):
        """Test exact boundary conditions."""
        boundary = date(2023, 6, 15)

        # ge: boundary should be valid
        DateGE = Date(ge=boundary)
        assert DateGE(boundary) == boundary

        # gt: boundary should be invalid
        DateGT = Date(gt=boundary)
        with pytest.raises(ValueError, match="Date must be after"):
            DateGT(boundary)

        # le: boundary should be valid
        DateLE = Date(le=boundary)
        assert DateLE(boundary) == boundary

        # lt: boundary should be invalid
        DateLT = Date(lt=boundary)
        with pytest.raises(ValueError, match="Date must be before"):
            DateLT(boundary)
