import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Download, FileText, Clock } from 'lucide-react';
import { useThreats } from '../../context/ThreatContext';
import { reportAPI } from '../../services/api';

const ReportsLogsCard = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const { threats } = useThreats();

  useEffect(() => {
    // Derive recent logs from global threats (top 5)
    const latest = [...(threats || [])]
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 5);

    const logEntries = latest.map((threat) => ({
      id: threat.id,
      timestamp: threat.timestamp,
      level:
        threat.severity === 'Critical'
          ? 'ERROR'
          : threat.severity === 'High'
          ? 'WARNING'
          : 'INFO',
      message: `${threat.threat_type} detected from ${threat.source_ip}`,
      severity: threat.severity,
    }));
    setLogs(logEntries);
  }, [threats]);

  const handleExport = async () => {
    setLoading(true);
    try {
      const response = await reportAPI.generate();
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      const contentDisposition = response.headers?.['content-disposition'] || '';
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      const filename = match?.[1] || `dl-sec-report-${new Date().toISOString().split('T')[0]}.pdf`;

      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      // Keep UI resilient; avoid crashing on network errors
      const msg =
        err?.isNetworkError
          ? 'Backend server is not available. Please ensure the backend is running.'
          : 'Failed to export report.';
      alert(msg);
    } finally {
      setLoading(false);
    }
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

