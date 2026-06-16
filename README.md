# tictoc

`tictoc` helps you measure elapsed time in Python programs, estimate how long a
loop or job still needs, inspect processing speed, and log progress messages
with readable timing information.

The main class is `TicToc`. It starts counting as soon as you create it.

```python
from tictoc import TicToc

timer = TicToc()

# Code you want to measure

print(timer.toc())
```

Example output:

```text
00:01:12
```

For a complete guide to all classes, methods, placeholders, parsing formats,
casts, comparisons, and arithmetic operations, see
[docs/usage.md](docs/usage.md).

## Installation

Install from PyPI, once the package is published:

```bash
python -m pip install tictoc
```

Install from a GitHub release:

```bash
python -m pip install "https://github.com/andreagemma/tictoc/releases/download/v0.1.0/tictoc-0.1.0-py3-none-any.whl"
```

Install from a local source checkout:

```bash
python -m pip install -e .
```

For more flexible date string parsing, install the optional parser support:

```bash
python -m pip install "tictoc[dateutil]"
```

## Quick Start

### Measure Elapsed Time

```python
from tictoc import TicToc

tt = TicToc()

# Work...

elapsed = tt.toc()
print(elapsed)          # Human-readable value
print(elapsed.seconds)  # Total seconds
```

`toc()` is an alias for `elapsed_time()`.

```python
tt.elapsed_time()
tt.elapsed_origin_time()
```

`elapsed_time()` measures from the most recent `tic()`.  
`elapsed_origin_time()` measures from the moment the timer was created.

### Reset the Timer

`tic()` resets the start time and returns the same object, so it works well with
method chaining.

```python
tt = TicToc()

tt.tic().info("starting again")
```

### Named Timers

One `TicToc` object can manage multiple independent named timers.

```python
tt = TicToc()

tt.tic("download")
# Download...

tt.tic("parse")
# Parse...

print(tt.toc("download"))
print(tt.toc("parse"))
```

You can also access a named timer directly:

```python
download_timer = tt["download"]
print(download_timer.elapsed_time())
```

## Progress, ETA, and Speed

When you know the total number of steps, `TicToc` can estimate remaining time,
total time, end time, and processing speed.

```python
from tictoc import TicToc

tt = TicToc(total=100)

for i in range(1, 101):
    # Process one step
    if i % 10 == 0:
        print(
            i,
            tt.elapsed_time(),
            tt.remaining_time(i=i),
            tt.total_time(i=i),
            tt.end_time(i=i),
            tt.speed(i=i),
        )
```

Useful methods:

- `remaining_time(i=..., total=...)`: estimate time left.
- `total_time(i=..., total=...)`: estimate total execution time.
- `end_time(i=..., total=...)`: estimate when the job will finish.
- `speed(i=...)`: return a `TicTocSpeed` object.
- `percent(i=..., total=...)`: return completion percentage.

### Estimation Methods

Choose how remaining time should be estimated with `method`.

```python
tt.remaining_time(i=i, total=100, method="origin")
tt.remaining_time(i=i, total=100, method="last")
tt.remaining_time(i=i, total=100, method="moving", n=5)
tt.remaining_time(i=i, total=100, method="ema", n=5)
```

- `origin`: average speed since the latest `tic()`.
- `last`: speed from the latest interval between two updates.
- `moving`: average speed over the latest `n` updates.
- `ema`: exponential moving average over the latest updates.

## Built-In Logging

`TicToc` can also log progress. If you do not pass a logger, it uses an internal
logger named `tictoc`.

```python
import logging
from tictoc import TicToc

logging.basicConfig(level=logging.INFO)

tt = TicToc(total=50)

for i in range(1, 51):
    # Work...
    tt.info("{i}/{tot} elapsed={et} eta={rt} speed={v}", i=i, each=10)
```

`each=10` logs only every 10 steps.

Available logging methods:

