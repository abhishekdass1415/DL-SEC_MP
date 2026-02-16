import React, { useEffect, useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { AlertTriangle } from 'lucide-react';
import { threatAPI } from '../../services/api';
import { initSocket } from '../../services/socket';
import { useDashboardStore } from '../../store/dashboardStore';

const COLORS = ['#ef4444', '#f97316', '#f59e0b', '#10b981', '#06b6d4', '#3b82f6'];

const ThreatAnalyticsCard = () => {
  const [threats, setThreats] = useState([]);
  const { selectedThreat, setSelectedThreat } = useDashboardStore();

  useEffect(() => {
    const loadThreats = async () => {
      try {
        const response = await threatAPI.getThreats({ limit: 100 });
        setThreats(response.data.threats || []);
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

  const pieData = useMemo(() => {
    const threatCounts = threats.reduce((acc, threat) => {
      const type = threat.threat_type || 'Unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(threatCounts).map(([name, value]) => ({
      name,
      value,
    })).filter(item => item.value > 0);
  }, [threats]);

  const totalThreats = threats.length;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card card-hover"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Threat Analytics</h3>
        <AlertTriangle className="w-5 h-5 text-primary-red" />
      </div>

      {totalThreats === 0 ? (
        <div className="flex items-center justify-center h-48 text-gray-400">
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No threats detected</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-1">{totalThreats}</div>
            <div className="text-sm text-gray-400">Total Threats</div>
          </div>

          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
                onMouseEnter={(data, index) => {
                  // Highlight corresponding threat in Alert Center
                  const threatType = data.name;
                  const threat = threats.find(t => t.threat_type === threatType);
                  if (threat) setSelectedThreat(threat);
                }}
              >
                {pieData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS[index % COLORS.length]}
                    style={{ 
                      filter: selectedThreat?.threat_type === entry.name 
                        ? 'brightness(1.3) drop-shadow(0 0 8px rgba(59, 130, 246, 0.5))' 
                        : 'none' 
                    }}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f1f1f',
                  border: '1px solid #2a2a2a',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: '12px', color: '#9ca3af' }}
                iconType="circle"
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </motion.div>
  );
};

export default ThreatAnalyticsCard;

