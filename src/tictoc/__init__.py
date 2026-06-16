"""Public API for the tictoc package."""

from __future__ import annotations

import logging

from .interval import TicTocInterval
from .speed import TicTocSpeed
from .time import TicTocTime
from .timer import TicToc

__all__ = ["TicToc", "TicTocInterval", "TicTocSpeed", "TicTocTime"]

__version__ = "0.1.0"

logging.getLogger(__name__).addHandler(logging.NullHandler())
