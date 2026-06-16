from __future__ import annotations

import io
import logging
import unittest

from tictoc import TicToc, TicTocInterval, TicTocSpeed, TicTocTime


class FakeClock:
    def __init__(self, value: float = 0.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


class TicTocTest(unittest.TestCase):
    def test_elapsed_tic_toc_and_origin(self) -> None:
        clock = FakeClock(100)
        timer = TicToc(clock=clock)
        clock.advance(5)
        self.assertEqual(timer.toc(), TicTocInterval(5))
        self.assertIs(timer.tic(), timer)
        self.assertEqual(timer.elapsed_time().seconds, 0)
        clock.advance(2)
        self.assertEqual(timer.elapsed_time().seconds, 2)
        self.assertEqual(timer.elapsed_origin_time().seconds, 7)
        self.assertIsInstance(timer.start_time(), TicTocTime)
        self.assertEqual(float(timer), 105)

    def test_named_timers(self) -> None:
        clock = FakeClock(0)
        timer = TicToc(clock=clock)
        timer.tic("load")
        clock.advance(3)
        timer.tic("save")
        clock.advance(2)
        self.assertEqual(timer.elapsed_time("load").seconds, 5)
        self.assertEqual(timer["save"].toc().seconds, 2)
        self.assertEqual(timer.names, ("load", "save"))

    def test_progress_estimates_from_origin(self) -> None:
        clock = FakeClock(0)
        timer = TicToc(total=10, clock=clock)
        clock.advance(10)
        speed = timer.speed(i=5)
        self.assertIsInstance(speed, TicTocSpeed)
        self.assertEqual(speed.steps_per_second, 0.5)
        self.assertEqual(timer.remaining_time(i=5).seconds, 10)
        self.assertEqual(timer.total_time(i=5).seconds, 20)
        self.assertEqual(float(timer.end_time(i=5)), 20)

    def test_last_and_moving_estimates_use_progress_history(self) -> None:
        clock = FakeClock(0)
        timer = TicToc(clock=clock)
        timer.update(0, total=10)
        clock.advance(10)
        timer.update(5)
        clock.advance(2)
        self.assertEqual(timer.speed(i=9, method="last").steps_per_second, 2)
        self.assertEqual(timer.remaining_time(i=9, total=10, method="last").seconds, 0.5)
        self.assertAlmostEqual(timer.speed(method="moving", n=3).steps_per_second, 0.75)

    def test_logging_formats_placeholders_and_chains(self) -> None:
        stream = io.StringIO()
        logger = logging.getLogger("tictoc-test")
        logger.handlers.clear()
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
        logger.addHandler(handler)

        clock = FakeClock(0)
        timer = TicToc(total=10, logger=logger, clock=clock)
        clock.advance(10)
        returned = timer.info("{i}/{tot} {et_s:.0f}s {rt_s:.0f}s {v_s:.1f}/s", i=5)

        self.assertIs(returned, timer)
        self.assertIn("INFO:5/10 10s 10s 0.5/s", stream.getvalue())

    def test_logging_each_filter(self) -> None:
        stream = io.StringIO()
        logger = logging.getLogger("tictoc-each-test")
        logger.handlers.clear()
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler(stream))

        timer = TicToc(logger=logger, clock=FakeClock(0))
        timer.info("hidden", i=3, each=2)
        timer.info("visible {i}", i=4, each=2)
        self.assertEqual(stream.getvalue().strip(), "visible 4")


if __name__ == "__main__":
    unittest.main()
