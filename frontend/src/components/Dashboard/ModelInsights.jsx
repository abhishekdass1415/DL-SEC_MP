import React from 'react';
import '../../styles/components.css';

const ModelInsights = () => {
  return (
    <div className="widget model-insights">
      <h3>Model Insights</h3>
      <div className="model-content">
        <div className="model-name">CNN</div>
        <div className="metrics">
          <div className="metric">
            <span className="metric-label">Accuracy:</span>
            <span className="metric-value">98%</span>
          </div>
          <div className="metric">
            <span className="metric-label">Precision:</span>
            <span className="metric-value">97%</span>
            <span className="metric-details">(50, 2)</span>
          </div>
          <div className="metric">
            <span className="metric-label">Recall:</span>
            <span className="metric-value">98%</span>
            <span className="metric-details">(1, 47)</span>
          </div>
          <div className="metric">
            <span className="metric-label">F1-Score:</span>
            <span className="metric-value">0.97</span>
          </div>
        </div>
        <button className="retrain-btn">Retrain Model</button>
      </div>
    </div>
  );
};

export default ModelInsights;


