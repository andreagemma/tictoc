"""Human readable formatting utilities used by the public classes."""

from __future__ import annotations

from math import isfinite


def compact_number(value: float, *, digits: int = 3) -> str:
    """Format a number with useful significant digits and no visual noise."""

    if not isfinite(value):
        return str(value)
    abs_value = abs(value)
    if abs_value == 0:
        return "0"
    if abs_value < 0.001:
        return f"{value:.2e}"
    if abs_value < 1:
        return f"{value:.3f}".rstrip("0").rstrip(".")
    if abs_value < 10:
        return f"{value:.2f}".rstrip("0").rstrip(".")
    if abs_value < 100:
        return f"{value:.1f}".rstrip("0").rstrip(".")
    return f"{value:.0f}"


def humanize_seconds(seconds: float) -> str:
    """Return a readable duration, balancing precision and scanability."""

    if not isfinite(seconds):
        return str(seconds)

    sign = "-" if seconds < 0 else ""
    value = abs(seconds)

    if value < 60:
        return f"{sign}{compact_number(value)} s"

    rounded = int(round(value))
    days, remainder = divmod(rounded, 86_400)
    hours, remainder = divmod(remainder, 3_600)
    minutes, secs = divmod(remainder, 60)

    if days:
        return f"{sign}{days}.{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{sign}{hours:02d}:{minutes:02d}:{secs:02d}"
