import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { threatAPI, actionAPI } from '../../services/api';
import { useDashboardStore } from '../../store/dashboardStore';
import { useThreats } from '../../context/ThreatContext';

const AlertCenter = () => {
  const [threats, setThreats] = useState([]);
  const { activeThreats, loading, error } = useThreats();
  const [expandedThreat, setExpandedThreat] = useState(null);
  const [executingActionId, setExecutingActionId] = useState(null);
  const { setSelectedThreat, setTotalActiveThreats } = useDashboardStore();

  // Sync local list (for expanded state and actions) with global active threats
  useEffect(() => {
    const list = activeThreats.slice(0, 10);
    setThreats((prevThreats) => {
      return list.map((incoming) => {
        const existing = prevThreats.find(t => t.id === incoming.id);
        if (existing && existing.actions) {
          return { ...incoming, actions: existing.actions };
        }
        return incoming;
      });
    });
    setTotalActiveThreats(list.length);
  }, [activeThreats, setTotalActiveThreats]);

  const loadThreatActions = async (threatId) => {
    try {
      const response = await threatAPI.getThreatActions(threatId);
      setThreats(prev =>
        prev.map(t =>
          t.id === threatId ? { ...t, actions: response.data.actions } : t
        )
      );
    } catch (err) {
      // Silently handle network errors (backend not running or network issues)
      if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
        console.error('Error fetching actions:', err);
      }
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getSeverityBadge = (severity) => {
    const colors = {
      Critical: 'badge-critical',
      High: 'badge-high',
      Medium: 'badge-medium',
      Low: 'badge-low',
    };
    return colors[severity] || 'badge-low';
  };

  const handleExecuteAction = async (actionId, threatId) => {
    try {
      setExecutingActionId(actionId);
      await actionAPI.executeAction(actionId);
      await loadThreatActions(threatId);
    } catch (err) {
      // Silently handle network errors (backend not running or network issues)
      if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
        console.error('Error executing action:', err);
      }
    } finally {
      setExecutingActionId(null);
    }
  };

  const toggleThreatExpansion = async (threatId) => {
    if (expandedThreat === threatId) {
      setExpandedThreat(null);
      setSelectedThreat(null);
    } else {
      setExpandedThreat(threatId);
      const threat = threats.find(t => t.id === threatId);
      if (threat) {
        setSelectedThreat(threat);
        if (!threat.actions) await loadThreatActions(threatId);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="text-gray-400">Loading threats...</div>
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-96 overflow-y-auto">
      {error && (
        <div className="p-3 bg-primary-red/20 border border-primary-red/50 rounded-lg text-primary-red text-sm">
          {error}
        </div>
      )}

      {threats.length === 0 ? (
        <div className="text-center py-8 text-gray-400 text-sm">
          No active threats detected
        </div>
      ) : (
        <AnimatePresence>
          {threats.map((threat) => (
            <motion.div
              key={threat.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-dark-surface border border-dark-border rounded-lg overflow-hidden hover:border-primary-cyan/50 transition-colors"
            >
              <div
                onClick={() => toggleThreatExpansion(threat.id)}
                className="p-3 cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="text-xs text-gray-400 w-16 flex-shrink-0">
                    {formatTime(threat.timestamp)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">
                      {threat.threat_type}
                    </div>
                    <div className="text-xs text-gray-400 truncate">
                      {threat.source_ip || 'Unknown'}
                    </div>
                  </div>
                  <span className={`badge ${getSeverityBadge(threat.severity)} flex-shrink-0`}>
                    {threat.severity}
                  </span>
                </div>
                {expandedThreat === threat.id ? (
                  <ChevronUp className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                )}
              </div>

              <AnimatePresence>
                {expandedThreat === threat.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-dark-border bg-dark-card"
                  >
                    <div className="p-4 space-y-3">
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-gray-400">Confidence:</span>
                          <span className="ml-2 text-white font-semibold">
                            {threat.confidence ? `${(threat.confidence * 100).toFixed(1)}%` : 'N/A'}
                          </span>
                        </div>
                        {threat.destination_ip && (
                          <div>
                            <span className="text-gray-400">Destination:</span>
                            <span className="ml-2 text-white">{threat.destination_ip}</span>
                          </div>
                        )}
                      </div>

                      <div>
                        <div className="text-sm font-semibold text-gray-300 mb-2">Suggested Actions:</div>
                        {threat.actions && threat.actions.length > 0 ? (
                          <div className="space-y-2">
                            {threat.actions.map((action) => (
                              <div
                                key={action.id}
                                className="flex items-center justify-between p-2 bg-dark-surface rounded border border-dark-border"
                              >
                                <span className="text-sm text-white flex-1">{action.suggested_action}</span>
                                <div className="flex items-center gap-2">
                                  <span className={`badge ${getSeverityBadge(action.priority)} text-xs`}>
                                    {action.priority}
                                  </span>
                                  {action.executed ? (
                                    <CheckCircle className="w-4 h-4 text-primary-green" />
                                  ) : (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleExecuteAction(action.id, threat.id);
                                      }}
                                      disabled={executingActionId === action.id}
                                      className="btn-primary text-xs px-3 py-1"
                                    >
                                      {executingActionId === action.id ? 'Executing...' : 'Execute'}
                                    </button>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-400">Loading actions...</div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </AnimatePresence>
      )}
    </div>
  );
};

export default AlertCenter;
