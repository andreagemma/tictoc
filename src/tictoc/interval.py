"""Time interval value object."""

from __future__ import annotations

from datetime import timedelta
from functools import total_ordering
from numbers import Real
from typing import Any, TypeAlias

from ._human import humanize_seconds
from ._parse import parse_interval_seconds

IntervalInput: TypeAlias = "int | float | str | timedelta | TicTocInterval | None"


@total_ordering
class TicTocInterval:
    """A typed interval stored as seconds.

    The class accepts numbers, ``datetime.timedelta`` and common text formats
    such as ``"1 day 2 seconds"``, ``"1d 2s"``, ``"01:02:03"`` and
    ``"1.02:00:53"``.
    """

    __slots__ = ("_seconds",)

    def __init__(self, value: IntervalInput = 0.0) -> None:
        self._seconds = _coerce_interval_seconds(value)

    @classmethod
    def from_seconds(cls, seconds: int | float) -> "TicTocInterval":
        return cls(seconds)

    @classmethod
    def from_minutes(cls, minutes: int | float) -> "TicTocInterval":
        return cls(float(minutes) * 60.0)

    @classmethod
    def from_hours(cls, hours: int | float) -> "TicTocInterval":
        return cls(float(hours) * 3_600.0)

    @classmethod
    def from_days(cls, days: int | float) -> "TicTocInterval":
        return cls(float(days) * 86_400.0)

    @classmethod
    def from_timedelta(cls, value: timedelta) -> "TicTocInterval":
        return cls(value)

    @classmethod
    def from_string(cls, value: str) -> "TicTocInterval":
        return cls(value)

    def copy(self) -> "TicTocInterval":
        return type(self)(self._seconds)

    def __copy__(self) -> "TicTocInterval":
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> "TicTocInterval":
        return self.copy()

    @property
    def seconds(self) -> float:
        """Total seconds."""

        return self._seconds

    @property
    def total_seconds(self) -> float:
        return self._seconds

    @property
    def milliseconds(self) -> float:
        return self._seconds * 1_000.0

    @property
    def total_milliseconds(self) -> float:
        return self.milliseconds

    @property
    def microseconds(self) -> float:
        return self._seconds * 1_000_000.0

    @property
    def total_microseconds(self) -> float:
        return self.microseconds

    @property
    def minutes(self) -> float:
        return self._seconds / 60.0

    @property
    def total_minutes(self) -> float:
        return self.minutes

    @property
    def hours(self) -> float:
        return self._seconds / 3_600.0

    @property
    def total_hours(self) -> float:
        return self.hours

    @property
    def days(self) -> float:
        return self._seconds / 86_400.0

    @property
    def total_days(self) -> float:
        return self.days

    @property
    def component_days(self) -> int:
        return _split_components(self._seconds)[0]

    @property
    def component_hours(self) -> int:
        return _split_components(self._seconds)[1]

    @property
    def component_minutes(self) -> int:
        return _split_components(self._seconds)[2]

    @property
    def component_seconds(self) -> int:
        return _split_components(self._seconds)[3]

    @property
    def component_microseconds(self) -> int:
        return _split_components(self._seconds)[4]

    @property
    def timedelta(self) -> timedelta:
        return self.to_timedelta()

    def to_timedelta(self) -> timedelta:
        return timedelta(seconds=self._seconds)

    def humanize(self) -> str:
        return humanize_seconds(self._seconds)

    def __int__(self) -> int:
        return int(self._seconds)

    def __float__(self) -> float:
        return float(self._seconds)

    def __bool__(self) -> bool:
        return bool(self._seconds)

    def __str__(self) -> str:
        return self.humanize()

    def __repr__(self) -> str:
        return f"TicTocInterval({self._seconds!r})"

    def __format__(self, format_spec: str) -> str:
        if format_spec in ("", "human"):
            return str(self)
        if format_spec in ("td", "timedelta"):
            return str(self.to_timedelta())
        return format(self._seconds, format_spec)

    def __hash__(self) -> int:
        return hash(self._seconds)

    def __add__(self, other: object) -> "TicTocInterval":
        try:
            return type(self)(self._seconds + _coerce_interval_seconds(other))
        except TypeError:
            return NotImplemented  # type: ignore[return-value]

    def __radd__(self, other: object) -> "TicTocInterval":
        return self.__add__(other)

    def __iadd__(self, other: object) -> "TicTocInterval":
        self._seconds += _coerce_interval_seconds(other)
        return self

    def __sub__(self, other: object) -> "TicTocInterval":
        try:
            return type(self)(self._seconds - _coerce_interval_seconds(other))
        except TypeError:
            return NotImplemented  # type: ignore[return-value]

    def __rsub__(self, other: object) -> "TicTocInterval":
        try:
            return type(self)(_coerce_interval_seconds(other) - self._seconds)
        except TypeError:
            return NotImplemented  # type: ignore[return-value]

    def __isub__(self, other: object) -> "TicTocInterval":
        self._seconds -= _coerce_interval_seconds(other)
        return self

    def __mul__(self, other: int | float) -> "TicTocInterval":
        return type(self)(self._seconds * float(other))

    def __rmul__(self, other: int | float) -> "TicTocInterval":
        return self.__mul__(other)

    def __imul__(self, other: int | float) -> "TicTocInterval":
        self._seconds *= float(other)
        return self

    def __truediv__(self, other: object) -> "TicTocInterval | float":
        if isinstance(other, (TicTocInterval, timedelta)):
            denominator = _coerce_interval_seconds(other)
            return self._seconds / denominator
        if isinstance(other, Real):
            return type(self)(self._seconds / float(other))
        return NotImplemented

    def __itruediv__(self, other: int | float) -> "TicTocInterval":
        self._seconds /= float(other)
        return self

    def __neg__(self) -> "TicTocInterval":
        return type(self)(-self._seconds)

    def __pos__(self) -> "TicTocInterval":
        return self.copy()

    def __abs__(self) -> "TicTocInterval":
        return type(self)(abs(self._seconds))

    def __eq__(self, other: object) -> bool:
        try:
            return self._seconds == _coerce_interval_seconds(other)
        except TypeError:
            return False

    def __lt__(self, other: object) -> bool:
        try:
            return self._seconds < _coerce_interval_seconds(other)
        except TypeError:
            return NotImplemented  # type: ignore[return-value]


def _coerce_interval_seconds(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, TicTocInterval):
        return value.seconds
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, str):
        return parse_interval_seconds(value)
    raise TypeError(f"Cannot convert {type(value).__name__!r} to TicTocInterval.")


def _split_components(seconds: float) -> tuple[int, int, int, int, int]:
    delta = timedelta(seconds=abs(seconds))
    days = delta.days
    whole_seconds = delta.seconds
    hours, whole_seconds = divmod(whole_seconds, 3_600)
    minutes, whole_seconds = divmod(whole_seconds, 60)
    return days, hours, minutes, whole_seconds, delta.microseconds
