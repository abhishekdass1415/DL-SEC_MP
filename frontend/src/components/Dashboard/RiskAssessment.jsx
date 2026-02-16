import React from 'react';
import '../../styles/components.css';

const RiskAssessment = () => {
  const riskLevel = 72;
  const radius = 80;
  const circumference = 2 * Math.PI * radius;

  const lowPercentage = 60;
  const criticalPercentage = Math.max(0, riskLevel - lowPercentage);

  const lowArcLength = (lowPercentage / 100) * circumference;
  const criticalArcLength = (criticalPercentage / 100) * circumference;

  const riskyIPs = [
    { ip: '192.188.20.52', risk: 75 },
    { ip: '192.193.20.16', risk: 60 },
  ];

  return (
    <div className="widget risk-assessment">
      <h3>Risk Assessment</h3>
      <div className="risk-content">
        <div className="risk-gauge-container">
          <div className="risk-gauge">
            <svg viewBox="0 0 200 200" className="gauge-svg">
              <circle
                className="gauge-background"
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="#2a2a2a"
                strokeWidth="16"
              />
              <circle
                className="gauge-fill-low"
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="#4caf50"
                strokeWidth="16"
                strokeDasharray={`${lowArcLength} ${circumference}`}
                strokeDashoffset={circumference * 0.25}
                strokeLinecap="round"
              />
              <circle
                className="gauge-fill-critical"
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="#ff8800"
                strokeWidth="16"
                strokeDasharray={`${criticalArcLength} ${circumference}`}
                strokeDashoffset={circumference * 0.25 - lowArcLength}
                strokeLinecap="round"
              />
            </svg>
            <div className="gauge-value-text">{riskLevel}</div>
            <div className="gauge-labels">
              <span className="gauge-label-low">Low</span>
              <span className="gauge-label-critical">Critical</span>
            </div>
          </div>
        </div>
        <div className="risky-ips">
          <h4>Top 3 Risky IPs</h4>
          {riskyIPs.map((item, index) => (
            <div key={index} className="ip-risk">
              <span className="ip-address">{item.ip}</span>
              <div className="risk-bar-container">
                <div
                  className="risk-bar"
                  style={{ width: `${item.risk}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessment;


