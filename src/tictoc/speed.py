"""Execution speed value object."""

from __future__ import annotations

from datetime import timedelta
from functools import total_ordering
from math import isfinite
from numbers import Real
from typing import Any, Literal

from ._human import compact_number
from .interval import TicTocInterval

SpeedUnit = Literal["second", "minute", "hour", "day"]


@total_ordering
class TicTocSpeed:
    """Processing speed stored as steps per second."""

    __slots__ = ("_steps_per_second", "_steps", "_interval")

    def __init__(
        self,
        value: int | float | "TicTocSpeed" = 0.0,
        *,
        steps: int | float | None = None,
        interval: int | float | TicTocInterval | timedelta | None = None,
        per: SpeedUnit = "second",
    ) -> None:
        if isinstance(value, TicTocSpeed):
            self._steps_per_second = value.steps_per_second
            self._steps = value.steps
            self._interval = value.interval.copy()
            return

        if steps is not None or interval is not None:
            if steps is None or interval is None:
                raise ValueError("Both 'steps' and 'interval' are required to compute speed.")
            interval_obj = TicTocInterval(interval)
            seconds = interval_obj.seconds
            self._steps_per_second = float(steps) / seconds if seconds > 0 else 0.0
            self._steps = float(steps)
            self._interval = interval_obj
            return

        multiplier = {"second": 1.0, "minute": 1.0 / 60.0, "hour": 1.0 / 3_600.0, "day": 1.0 / 86_400.0}
        if per not in multiplier:
            raise ValueError(f"Unsupported speed unit: {per!r}.")
        self._steps_per_second = float(value) * multiplier[per]
        self._steps = 0.0
        self._interval = TicTocInterval(0)

    @classmethod
    def from_steps(
        cls,
        steps: int | float,
        interval: int | float | TicTocInterval | timedelta,
    ) -> "TicTocSpeed":
        return cls(steps=steps, interval=interval)

    @classmethod
    def per_second(cls, value: int | float) -> "TicTocSpeed":
        return cls(value, per="second")

    @classmethod
    def per_minute(cls, value: int | float) -> "TicTocSpeed":
        return cls(value, per="minute")

    @classmethod
    def per_hour(cls, value: int | float) -> "TicTocSpeed":
        return cls(value, per="hour")

    @classmethod
    def per_day(cls, value: int | float) -> "TicTocSpeed":
        return cls(value, per="day")

    def copy(self) -> "TicTocSpeed":
        return type(self)(self)

    def __copy__(self) -> "TicTocSpeed":
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> "TicTocSpeed":
        return self.copy()

    @property
    def steps_per_second(self) -> float:
        return self._steps_per_second

    @property
    def per_sec(self) -> float:
        return self._steps_per_second

    @property
    def at_seconds(self) -> float:
        return self._steps_per_second

    @property
    def steps_per_minute(self) -> float:
        return self._steps_per_second * 60.0

    @property
    def per_min(self) -> float:
        return self.steps_per_minute

    @property
    def at_minutes(self) -> float:
        return self.steps_per_minute

    @property
    def steps_per_hour(self) -> float:
        return self._steps_per_second * 3_600.0

    @property
    def per_hour_value(self) -> float:
        return self.steps_per_hour

    @property
    def at_hours(self) -> float:
        return self.steps_per_hour

    @property
    def steps_per_day(self) -> float:
        return self._steps_per_second * 86_400.0

    @property
    def at_days(self) -> float:
        return self.steps_per_day

    @property
    def steps(self) -> float:
        return self._steps

    @property
    def interval(self) -> TicTocInterval:
        return self._interval.copy()

    def in_unit(self, unit: SpeedUnit) -> float:
        if unit == "second":
            return self.steps_per_second
        if unit == "minute":
            return self.steps_per_minute
        if unit == "hour":
            return self.steps_per_hour
        if unit == "day":
            return self.steps_per_day
        raise ValueError(f"Unsupported speed unit: {unit!r}.")

    def humanize(self, *, label: str = "step") -> str:
        value, suffix = _best_speed_unit(self._steps_per_second)
        plural_label = label if abs(value) == 1 else f"{label}s"
        return f"{compact_number(value)} {plural_label}/{suffix}"

    def __int__(self) -> int:
        return int(self._steps_per_second)

    def __float__(self) -> float:
        return float(self._steps_per_second)

    def __bool__(self) -> bool:
        return bool(self._steps_per_second)

    def __str__(self) -> str:
        return self.humanize()

    def __repr__(self) -> str:
        return f"TicTocSpeed({self._steps_per_second!r})"

    def __format__(self, format_spec: str) -> str:
        if format_spec in ("", "human"):
            return str(self)
        if format_spec in ("s", "sec", "second"):
            return str(self.steps_per_second)
        if format_spec in ("m", "min", "minute"):
            return str(self.steps_per_minute)
        if format_spec in ("h", "hour"):
            return str(self.steps_per_hour)
        if format_spec in ("d", "day"):
            return str(self.steps_per_day)
        return format(self._steps_per_second, format_spec)

    def __hash__(self) -> int:
        return hash(self._steps_per_second)

    def __eq__(self, other: object) -> bool:
        try:
            return self._steps_per_second == _coerce_speed_value(other)
        except TypeError:
            return False

    def __lt__(self, other: object) -> bool:
        try:
            return self._steps_per_second < _coerce_speed_value(other)
        except TypeError:
            return NotImplemented  # type: ignore[return-value]


def _coerce_speed_value(value: object) -> float:
    if isinstance(value, TicTocSpeed):
        return value.steps_per_second
    if isinstance(value, Real):
        return float(value)
    raise TypeError(f"Cannot convert {type(value).__name__!r} to TicTocSpeed.")


def _best_speed_unit(per_second: float) -> tuple[float, str]:
    if not isfinite(per_second):
        return per_second, "s"
    candidates = (
        (per_second, "s"),
        (per_second * 60.0, "min"),
        (per_second * 3_600.0, "h"),
        (per_second * 86_400.0, "day"),
    )
    for value, suffix in candidates:
        if abs(value) >= 1:
            return value, suffix
    return candidates[-1]
