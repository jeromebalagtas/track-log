# Full Stack Developer Assessment

## Deliverables

1. Live hosted version (e.g. Vercel for frontend + Render/Railway for Django API)
2. 3–5 minute Loom walkthrough of app and code
3. GitHub repository

## Objective

Build an app that takes trip details as inputs and outputs **route instructions** and **drawn ELD / daily log sheets**.

## Inputs

- Current location
- Pickup location
- Dropoff location
- Current Cycle Used (hours) — 70-hour / 8-day rolling total before trip

## Outputs

1. **Map** showing route with stops and rests (free map API)
2. **Daily Log Sheets** — filled paper-style logs with duty grid drawn; multiple sheets for multi-day trips

## Assumptions (fixed for grading)

| Rule | Value |
|------|-------|
| Driver type | Property-carrying |
| Cycle | 70 hours / 8 days |
| Adverse driving | None |
| Fueling | At least once every 1,000 miles |
| Pickup / dropoff | 1 hour on-duty each |

## Grading notes

- Accuracy of HOS calculations is tested on hosted build
- Good UI/UX can offset minor inaccuracies
- $100 reward for meeting standards

## Implementation mapping (this repo)

| Requirement | Implementation |
|-------------|----------------|
| Django + React | `backend/` + `frontend/` |
| Map + route | Leaflet + OSRM + Nominatim |
| Daily logs | `DailyLogSheet.jsx` + `hos_engine.py` |
| Multi-day logs | `HOSEngine._finalize_day()` per calendar day |
| 70/8 recap | `DailyLog.recap_70_8()` on each sheet |
