# Warranty Watch — Project Handoff Report

A personal after-sales intelligence platform for product warranties, service requests,
recalls and AI-assisted troubleshooting. This document captures the exact state of the
project so development can continue with another assistant.

Project root: `C:\Users\sanid\OneDrive\Desktop\Tinyfish`

---

## 1. Current project architecture

**Backend (built and boots):** FastAPI + SQLAlchemy + SQLite + the official TinyFish Python SDK.

- `main.py` — FastAPI app. The lifespan creates tables, seeds demo data, and regenerates notifications on startup. CORS is open (`*`) for local dev.
- `database.py` — SQLAlchemy engine, `SessionLocal`, `Base`, `init_db()`.
- `models.py` — ORM models: `Product`, `ServiceRequest`, `RecallAlert`, `Notification`, `TinyFishActivity`, `Monitor`, `Setting`.
- `schemas.py` — Pydantic v2 request/response models.
- `serialize.py` — ORM → schema converters (adds computed fields like warranty status).
- `warranty_service.py` — warranty / AMC status computed from stored dates (never hardcoded).
- `notification_service.py` — generates warranty (30/7/expired), AMC, and recall notifications with de-duplication that preserves read state.
- `settings_service.py` — persistent live/demo mode setting.
- `demo_data.py` — seeds clearly-labelled demo products, a service request and a recall alert when the DB is empty.
- `services/tinyfish/` — one module per TinyFish capability (see §6). `runner.py` routes every call to **live** (real SDK) or **demo** (labelled sample data) based on the `mode` setting and key presence.
- `routes/` — REST layer. Orchestrates capabilities, e.g. Warranty Intelligence = Search → Fetch; AI Assistant = Search → Fetch → Agent.

**Mode system:** default mode is `live` (because an API key is present). Toggle with
`PUT /api/settings/mode`. In `demo` mode (or when no key is present), every TinyFish call
returns clearly-labelled sample data and records an activity with `status="demo"` — never
reported as a live success.

**Frontend:** NOT created. This is the largest remaining gap (see §3).

### REST API contract (for the frontend developer)

- `GET /api/health`, `GET /api/tinyfish/health`
- `GET /api/dashboard`
- Products: `GET/POST /api/products` · `GET /api/products/categories` · `GET /api/products/statuses` · `GET/PUT/DELETE /api/products/{id}` · `POST/DELETE /api/products/{id}/invoice` · `GET /api/products/{id}/invoice`
- `POST /api/warranty/investigate` body `{product_id, manufacturer, model_number?, category?}` → `{search, fetch, top_url}`
- `POST /api/assistant/investigate` body `{product_id, issue}` → `{search, fetch, agent, top_url}`
- Service requests: `GET/POST /api/service-requests` · `PUT/DELETE /api/service-requests/{id}` · `POST /api/service-requests/{id}/check-status`
- Recalls: `GET/POST /api/recalls` · `DELETE /api/recalls/{id}` · `POST /api/recalls/discover`
- Notifications: `GET /api/notifications` · `POST /api/notifications/regenerate` · `POST /api/notifications/{id}/read` · `POST /api/notifications/read-all`
- Monitors: `GET/POST /api/monitors` · `POST /api/monitors/{id}/run` · `DELETE /api/monitors/{id}`
- Activity: `GET /api/activity?limit=`
- Settings: `GET /api/settings` · `PUT /api/settings/mode` (body `{mode}`) · `GET /api/settings/capabilities`

---

## 2. All files created and modified

### Backend files created this session (hand-written)

```
backend/
  config.py
  database.py
  models.py
  schemas.py
  serialize.py
  warranty_service.py
  notification_service.py
  settings_service.py
  demo_data.py
  main.py
  routes/
    __init__.py
    products.py
    dashboard.py
    warranty.py
    assistant.py
    service_requests.py
    recalls.py
    notifications.py
    monitors.py
    activity.py
    settings.py
    tinyfish.py
  services/
    __init__.py
    tinyfish/
      __init__.py
      client.py
      activity.py
      runner.py
      search.py
      fetch.py
      agent.py
      browser.py
      monitor.py
```

### Auto-generated (not hand-written; safe to delete/regenerate)

- `backend/warrantywatch.db` — SQLite DB created on first server run. Already seeded with demo data (Samsung refrigerator, LG washing machine, Daikin AC, Sony TV, one service request, one recall alert, notifications).
- `backend/uploads/` — empty invoice upload directory.
- `backend/__pycache__/`, `backend/routes/__pycache__/`, `backend/services/__pycache__/`, `backend/services/tinyfish/__pycache__/` — Python bytecode caches.

