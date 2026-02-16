import React from 'react';
import DatasetManager from '../components/Dashboard/DatasetManager';
import '../styles/App.css';

const DatasetPage = () => {
  return (
    <main className="main-content">
      <div className="w-full max-w-7xl">
        <h1 className="dashboard-title">Dataset Management</h1>
        <div className="page-content">
        <DatasetManager />
        <div className="widget">
          <h3>Dataset Information</h3>
          <p>Upload CSV or Excel files to process through the threat detection model.</p>
          <p>You can also load the test dataset (UNSW_NB15_testing-set.csv) directly.</p>
        </div>
      </div>
      </div>
    </main>
  );
};

export default DatasetPage;

