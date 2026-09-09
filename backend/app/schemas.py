"""Pydantic schemas for Bhandar Setu API responses with strict static typing."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class FacilityResponse(BaseModel):
    facility_id: str
    facility_name: str
    state: str
    district: str
    latitude: float
    longitude: float
    facility_type: str
    bed_capacity: int

    model_config = ConfigDict(from_attributes=True)


class MedicineCatalogResponse(BaseModel):
    medicine_id: str
    medicine_name: str
    unit: str
    category: str
    criticality: str
    minimum_stock_days: int

    model_config = ConfigDict(from_attributes=True)


class InventoryItemResponse(BaseModel):
    facility_id: str
    medicine_id: str
    medicine_name: str
    category: str
    criticality: str
    unit: str
    date: str
    closing_stock: int
    expiry_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InventoryHistoryResponse(BaseModel):
    id: int
    facility_id: str
    medicine_id: str
    date: str
    opening_stock: int
    received_quantity: int
    dispensed_quantity: int
    damaged_quantity: int
    closing_stock: int
    expiry_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ForecastResponse(BaseModel):
    facility_id: str
    facility_name: str
    district: str
    state: str
    medicine_id: str
    medicine_name: str
    criticality: str
    current_stock: int
    avg_daily_consumption: float
    forecast_14d_demand: float
    days_of_stock_remaining: float
    risk_band: str  # green, yellow, orange, red
    last_updated: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RiskSummaryResponse(BaseModel):
    total_facilities_monitored: int
    high_risk_count: int
    total_items_evaluated: int
    items: List[ForecastResponse]


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
