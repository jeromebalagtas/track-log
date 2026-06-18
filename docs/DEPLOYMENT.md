# Track Log — Deployment Guide

## Vercel (recommended — frontend + API in one project)

### 1. Import project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import `haruki-izumo/track-log`

### 2. Project settings

| Setting | Value |
|---------|--------|
| **Application Preset** | **Services** (Vercel auto-detects frontend + API) |
| **Root Directory** | `./` |

Root `vercel.json` must include `experimentalServices` — this is already in the repo. Click **Refresh** on the import screen if Deploy is disabled.

### 3. How routing works

```
https://your-app.vercel.app/
├── /                 → React app (frontend/ — Vite)
├── /api/health       → Python API (api/index.py)
└── /api/plan-trip    → Python API (api/index.py)
```

`vercel.json` `experimentalServices` defines two services: **frontend** (Vite) and **api** (Python). The `backend/` Django project is for local dev only.

### 4. Deploy

Click **Deploy**. No extra environment variables required for basic operation.

### 5. Verify

1. `https://YOUR-URL.vercel.app/api/health` → `{"status":"ok","service":"track-log-api"}`
2. Open the app and plan a trip (Chicago → Indianapolis → Columbus)

---

## Local development

```powershell
# Terminal 1 — Django API
.\scripts\run-backend.ps1

# Terminal 2 — React UI
.\scripts\run-frontend.ps1
```

Open http://localhost:5173

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| 500 on `/api/plan-trip` | Redeploy latest `main`. Check Vercel function logs for `api/plan-trip.py`. |
| 404 on `/api/health` | Click **Refresh** on import screen; confirm `vercel.json` has `experimentalServices` |
| Homepage 404 | `outputDirectory` must be `frontend/dist` |
| "A server error has occurred" | Backend function crashed — check Deployments → Functions → Logs |

---

## Optional: Django on Render

For a full Django host (not required if Vercel API works):

- Deploy `backend/` to Render/Railway with `gunicorn tracklog.wsgi`
- Set `VITE_API_URL` on Vercel to your Render API URL
