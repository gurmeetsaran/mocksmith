"""Temporal types with V3 pattern - extends Python datetime types directly."""

from datetime import date, datetime, time, timezone
from typing import Any, ClassVar

try:
    from pydantic import GetCoreSchemaHandler  # type: ignore
    from pydantic_core import PydanticCustomError, core_schema  # type: ignore

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    GetCoreSchemaHandler = Any
    core_schema = None
    PydanticCustomError = ValueError


class _DATE(date):
    """Date type that validates at instantiation."""

    SQL_TYPE: ClassVar[str] = "DATE"

    def __new__(cls, year: Any, month: Any = None, day: Any = None):  # type: ignore
        """Create new date with validation.

        Can be called with:
        - DATE(2024, 3, 15) - separate year, month, day
        - DATE("2024-03-15") - ISO format string
        - DATE(date_obj) - existing date object
        - DATE(datetime_obj) - datetime (extracts date part)
        """
        # Handle single argument cases
        if month is None and day is None:
            value = year

            if value is None:  # type: ignore[comparison-overlap]
                raise ValueError("Value cannot be None")

            # Handle existing date/datetime
            if isinstance(value, datetime):
                return super().__new__(cls, value.year, value.month, value.day)
            elif isinstance(value, date):
                return super().__new__(cls, value.year, value.month, value.day)
            # Handle string
            elif isinstance(value, str):  # type: ignore[unreachable]
                try:
                    parsed = date.fromisoformat(value)
                    return super().__new__(cls, parsed.year, parsed.month, parsed.day)
                except ValueError as e:
                    raise ValueError(f"Invalid date string: {value}") from e
            else:
                raise ValueError(f"Cannot convert {type(value).__name__} to date")

        # Handle three argument case (year, month, day)
        try:
            return super().__new__(cls, int(year), int(month), int(day))
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid date components: year={year}, month={month}, day={day}"
            ) from e

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        return self.SQL_TYPE

    def serialize(self) -> str:
        """Serialize to ISO format string for SQL."""
        return self.isoformat()

    @classmethod
    def validate(cls, value: Any) -> date:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return date(instance.year, instance.month, instance.day)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_date(value: Any) -> date:
            """Validate and convert to date."""
            try:
                instance = cls(value)
                return date(instance.year, instance.month, instance.day)
            except ValueError as e:
                raise PydanticCustomError("date_type", str(e)) from e

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_date,
            core_schema.union_schema(  # type: ignore
                [
                    core_schema.date_schema(),  # type: ignore
                    core_schema.datetime_schema(),  # type: ignore
                    core_schema.str_schema(),  # type: ignore
                ]
            ),
        )

    @classmethod
    def mock(cls) -> date:
        """Generate mock date value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()
            return fake.date_object()
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


class _TIME(time):
    """Time type that validates at instantiation."""

    SQL_TYPE: ClassVar[str] = "TIME"
    _precision: ClassVar[int] = 6

    def __new__(  # type: ignore
        cls,
        hour: Any = 0,
        minute: Any = 0,
        second: Any = 0,
        microsecond: Any = 0,
        *,
        tzinfo: Any = None,
        fold: int = 0,
    ):
        """Create new time with validation.

        Can be called with:
        - TIME(14, 30, 45) - hour, minute, second
        - TIME("14:30:45") - ISO format string
        - TIME(time_obj) - existing time object
        - TIME(datetime_obj) - datetime (extracts time part)
        """
        # Handle single argument case
        if (
            isinstance(hour, (str, time, datetime))
            and minute == 0
            and second == 0
            and microsecond == 0
        ):
            value = hour

            if value is None:  # type: ignore[comparison-overlap]
                raise ValueError("Value cannot be None")

            # Handle existing time/datetime
            if isinstance(value, datetime):
                value = value.time()

            if isinstance(value, time):
                hour = value.hour
                minute = value.minute
                second = value.second
                microsecond = value.microsecond
                tzinfo = value.tzinfo
                fold = value.fold
            # Handle string
            elif isinstance(value, str):  # type: ignore[unreachable]
                try:
                    parsed = time.fromisoformat(value)
                    hour = parsed.hour
                    minute = parsed.minute
                    second = parsed.second
                    microsecond = parsed.microsecond
                    tzinfo = parsed.tzinfo
                    fold = parsed.fold
                except ValueError as e:
                    raise ValueError(f"Invalid time string: {value}") from e

        # Apply precision truncation if needed
        if cls._precision < 6 and microsecond != 0:
            factor = 10 ** (6 - cls._precision)
            microsecond = (microsecond // factor) * factor

        try:
            return super().__new__(
                cls, int(hour), int(minute), int(second), int(microsecond), tzinfo=tzinfo, fold=fold
            )
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid time components") from e

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        if self._precision != 6:
            return f"TIME({self._precision})"
        return self.SQL_TYPE

    def serialize(self) -> str:
        """Serialize to ISO format string for SQL."""
        return self.isoformat()

    @classmethod
    def validate(cls, value: Any) -> time:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return time(
            instance.hour,
            instance.minute,
            instance.second,
            instance.microsecond,
            tzinfo=instance.tzinfo,
        )

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_time(value: Any) -> time:
            """Validate and convert to time."""
            try:
                instance = cls(value)
                return time(
                    instance.hour,
                    instance.minute,
                    instance.second,
                    instance.microsecond,
                    tzinfo=instance.tzinfo,
                )
            except ValueError as e:
                raise PydanticCustomError("time_type", str(e)) from e

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_time,
            core_schema.union_schema(  # type: ignore
                [
                    core_schema.time_schema(),  # type: ignore
                    core_schema.datetime_schema(),  # type: ignore
                    core_schema.str_schema(),  # type: ignore
                ]
            ),
        )

    @classmethod
    def mock(cls) -> time:
        """Generate mock time value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()
            return fake.time_object()
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


