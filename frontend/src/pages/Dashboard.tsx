import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Building2, Globe, RefreshCw, ShieldAlert } from 'lucide-react';
import { api } from '../api/client';
import { ForecastResponse, RiskSummaryResponse } from '../api/types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // State / District filter state
  const [selectedState, setSelectedState] = useState<string>('Madhya Pradesh');
  const [selectedDistrict, setSelectedDistrict] = useState<string>('Sehore');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Data states
  const [riskSummary, setRiskSummary] = useState<RiskSummaryResponse | null>(null);
  const [briefingText, setBriefingText] = useState<string>('');
  const [translatedBriefing, setTranslatedBriefing] = useState<string>('');
  const [redistributionCount, setRedistributionCount] = useState<number>(0);

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
      const [summaryRes, briefingRes, recsRes] = await Promise.all([
        api.getRiskSummary(selectedState, selectedDistrict === 'All' ? undefined : selectedDistrict),
        api.getOfficerBriefing(selectedDistrict === 'All' ? 'Sehore' : selectedDistrict),
        api.getRedistributionRecommendations(selectedState, selectedDistrict === 'All' ? undefined : selectedDistrict),
      ]);

      setRiskSummary(summaryRes);
      setBriefingText(briefingRes.briefing);
      setTranslatedBriefing(''); // Reset translated buffer on district change
      setRedistributionCount(recsRes.total_recommendations);
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

  // Filtered items
  const filteredItems = (riskSummary?.items || []).filter((item: ForecastResponse) => {
    const query = searchQuery.toLowerCase();
    return (
      item.facility_name.toLowerCase().includes(query) ||
      item.medicine_name.toLowerCase().includes(query) ||
      item.facility_id.toLowerCase().includes(query)
    );
  });

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

      {/* Stock-Out Risk Summary Table */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <Building2 size={20} style={{ color: 'var(--primary)' }} />
            Facility Stock-Out Risk Matrix (Ranked by Shortage Urgency)
          </div>
        </div>

        {loading ? (
          <div className="loading-spinner">
            <RefreshCw className="animate-spin" size={20} />
            Fetching stock-out risk matrix...
          </div>
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
