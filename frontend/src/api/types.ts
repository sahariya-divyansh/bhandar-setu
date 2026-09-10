export interface Facility {
  facility_id: string;
  facility_name: string;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  facility_type: 'PHC' | 'CHC' | 'SC';
  bed_capacity: number;
}

export interface MedicineCatalogItem {
  medicine_id: string;
  medicine_name: string;
  unit: string;
  category: string;
  criticality: 'low' | 'medium' | 'high' | 'critical';
  minimum_stock_days: number;
}

export interface InventoryItem {
  facility_id: string;
  medicine_id: string;
  medicine_name: string;
  category: string;
  criticality: string;
  unit: string;
  date: string;
  closing_stock: number;
  expiry_date?: string | null;
}

export interface InventoryHistoryItem {
  id: number;
  facility_id: string;
  medicine_id: string;
  date: string;
  opening_stock: number;
  received_quantity: number;
  dispensed_quantity: number;
  damaged_quantity: number;
  closing_stock: number;
  expiry_date?: string | null;
}

export interface ForecastResponse {
  facility_id: string;
  facility_name: string;
  district: string;
  state: string;
  medicine_id: string;
  medicine_name: string;
  criticality: string;
  current_stock: number;
  avg_daily_consumption: number;
  forecast_14d_demand: number;
  days_of_stock_remaining: number;
  risk_band: 'green' | 'yellow' | 'orange' | 'red';
  last_updated?: string | null;
}

export interface RiskSummaryResponse {
  total_facilities_monitored: number;
  high_risk_count: number;
  total_items_evaluated: number;
  items: ForecastResponse[];
}

export interface RedistributionRecommendation {
  source_facility_id: string;
  source_facility_name: string;
  source_district: string;
  source_state: string;
  source_current_stock: number;
  source_surplus_available: number;
  destination_facility_id: string;
  destination_facility_name: string;
  destination_district: string;
  destination_state: string;
  destination_current_stock: number;
  days_of_stock_remaining: number;
  medicine_id: string;
  medicine_name: string;
  unit: string;
  suggested_quantity: number;
  distance_km: number;
  estimated_transit_days: number;
  shortage_avoided_days: number;
  urgency: 'critical' | 'high' | 'medium';
  status: string;
}

export interface RedistributionListResponse {
  total_recommendations: number;
  items: RedistributionRecommendation[];
}

export interface AlertExplanationResponse {
  facility_id: string;
  medicine_id: string;
  explanation: string;
}

export interface OfficerBriefingResponse {
  district: string;
  briefing: string;
}

export interface TranslateRequest {
  text: string;
  target_language: string;
}

export interface TranslateResponse {
  target_language: string;
  translated_text: string;
}

export interface FederatedStateNode {
  state: string;
  facilities: number;
  local_mae: number;
  sample_count: number;
  status: string;
  data_depth?: string | null;
}

export interface FederationStatusResponse {
  timestamp: string;
  participating_states: FederatedStateNode[];
  target_evaluation_node: string;
  local_only_mae: number;
  federated_aggregated_mae: number;
  accuracy_improvement_pct: number;
  privacy_boundary: string;
}
