"""
FMCSA Hours of Service trip planner for property-carrying drivers (70hr/8-day).
Based on Interstate Truck Driver's Guide to Hours of Service (FMCSA, April 2022).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional


class DutyStatus(str, Enum):
    OFF_DUTY = "off_duty"
    SLEEPER = "sleeper_berth"
    DRIVING = "driving"
    ON_DUTY = "on_duty"


# Property-carrying limits (49 CFR 395.3)
MAX_DRIVE_HOURS = 11.0
MAX_WINDOW_HOURS = 14.0
BREAK_AFTER_DRIVE_HOURS = 8.0
BREAK_DURATION_HOURS = 0.5
MIN_REST_HOURS = 10.0
MAX_CYCLE_HOURS = 70.0
CYCLE_DAYS = 8
FUEL_INTERVAL_MILES = 1000
PICKUP_DROP_HOURS = 1.0
AVG_SPEED_MPH = 55.0
FUEL_STOP_HOURS = 0.5


@dataclass
class DutySegment:
    status: DutyStatus
    start: datetime
    end: datetime
    location: str = ""
    remark: str = ""

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_hours": round(self.duration_hours, 2),
            "location": self.location,
            "remark": self.remark,
        }


@dataclass
class DailyLog:
    date: datetime
    from_location: str
    to_location: str
    segments: List[DutySegment] = field(default_factory=list)
    total_miles: float = 0.0
    driving_miles: float = 0.0
    cycle_used_before: float = 0.0

    def totals(self) -> dict:
        totals = {s.value: 0.0 for s in DutyStatus}
        for seg in self.segments:
            totals[seg.status.value] += seg.duration_hours
        return {k: round(v, 2) for k, v in totals.items()}

    def on_duty_today(self) -> float:
        t = self.totals()
        return round(t["driving"] + t["on_duty"], 2)

    def recap_70_8(self, prior_on_duty_days: List[float]) -> dict:
        """70-hour / 8-day recap per paper log form."""
        today = self.on_duty_today()
        last_7 = prior_on_duty_days[-7:] + [today]
        last_8 = prior_on_duty_days[-7:] + [today]
        a_7 = round(sum(last_7), 1)
        c_8 = round(sum(last_8), 1)
        return {
            "daily_on_duty": today,
            "a_last_7_days": a_7,
            "b_available_tomorrow_70": round(max(0, MAX_CYCLE_HOURS - a_7), 1),
            "c_last_8_days": c_8,
        }

    def to_dict(self) -> dict:
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "from_location": self.from_location,
            "to_location": self.to_location,
            "segments": [s.to_dict() for s in self.segments],
            "totals": self.totals(),
            "total_miles": round(self.total_miles, 1),
            "driving_miles": round(self.driving_miles, 1),
            "recap": self.recap_70_8([]),
            "remarks": [s.remark for s in self.segments if s.remark],
        }


@dataclass
class TripStop:
    name: str
    lat: float
    lon: float
    stop_type: str
    arrival: Optional[datetime] = None
    departure: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "type": self.stop_type,
            "arrival": self.arrival.isoformat() if self.arrival else None,
            "departure": self.departure.isoformat() if self.departure else None,
        }


@dataclass
class TripPlan:
    stops: List[TripStop]
    daily_logs: List[DailyLog]
    route_coordinates: List[List[float]]
    total_miles: float
    total_days: int
    instructions: List[str]
    cycle_hours_used: float

    def to_dict(self) -> dict:
        prior = []
        logs = []
        for log in self.daily_logs:
            d = log.to_dict()
            d["recap"] = log.recap_70_8(prior)
            prior.append(log.on_duty_today())
            logs.append(d)
        return {
            "stops": [s.to_dict() for s in self.stops],
            "daily_logs": logs,
            "route_coordinates": self.route_coordinates,
            "total_miles": round(self.total_miles, 1),
            "total_days": self.total_days,
            "instructions": self.instructions,
            "cycle_hours_used": round(self.cycle_hours_used, 1),
            "cycle_hours_remaining": round(max(0, MAX_CYCLE_HOURS - self.cycle_hours_used), 1),
        }


class HOSEngine:
    def __init__(self, cycle_used: float = 0.0, start_time: Optional[datetime] = None):
        self.cycle_used = cycle_used
        self.current_time = start_time or datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        self.drive_since_rest = 0.0
        self.drive_since_break = 0.0
        self.window_start: Optional[datetime] = None
        self.on_duty_today = 0.0
        self.driving_today = 0.0
        self.miles_today = 0.0
        self.segments: List[DutySegment] = []
        self.daily_logs: List[DailyLog] = []
        self.prior_on_duty: List[float] = []
        self.instructions: List[str] = []
        self.stops: List[TripStop] = []
        self._log_date = self.current_time.date()
        self._log_from = ""
        self._log_to = ""

    def _add_segment(self, status: DutyStatus, hours: float, location: str, remark: str = ""):
        end = self.current_time + timedelta(hours=hours)
        self.segments.append(DutySegment(status, self.current_time, end, location, remark))
        if status == DutyStatus.DRIVING:
            self.drive_since_rest += hours
            self.drive_since_break += hours
            self.driving_today += hours
            self.miles_today += hours * AVG_SPEED_MPH
        if status in (DutyStatus.DRIVING, DutyStatus.ON_DUTY):
            self.on_duty_today += hours
            if self.window_start is None:
                self.window_start = self.current_time
        self.current_time = end

    def _finalize_day(self, to_location: str):
        totals = {s.value: 0.0 for s in DutyStatus}
        for seg in self.segments:
            totals[seg.status.value] += seg.duration_hours
        # Pad remaining hours to 24 with off-duty
        used = sum(totals.values())
        if used < 24:
            self._add_segment(DutyStatus.OFF_DUTY, 24 - used, to_location, "Off duty remainder of day")

        log = DailyLog(
            date=datetime.combine(self._log_date, datetime.min.time()),
            from_location=self._log_from or to_location,
            to_location=to_location,
            segments=list(self.segments),
            total_miles=self.miles_today,
            driving_miles=self.miles_today,
            cycle_used_before=self.cycle_used,
        )
        self.daily_logs.append(log)
        self.prior_on_duty.append(log.on_duty_today())
        self.cycle_used += log.on_duty_today()
        self.segments = []
        self.on_duty_today = 0.0
        self.driving_today = 0.0
        self.miles_today = 0.0
        self._log_date = self.current_time.date()
        self._log_from = to_location

    def _take_rest(self, location: str, hours: float = MIN_REST_HOURS):
        self.instructions.append(f"Take {hours}h rest at {location}")
        self._add_segment(DutyStatus.SLEEPER, hours, location, f"{hours}-hour sleeper berth rest")
        self.drive_since_rest = 0.0
        self.drive_since_break = 0.0
        self.window_start = None

    def _maybe_break(self, location: str):
        if self.drive_since_break >= BREAK_AFTER_DRIVE_HOURS:
            self.instructions.append(f"30-minute rest break required at {location}")
            self._add_segment(
                DutyStatus.OFF_DUTY,
                BREAK_DURATION_HOURS,
                location,
                "30-minute rest break (required after 8h driving)",
            )
            self.drive_since_break = 0.0

    def _drive_hours_available(self) -> float:
        drive_left = MAX_DRIVE_HOURS - self.drive_since_rest
        window_left = MAX_WINDOW_HOURS
        if self.window_start:
            elapsed = (self.current_time - self.window_start).total_seconds() / 3600
            window_left = max(0, MAX_WINDOW_HOURS - elapsed)
        return max(0, min(drive_left, window_left))

    def _drive_chunk(self, hours: float, location: str, remark: str = "Driving"):
        remaining = hours
        while remaining > 0.01:
            self._maybe_break(location)
            avail = self._drive_hours_available()
            if avail < 0.01:
                self._finalize_day(location)
                self._take_rest(location)
                avail = self._drive_hours_available()
            chunk = min(remaining, avail)
            self._add_segment(DutyStatus.DRIVING, chunk, location, remark)
            self.instructions.append(f"Drive {chunk:.1f}h toward {location}")
            remaining -= chunk
            if self._drive_hours_available() < 0.01 and remaining > 0.01:
                self._finalize_day(location)
                self._take_rest(location)

    def plan_trip(
        self,
        current: dict,
        pickup: dict,
        dropoff: dict,
        route_legs: List[dict],
        total_miles: float,
    ) -> TripPlan:
        """
        route_legs: [{from, to, miles, coordinates}, ...]
        Locations: {name, lat, lon}
        """
        self._log_from = current["name"]
        self.stops.append(TripStop(current["name"], current["lat"], current["lon"], "start",
                                   arrival=self.current_time))

        all_coords = []
        miles_since_fuel = 0.0
        leg_idx = 0

        # Leg 1: current -> pickup
        leg = route_legs[leg_idx]
        all_coords.extend(leg.get("coordinates", []))
        drive_h = leg["miles"] / AVG_SPEED_MPH
        self.instructions.append(f"Depart {current['name']} for pickup at {pickup['name']}")
        self._drive_chunk(drive_h, pickup["name"], f"Driving to pickup — {pickup['name']}")
        miles_since_fuel += leg["miles"]

        self.instructions.append(f"Arrive pickup: {pickup['name']} — 1h on-duty (loading)")
        self._add_segment(DutyStatus.ON_DUTY, PICKUP_DROP_HOURS, pickup["name"],
                          f"On duty at pickup — {pickup['name']}")
        self.stops.append(TripStop(pickup["name"], pickup["lat"], pickup["lon"], "pickup",
                                   arrival=self.current_time - timedelta(hours=PICKUP_DROP_HOURS),
                                   departure=self.current_time))

        # Leg 2: pickup -> dropoff
        leg_idx = 1
        leg = route_legs[leg_idx]
        remaining_miles = leg["miles"]
        dest = dropoff["name"]
        coord_offset = 0

        while remaining_miles > 0.5:
            if miles_since_fuel >= FUEL_INTERVAL_MILES:
                fuel_loc = f"Fuel stop near mile {int(total_miles - remaining_miles)}"
                self.instructions.append(fuel_loc)
                self._add_segment(DutyStatus.ON_DUTY, FUEL_STOP_HOURS, fuel_loc, "Fueling (on duty, not driving)")
                miles_since_fuel = 0.0

            chunk_miles = min(remaining_miles, self._drive_hours_available() * AVG_SPEED_MPH)
            if chunk_miles < 1:
                chunk_miles = min(remaining_miles, MAX_DRIVE_HOURS * AVG_SPEED_MPH)

            drive_h = chunk_miles / AVG_SPEED_MPH
            mid_name = dest if remaining_miles <= chunk_miles + 0.5 else f"En route to {dest}"
            self._drive_chunk(drive_h, mid_name, f"Driving — {mid_name}")
            miles_since_fuel += chunk_miles
            remaining_miles -= chunk_miles

            if remaining_miles > 0.5 and self._drive_hours_available() < 0.1:
                rest_loc = mid_name
                self._finalize_day(rest_loc)
                self._take_rest(rest_loc)

        all_coords.extend(leg.get("coordinates", []))

        self.instructions.append(f"Arrive dropoff: {dropoff['name']} — 1h on-duty (unloading)")
        self._add_segment(DutyStatus.ON_DUTY, PICKUP_DROP_HOURS, dropoff["name"],
                          f"On duty at dropoff — {dropoff['name']}")
        self.stops.append(TripStop(dropoff["name"], dropoff["lat"], dropoff["lon"], "dropoff",
                                   arrival=self.current_time - timedelta(hours=PICKUP_DROP_HOURS),
                                   departure=self.current_time))

        self._finalize_day(dropoff["name"])

        return TripPlan(
            stops=self.stops,
            daily_logs=self.daily_logs,
            route_coordinates=all_coords,
            total_miles=total_miles,
            total_days=len(self.daily_logs),
            instructions=self.instructions,
            cycle_hours_used=self.cycle_used,
        )
