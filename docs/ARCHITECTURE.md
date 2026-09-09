# Bhandar Setu — Architecture Specification

> **Note**: This document serves as the primary architectural blueprint for Bhandar Setu. Subsystem specifications, data flow diagrams, and database schemas are detailed below.

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

## 4. Data Model & Schema Specification

The core relational database model powers inventory tracking, disease surveillance, workforce availability, and inter-facility drug transfers.

### Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    FACILITIES ||--o{ MEDICINE_INVENTORY : "tracks daily stock"
    MEDICINE_CATALOG ||--o{ MEDICINE_INVENTORY : "catalog item"
    FACILITIES ||--o{ PATIENT_VISITS : "logs surveillance"
    FACILITIES ||--o{ STAFF_ATTENDANCE : "records staffing"
    FACILITIES ||--o{ DELIVERIES : "sends/receives consignment"
    MEDICINE_CATALOG ||--o{ DELIVERIES : "shipped item"

    FACILITIES {
        string facility_id PK
        string facility_name
        string state
        string district
        float latitude
        float longitude
        string facility_type
        int bed_capacity
    }

    MEDICINE_CATALOG {
        string medicine_id PK
        string medicine_name
        string unit
        string category
        string criticality
        int minimum_stock_days
    }

    MEDICINE_INVENTORY {
        int id PK
        string facility_id FK
        string medicine_id FK
        date date
        int opening_stock
        int received_quantity
        int dispensed_quantity
        int damaged_quantity
        int closing_stock
        date expiry_date
    }

    PATIENT_VISITS {
        int id PK
        string facility_id FK
        date date
        int total_visits
        int fever_cases
        int diarrhoea_cases
        int respiratory_cases
        int maternal_cases
    }

    STAFF_ATTENDANCE {
        int id PK
        string facility_id FK
        date date
        string staff_role
        int scheduled_count
        int present_count
    }

    DELIVERIES {
        string delivery_id PK
        string source_facility_id FK
        string destination_facility_id FK
        string medicine_id FK
        int quantity
        date dispatch_date
        date expected_arrival_date
        string status
    }
```

### Table Definitions

1. **`facilities`**: Master directory of Primary Health Centres (PHC), Community Health Centres (CHC), and Sub-Centres (SC) across districts.
2. **`medicine_catalog`**: NLEM-compliant essential drug catalog detailing dosage units, criticality tiers, and safety stock thresholds.
3. **`medicine_inventory`**: High-frequency daily balance ledger tracking stock movements, dispensations, receipts, and expirations.
4. **`patient_visits`**: Clinical epidemiological surveillance logs recording disease-specific outpatient surges (diarrhoea, respiratory, fever).
5. **`staff_attendance`**: Healthcare worker staffing telemetry monitoring clinical capacity and operational status.
6. **`deliveries`**: Multi-echelon stock dispatch tracking for inter-facility redistribution and district warehouse supply pipelines.
