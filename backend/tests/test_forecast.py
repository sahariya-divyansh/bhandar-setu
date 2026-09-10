"""Tests for /forecast API endpoints and risk-band classification logic."""

import pytest
from fastapi.testclient import TestClient
from ml.src.predict import calculate_risk_band


def test_calculate_risk_band_logic():
    """Test risk band threshold boundaries: Red (<3d), Orange (3-7d), Yellow (7-21d), Green (>21d)."""
    assert calculate_risk_band(0.0) == "red"
    assert calculate_risk_band(2.9) == "red"
    assert calculate_risk_band(3.0) == "orange"
    assert calculate_risk_band(7.0) == "orange"
    assert calculate_risk_band(7.1) == "yellow"
    assert calculate_risk_band(21.0) == "yellow"
    assert calculate_risk_band(21.1) == "green"
    assert calculate_risk_band(90.0) == "green"


def test_get_single_forecast(client: TestClient):
    """Test /forecast/{facility_id}/{medicine_id} endpoint returns valid schema and predictions."""
    response = client.get("/api/v1/forecast/PHC_SEHORE_01/MED_PARACETAMOL_500")
    assert response.status_code == 200
    data = response.json()

    assert data["facility_id"] == "PHC_SEHORE_01"
    assert data["medicine_id"] == "MED_PARACETAMOL_500"
    assert data["current_stock"] == 50
    assert data["avg_daily_consumption"] > 0
    assert data["days_of_stock_remaining"] <= 3.0
    assert data["risk_band"] == "red"
    assert "forecast_14d_demand" in data


def test_get_risk_summary(client: TestClient):
    """Test /forecast/risk-summary returns ranked stock-out risks across facilities."""
    response = client.get("/api/v1/forecast/risk-summary")
    assert response.status_code == 200
    data = response.json()

    assert "total_facilities_monitored" in data
    assert "high_risk_count" in data
    assert "items" in data
    assert len(data["items"]) > 0

    first_item = data["items"][0]
    assert first_item["risk_band"] in ["red", "orange"]
    assert "facility_id" in first_item


def test_get_risk_summary_filtered_by_state(client: TestClient):
    """Test /forecast/risk-summary filtered by State."""
    response = client.get("/api/v1/forecast/risk-summary?state=Madhya Pradesh")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["state"] == "Madhya Pradesh"
