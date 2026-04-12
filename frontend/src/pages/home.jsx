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
import { useThreats } from '../context/ThreatContext';

const Home = () => {
  const { 
    setThreats, 
    setTotalActiveThreats, 
    setSafeRequests,
    setServerHealth,
    updateLastUpdate 
  } = useDashboardStore();

  const { threats, activeThreats } = useThreats();

  // Keep dashboard summary in sync with centralized threat data
  useEffect(() => {
    const list = threats || [];
    setThreats(list);
    setTotalActiveThreats(activeThreats.length);
    // Calculate safe requests and server health (same behavior as before)
    setSafeRequests(Math.floor(Math.random() * 10000) + 5000);
    setServerHealth(95 + Math.floor(Math.random() * 5));
    updateLastUpdate();
  }, [
    threats,
    activeThreats,
    setThreats,
    setTotalActiveThreats,
    setSafeRequests,
    setServerHealth,
    updateLastUpdate,
  ]);

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
