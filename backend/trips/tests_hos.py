"""Tests for FMCSA HOS trip planner."""
from datetime import datetime

from django.test import SimpleTestCase

from trips.hos_engine import (
    BREAK_AFTER_DRIVE_HOURS,
    HOSEngine,
    MAX_DRIVE_HOURS,
    DutyStatus,
)


class HOSEngineTests(SimpleTestCase):
    def _fake_legs(self, miles1=200, miles2=200):
        return [
            {"from": "A", "to": "B", "miles": miles1, "coordinates": []},
            {"from": "B", "to": "C", "miles": miles2, "coordinates": []},
        ]

    def test_short_trip_single_day(self):
        engine = HOSEngine(cycle_used=0, start_time=datetime(2026, 6, 18, 6, 0))
        plan = engine.plan_trip(
            {"name": "Chicago", "lat": 41.88, "lon": -87.63},
            {"name": "Indianapolis", "lat": 39.77, "lon": -86.16},
            {"name": "Columbus", "lat": 39.96, "lon": -82.99},
            self._fake_legs(185, 175),
            360,
        )
        self.assertEqual(len(plan.daily_logs), 1)
        totals = plan.daily_logs[0].totals()
        self.assertAlmostEqual(sum(totals.values()), 24.0, places=1)

    def test_driving_never_exceeds_11h_per_shift(self):
        engine = HOSEngine(cycle_used=0, start_time=datetime(2026, 6, 18, 6, 0))
        plan = engine.plan_trip(
            {"name": "LA", "lat": 34.05, "lon": -118.24},
            {"name": "Vegas", "lat": 36.17, "lon": -115.14},
            {"name": "Denver", "lat": 39.74, "lon": -104.99},
            self._fake_legs(270, 750),
            1020,
        )
        for log in plan.daily_logs:
            driving = log.totals()["driving"]
            self.assertLessEqual(driving, MAX_DRIVE_HOURS + 0.1)

    def test_recap_includes_on_duty_and_driving(self):
        engine = HOSEngine(cycle_used=10, start_time=datetime(2026, 6, 18, 6, 0))
        plan = engine.plan_trip(
            {"name": "A", "lat": 0, "lon": 0},
            {"name": "B", "lat": 1, "lon": 1},
            {"name": "C", "lat": 2, "lon": 2},
            self._fake_legs(100, 100),
            200,
        )
        log = plan.daily_logs[0]
        self.assertGreater(log.on_duty_today(), 0)
        recap = log.recap_70_8([5, 8, 7])
        self.assertEqual(recap["b_available_tomorrow_70"], round(70 - recap["a_last_7_days"], 1))
