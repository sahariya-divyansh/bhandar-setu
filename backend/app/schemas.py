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


class RedistributionRecommendationResponse(BaseModel):
    source_facility_id: str
    source_facility_name: str
    source_district: str
    source_state: str
    source_current_stock: int
    source_surplus_available: int
    destination_facility_id: str
    destination_facility_name: str
    destination_district: str
    destination_state: str
    destination_current_stock: int
    days_of_stock_remaining: float
    medicine_id: str
    medicine_name: str
    unit: str
    suggested_quantity: int
    distance_km: float
    estimated_transit_days: int
    shortage_avoided_days: float
    urgency: str
    status: str


class RedistributionListResponse(BaseModel):
    total_recommendations: int
    items: List[RedistributionRecommendationResponse]


class AlertExplanationResponse(BaseModel):
    facility_id: str
    medicine_id: str
    explanation: str


class OfficerBriefingResponse(BaseModel):
    district: str
    briefing: str


class TranslateRequest(BaseModel):
    text: str
    target_language: str = "hi"


class TranslateResponse(BaseModel):
    target_language: str
    translated_text: str


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class FederatedStateNode(BaseModel):
    state: str
    facilities: int
    local_mae: float
    sample_count: int
    status: str
    data_depth: Optional[str] = None


class FederationStatusResponse(BaseModel):
    timestamp: str
    participating_states: List[FederatedStateNode]
    target_evaluation_node: str
    local_only_mae: float
    federated_aggregated_mae: float
    accuracy_improvement_pct: float
    privacy_boundary: str