### Scratch files at project root (created for verification; safe to delete)

- `install_out.txt`, `smoke.txt`, `smoke2.txt`, `_depcheck.py`, `_smoke.py`

### Preserved (untouched this session)

- `.env`, `.gitignore`, `README.md`, `requirements.txt`, `test_agent.py`, `.venv/`

### Modified existing files

- None. No existing working files were edited. (The only fix was a typo in `config.py`, a file created this session.)

---

## 3. Completed and pending features

### Completed (backend)

- Database, ORM models, and demo-data seeding.
- Product CRUD + invoice upload/download (served via a non-public `FileResponse` endpoint, not a public static mount).
- Warranty status calculated from stored dates.
- Dashboard aggregates (counts, upcoming expiries, recent activity, breakdowns).
- Notification generation with de-duplication and read-state preservation.
- Service request tracker with manual status updates.
- Recall & alert centre with a Search-based "discover" action.
- TinyFish Activity Centre (persisted to the DB).
- Settings: live/demo mode toggle, key-status indicator.
- TinyFish health endpoint (free, non-billed).
- Demo mode data for every capability.
- TinyFish Search / Fetch / Agent / Browser / Monitor — code written and import-verified.

### Pending

- **Frontend — 0% done.** The 10 pages (Dashboard, My Products, Add Product, Product Details, Warranty Intelligence, AI Service Assistant, Service Requests, Recall & Alerts, TinyFish Activity Centre, Settings) with React + Vite + TypeScript + Tailwind + Lucide + Recharts.
- **Tests (pytest) — 0% done.**
- `requirements.txt` does not yet list the backend dependencies installed in `.venv`.
- `.gitignore` should add `warrantywatch.db` and `backend/uploads/`.
- `README.md` still describes the original `test_agent.py` setup, not Warranty Watch.
- Runtime verification of live TinyFish calls (see §6, §7).

---

## 4. Exact frontend and backend run commands

### Backend (working — confirmed to boot)

From the project root `C:\Users\sanid\OneDrive\Desktop\Tinyfish`:

```powershell
.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --port 8000
```

API base: `http://127.0.0.1:8000`

### Frontend (does not exist yet — scaffolding starting point)

```powershell
mkdir frontend
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install lucide-react recharts react-router-dom axios
npm run dev
```

Configure Vite to proxy `/api` → `http://127.0.0.1:8000` so the SPA and backend share an origin during development.

---

## 5. Environment variables required

Only one variable is required, and it is a secret — never print, log, or commit it.

```
TINYFISH_API_KEY=<your key here>
```

- Stored in `.env` at the project root.
- `.env` is in `.gitignore` and must never be committed.
- The backend reads it via `python-dotenv` in `backend/config.py` (`tinyfish_api_key()`).
- No other environment variables are required.

Verification performed: the `.env` file still contains a non-empty `TINYFISH_API_KEY` (confirmed present without exposing its value). The application code only **reads** `.env`; nothing writes to it, and the key is never logged or sent to the TinyFish activity log.

---

## 6. Actual implementation status of all five TinyFish capabilities

All five are implemented in separate modules using SDK signatures read directly from the
installed SDK source (`tinyfish 0.11.0`). They are **import-verified** (the backend imports
cleanly). They are **not yet runtime-verified** against the live TinyFish API in this session.