class _DATETIME(datetime):
    """DateTime type that validates at instantiation (no timezone)."""

    SQL_TYPE: ClassVar[str] = "DATETIME"
    _precision: ClassVar[int] = 6

    def __new__(  # type: ignore
        cls,
        year: Any,
        month: Any = 1,
        day: Any = 1,
        hour: Any = 0,
        minute: Any = 0,
        second: Any = 0,
        microsecond: Any = 0,
        tzinfo: Any = None,
        *,
        fold: int = 0,
    ):
        """Create new datetime with validation.

        Can be called with:
        - DATETIME(2024, 3, 15, 14, 30, 45) - components
        - DATETIME("2024-03-15T14:30:45") - ISO format string
        - DATETIME(datetime_obj) - existing datetime object
        - DATETIME(date_obj) - date (sets time to 00:00:00)
        """
        # Handle single argument case
        if isinstance(year, (str, date, datetime)) and month == 1 and day == 1:
            value = year

            if value is None:  # type: ignore[comparison-overlap]
                raise ValueError("Value cannot be None")

            # Handle existing datetime
            if isinstance(value, datetime):
                year = value.year
                month = value.month
                day = value.day
                hour = value.hour
                minute = value.minute
                second = value.second
                microsecond = value.microsecond
                # DATETIME should not have timezone
                tzinfo = None
            # Handle date
            elif isinstance(value, date):
                year = value.year
                month = value.month
                day = value.day
                hour = minute = second = microsecond = 0
                tzinfo = None
            # Handle string
            elif isinstance(value, str):  # type: ignore[unreachable]
                try:
                    parsed = datetime.fromisoformat(value)
                    year = parsed.year
                    month = parsed.month
                    day = parsed.day
                    hour = parsed.hour
                    minute = parsed.minute
                    second = parsed.second
                    microsecond = parsed.microsecond
                    # DATETIME should not have timezone
                    tzinfo = None
                except ValueError as e:
                    raise ValueError(f"Invalid datetime string: {value}") from e

        # Apply precision truncation if needed
        if cls._precision < 6 and microsecond != 0:
            factor = 10 ** (6 - cls._precision)
            microsecond = (microsecond // factor) * factor

        # DATETIME should never have timezone
        if tzinfo is not None:
            raise ValueError(
                "DATETIME type does not support timezone. Use TIMESTAMP for timezone support."
            )

        try:
            return super().__new__(
                cls,
                int(year),
                int(month),
                int(day),
                int(hour),
                int(minute),
                int(second),
                int(microsecond),
                tzinfo=None,
                fold=fold,
            )
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid datetime components") from e

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        if self._precision != 6:
            return f"DATETIME({self._precision})"
        return self.SQL_TYPE

    def serialize(self) -> str:
        """Serialize to ISO format string for SQL."""
        return self.isoformat()

    @classmethod
    def validate(cls, value: Any) -> datetime:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return datetime(  # noqa: DTZ001
            instance.year,
            instance.month,
            instance.day,
            instance.hour,
            instance.minute,
            instance.second,
            instance.microsecond,
        )

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_datetime(value: Any) -> datetime:
            """Validate and convert to datetime."""
            try:
                instance = cls(value)
                return datetime(  # noqa: DTZ001
                    instance.year,
                    instance.month,
                    instance.day,
                    instance.hour,
                    instance.minute,
                    instance.second,
                    instance.microsecond,
                )
            except ValueError as e:
                raise PydanticCustomError("datetime_type", str(e)) from e

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_datetime,
            core_schema.union_schema(  # type: ignore
                [
                    core_schema.datetime_schema(),  # type: ignore
                    core_schema.date_schema(),  # type: ignore
                    core_schema.str_schema(),  # type: ignore
                ]
            ),
        )

    @classmethod
    def mock(cls) -> datetime:
        """Generate mock datetime value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()
            # Return without timezone for DATETIME
            dt = fake.date_time()
            return dt.replace(tzinfo=None)
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


class _TIMESTAMP(datetime):
    """Timestamp type with timezone support."""

    SQL_TYPE: ClassVar[str] = "TIMESTAMP"
    _precision: ClassVar[int] = 6
    _with_timezone: ClassVar[bool] = True

    def __new__(  # type: ignore
        cls,
        year: Any,
        month: Any = 1,
        day: Any = 1,
        hour: Any = 0,
        minute: Any = 0,
        second: Any = 0,
        microsecond: Any = 0,
        tzinfo: Any = None,
        *,
        fold: int = 0,
    ):
        """Create new timestamp with validation.

        Can be called with:
        - TIMESTAMP(2024, 3, 15, 14, 30, 45) - components
        - TIMESTAMP("2024-03-15T14:30:45+00:00") - ISO format string
        - TIMESTAMP(datetime_obj) - existing datetime object
        - TIMESTAMP(date_obj) - date (sets time to 00:00:00)
        """
        # Handle single argument case
        if isinstance(year, (str, date, datetime)) and month == 1 and day == 1:
            value = year

            if value is None:  # type: ignore[comparison-overlap]
                raise ValueError("Value cannot be None")

            # Handle existing datetime
            if isinstance(value, datetime):
                year = value.year
                month = value.month
                day = value.day
                hour = value.hour
                minute = value.minute
                second = value.second
                microsecond = value.microsecond
                tzinfo = value.tzinfo
            # Handle date
            elif isinstance(value, date):
                year = value.year
                month = value.month
                day = value.day
                hour = minute = second = microsecond = 0
                tzinfo = timezone.utc if cls._with_timezone else None
            # Handle string
            elif isinstance(value, str):  # type: ignore[unreachable]
                try:
                    # Handle 'Z' suffix for UTC
                    if value.endswith("Z"):
                        value = value[:-1] + "+00:00"
                    parsed = datetime.fromisoformat(value)
                    year = parsed.year
                    month = parsed.month
                    day = parsed.day
                    hour = parsed.hour
                    minute = parsed.minute
                    second = parsed.second
                    microsecond = parsed.microsecond
                    tzinfo = parsed.tzinfo
                except ValueError as e:
                    raise ValueError(f"Invalid timestamp string: {value}") from e

        # Apply precision truncation if needed
        if cls._precision < 6 and microsecond != 0:
            factor = 10 ** (6 - cls._precision)
            microsecond = (microsecond // factor) * factor

        # Check timezone requirements
        if cls._with_timezone and tzinfo is None:
            # Default to UTC for timestamp with timezone
            tzinfo = timezone.utc
        elif not cls._with_timezone and tzinfo is not None:
            # Remove timezone for timestamp without timezone
            tzinfo = None

        try:
            return super().__new__(
                cls,
                int(year),
                int(month),
                int(day),
                int(hour),
                int(minute),
                int(second),
                int(microsecond),
                tzinfo=tzinfo,
                fold=fold,
            )
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid timestamp components") from e

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        tz_suffix = " WITH TIME ZONE" if self._with_timezone else ""
        if self._precision != 6:
            return f"TIMESTAMP({self._precision}){tz_suffix}"
        return f"TIMESTAMP{tz_suffix}"

    def serialize(self) -> str:
        """Serialize to ISO format string for SQL."""
        return self.isoformat()

    @classmethod
    def validate(cls, value: Any) -> datetime:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return datetime(
            instance.year,
            instance.month,
            instance.day,
            instance.hour,
            instance.minute,
            instance.second,
            instance.microsecond,
            tzinfo=instance.tzinfo,
        )

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_timestamp(value: Any) -> datetime:
            """Validate and convert to timestamp."""
            try:
                instance = cls(value)
                return datetime(
                    instance.year,
                    instance.month,
                    instance.day,
                    instance.hour,
                    instance.minute,
                    instance.second,
                    instance.microsecond,
                    tzinfo=instance.tzinfo,
                )
            except ValueError as e:
                raise PydanticCustomError("timestamp_type", str(e)) from e

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_timestamp,
            core_schema.union_schema(  # type: ignore
                [
                    core_schema.datetime_schema(),  # type: ignore
                    core_schema.date_schema(),  # type: ignore
                    core_schema.str_schema(),  # type: ignore
                ]
            ),
        )

    @classmethod
    def mock(cls) -> datetime:
        """Generate mock timestamp value."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()
            dt = fake.date_time()
            if cls._with_timezone:
                # Add UTC timezone
                return dt.replace(tzinfo=timezone.utc)
            else:
                return dt.replace(tzinfo=None)
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


