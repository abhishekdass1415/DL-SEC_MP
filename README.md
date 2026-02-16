# DL-SEC Dashboard

A modern cybersecurity dashboard built with React.js, featuring real-time threat monitoring, analytics, and risk assessment. **Now integrated with AI/ML threat detection model!**

## Features

- **Alert Center**: Real-time security alerts with threat classification and model-suggested actions
- **Threat Detection**: AI/ML-powered threat detection using CNN-LSTM model
- **Action Management**: Execute model-suggested actions directly from the dashboard
- **Threat Analytics**: Visual analytics with pie charts and trend graphs
- **Real-Time Monitoring**: Live network activity feed and traffic volume monitoring
- **Model Insights**: ML model performance metrics (CNN-LSTM)
- **Risk Assessment**: Circular gauge showing risk levels and top risky IPs
- **Reports & Logs**: Export and view security logs
- **WebSocket Integration**: Real-time threat updates via WebSocket

## Tech Stack

### Frontend
- React.js 18
- Vite (Build tool)
- Recharts (Data visualization)
- Lucide React (Icons)
- Axios (HTTP client)
- Socket.io-client (WebSocket)

### Backend
- Flask (Python web framework)
- TensorFlow/Keras (ML model)
- SQLAlchemy (Database ORM)
- Flask-SocketIO (WebSocket support)
- scikit-learn (Preprocessing)

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Place your model files in `backend/models/`:
   - `final_cnn_lstm.keras` (or your model file)
   - `scaler.pkl`

3. Start the backend server:
```bash
python app.py
```

Backend runs on `http://localhost:5000`

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

Frontend runs on `http://localhost:5173` (or similar)

## Project Structure

```
dl-sec2db/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── models/             # Place your model files here
│   │   ├── final_cnn_lstm.keras
│   │   └── scaler.pkl
│   ├── database/          # Database models and setup
│   ├── routes/            # API endpoints
│   └── services/          # Business logic (model, actions)
├── src/                    # React frontend
│   ├── components/
│   │   ├── Layout/
│   │   └── Dashboard/
│   │       ├── AlertCenter.jsx  # Integrated with backend
│   │       ├── ThreatAnalytics.jsx
│   │       ├── RealTimeMonitoring.jsx
│   │       ├── ReportsLogs.jsx
│   │       ├── ModelInsights.jsx
│   │       └── RiskAssessment.jsx
│   ├── services/          # API and WebSocket clients
│   │   ├── api.js
│   │   └── socket.js
│   └── styles/
├── index.html
├── package.json
└── vite.config.js
```

## Integration Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [README_INTEGRATION.md](README_INTEGRATION.md) - Detailed integration documentation

## Color Scheme

- Background: `#1a1a1a` (Main background)
- Sidebar: `#1f1f1f` (Sidebar background)
- Content: `#252525` (Content area)
- Widgets: `#2a2a2a` (Widget background)
- Borders: `#333` (Border color)
- Primary Accent: `#00bcd4` (Cyan)
- Success: `#4caf50` (Green)
- Warning: `#ff8800` (Orange)
- Danger: `#ff4444` (Red)

## License

MIT

