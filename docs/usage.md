# tictoc Usage Guide

This guide explains how to use `tictoc` in everyday code and how each public
class behaves.

Public API:

```python
from tictoc import TicToc, TicTocInterval, TicTocTime, TicTocSpeed
```

## Installation

Install from PyPI once the package is published:

```bash
python -m pip install tictoc
```

Install from a GitHub release wheel:

```bash
python -m pip install "https://github.com/andreagemma/tictoc/releases/download/v0.1.0/tictoc-0.1.0-py3-none-any.whl"
```

Install from a local checkout:

```bash
python -m pip install -e .
```

Install optional flexible date parsing:

```bash
python -m pip install "tictoc[dateutil]"
```

The optional `python-dateutil` dependency is imported lazily. If you only use
standard date formats, no optional package is needed.

## Core Concepts

`TicToc` is the main timer. It records two important instants:

| Concept | Meaning |
| --- | --- |
| `origin_time()` | when the object was created, or reset with `reset_origin=True` |
| `start_time()` | when the current timing window began |

`tic()` resets `start_time()`.  
`elapsed_time()` measures from `start_time()`.  
`elapsed_origin_time()` measures from `origin_time()`.

Intervals are returned as `TicTocInterval`.  
Times are returned as `TicTocTime`.  
Speeds are returned as `TicTocSpeed`.

## TicToc

Use `TicToc` to measure elapsed time, track progress, estimate ETA, and log
messages.

### Create a Timer

```python
from tictoc import TicToc

tt = TicToc()
```

The timer starts immediately.

You can also provide an initial start time:

```python
from datetime import datetime
from tictoc import TicToc, TicTocTime

TicToc(1_781_600_000)
TicToc(datetime(2026, 6, 16, 12, 0, 0))
TicToc("2026-06-16 12:00:00")
TicToc(TicTocTime.now())
```

Constructor parameters:

| Parameter | Meaning |
| --- | --- |
| `start` | optional start instant |
| `i` | optional initial progress counter |
| `total` or `tot` | optional total number of steps |
| `logger` | external `logging.Logger` |
| `logger_name` | logger name used when no logger is passed |
| `info_format` | default message when there is no progress counter |
| `progress_format` | default message when there is a counter |
| `total_format` | default message when there is a counter and a total |
| `datetime_format` | display format for `TicTocTime` values |

### Measure Elapsed Time

```python
tt = TicToc()

# Do work

elapsed = tt.toc()
print(elapsed)
print(elapsed.seconds)
```

`toc()` is an alias for `elapsed_time()`.

```python
tt.elapsed_time()
tt.elapsed_origin_time()
```

Both methods return `TicTocInterval`.

### Reset Timing with tic()

```python
tt = TicToc()

# First section

tt.tic()

# Second section
```

`tic()` returns `self`, so it supports method chaining:

```python
tt.tic().info("new section started")
```

Useful parameters:

```python
tt.tic(i=0, total=100)
tt.tic(reset_origin=True)
```

`reset_origin=True` resets both `start_time()` and `origin_time()`.

### Named Timers

Named timers let one object track multiple independent operations.

```python
tt = TicToc()

tt.tic("download")
# Download files

tt.tic("parse")
# Parse files

print(tt.toc("download"))
print(tt.toc("parse"))
```

Access a named timer directly:

```python
download = tt["download"]
print(download.elapsed_time())
```

Create or get a named timer:

```python
download = tt.named("download")
```

List names:

```python
print(tt.names)
```

Named timer methods support `name=...` in progress and ETA calls:

```python
tt.remaining_time(i=20, total=100, name="download")
tt.speed(i=20, name="download")
```

### Track Progress

Use `update()` when you want to record progress samples explicitly:

```python
tt = TicToc(total=100)

for i in range(1, 101):
    # Work
    tt.update(i)
```

Most progress methods also update the current counter when you pass `i`.

```python
tt.speed(i=25)
tt.remaining_time(i=25)
```

### Estimate Remaining Time

