import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Building2, Globe, RefreshCw, ShieldAlert, Network, Lock } from 'lucide-react';
import { api } from '../api/client';
import { ForecastResponse, RiskSummaryResponse, FederationStatusResponse } from '../api/types';
import { DashboardSkeleton } from '../components/SkeletonComponents';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // State / District filter state
  const [selectedState, setSelectedState] = useState<string>('Madhya Pradesh');
  const [selectedDistrict, setSelectedDistrict] = useState<string>('Sehore');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [debouncedQuery, setDebouncedQuery] = useState<string>('');

  // 300ms search input debouncing
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Data states
  const [riskSummary, setRiskSummary] = useState<RiskSummaryResponse | null>(null);
  const [briefingText, setBriefingText] = useState<string>('');
  const [translatedBriefing, setTranslatedBriefing] = useState<string>('');
  const [redistributionCount, setRedistributionCount] = useState<number>(0);
  const [federationStatus, setFederationStatus] = useState<FederationStatusResponse | null>(null);

  // UI state
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [loading, setLoading] = useState<boolean>(true);
  const [translating, setTranslating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load dashboard metrics
  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryRes, briefingRes, recsRes, fedRes] = await Promise.all([
        api.getRiskSummary(selectedState, selectedDistrict === 'All' ? undefined : selectedDistrict),
        api.getOfficerBriefing(selectedDistrict === 'All' ? 'Sehore' : selectedDistrict),
        api.getRedistributionRecommendations(selectedState, selectedDistrict === 'All' ? undefined : selectedDistrict),
        api.getFederationStatus().catch(() => null),
      ]);

      setRiskSummary(summaryRes);
      setBriefingText(briefingRes.briefing);
      setTranslatedBriefing(''); // Reset translated buffer on district change
      setRedistributionCount(recsRes.total_recommendations);
      if (fedRes) setFederationStatus(fedRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [selectedState, selectedDistrict]);

  // Language translation handler
  const handleLanguageToggle = async () => {
    const nextLang = language === 'en' ? 'hi' : 'en';
    setLanguage(nextLang);

    if (nextLang === 'hi' && !translatedBriefing && briefingText) {
      setTranslating(true);
      try {
        const transRes = await api.translateText(briefingText, 'hi');
        setTranslatedBriefing(transRes.translated_text);
      } catch (err) {
        console.error('Translation failed:', err);
      } finally {
        setTranslating(false);
      }
    }
  };

  // Memoized client-side list filtering
  const filteredItems = useMemo(() => {
    const items = riskSummary?.items || [];
    if (!debouncedQuery.trim()) return items;
    const query = debouncedQuery.toLowerCase();
    return items.filter((item: ForecastResponse) => (
      item.facility_name.toLowerCase().includes(query) ||
      item.medicine_name.toLowerCase().includes(query) ||
      item.facility_id.toLowerCase().includes(query)
    ));
  }, [riskSummary, debouncedQuery]);

  return (
    <div>
      {/* Top Filter & Language Controls */}
      <div className="controls-bar">
        <div className="selector-group">
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.2rem' }}>State</label>
            <select
              className="select-control"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
            >
              <option value="Madhya Pradesh">Madhya Pradesh</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.2rem' }}>District</label>
            <select
              className="select-control"
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
            >
              <option value="Sehore">Sehore District</option>
              <option value="Raisen">Raisen District</option>
              <option value="Vidisha">Vidisha District</option>
              <option value="All">All Districts (30 Facilities)</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.2rem' }}>Search Facility / Drug</label>
            <input
              type="text"
              className="input-control"
              placeholder="Search PHC or medicine..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: '220px' }}
            />
          </div>
        </div>

        <button className="lang-toggle-btn" onClick={handleLanguageToggle} disabled={translating}>
          <Globe size={16} />
          {translating ? 'Translating...' : language === 'en' ? 'Switch to Hindi (हिंदी)' : 'Switch to English'}
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="error-banner">
          <AlertTriangle size={20} />
          <span>{error}</span>
          <button className="btn-primary" onClick={loadDashboardData} style={{ marginLeft: 'auto' }}>Retry</button>
        </div>
      )}

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-title">Monitored Facilities</div>
          <div className="kpi-value">{loading ? '...' : riskSummary?.total_facilities_monitored || 0}</div>
          <div className="kpi-subtext">Active PHCs, CHCs & Sub-Centres</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">High-Risk Stock Alerts</div>
          <div className="kpi-value" style={{ color: 'var(--risk-red-text)' }}>
            {loading ? '...' : riskSummary?.high_risk_count || 0}
          </div>
          <div className="kpi-subtext">Red & Orange risk band items (&lt;7d)</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Redistribution Opportunities</div>
          <div className="kpi-value" style={{ color: 'var(--risk-green-text)' }}>
            {loading ? '...' : redistributionCount}
          </div>
          <div className="kpi-subtext">Calculated inter-PHC transfers</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Evaluated Stock Items</div>
          <div className="kpi-value">{loading ? '...' : riskSummary?.total_items_evaluated || 0}</div>
          <div className="kpi-subtext">NLEM essential medicines tracked</div>
        </div>
      </div>

      {/* DHO Executive Briefing Panel */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <ShieldAlert size={20} style={{ color: 'var(--primary)' }} />
            District Health Officer Briefing ({selectedDistrict})
          </div>
          {translating && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Translating via GenAI...</span>}
        </div>
        <div className="insight-box">
          {loading ? (
            <div className="loading-spinner">
              <RefreshCw className="animate-spin" size={18} />
              Generating executive briefing...
            </div>
          ) : (
            language === 'hi' && translatedBriefing ? translatedBriefing : briefingText
          )}
        </div>
      </div>

      {/* Federated Learning Network Panel */}
      {federationStatus && (
        <div className="panel" style={{ borderLeft: '4px solid #3b82f6' }}>
          <div className="panel-header" style={{ marginBottom: '1rem' }}>
            <div className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Network size={20} style={{ color: '#3b82f6' }} />
              Federated Collaborative Forecasting Network (FedAvg Cross-State Telemetry)
            </div>
            <span style={{ fontSize: '0.75rem', background: '#eff6ff', color: '#1d4ed8', padding: '0.2rem 0.6rem', borderRadius: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Lock size={12} /> State Data Sovereignty Enforced
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
            {federationStatus.participating_states.map((node) => (
              <div key={node.state} style={{ background: 'var(--bg-card, #f8fafc)', padding: '0.8rem 1rem', borderRadius: '8px', border: '1px solid var(--border, #e2e8f0)' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main, #0f172a)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>{node.state} Node</span>
                  <span style={{ fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '4px', background: node.state === 'Rajasthan' ? '#fef3c7' : '#dcfce7', color: node.state === 'Rajasthan' ? '#92400e' : '#166534', fontWeight: 600 }}>
                    {node.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted, #64748b)', marginTop: '0.3rem' }}>
                  Facilities: {node.facilities} | Samples: {node.sample_count.toLocaleString()}
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary, #2563eb)', marginTop: '0.2rem' }}>
                  Local MAE: {node.local_mae} units
                </div>
              </div>
            ))}
          </div>

          <div style={{ background: '#f0f9ff', padding: '0.8rem 1rem', borderRadius: '8px', border: '1px solid #bae6fd', display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ fontSize: '0.85rem', color: '#0369a1' }}>
              <strong>Evaluated Sparse Node (Rajasthan):</strong> Local-Only MAE: <strong>{federationStatus.local_only_mae} units</strong> &rarr; Global Federated MAE: <strong>{federationStatus.federated_aggregated_mae} units</strong>
            </div>
            <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#15803d', background: '#dcfce7', padding: '0.3rem 0.8rem', borderRadius: '6px' }}>
              +{federationStatus.accuracy_improvement_pct}% Forecasting Accuracy Lift
            </div>
          </div>
        </div>
      )}

      {/* Stock-Out Risk Summary Table */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <Building2 size={20} style={{ color: 'var(--primary)' }} />
            Facility Stock-Out Risk Matrix (Ranked by Shortage Urgency)
          </div>
        </div>

        {loading ? (
          <DashboardSkeleton />
        ) : filteredItems.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No stock-out risks matching criteria.
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Risk Band</th>
                  <th>Facility Name</th>
                  <th>District</th>
                  <th>Medicine Name</th>
                  <th>Criticality</th>
                  <th>Current Stock</th>
                  <th>Avg Daily Burn</th>
                  <th>14-Day Demand</th>
                  <th>Stock Days Left</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item, idx) => (
                  <tr key={`${item.facility_id}-${item.medicine_id}-${idx}`}>
                    <td>
                      <span className={`risk-pill ${item.risk_band}`}>
                        {item.risk_band}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{item.facility_name}</td>
                    <td>{item.district}</td>
                    <td>{item.medicine_name}</td>
                    <td style={{ textTransform: 'capitalize' }}>{item.criticality}</td>
                    <td style={{ fontWeight: 700 }}>{item.current_stock.toLocaleString()}</td>
                    <td>{item.avg_daily_consumption.toFixed(1)}/day</td>
                    <td>{item.forecast_14d_demand.toFixed(1)}</td>
                    <td style={{ fontWeight: 700 }}>
                      {item.days_of_stock_remaining > 90 ? '>90 days' : `${item.days_of_stock_remaining.toFixed(1)} d`}
                    </td>
                    <td>
                      <button
                        className="btn-primary"
                        onClick={() => navigate(`/facility/${item.facility_id}`)}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
