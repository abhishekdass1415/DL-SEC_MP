import React from 'react';
import ModelInsightsRow from '../components/Dashboard/ModelInsightsRow';
import '../styles/App.css';

const ModelInsightsPage = () => {
  return (
    <main className="main-content">
      <div className="w-full max-w-7xl mx-auto space-y-6">
        <h1 className="dashboard-title">Model Insights</h1>
        <div className="space-y-6">
          <ModelInsightsRow />
          <div className="card card-hover">
            <h3 className="text-lg font-semibold text-white mb-2">Model Training History</h3>
            <p className="text-gray-400">Historical data on model training and performance improvements.</p>
          </div>
          <div className="card card-hover">
            <h3 className="text-lg font-semibold text-white mb-2">Model Comparison</h3>
            <p className="text-gray-400">Compare different models and their performance metrics.</p>
          </div>
        </div>
      </div>
    </main>
  );
};

export default ModelInsightsPage;
