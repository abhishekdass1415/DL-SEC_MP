import React from 'react';
import { Download } from 'lucide-react';
import '../../styles/components.css';

const ReportsLogs = () => {
  return (
    <div className="widget reports-logs">
      <h3>Reports & Logs</h3>
      <div className="reports-content">
        <button className="view-logs-btn">View Full Log History &gt;</button>
        <button className="export-btn">
          <Download size={16} />
          Export Report
        </button>
      </div>
    </div>
  );
};

export default ReportsLogs;


