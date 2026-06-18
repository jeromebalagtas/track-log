"""Geocoding and routing via free OpenStreetMap services."""
from __future__ import annotations

import math
from typing import List, Tuple

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
HEADERS = {"User-Agent": "TrackLog-HOS-App/1.0 (FMCSA assessment project)"}

NA_VALUES = {"n/a", "na", "none", "-"}


def is_na(address: str) -> bool:
    return address.strip().lower() in NA_VALUES


def geocode(address: str) -> dict:
    if is_na(address):
        raise ValueError("Cannot geocode N/A — use resolve_location instead")

    if len(address.strip()) < 2:
        raise ValueError(f"Location is too short: {address}")

    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": 1, "countrycodes": "us"},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise ValueError(f"Geocoding service unavailable for: {address} ({exc})") from exc

    if not data:
        raise ValueError(f"Could not find location: {address}. Check spelling or use City, ST format.")

    return {
        "name": data[0].get("display_name", address).split(",")[0],
        "full_name": data[0].get("display_name", address),
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "is_na": False,
    }


def na_location(label: str = "N/A") -> dict:
    return {
        "name": label,
        "full_name": label,
        "lat": None,
        "lon": None,
        "is_na": True,
    }


def resolve_location(address: str, anchor: dict | None = None) -> dict:
    if is_na(address):
        loc = na_location("N/A")
        if anchor and anchor.get("lat") is not None:
            loc["lat"] = anchor["lat"]
            loc["lon"] = anchor["lon"]
        return loc
    return geocode(address)


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def get_route(from_loc: dict, to_loc: dict) -> dict:
    if from_loc.get("is_na") or to_loc.get("is_na"):
        raise ValueError("Cannot route to or from N/A")

    coords = f"{from_loc['lon']},{from_loc['lat']};{to_loc['lon']},{to_loc['lat']}"
    url = f"{OSRM_URL}/{coords}"
    resp = requests.get(url, params={"overview": "full", "geometries": "geojson"}, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            miles = route["distance"] / 1609.34
            geometry = route["geometry"]["coordinates"]
            line = [[c[1], c[0]] for c in geometry]
            return {"miles": miles, "coordinates": line, "duration_hours": route["duration"] / 3600}

    miles = haversine_miles(from_loc["lat"], from_loc["lon"], to_loc["lat"], to_loc["lon"]) * 1.25
    return {
        "miles": miles,
        "coordinates": [[from_loc["lat"], from_loc["lon"]], [to_loc["lat"], to_loc["lon"]]],
        "duration_hours": miles / 55,
    }


def build_trip_route(
    current: dict,
    pickup: dict,
    dropoff: dict,
) -> Tuple[List[dict], float, List[List[float]]]:
    """Build route legs skipping N/A stops."""
    legs: List[dict] = []
    all_coords: List[List[float]] = []

    if pickup.get("is_na") and dropoff.get("is_na"):
        raise ValueError("At least one of pickup or dropoff must be a real location (not N/A).")

    if pickup.get("is_na"):
        leg = get_route(current, dropoff)
        legs.append({"from": current["name"], "to": dropoff["name"], "dest": "dropoff", **leg})
        all_coords.extend(leg["coordinates"])
    elif dropoff.get("is_na"):
        leg = get_route(current, pickup)
        legs.append({"from": current["name"], "to": pickup["name"], "dest": "pickup", **leg})
        all_coords.extend(leg["coordinates"])
    else:
        leg1 = get_route(current, pickup)
        leg2 = get_route(pickup, dropoff)
        legs.append({"from": current["name"], "to": pickup["name"], "dest": "pickup", **leg1})
        legs.append({"from": pickup["name"], "to": dropoff["name"], "dest": "dropoff", **leg2})
        all_coords.extend(leg1["coordinates"])
        all_coords.extend(leg2["coordinates"])

    total_miles = sum(leg["miles"] for leg in legs)
    return legs, total_miles, all_coords


# Keep alias for tests
def build_full_route(current: dict, pickup: dict, dropoff: dict) -> Tuple[List[dict], float, List[List[float]]]:
    return build_trip_route(current, pickup, dropoff)
