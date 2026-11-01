# Warranty Watch — Personal After-Sales Intelligence Platform

A comprehensive after-sales intelligence platform for home appliances and consumer electronics. Powered by the **TinyFish Python SDK** across all five core capabilities (**Search**, **Fetch**, **Agent**, **Browser**, and **Monitor**), paired with a **FastAPI** backend and a **React + Vite + TypeScript + Tailwind CSS** dashboard.

---

## 🌟 Features & The 5 TinyFish Capabilities

1. **Search (Discovery Engine):**
   - Discovers official manufacturer warranty pages, OEM service portals, repair depots, and safety notices.
   - Powers the **Warranty Intelligence** and **Recall Discovery** modules.

2. **Fetch (Policy Extraction):**
   - Extracts clean markdown text, clauses, compressor/motor warranty terms, and exclusions directly from official URLs.

3. **Agent (Autonomous Issue Triage):**
   - Investigates user-reported appliance breakdowns (e.g. fluctuating refrigerator temperatures, drain pump error codes) through multi-step reasoning.
   - Enforces a strict JSON output schema separating diagnosis, warranty eligibility, exclusions, and safe repair procedures.

4. **Browser (Support Portal Interaction):**
   - Provisions remote browser sessions via `client.browser.sessions.create()` for OEM service portals (e.g. Samsung, LG).
   - Allows users to check ticket progress and handle customer authentication securely.

5. **Monitor (Policy Change Watcher):**
   - Cloud-scheduled recurring monitors that track updates to manufacturer warranty policies and detect new recall bulletins.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.13 (virtual environment already setup in `.venv/`)
- Node.js v20+ / v26+ and npm
- A valid TinyFish API Key in `.env`:
  ```
  TINYFISH_API_KEY=your_key_here
  ```

---

### 2. Start the Backend API (FastAPI)

Open a terminal at the project root (`C:\Users\sanid\OneDrive\Desktop\Tinyfish`):

```powershell
# Start the FastAPI server on port 8000
.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --port 8000
```

- **Backend Base URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

---

### 3. Start the Frontend Dashboard (React + Vite)

Open a second terminal at the project root:

```powershell
cd frontend
npm.cmd run dev
```

- **Frontend URL:** `http://localhost:5173`
- *Note: Vite automatically proxies all `/api` requests to `http://127.0.0.1:8000`.*

---

### 4. Run Automated Backend Tests

```powershell
.venv\Scripts\pytest.exe tests\test_backend.py
```

---

## 🖥️ Application Screens (10 Views)

1. **Dashboard:** High-level overview of appliances, upcoming 30-day expiries, category distribution, and live TinyFish telemetry.
2. **My Products:** Full appliance catalog with dynamic warranty badges, purchase dates, and attached proof-of-purchase invoices.
3. **Add Appliance:** Registration form with auto-calculated warranty expiry and secure document upload (PDF/Images).
4. **Product Details:** Complete specification sheet, countdown timer, AMC status, and invoice downloader.
5. **Warranty Intelligence:** TinyFish Search + Fetch workflow extracting official warranty terms from live OEM websites.
6. **AI Troubleshooter:** TinyFish Agent diagnosing symptoms with structured JSON findings and safety guidance.
7. **Service Requests:** Repair ticket management and TinyFish Browser portal launcher.
8. **Recall Alerts:** Active safety bulletins with automated Search discovery for any brand/model.
9. **Activity Centre:** Real-time audit trail and JSON provenance viewer for every capability call.
10. **Settings:** Toggle between **Live SDK Mode** and **Demo Mode**, inspect API credentials status, and manage TinyFish Monitors.

