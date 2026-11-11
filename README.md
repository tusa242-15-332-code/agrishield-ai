# AgriShield AI

**Climate-aware crop intelligence and farmer-first marketplace for Bangladesh.**

This is a full-stack MVP that combines the strongest parts of the AgriVibes BD concept with the AgriShield AI direction, but presents them in a simpler product structure.

## Product structure

- **Farmer workspace:** Overview, Farm Planner, Climate & Risk, Disease Scan, Irrigation, Marketplace, Harvest & Traceability.
- **Consumer marketplace:** Separate shopping experience with search, category filters, sorting, product cards, favorites, and a demo basket.
- **AgriBot:** A small retrieval-based assistant that answers from a curated, cautious agriculture knowledge set.

## Stack

- Frontend: React + Vite, Recharts, Lucide icons, responsive CSS.
- Backend: Python + FastAPI + Pydantic.
- Weather: Open-Meteo forecast API (no API key required). If unavailable, the backend explicitly returns fallback sample data.
- Storage: In-memory demo records for produce listings and activity logs. This is intentional for a fast MVP, not production persistence.

## Run locally

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs
Health check: http://localhost:8000/api/health

### 2. Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally http://localhost:5173).

Optional frontend API override: create `frontend/.env` with:

```env
VITE_API_URL=http://localhost:8000
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Backend health |
| GET | `/api/dashboard?district=Bogura` | Farmer overview data |
| GET | `/api/weather?district=Bogura` | Live Open-Meteo forecast, with clearly labelled fallback |
| POST | `/api/assess-risk` | Transparent rule-based climate exposure screening |
| POST | `/api/farm-plan` | Illustrative crop cost/yield planning estimate |
| GET | `/api/produce` | Marketplace listings with optional category/search filters |
| POST | `/api/produce` | Add a produce listing in the current backend process |
| POST | `/api/disease/scan` | Validate and receive a leaf image; does not claim diagnosis |
| POST | `/api/assistant` | Retrieve basic guidance from curated agriculture notes |
| GET | `/api/locations` | Supported Bangladesh district presets |

## Important accuracy and demo boundaries

This project is a competition MVP, not a deployed agricultural advisory service. It deliberately avoids pretending that illustrative data is real sensor telemetry or validated AI output.

- Dashboard soil readings, farm revenue, harvest records, and product listings are sample/demo records.
- Weather is fetched from Open-Meteo when available. The UI labels fallback data as sample data.
- Risk screening is a transparent rule-based prototype. It is **not** a trained or validated machine-learning prediction model.
- Farm-plan cost and yield ranges are illustrative coefficients. They are not guaranteed outcomes or profit forecasts.
- Disease image upload is implemented, but no trained plant-disease classifier is bundled. The endpoint will not invent a disease diagnosis or pesticide dose.
- AgriBot uses a small keyword-retrieval knowledge set, not a large language model or full RAG pipeline yet.
- Marketplace basket, favorites, and activity logs are demo interactions. No payment, delivery, authentication, or production order management is connected.
- IoT controls, insurance, robotics, live auctions, and public QR verification from the original concept are intentionally left out of the first MVP. They can be added later after real hardware/data integrations exist.

## Before a public/competition deployment

1. Replace in-memory data with PostgreSQL and SQLAlchemy/Alembic migrations.
2. Add authentication and role-based access for farmers, consumers, and admins.
3. Add a validated crop-disease model and evaluate it on local field images before showing diagnoses.
4. Train and validate climate/crop risk models with documented Bangladesh datasets and hold-out evaluation.
5. Replace illustrative agronomic coefficients with verified crop budgets, local market prices, and extension-approved recommendations.
6. Add real sensor ingestion only after the ESP32/LoRa hardware and calibration are tested.
7. Add order, payment, delivery, and QR verification services before claiming production marketplace functionality.
8. Add logging, rate limiting, file scanning, backups, privacy notices, and production CORS settings.

## Suggested demo walkthrough

1. Start at Overview and explain that sample sensor values are clearly marked.
2. Change the district to show the weather panel refresh.
3. Open Farm Planner, choose a crop/land type/budget, and generate a draft plan.
4. Open Climate & Risk and run the transparent screening.
5. Open Disease Scan and show the safe image-upload workflow, including its no-classifier notice.
6. Open Marketplace, search/filter produce, add an item to the basket, and show farmer listing creation.
7. Finish with a sample traceability batch and the activity log.

## Project layout

```text
agrishield-ai/
  backend/
    app/main.py
    requirements.txt
    .env.example
  frontend/
    index.html
    package.json
    src/main.jsx
    src/App.jsx
    src/styles.css
  docs/
    architecture.md
  README.md
```


## Deploy for free without VS Code

See [DEPLOY_FREE_NO_VSCODE.md](./DEPLOY_FREE_NO_VSCODE.md). The Dockerfile builds the frontend and serves it from the FastAPI service, so one Render service provides one public URL.
