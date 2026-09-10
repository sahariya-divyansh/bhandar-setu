"""Tests for /facilities API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_get_all_facilities(client: TestClient):
    """Test retrieving all facilities without filters."""
    response = client.get("/api/v1/facilities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    facility_ids = [f["facility_id"] for f in data]
    assert "PHC_SEHORE_01" in facility_ids
    assert "PHC_RAIPUR_01" in facility_ids


def test_get_facilities_filtered_by_state(client: TestClient):
    """Test filtering facilities by State."""
    response = client.get("/api/v1/facilities?state=Madhya Pradesh")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for fac in data:
        assert fac["state"] == "Madhya Pradesh"

    response_cg = client.get("/api/v1/facilities?state=Chhattisgarh")
    assert response_cg.status_code == 200
    data_cg = response_cg.json()
    assert len(data_cg) == 1
    assert data_cg[0]["facility_id"] == "PHC_RAIPUR_01"


def test_get_facilities_filtered_by_district(client: TestClient):
    """Test filtering facilities by District."""
    response = client.get("/api/v1/facilities?district=Sehore")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for fac in data:
        assert fac["district"] == "Sehore"


def test_get_facility_by_id(client: TestClient):
    """Test retrieving a single facility by ID."""
    response = client.get("/api/v1/facilities/PHC_SEHORE_01")
    assert response.status_code == 200
    data = response.json()
    assert data["facility_id"] == "PHC_SEHORE_01"
    assert data["facility_name"] == "PHC Sehore Town"
    assert data["bed_capacity"] == 6


def test_get_facility_not_found(client: TestClient):
    """Test 404 response for non-existent facility ID."""
    response = client.get("/api/v1/facilities/NON_EXISTENT_PHC")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
