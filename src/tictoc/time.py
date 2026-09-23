"""Timestamp value object."""

from __future__ import annotations

from datetime import (
    date as datetime_date,
)
from datetime import (
    datetime as datetime_dt,
)
from datetime import (
    time as datetime_time,
)
from datetime import (
    timedelta as datetime_timedelta,
)
from functools import total_ordering
from numbers import Real
from types import NotImplementedType
from typing import Any, TypeAlias

from ._parse import parse_datetime
from .interval import TicTocInterval

TimeInput: TypeAlias = "int | float | str | datetime_dt | TicTocTime | None"


@total_ordering
class TicTocTime:
    """A timestamp stored as a Unix epoch float."""

    __slots__ = ("_timestamp", "_format")

    default_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, value: TimeInput = None, *, fmt: str | None = None) -> None:
        """Implement `__init__`.

        Args:
            value: TODO describe value.
            fmt: TODO describe fmt.

        """
        self._format = fmt or self.default_format
        self._timestamp = _coerce_timestamp(value, fmt=fmt)

    @classmethod
    def now(cls, *, fmt: str | None = None) -> TicTocTime:
        """Now.

        Args:
            fmt: TODO describe fmt.

        Returns:
            TODO describe return value.

        """
        return cls(datetime_dt.now().timestamp(), fmt=fmt)

    @classmethod
    def from_timestamp(cls, value: int | float, *, fmt: str | None = None) -> TicTocTime:
        """From timestamp.

        Args:
            value: TODO describe value.
            fmt: TODO describe fmt.

        Returns:
            TODO describe return value.

        """
        return cls(value, fmt=fmt)

    @classmethod
    def from_datetime(cls, value: datetime_dt, *, fmt: str | None = None) -> TicTocTime:
        """From datetime.

        Args:
            value: TODO describe value.
            fmt: TODO describe fmt.

        Returns:
            TODO describe return value.

        """
        return cls(value, fmt=fmt)

    @classmethod
    def from_string(cls, value: str, *, fmt: str | None = None) -> TicTocTime:
        """From string.

        Args:
            value: TODO describe value.
            fmt: TODO describe fmt.

        Returns:
            TODO describe return value.

        """
        return cls(value, fmt=fmt)

    def copy(self) -> TicTocTime:
        """Copy.

        Returns:
            TODO describe return value.

        """
        return type(self)(self._timestamp, fmt=self._format)

    def __copy__(self) -> TicTocTime:
        """Implement `__copy__`.

        Returns:
            TODO describe return value.

        """
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> TicTocTime:
        """Implement `__deepcopy__`.

        Args:
            memo: TODO describe memo.

        Returns:
            TODO describe return value.

        """
        return self.copy()

    @property
    def timestamp(self) -> float:
        """Timestamp.

        Returns:
            TODO describe return value.

        """
        return self._timestamp

    @property
    def seconds(self) -> float:
        """Seconds.

        Returns:
            TODO describe return value.

        """
        return self._timestamp

    @property
    def datetime(self) -> datetime_dt:
        """Datetime.

        Returns:
            TODO describe return value.

        """
        return self.to_datetime()

    @property
    def date(self) -> datetime_date:
        """Date.

        Returns:
            TODO describe return value.

        """
        return self.datetime.date()

    @property
    def time(self) -> datetime_time:
        """Time.

        Returns:
            TODO describe return value.

        """
        return self.datetime.time()

    @property
    def year(self) -> int:
        """Year.

        Returns:
            TODO describe return value.

        """
        return self.datetime.year

    @property
    def month(self) -> int:
        """Month.

        Returns:
            TODO describe return value.

        """
        return self.datetime.month

    @property
    def day(self) -> int:
        """Day.

        Returns:
            TODO describe return value.

        """
        return self.datetime.day

    @property
    def hour(self) -> int:
        """Hour.

        Returns:
            TODO describe return value.

        """
        return self.datetime.hour

    @property
    def minute(self) -> int:
        """Minute.

        Returns:
            TODO describe return value.

        """
        return self.datetime.minute

    @property
    def second(self) -> int:
        """Second.

        Returns:
            TODO describe return value.

        """
        return self.datetime.second

    @property
    def microsecond(self) -> int:
        """Microsecond.

        Returns:
            TODO describe return value.

        """
        return self.datetime.microsecond

    @property
    def weekday(self) -> int:
        """Weekday.

        Returns:
            TODO describe return value.

        """
        return self.datetime.weekday()

    def to_datetime(self) -> datetime_dt:
        """To datetime.

        Returns:
            TODO describe return value.

        """
        return datetime_dt.fromtimestamp(self._timestamp)

    def to_string(self, fmt: str | None = None) -> str:
        """To string.

        Args:
            fmt: TODO describe fmt.

        Returns:
            TODO describe return value.

        """
        return self.to_datetime().strftime(fmt or self._format)

    def isoformat(self, sep: str = "T", timespec: str = "auto") -> str:
        """Isoformat.

        Args:
            sep: TODO describe sep.
            timespec: TODO describe timespec.

        Returns:
            TODO describe return value.

        """
        return self.to_datetime().isoformat(sep=sep, timespec=timespec)

    def humanize(self, fmt: str | None = None) -> str:
        """Humanize.

        Args:
            fmt: TODO describe fmt.

        Returns:
            TODO describe return value.

        """
        return self.to_string(fmt)

    def __int__(self) -> int:
        """Implement `__int__`.

        Returns:
            TODO describe return value.

        """
        return int(self._timestamp)

    def __float__(self) -> float:
        """Implement `__float__`.

        Returns:
            TODO describe return value.

        """
        return float(self._timestamp)

    def __bool__(self) -> bool:
        """Implement `__bool__`.

        Returns:
            TODO describe return value.

        """
        return bool(self._timestamp)

    def __str__(self) -> str:
        """Implement `__str__`.

        Returns:
            TODO describe return value.

        """
        return self.humanize()

    def __repr__(self) -> str:
        """Implement `__repr__`.

        Returns:
            TODO describe return value.

        """
        return f"TicTocTime({self._timestamp!r}, fmt={self._format!r})"

    def __format__(self, format_spec: str) -> str:
        """Implement `__format__`.

        Args:
            format_spec: TODO describe format_spec.

        Returns:
            TODO describe return value.

        """
        if format_spec in ("", "human"):
            return str(self)
        if format_spec == "iso":
            return self.isoformat()
        if "%" in format_spec:
            return self.to_string(format_spec)
        return format(self._timestamp, format_spec)

    def __hash__(self) -> int:
        """Implement `__hash__`.

        Returns:
            TODO describe return value.

        """
        return hash(self._timestamp)

    def __add__(self, other: object) -> TicTocTime | NotImplementedType:
        """Implement `__add__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if _can_coerce_interval_for_time_math(other):
            return type(self)(
                self._timestamp + _coerce_interval_for_time_math(other),
                fmt=self._format,
            )
        return NotImplemented

    def __radd__(self, other: object) -> TicTocTime:
        """Implement `__radd__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        return self.__add__(other)

    def __iadd__(self, other: object) -> TicTocTime:
        """Implement `__iadd__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        self._timestamp += _coerce_interval_for_time_math(other)
        return self

    def __sub__(self, other: object) -> TicTocInterval | TicTocTime | NotImplementedType:
        """Implement `__sub__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if isinstance(other, (TicTocTime, datetime_dt)):
            return TicTocInterval(self._timestamp - _coerce_timestamp(other))
        if _can_coerce_interval_for_time_math(other):
            return type(self)(
                self._timestamp - _coerce_interval_for_time_math(other),
                fmt=self._format,
            )
        return NotImplemented

    def __rsub__(self, other: object) -> TicTocInterval | NotImplementedType:
        """Implement `__rsub__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if isinstance(other, (TicTocTime, datetime_dt)):
            return TicTocInterval(_coerce_timestamp(other) - self._timestamp)
        return NotImplemented

    def __isub__(self, other: object) -> TicTocTime:
        """Implement `__isub__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        self._timestamp -= _coerce_interval_for_time_math(other)
        return self

    def __eq__(self, other: object) -> bool:
        """Implement `__eq__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        try:
            return self._timestamp == _coerce_timestamp(other)
        except TypeError:
            return False

    def __lt__(self, other: object) -> bool:
        """Implement `__lt__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if _can_coerce_timestamp(other):
            return self._timestamp < _coerce_timestamp(other)
        return NotImplemented


def _coerce_timestamp(value: object, *, fmt: str | None = None) -> float:
    # Internal helper: coerce timestamp.
    """Internal helper: coerce timestamp."""
    if value is None:
        return datetime_dt.now().timestamp()
    if isinstance(value, TicTocTime):
        return value.timestamp
    if isinstance(value, datetime_dt):
        return value.timestamp()
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, str):
        return parse_datetime(value, fmt=fmt).timestamp()
    raise TypeError(f"Cannot convert {type(value).__name__!r} to TicTocTime.")


def _coerce_interval_for_time_math(value: object) -> float:
    # Internal helper: coerce interval for time math.
    """Internal helper: coerce interval for time math."""
    if isinstance(value, TicTocInterval):
        return value.seconds
    if isinstance(value, datetime_timedelta):
        return value.total_seconds()
    if isinstance(value, Real):
        return float(value)
    raise TypeError(f"Cannot use {type(value).__name__!r} as a time interval.")


def _can_coerce_timestamp(value: object) -> bool:
    # Internal helper: can coerce timestamp.
    """Internal helper: can coerce timestamp."""
    return value is None or isinstance(value, (TicTocTime, datetime_dt, Real, str))


def _can_coerce_interval_for_time_math(value: object) -> bool:
    # Internal helper: can coerce interval for time math.
    """Internal helper: can coerce interval for time math."""
    return isinstance(value, (TicTocInterval, datetime_timedelta, Real))
