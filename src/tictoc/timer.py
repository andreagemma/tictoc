"""Main timer and progress logger."""

from __future__ import annotations

import logging
import string
import time as _time
from dataclasses import dataclass
from datetime import datetime
from functools import total_ordering
from math import isfinite
from numbers import Real
from typing import Any, Callable, Iterable, Literal

from .interval import TicTocInterval
from .speed import TicTocSpeed
from .time import TicTocTime

EstimationMethod = Literal["origin", "average", "tic", "last", "instant", "moving", "rolling", "ema"]
Clock = Callable[[], float]

_DEFAULT_FORMAT = "elapsed={et}"
_DEFAULT_PROGRESS_FORMAT = "{i} elapsed={et} speed={v}"
_DEFAULT_TOTAL_FORMAT = "{i}/{tot} elapsed={et} eta={rt} total={tt} end={end} speed={v}"
_LOGGING_KWARGS = {"exc_info", "stack_info", "stacklevel", "extra"}


@dataclass(frozen=True, slots=True)
class _ProgressSample:
    counter: float
    timestamp: float


@total_ordering
class TicToc(logging.LoggerAdapter):
    """Timer, progress estimator and logging adapter.

    ``tic`` resets the timer and returns ``self`` for method chaining. Named
    timers are created with ``tic("name")`` or ``named("name")`` and can then
    be accessed with ``timer["name"]``.
    """

    default_datetime_format = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        start: int | float | str | datetime | TicTocTime | "TicToc" | None = None,
        *,
        i: int | float | None = None,
        total: int | float | None = None,
        tot: int | float | None = None,
        logger: logging.Logger | None = None,
        logger_name: str = "tictoc",
        info_format: str | None = None,
        progress_format: str | None = None,
        total_format: str | None = None,
        datetime_format: str | None = None,
        clock: Clock | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        actual_logger = logger if logger is not None else logging.getLogger(logger_name)
        super().__init__(actual_logger, extra or {})

        self._clock: Clock = clock or _time.time
        self.info_format = info_format or _DEFAULT_FORMAT
        self.progress_format = progress_format or _DEFAULT_PROGRESS_FORMAT
        self.total_format = total_format or _DEFAULT_TOTAL_FORMAT
        self.datetime_format = datetime_format or self.default_datetime_format

        if isinstance(start, TicToc):
            self._origin = start._origin.copy()
            self._start = start._start.copy()
            self.counter = start.counter if i is None else float(i)
            self.total = start.total if total is None and tot is None else _coerce_optional_float(total, tot)
            self._samples = list(start._samples)
            self._named = {key: value.copy() for key, value in start._named.items()}
            if logger is None:
                self.logger = start.logger
            return

        timestamp = self._clock() if start is None else TicTocTime(start, fmt=self.datetime_format).timestamp
        self._origin = TicTocTime(timestamp, fmt=self.datetime_format)
        self._start = TicTocTime(timestamp, fmt=self.datetime_format)
        self.counter = None if i is None else float(i)
        self.total = _coerce_optional_float(total, tot)
        self._samples: list[_ProgressSample] = []
        self._named: dict[str, TicToc] = {}
        if self.counter is not None:
            self._append_sample(self.counter, timestamp)

    @classmethod
    def now(cls, **kwargs: Any) -> "TicToc":
        return cls(None, **kwargs)

    @classmethod
    def from_timestamp(cls, value: int | float, **kwargs: Any) -> "TicToc":
        return cls(value, **kwargs)

    @classmethod
    def from_datetime(cls, value: datetime, **kwargs: Any) -> "TicToc":
        return cls(value, **kwargs)

    @classmethod
    def from_string(cls, value: str, **kwargs: Any) -> "TicToc":
        return cls(value, **kwargs)

    def copy(self) -> "TicToc":
        return type(self)(
            self,
            logger=self.logger,
            info_format=self.info_format,
            progress_format=self.progress_format,
            total_format=self.total_format,
            datetime_format=self.datetime_format,
            clock=self._clock,
            extra=dict(self.extra),
        )

    def __copy__(self) -> "TicToc":
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> "TicToc":
        return self.copy()

    def __getitem__(self, name: str) -> "TicToc":
        return self._named[name]

    def __contains__(self, name: object) -> bool:
        return name in self._named

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._named.keys())

    @property
    def datetime(self) -> datetime:
        return self.start_time().datetime

    def to_datetime(self) -> datetime:
        return self.datetime

    def named(self, name: str, *, create: bool = True) -> "TicToc":
        if name not in self._named:
            if not create:
                raise KeyError(name)
            self._named[name] = type(self)(
                self._clock(),
                total=self.total,
                logger=self.logger,
                info_format=self.info_format,
                progress_format=self.progress_format,
                total_format=self.total_format,
                datetime_format=self.datetime_format,
                clock=self._clock,
                extra=dict(self.extra),
            )
        return self._named[name]

    def tic(
        self,
        name: str | None = None,
        *,
        i: int | float | None = None,
        total: int | float | None = None,
        tot: int | float | None = None,
        reset_origin: bool = False,
    ) -> "TicToc":
        """Reset the start instant and return ``self`` for method chaining."""

        if name is not None:
            self.named(name).tic(i=i, total=total, tot=tot, reset_origin=reset_origin)
            return self

        timestamp = self._clock()
        self._start = TicTocTime(timestamp, fmt=self.datetime_format)
        if reset_origin:
            self._origin = self._start.copy()
        new_total = _coerce_optional_float(total, tot)
        if new_total is not None:
            self.total = new_total
        self.counter = None if i is None else float(i)
        self._samples.clear()
        if self.counter is not None:
            self._append_sample(self.counter, timestamp)
        return self

    def update(
        self,
        i: int | float | None = None,
        *,
        total: int | float | None = None,
        tot: int | float | None = None,
        name: str | None = None,
    ) -> "TicToc":
        if name is not None:
            self.named(name).update(i=i, total=total, tot=tot)
            return self

        new_total = _coerce_optional_float(total, tot)
        if new_total is not None:
            self.total = new_total
        if i is not None:
            self.counter = float(i)
            self._append_sample(self.counter, self._clock())
        return self

    def toc(self, name: str | None = None) -> TicTocInterval:
        return self.elapsed_time(name=name)

    def elapsed_time(self, name: str | None = None) -> TicTocInterval:
        if name is not None:
            return self.named(name, create=False).elapsed_time()
        return TicTocInterval(self._clock() - self._start.timestamp)

    def elapsed_origin_time(self, name: str | None = None) -> TicTocInterval:
        if name is not None:
            return self.named(name, create=False).elapsed_origin_time()
        return TicTocInterval(self._clock() - self._origin.timestamp)

    def start_time(self, name: str | None = None) -> TicTocTime:
        if name is not None:
            return self.named(name, create=False).start_time()
        return self._start.copy()

    def origin_time(self, name: str | None = None) -> TicTocTime:
        if name is not None:
            return self.named(name, create=False).origin_time()
        return self._origin.copy()

    def speed(
        self,
        i: int | float | None = None,
        *,
        method: EstimationMethod = "origin",
        n: int | None = None,
        name: str | None = None,
    ) -> TicTocSpeed:
        if name is not None:
            return self.named(name, create=False).speed(i=i, method=method, n=n)
        resolved_i = self._resolve_counter(i)
        if resolved_i is None:
            return TicTocSpeed(0)
        if i is not None:
            self.update(i)
        return TicTocSpeed(self._estimate_rate(resolved_i, method=method, n=n))

    def remaining_time(
        self,
        i: int | float | None = None,
        total: int | float | None = None,
        *,
        tot: int | float | None = None,
        method: EstimationMethod = "origin",
        n: int | None = None,
        name: str | None = None,
    ) -> TicTocInterval:
        if name is not None:
            return self.named(name, create=False).remaining_time(i=i, total=total, tot=tot, method=method, n=n)

        resolved_i = self._resolve_counter(i)
        resolved_total = self._resolve_total(total, tot)
        if resolved_i is None or resolved_total is None:
            return TicTocInterval(0)
        self.update(i, total=total, tot=tot)
        remaining_steps = max(resolved_total - resolved_i, 0.0)
        rate = self._estimate_rate(resolved_i, method=method, n=n)
        if rate <= 0 or not isfinite(rate):
            return TicTocInterval(0)
        return TicTocInterval(remaining_steps / rate)

    def total_time(
        self,
        i: int | float | None = None,
        total: int | float | None = None,
        *,
        tot: int | float | None = None,
        method: EstimationMethod = "origin",
        n: int | None = None,
        name: str | None = None,
    ) -> TicTocInterval:
        if name is not None:
            return self.named(name, create=False).total_time(i=i, total=total, tot=tot, method=method, n=n)
        return self.elapsed_time() + self.remaining_time(i=i, total=total, tot=tot, method=method, n=n)

    def end_time(
        self,
        i: int | float | None = None,
        total: int | float | None = None,
        *,
        tot: int | float | None = None,
        method: EstimationMethod = "origin",
        n: int | None = None,
        name: str | None = None,
    ) -> TicTocTime:
        if name is not None:
            return self.named(name, create=False).end_time(i=i, total=total, tot=tot, method=method, n=n)
        return TicTocTime(self._clock(), fmt=self.datetime_format) + self.remaining_time(
            i=i,
            total=total,
            tot=tot,
            method=method,
            n=n,
        )

    def percent(
        self,
        i: int | float | None = None,
        total: int | float | None = None,
        *,
        tot: int | float | None = None,
    ) -> float | None:
        resolved_i = self._resolve_counter(i)
        resolved_total = self._resolve_total(total, tot)
        if resolved_i is None or resolved_total in (None, 0):
            return None
        return 100.0 * resolved_i / resolved_total

    def format_log(
        self,
        template: str | None = None,
        *,
        i: int | float | None = None,
        total: int | float | None = None,
        tot: int | float | None = None,
        method: EstimationMethod = "origin",
        n: int | None = None,
        name: str | None = None,
        datetime_format: str | None = None,
        **values: Any,
    ) -> str:
        target = self.named(name, create=False) if name is not None else self
        target.update(i=i, total=total, tot=tot)

        resolved_i = target.counter
        resolved_total = target.total
        if template is None:
            if resolved_total is not None:
                template = target.total_format
            elif resolved_i is not None:
                template = target.progress_format
            else:
                template = target.info_format

        mapping = target._format_values(
            i=resolved_i,
            total=resolved_total,
            method=method,
            n=n,
            name=name,
            datetime_format=datetime_format,
        )
        mapping.update(values)
        return _SafeFormatDict(mapping).format(template)

    def str_info(self, *args: Any, **kwargs: Any) -> str:
        return self.format_log(*args, **kwargs)

    def debug(self, msg: str | None = None, *args: Any, **kwargs: Any) -> "TicToc":
        return self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str | None = None, *args: Any, **kwargs: Any) -> "TicToc":
        return self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str | None = None, *args: Any, **kwargs: Any) -> "TicToc":
        return self.log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str | None = None, *args: Any, **kwargs: Any) -> "TicToc":
        return self.log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str | None = None, *args: Any, **kwargs: Any) -> "TicToc":
        return self.log(logging.CRITICAL, msg, *args, **kwargs)

    def exception(self, msg: str | None = None, *args: Any, **kwargs: Any) -> "TicToc":
        kwargs.setdefault("exc_info", True)
        return self.log(logging.ERROR, msg, *args, **kwargs)

    def log(self, level: int, msg: str | None = None, *args: Any, **kwargs: Any) -> "TicToc":
        each = kwargs.pop("each", None)
        i = kwargs.pop("i", None)
        total = kwargs.pop("total", None)
        tot = kwargs.pop("tot", None)
        method = kwargs.pop("method", "origin")
        n = kwargs.pop("n", None)
        name = kwargs.pop("name", None)
        datetime_format = kwargs.pop("datetime_format", None)

        log_kwargs, format_values = _split_log_kwargs(kwargs)
        resolved_i = i if i is not None else (self.named(name, create=False).counter if name is not None else self.counter)
        if not _should_log(each, resolved_i):
            return self

        message = self.format_log(
            msg,
            i=i,
            total=total,
            tot=tot,
            method=method,
            n=n,
            name=name,
            datetime_format=datetime_format,
            **format_values,
        )
        super().log(level, message, *args, **log_kwargs)
        return self

    def humanize(self) -> str:
        return self.elapsed_time().humanize()

    def __int__(self) -> int:
        return int(self._start)

    def __float__(self) -> float:
        return float(self._start)

    def __bool__(self) -> bool:
        return bool(self._start)

    def __str__(self) -> str:
        return self.humanize()

    def __repr__(self) -> str:
        return (
            f"TicToc(start={self._start.timestamp!r}, total={self.total!r}, "
            f"counter={self.counter!r}, names={self.names!r})"
        )

    def __format__(self, format_spec: str) -> str:
        if format_spec in ("", "human"):
            return str(self)
        return format(self.elapsed_time().seconds, format_spec)

    def __eq__(self, other: object) -> bool:
        try:
            return float(self) == _coerce_compare_timestamp(other)
        except TypeError:
            return False

    def __lt__(self, other: object) -> bool:
        try:
            return float(self) < _coerce_compare_timestamp(other)
        except TypeError:
            return NotImplemented  # type: ignore[return-value]

    def _append_sample(self, counter: float, timestamp: float) -> None:
        if self._samples and self._samples[-1].counter == counter:
            return
        self._samples.append(_ProgressSample(counter, timestamp))

    def _resolve_counter(self, i: int | float | None) -> float | None:
        if i is not None:
            return float(i)
        return self.counter

    def _resolve_total(self, total: int | float | None, tot: int | float | None) -> float | None:
        return self.total if total is None and tot is None else _coerce_optional_float(total, tot)

    def _estimate_rate(self, i: float, *, method: EstimationMethod, n: int | None) -> float:
        normalized = _normalize_method(method)
        now = self._clock()
        if not self._samples or self._samples[-1].counter != i:
            self._append_sample(i, now)

        if normalized == "last":
            return self._last_rate(i)
        if normalized == "moving":
            return self._moving_rate(i, n=n or 5)
        if normalized == "ema":
            return self._ema_rate(i, n=n or 5)
        return self._origin_rate(i, now=now)

    def _origin_rate(self, i: float, *, now: float | None = None) -> float:
        timestamp = self._clock() if now is None else now
        elapsed = timestamp - self._start.timestamp
        if elapsed <= 0 or i <= 0:
            return 0.0
        return i / elapsed

    def _last_rate(self, i: float) -> float:
        samples = _different_counter_tail(self._samples)
        if len(samples) < 2:
            return self._origin_rate(i)
        previous, current = samples[-2], samples[-1]
        return _rate_between(previous, current, fallback=self._origin_rate(i))

    def _moving_rate(self, i: float, *, n: int) -> float:
        samples = _different_counter_tail(self._samples)
        if len(samples) < 2:
            return self._origin_rate(i)
        window = samples[-max(n, 2) :]
        return _rate_between(window[0], window[-1], fallback=self._origin_rate(i))

    def _ema_rate(self, i: float, *, n: int) -> float:
        samples = _different_counter_tail(self._samples)
        if len(samples) < 2:
            return self._origin_rate(i)
        alpha = 2.0 / (max(n, 1) + 1.0)
        ema: float | None = None
        for previous, current in zip(samples, samples[1:]):
            rate = _rate_between(previous, current, fallback=0.0)
            if rate <= 0:
                continue
            ema = rate if ema is None else alpha * rate + (1.0 - alpha) * ema
        return self._origin_rate(i) if ema is None else ema

    def _format_values(
        self,
        *,
        i: float | None,
        total: float | None,
        method: EstimationMethod,
        n: int | None,
        name: str | None,
        datetime_format: str | None,
    ) -> dict[str, Any]:
        elapsed = self.elapsed_time()
        elapsed_origin = self.elapsed_origin_time()
        speed = self.speed(method=method, n=n)
        remaining = self.remaining_time(total=total, method=method, n=n)
        total_interval = self.total_time(total=total, method=method, n=n)
        end = self.end_time(total=total, method=method, n=n)
        start = self.start_time()
        origin = self.origin_time()
        percent = self.percent(total=total)
        display_i = _friendly_number(i)
        display_total = _friendly_number(total)

        fmt = datetime_format or self.datetime_format
        values: dict[str, Any] = {
            "i": display_i,
            "counter": display_i,
            "tot": display_total,
            "total": display_total,
            "name": name,
            "percent": percent,
            "percent_str": "" if percent is None else f"{percent:.1f}%",
            "elapsed_time": elapsed,
            "et": elapsed,
            "elapsed_origin_time": elapsed_origin,
            "eot": elapsed_origin,
            "remaining_time": remaining,
            "rt": remaining,
            "total_time": total_interval,
            "tt": total_interval,
            "speed": speed,
            "v": speed,
            "start_time": start,
            "start": start,
            "origin_time": origin,
            "origin": origin,
            "end_time": end,
            "end": end,
            "start_str": start.to_string(fmt),
            "origin_str": origin.to_string(fmt),
            "end_str": end.to_string(fmt),
        }
        _add_interval_aliases(values, "et", elapsed)
        _add_interval_aliases(values, "elapsed_time", elapsed)
        _add_interval_aliases(values, "eot", elapsed_origin)
        _add_interval_aliases(values, "elapsed_origin_time", elapsed_origin)
        _add_interval_aliases(values, "rt", remaining)
        _add_interval_aliases(values, "remaining_time", remaining)
        _add_interval_aliases(values, "tt", total_interval)
        _add_interval_aliases(values, "total_time", total_interval)
        _add_speed_aliases(values, "v", speed)
        _add_speed_aliases(values, "speed", speed)
        return values


