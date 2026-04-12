import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, RefreshCw } from 'lucide-react';
import { useThreats } from '../context/ThreatContext';
import '../styles/App.css';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all', 'ERROR', 'WARNING', 'INFO'
  const { threats, loading: threatsLoading } = useThreats();

  const buildLogsFromThreats = (sourceThreats) => {
    return (sourceThreats || [])
      .map((threat) => ({
        id: threat.id,
        timestamp: threat.timestamp,
        level:
          threat.severity === 'Critical'
            ? 'ERROR'
            : threat.severity === 'High'
            ? 'WARNING'
            : 'INFO',
        message: `${threat.threat_type} detected from ${
          threat.source_ip || 'Unknown'
        }`,
        severity: threat.severity,
        threatType: threat.threat_type,
        sourceIp: threat.source_ip,
        destinationIp: threat.destination_ip,
        confidence: threat.confidence,
      }))
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  };

  useEffect(() => {
    // Build logs list from global threats (sorted newest first)
    const logEntries = buildLogsFromThreats(threats);
    setLogs(logEntries);
    setLoading(false);
  }, [threats]);

  const handleRefresh = () => {
    // Rebuild from latest threats; ThreatContext already keeps data fresh
    setLoading(true);
    const logEntries = buildLogsFromThreats(threats);
    setLogs(logEntries);
    setLoading(false);
  };

  const handleExport = () => {
    const csvContent = [
      ['Timestamp', 'Level', 'Message', 'Severity', 'Source IP', 'Destination IP', 'Confidence'],
      ...logs.map(log => [
        new Date(log.timestamp).toISOString(),
        log.level,
        log.message,
        log.severity,
        log.sourceIp || 'N/A',
        log.destinationIp || 'N/A',
        log.confidence ? `${(log.confidence * 100).toFixed(1)}%` : 'N/A'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `security-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
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

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(log => log.level === filter);

  return (
    <main className="main-content">
      <div className="w-full max-w-7xl mx-auto space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="dashboard-title">System Logs</h1>
              <p className="text-gray-400">Security and system event logs</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="btn-primary flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={handleExport}
                className="btn-success flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
          </div>
        </motion.div>

        {/* Filter Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex gap-2"
        >
          {['all', 'ERROR', 'WARNING', 'INFO'].map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === level
                  ? 'bg-primary-blue text-white'
                  : 'bg-dark-surface border border-dark-border text-gray-300 hover:border-primary-cyan/50'
              }`}
            >
              {level === 'all' ? 'All Logs' : level}
            </button>
          ))}
        </motion.div>

        {/* Logs List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card card-hover"
        >
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="text-gray-400">Loading logs...</div>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="flex items-center justify-center h-48">
              <div className="text-center">
                <FileText className="w-12 h-12 mx-auto mb-2 text-gray-500 opacity-50" />
                <p className="text-gray-400">No logs available</p>
              </div>
            </div>
          ) : (
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredLogs.map((log, index) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className={`p-4 rounded-lg border ${getLevelBg(log.level)}`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`text-xs font-semibold px-2 py-1 rounded ${getLevelColor(log.level)} bg-opacity-20`}>
                          {log.level}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                        {log.severity && (
                          <span className="text-xs text-gray-500">
                            Severity: {log.severity}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-white font-medium mb-1">{log.message}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        {log.sourceIp && (
                          <span>Source: {log.sourceIp}</span>
                        )}
                        {log.destinationIp && (
                          <span>Destination: {log.destinationIp}</span>
                        )}
                        {log.confidence && (
                          <span>Confidence: {(log.confidence * 100).toFixed(1)}%</span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </main>
  );
};

export default Logs;
