import { create } from 'zustand';

export const useDashboardStore = create((set) => ({
  // System status
  systemStatus: 'active', // active, idle, error
  lastUpdate: new Date().toISOString(),
  
  // Summary stats
  totalActiveThreats: 0,
  safeRequests: 0,
  serverHealth: 100,
  
  // Dataset stats
  datasetStats: null,
  streamingStatus: false,
  
  // Threats
  threats: [],
  selectedThreat: null,
  
  // Model insights
  modelInsights: {
    cnn: { accuracy: 0, precision: 0, recall: 0, f1: 0 },
    lstm: { accuracy: 0, precision: 0, recall: 0, f1: 0 },
    cnnLstm: { accuracy: 0, precision: 0, recall: 0, f1: 0 },
  },
  
  // Actions
  setSystemStatus: (status) => set({ systemStatus: status }),
  updateLastUpdate: () => set({ lastUpdate: new Date().toISOString() }),
  setTotalActiveThreats: (count) => set({ totalActiveThreats: count }),
  setSafeRequests: (count) => set({ safeRequests: count }),
  setServerHealth: (health) => set({ serverHealth: health }),
  setDatasetStats: (stats) => set({ datasetStats: stats }),
  setStreamingStatus: (status) => set({ streamingStatus: status }),
  setThreats: (threats) => set({ threats }),
  setSelectedThreat: (threat) => set({ selectedThreat: threat }),
  setModelInsights: (insights) => set({ modelInsights: insights }),
}));