```python
tt = TicToc(total=100)

for i in range(1, 101):
    # Work
    if i % 10 == 0:
        print(tt.remaining_time(i=i))
```

`remaining_time()` returns `TicTocInterval`.

Parameters:

| Parameter | Meaning |
| --- | --- |
| `i` | current completed step |
| `total` or `tot` | total steps |
| `method` | estimation method |
| `n` | window size for moving methods |
| `name` | named timer to use |

If there is not enough information, the result is a zero interval.

### Estimation Methods

`method` controls how speed and remaining time are estimated.

| Method | Aliases | Meaning |
| --- | --- | --- |
| `origin` | `average`, `tic` | average speed since the current `tic()` |
| `last` | `instant` | speed between the last two progress samples |
| `moving` | `rolling` | average speed over the latest `n` samples |
| `ema` | | exponential moving average over progress samples |

Examples:

```python
tt.remaining_time(i=50, total=100, method="origin")
tt.remaining_time(i=50, total=100, method="last")
tt.remaining_time(i=50, total=100, method="moving", n=5)
tt.remaining_time(i=50, total=100, method="ema", n=5)
```

### Total Time, End Time, Speed, Percent

```python
tt.total_time(i=50, total=100)
tt.end_time(i=50, total=100)
tt.speed(i=50)
tt.percent(i=50, total=100)
```

Return types:

| Method | Return type |
| --- | --- |
| `total_time()` | `TicTocInterval` |
| `end_time()` | `TicTocTime` |
| `speed()` | `TicTocSpeed` |
| `percent()` | `float | None` |

### Start and Origin Times

```python
start = tt.start_time()
origin = tt.origin_time()

print(start.datetime)
print(origin.to_string("%Y-%m-%d"))
```

Both methods return `TicTocTime`.

### Formatting a Log Message without Logging

Use `format_log()` when you want the rendered message but do not want to emit it
through `logging`.

```python
message = tt.format_log(
    "{i}/{tot} elapsed={et} eta={rt} speed={v}",
    i=10,
    total=100,
)
print(message)
```

`str_info()` is an alias for `format_log()`.

### Logging Methods

`TicToc` extends `logging.LoggerAdapter` and returns `self` from logging calls,
so you can chain operations.

```python
import logging
from tictoc import TicToc

logging.basicConfig(level=logging.INFO, format="%(message)s")

tt = TicToc(total=100)
tt.info("{i}/{tot} elapsed={et} eta={rt}", i=10)
```

Available methods:

```python
tt.debug("...")
tt.info("...")
tt.warning("...")
tt.error("...")
tt.critical("...")
tt.exception("...")
tt.log(logging.INFO, "...")
```

Use `each` to log every N steps:

```python
for i in range(1, 101):
    # Work
    tt.info("{i}/{tot} elapsed={et}", i=i, each=10)
```

Pass logging keyword arguments as usual:

```python
tt.info("step {i}", i=10, stacklevel=2)

try:
    raise RuntimeError("failed")
except RuntimeError:
    tt.exception("job failed after {et}")
```

### Log Placeholders

Base placeholders:

| Placeholder | Meaning |
| --- | --- |
| `{i}` or `{counter}` | current counter |
| `{tot}` or `{total}` | total steps |
| `{name}` | timer name |
| `{percent}` | raw percentage |
| `{percent_str}` | formatted percentage |
| `{et}` or `{elapsed_time}` | elapsed time from current `tic()` |
| `{eot}` or `{elapsed_origin_time}` | elapsed time from object creation |
| `{rt}` or `{remaining_time}` | estimated remaining time |
| `{tt}` or `{total_time}` | estimated total time |
| `{v}` or `{speed}` | speed |
| `{start}` or `{start_time}` | current start time |
| `{origin}` or `{origin_time}` | origin time |
| `{end}` or `{end_time}` | estimated end time |
| `{start_str}` | start time formatted as string |
| `{origin_str}` | origin time formatted as string |
| `{end_str}` | end time formatted as string |

