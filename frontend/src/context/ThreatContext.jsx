import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { threatAPI } from '../services/api';
import { initSocket } from '../services/socket';
import { useDashboardStore } from '../store/dashboardStore';

const ThreatContext = createContext(null);

export const ThreatProvider = ({ children }) => {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [latestAlert, setLatestAlert] = useState(null);

  const setDatasetStats = useDashboardStore((s) => s.setDatasetStats);
  const setStreamingStatus = useDashboardStore((s) => s.setStreamingStatus);
  const setModelInsights = useDashboardStore((s) => s.setModelInsights);
  const updateLastUpdate = useDashboardStore((s) => s.updateLastUpdate);

  const activeThreats = useMemo(
    () => threats.filter((t) => t.status === 'active'),
    [threats]
  );

  useEffect(() => {
    let isMounted = true;

    const loadThreats = async () => {
      try {
        if (!isMounted) return;
        const response = await threatAPI.getThreats({ limit: 100 });
        const data = response.data?.threats || [];
        if (!isMounted) return;
        setThreats(data);
        setError(null);
        setLoading(false);
      } catch (err) {
        if (!isMounted) return;
        // Silently handle network errors (backend not running or network issues)
        if (
          err.isNetworkError ||
          err.code === 'ERR_NETWORK' ||
          err.code === 'ERR_NETWORK_CHANGED' ||
          err.code === 'ECONNABORTED'
        ) {
          setError(null);
        } else {
          console.error('Error loading threats:', err);
          setError('Failed to load threats');
        }
        setLoading(false);
      }
    };

    // Initial fetch
    loadThreats();

    // Single shared WebSocket connection for threat updates
    const socket = initSocket();
    socket.on('new_threat', loadThreats);
    socket.on('threat_updated', loadThreats);
    socket.on('action_executed', loadThreats);

    // Real-time metrics updates (no refresh needed)
    const onMetricsUpdate = (payload) => {
      try {
        const dataset = payload?.dataset;
        const models = payload?.models;

        if (dataset) setDatasetStats(dataset);

        if (models) {
          setModelInsights({
            cnn: {
              accuracy: models.cnn?.accuracy ?? 0,
              precision: models.cnn?.precision ?? 0,
              recall: models.cnn?.recall ?? 0,
              f1: models.cnn?.f1 ?? 0,
            },
            lstm: {
              accuracy: models.lstm?.accuracy ?? 0,
              precision: models.lstm?.precision ?? 0,
              recall: models.lstm?.recall ?? 0,
              f1: models.lstm?.f1 ?? 0,
            },
            cnnLstm: {
              accuracy: models.cnn_lstm?.accuracy ?? 0,
              precision: models.cnn_lstm?.precision ?? 0,
              recall: models.cnn_lstm?.recall ?? 0,
              f1: models.cnn_lstm?.f1 ?? 0,
            },
          });
        }
        updateLastUpdate();
      } catch (e) {
        // Never crash UI on socket payload issues
      }
    };
    socket.on('metrics_update', onMetricsUpdate);

    // Alerts stream
    const onAlert = (alert) => {
      setLatestAlert(alert || null);
      updateLastUpdate();
    };
    socket.on('alert', onAlert);

    // Poll every 10 seconds as a safety net
    const intervalId = setInterval(loadThreats, 10000);

    return () => {
      isMounted = false;
      socket.off('new_threat', loadThreats);
      socket.off('threat_updated', loadThreats);
      socket.off('action_executed', loadThreats);
      socket.off('metrics_update', onMetricsUpdate);
      socket.off('alert', onAlert);
      clearInterval(intervalId);
    };
  }, []);

  const value = useMemo(
    () => ({
      threats,
      activeThreats,
      loading,
      error,
      latestAlert,
    }),
    [threats, activeThreats, loading, error, latestAlert]
  );

  return (
    <ThreatContext.Provider value={value}>{children}</ThreatContext.Provider>
  );
};

export const useThreats = () => {
  const ctx = useContext(ThreatContext);
  if (!ctx) {
    throw new Error('useThreats must be used within a ThreatProvider');
  }
  return ctx;
};

