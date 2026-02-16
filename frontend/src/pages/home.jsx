import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import DatasetManager from '../components/Dashboard/DatasetManager';
import DatasetStatistics from '../components/Dashboard/DatasetStatistics';
import ThreatAnalyticsCard from '../components/Dashboard/ThreatAnalyticsCard';
import RiskAssessmentCard from '../components/Dashboard/RiskAssessmentCard';
import ModelInsightsRow from '../components/Dashboard/ModelInsightsRow';
import MonitoringAlertsRow from '../components/Dashboard/MonitoringAlertsRow';
import ReportsLogsCard from '../components/Dashboard/ReportsLogsCard';
import { useDashboardStore } from '../store/dashboardStore';
import { threatAPI } from '../services/api';
import { initSocket } from '../services/socket';

const Home = () => {
  const { 
    setThreats, 
    setTotalActiveThreats, 
    setSafeRequests,
    setServerHealth,
    updateLastUpdate 
  } = useDashboardStore();

  useEffect(() => {
    // Load initial threats
    const loadThreats = async () => {
      try {
        const response = await threatAPI.getThreats({ status: 'active', limit: 100 });
        const threats = response.data.threats || [];
        setThreats(threats);
        setTotalActiveThreats(threats.length);
        
        // Calculate safe requests (mock for now)
        setSafeRequests(Math.floor(Math.random() * 10000) + 5000);
        setServerHealth(95 + Math.floor(Math.random() * 5));
        updateLastUpdate();
      } catch (err) {
        // Silently handle network errors (backend not running or network issues)
        if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
          console.error('Error loading threats:', err);
        }
      }
    };

    loadThreats();

    // Set up WebSocket for real-time updates
    const socket = initSocket();
    
    socket.on('new_threat', (data) => {
      loadThreats();
      updateLastUpdate();
    });

    socket.on('threat_updated', () => {
      loadThreats();
      updateLastUpdate();
    });

    // Auto-refresh every 5 seconds
    const refreshInterval = setInterval(() => {
      loadThreats();
    }, 5000);

    return () => {
      socket.off('new_threat');
      socket.off('threat_updated');
      clearInterval(refreshInterval);
    };
  }, [setThreats, setTotalActiveThreats, setSafeRequests, setServerHealth, updateLastUpdate]);

  return (
    <main className="main-content">
      <div className="w-full max-w-7xl mx-auto space-y-6">
        {/* Page Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h1 className="dashboard-title">Security Dashboard</h1>
          <p className="text-gray-400">Real-time threat detection and monitoring</p>
        </motion.div>

        {/* Row 1: Dataset Manager */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <DatasetManager />
        </motion.div>

        {/* Row 2: Dataset Statistics + Analytics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <DatasetStatistics />
          <ThreatAnalyticsCard />
          <RiskAssessmentCard />
        </motion.div>

        {/* Row 3: Model Insights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <ModelInsightsRow />
        </motion.div>

        {/* Row 4: Monitoring & Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          <MonitoringAlertsRow />
        </motion.div>

        {/* Row 5: Reports & Logs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          <ReportsLogsCard />
        </motion.div>
      </div>
    </main>
  );
};

export default Home;