Interval placeholders support suffixes:

| Suffix | Meaning |
| --- | --- |
| `_s`, `_sec`, `_seconds` | total seconds |
| `_m`, `_min`, `_minutes` | total minutes |
| `_h`, `_hours` | total hours |
| `_d`, `_days` | total days |
| `_str` | human-readable string |

Speed placeholders support suffixes:

| Suffix | Meaning |
| --- | --- |
| `_s`, `_sec` | steps per second |
| `_m`, `_min` | steps per minute |
| `_h` | steps per hour |
| `_d` | steps per day |
| `_str` | human-readable string |

Examples:

```python
tt.info("elapsed={et_s:.3f}s eta={rt_m:.1f}min", i=25, total=100)
tt.info("speed={v_h:.0f} rows/hour", i=25)
tt.info("end={end:%Y-%m-%d %H:%M}", i=25, total=100)
```

Custom placeholders are also accepted:

```python
tt.info("file={filename} elapsed={et}", filename="data.csv")
```

### Casting and Comparison

`TicToc` compares by its current `start_time()`.

```python
float(tt)  # Unix timestamp of start_time()
int(tt)
tt.datetime
tt.to_datetime()
```

Compare with another `TicToc`, a `TicTocTime`, a `datetime`, or a timestamp:

```python
other = TicToc()
print(tt <= other)
```

Use `str(tt)` for the humanized elapsed time.

### Copying

```python
copy_tt = tt.copy()
```

The copy keeps timer configuration and progress samples, and named timers are
copied as separate objects.

## TicTocInterval

`TicTocInterval` represents a duration stored internally as seconds.

### Create Intervals

```python
from datetime import timedelta
from tictoc import TicTocInterval

TicTocInterval(10)
TicTocInterval(2.5)
TicTocInterval(timedelta(minutes=3))
TicTocInterval("1 day 2 hours 3 minutes 4 seconds")
```

Constructor helpers:

```python
TicTocInterval.from_seconds(10)
TicTocInterval.from_minutes(2)
TicTocInterval.from_hours(1.5)
TicTocInterval.from_days(1)
TicTocInterval.from_timedelta(timedelta(seconds=30))
TicTocInterval.from_string("01:02:03")
```

### Accepted String Formats

Natural units:

```python
TicTocInterval("1 week")
TicTocInterval("1 day 2 hours")
TicTocInterval("1d 2h 3m 4s")
TicTocInterval("250ms")
TicTocInterval("500us")
```

Clock-like formats:

```python
TicTocInterval("10:30")       # 10 minutes, 30 seconds
TicTocInterval("01:02:03")    # 1 hour, 2 minutes, 3 seconds
TicTocInterval("1.02:00:53")  # 1 day, 2 hours, 53 seconds
```

ISO-like duration formats:

```python
TicTocInterval("PT1H30M")
TicTocInterval("P2DT3H")
```

### Totals and Components

Total values:

```python
interval = TicTocInterval("1d 2h 3m 4s")

interval.seconds
interval.total_seconds
interval.milliseconds
interval.total_milliseconds
interval.microseconds
interval.total_microseconds
interval.minutes
interval.total_minutes
interval.hours
interval.total_hours
interval.days
interval.total_days
```

Component values:

```python
interval.component_days
interval.component_hours
interval.component_minutes
interval.component_seconds
interval.component_microseconds
```

For `1d 2h 3m 4s`, components are `1`, `2`, `3`, `4`.

### Arithmetic

```python
from datetime import timedelta
from tictoc import TicTocInterval

a = TicTocInterval("1h")
b = TicTocInterval("30m")

a + b
a - b
a + 10
a - timedelta(seconds=5)
2 * a
a * 2
a / 2
a / b  # ratio as float
```

In-place arithmetic is supported:

```python
a += 10
a -= TicTocInterval("5m")
a *= 2
a /= 4
```

### Conversion and Formatting

