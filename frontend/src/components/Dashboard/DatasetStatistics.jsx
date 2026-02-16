import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Database, FileText, AlertTriangle, CheckCircle } from 'lucide-react';
import { metricsAPI } from '../../services/api';
import { useDashboardStore } from '../../store/dashboardStore';

const DatasetStatistics = () => {
  const [stats, setStats] = useState(null);
  const { datasetStats } = useDashboardStore();

  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await metricsAPI.getMetrics();
        setStats(response.data?.dataset || {});
      } catch (err) {
        // Silently handle network errors (backend not running or network issues)
        if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
          console.error('Error loading stats:', err);
        }
      }
    };

    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const displayStats = stats || datasetStats;

  const statsData = [
    {
      label: 'Total Records',
      value: displayStats?.totalRecords || 0,
      icon: Database,
      color: 'text-primary-cyan',
      bgColor: 'bg-primary-cyan/10',
    },
    {
      label: 'Processed',
      value: displayStats?.currentIndex || 0,
      icon: CheckCircle,
      color: 'text-primary-green',
      bgColor: 'bg-primary-green/10',
    },
    {
      label: 'Threats Detected',
      value: displayStats?.threatsDetected || displayStats?.threats || 0,
      icon: AlertTriangle,
      color: 'text-primary-red',
      bgColor: 'bg-primary-red/10',
    },
    {
      label: 'Remaining',
      value: displayStats?.remaining || displayStats?.remaining_records || 0,
      icon: FileText,
      color: 'text-primary-amber',
      bgColor: 'bg-primary-amber/10',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card card-hover"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Dataset Statistics</h3>
        <Database className="w-5 h-5 text-primary-cyan" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {statsData.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border border-dark-border ${stat.bgColor}`}
            >
              <div className="flex items-center justify-between mb-2">
                <Icon className={`w-5 h-5 ${stat.color}`} />
                <span className="text-xs text-gray-400">{stat.label}</span>
              </div>
              <motion.div
                className={`text-2xl font-bold ${stat.color}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 + 0.2, type: 'spring' }}
              >
                {stat.value.toLocaleString()}
              </motion.div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default DatasetStatistics;

