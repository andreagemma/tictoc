from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import tictoc
from tictoc._version import __version__


def test_public_version_uses_code_source() -> None:
    assert tictoc.__version__ == __version__
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:[a-zA-Z0-9.+-]*)?", __version__)


def test_version_module_can_be_loaded_directly_from_file() -> None:
    version_file = Path(__file__).resolve().parents[1] / "src" / "tictoc" / "_version.py"
    spec = importlib.util.spec_from_file_location("tictoc._version", version_file)

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert getattr(module, "__version__", "") == __version__
