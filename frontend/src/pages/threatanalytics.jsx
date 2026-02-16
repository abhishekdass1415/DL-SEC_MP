import React from 'react';
import ThreatAnalytics from '../components/Dashboard/ThreatAnalytics';
import '../styles/App.css';

const ThreatAnalyticsPage = () => {
  return (
    <main className="main-content">
      <div className="w-full max-w-7xl">
        <h1 className="dashboard-title">Threat Analytics</h1>
        <div className="page-content">
        <ThreatAnalytics />
        <div className="widget">
          <h3>Threat Detection History</h3>
          <p>Comprehensive threat detection history and trends.</p>
        </div>
        <div className="widget">
          <h3>Top Threat Sources</h3>
          <p>Analysis of top threat sources and their patterns.</p>
        </div>
      </div>
      </div>
    </main>
  );
};

export default ThreatAnalyticsPage;
