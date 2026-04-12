import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add response interceptor to handle network errors gracefully
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors (connection refused, network changed, timeout, etc.)
    const isNetworkError = 
      error.code === 'ERR_NETWORK' || 
      error.code === 'ERR_NETWORK_CHANGED' ||
      error.code === 'ECONNABORTED' || // Timeout
      error.message === 'Network Error' ||
      error.message?.includes('ERR_NETWORK_CHANGED') ||
      error.message?.includes('Failed to fetch') ||
      error.message?.includes('timeout');
    
    if (isNetworkError) {
      // Don't log network errors to console - they're expected when backend is down or network issues
      // Components will handle these errors appropriately
      const errorMessage = error.code === 'ECONNABORTED' 
        ? 'Request timed out. The server may be processing a large file. Please try again.'
        : 'Backend server is not available. Please ensure the backend is running.';
      
      return Promise.reject({
        ...error,
        isNetworkError: true,
        code: error.code || 'ERR_NETWORK',
        message: errorMessage,
      });
    }
    // For other errors, pass them through normally
    return Promise.reject(error);
  }
);

// Add request timeout to prevent hanging connections
// Use longer timeout for file uploads, shorter for regular requests
api.defaults.timeout = 30000; // 30 seconds default (increased for file uploads)

export const threatAPI = {
  detectThreat: (data) => api.post('/threats/detect', data),
  getThreats: (params = {}) => api.get('/threats', { params }),
  getThreat: (threatId) => api.get(`/threats/${threatId}`),
  getThreatActions: (threatId) => api.get(`/threats/${threatId}/actions`),
  updateThreat: (threatId, data) => api.patch(`/threats/${threatId}`, data),
};

export const actionAPI = {
  getAction: (actionId) => api.get(`/actions/${actionId}`),
  executeAction: (actionId) => api.post(`/actions/${actionId}/execute`),
  getThreatActions: (threatId) => api.get(`/actions/threat/${threatId}`),
};

export const modelAPI = {
  getStatus: () => api.get('/model/status'),
  predict: (data) => api.post('/model/predict', data),
  getMetrics: () => api.get('/model/metrics'),
  retrain: () => api.post('/model/retrain'),
};

export const datasetAPI = {
  uploadDataset: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    // Use longer timeout for file uploads (60 seconds for large files)
    return api.post('/dataset/upload', formData, {
      timeout: 60000, // 60 seconds for file uploads
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      // onUploadProgress can be added here if needed for progress indicators
    });
  },
  loadDataset: (filePath) => api.post('/dataset/load', { file_path: filePath }),
  getDatasetStats: () => api.get('/dataset/stats'),
  getSampleRecords: (n = 5) => api.get('/dataset/sample', { params: { n } }),
  processDataset: (batchSize = 1) => api.post('/dataset/process', { batch_size: batchSize }),
  startStreaming: (interval = 2.0, useDataset = true, source = 'dataset', apiUrl = null, sessionId = null) => 
    api.post('/dataset/stream/start', { interval, use_dataset: useDataset, source, api_url: apiUrl, session_id: sessionId }),
  stopStreaming: () => api.post('/dataset/stream/stop'),
  getStreamingStatus: () => api.get('/dataset/stream/status'),
  resetDataset: () => api.post('/dataset/reset'),
  configureStream: ({ source, apiUrl, interval }) =>
    api.post('/dataset/configure-stream', { source, api_url: apiUrl, interval }),
};

export const metricsAPI = {
  getMetrics: () => api.get('/metrics'),
};

export const analyticsAPI = {
  getSummary: () => api.get('/analytics/summary'),
};

export const reportAPI = {
  generate: () =>
    api.post('/report/generate', null, {
      responseType: 'blob',
      timeout: 60000,
    }),
};

// New streaming endpoints (Phase 3 spec). Backward compatible with /dataset/stream/*
export const streamAPI = {
  start: ({ interval = 2.0, source = 'dataset', apiUrl = null, sessionId = null } = {}) =>
    api.post('/stream/start', {
      interval,
      source,
      api_url: apiUrl,
      session_id: sessionId,
      use_dataset: source === 'dataset',
    }),
  pause: () => api.post('/stream/pause'),
  reset: () => api.post('/stream/reset'),
  status: () => api.get('/stream/status'),
};

export default api;


