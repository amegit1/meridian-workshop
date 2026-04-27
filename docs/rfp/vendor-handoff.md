# Handoff Notes — Inventory Dashboard

*Prepared by previous vendor at contract end, Nov 2024. Provided by Meridian as part of the RFP package.*

---

## Stack

- Frontend: Vue 3 + Composition API + Vite (port 3000)
- Backend: Python FastAPI (port 8001)
- Data: JSON files in `server/data/` loaded via `server/mock_data.py` (no database)

## Running it

```bash
# Backend
cd server && uv run python main.py

# Frontend
cd client && npm install && npm run dev
```

There is also a `scripts/start.sh` that runs both.

## API

- `GET /api/inventory` — filters: warehouse, category
- `GET /api/orders` — filters: warehouse, category, status, month
- `GET /api/dashboard/summary` — all filters
- `GET /api/demand`, `/api/backlog` — no filters
- `GET /api/spending/*` — summary, monthly, categories, transactions

## Patterns

- Filter system: 4 filters (Time Period, Warehouse, Category, Order Status) apply via query params
- Data flow: Vue filters → `client/src/api.js` → FastAPI → in-memory filtering → Pydantic → computed properties
- Reactivity: raw data in refs, derived data in computed

## Known issues at handoff

- Reports module was in progress; not all filters wired up
- No automated tests were delivered
- Some views still use older patterns (Options API) — migration incomplete

## Design tokens

- Colors: slate/gray (#0f172a, #64748b, #e2e8f0)
- Status colors: green/blue/yellow/red
- Charts: custom SVG, CSS Grid layouts

## File map

- Views: `client/src/views/*.vue`
- API client: `client/src/api.js`
- Backend: `server/main.py`, `server/mock_data.py`
- Data: `server/data/*.json`
