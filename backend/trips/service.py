"""Shared trip planning logic for Django views and Vercel serverless."""
from __future__ import annotations

from .hos_engine import HOSEngine
from .routing import build_full_route, geocode


def validate_trip_payload(data: dict) -> dict:
    required = ("current_location", "pickup_location", "dropoff_location")
    for field in required:
        value = data.get(field)
        if not value or not str(value).strip():
            raise ValueError(f"{field} is required")

    try:
        cycle_used = float(data.get("cycle_used_hours", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("cycle_used_hours must be a number") from exc

    if cycle_used < 0 or cycle_used > 70:
        raise ValueError("cycle_used_hours must be between 0 and 70")

    return {
        "current_location": str(data["current_location"]).strip(),
        "pickup_location": str(data["pickup_location"]).strip(),
        "dropoff_location": str(data["dropoff_location"]).strip(),
        "cycle_used_hours": cycle_used,
    }


def build_trip_plan(data: dict) -> dict:
    payload = validate_trip_payload(data)

    current = geocode(payload["current_location"])
    pickup = geocode(payload["pickup_location"])
    dropoff = geocode(payload["dropoff_location"])
    legs, total_miles, _ = build_full_route(current, pickup, dropoff)

    engine = HOSEngine(cycle_used=payload["cycle_used_hours"])
    plan = engine.plan_trip(current, pickup, dropoff, legs, total_miles)

    result = plan.to_dict()
    result["locations"] = {
        "current": current,
        "pickup": pickup,
        "dropoff": dropoff,
    }
    result["legs"] = [
        {"from": leg["from"], "to": leg["to"], "miles": round(leg["miles"], 1)}
        for leg in legs
    ]
    return result
