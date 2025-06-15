"""Temporal database types."""

from datetime import date, datetime, time
from typing import Type, Union

from db_types.types.base import DBType


class DATE(DBType[date]):
    """Date type (year, month, day)."""

    @property
    def sql_type(self) -> str:
        return "DATE"

    @property
    def python_type(self) -> Type[date]:
        return date

    def validate(self, value: any) -> None:
        if value is None:
            return

        if not isinstance(value, (date, datetime, str)):
            raise ValueError(f"Expected date value, got {type(value).__name__}")

        if isinstance(value, str):
            try:
                date.fromisoformat(value)
            except ValueError as e:
                raise ValueError(f"Invalid date string: {e}")

    def _serialize(self, value: Union[date, datetime, str]) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        elif isinstance(value, date):
            return value.isoformat()
        else:  # str
            # Validate and normalize
            return date.fromisoformat(value).isoformat()

    def _deserialize(self, value: any) -> date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        elif isinstance(value, datetime):
            return value.date()
        else:
            return date.fromisoformat(str(value))


class TIME(DBType[time]):
    """Time type (hour, minute, second, microsecond)."""

    def __init__(self, precision: int = 6):
        super().__init__()
        if precision < 0 or precision > 6:
            raise ValueError("Time precision must be between 0 and 6")
        self.precision = precision

    @property
    def sql_type(self) -> str:
        if self.precision != 6:
            return f"TIME({self.precision})"
        return "TIME"

    @property
    def python_type(self) -> Type[time]:
        return time

    def validate(self, value: any) -> None:
        if value is None:
            return

        if not isinstance(value, (time, datetime, str)):
            raise ValueError(f"Expected time value, got {type(value).__name__}")

        if isinstance(value, str):
            try:
                time.fromisoformat(value)
            except ValueError as e:
                raise ValueError(f"Invalid time string: {e}")

    def _serialize(self, value: Union[time, datetime, str]) -> str:
        if isinstance(value, datetime):
            time_val = value.time()
        elif isinstance(value, time):
            time_val = value
        else:  # str
            time_val = time.fromisoformat(value)

        # Truncate microseconds based on precision
        if self.precision < 6:
            microseconds = time_val.microsecond
            factor = 10 ** (6 - self.precision)
            microseconds = (microseconds // factor) * factor
            time_val = time_val.replace(microsecond=microseconds)

        return time_val.isoformat()

    def _deserialize(self, value: any) -> time:
        if isinstance(value, time) and not isinstance(value, datetime):
            return value
        elif isinstance(value, datetime):
            return value.time()
        else:
            return time.fromisoformat(str(value))


class TIMESTAMP(DBType[datetime]):
    """Timestamp type with timezone support."""

    def __init__(self, precision: int = 6, with_timezone: bool = True):
        super().__init__()
        if precision < 0 or precision > 6:
            raise ValueError("Timestamp precision must be between 0 and 6")
        self.precision = precision
        self.with_timezone = with_timezone

    @property
    def sql_type(self) -> str:
        tz_suffix = " WITH TIME ZONE" if self.with_timezone else ""
        if self.precision != 6:
            return f"TIMESTAMP({self.precision}){tz_suffix}"
        return f"TIMESTAMP{tz_suffix}"

    @property
    def python_type(self) -> Type[datetime]:
        return datetime

    def validate(self, value: any) -> None:
        if value is None:
            return

        if not isinstance(value, (datetime, date, str)):
            raise ValueError(f"Expected datetime value, got {type(value).__name__}")

        if isinstance(value, str):
            try:
                datetime.fromisoformat(value)
            except ValueError as e:
                raise ValueError(f"Invalid datetime string: {e}")

        if isinstance(value, datetime) and self.with_timezone and value.tzinfo is None:
            raise ValueError("Timestamp with timezone requires timezone-aware datetime")

    def _serialize(self, value: Union[datetime, date, str]) -> str:
        if isinstance(value, date) and not isinstance(value, datetime):
            dt_value = datetime.combine(value, time.min)
        elif isinstance(value, datetime):
            dt_value = value
        else:  # str
            dt_value = datetime.fromisoformat(value)

        # Truncate microseconds based on precision
        if self.precision < 6:
            microseconds = dt_value.microsecond
            factor = 10 ** (6 - self.precision)
            microseconds = (microseconds // factor) * factor
            dt_value = dt_value.replace(microsecond=microseconds)

        return dt_value.isoformat()

    def _deserialize(self, value: any) -> datetime:
        if isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            return datetime.combine(value, time.min)
        else:
            return datetime.fromisoformat(str(value))

    def __repr__(self) -> str:
        parts = [f"precision={self.precision}"]
        if self.with_timezone:
            parts.append("with_timezone=True")
        return f"TIMESTAMP({', '.join(parts)})"


class DATETIME(TIMESTAMP):
    """Alias for TIMESTAMP without timezone."""

    def __init__(self, precision: int = 6):
        super().__init__(precision, with_timezone=False)

    @property
    def sql_type(self) -> str:
        if self.precision != 6:
            return f"DATETIME({self.precision})"
        return "DATETIME"
