"""Tests for cross-facility redistribution recommendation service and endpoint."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.redistribution import recommend_redistributions


def test_redistribution_donor_minimum_stock_buffer(test_db: Session):
    """Test recommendation engine NEVER suggests a transfer quantity that causes donor stock to drop below minimum_stock_days buffer."""
    recommendations = recommend_redistributions(test_db)
    assert len(recommendations) > 0

    for rec in recommendations:
        donor_stock = rec["source_current_stock"]
        suggested_qty = rec["suggested_quantity"]
        surplus_available = rec["source_surplus_available"]

        # 1. Suggested transfer quantity must never exceed calculated surplus
        assert suggested_qty <= surplus_available

        # 2. Donor post-transfer stock must remain at or above minimum safety stock buffer
        remaining_donor_stock = donor_stock - suggested_qty
        
        # In test_db: PHC Ashta (donor) has 3000 stock, avg daily burn = 15, min_days = 30
        # Required buffer = 30 * 15 = 450 tablets. Remaining stock must be >= 450.
        assert remaining_donor_stock >= 450


def test_redistribution_api_endpoint(client: TestClient):
    """Test /redistribution/recommendations endpoint returns valid recommendation list."""
    response = client.get("/api/v1/redistribution/recommendations")
    assert response.status_code == 200
    data = response.json()

    assert "total_recommendations" in data
    assert "items" in data
    assert data["total_recommendations"] == len(data["items"])
    assert len(data["items"]) > 0

    first_rec = data["items"][0]
    assert first_rec["source_facility_id"] == "PHC_ASHTA_01"
    assert first_rec["destination_facility_id"] == "PHC_SEHORE_01"
    assert first_rec["suggested_quantity"] > 0
    assert first_rec["distance_km"] > 0
    assert first_rec["urgency"] in ["critical", "high"]
