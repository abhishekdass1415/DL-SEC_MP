import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './styles/App.css';
import './index.css';
import { ThreatProvider } from './context/ThreatContext.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThreatProvider>
      <App />
    </ThreatProvider>
  </React.StrictMode>,
);

