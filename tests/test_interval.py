from __future__ import annotations

import copy
from datetime import timedelta

from tictoc import TicTocInterval


class TestTicTocInterval:
    def test_constructors_and_parsing(self) -> None:
        assert TicTocInterval(2).seconds == 2
        assert TicTocInterval(timedelta(minutes=2)).seconds == 120
        assert TicTocInterval.from_string("1 day 2 seconds").seconds == 86_402
        assert TicTocInterval.from_string("1d 2h 3m 4s").seconds == 93_784
        assert TicTocInterval.from_string("01:02:03").seconds == 3_723
        assert TicTocInterval.from_string("1.02:00:53").seconds == 93_653
        assert TicTocInterval.from_string("PT1H30M").seconds == 5_400

    def test_arithmetic_and_comparison(self) -> None:
        interval = TicTocInterval(10)
        assert (interval + 5).seconds == 15
        assert (5 + interval).seconds == 15
        assert (interval - timedelta(seconds=4)).seconds == 6
        assert (20 - interval).seconds == 10
        assert (interval * 3).seconds == 30
        assert (interval / 2).seconds == 5  # type: ignore
        assert interval / TicTocInterval(5) == 2
        assert interval > 5
        assert interval >= timedelta(seconds=10)
        assert copy.copy(interval) == interval

    def test_totals_components_and_humanize(self) -> None:
        interval = TicTocInterval("1d 2h 3m 4.000005s")
        assert round(interval.total_days, 5) == 1.08546
        assert interval.component_days == 1
        assert interval.component_hours == 2
        assert interval.component_minutes == 3
        assert interval.component_seconds == 4
        assert interval.component_microseconds == 5
        assert str(TicTocInterval(0.152368)) == "0.152 s"
        assert str(TicTocInterval(53.152368)) == "53.2 s"
        assert str(TicTocInterval(653.152368)) == "00:10:53"
        assert str(TicTocInterval(93_653.152368)) == "1.02:00:53"
