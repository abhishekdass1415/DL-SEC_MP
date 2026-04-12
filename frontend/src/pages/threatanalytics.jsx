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
        </div>
      </div>
    </main>
  );
};

export default ThreatAnalyticsPage;
