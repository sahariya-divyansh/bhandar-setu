import {
  Facility,
  InventoryItem,
  InventoryHistoryItem,
  ForecastResponse,
  RiskSummaryResponse,
  RedistributionListResponse,
  AlertExplanationResponse,
  OfficerBriefingResponse,
  TranslateResponse,
  FederationStatusResponse,
} from './types';

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
const API_BASE = rawBaseUrl
  ? (rawBaseUrl.endsWith('/api/v1') ? rawBaseUrl : `${rawBaseUrl.replace(/\/$/, '')}/api/v1`)
  : '/api/v1';

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      }
    } catch {
      // Ignore JSON parse errors for non-JSON responses
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

export const api = {
  // Facilities
  getFacilities: (state?: string, district?: string): Promise<Facility[]> => {
    const params = new URLSearchParams();
    if (state) params.append('state', state);
    if (district) params.append('district', district);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJSON<Facility[]>(`/facilities${query}`);
  },

  getFacilityById: (facilityId: string): Promise<Facility> => {
    return fetchJSON<Facility>(`/facilities/${facilityId}`);
  },

  // Inventory
  getFacilityInventory: (facilityId: string): Promise<InventoryItem[]> => {
    return fetchJSON<InventoryItem[]>(`/inventory/${facilityId}`);
  },

  getInventoryHistory: (facilityId: string, medicineId: string, limit = 30): Promise<InventoryHistoryItem[]> => {
    return fetchJSON<InventoryHistoryItem[]>(`/inventory/${facilityId}/${medicineId}/history?limit=${limit}`);
  },

  // Forecasting & Risk Engine
  getForecast: (facilityId: string, medicineId: string): Promise<ForecastResponse> => {
    return fetchJSON<ForecastResponse>(`/forecast/${facilityId}/${medicineId}`);
  },

  getRiskSummary: (state?: string, district?: string): Promise<RiskSummaryResponse> => {
    const params = new URLSearchParams();
    if (state) params.append('state', state);
    if (district) params.append('district', district);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJSON<RiskSummaryResponse>(`/forecast/risk-summary${query}`);
  },

  // Redistribution
  getRedistributionRecommendations: (state?: string, district?: string): Promise<RedistributionListResponse> => {
    const params = new URLSearchParams();
    if (state) params.append('state', state);
    if (district) params.append('district', district);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJSON<RedistributionListResponse>(`/redistribution/recommendations${query}`);
  },

  // GenAI Insights
  getAlertExplanation: (facilityId: string, medicineId: string): Promise<AlertExplanationResponse> => {
    return fetchJSON<AlertExplanationResponse>(`/insights/alert-explanation/${facilityId}/${medicineId}`);
  },

  getOfficerBriefing: (district: string): Promise<OfficerBriefingResponse> => {
    return fetchJSON<OfficerBriefingResponse>(`/insights/officer-briefing?district=${encodeURIComponent(district)}`);
  },

  translateText: (text: string, targetLanguage = 'hi'): Promise<TranslateResponse> => {
    return fetchJSON<TranslateResponse>('/insights/translate', {
      method: 'POST',
      body: JSON.stringify({ text, target_language: targetLanguage }),
    });
  },

  // Federated Learning Status
  getFederationStatus: (): Promise<FederationStatusResponse> => {
    return fetchJSON<FederationStatusResponse>('/federation/status');
  },
};