```python
interval = TicTocInterval("90s")

float(interval)       # 90.0
int(interval)         # 90
interval.to_timedelta()
interval.timedelta
interval.humanize()
str(interval)
repr(interval)
```

Formatting:

```python
format(interval, ".2f")       # numeric seconds
format(interval, "td")        # timedelta string
format(interval, "human")     # same as str(interval)
```

### Comparison and Copying

```python
from datetime import timedelta

interval = TicTocInterval("10s")

interval > 5
interval == timedelta(seconds=10)
interval.copy()
```

Comparisons accept numbers, `timedelta`, and other `TicTocInterval` values.

## TicTocTime

`TicTocTime` represents a timestamp stored internally as a Unix timestamp.

### Create Times

```python
from datetime import datetime
from tictoc import TicTocTime

TicTocTime.now()
TicTocTime.from_timestamp(1_781_600_000)
TicTocTime.from_datetime(datetime(2026, 6, 16, 12, 0, 0))
TicTocTime.from_string("2026-06-16 12:00:00")
```

The constructor accepts the same input types:

```python
TicTocTime()
TicTocTime(1_781_600_000)
TicTocTime("2026-06-16")
TicTocTime(datetime.now())
```

Use `fmt` when parsing or displaying a custom format:

```python
TicTocTime.from_string("16/06/2026 12:00", fmt="%d/%m/%Y %H:%M")
instant = TicTocTime.now(fmt="%d/%m/%Y %H:%M:%S")
print(instant)
```

### Supported Date Strings

Standard parsing supports:

```text
YYYY-MM-DD
YYYY-MM-DD HH:MM
YYYY-MM-DD HH:MM:SS
YYYY-MM-DD HH:MM:SS.microseconds
YYYY/MM/DD
DD/MM/YYYY
MM/DD/YYYY
ISO 8601 strings accepted by datetime.fromisoformat()
```

If a string is not recognized and `python-dateutil` is installed, `dateutil` is
used lazily as a fallback.

### Properties

```python
instant = TicTocTime.now()

instant.timestamp
instant.seconds
instant.datetime
instant.date
instant.time
instant.year
instant.month
instant.day
instant.hour
instant.minute
instant.second
instant.microsecond
instant.weekday
```

### Arithmetic

Add intervals to get a new `TicTocTime`:

```python
from datetime import timedelta
from tictoc import TicTocInterval, TicTocTime

start = TicTocTime.from_string("2026-06-16 12:00:00")

start + 60
start + timedelta(minutes=5)
start + TicTocInterval("10m")
```

Subtract intervals to get a new `TicTocTime`:

```python
start - 60
start - timedelta(minutes=5)
start - TicTocInterval("10m")
```

Subtract two times to get a `TicTocInterval`:

```python
end = start + TicTocInterval("1h")
duration = end - start
```

Subtract a `datetime` from a `TicTocTime`, or the other way around, to get a
`TicTocInterval`.

### Conversion and Formatting

```python
instant = TicTocTime.now()

float(instant)         # Unix timestamp
int(instant)
instant.to_datetime()
instant.to_string()
instant.to_string("%Y-%m-%d")
instant.isoformat()
instant.humanize()
str(instant)
repr(instant)
```

Formatting:

```python
format(instant, "iso")
format(instant, "%Y-%m-%d %H:%M")
format(instant, ".3f")  # numeric timestamp
```

Python does not have a built-in `datetime()` casting protocol. Use
`.datetime` or `.to_datetime()` when you need a `datetime.datetime`.

### Comparison and Copying

```python
from datetime import datetime

instant = TicTocTime.now()

instant > 1_700_000_000
instant == datetime.fromtimestamp(float(instant))
instant.copy()
```

Comparisons accept numbers, `datetime`, and other `TicTocTime` values.

## TicTocSpeed

`TicTocSpeed` represents processing speed stored internally as steps per second.

### Create Speeds

