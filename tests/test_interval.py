from __future__ import annotations

import copy
import unittest
from datetime import timedelta

from tictoc import TicTocInterval


class TicTocIntervalTest(unittest.TestCase):
    def test_constructors_and_parsing(self) -> None:
        self.assertEqual(TicTocInterval(2).seconds, 2)
        self.assertEqual(TicTocInterval(timedelta(minutes=2)).seconds, 120)
        self.assertEqual(TicTocInterval.from_string("1 day 2 seconds").seconds, 86_402)
        self.assertEqual(TicTocInterval.from_string("1d 2h 3m 4s").seconds, 93_784)
        self.assertEqual(TicTocInterval.from_string("01:02:03").seconds, 3_723)
        self.assertEqual(TicTocInterval.from_string("1.02:00:53").seconds, 93_653)
        self.assertEqual(TicTocInterval.from_string("PT1H30M").seconds, 5_400)

    def test_arithmetic_and_comparison(self) -> None:
        interval = TicTocInterval(10)
        self.assertEqual((interval + 5).seconds, 15)
        self.assertEqual((5 + interval).seconds, 15)
        self.assertEqual((interval - timedelta(seconds=4)).seconds, 6)
        self.assertEqual((20 - interval).seconds, 10)
        self.assertEqual((interval * 3).seconds, 30)
        self.assertEqual((interval / 2).seconds, 5)
        self.assertEqual(interval / TicTocInterval(5), 2)
        self.assertTrue(interval > 5)
        self.assertTrue(interval >= timedelta(seconds=10))
        self.assertEqual(copy.copy(interval), interval)

    def test_totals_components_and_humanize(self) -> None:
        interval = TicTocInterval("1d 2h 3m 4.000005s")
        self.assertAlmostEqual(interval.total_days, 1.08546, places=5)
        self.assertEqual(interval.component_days, 1)
        self.assertEqual(interval.component_hours, 2)
        self.assertEqual(interval.component_minutes, 3)
        self.assertEqual(interval.component_seconds, 4)
        self.assertEqual(interval.component_microseconds, 5)
        self.assertEqual(str(TicTocInterval(0.152368)), "0.152 s")
        self.assertEqual(str(TicTocInterval(53.152368)), "53.2 s")
        self.assertEqual(str(TicTocInterval(653.152368)), "00:10:53")
        self.assertEqual(str(TicTocInterval(93_653.152368)), "1.02:00:53")


if __name__ == "__main__":
    unittest.main()
