import React from 'react';

export const DashboardSkeleton: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Metric Cards Skeleton */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="panel" style={{ padding: '1.25rem' }}>
            <div className="skeleton-box" style={{ width: '40%', height: '14px', marginBottom: '0.75rem' }} />
            <div className="skeleton-box" style={{ width: '70%', height: '28px', marginBottom: '0.5rem' }} />
            <div className="skeleton-box" style={{ width: '50%', height: '12px' }} />
          </div>
        ))}
      </div>

      {/* AI Briefing Skeleton */}
      <div className="panel" style={{ padding: '1.5rem' }}>
        <div className="skeleton-box" style={{ width: '30%', height: '20px', marginBottom: '1rem' }} />
        <div className="skeleton-box" style={{ width: '100%', height: '16px', marginBottom: '0.5rem' }} />
        <div className="skeleton-box" style={{ width: '90%', height: '16px', marginBottom: '0.5rem' }} />
        <div className="skeleton-box" style={{ width: '60%', height: '16px' }} />
      </div>

      {/* Table Skeleton */}
      <div className="panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div className="skeleton-box" style={{ width: '25%', height: '22px' }} />
          <div className="skeleton-box" style={{ width: '30%', height: '36px' }} />
        </div>
        {[1, 2, 3, 4, 5].map((row) => (
          <div key={row} style={{ display: 'flex', gap: '1rem', padding: '0.85rem 0', borderBottom: '1px solid var(--panel-border)' }}>
            <div className="skeleton-box" style={{ width: '25%', height: '18px' }} />
            <div className="skeleton-box" style={{ width: '20%', height: '18px' }} />
            <div className="skeleton-box" style={{ width: '15%', height: '18px' }} />
            <div className="skeleton-box" style={{ width: '15%', height: '18px' }} />
            <div className="skeleton-box" style={{ width: '15%', height: '18px' }} />
          </div>
        ))}
      </div>
    </div>
  );
};

export const FacilityDetailSkeleton: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header Skeleton */}
      <div className="panel" style={{ padding: '1.5rem' }}>
        <div className="skeleton-box" style={{ width: '35%', height: '24px', marginBottom: '0.75rem' }} />
        <div className="skeleton-box" style={{ width: '50%', height: '16px' }} />
      </div>

      {/* Grid Content Skeleton */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        {/* Left Inventory Column */}
        <div className="panel" style={{ padding: '1.5rem' }}>
          <div className="skeleton-box" style={{ width: '50%', height: '20px', marginBottom: '1rem' }} />
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton-box" style={{ width: '100%', height: '48px', marginBottom: '0.75rem' }} />
          ))}
        </div>

        {/* Right Chart & AI Insight Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="panel" style={{ padding: '1.5rem' }}>
            <div className="skeleton-box" style={{ width: '40%', height: '20px', marginBottom: '1rem' }} />
            <div className="skeleton-box" style={{ width: '100%', height: '220px' }} />
          </div>

          <div className="panel" style={{ padding: '1.5rem' }}>
            <div className="skeleton-box" style={{ width: '30%', height: '20px', marginBottom: '1rem' }} />
            <div className="skeleton-box" style={{ width: '100%', height: '16px', marginBottom: '0.5rem' }} />
            <div className="skeleton-box" style={{ width: '80%', height: '16px' }} />
          </div>
        </div>
      </div>
    </div>
  );
};

export const RedistributionSkeleton: React.FC = () => {
  return (
    <div className="panel" style={{ padding: '1.5rem' }}>
      <div className="skeleton-box" style={{ width: '30%', height: '22px', marginBottom: '1.5rem' }} />
      {[1, 2, 3, 4].map((row) => (
        <div key={row} style={{ display: 'flex', gap: '1rem', padding: '1rem 0', borderBottom: '1px solid var(--panel-border)' }}>
          <div className="skeleton-box" style={{ width: '25%', height: '20px' }} />
          <div className="skeleton-box" style={{ width: '25%', height: '20px' }} />
          <div className="skeleton-box" style={{ width: '20%', height: '20px' }} />
          <div className="skeleton-box" style={{ width: '15%', height: '20px' }} />
          <div className="skeleton-box" style={{ width: '10%', height: '20px' }} />
        </div>
      ))}
    </div>
  );
};
