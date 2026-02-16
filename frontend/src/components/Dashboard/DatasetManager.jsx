import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, Play, Square, RefreshCw, FileText, Activity, Globe2, Database } from 'lucide-react';
import { datasetAPI, metricsAPI } from '../../services/api';
import { initSocket } from '../../services/socket';
import { useDashboardStore } from '../../store/dashboardStore';

const DatasetManager = () => {
  const [datasetStats, setDatasetStats] = useState(null);
  const [streamingStatus, setStreamingStatus] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [file, setFile] = useState(null);
  const [interval, setInterval] = useState(2.0);
  const [progress, setProgress] = useState(0);
  const [dataSource, setDataSource] = useState('dataset'); // 'dataset' | 'api'
  const [apiUrl, setApiUrl] = useState('');
  
  const { setDatasetStats: setStoreStats, setStreamingStatus: setStoreStreaming } = useDashboardStore();

  useEffect(() => {
    loadStats();
    loadStreamingStatus();
    
    const socket = initSocket();
    socket.on('new_threat', () => {
      loadStats();
    });
    
    const statusInterval = setInterval(() => {
      loadStreamingStatus();
    }, 2000);
    
    return () => {
      socket.off('new_threat');
      clearInterval(statusInterval);
    };
  }, []);

  const loadStats = async () => {
    try {
      const response = await metricsAPI.getMetrics();
      const stats = response.data?.dataset || {};
      setDatasetStats(stats);
      setStoreStats(stats);
      if (stats.totalRecords && stats.currentIndex) {
        setProgress((stats.currentIndex / stats.totalRecords) * 100);
      }
      setError(null);
    } catch (err) {
      // Silently handle network errors (backend not running or network issues)
      if (err.isNetworkError || err.code === 'ERR_NETWORK' || err.code === 'ERR_NETWORK_CHANGED' || err.code === 'ECONNABORTED') {
        // Don't show error message for network errors - backend might not be running
        return;
      }
      if (err.response?.status !== 404) {
        setError('Failed to load dataset statistics');
      }
    }
  };

  const loadStreamingStatus = async () => {
    try {
      const response = await datasetAPI.getStreamingStatus();
      const status = response.data.is_running || false;
      setStreamingStatus(status);
      setStoreStreaming(status);
    } catch (err) {
      // Silently handle network errors (backend not running or network issues)
      if (!err.isNetworkError && err.code !== 'ERR_NETWORK' && err.code !== 'ERR_NETWORK_CHANGED' && err.code !== 'ECONNABORTED') {
        console.error('Error loading streaming status:', err);
      }
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await datasetAPI.uploadDataset(file);
      setSuccess(`Dataset loaded: ${response.data.total_records} records`);
      setFile(null);
      await loadStats();
    } catch (err) {
      // Handle timeout and network errors with better messages
      if (err.isNetworkError || err.code === 'ECONNABORTED' || err.code === 'ERR_NETWORK' || err.code === 'ERR_NETWORK_CHANGED') {
        if (err.code === 'ECONNABORTED') {
          setError('Upload timed out. The file may be too large or the server is processing. Please try a smaller file or wait and try again.');
        } else {
          setError('Failed to connect to server. Please ensure the backend is running.');
        }
      } else {
        setError(err.response?.data?.error || err.message || 'Failed to upload dataset');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLoadDataset = async () => {
    const defaultPath = 'UNSW_NB15_testing-set.csv';
    const fullPath = prompt('Enter the full path to the test dataset file:', defaultPath);
    
    if (!fullPath) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await datasetAPI.loadDataset(fullPath);
      setSuccess(`Dataset loaded: ${response.data.total_records} records`);
      await loadStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleStartStreaming = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Configure stream first based on selected source
      await datasetAPI.configureStream({
        source: dataSource === 'api' ? 'api' : 'dataset',
        apiUrl: dataSource === 'api' ? apiUrl : null,
        interval,
      });

      await datasetAPI.startStreaming(
        interval,
        dataSource !== 'api', // use_dataset flag
        dataSource === 'api' ? 'api' : 'dataset',
        dataSource === 'api' ? apiUrl : null,
      );
      setSuccess('Streaming started');
      setStreamingStatus(true);
      setStoreStreaming(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start streaming');
    } finally {
      setLoading(false);
    }
  };

  const handleStopStreaming = async () => {
    setLoading(true);
    try {
      await datasetAPI.stopStreaming();
      setSuccess('Streaming stopped');
      setStreamingStatus(false);
      setStoreStreaming(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to stop streaming');
    } finally {
      setLoading(false);
    }
  };

  const handleResetDataset = async () => {
    setLoading(true);
    try {
      await datasetAPI.resetDataset();
      setSuccess('Dataset stream reset');
      await loadStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to reset dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleProcessBatch = async () => {
    setLoading(true);
    try {
      const response = await datasetAPI.processDataset(10);
      setSuccess(`Processed ${response.data.processed} records`);
      await loadStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process batch');
    } finally {
      setLoading(false);
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
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary-cyan" />
            Dataset Manager
          </h2>
          <p className="text-sm text-gray-400 mt-1">Manage datasets and real-time streaming</p>
        </div>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-4 p-3 bg-primary-red/20 border border-primary-red/50 rounded-lg text-primary-red text-sm"
        >
          {error}
        </motion.div>
      )}

      {success && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-4 p-3 bg-primary-green/20 border border-primary-green/50 rounded-lg text-primary-green text-sm"
        >
          {success}
        </motion.div>
      )}

      {/* Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Upload Dataset */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Upload Dataset</h3>
          
          <form onSubmit={handleFileUpload} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Select File (CSV/Excel)</label>
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-white text-sm
                         file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0
                         file:text-sm file:font-semibold
                         file:bg-primary-blue file:text-white
                         hover:file:bg-primary-blue/90"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !file}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <Upload className="w-4 h-4" />
              Upload Dataset
            </button>
          </form>

          {datasetStats && (
            <div className="mt-4 p-4 bg-dark-surface rounded-lg border border-dark-border">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Processing Progress</span>
                <span className="text-sm font-semibold text-white">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-dark-border rounded-full h-2">
                <motion.div
                  className="bg-gradient-to-r from-primary-cyan to-primary-blue h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Real-Time Streaming */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Real-Time Streaming</h3>
          
          <div className="space-y-4">
            {/* Data Source Selector */}
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setDataSource('dataset')}
                disabled={streamingStatus}
                className={`px-3 py-2 rounded-lg text-sm flex items-center justify-center gap-2 border ${
                  dataSource === 'dataset'
                    ? 'bg-primary-blue/20 border-primary-blue text-primary-cyan'
                    : 'bg-dark-surface border-dark-border text-gray-300'
                }`}
              >
                <Database className="w-4 h-4" />
                Dataset Upload
              </button>
              <button
                type="button"
                onClick={() => setDataSource('api')}
                disabled={streamingStatus}
                className={`px-3 py-2 rounded-lg text-sm flex items-center justify-center gap-2 border ${
                  dataSource === 'api'
                    ? 'bg-primary-blue/20 border-primary-blue text-primary-cyan'
                    : 'bg-dark-surface border-dark-border text-gray-300'
                }`}
              >
                <Globe2 className="w-4 h-4" />
                External API
              </button>
            </div>

            {/* External API URL (only when API mode is selected) */}
            {dataSource === 'api' && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">API Endpoint URL</label>
                <input
                  type="text"
                  value={apiUrl ?? ''}
                  onChange={(e) => setApiUrl(e.target.value || '')}
                  placeholder="https://example.com/traffic-stream"
                  disabled={streamingStatus}
                  className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-white text-sm placeholder-gray-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  The endpoint should return JSON for each poll (single record or list of records).
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm text-gray-400 mb-2">Streaming Interval (seconds)</label>
              <input
                type="number"
                value={interval ?? 2.0}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setInterval(isNaN(val) ? 2.0 : val);
                }}
                min="0.5"
                max="60"
                step="0.5"
                disabled={streamingStatus}
                className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-white"
              />
            </div>

            <div className="flex items-center gap-3">
              {!streamingStatus ? (
                <button
                  onClick={handleStartStreaming}
                  disabled={
                    loading ||
                    (dataSource === 'dataset' && (!datasetStats || !datasetStats.totalRecords)) ||
                    (dataSource === 'api' && !apiUrl)
                  }
                  className="btn-success flex-1 flex items-center justify-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Start Streaming
                </button>
              ) : (
                <button
                  onClick={handleStopStreaming}
                  disabled={loading}
                  className="btn-danger flex-1 flex items-center justify-center gap-2"
                >
                  <Square className="w-4 h-4" />
                  Stop Streaming
                </button>
              )}
              
              <div className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                streamingStatus 
                  ? 'bg-primary-green/20 border border-primary-green/50 text-primary-green' 
                  : 'bg-gray-800 border border-dark-border text-gray-400'
              }`}>
                <div className={`w-2 h-2 rounded-full ${streamingStatus ? 'bg-primary-green animate-pulse' : 'bg-gray-500'}`} />
                <span className="text-sm font-medium">
                  {streamingStatus ? 'Active' : 'Paused'}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleResetDataset}
                disabled={loading || !datasetStats}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Reset
              </button>
              <button
                onClick={handleProcessBatch}
                disabled={loading || !datasetStats || streamingStatus}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                <FileText className="w-4 h-4" />
                Process Batch
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Dataset Statistics Preview */}
      {datasetStats && !datasetStats.error && (
        <div className="mt-6 pt-6 border-t border-dark-border">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <div className="text-2xl font-bold text-white">{datasetStats.totalRecords || 0}</div>
              <div className="text-xs text-gray-400 mt-1">Total Records</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">{datasetStats.currentIndex || 0}</div>
              <div className="text-xs text-gray-400 mt-1">Current Index</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary-red">{datasetStats.threatsDetected || datasetStats.threats || 0}</div>
              <div className="text-xs text-gray-400 mt-1">Threats Detected</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary-green">{datasetStats.remaining || datasetStats.remaining_records || 0}</div>
              <div className="text-xs text-gray-400 mt-1">Remaining</div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default DatasetManager;
