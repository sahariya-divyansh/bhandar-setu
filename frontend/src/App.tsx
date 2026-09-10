import React from 'react';
import { Routes, Route, NavLink, Link } from 'react-router-dom';
import { LayoutDashboard, Truck, Pill } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import FacilityDetail from './pages/FacilityDetail';
import RedistributionPlanner from './pages/RedistributionPlanner';

export const App: React.FC = () => {
  return (
    <div className="app-shell">
      {/* Top Enterprise Navigation Header */}
      <header className="top-navbar">
        <Link to="/" style={{ textDecoration: 'none' }}>
          <div className="brand-title">
            <Pill size={24} style={{ color: '#3b82f6' }} />
            <span>Bhandar Setu</span>
            <span className="brand-tag">v0.1 PHC Logistics</span>
          </div>
        </Link>

        <nav>
          <ul className="nav-menu">
            <li>
              <NavLink to="/" end className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}>
                <LayoutDashboard size={18} />
                Risk Matrix Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink to="/redistribution" className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}>
                <Truck size={18} />
                Redistribution Planner
              </NavLink>
            </li>
          </ul>
        </nav>
      </header>

      {/* Main App Page View */}
      <main className="page-container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/facility/:id" element={<FacilityDetail />} />
          <Route path="/redistribution" element={<RedistributionPlanner />} />
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
