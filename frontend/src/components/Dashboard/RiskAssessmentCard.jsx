import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, TrendingUp } from 'lucide-react';
import { threatAPI } from '../../services/api';
import { initSocket } from '../../services/socket';

const RiskAssessmentCard = () => {
  const [threats, setThreats] = useState([]);
  const [hoveredApi, setHoveredApi] = useState(null);
  const [riskLevel, setRiskLevel] = useState(0);

  useEffect(() => {
    const loadThreats = async () => {
      try {
        const response = await threatAPI.getThreats({ limit: 50 });
        const threatsData = response.data.threats || [];
        setThreats(threatsData);
        
        // Calculate overall risk level
        const criticalCount = threatsData.filter(t => t.severity === 'Critical').length;
        const highCount = threatsData.filter(t => t.severity === 'High').length;
        const total = threatsData.length;
        const risk = total > 0 ? ((criticalCount * 100 + highCount * 60) / total) : 0;
        setRiskLevel(Math.min(100, risk));
      } catch (err) {
        // Silently handle network errors (backend not running or network issues)
        if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
          console.error('Error loading threats:', err);
        }
      }
    };

    loadThreats();
    const socket = initSocket();
    socket.on('new_threat', loadThreats);
    socket.on('threat_updated', loadThreats);

    const interval = setInterval(loadThreats, 5000);
    return () => {
      socket.off('new_threat');
      socket.off('threat_updated');
      clearInterval(interval);
    };
  }, []);

  // Get top risky IPs/APIs
  const riskyIPs = Object.values(
    threats.reduce((acc, threat) => {
      const ip = threat.source_ip || 'Unknown';
      if (!acc[ip]) {
        acc[ip] = {
          ip,
          count: 0,
          maxSeverity: 'Low',
          lastDetected: threat.timestamp,
          threatTypes: new Set(),
        };
      }
      acc[ip].count++;
      acc[ip].threatTypes.add(threat.threat_type);
      const severityOrder = ['Low', 'Medium', 'High', 'Critical'];
      if (severityOrder.indexOf(threat.severity) > severityOrder.indexOf(acc[ip].maxSeverity)) {
        acc[ip].maxSeverity = threat.severity;
      }
      return acc;
    }, {})
  )
    .map(item => ({ ...item, threatTypes: Array.from(item.threatTypes) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  const getRiskColor = (level) => {
    if (level >= 75) return 'bg-primary-red';
    if (level >= 50) return 'bg-primary-amber';
    if (level >= 25) return 'bg-yellow-500';
    return 'bg-primary-green';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Critical': return 'text-primary-red';
      case 'High': return 'text-primary-amber';
      case 'Medium': return 'text-yellow-500';
      case 'Low': return 'text-primary-green';
      default: return 'text-gray-400';
    }
  };

  const displayRiskLevel = hoveredApi 
    ? (hoveredApi.maxSeverity === 'Critical' ? 90 : 
       hoveredApi.maxSeverity === 'High' ? 70 : 
       hoveredApi.maxSeverity === 'Medium' ? 50 : 30)
    : riskLevel;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card card-hover"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Risk Assessment</h3>
        <TrendingUp className="w-5 h-5 text-primary-amber" />
      </div>

      <div className="space-y-4">
        {/* Risk Level Bar */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Overall Risk Level</span>
            <span className="text-lg font-bold text-white">{Math.round(displayRiskLevel)}%</span>
          </div>
          <div className="w-full bg-dark-border rounded-full h-4 overflow-hidden">
            <motion.div
              className={`h-full ${getRiskColor(displayRiskLevel)}`}
              initial={{ width: 0 }}
              animate={{ width: `${displayRiskLevel}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <div className="flex justify-between mt-1 text-xs text-gray-500">
            <span>Low</span>
            <span>Medium</span>
            <span>High</span>
            <span>Critical</span>
          </div>
        </div>

        {/* Top Risky IPs */}
        <div>
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Top Risky IPs</h4>
          <div className="space-y-2">
            {riskyIPs.length > 0 ? (
              riskyIPs.map((item, index) => (
                <motion.div
                  key={item.ip}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  onMouseEnter={() => setHoveredApi(item)}
                  onMouseLeave={() => setHoveredApi(null)}
                  className={`p-3 rounded-lg border transition-all cursor-pointer ${
                    hoveredApi?.ip === item.ip
                      ? 'border-primary-cyan bg-primary-cyan/10'
                      : 'border-dark-border bg-dark-surface'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-white">{item.ip}</span>
                    <span className={`text-xs font-semibold ${getSeverityColor(item.maxSeverity)}`}>
                      {item.maxSeverity}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">{item.count} threats</span>
                    <div className="w-24 bg-dark-border rounded-full h-1.5">
                      <div
                        className={`h-full ${getRiskColor(item.count * 10)}`}
                        style={{ width: `${Math.min(100, item.count * 10)}%` }}
                      />
                    </div>
                  </div>
                  {hoveredApi?.ip === item.ip && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-2 pt-2 border-t border-dark-border text-xs text-gray-400"
                    >
                      <div>Types: {Array.from(item.threatTypes).join(', ')}</div>
                      <div>Last: {new Date(item.lastDetected).toLocaleTimeString()}</div>
                    </motion.div>
                  )}
                </motion.div>
              ))
            ) : (
              <div className="text-center py-4 text-gray-400 text-sm">
                No risky IPs detected
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default RiskAssessmentCard;

