# Bhandar Setu — OpenAPI & Endpoint Specifications

Interactive Swagger UI documentation is available at `http://localhost:8000/docs` when running the backend service locally.

---

## Endpoint Summary Table

| Method | Endpoint | Description | Query Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service status health check | None |
| `GET` | `/api/v1/facilities` | List healthcare facilities | `state` (optional), `district` (optional) |
| `GET` | `/api/v1/facilities/{facility_id}` | Fetch facility metadata | None |
| `GET` | `/api/v1/inventory/{facility_id}` | Get current medicine inventory for a facility | None |
| `GET` | `/api/v1/inventory/{facility_id}/{medicine_id}/history` | Historical daily inventory ledger | `limit` (default: 30) |
| `GET` | `/api/v1/forecast/{facility_id}/{medicine_id}` | 14-day demand forecast & risk band for pair | None |
| `GET` | `/api/v1/forecast/risk-summary` | Ranked district/state stock-out risk report | `state` (optional), `district` (optional) |

---

## Detailed Endpoint Schemas & Responses

### 1. `GET /health`
**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Bhandar Setu API",
  "version": "0.1.0",
  "environment": "development"
}
```

---

### 2. `GET /api/v1/facilities`
**Query Parameters:**
- `state` *(string, optional)*: e.g., `"Madhya Pradesh"`
- `district` *(string, optional)*: e.g., `"Sehore"`

**Response (200 OK):**
```json
[
  {
    "facility_id": "FAC_MP_SEH_001",
    "facility_name": "Sehore District CHC",
    "state": "Madhya Pradesh",
    "district": "Sehore",
    "latitude": 23.2032,
    "longitude": 77.0844,
    "facility_type": "CHC",
    "bed_capacity": 30
  }
]
```

---

### 3. `GET /api/v1/inventory/{facility_id}`
**Response (200 OK):**
```json
[
  {
    "facility_id": "FAC_MP_SEH_001",
    "medicine_id": "MED_AMOXICILLIN_500",
    "medicine_name": "Amoxicillin 500mg Capsules",
    "category": "Antibiotic",
    "criticality": "high",
    "unit": "Capsules",
    "date": "2026-08-22",
    "closing_stock": 1488,
    "expiry_date": "2027-04-12"
  }
]
```

---

### 4. `GET /api/v1/forecast/{facility_id}/{medicine_id}`
**Response (200 OK):**
```json
{
  "facility_id": "FAC_MP_SEH_002",
  "facility_name": "Shyampur CHC",
  "district": "Sehore",
  "state": "Madhya Pradesh",
  "medicine_id": "MED_ORS_SACHET",
  "medicine_name": "Oral Rehydration Salts (ORS)",
  "criticality": "critical",
  "current_stock": 0,
  "avg_daily_consumption": 41.47,
  "forecast_14d_demand": 705.4,
  "days_of_stock_remaining": 0.0,
  "risk_band": "red",
  "last_updated": "2026-08-22"
}
```

---

### 5. `GET /api/v1/forecast/risk-summary`
**Query Parameters:**
- `state` *(string, optional)*
- `district` *(string, optional)*

**Response (200 OK):**
```json
{
  "total_facilities_monitored": 10,
  "high_risk_count": 18,
  "total_items_evaluated": 150,
  "items": [
    {
      "facility_id": "FAC_MP_SEH_002",
      "facility_name": "Shyampur CHC",
      "district": "Sehore",
      "state": "Madhya Pradesh",
      "medicine_id": "MED_ORS_SACHET",
      "medicine_name": "Oral Rehydration Salts (ORS)",
      "criticality": "critical",
      "current_stock": 0,
      "avg_daily_consumption": 41.47,
      "forecast_14d_demand": 705.4,
      "days_of_stock_remaining": 0.0,
      "risk_band": "red",
      "last_updated": "2026-08-22"
    }
  ]
}
```
