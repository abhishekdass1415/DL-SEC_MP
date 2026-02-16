import React from 'react';
import '../styles/App.css';

const Settings = () => {
  return (
    <main className="main-content">
      <div className="w-full max-w-7xl">
        <h1 className="dashboard-title">Settings</h1>
        <div className="page-content">
        <div className="widget">
          <h3>General Settings</h3>
          <div className="settings-section">
            <div className="setting-item">
              <label>Dashboard Refresh Rate</label>
              <select className="setting-input">
                <option>5 seconds</option>
                <option>10 seconds</option>
                <option>30 seconds</option>
                <option>1 minute</option>
              </select>
            </div>
            <div className="setting-item">
              <label>Theme</label>
              <select className="setting-input">
                <option>Dark</option>
                <option>Light</option>
              </select>
            </div>
            <div className="setting-item">
              <label>Notifications</label>
              <input type="checkbox" defaultChecked />
            </div>
          </div>
        </div>
        <div className="widget">
          <h3>Security Settings</h3>
          <div className="settings-section">
            <div className="setting-item">
              <label>Two-Factor Authentication</label>
              <input type="checkbox" />
            </div>
            <div className="setting-item">
              <label>Auto-Lock After</label>
              <select className="setting-input">
                <option>5 minutes</option>
                <option>15 minutes</option>
                <option>30 minutes</option>
                <option>1 hour</option>
              </select>
            </div>
          </div>
        </div>
        <div className="widget">
          <h3>Alert Settings</h3>
          <div className="settings-section">
            <div className="setting-item">
              <label>Email Alerts</label>
              <input type="checkbox" defaultChecked />
            </div>
            <div className="setting-item">
              <label>SMS Alerts</label>
              <input type="checkbox" />
            </div>
            <div className="setting-item">
              <label>Alert Threshold</label>
              <select className="setting-input">
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
                <option>Critical</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      </div>
    </main>
  );
};

export default Settings;
