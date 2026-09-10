# Bhandar Setu (भंडार सेतु)

> **Mission**: An intelligent inventory intelligence and cross-facility redistribution platform engineered to eliminate medicine stock-outs across India's Primary Health Centre (PHC) network.

---

## 📌 Problem Statement

India's rural public healthcare network — comprising over 30,000 Primary Health Centres (PHCs), Community Health Centres (CHCs), and Sub-Centres — frequently experiences critical stock-outs of essential, life-saving medicines due to unexpected demand surges, seasonal disease outbreaks (e.g., monsoon fever and respiratory spikes), and rigid top-down supply chains. Concurrently, nearby facilities often retain surplus stock that expires unused due to a lack of inter-facility visibility.

**Bhandar Setu** bridges this gap by combining time-series demand forecasting with Haversine spatial optimization and Generative AI clinical insights. The platform predicts facility-level stock-outs 30–60 days in advance and automatically generates optimal inter-facility redistribution recommendations, ensuring equitable medicine distribution and minimizing wastage across District Health Officer (DHO) administrative zones.

---

## 📸 Screenshots

| Executive Dashboard | Facility Detail & Forecast | Redistribution Planner |
| :---: | :---: | :---: |
| ![Dashboard Screenshot](docs/screenshots/dashboard.png) | ![Facility Detail Screenshot](docs/screenshots/facility_detail.png) | ![Redistribution Planner Screenshot](docs/screenshots/redistribution_planner.png) |

---

## 🏗️ Architecture Overview

For full technical specifications, database schemas (ERD), and privacy engineering details, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

```
┌────────────────────────────────────────────────────────────────────────┐
│                        React 18 + TypeScript SPA                       │
│              (Vite, Recharts, GIS Risk Matrix, Multilingual UI)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST API (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         FastAPI API Gateway                            │
│                 (Python 3.11+ / Pydantic v2 / SQLAlchemy)              │
└─────────┬─────────────────────────┬──────────────────────────┬─────────┘
          │                         │                          │
          ▼                         ▼                          ▼
┌──────────────────┐      ┌──────────────────┐       ┌──────────────────┐
│   ML Engine      │      │ GenAI Engine     │       │ Federated Nodes  │
│ Demand Forecast  │      │ Gemini 1.5 Pro   │       │ FedAvg Simulator │
│  (RandomForest)  │      │ Action Briefings │       │ State Data Privacy│
└──────────────────┘      └──────────────────┘       └──────────────────┘
```

---

## 🧰 Tech Stack

| Category | Technologies Used | Description |
| :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Recharts, Lucide Icons | Responsive dashboard with risk heatmaps, burn-rate charts, and bilingual support |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, SQLite | High-throughput async REST API service with strict static typing |
| **ML Engine** | Scikit-Learn (RandomForestRegressor), Pandas, NumPy | 14-day rolling demand forecaster with seasonal & epidemiological features |
| **AI Layer** | Google Generative AI (Gemini 1.5 Pro) | Generates executive DHO district briefings and automated risk explanations |
| **Infra** | Docker, Google Cloud Run, Firebase Hosting, Makefile | Microservice containerization and serverless infrastructure hosting |

---

## 📊 Key Results & Empirical Performance

### 1. Demand Forecasting Accuracy
Evaluated on a held-out 60-day temporal test split across Primary Health Centres:
- **Baseline Model (Weighted Moving Average + Seasonal Adjustment)**: `13.94 units` MAE
- **Machine Learning Model (RandomForestRegressor)**: `7.72 units` MAE
- **Performance Lift**: **`+44.62%` improvement in forecasting accuracy**

### 2. Federated Learning Cross-State Simulation (FedAvg)
Evaluated on a newly onboarded state node (Rajasthan) with sparse historical telemetry:
- **Local-Only Model (Sparse Data)**: `13.82 units` MAE
- **Global Federated Aggregated Model (FedAvg)**: `8.57 units` MAE
- **Collaborative Accuracy Gain**: **`+38.00%` MAE reduction** achieved with **zero raw patient or inventory telemetry crossing state boundaries**.

---

## 🔬 Data Calibration & Realism Note

All inventory balances, patient visit footfalls, disease surveillance statistics, and supply chain lead times in Bhandar Setu are **synthetically generated using realistic epidemiological models calibrated to India's National List of Essential Medicines (NLEM)**. The dataset incorporates authentic monsoon/winter disease surge multipliers (fever, diarrhoea, respiratory cases) and real geographic coordinates across Madhya Pradesh, Chhattisgarh, and Rajasthan.

---

## 🚀 Setup & Local Execution

### Quick Start (Under 5 Commands via Makefile)

```bash
# 1. Complete environment setup, database seeding, and ML model training
make setup

# 2. Launch backend API service and frontend application in parallel
make run
```

### Manual Installation & Running

#### 1. Backend & ML Engine Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Seed multi-state SQLite database (65 facilities, 400K+ inventory rows)
python ../ml/src/generate_multistate_data.py

# Train demand forecaster & federated learning simulation
python ../ml/src/train.py
python ../ml/src/federated_train.py

# Run FastAPI backend service
uvicorn app.main:app --reload --port 8000
```
Interactive OpenAPI documentation will be live at [`http://localhost:8000/docs`](http://localhost:8000/docs).

#### 2. Running Backend Pytest Suite
```bash
cd backend
python -m pytest
```

#### 3. Frontend Web Application Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend user interface will be live at [`http://localhost:5173`](http://localhost:5173).

---

## 📚 API Documentation & Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/facilities` | `GET` | List facilities filtered by State and District |
| `/api/v1/forecast/risk-summary` | `GET` | Retrieve district-wide facility-medicine stock-out risk matrix |
| `/api/v1/forecast/{facility_id}/{medicine_id}` | `GET` | Detailed 14-day demand prediction & risk band |
| `/api/v1/redistribution/recommendations` | `GET` | Spatial Haversine inter-facility stock transfer recommendations |
| `/api/v1/federation/status` | `GET` | Telemetry status of cross-state federated learning network |
| `/api/v1/insights/officer-briefing` | `GET` | GenAI executive summary for District Health Officers |
| `/api/v1/insights/translate` | `POST` | Bilingual English-to-Hindi AI translation engine |

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
