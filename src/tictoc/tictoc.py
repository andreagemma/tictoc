"""Compatibility module for ``from tictoc.tictoc import TicToc``."""

from __future__ import annotations

from ._version import __version__
from .timer import TicToc

__all__ = ["TicToc", "__version__"]