```python
tt.debug("...")
tt.info("...")
tt.warning("...")
tt.error("...")
tt.exception("...")
```

You can also pass your own logger:

```python
import logging
from tictoc import TicToc

logger = logging.getLogger("my-job")
tt = TicToc(logger=logger)
```

### Log Placeholders

Progress messages support quick placeholders.

| Placeholder | Meaning |
| --- | --- |
| `{i}` or `{counter}` | current step |
| `{tot}` or `{total}` | total steps |
| `{percent_str}` | formatted percentage |
| `{et}` | elapsed time |
| `{eot}` | elapsed origin time |
| `{rt}` | remaining time |
| `{tt}` | estimated total time |
| `{v}` | speed |
| `{start}` | start time |
| `{origin}` | object creation time |
| `{end}` | estimated end time |

Use suffixes when you want numeric values:

```python
tt.info("elapsed={et_s:.2f}s eta={rt_m:.1f}min speed={v_h:.0f}/h", i=i)
```

Common suffixes:

- `_s`, `_sec`, `_seconds`
- `_m`, `_min`, `_minutes`
- `_h`, `_hours`
- `_d`, `_days`
- `_str`

## Intervals: TicTocInterval

`TicTocInterval` represents a duration.

```python
from datetime import timedelta
from tictoc import TicTocInterval

a = TicTocInterval("1 day 2 hours")
b = TicTocInterval(timedelta(minutes=30))
c = TicTocInterval(10)  # Seconds

print(a + b)
print(c * 3)
print(float(a))         # Total seconds
print(a.total_hours)
print(a.component_days)
```

Accepted formats include:

```python
TicTocInterval("1 day 2 seconds")
TicTocInterval("1d 2h 3m 4s")
TicTocInterval("01:02:03")
TicTocInterval("1.02:00:53")
TicTocInterval("PT1H30M")
```

## Timestamps: TicTocTime

`TicTocTime` represents a point in time.

```python
from datetime import datetime, timedelta
from tictoc import TicTocTime

now = TicTocTime.now()
start = TicTocTime.from_string("2026-06-16 12:00:00")
later = start + timedelta(minutes=10)

print(now)
print(later - start)  # TicTocInterval
print(start.year, start.month, start.day)
print(float(start))   # Unix timestamp
```

You can create a `TicTocTime` from:

```python
TicTocTime.now()
TicTocTime.from_timestamp(1_781_600_000)
TicTocTime.from_datetime(datetime.now())
TicTocTime.from_string("2026-06-16 12:00:00")
```

## Speed: TicTocSpeed

`TicTocSpeed` represents steps per second and gives you ready-to-use
conversions.

```python
from tictoc import TicTocSpeed, TicTocInterval

speed = TicTocSpeed.from_steps(120, TicTocInterval.from_minutes(2))

print(speed)                  # 1 step/s
print(speed.steps_per_second)
print(speed.steps_per_minute)
print(speed.steps_per_hour)
```

## Complete Example

```python
import logging
import time

from tictoc import TicToc

logging.basicConfig(level=logging.INFO, format="%(message)s")

tt = TicToc(total=20)

for i in range(1, 21):
    time.sleep(0.1)
    tt.info(
        "{i}/{tot} ({percent_str}) elapsed={et} eta={rt} end={end} speed={v}",
        i=i,
        each=5,
    )

print("finished in", tt.elapsed_time())
```

Example output:

```text
5/20 (25.0%) elapsed=0.501 s eta=1.5 s end=2026-06-16 12:00:03 speed=10 steps/s
10/20 (50.0%) elapsed=1 s eta=1 s end=2026-06-16 12:00:03 speed=10 steps/s
15/20 (75.0%) elapsed=1.5 s eta=0.5 s end=2026-06-16 12:00:03 speed=10 steps/s
20/20 (100.0%) elapsed=2 s eta=0 s end=2026-06-16 12:00:03 speed=10 steps/s
finished in 2 s
```
