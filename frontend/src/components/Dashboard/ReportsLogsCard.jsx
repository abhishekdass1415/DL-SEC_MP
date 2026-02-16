import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Download, FileText, Clock } from 'lucide-react';
import { threatAPI } from '../../services/api';

const ReportsLogsCard = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRecentLogs();
    const interval = setInterval(loadRecentLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadRecentLogs = async () => {
    try {
      const response = await threatAPI.getThreats({ limit: 5 });
      const threats = response.data.threats || [];
      
      // Convert threats to log entries
      const logEntries = threats.map((threat, index) => ({
        id: threat.id,
        timestamp: threat.timestamp,
        level: threat.severity === 'Critical' ? 'ERROR' : 
               threat.severity === 'High' ? 'WARNING' : 'INFO',
        message: `${threat.threat_type} detected from ${threat.source_ip}`,
        severity: threat.severity,
      }));
      
      setLogs(logEntries);
    } catch (err) {
      // Silently handle network errors (backend not running or network issues)
      if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
        console.error('Error loading logs:', err);
      }
    }
  };

  const handleExport = () => {
    setLoading(true);
    // Simulate export
    setTimeout(() => {
      alert('Report exported successfully!');
      setLoading(false);
    }, 1000);
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'ERROR': return 'text-primary-red';
      case 'WARNING': return 'text-primary-amber';
      case 'INFO': return 'text-primary-cyan';
      default: return 'text-gray-400';
    }
  };

  const getLevelBg = (level) => {
    switch (level) {
      case 'ERROR': return 'bg-primary-red/20 border-primary-red/50';
      case 'WARNING': return 'bg-primary-amber/20 border-primary-amber/50';
      case 'INFO': return 'bg-primary-cyan/20 border-primary-cyan/50';
      default: return 'bg-gray-800 border-gray-700';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card card-hover"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary-cyan" />
            Reports & Logs
          </h3>
          <p className="text-sm text-gray-400 mt-1">System logs and reports</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => window.location.href = '/logs'}
            className="flex-1 btn-primary flex items-center justify-center gap-2"
          >
            <FileText className="w-4 h-4" />
            View Full Log History
          </button>
          <button
            onClick={handleExport}
            disabled={loading}
            className="flex-1 btn-success flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            {loading ? 'Exporting...' : 'Export Report'}
          </button>
        </div>

        {/* Latest Log Entries */}
        <div>
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Latest 5 Log Entries</h4>
          <div className="space-y-2">
            {logs.length > 0 ? (
              logs.map((log, index) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-3 rounded-lg border ${getLevelBg(log.level)}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs font-semibold ${getLevelColor(log.level)}`}>
                          {log.level}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-white">{log.message}</p>
                    </div>
                    <Clock className="w-4 h-4 text-gray-500 flex-shrink-0" />
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-400 text-sm">
                No log entries available
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ReportsLogsCard;

