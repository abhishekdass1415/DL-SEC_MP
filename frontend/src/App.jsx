import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import Home from './pages/home';
import RealTimeMonitor from './pages/realtimemonitor';
import ThreatAnalyticsPage from './pages/threatanalytics';
import Logs from './pages/logs';
import Settings from './pages/settings';
import ModelInsightsPage from './pages/modelinsights';
import DatasetPage from './pages/dataset';
import './styles/App.css';

const Placeholder = ({ title }) => (
  <main className="main-content">
    <div className="w-full max-w-7xl">
      <h1 className="dashboard-title">{title}</h1>
      <div className="widget"><p style={{ color: '#b0b0b0' }}>Coming soon.</p></div>
    </div>
  </main>
);

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <div className="min-h-screen bg-dark-bg">
        <Header />
        <div className="flex">
          <Sidebar />
          <div className="flex-1 ml-60">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Home />} />
              <Route path="/monitor" element={<RealTimeMonitor />} />
              <Route path="/analytics" element={<ThreatAnalyticsPage />} />
              <Route path="/insights" element={<ModelInsightsPage />} />
              <Route path="/logs" element={<Logs />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/dataset" element={<DatasetPage />} />
              <Route path="/reports" element={<Placeholder title="Reports" />} />
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;


