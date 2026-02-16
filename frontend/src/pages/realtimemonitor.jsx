import React from 'react';
import RealTimeMonitoring from '../components/Dashboard/RealTimeMonitoring';
import '../styles/App.css';

const RealTimeMonitor = () => {
  return (
    <main className="main-content">
      <div className="w-full max-w-7xl">
        <h1 className="dashboard-title">Real-Time Monitor</h1>
        <div className="page-content">
        <RealTimeMonitoring />
        <div className="widget">
          <h3>Network Traffic Details</h3>
          <p>Detailed network traffic monitoring and analysis will be displayed here.</p>
        </div>
        <div className="widget">
          <h3>Active Connections</h3>
          <p>Current active network connections and their status.</p>
        </div>
      </div>
      </div>
    </main>
  );
};

export default RealTimeMonitor;
