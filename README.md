# Bhandar Setu (भंडार सेतु)

> **Mission**: An intelligent inventory intelligence and cross-facility redistribution platform engineered to eliminate medicine stock-outs across India's Primary Health Centre (PHC) network.

---

## 📌 Problem Statement Summary

India's rural healthcare backbone — comprising over 30,000 Primary Health Centres (PHCs) and Community Health Centres (CHCs) — frequently experiences critical stock-outs of essential, life-saving medicines due to demand surges, seasonal disease outbreaks, and rigid top-down supply allocation chains. Concurrently, neighboring healthcare facilities often retain surplus stock that expires unused.

**Bhandar Setu** bridges this gap by combining time-series demand forecasting with dynamic spatial optimization. The platform predicts facility-level stock-outs 30–60 days in advance and automatically calculates optimal inter-facility redistribution routes, ensuring equitable medicine distribution and minimizing wastage across District Health Officer (DHO) administrative zones.

---

## 🏗️ Architecture Overview

Bhandar Setu is structured as a high-performance monorepo designed for scale, resilience, and rapid deployment:

```
                          ┌─────────────────────────────┐
                          │   React + TypeScript SPA    │
                          │     (Vite + Recharts)       │
                          └──────────────┬──────────────┘
                                         │ REST / JSON
                                         ▼
                          ┌─────────────────────────────┐
                          │    FastAPI API Gateway      │
                          │   (Python 3.11+ / Pydantic) │
                          └──────┬──────────────┬───────┘
                                 │              │
                    ┌────────────┘              └────────────┐
                    ▼                                        ▼
    ┌─────────────────────────────┐            ┌─────────────────────────────┐
    │     ML Forecasting Engine   │            │   LLM Intelligence Core     │
    │  (Scikit-Learn / Pandas)    │            │  (Google Generative AI)     │
    └─────────────────────────────┘            └─────────────────────────────┘
```

- **Frontend (`/frontend`)**: React 18 SPA built with TypeScript and Vite. Uses `react-router-dom` for client-side navigation and `recharts` for dynamic stock projections and GIS facility mapping visuals.
- **Backend (`/backend`)**: High-throughput FastAPI application exposing REST APIs for inventory management, alert generation, and redistribution calculation.
- **ML Engine (`/ml`)**: Predictive pipelines for facility-level consumption forecasting, lead-time estimation, and linear programming algorithms for optimal stock transfers.
- **Infrastructure (`/infra`)**: Containerized configurations for Google Cloud Run (Backend API) and Firebase Hosting (Frontend SPA).
- **Documentation (`/docs`)**: Technical specifications, API reference schema, and architectural decision records.

---

## 🧰 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite | User interface for PHC pharmacists & District Health Officers |
| **Data Visualization** | Recharts, Lucide Icons | Stock level charts, burn-rate visualization & alert counters |
| **Backend API** | Python 3.11+, FastAPI, Uvicorn | Asynchronous RESTful backend service |
| **Validation & Settings** | Pydantic v2, Python-Dotenv | Schema validation and environment management |
| **AI & Forecasting** | Google Generative AI, Scikit-Learn | Clinical insights generation & time-series forecasting |
| **Data Processing** | Pandas, NumPy | Multi-facility inventory dataset ingestion & feature engineering |
| **Cloud & Deployment**| Cloud Run, Firebase, Docker | Serverless container hosting & global CDN deployment |

---

## 🚀 Setup & Local Development

### Prerequisites
- **Node.js**: v18.x or higher
- **Python**: v3.11 or higher
- **Git**

### 1. Repository Setup
```bash
git clone https://github.com/sahariya-divyansh/bhandar-setu.git
cd bhandar-setu
```

### 2. Backend Service Setup
```bash
cd backend
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Backend API interactive documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Web Application Setup
```bash
cd ../frontend
npm install
npm run dev
```
Frontend development server will launch at `http://localhost:5173`.

### 4. ML Pipeline Setup
```bash
cd ../ml
pip install -r requirements.txt
python src/predict.py --help
```

---

## 📈 Project Status

- [x] Monorepo scaffold & foundational architecture definition
- [ ] Core REST API endpoint implementation & Pydantic models
- [ ] Time-series demand forecasting model development
- [ ] District Health Officer (DHO) dashboard & reallocation interface
- [ ] Deployment integration on Google Cloud Run & Firebase Hosting

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
