# Track Log — Deployment Guide

Deploy **frontend + backend together** on Vercel using **Services** mode (one project, one URL).

---

## Step 1: Push latest code

Make sure GitHub has the latest `vercel.json` with `experimentalServices`:

https://github.com/haruki-izumo/track-log

---

## Step 2: Import on Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **Import** next to `haruki-izumo/track-log`
3. On the configuration screen (your screenshot):

| Setting | Value |
|---------|--------|
| **Application Preset** | **Services** (keep this — Vercel detected frontend + backend) |
| **Project Name** | `track-log` (or any name) |
| **Root Directory** | `./` (repo root) |

4. Vercel should detect:
   - **Frontend** → `frontend/` (Vite) at `/`
   - **Backend** → `backend/` (Django) at `/api`

5. If it says *"vercel.json required"*, click **Refresh** after the latest push — the repo now includes it.

---

## Step 3: Environment variables (recommended)

In **Environment Variables**, add:

| Name | Value | Notes |
|------|--------|--------|
| `SECRET_KEY` | *(random 50+ char string)* | Required for Django in production |
| `DEBUG` | `False` | Production |
| `DJANGO_API_PREFIX` | *(leave empty)* | Backend mounted at `/api` on Vercel |

You do **not** need `VITE_API_URL` when using Services — frontend calls `/api` on the same domain.

Generate a secret key locally:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Step 4: Deploy

1. Click **Deploy**
2. Wait for both services to build (frontend + backend)
3. Open your URL: `https://track-log-xxxx.vercel.app`

---

## Step 5: Verify it works

1. **Frontend** — page loads with the Track Log UI (not 404)
2. **Backend health** — open:
   ```
   https://YOUR-URL.vercel.app/api/health/
   ```
   Expected: `{"status":"ok","service":"track-log-api"}`
3. **Full flow** — enter cities and click **Plan Trip & Generate Logs**

---

## Architecture (how it works)

```
https://track-log.vercel.app/
├── /                    → Vite React app (frontend service)
└── /api/plan-trip/      → Django API (backend service)
    /api/health/
```

`vercel.json` routes traffic:

- `/` → `frontend/` (Vite build)
- `/api/*` → `backend/` (Django)

---

## Troubleshooting

### Deploy button is disabled / "vercel.json required"
- Pull latest `main` from GitHub
- Click **Refresh** on the Vercel import screen
- Confirm **Application Preset** = **Services**

### 404 on homepage
- Preset must be **Services**, not Vite-only
- `vercel.json` must include `experimentalServices`

### Trip planning fails (network error)
- Check `https://YOUR-URL.vercel.app/api/health/`
- Set `SECRET_KEY` and redeploy
- Check Vercel → Deployments → backend build logs

### Build fails on backend
- Ensure `backend/requirements.txt` exists
- Check Python version (3.12+)

---

## Alternative: split deployment (optional)

If Services mode causes issues, deploy separately:

| Part | Platform | Root |
|------|----------|------|
| Frontend | Vercel | Set preset to **Vite**, Root Directory = `frontend` |
| Backend | [Render](https://render.com) or Railway | `backend/` |

Then set on Vercel: `VITE_API_URL=https://your-backend.onrender.com/api`

---

## Local development (unchanged)

```powershell
# Terminal 1
.\scripts\run-backend.ps1

# Terminal 2
.\scripts\run-frontend.ps1
```

Open http://localhost:5173