class _SafeFormatDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"

    def format(self, template: str) -> str:
        formatter = string.Formatter()
        parts: list[str] = []
        for literal, field_name, format_spec, conversion in formatter.parse(template):
            parts.append(literal)
            if field_name is None:
                continue
            value = self.get(field_name, "{" + field_name + "}")
            if conversion == "s":
                value = str(value)
            elif conversion == "r":
                value = repr(value)
            elif conversion == "a":
                value = ascii(value)
            parts.append(format(value, format_spec) if format_spec else str(value))
        return "".join(parts)


def _add_interval_aliases(values: dict[str, Any], prefix: str, interval: TicTocInterval) -> None:
    values[f"{prefix}_s"] = interval.seconds
    values[f"{prefix}_sec"] = interval.seconds
    values[f"{prefix}_seconds"] = interval.seconds
    values[f"{prefix}_m"] = interval.minutes
    values[f"{prefix}_min"] = interval.minutes
    values[f"{prefix}_minutes"] = interval.minutes
    values[f"{prefix}_h"] = interval.hours
    values[f"{prefix}_hours"] = interval.hours
    values[f"{prefix}_d"] = interval.days
    values[f"{prefix}_days"] = interval.days
    values[f"{prefix}_str"] = str(interval)


def _add_speed_aliases(values: dict[str, Any], prefix: str, speed: TicTocSpeed) -> None:
    values[f"{prefix}_s"] = speed.steps_per_second
    values[f"{prefix}_sec"] = speed.steps_per_second
    values[f"{prefix}_m"] = speed.steps_per_minute
    values[f"{prefix}_min"] = speed.steps_per_minute
    values[f"{prefix}_h"] = speed.steps_per_hour
    values[f"{prefix}_d"] = speed.steps_per_day
    values[f"{prefix}_str"] = str(speed)


