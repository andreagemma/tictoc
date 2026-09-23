"""Time interval value object."""

from __future__ import annotations

from datetime import timedelta as datetime_timedelta
from functools import total_ordering
from numbers import Real
from types import NotImplementedType
from typing import Any, TypeAlias

from ._human import humanize_seconds
from ._parse import parse_interval_seconds

IntervalInput: TypeAlias = "int | float | str | datetime_timedelta | TicTocInterval | None"


@total_ordering
class TicTocInterval:
    """A typed interval stored as seconds.

    The class accepts numbers, ``datetime.timedelta`` and common text formats
    such as ``"1 day 2 seconds"``, ``"1d 2s"``, ``"01:02:03"`` and
    ``"1.02:00:53"``.
    """

    __slots__ = ("_seconds",)

    def __init__(self, value: IntervalInput = 0.0) -> None:
        """Implement `__init__`.

        Args:
            value: TODO describe value.

        """
        self._seconds: float = _coerce_interval_seconds(value)

    @classmethod
    def from_seconds(cls, seconds: int | float) -> TicTocInterval:
        """From seconds.

        Args:
            seconds: TODO describe seconds.

        Returns:
            TODO describe return value.

        """
        return cls(seconds)

    @classmethod
    def from_minutes(cls, minutes: int | float) -> TicTocInterval:
        """From minutes.

        Args:
            minutes: TODO describe minutes.

        Returns:
            TODO describe return value.

        """
        return cls(float(minutes) * 60.0)

    @classmethod
    def from_hours(cls, hours: int | float) -> TicTocInterval:
        """From hours.

        Args:
            hours: TODO describe hours.

        Returns:
            TODO describe return value.

        """
        return cls(float(hours) * 3_600.0)

    @classmethod
    def from_days(cls, days: int | float) -> TicTocInterval:
        """From days.

        Args:
            days: TODO describe days.

        Returns:
            TODO describe return value.

        """
        return cls(float(days) * 86_400.0)

    @classmethod
    def from_timedelta(cls, value: datetime_timedelta) -> TicTocInterval:
        """From timedelta.

        Args:
            value: TODO describe value.

        Returns:
            TODO describe return value.

        """
        return cls(value)

    @classmethod
    def from_string(cls, value: str) -> TicTocInterval:
        """From string.

        Args:
            value: TODO describe value.

        Returns:
            TODO describe return value.

        """
        return cls(value)

    def copy(self) -> TicTocInterval:
        """Copy.

        Returns:
            TODO describe return value.

        """
        return type(self)(self._seconds)

    def __copy__(self) -> TicTocInterval:
        """Implement `__copy__`.

        Returns:
            TODO describe return value.

        """
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> TicTocInterval:
        """Implement `__deepcopy__`.

        Args:
            memo: TODO describe memo.

        Returns:
            TODO describe return value.

        """
        return self.copy()

    @property
    def seconds(self) -> float:
        """Total seconds."""

        return self._seconds

    @property
    def total_seconds(self) -> float:
        """Total seconds.

        Returns:
            TODO describe return value.

        """
        return self._seconds

    @property
    def milliseconds(self) -> float:
        """Milliseconds.

        Returns:
            TODO describe return value.

        """
        return self._seconds * 1_000.0

    @property
    def total_milliseconds(self) -> float:
        """Total milliseconds.

        Returns:
            TODO describe return value.

        """
        return self.milliseconds

    @property
    def microseconds(self) -> float:
        """Microseconds.

        Returns:
            TODO describe return value.

        """
        return self._seconds * 1_000_000.0

    @property
    def total_microseconds(self) -> float:
        """Total microseconds.

        Returns:
            TODO describe return value.

        """
        return self.microseconds

    @property
    def minutes(self) -> float:
        """Minutes.

        Returns:
            TODO describe return value.

        """
        return self._seconds / 60.0

    @property
    def total_minutes(self) -> float:
        """Total minutes.

        Returns:
            TODO describe return value.

        """
        return self.minutes

    @property
    def hours(self) -> float:
        """Hours.

        Returns:
            TODO describe return value.

        """
        return self._seconds / 3_600.0

    @property
    def total_hours(self) -> float:
        """Total hours.

        Returns:
            TODO describe return value.

        """
        return self.hours

    @property
    def days(self) -> float:
        """Days.

        Returns:
            TODO describe return value.

        """
        return self._seconds / 86_400.0

    @property
    def total_days(self) -> float:
        """Total days.

        Returns:
            TODO describe return value.

        """
        return self.days

    @property
    def component_days(self) -> int:
        """Component days.

        Returns:
            TODO describe return value.

        """
        return _split_components(self._seconds)[0]

    @property
    def component_hours(self) -> int:
        """Component hours.

        Returns:
            TODO describe return value.

        """
        return _split_components(self._seconds)[1]

    @property
    def component_minutes(self) -> int:
        """Component minutes.

        Returns:
            TODO describe return value.

        """
        return _split_components(self._seconds)[2]

    @property
    def component_seconds(self) -> int:
        """Component seconds.

        Returns:
            TODO describe return value.

        """
        return _split_components(self._seconds)[3]

    @property
    def component_microseconds(self) -> int:
        """Component microseconds.

        Returns:
            TODO describe return value.

        """
        return _split_components(self._seconds)[4]

    @property
    def timedelta(self) -> datetime_timedelta:
        """Timedelta.

        Returns:
            TODO describe return value.

        """
        return self.to_timedelta()

    def to_timedelta(self) -> datetime_timedelta:
        """To timedelta.

        Returns:
            TODO describe return value.

        """
        return datetime_timedelta(seconds=self._seconds)

    def humanize(self) -> str:
        """Humanize.

        Returns:
            TODO describe return value.

        """
        return humanize_seconds(self._seconds)

    def __int__(self) -> int:
        """Implement `__int__`.

        Returns:
            TODO describe return value.

        """
        return int(self._seconds)

    def __float__(self) -> float:
        """Implement `__float__`.

        Returns:
            TODO describe return value.

        """
        return float(self._seconds)

    def __bool__(self) -> bool:
        """Implement `__bool__`.

        Returns:
            TODO describe return value.

        """
        return bool(self._seconds)

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
        return f"TicTocInterval({self._seconds!r})"

    def __format__(self, format_spec: str) -> str:
        """Implement `__format__`.

        Args:
            format_spec: TODO describe format_spec.

        Returns:
            TODO describe return value.

        """
        if format_spec in ("", "human"):
            return str(self)
        if format_spec in ("td", "timedelta"):
            return str(self.to_timedelta())
        return format(self._seconds, format_spec)

    def __hash__(self) -> int:
        """Implement `__hash__`.

        Returns:
            TODO describe return value.

        """
        return hash(self._seconds)

    def __add__(self, other: object) -> TicTocInterval | NotImplementedType:
        """Implement `__add__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if _can_coerce_interval(other):
            return type(self)(self._seconds + _coerce_interval_seconds(other))
        return NotImplemented

    def __radd__(self, other: object) -> TicTocInterval:
        """Implement `__radd__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        return self.__add__(other)

    def __iadd__(self, other: object) -> TicTocInterval:
        """Implement `__iadd__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        self._seconds += _coerce_interval_seconds(other)
        return self

    def __sub__(self, other: object) -> TicTocInterval | NotImplementedType:
        """Implement `__sub__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if _can_coerce_interval(other):
            return type(self)(self._seconds - _coerce_interval_seconds(other))
        return NotImplemented

    def __rsub__(self, other: object) -> TicTocInterval | NotImplementedType:
        """Implement `__rsub__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if _can_coerce_interval(other):
            return type(self)(_coerce_interval_seconds(other) - self._seconds)
        return NotImplemented

    def __isub__(self, other: object) -> TicTocInterval:
        """Implement `__isub__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        self._seconds -= _coerce_interval_seconds(other)
        return self

    def __mul__(self, other: int | float) -> TicTocInterval:
        """Implement `__mul__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        return type(self)(self._seconds * float(other))

    def __rmul__(self, other: int | float) -> TicTocInterval:
        """Implement `__rmul__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        return self.__mul__(other)

    def __imul__(self, other: int | float) -> TicTocInterval:
        """Implement `__imul__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        self._seconds *= float(other)
        return self

    def __truediv__(self, other: object) -> TicTocInterval | float | NotImplementedType:
        """Implement `__truediv__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if isinstance(other, (TicTocInterval, datetime_timedelta)):
            denominator = _coerce_interval_seconds(other)
            return self._seconds / denominator
        if isinstance(other, Real):
            return type(self)(self._seconds / float(other))
        return NotImplemented

    def __itruediv__(self, other: object) -> TicTocInterval:
        """Implement `__itruediv__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if not isinstance(other, Real):
            raise TypeError(f"Cannot divide TicTocInterval by {type(other).__name__!r}.")
        self._seconds /= float(other)
        return self

    def __neg__(self) -> TicTocInterval:
        """Implement `__neg__`.

        Returns:
            TODO describe return value.

        """
        return type(self)(-self._seconds)

    def __pos__(self) -> TicTocInterval:
        """Implement `__pos__`.

        Returns:
            TODO describe return value.

        """
        return self.copy()

    def __abs__(self) -> TicTocInterval:
        """Implement `__abs__`.

        Returns:
            TODO describe return value.

        """
        return type(self)(abs(self._seconds))

    def __eq__(self, other: object) -> bool:
        """Implement `__eq__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        try:
            return self._seconds == _coerce_interval_seconds(other)
        except TypeError:
            return False

    def __lt__(self, other: object) -> bool:
        """Implement `__lt__`.

        Args:
            other: TODO describe other.

        Returns:
            TODO describe return value.

        """
        if _can_coerce_interval(other):
            return self._seconds < _coerce_interval_seconds(other)
        return NotImplemented


def _coerce_interval_seconds(value: object) -> float:
    # Internal helper: coerce interval seconds.
    """Internal helper: coerce interval seconds."""
    if value is None:
        return 0.0
    if isinstance(value, TicTocInterval):
        return value.seconds
    if isinstance(value, datetime_timedelta):
        return value.total_seconds()
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, str):
        return parse_interval_seconds(value)
    raise TypeError(f"Cannot convert {type(value).__name__!r} to TicTocInterval.")


def _split_components(seconds: float) -> tuple[int, int, int, int, int]:
    # Internal helper: split components.
    """Internal helper: split components."""
    delta = datetime_timedelta(seconds=abs(seconds))
    days = delta.days
    whole_seconds = delta.seconds
    hours, whole_seconds = divmod(whole_seconds, 3_600)
    minutes, whole_seconds = divmod(whole_seconds, 60)
    return days, hours, minutes, whole_seconds, delta.microseconds


def _can_coerce_interval(value: object) -> bool:
    # Internal helper: can coerce interval.
    """Internal helper: can coerce interval."""
    return value is None or isinstance(value, (TicTocInterval, datetime_timedelta, Real, str))
