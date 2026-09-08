from __future__ import annotations

import copy
from datetime import datetime, timedelta

from tictoc import TicTocInterval, TicTocSpeed, TicTocTime


class TestTicTocTime:
    def test_constructors_components_and_casts(self) -> None:
        dt = datetime(2024, 1, 2, 3, 4, 5)
        instant = TicTocTime.from_datetime(dt)
        assert instant.year == 2024
        assert instant.month == 1
        assert instant.day == 2
        assert instant.hour == 3
        assert instant.minute == 4
        assert instant.second == 5
        assert int(instant) == int(dt.timestamp())
        assert instant.to_string("%Y-%m-%d") == "2024-01-02"
        assert copy.deepcopy(instant) == instant

    def test_string_parsing_and_time_math(self) -> None:
        instant = TicTocTime.from_string("2024-01-02 03:04:05")
        later = instant + TicTocInterval(10)
        assert isinstance(later, TicTocTime)
        assert (later - instant).seconds == 10
        assert (later - datetime.fromtimestamp(float(instant))).seconds == 10
        assert ((later - timedelta(seconds=5)) - instant).seconds == 5
        assert later > instant


class TestTicTocSpeed:
    def test_speed_conversions_and_comparison(self) -> None:
        speed = TicTocSpeed.from_steps(120, TicTocInterval.from_minutes(2))
        assert speed.steps_per_second == 1
        assert speed.steps_per_minute == 60
        assert speed.steps_per_hour == 3_600
        assert float(speed) == 1
        assert str(speed) == "1 step/s"
        assert speed == TicTocSpeed.per_hour(3_600)
        assert speed > TicTocSpeed.per_minute(30)
        assert copy.copy(speed) == speed
