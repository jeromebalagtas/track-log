# AI Development Prompts

Use these prompts in Cursor or other AI tools when building or extending Track Log.

---

## Prompt 1 — Project bootstrap

```
Build a Django + React full-stack app called Track Log in f:\track-log.

Requirements from the Full Stack Developer Assessment:
- Inputs: current location, pickup, dropoff, current cycle used (hours)
- Outputs: interactive map with route/stops/rests, FMCSA daily log sheets (drawn grid, multiple days)
- Stack: Django REST API backend, React (Vite) frontend
- Assumptions: property-carrying, 70hr/8day, fuel every 1000mi, 1hr pickup/dropoff, 55mph average
- Use free APIs: OSRM for routing, Nominatim for geocoding, Leaflet/OSM for maps
- Implement HOS rules from FMCSA Driver's Guide: 11hr drive, 14hr window, 30min break after 8hr, 10hr rest
- Daily log must match paper form: 4 duty rows, 15-min grid, remarks, 70/8 recap section

Read docs/ASSESSMENT.md and docs/HOS_RULES.md before coding.
```

---

## Prompt 2 — HOS engine

```
Implement or refine backend/trips/hos_engine.py for FMCSA property-carrying drivers.

Rules:
- MAX_DRIVE_HOURS = 11 after 10h off duty
- MAX_WINDOW_HOURS = 14 from first on-duty
- 30-minute off-duty break required after 8 cumulative driving hours
- 10-hour sleeper berth resets drive and window clocks
- Track 70-hour on-duty rolling cycle (driving + on-duty not driving)
- Fuel: 30 min on-duty every 1000 miles
- Pickup and dropoff: 1 hour on-duty each

The engine should accept geocoded legs (current→pickup, pickup→dropoff) with mile distances,
simulate the trip chronologically, split into DailyLog objects per calendar day,
and pad each day to 24 hours on the grid with off-duty.

Return TripPlan with stops, instructions, daily_logs, and route coordinates.
Add unit tests for: single-day short trip, multi-day long trip, break at 8h, cycle recap math.
```

---

## Prompt 3 — Daily log UI

```
Build frontend/src/components/DailyLogSheet.jsx to render FMCSA paper daily logs.

Match the blank log form structure:
- Header: date (month/day/year), from/to, total miles
- Grid: 24 hours × 15-minute cells, rows for Off Duty, Sleeper Berth, Driving, On Duty
- Draw filled cells from backend segments (start/end ISO timestamps)
- Show per-row hour totals (must sum to 24)
- Remarks list from segment remarks
- Recap block: 70hr/8day A, B, C values from API

Style for printability and clarity. Support multiple sheets in a scrollable list for multi-day trips.
```

---

## Prompt 4 — Map & routing

```
Implement trip routing in backend/trips/routing.py and RouteMap.jsx.

Backend:
- Geocode US addresses via Nominatim (set User-Agent)
- Route via OSRM public API; fallback to haversine × 1.25 if OSRM fails
- Return GeoJSON coordinates as [lat, lon] for Leaflet

Frontend:
- react-leaflet MapContainer with OSM tiles
- Polyline for full route
- Markers for start, pickup, dropoff with popups showing arrival times
- Leg summary chips with mile distances
```

---

## Prompt 5 — API integration

```
Wire POST /api/plan-trip/ end-to-end.

Request body:
{ current_location, pickup_location, dropoff_location, cycle_used_hours }

Response:
{ locations, legs, stops, route_coordinates, daily_logs, instructions,
  total_miles, total_days, cycle_hours_used, cycle_hours_remaining }

Frontend: TripForm submits to API via axios; show loading and error states.
Vite dev proxy /api → Django :8000.
```

---

## Prompt 6 — Deployment

```
Prepare Track Log for production deployment.

Backend (Render/Railway):
- gunicorn tracklog.wsgi
- ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS env vars
- requirements.txt, migrate on deploy

Frontend (Vercel):
- VITE_API_URL=https://your-api.onrender.com/api
- npm run build

Document steps in README.md. Ensure CORS allows frontend origin.
```

---

## Prompt 7 — Accuracy test cases

```
Validate HOS planner against these manual scenarios:

1. Chicago IL → Indianapolis IN → Columbus OH (~400 mi): likely 1 day, no overnight rest
2. Los Angeles CA → Denver CO (~1000+ mi): 2+ days, at least one 10h sleeper rest
3. cycle_used_hours=65: trip should warn or fail if would exceed 70hr limit
4. Trip >2000 mi: verify fuel stops every 1000 miles appear as on-duty segments
5. Verify 30-min break appears after 8h cumulative driving in a single shift

Fix hos_engine.py until grid totals per day equal 24 hours and driving never exceeds 11h per shift.
```

---

## Prompt 8 — UI polish (assessment grading)

```
Improve Track Log UI for the assessment ($100 reward criteria):

- Professional trucking/logistics aesthetic (dark navy theme, clear typography)
- Responsive layout: form sidebar + map/results main area
- Empty state explaining HOS assumptions
- Route instructions as numbered steps
- Log sheets visually match FMCSA paper form colors per duty status
- Mobile-friendly horizontal scroll on log grid

Good UX should compensate for minor calculation edge cases per assessment instructions.
```
