"""Geocoding and routing via free OpenStreetMap services."""
from __future__ import annotations

import math
from typing import List, Tuple

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
HEADERS = {"User-Agent": "TrackLog-HOS-App/1.0 (FMCSA assessment project)"}


def geocode(address: str) -> dict:
    resp = requests.get(
        NOMINATIM_URL,
        params={"q": address, "format": "json", "limit": 1, "countrycodes": "us"},
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"Could not geocode address: {address}")
    return {
        "name": data[0].get("display_name", address).split(",")[0],
        "full_name": data[0].get("display_name", address),
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
    }


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def get_route(from_loc: dict, to_loc: dict) -> dict:
    coords = f"{from_loc['lon']},{from_loc['lat']};{to_loc['lon']},{to_loc['lat']}"
    url = f"{OSRM_URL}/{coords}"
    resp = requests.get(url, params={"overview": "full", "geometries": "geojson"}, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            miles = route["distance"] / 1609.34
            geometry = route["geometry"]["coordinates"]
            # GeoJSON is [lon, lat] — convert to [lat, lon] for Leaflet
            line = [[c[1], c[0]] for c in geometry]
            return {"miles": miles, "coordinates": line, "duration_hours": route["duration"] / 3600}

    # Fallback: straight-line estimate
    miles = haversine_miles(from_loc["lat"], from_loc["lon"], to_loc["lat"], to_loc["lon"]) * 1.25
    return {
        "miles": miles,
        "coordinates": [[from_loc["lat"], from_loc["lon"]], [to_loc["lat"], to_loc["lon"]]],
        "duration_hours": miles / 55,
    }


def build_full_route(current: dict, pickup: dict, dropoff: dict) -> Tuple[List[dict], float, List[List[float]]]:
    leg1 = get_route(current, pickup)
    leg2 = get_route(pickup, dropoff)
    legs = [
        {"from": current["name"], "to": pickup["name"], **leg1},
        {"from": pickup["name"], "to": dropoff["name"], **leg2},
    ]
    total_miles = leg1["miles"] + leg2["miles"]
    all_coords = leg1["coordinates"] + leg2["coordinates"]
    return legs, total_miles, all_coords
