import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, RefreshCw, Truck, ArrowRight } from 'lucide-react';
import { api } from '../api/client';
import { RedistributionRecommendation } from '../api/types';
import { RedistributionSkeleton } from '../components/SkeletonComponents';

export const RedistributionPlanner: React.FC = () => {
  const [selectedDistrict, setSelectedDistrict] = useState<string>('Sehore');
  const [recommendations, setRecommendations] = useState<RedistributionRecommendation[]>([]);
  const [approvedIds, setApprovedIds] = useState<Set<string>>(new Set());

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getRedistributionRecommendations(
        'Madhya Pradesh',
        selectedDistrict === 'All' ? undefined : selectedDistrict
      );
      setRecommendations(res.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load redistribution recommendations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [selectedDistrict]);

  const handleApprove = (recKey: string) => {
    setApprovedIds((prev) => {
      const next = new Set(prev);
      next.add(recKey);
      return next;
    });
  };

  return (
    <div>
      {/* Control Bar */}
      <div className="controls-bar">
        <div className="selector-group">
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.2rem' }}>District Filter</label>
            <select
              className="select-control"
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
            >
              <option value="Sehore">Sehore District</option>
              <option value="Raisen">Raisen District</option>
              <option value="Vidisha">Vidisha District</option>
              <option value="All">All Districts</option>
            </select>
          </div>
        </div>

        <button className="btn-primary" onClick={fetchRecommendations} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <RefreshCw size={16} />
          Recalculate Routes
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <AlertTriangle size={20} />
          <span>{error}</span>
          <button className="btn-primary" onClick={fetchRecommendations} style={{ marginLeft: 'auto' }}>Retry</button>
        </div>
      )}

      {/* Header Info Banner */}
      <div className="panel" style={{ backgroundColor: 'var(--panel-card)', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Truck size={32} style={{ color: 'var(--primary)' }} />
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Cross-Facility Stock Redistribution Planner</h2>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              Haversine spatial optimization matches high-risk deficit PHCs with nearby surplus donor facilities.
              Transfers require explicit District Health Officer human approval before dispatch.
            </p>
          </div>
        </div>
      </div>

      {/* Recommendations Table */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            Active Redistribution Recommendations ({recommendations.length})
          </div>
        </div>

        {loading ? (
          <RedistributionSkeleton />
        ) : recommendations.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            No redistribution recommendations generated for current district selection.
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Urgency</th>
                  <th>Source (Donor) PHC</th>
                  <th></th>
                  <th>Destination (Deficit) PHC</th>
                  <th>Medicine</th>
                  <th>Transfer Qty</th>
                  <th>Distance</th>
                  <th>Transit Time</th>
                  <th>Shortage Avoided</th>
                  <th>Human Approval</th>
                </tr>
              </thead>
              <tbody>
                {recommendations.map((rec, idx) => {
                  const recKey = `${rec.source_facility_id}-${rec.destination_facility_id}-${rec.medicine_id}`;
                  const isApproved = approvedIds.has(recKey);

                  return (
                    <tr key={`${recKey}-${idx}`}>
                      <td>
                        <span className={`risk-pill ${rec.urgency === 'critical' ? 'red' : 'orange'}`}>
                          {rec.urgency}
                        </span>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{rec.source_facility_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
                          Surplus: {rec.source_surplus_available.toLocaleString()} {rec.unit}
                        </div>
                      </td>
                      <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                        <ArrowRight size={16} />
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{rec.destination_facility_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
                          Stock: {rec.destination_current_stock} {rec.unit} ({rec.days_of_stock_remaining.toFixed(1)}d left)
                        </div>
                      </td>
                      <td>{rec.medicine_name}</td>
                      <td style={{ fontWeight: 700, color: 'var(--accent)' }}>
                        {rec.suggested_quantity.toLocaleString()} {rec.unit}
                      </td>
                      <td>{rec.distance_km} km</td>
                      <td>~{rec.estimated_transit_days} day(s)</td>
                      <td style={{ fontWeight: 600, color: 'var(--risk-green-text)' }}>
                        +{rec.shortage_avoided_days} days
                      </td>
                      <td>
                        {isApproved ? (
                          <span className="btn-approved" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                            <CheckCircle size={14} /> Approved
                          </span>
                        ) : (
                          <button className="btn-primary" onClick={() => handleApprove(recKey)}>
                            Approve Transfer
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default RedistributionPlanner;
