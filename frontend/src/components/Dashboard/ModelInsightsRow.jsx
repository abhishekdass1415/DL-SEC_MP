import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, RefreshCw } from 'lucide-react';
import { modelAPI } from '../../services/api';
import { useDashboardStore } from '../../store/dashboardStore';

const ModelInsightsRow = () => {
  const [loading, setLoading] = useState(false);
  const { modelInsights, setModelInsights } = useDashboardStore();

  useEffect(() => {
    loadModelInsights();
    const interval = setInterval(loadModelInsights, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadModelInsights = async () => {
    try {
      const response = await modelAPI.getMetrics();
      const data = response.data || {};
      const models = data.models || {};

      const normalized = {
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
      };

      setModelInsights(normalized);
    } catch (err) {
      // Silently handle network errors (backend not running or network issues)
      if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
        console.error('Error loading model insights:', err);
      }
    }
  };

  const handleRetrain = async () => {
    setLoading(true);
    try {
      await modelAPI.retrain();
      // After retraining completes, refresh metrics
      await loadModelInsights();
    } catch (err) {
      // Silently handle network errors (backend not running or network issues)
      if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
        console.error('Error retraining model:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const ModelCard = ({ name, data, gradient }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card card-hover bg-gradient-to-br ${gradient}`}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">{name}</h3>
        <Brain className="w-5 h-5 text-primary-cyan" />
      </div>

      <div className="space-y-3">
        <Metric label="Accuracy" value={data.accuracy} />
        <Metric label="Precision" value={data.precision} />
        <Metric label="Recall" value={data.recall} />
        <Metric label="F1-Score" value={data.f1} />
      </div>
    </motion.div>
  );

  const Metric = ({ label, value }) => (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-300">{label}</span>
      <motion.span
        key={value}
        initial={{ scale: 1.2 }}
        animate={{ scale: 1 }}
        className="text-lg font-bold text-white"
      >
        {(value * 100).toFixed(1)}%
      </motion.span>
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ModelCard
          name="CNN"
          data={modelInsights.cnn}
          gradient="from-blue-900/20 to-blue-800/10"
        />
        <ModelCard
          name="LSTM"
          data={modelInsights.lstm}
          gradient="from-purple-900/20 to-purple-800/10"
        />
        <ModelCard
          name="CNN + LSTM"
          data={modelInsights.cnnLstm}
          gradient="from-cyan-900/20 to-cyan-800/10"
        />
      </div>

      <motion.button
        onClick={handleRetrain}
        disabled={loading}
        className="w-full btn-primary flex items-center justify-center gap-2 py-3"
      >
        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        {loading ? 'Retraining...' : 'Retrain Model'}
      </motion.button>
    </div>
  );
};

export default ModelInsightsRow;

