"""Helpers for optional runtime dependencies."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType


class OptionalDependencyError(ImportError):
    """Raised only when an optional dependency is actually needed."""


def import_optional(module_name: str, install_hint: str) -> ModuleType:
    """Import an optional dependency and raise a focused error if it is missing."""

    try:
        return import_module(module_name)
    except ModuleNotFoundError as exc:
        root_name = module_name.partition(".")[0]
        if exc.name == root_name:
            message = (
                f"Optional dependency '{module_name}' is required for this input. "
                f"Install it with: {install_hint}"
            )
            raise OptionalDependencyError(message) from exc
        raise