```python
from tictoc import TicTocInterval, TicTocSpeed

TicTocSpeed(10)  # 10 steps per second
TicTocSpeed.per_second(10)
TicTocSpeed.per_minute(600)
TicTocSpeed.per_hour(36_000)
TicTocSpeed.per_day(864_000)
TicTocSpeed.from_steps(120, TicTocInterval.from_minutes(2))
```

The constructor can also compute speed from `steps` and `interval`:

```python
TicTocSpeed(steps=500, interval=TicTocInterval("10m"))
```

### Properties and Unit Conversion

```python
speed = TicTocSpeed.from_steps(120, TicTocInterval.from_minutes(2))

speed.steps_per_second
speed.per_sec
speed.at_seconds
speed.steps_per_minute
speed.per_min
speed.at_minutes
speed.steps_per_hour
speed.per_hour_value
speed.at_hours
speed.steps_per_day
speed.at_days
speed.steps
speed.interval
speed.in_unit("minute")
```

### Conversion and Formatting

```python
float(speed)
int(speed)
speed.humanize()
speed.humanize(label="row")
str(speed)
repr(speed)
```

Formatting:

```python
format(speed, "s")      # steps per second
format(speed, "m")      # steps per minute
format(speed, "h")      # steps per hour
format(speed, "d")      # steps per day
format(speed, ".2f")    # numeric steps per second
```

### Comparison and Copying

```python
speed > 1
speed == TicTocSpeed.per_minute(60)
speed.copy()
```

Comparisons accept numbers and other `TicTocSpeed` values.

## Human-Readable Output

All public classes provide human-readable string output:

```python
str(TicTocInterval(0.152368))     # 0.152 s
str(TicTocInterval(53.152368))    # 53.2 s
str(TicTocInterval(653.152368))   # 00:10:53
str(TicTocInterval(93_653))       # 1.02:00:53

str(TicTocTime.now())             # 2026-06-16 12:00:00
str(TicTocSpeed.per_hour(3600))   # 1 step/s
```

Use numeric properties when exact machine-readable values are needed.

## Common Recipes

### Time a Function

```python
from tictoc import TicToc

def load_data() -> list[int]:
    tt = TicToc()
    data = [1, 2, 3]
    print("loaded in", tt.toc())
    return data
```

### Log a Long Loop

```python
import logging
from tictoc import TicToc

logging.basicConfig(level=logging.INFO, format="%(message)s")

items = range(1, 10_001)
tt = TicToc(total=len(items))

for i, item in enumerate(items, start=1):
    # Process item
    tt.info("{i}/{tot} {percent_str} eta={rt} speed={v}", i=i, each=500)
```

### Track Multiple Phases

```python
from tictoc import TicToc

tt = TicToc()

tt.tic("download")
# Download

tt.tic("parse")
# Parse

tt.tic("save")
# Save

print("download:", tt.toc("download"))
print("parse:", tt.toc("parse"))
print("save:", tt.toc("save"))
print("overall:", tt.elapsed_origin_time())
```

### Estimate with a Moving Window

```python
from tictoc import TicToc

tt = TicToc(total=1_000)

for i in range(1, 1_001):
    # Work
    if i % 50 == 0:
        print(tt.remaining_time(i=i, method="moving", n=10))
```

### Build a Custom Progress Message

```python
message = tt.format_log(
    "job={job} {i}/{tot} elapsed={et} eta={rt} rows/hour={v_h:.0f}",
    job="daily-import",
    i=250,
    total=1000,
)
print(message)
```

## Notes and Edge Cases

If `remaining_time()` or `speed()` does not have enough progress information,
it returns zero values instead of raising.

For ETA methods, pass `i` as completed units. If your loop index is zero-based,
use `i + 1`.

```python
for index, item in enumerate(items):
    completed = index + 1
    tt.info("{completed}/{tot} eta={rt}", i=completed, completed=completed)
```

`total` and `tot` are aliases. Prefer `total` in new code.

String formatting placeholders that are unknown are kept as `{placeholder}`
rather than raising immediately. This makes progressive log template changes
easier while developing.
