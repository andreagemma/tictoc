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
        self._format = fmt or self.default_format
        self._timestamp = _coerce_timestamp(value, fmt=fmt)

    @classmethod
    def now(cls, *, fmt: str | None = None) -> TicTocTime:
        return cls(datetime_dt.now().timestamp(), fmt=fmt)

    @classmethod
    def from_timestamp(cls, value: int | float, *, fmt: str | None = None) -> TicTocTime:
        return cls(value, fmt=fmt)

    @classmethod
    def from_datetime(cls, value: datetime_dt, *, fmt: str | None = None) -> TicTocTime:
        return cls(value, fmt=fmt)

    @classmethod
    def from_string(cls, value: str, *, fmt: str | None = None) -> TicTocTime:
        return cls(value, fmt=fmt)

    def copy(self) -> TicTocTime:
        return type(self)(self._timestamp, fmt=self._format)

    def __copy__(self) -> TicTocTime:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> TicTocTime:
        return self.copy()

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def seconds(self) -> float:
        return self._timestamp

    @property
    def datetime(self) -> datetime_dt:
        return self.to_datetime()

    @property
    def date(self) -> datetime_date:
        return self.datetime.date()

    @property
    def time(self) -> datetime_time:
        return self.datetime.time()

    @property
    def year(self) -> int:
        return self.datetime.year

    @property
    def month(self) -> int:
        return self.datetime.month

    @property
    def day(self) -> int:
        return self.datetime.day

    @property
    def hour(self) -> int:
        return self.datetime.hour

    @property
    def minute(self) -> int:
        return self.datetime.minute

    @property
    def second(self) -> int:
        return self.datetime.second

    @property
    def microsecond(self) -> int:
        return self.datetime.microsecond

    @property
    def weekday(self) -> int:
        return self.datetime.weekday()

    def to_datetime(self) -> datetime_dt:
        return datetime_dt.fromtimestamp(self._timestamp)

    def to_string(self, fmt: str | None = None) -> str:
        return self.to_datetime().strftime(fmt or self._format)

    def isoformat(self, sep: str = "T", timespec: str = "auto") -> str:
        return self.to_datetime().isoformat(sep=sep, timespec=timespec)

    def humanize(self, fmt: str | None = None) -> str:
        return self.to_string(fmt)

    def __int__(self) -> int:
        return int(self._timestamp)

    def __float__(self) -> float:
        return float(self._timestamp)

    def __bool__(self) -> bool:
        return bool(self._timestamp)

    def __str__(self) -> str:
        return self.humanize()

    def __repr__(self) -> str:
        return f"TicTocTime({self._timestamp!r}, fmt={self._format!r})"

    def __format__(self, format_spec: str) -> str:
        if format_spec in ("", "human"):
            return str(self)
        if format_spec == "iso":
            return self.isoformat()
        if "%" in format_spec:
            return self.to_string(format_spec)
        return format(self._timestamp, format_spec)

    def __hash__(self) -> int:
        return hash(self._timestamp)

    def __add__(self, other: object) -> TicTocTime | NotImplementedType:
        if _can_coerce_interval_for_time_math(other):
            return type(self)(
                self._timestamp + _coerce_interval_for_time_math(other),
                fmt=self._format,
            )
        return NotImplemented

    def __radd__(self, other: object) -> TicTocTime:
        return self.__add__(other)

    def __iadd__(self, other: object) -> TicTocTime:
        self._timestamp += _coerce_interval_for_time_math(other)
        return self

    def __sub__(self, other: object) -> TicTocInterval | TicTocTime | NotImplementedType:
        if isinstance(other, (TicTocTime, datetime_dt)):
            return TicTocInterval(self._timestamp - _coerce_timestamp(other))
        if _can_coerce_interval_for_time_math(other):
            return type(self)(
                self._timestamp - _coerce_interval_for_time_math(other),
                fmt=self._format,
            )
        return NotImplemented

    def __rsub__(self, other: object) -> TicTocInterval | NotImplementedType:
        if isinstance(other, (TicTocTime, datetime_dt)):
            return TicTocInterval(_coerce_timestamp(other) - self._timestamp)
        return NotImplemented

    def __isub__(self, other: object) -> TicTocTime:
        self._timestamp -= _coerce_interval_for_time_math(other)
        return self

    def __eq__(self, other: object) -> bool:
        try:
            return self._timestamp == _coerce_timestamp(other)
        except TypeError:
            return False

    def __lt__(self, other: object) -> bool:
        if _can_coerce_timestamp(other):
            return self._timestamp < _coerce_timestamp(other)
        return NotImplemented


def _coerce_timestamp(value: object, *, fmt: str | None = None) -> float:
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
    if isinstance(value, TicTocInterval):
        return value.seconds
    if isinstance(value, datetime_timedelta):
        return value.total_seconds()
    if isinstance(value, Real):
        return float(value)
    raise TypeError(f"Cannot use {type(value).__name__!r} as a time interval.")


def _can_coerce_timestamp(value: object) -> bool:
    return value is None or isinstance(value, (TicTocTime, datetime_dt, Real, str))


def _can_coerce_interval_for_time_math(value: object) -> bool:
    return isinstance(value, (TicTocInterval, datetime_timedelta, Real))
