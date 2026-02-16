import React, { useEffect, useMemo, useState } from 'react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import '../../styles/components.css';
import { threatAPI } from '../../services/api';
import { initSocket } from '../../services/socket';

const COLORS = ['#ff8800', '#00bcd4', '#ffb300', '#4caf50', '#ff4444'];

const ThreatAnalytics = () => {
  const [threats, setThreats] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await threatAPI.getThreats({ limit: 100 });
        setThreats(res.data.threats || []);
      } catch {
        setThreats([]);
      }
    };
    load();
    const socket = initSocket();
    socket.on('new_threat', () => load());
    socket.on('threat_updated', () => load());
    return () => {
      socket.off('new_threat');
      socket.off('threat_updated');
    };
  }, []);

  const pieData = useMemo(() => {
    const counts = threats.reduce((acc, t) => {
      const key = t.threat_type || 'Unknown';
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});
    const entries = Object.entries(counts).map(([name, value]) => ({ name, value }));
    return entries.length ? entries : [{ name: 'No Data', value: 1 }];
  }, [threats]);

  const lineData = useMemo(() => {
    const buckets = threats.reduce((acc, t) => {
      const label = new Date(t.timestamp).toLocaleTimeString('en-US', { hour: '2-digit' });
      acc[label] = (acc[label] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(buckets).map(([name, threats]) => ({ name, threats }));
  }, [threats]);

  return (
    <div className="widget threat-analytics">
      <h3>Threat Analytics</h3>
      <div className="analytics-content">
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={150}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} dataKey="value">
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="line-chart-container">
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={lineData}>
              <XAxis dataKey="name" hide />
              <YAxis hide />
              <Line type="monotone" dataKey="threats" stroke="#00bcd4" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
          <p className="chart-label">Number of Threats Over Time</p>
        </div>
      </div>
      <div className="analytics-buttons">
        <button>Top 5 Sources</button>
        <button>Detection Rate &gt;</button>
      </div>
    </div>
  );
};

export default ThreatAnalytics;


