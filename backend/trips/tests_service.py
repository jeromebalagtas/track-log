"""Tests for shared trip planning service."""
from django.test import SimpleTestCase

from trips.service import build_trip_plan, validate_trip_payload


class TripServiceTests(SimpleTestCase):
    def test_validate_rejects_missing_location(self):
        with self.assertRaises(ValueError):
            validate_trip_payload({"pickup_location": "A", "dropoff_location": "B"})

    def test_validate_rejects_bad_cycle(self):
        with self.assertRaises(ValueError):
            validate_trip_payload(
                {
                    "current_location": "A",
                    "pickup_location": "B",
                    "dropoff_location": "C",
                    "cycle_used_hours": 99,
                }
            )

    def test_build_trip_plan_short_route(self):
        plan = build_trip_plan(
            {
                "current_location": "Chicago, IL",
                "pickup_location": "Indianapolis, IN",
                "dropoff_location": "Columbus, OH",
                "cycle_used_hours": 2.5,
            }
        )
        self.assertGreater(plan["total_miles"], 0)
        self.assertGreaterEqual(len(plan["daily_logs"]), 1)
