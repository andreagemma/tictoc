"""Parsing helpers for intervals and timestamps."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Final

from ._optional import import_optional

_INTERVAL_PART_RE: Final[re.Pattern[str]] = re.compile(
    r"(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*"
    r"(?P<unit>microseconds?|usec|us|milliseconds?|msec|ms|"
    r"seconds?|secs?|s|minutes?|mins?|m(?!s)|hours?|hrs?|h|days?|d|weeks?|w)",
    re.IGNORECASE,
)

_UNIT_SECONDS: Final[dict[str, float]] = {
    "w": 604_800.0,
    "week": 604_800.0,
    "weeks": 604_800.0,
    "d": 86_400.0,
    "day": 86_400.0,
    "days": 86_400.0,
    "h": 3_600.0,
    "hr": 3_600.0,
    "hrs": 3_600.0,
    "hour": 3_600.0,
    "hours": 3_600.0,
    "m": 60.0,
    "min": 60.0,
    "mins": 60.0,
    "minute": 60.0,
    "minutes": 60.0,
    "s": 1.0,
    "sec": 1.0,
    "secs": 1.0,
    "second": 1.0,
    "seconds": 1.0,
    "ms": 0.001,
    "msec": 0.001,
    "millisecond": 0.001,
    "milliseconds": 0.001,
    "us": 0.000001,
    "usec": 0.000001,
    "microsecond": 0.000001,
    "microseconds": 0.000001,
}

_COMMON_DATETIME_FORMATS: Final[tuple[str, ...]] = (
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%Y/%m/%d",
)


def parse_interval_seconds(value: str) -> float:
    """Parse common interval strings into seconds."""

    text = value.strip()
    if not text:
        raise ValueError("Interval string cannot be empty.")

    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", text):
        return float(text)

    colon_seconds = _parse_colon_interval(text)
    if colon_seconds is not None:
        return colon_seconds

    iso_seconds = _parse_iso_duration(text)
    if iso_seconds is not None:
        return iso_seconds

    total = 0.0
    position = 0
    matched = False
    for match in _INTERVAL_PART_RE.finditer(text):
        gap = text[position : match.start()]
        if gap.strip(" ,;"):
            raise ValueError(f"Cannot parse interval segment: {gap!r}.")
        unit = match.group("unit").lower()
        total += float(match.group("value")) * _UNIT_SECONDS[unit]
        position = match.end()
        matched = True

    if matched and not text[position:].strip(" ,;"):
        return total

    raise ValueError(f"Unsupported interval string: {value!r}.")


def _parse_colon_interval(text: str) -> float | None:
    sign = -1.0 if text.startswith("-") else 1.0
    unsigned = text[1:] if text[:1] in "+-" else text
    day_part = 0.0
    if "." in unsigned and re.fullmatch(r"\d+\.\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?", unsigned):
        day_text, unsigned = unsigned.split(".", 1)
        day_part = float(day_text)

    parts = unsigned.split(":")
    if len(parts) not in (2, 3):
        return None
    if not all(re.fullmatch(r"\d+(?:\.\d+)?", part) for part in parts):
        return None

    numbers = [float(part) for part in parts]
    if len(numbers) == 2:
        minutes, seconds = numbers
        hours = 0.0
    else:
        hours, minutes, seconds = numbers
    return sign * (day_part * 86_400 + hours * 3_600 + minutes * 60 + seconds)


def _parse_iso_duration(text: str) -> float | None:
    pattern = re.compile(
        r"^(?P<sign>[+-])?P"
        r"(?:(?P<days>\d+(?:\.\d+)?)D)?"
        r"(?:T"
        r"(?:(?P<hours>\d+(?:\.\d+)?)H)?"
        r"(?:(?P<minutes>\d+(?:\.\d+)?)M)?"
        r"(?:(?P<seconds>\d+(?:\.\d+)?)S)?"
        r")?$",
        re.IGNORECASE,
    )
    match = pattern.fullmatch(text)
    if match is None:
        return None
    total = 0.0
    for name, multiplier in (("days", 86_400), ("hours", 3_600), ("minutes", 60), ("seconds", 1)):
        raw = match.group(name)
        if raw is not None:
            total += float(raw) * multiplier
    return -total if match.group("sign") == "-" else total


def parse_datetime(value: str, *, fmt: str | None = None) -> datetime:
    """Parse common datetime strings, lazily falling back to python-dateutil."""

    text = value.strip()
    if not text:
        raise ValueError("Datetime string cannot be empty.")

    if fmt is not None:
        return datetime.strptime(text, fmt)

    iso_text = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        return datetime.fromisoformat(iso_text)
    except ValueError:
        pass

    for candidate in _COMMON_DATETIME_FORMATS:
        try:
            return datetime.strptime(text, candidate)
        except ValueError:
            continue

    parser = import_optional("dateutil.parser", "python -m pip install 'tictoc[dateutil]'")
    return parser.parse(text)  # type: ignore[attr-defined,no-any-return]