| Capability | Verified SDK call | Module | Runtime-tested? |
|---|---|---|---|
| **Search** | `client.search.query(query, purpose, include_domains, domain_type, …)` → `SearchQueryResponse` (`results` list with `title`, `url`, `snippet`, `site_name`) | `services/tinyfish/search.py` | No |
| **Fetch** | `client.fetch.get_contents(urls, purpose, format, links, include_etag_and_last_modified, …)` → `FetchResponse` (`results` with `text`, `title`, `links`, `etag`, `last_modified`, `not_modified`) | `services/tinyfish/fetch.py` | No |
| **Agent** | `client.agent.run(goal, url, output_schema=…)` → `AgentRunResponse` (`status`, `result`, `error`, `run_id`, `num_of_steps`) | `services/tinyfish/agent.py` | No (the user's earlier `test_agent.py` reportedly completed an Agent task, confirming the SDK + key work in general) |
| **Browser** | `client.browser.sessions.create(url, timeout_seconds)` → `BrowserSession` (`session_id`, `cdp_url`, `base_url`) | `services/tinyfish/browser.py` | No |
| **Monitor** | `client.monitors.create(type, config, schedule_cron, …)` plus `.list/.get/.run/.pause/.resume/.cancel` | `services/tinyfish/monitor.py` | No |

Each capability routes through `services/tinyfish/runner.py`, which records a live
(completed/failed) or demo activity to the `TinyFishActivity` table for the Activity Centre.

---

## 7. Errors and incomplete integrations

- **Fixed:** `config.py` used `@lr_cache()` (typo); corrected to `@lru_cache()`. After the fix the backend imports cleanly (`IMPORT_OK`) and the server boots (`Application startup complete`).
- **No endpoint was exercised at runtime.** The server started successfully, but the curl test of endpoints was interrupted before approval. Endpoints are written and the app boots, but individual endpoint responses were not confirmed.
- **Live TinyFish calls are not runtime-verified** (billing caution + the interruption). The code matches the SDK's actual signatures, but a live success was not observed this session. Do not mark any capability "fully working" until one real call succeeds and the result is recorded.
- **`requirements.txt`** currently lists only `tinyfish` and `python-dotenv`. The backend dependencies installed in `.venv` are not recorded there. Recommended full content:
  ```
  tinyfish
  python-dotenv
  fastapi
  uvicorn[standard]
  sqlalchemy
  python-multipart
  pytest
  ```
  Observed versions during the build: fastapi 0.162.0, uvicorn 0.54.0, sqlalchemy 2.1.6, pydantic 2.14.2.
- **`.gitignore`** should add `warrantywatch.db` and `backend/uploads/`.
- **CORS** is `allow_origins=["*"]` (dev only); tighten before any deployment.
- **Agent start URL:** if Search returns no support URL, Agent starts at a Google search URL. The normal path uses the discovered official support URL.
- **Browser interaction:** `client.browser.sessions.create()` opens a real remote session. Deeper page interaction (clicks, form inspection) requires a CDP client connected to `cdp_url`; that driver is not implemented. The current flow opens the portal and returns the live session for the user to interact with — it does not auto-submit forms or bypass auth.

---

## 8. Steps required to run and test the application

1. **Ensure the API key is present** in `.env` (`TINYFISH_API_KEY=...`). Without it, the app still runs in demo mode.
2. **Confirm backend dependencies are installed in `.venv`** (or install them):
   ```powershell
   .venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" sqlalchemy python-multipart pytest
   ```
3. **Start the backend** from the project root:
   ```powershell
   .venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --port 8000
   ```
4. **Smoke-check imports** (no server needed):
   ```powershell
   .venv\Scripts\python.exe _smoke.py
   ```
   Expect `IMPORT_OK`.
5. **Verify basic endpoints** (in another terminal):
   ```powershell
   curl http://127.0.0.1:8000/api/health
   curl http://127.0.0.1:8000/api/dashboard
   curl http://127.0.0.1:8000/api/products
   curl http://127.0.0.1:8000/api/tinyfish/health
   ```
   The last one performs a free (non-billed) `monitors.list()` reachability check against TinyFish.
6. **Verify live TinyFish capabilities (each bills credits; do one call per capability):**
   - Search + Fetch: `POST /api/warranty/investigate` with a product's `{manufacturer, model_number}`.
   - Agent: `POST /api/assistant/investigate` with `{product_id, issue}`.
   - Browser: `POST /api/service-requests/{id}/check-status` (requires a service request with a portal URL).
   - Monitor: `POST /api/monitors` to create, then `POST /api/monitors/{id}/run`, then `DELETE /api/monitors/{id}` to clean up.
   - Record the actual result for each before marking it "fully working."
7. **Toggle modes** as needed: `PUT /api/settings/mode` with `{"mode":"demo"}` or `{"mode":"live"}`.
8. **Build the frontend** (pending) using the scaffolding commands in §4, then implement the pages against the API contract in §1.
9. **Add tests** (pending) for product CRUD, warranty expiry calculation, invoice validation, notification generation, DB persistence, and one real call per TinyFish capability.

---

### Notes for the next developer

- The DB is already seeded with demo data, so the dashboard and product list will be populated immediately on first run.
- The original `test_agent.py` (from the initial TinyFish setup) still works and is a good reference for a minimal live Agent call.
- This `HANDOFF.md` is the only file added in this step; no existing implementation was modified.
