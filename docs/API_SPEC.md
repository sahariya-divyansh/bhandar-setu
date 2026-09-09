# Bhandar Setu — OpenAPI & Endpoint Specifications

Interactive Swagger UI documentation is available at `http://localhost:8000/docs` when running the backend service locally.

---

## Endpoint Summary Table

| Method | Endpoint | Description | Query / Body Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service status health check | None |
| `GET` | `/api/v1/facilities` | List healthcare facilities | `state` (optional), `district` (optional) |
| `GET` | `/api/v1/facilities/{facility_id}` | Fetch facility metadata | None |
| `GET` | `/api/v1/inventory/{facility_id}` | Current medicine inventory for a facility | None |
| `GET` | `/api/v1/inventory/{facility_id}/{medicine_id}/history` | Historical daily inventory ledger | `limit` (default: 30) |
| `GET` | `/api/v1/forecast/{facility_id}/{medicine_id}` | 14-day demand forecast & risk band | None |
| `GET` | `/api/v1/forecast/risk-summary` | Ranked district/state stock-out risk report | `state` (optional), `district` (optional) |
| `GET` | `/api/v1/redistribution/recommendations` | Cross-facility transfer recommendations | `state` (optional), `district` (optional) |
| `GET` | `/api/v1/insights/alert-explanation/{facility_id}/{medicine_id}` | GenAI plain-language risk explanation | None |
| `GET` | `/api/v1/insights/officer-briefing` | DHO executive district briefing | `district` (required) |
| `POST`| `/api/v1/insights/translate` | Multi-lingual translation of alert text | Body: `{ "text": "...", "target_language": "hi" }` |

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

### 2. `GET /api/v1/redistribution/recommendations`
**Query Parameters:** `state` *(optional)*, `district` *(optional)*

**Response (200 OK):**
```json
{
  "total_recommendations": 1,
  "items": [
    {
      "source_facility_id": "FAC_MP_SEH_001",
      "source_facility_name": "Sehore District CHC",
      "source_district": "Sehore",
      "source_state": "Madhya Pradesh",
      "source_current_stock": 1022,
      "source_surplus_available": 500,
      "destination_facility_id": "FAC_MP_SEH_002",
      "destination_facility_name": "Shyampur CHC",
      "destination_district": "Sehore",
      "destination_state": "Madhya Pradesh",
      "destination_current_stock": 0,
      "days_of_stock_remaining": 0.0,
      "medicine_id": "MED_ORS_SACHET",
      "medicine_name": "Oral Rehydration Salts (ORS)",
      "unit": "Sachets",
      "suggested_quantity": 500,
      "distance_km": 13.8,
      "estimated_transit_days": 1,
      "shortage_avoided_days": 12.1,
      "urgency": "critical",
      "status": "Recommendation Generated"
    }
  ]
}
```

---

### 3. `GET /api/v1/insights/alert-explanation/{facility_id}/{medicine_id}`
**Response (200 OK):**
```json
{
  "facility_id": "FAC_MP_SEH_002",
  "medicine_id": "MED_ORS_SACHET",
  "explanation": "• [RED RISK ALERT]: Shyampur CHC has currently 0 units of Oral Rehydration Salts (ORS) remaining, which provides only 0.0 days of coverage based on a 30-day average daily burn rate of 41.5 units/day.\n• Demand Surge Projection: The ML forecasting engine projects a 14-day cumulative demand of 705.4 units. Because this drug is categorized as CRITICAL criticality, stock depletion poses an immediate clinical care risk.\n• Operational Impact: Immediate replenishment or inter-facility cross-redistribution is required within 1 day(s) to prevent complete stock-out."
}
```

---

### 4. `GET /api/v1/insights/officer-briefing`
**Query Parameters:** `district` *(required, e.g. "Sehore")*

**Response (200 OK):**
```json
{
  "district": "Sehore",
  "briefing": "Executive Briefing for District Health Officer (Sehore):\n\n1. Risk Overview: A total of 18 critical stock-out alerts (Red/Orange risk bands) were identified across 150 evaluated facility-medicine pairs in Sehore.\n\n2. Urgent Clinical Stock-Outs: High-risk shortages are concentrated in essential medicines including Oral Rehydration Salts (ORS), Zinc Sulphate, and Metronidazole during active demand surge periods.\n\n3. Recommended Interventions: 10 cross-facility redistribution opportunities have been calculated. The primary recommended action is transferring 500 units of Oral Rehydration Salts (ORS) from Sehore District CHC to Shyampur CHC (13.8 km distance, ~1 day transit time), avoiding 12.1 days of shortage."
}
```

---

### 5. `POST /api/v1/insights/translate`
**Request Body:**
```json
{
  "text": "Critical Stock-out alert for ORS Sachets at Shyampur CHC. 0 days of stock remaining.",
  "target_language": "hi"
}
```

**Response (200 OK):**
```json
{
  "target_language": "hi",
  "translated_text": "[अनुवादित चेतावनी - हिंदी]:\nस्वास्थ्य केंद्र दवा स्टॉक चेतावनी: भंडार की कमी पाई गई है। कृपया तुरंत स्टॉक पुनर्वितरण एवं आपूर्ति स्थिति की जांच करें。\n\nमूल संदेश: Critical Stock-out alert for ORS Sachets at Shyampur CHC. 0 days of stock remaining."
}
```
