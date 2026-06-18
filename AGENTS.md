# Track Log — Agent & Development Prompts

Full-stack FMCSA Hours of Service trip planner (Django + React).

## Quick context

| Source | Purpose |
|--------|---------|
| `docs/ASSESSMENT.md` | Full-stack dev assessment requirements |
| `docs/HOS_RULES.md` | FMCSA HOS rules encoded in the app |
| `docs/PROMPTS.md` | Copy-paste prompts for AI-assisted development |
| `backend/trips/hos_engine.py` | Core compliance planner |
| `frontend/src/components/DailyLogSheet.jsx` | Paper log grid renderer |

## Stack

- **Backend:** Django 6 + DRF, OSRM routing, Nominatim geocoding
- **Frontend:** React 19 + Vite, Leaflet maps
- **Assumptions:** Property-carrying, 70 hr/8 day, no adverse conditions

## Run locally

```bash
# Backend (from backend/)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (from frontend/)
npm install
npm run dev
```

Open http://localhost:5173

## API

`POST /api/plan-trip/`

```json
{
  "current_location": "Chicago, IL",
  "pickup_location": "Indianapolis, IN",
  "dropoff_location": "Columbus, OH",
  "cycle_used_hours": 0
}
```

## When extending

1. Read `docs/HOS_RULES.md` before changing `hos_engine.py`
2. Keep daily log grid aligned with FMCSA paper form (4 duty rows, 15-min quarters)
3. Multi-day trips must emit one `DailyLog` per calendar day
4. Test with a 2,000+ mile route to verify multiple log sheets and fuel stops