def _coerce_optional_float(total: int | float | None, tot: int | float | None) -> float | None:
    value = total if total is not None else tot
    return None if value is None else float(value)


def _friendly_number(value: float | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if float(value).is_integer() else value


def _coerce_compare_timestamp(value: object) -> float:
    if isinstance(value, TicToc):
        return float(value)
    if isinstance(value, TicTocTime):
        return value.timestamp
    if isinstance(value, datetime):
        return value.timestamp()
    if isinstance(value, Real):
        return float(value)
    raise TypeError(f"Cannot compare TicToc with {type(value).__name__!r}.")


def _normalize_method(method: EstimationMethod) -> Literal["origin", "last", "moving", "ema"]:
    aliases: dict[str, Literal["origin", "last", "moving", "ema"]] = {
        "origin": "origin",
        "average": "origin",
        "tic": "origin",
        "last": "last",
        "instant": "last",
        "moving": "moving",
        "rolling": "moving",
        "ema": "ema",
    }
    try:
        return aliases[method]
    except KeyError as exc:
        raise ValueError(f"Unsupported estimation method: {method!r}.") from exc


def _different_counter_tail(samples: Iterable[_ProgressSample]) -> list[_ProgressSample]:
    filtered: list[_ProgressSample] = []
    for sample in samples:
        if filtered and filtered[-1].counter == sample.counter:
            continue
        filtered.append(sample)
    return filtered


def _rate_between(previous: _ProgressSample, current: _ProgressSample, *, fallback: float) -> float:
    delta_counter = current.counter - previous.counter
    delta_time = current.timestamp - previous.timestamp
    if delta_counter <= 0 or delta_time <= 0:
        return fallback
    return delta_counter / delta_time


def _split_log_kwargs(kwargs: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    log_kwargs: dict[str, Any] = {}
    format_values: dict[str, Any] = {}
    for key, value in kwargs.items():
        if key in _LOGGING_KWARGS:
            log_kwargs[key] = value
        else:
            format_values[key] = value
    return log_kwargs, format_values


def _should_log(each: int | float | None, i: int | float | None) -> bool:
    if each in (None, 0):
        return True
    if i is None:
        return True
    return float(i) % float(each) == 0
