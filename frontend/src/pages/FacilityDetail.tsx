import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Globe, Pill, RefreshCw, LineChart as ChartIcon } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { api } from '../api/client';
import { Facility, InventoryItem, InventoryHistoryItem, ForecastResponse } from '../api/types';

export const FacilityDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [facility, setFacility] = useState<Facility | null>(null);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [selectedMedicineId, setSelectedMedicineId] = useState<string>('');
  
  // Forecast & Insights states
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [history, setHistory] = useState<InventoryHistoryItem[]>([]);
  const [explanation, setExplanation] = useState<string>('');
  const [translatedExplanation, setTranslatedExplanation] = useState<string>('');
  
  // UI states
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [loading, setLoading] = useState<boolean>(true);
  const [insightLoading, setInsightLoading] = useState<boolean>(false);
  const [translating, setTranslating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load facility & current inventory
  useEffect(() => {
    if (!id) return;
    const fetchFacilityData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [facData, invData] = await Promise.all([
          api.getFacilityById(id),
          api.getFacilityInventory(id),
        ]);
        setFacility(facData);
        setInventory(invData);

        if (invData.length > 0) {
          setSelectedMedicineId(invData[0].medicine_id);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load facility data.');
      } finally {
        setLoading(false);
      }
    };

    fetchFacilityData();
  }, [id]);

  // Load forecast, history & AI explanation when selected medicine changes
  useEffect(() => {
    if (!id || !selectedMedicineId) return;

    const fetchMedicineInsight = async () => {
      setInsightLoading(true);
      setTranslatedExplanation('');
      try {
        const [fcData, histData, expData] = await Promise.all([
          api.getForecast(id, selectedMedicineId),
          api.getInventoryHistory(id, selectedMedicineId, 30),
          api.getAlertExplanation(id, selectedMedicineId),
        ]);

        setForecast(fcData);
        setHistory(histData.reverse()); // Chronological order
        setExplanation(expData.explanation);
      } catch (err) {
        console.error('Error fetching medicine insight:', err);
      } finally {
        setInsightLoading(false);
      }
    };

    fetchMedicineInsight();
  }, [id, selectedMedicineId]);

  // Handle translation toggle
  const handleLanguageToggle = async () => {
    const nextLang = language === 'en' ? 'hi' : 'en';
    setLanguage(nextLang);

    if (nextLang === 'hi' && !translatedExplanation && explanation) {
      setTranslating(true);
      try {
        const res = await api.translateText(explanation, 'hi');
        setTranslatedExplanation(res.translated_text);
      } catch (err) {
        console.error('Translation failed:', err);
      } finally {
        setTranslating(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <RefreshCw className="animate-spin" size={24} />
        Loading facility dashboard...
      </div>
    );
  }

  if (error || !facility) {
    return (
      <div>
        <div className="error-banner">
          <AlertTriangle size={20} />
          <span>{error || 'Facility not found.'}</span>
        </div>
        <button className="btn-primary" onClick={() => navigate('/')}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  // Format Recharts data
  const chartData = history.map((item) => ({
    date: item.date,
    dispensed: item.dispensed_quantity,
    closing: item.closing_stock,
  }));

  return (
    <div>
      {/* Header Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <button className="btn-primary" onClick={() => navigate('/')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ArrowLeft size={16} />
          Back to Dashboard
        </button>

        <button className="lang-toggle-btn" onClick={handleLanguageToggle} disabled={translating}>
          <Globe size={16} />
          {translating ? 'Translating...' : language === 'en' ? 'Switch to Hindi (हिंदी)' : 'Switch to English'}
        </button>
      </div>

      {/* Facility Header Panel */}
      <div className="hero-card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>{facility.facility_name}</h1>
            <p>
              {facility.facility_type} Facility • {facility.district} District, {facility.state} • Bed Capacity: {facility.bed_capacity} beds
            </p>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-subtle)', marginTop: '0.5rem' }}>
              GPS Coordinates: {facility.latitude}° N, {facility.longitude}° E
            </div>
          </div>
          <span className="brand-tag">{facility.facility_type}</span>
        </div>
      </div>

      {/* Main Grid: Inventory Table + Selected Drug Analysis */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Left Column: Inventory List */}
        <div className="panel" style={{ margin: 0 }}>
          <div className="panel-header">
            <div className="panel-title">
              <Pill size={20} style={{ color: 'var(--primary)' }} />
              Current Medicine Stock
            </div>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th>Category</th>
                  <th>Stock</th>
                  <th>Unit</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map((item) => (
                  <tr
                    key={item.medicine_id}
                    style={{
                      backgroundColor: item.medicine_id === selectedMedicineId ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    }}
                  >
                    <td style={{ fontWeight: 600 }}>{item.medicine_name}</td>
                    <td>{item.category}</td>
                    <td style={{ fontWeight: 700 }}>{item.closing_stock.toLocaleString()}</td>
                    <td>{item.unit}</td>
                    <td>
                      <button
                        className="btn-primary"
                        style={{
                          fontSize: '0.75rem',
                          padding: '0.25rem 0.5rem',
                          backgroundColor: item.medicine_id === selectedMedicineId ? 'var(--primary-hover)' : 'var(--panel-border)',
                        }}
                        onClick={() => setSelectedMedicineId(item.medicine_id)}
                      >
                        {item.medicine_id === selectedMedicineId ? 'Active' : 'Analyze'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Column: Selected Medicine Insights & Chart */}
        <div className="panel" style={{ margin: 0 }}>
          <div className="panel-header">
            <div className="panel-title">
              <ChartIcon size={20} style={{ color: 'var(--primary)' }} />
              Demand & Forecast Analysis
            </div>
            {forecast && (
              <span className={`risk-pill ${forecast.risk_band}`}>
                {forecast.risk_band} Risk ({forecast.days_of_stock_remaining.toFixed(1)} Days Left)
              </span>
            )}
          </div>

          {insightLoading ? (
            <div className="loading-spinner">
              <RefreshCw className="animate-spin" size={20} />
              Analyzing consumption trends...
            </div>
          ) : forecast ? (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                <div style={{ backgroundColor: 'var(--panel-card)', padding: '0.85rem', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>CURRENT STOCK</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{forecast.current_stock.toLocaleString()}</div>
                </div>

                <div style={{ backgroundColor: 'var(--panel-card)', padding: '0.85rem', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>DAILY BURN RATE</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{forecast.avg_daily_consumption.toFixed(1)}/day</div>
                </div>

                <div style={{ backgroundColor: 'var(--panel-card)', padding: '0.85rem', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>14-DAY FORECAST</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent)' }}>{forecast.forecast_14d_demand.toFixed(1)}</div>
                </div>
              </div>

              {/* Historical Consumption Chart */}
              <div style={{ height: 200, width: '100%', marginBottom: '1.25rem' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a385b" />
                    <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1c2541', borderColor: '#2a385b', color: '#f1f5f9' }} />
                    <Area type="monotone" dataKey="dispensed" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} name="Daily Dispensed" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* GenAI Clinical Explanation Box */}
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Clinical Risk Explanation ({language === 'en' ? 'English' : 'Hindi'}):
              </div>
              <div className="insight-box" style={{ fontSize: '0.85rem' }}>
                {language === 'hi' && translatedExplanation ? translatedExplanation : explanation}
              </div>
            </div>
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Select a medicine to view demand analysis.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FacilityDetail;
