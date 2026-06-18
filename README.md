# Track Log

FMCSA Hours of Service trip planner — Full Stack Developer Assessment.

Takes trip locations and cycle hours, outputs a compliant route plan, interactive map, and filled **Driver's Daily Log** sheets.

## Features

- Geocoding & routing (Nominatim + OSRM — free, no API keys)
- HOS compliance engine: 11h drive, 14h window, 30min break, 10h rest, 70/8 cycle
- Fuel stops every 1,000 miles; 1h pickup/dropoff on-duty
- Paper-style daily log grids with duty status coloring and 70/8 recap
- Multi-day trips generate multiple log sheets

## Quick start

### Prerequisites

- Python 3.12+
- Node.js 20+

### Backend

```powershell
cd f:\track-log\backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Or use the helper script:

```powershell
.\scripts\run-backend.ps1
```

API health check: http://127.0.0.1:8000/api/health/ should return `{"status":"ok","service":"track-log-api"}`.

If port 8000 is already in use, run `python manage.py runserver 8001` and set the Vite proxy in `frontend/vite.config.js` to `http://127.0.0.1:8001`.

### Frontend

```powershell
cd f:\track-log\frontend
npm install
npm run dev
```

Or:

```powershell
.\scripts\run-frontend.ps1
```

App: http://localhost:5173

## Example request

```bash
curl -X POST http://127.0.0.1:8000/api/plan-trip/ \
  -H "Content-Type: application/json" \
  -d "{\"current_location\":\"Chicago, IL\",\"pickup_location\":\"Indianapolis, IN\",\"dropoff_location\":\"Columbus, OH\",\"cycle_used_hours\":0}"
```

## Documentation

- [Assessment requirements](docs/ASSESSMENT.md)
- [HOS rules reference](docs/HOS_RULES.md)
- [AI development prompts](docs/PROMPTS.md)
- [Agent guide](AGENTS.md)

## Deployment

### Frontend (Vercel)

This repo includes a root `vercel.json` so Vercel builds the React app from `frontend/` automatically.

1. Import https://github.com/haruki-izumo/track-log in Vercel
2. Leave **Root Directory** empty (use repo root — `vercel.json` handles paths)
3. Add environment variable: `VITE_API_URL` = `https://your-backend.example.com/api`
4. Deploy

If you previously set Root Directory to something else, clear it or set it to `.` so `vercel.json` is picked up.

### Backend (Render / Railway)

- Start command: `gunicorn tracklog.wsgi --chdir backend`
- Set `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` (include your Vercel URL)
- Install: `pip install -r backend/requirements.txt`

## Tech stack

- Django 6 + Django REST Framework
- React 19 + Vite + Leaflet
- OpenStreetMap / OSRM / Nominatim

## License

Assessment project — FMCSA rules are public domain guidance; map data © OpenStreetMap contributors.
