"""Timestamp value object."""

from __future__ import annotations

from datetime import date, datetime, time as datetime_time, timedelta
from functools import total_ordering
from numbers import Real
from typing import Any, TypeAlias

from ._parse import parse_datetime
from .interval import TicTocInterval

TimeInput: TypeAlias = "int | float | str | datetime | TicTocTime | None"


@total_ordering
class TicTocTime:
    """A timestamp stored as a Unix epoch float."""

    __slots__ = ("_timestamp", "_format")

    default_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, value: TimeInput = None, *, fmt: str | None = None) -> None:
        self._format = fmt or self.default_format
        self._timestamp = _coerce_timestamp(value, fmt=fmt)

    @classmethod
    def now(cls, *, fmt: str | None = None) -> "TicTocTime":
        return cls(datetime.now().timestamp(), fmt=fmt)

    @classmethod
    def from_timestamp(cls, value: int | float, *, fmt: str | None = None) -> "TicTocTime":
        return cls(value, fmt=fmt)

    @classmethod
    def from_datetime(cls, value: datetime, *, fmt: str | None = None) -> "TicTocTime":
        return cls(value, fmt=fmt)

    @classmethod
    def from_string(cls, value: str, *, fmt: str | None = None) -> "TicTocTime":
        return cls(value, fmt=fmt)

    def copy(self) -> "TicTocTime":
        return type(self)(self._timestamp, fmt=self._format)

    def __copy__(self) -> "TicTocTime":
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> "TicTocTime":
        return self.copy()

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def seconds(self) -> float:
        return self._timestamp

    @property
    def datetime(self) -> datetime:
        return self.to_datetime()

    @property
    def date(self) -> date:
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

    def to_datetime(self) -> datetime:
        return datetime.fromtimestamp(self._timestamp)

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

    def __add__(self, other: object) -> "TicTocTime":
        try:
            return type(self)(self._timestamp + _coerce_interval_for_time_math(other), fmt=self._format)
        except TypeError:
            return NotImplemented  # type: ignore[return-value]

    def __radd__(self, other: object) -> "TicTocTime":
        return self.__add__(other)

    def __iadd__(self, other: object) -> "TicTocTime":
        self._timestamp += _coerce_interval_for_time_math(other)
        return self

    def __sub__(self, other: object) -> "TicTocInterval | TicTocTime":
        if isinstance(other, (TicTocTime, datetime)):
            return TicTocInterval(self._timestamp - _coerce_timestamp(other))
        try:
            return type(self)(self._timestamp - _coerce_interval_for_time_math(other), fmt=self._format)
        except TypeError:
            return NotImplemented  # type: ignore[return-value]

    def __rsub__(self, other: object) -> "TicTocInterval":
        if isinstance(other, (TicTocTime, datetime)):
            return TicTocInterval(_coerce_timestamp(other) - self._timestamp)
        return NotImplemented  # type: ignore[return-value]

    def __isub__(self, other: object) -> "TicTocTime":
        self._timestamp -= _coerce_interval_for_time_math(other)
        return self

    def __eq__(self, other: object) -> bool:
        try:
            return self._timestamp == _coerce_timestamp(other)
        except TypeError:
            return False

    def __lt__(self, other: object) -> bool:
        try:
            return self._timestamp < _coerce_timestamp(other)
        except TypeError:
            return NotImplemented  # type: ignore[return-value]


def _coerce_timestamp(value: object, *, fmt: str | None = None) -> float:
    if value is None:
        return datetime.now().timestamp()
    if isinstance(value, TicTocTime):
        return value.timestamp
    if isinstance(value, datetime):
        return value.timestamp()
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, str):
        return parse_datetime(value, fmt=fmt).timestamp()
    raise TypeError(f"Cannot convert {type(value).__name__!r} to TicTocTime.")


def _coerce_interval_for_time_math(value: object) -> float:
    if isinstance(value, TicTocInterval):
        return value.seconds
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, Real):
        return float(value)
    raise TypeError(f"Cannot use {type(value).__name__!r} as a time interval.")
