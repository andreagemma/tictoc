# tictoc

`tictoc` is a small, typed Python library for measuring elapsed time, estimating
remaining time, representing time intervals, handling timestamps, and logging
progress messages.

```python
from tictoc import TicToc

tt = TicToc(total=100)

for i in range(1, 101):
    # do work
    tt.info("{i}/{tot} elapsed={et} eta={rt} speed={v}", i=i, each=10)
```

Core objects:

- `TicToc`: timer, progress estimator and logger adapter.
- `TicTocInterval`: interval in seconds with arithmetic, parsing and humanized
  output.
- `TicTocTime`: timestamp with datetime conversion and interval arithmetic.
- `TicTocSpeed`: processing speed with step/second, step/minute, step/hour and
  step/day views.

Install locally while developing:

```bash
python -m pip install -e .
python -m unittest discover
```

Date parsing uses only the standard library for common formats. If a string is
not recognized, `python-dateutil` is imported lazily only at that moment. Install
the optional extra with:

```bash
python -m pip install "tictoc[dateutil]"
```

## Build and release

The project targets Python 3.10+ and is tested on Python 3.10, 3.11, 3.12,
3.13 and 3.14. Distribution artifacts are built on Python 3.14, the most recent
stable bugfix branch at the time this project was prepared.

Build locally:

```bash
python -m pip install -e ".[build,test]"
python -m unittest discover -v
python -m build
```

Create a release from GitHub:

```bash
git tag v0.1.0
git push origin main --tags
```

The release workflow builds both `sdist` and `wheel`, checks them with `twine`,
and attaches them to the GitHub Release. A remote install from a release asset
looks like:

```bash
python -m pip install "https://github.com/<owner>/<repo>/releases/download/v0.1.0/tictoc-0.1.0-py3-none-any.whl"
```