# Factory functions
def Date() -> type:  # noqa: N802
    """Create a Date type for use as type annotation.

    Example:
        class Person(BaseModel):
            birth_date: Date()
            hire_date: Date()
    """
    return _DATE


def Time(precision: int = 6) -> type:  # noqa: N802
    """Create a Time type with optional precision.

    Args:
        precision: Number of fractional seconds digits (0-6)

    Example:
        class Schedule(BaseModel):
            start_time: Time()
            end_time: Time(precision=0)  # No fractional seconds
    """
    if precision < 0 or precision > 6:
        raise ValueError("Time precision must be between 0 and 6")

    class ConstrainedTime(_TIME):
        _precision = precision
        SQL_TYPE = "TIME"

    return ConstrainedTime


def DateTime(precision: int = 6) -> type:  # noqa: N802
    """Create a DateTime type with optional precision.

    Args:
        precision: Number of fractional seconds digits (0-6)

    Example:
        class Log(BaseModel):
            timestamp: DateTime()
            processed: DateTime(precision=0)
    """
    if precision < 0 or precision > 6:
        raise ValueError("DateTime precision must be between 0 and 6")

    class ConstrainedDateTime(_DATETIME):
        _precision = precision
        SQL_TYPE = "DATETIME"

    return ConstrainedDateTime


def Timestamp(precision: int = 6, with_timezone: bool = True) -> type:  # noqa: N802
    """Create a Timestamp type with optional timezone.

    Args:
        precision: Number of fractional seconds digits (0-6)
        with_timezone: Whether to include timezone information

    Example:
        class Event(BaseModel):
            created_at: Timestamp()
            updated_at: Timestamp(with_timezone=False)
            processed_at: Timestamp(precision=3)  # Milliseconds
    """
    if precision < 0 or precision > 6:
        raise ValueError("Timestamp precision must be between 0 and 6")

    class ConstrainedTimestamp(_TIMESTAMP):
        _precision = precision
        _with_timezone = with_timezone
        SQL_TYPE = "TIMESTAMP"

    return ConstrainedTimestamp
