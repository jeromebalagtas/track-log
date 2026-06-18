"""Shared trip planning logic for Django views and Vercel serverless."""
from __future__ import annotations

import re

from .hos_engine import HOSEngine
from .routing import build_trip_route, is_na, resolve_location


def validate_trip_payload(data: dict) -> dict:
    fields = {
        "current_location": str(data.get("current_location", "")).strip(),
        "pickup_location": str(data.get("pickup_location", "")).strip(),
        "dropoff_location": str(data.get("dropoff_location", "")).strip(),
    }

    for label, key in [("Current location", "current_location"), ("Pickup location", "pickup_location"), ("Dropoff location", "dropoff_location")]:
        value = fields[key]
        if not value:
            raise ValueError(f"{label} is required (use N/A only for optional pickup or dropoff).")

    if is_na(fields["current_location"]):
        raise ValueError("Current location cannot be N/A — enter your starting city.")

    if is_na(fields["pickup_location"]) and is_na(fields["dropoff_location"]):
        raise ValueError("At least one of pickup or dropoff must be a real location (not both N/A).")

    raw_cycle = data.get("cycle_used_hours", 0)
    if isinstance(raw_cycle, str):
        raw_cycle = raw_cycle.strip()
        if not re.match(r"^\d+(\.\d+)?$", raw_cycle):
            raise ValueError("Current cycle used must be a number between 0 and 70.")
        cycle_used = float(raw_cycle)
    else:
        try:
            cycle_used = float(raw_cycle)
        except (TypeError, ValueError) as exc:
            raise ValueError("Current cycle used must be a number between 0 and 70.") from exc

    if cycle_used < 0 or cycle_used > 70:
        raise ValueError("Current cycle used must be between 0 and 70 hours.")

    return {
        **fields,
        "cycle_used_hours": cycle_used,
    }


def build_trip_plan(data: dict) -> dict:
    payload = validate_trip_payload(data)

    current = resolve_location(payload["current_location"])
    if current.get("is_na"):
        raise ValueError("Current location could not be resolved.")

    dropoff = resolve_location(payload["dropoff_location"])
    pickup = resolve_location(
        payload["pickup_location"],
        anchor=current if dropoff.get("is_na") else dropoff,
    )

    legs, total_miles, route_coords = build_trip_route(current, pickup, dropoff)

    engine = HOSEngine(cycle_used=payload["cycle_used_hours"])
    plan = engine.plan_trip(
        current,
        pickup,
        dropoff,
        legs,
        total_miles,
        route_coordinates=route_coords,
    )

    result = plan.to_dict()
    result["locations"] = {"current": current, "pickup": pickup, "dropoff": dropoff}
    result["legs"] = [
        {"from": leg["from"], "to": leg["to"], "miles": round(leg["miles"], 1)}
        for leg in legs
    ]
    result["route_coordinates"] = route_coords
    return result
