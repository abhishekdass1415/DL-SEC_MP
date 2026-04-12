import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, AlertCircle, Globe, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import RealTimeMonitoring from './RealTimeMonitoring';
import AlertCenter from './AlertCenter';
import { useThreats } from '../../context/ThreatContext';

const MonitoringAlertsRow = () => {
  const navigate = useNavigate();
  const [riskyAPIs, setRiskyAPIs] = useState([]);
  const { threats } = useThreats();

  useEffect(() => {
    // Group by API endpoint (destination_ip) based on global threats list
    const apiMap = threats.reduce((acc, threat) => {
      const api = threat.destination_ip || 'Unknown';
      if (!acc[api]) {
        acc[api] = {
          endpoint: api,
          count: 0,
          maxSeverity: 'Low',
          lastDetected: threat.timestamp,
        };
      }
      acc[api].count++;
      const severityOrder = ['Low', 'Medium', 'High', 'Critical'];
      if (severityOrder.indexOf(threat.severity) > severityOrder.indexOf(acc[api].maxSeverity)) {
        acc[api].maxSeverity = threat.severity;
      }
      return acc;
    }, {});

    setRiskyAPIs(
      Object.values(apiMap)
        .sort((a, b) => b.count - a.count)
        .slice(0, 5)
    );
  }, [threats]);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Critical': return 'text-primary-red';
      case 'High': return 'text-primary-amber';
      case 'Medium': return 'text-yellow-500';
      case 'Low': return 'text-primary-green';
      default: return 'text-gray-400';
    }
  };

  return (
    <>
      {/* Real-Time Monitoring */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card card-hover"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary-cyan" />
              Real-Time Monitoring
            </h3>
            <p className="text-sm text-gray-400 mt-1">Live network activity feed</p>
          </div>
        </div>
        <RealTimeMonitoring />
      </motion.div>

      {/* Alert Center */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card card-hover"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-primary-red" />
              Alert Center
            </h3>
            <p className="text-sm text-gray-400 mt-1">Active threat alerts</p>
          </div>
        </div>
        <AlertCenter />
      </motion.div>

      {/* Risky APIs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card card-hover"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Globe className="w-5 h-5 text-primary-amber" />
              Risky APIs
            </h3>
            <p className="text-sm text-gray-400 mt-1">Top threat endpoints</p>
          </div>
        </div>

        <div className="space-y-3">
          {riskyAPIs.length > 0 ? (
            riskyAPIs.map((api, index) => (
              <motion.div
                key={api.endpoint}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-3 bg-dark-surface rounded-lg border border-dark-border hover:border-primary-cyan/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{api.endpoint}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {api.count} threat{api.count !== 1 ? 's' : ''} detected
                    </div>
                  </div>
                  <div className={`text-xs font-semibold px-2 py-1 rounded ${getSeverityColor(api.maxSeverity)} bg-opacity-20`}>
                    {api.maxSeverity}
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-400 text-sm">
              No risky APIs detected
            </div>
          )}

          <button
            onClick={() => navigate('/analytics')}
            className="w-full mt-4 btn-primary flex items-center justify-center gap-2"
          >
            View More
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </motion.div>
    </>
  );
};

export default MonitoringAlertsRow;

