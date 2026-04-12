import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import '../../styles/components.css';
import { useThreats } from '../../context/ThreatContext';
import { analyticsAPI } from '../../services/api';

const COLORS = ['#ff8800', '#00bcd4', '#ffb300', '#4caf50', '#ff4444'];

const ThreatAnalytics = () => {
  const { threats } = useThreats();
  const [pieData, setPieData] = useState([{ name: 'Loading...', value: 1 }]);
  const [lineData, setLineData] = useState([]);

  useEffect(() => {
    let isMounted = true;
    const load = async () => {
      try {
        const response = await analyticsAPI.getSummary();
        if (!isMounted) return;
        const data = response.data || {};
        const byType = data.byType && data.byType.length ? data.byType : [{ name: 'No Data', value: 1 }];
        const overTime = (data.overTime || []).map((pt) => ({
          name: new Date(pt.time).toLocaleTimeString('en-US', { hour: '2-digit' }),
          threats: pt.threats,
        }));
        setPieData(byType);
        setLineData(overTime);
      } catch (err) {
        // Fallback to client-side aggregation from threats list
        const counts = threats.reduce((acc, t) => {
          const key = t.threat_type || 'Unknown';
          acc[key] = (acc[key] || 0) + 1;
          return acc;
        }, {});
        const entries = Object.entries(counts).map(([name, value]) => ({ name, value }));
        setPieData(entries.length ? entries : [{ name: 'No Data', value: 1 }]);

        const buckets = threats.reduce((acc, t) => {
          const label = new Date(t.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
          acc[label] = (acc[label] || 0) + 1;
          return acc;
        }, {});
        // Sort by time key to maintain graph timeline order
        const sortedBuckets = Object.entries(buckets).sort(([a], [b]) => a.localeCompare(b));
        setLineData(sortedBuckets.map(([name, threats]) => ({ name, threats })));
      }
    };
    load();
    const interval = setInterval(load, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [threats]);

  return (
    <div className="widget threat-analytics">
      <h3>Threat Analytics Dashboard</h3>
      <div className="analytics-content">
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} dataKey="value" label>
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="line-chart-container">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={lineData}>
              <XAxis dataKey="name" stroke="#666" />
              <YAxis stroke="#666" allowDecimals={false} />
              <Line type="monotone" dataKey="threats" stroke="#00bcd4" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
          <p className="chart-label mt-4 text-center text-gray-400">Number of Threats Detected (Per Minute)</p>
        </div>
      </div>
    </div>
  );
};

export default ThreatAnalytics;


