from __future__ import annotations

import copy
import unittest
from datetime import datetime, timedelta

from tictoc import TicTocInterval, TicTocSpeed, TicTocTime


class TicTocTimeTest(unittest.TestCase):
    def test_constructors_components_and_casts(self) -> None:
        dt = datetime(2024, 1, 2, 3, 4, 5)
        instant = TicTocTime.from_datetime(dt)
        self.assertEqual(instant.year, 2024)
        self.assertEqual(instant.month, 1)
        self.assertEqual(instant.day, 2)
        self.assertEqual(instant.hour, 3)
        self.assertEqual(instant.minute, 4)
        self.assertEqual(instant.second, 5)
        self.assertEqual(int(instant), int(dt.timestamp()))
        self.assertEqual(instant.to_string("%Y-%m-%d"), "2024-01-02")
        self.assertEqual(copy.deepcopy(instant), instant)

    def test_string_parsing_and_time_math(self) -> None:
        instant = TicTocTime.from_string("2024-01-02 03:04:05")
        later = instant + TicTocInterval(10)
        self.assertIsInstance(later, TicTocTime)
        self.assertEqual((later - instant).seconds, 10)
        self.assertEqual((later - datetime.fromtimestamp(float(instant))).seconds, 10)
        self.assertEqual(((later - timedelta(seconds=5)) - instant).seconds, 5)
        self.assertTrue(later > instant)


class TicTocSpeedTest(unittest.TestCase):
    def test_speed_conversions_and_comparison(self) -> None:
        speed = TicTocSpeed.from_steps(120, TicTocInterval.from_minutes(2))
        self.assertEqual(speed.steps_per_second, 1)
        self.assertEqual(speed.steps_per_minute, 60)
        self.assertEqual(speed.steps_per_hour, 3_600)
        self.assertEqual(float(speed), 1)
        self.assertEqual(str(speed), "1 step/s")
        self.assertTrue(speed == TicTocSpeed.per_hour(3_600))
        self.assertTrue(speed > TicTocSpeed.per_minute(30))
        self.assertEqual(copy.copy(speed), speed)


if __name__ == "__main__":
    unittest.main()
