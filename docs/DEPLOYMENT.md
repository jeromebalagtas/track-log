# Track Log — Deployment Guide

## Vercel (recommended — frontend + API in one project)

### 1. Import project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import `haruki-izumo/track-log`

### 2. Project settings

| Setting | Value |
|---------|--------|
| **Framework Preset** | **Other** (not "Services") |
| **Root Directory** | `./` |
| **Build Command** | `npm run build --prefix frontend` |
| **Output Directory** | `frontend/dist` |
| **Install Command** | `npm install --prefix frontend` |

Root `vercel.json` configures this automatically.

### 3. How routing works

```
https://your-app.vercel.app/
├── /                 → React app (frontend/dist)
├── /api/health       → Python serverless (api/health.py)
└── /api/plan-trip    → Python serverless (api/plan-trip.py)
```

Trip planning logic lives in `backend/trips/` and is imported by `api/plan-trip.py`.
Django in `backend/` is for **local development only**.

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
| 404 on `/api/health` | Framework preset must be **Other**, not Services. Root `vercel.json` must exist. |
| Homepage 404 | `outputDirectory` must be `frontend/dist` |
| "A server error has occurred" | Backend function crashed — check Deployments → Functions → Logs |

---

## Optional: Django on Render

For a full Django host (not required if Vercel API works):

- Deploy `backend/` to Render/Railway with `gunicorn tracklog.wsgi`
- Set `VITE_API_URL` on Vercel to your Render API URL
