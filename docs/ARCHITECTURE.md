# Bhandar Setu — Architecture Specification

> **Note**: This document serves as the primary architectural blueprint for Bhandar Setu. Detailed subsystem specifications, data flow diagrams, and schema definitions will be expanded in upcoming iterations.

---

## 1. System Overview

Bhandar Setu is designed as a distributed, modular platform targeting public health supply chain optimization across India's Primary Health Centres (PHCs).

### Subsystems Overview
1. **Frontend Layer (`/frontend`)**: React + TypeScript client providing role-based interfaces for Pharmacists, PHC Medical Officers, and District Health Officers (DHO).
2. **Backend API Service (`/backend`)**: FastAPI REST microservice delivering real-time stock status, automated alert dispatch, and redistribution triggers.
3. **Machine Learning Pipeline (`/ml`)**: Time-series demand forecasting engine using clinical consumption patterns, seasonal disease trends, and lead-time analytics.
4. **Cloud Infrastructure (`/infra`)**: Infrastructure-as-code definitions for serverless deployment on Google Cloud Run and Firebase Hosting.

---

## 2. Component Diagram

```
[ Primary Health Centres ] ──(Consumption Data)──► [ FastAPI Backend ]
                                                         │
                                               ┌─────────┴─────────┐
                                               ▼                   ▼
                                      [ Time-Series ML ]   [ LLM Intelligence ]
                                               │                   │
                                               └─────────┬─────────┘
                                                         ▼
[ District Officers Dashboard ] ◄──(Redistribution)── [ Spatial Optimizer ]
```

---

## 3. Data Flow & Security

- **Authentication**: JWT-based stateless authentication with role-based access control (RBAC).
- **Data Encryption**: TLS 1.3 in transit; AES-256 for persistent inventory storage.
- **Inter-service Communication**: Asynchronous payload processing via REST and structured JSON models.

---

## 4. Pending Architectural Details

*(Detailed component breakdowns, database schemas, and spatial routing algorithms will be documented here)*
