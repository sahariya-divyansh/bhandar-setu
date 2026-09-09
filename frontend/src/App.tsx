import React from 'react';
import { Routes, Route, Link, NavLink } from 'react-router-dom';
import { Activity, ShieldAlert, Truck, Pill } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const sampleStockTrend = [
  { month: 'Jan', stockLevel: 4200, predictedDemand: 3800 },
  { month: 'Feb', stockLevel: 3900, predictedDemand: 4100 },
  { month: 'Mar', stockLevel: 3100, predictedDemand: 4600 },
  { month: 'Apr', stockLevel: 2200, predictedDemand: 4900 },
  { month: 'May', stockLevel: 1400, predictedDemand: 5200 },
  { month: 'Jun', stockLevel: 3800, predictedDemand: 4400 },
];

const Dashboard: React.FC = () => {
  return (
    <div>
      <div className="hero-card">
        <h1>Bhandar Setu (भंडार सेतु)</h1>
        <p>
          AI-Powered Medicine Stock-Out Prediction & Inter-PHC Cross-Facility Redistribution Network
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Monitored PHCs</h3>
          <div className="value">142</div>
        </div>
        <div className="stat-card">
          <h3>Predicted Stock-Outs (30d)</h3>
          <div className="value" style={{ color: 'var(--danger)' }}>18</div>
        </div>
        <div className="stat-card">
          <h3>Active Redistribution Routes</h3>
          <div className="value" style={{ color: 'var(--accent)' }}>7</div>
        </div>
        <div className="stat-card">
          <h3>Essential Medicines Monitored</h3>
          <div className="value">54</div>
        </div>
      </div>

      <div className="hero-card">
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>District Stock Trend vs Predicted Demand</h2>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sampleStockTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }} />
              <Area type="monotone" dataKey="stockLevel" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} name="Current Stock Level" />
              <Area type="monotone" dataKey="predictedDemand" stroke="#ef4444" fill="#ef4444" fillOpacity={0.1} name="Predicted Demand" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

const PlaceholderPage: React.FC<{ title: string }> = ({ title }) => (
  <div className="hero-card">
    <h1>{title}</h1>
    <p>Module under active development. Return to <Link to="/" style={{ color: 'var(--primary)' }}>Dashboard</Link>.</p>
  </div>
);

export const App: React.FC = () => {
  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="brand">
          <Pill className="h-6 w-6 text-blue-500" style={{ color: '#3b82f6' }} />
          <span>Bhandar Setu</span>
        </div>
        <ul className="nav-links">
          <li>
            <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
              Dashboard
            </NavLink>
          </li>
          <li>
            <NavLink to="/facilities" className={({ isActive }) => (isActive ? 'active' : '')}>
              PHC Facilities
            </NavLink>
          </li>
          <li>
            <NavLink to="/alerts" className={({ isActive }) => (isActive ? 'active' : '')}>
              Stock Alerts
            </NavLink>
          </li>
          <li>
            <NavLink to="/redistribution" className={({ isActive }) => (isActive ? 'active' : '')}>
              Redistribution
            </NavLink>
          </li>
        </ul>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/facilities" element={<PlaceholderPage title="PHC Facility Directory" />} />
          <Route path="/alerts" element={<PlaceholderPage title="Stock-Out Alerts & Early Warnings" />} />
          <Route path="/redistribution" element={<PlaceholderPage title="Cross-Facility Redistribution Optimizer" />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
