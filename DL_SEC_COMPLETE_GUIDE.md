# DL-SEC Complete Integration Guide

## 🎯 Project Overview

DL-SEC is a complete deep learning-based cybersecurity threat detection system that:
- Uses a trained TensorFlow/Keras CNN-LSTM model to detect threats in real-time
- Processes datasets (CSV/Excel) or live API data streams
- Provides a React dashboard for real-time monitoring
- Suggests automated response actions based on threat type and severity
- Streams detection results via WebSocket for live updates

## 🏗️ Architecture

```
┌─────────────────┐
│   React Frontend │  ← Real-time Dashboard
│   (Port 5173)    │
└────────┬─────────┘
         │ HTTP/WebSocket
         ↓
┌─────────────────┐
│  Flask Backend  │  ← API Server
│  (Port 5000)    │
└────────┬─────────┘
         │
         ├──→ Model Service (TensorFlow/Keras)
         ├──→ Dataset Service (CSV/Excel Processing)
         ├──→ Data Simulator (Real-time Streaming)
         ├──→ Action Service (Response Recommendations)
         └──→ Database (SQLite - Threats & Actions)
```

## 📁 Project Structure

```
dlsec2db/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration settings
│   ├── routes/
│   │   ├── threats.py         # Threat detection endpoints
│   │   ├── actions.py         # Action execution endpoints
│   │   ├── model.py           # Model status endpoints
│   │   └── dataset.py         # Dataset processing endpoints
│   ├── services/
│   │   ├── model_service.py   # ML model inference service
│   │   ├── dataset_service.py # Dataset loading & processing
│   │   ├── data_simulator.py  # Real-time data streaming
│   │   └── action_service.py  # Action recommendation engine
│   ├── database/
│   │   ├── db.py              # Database initialization
│   │   └── models.py          # Database models (Threat, Action)
│   ├── models/                # Trained model files
│   │   ├── final_cnn_lstm.keras
│   │   └── scaler.pkl
│   ├── scripts/
│   │   └── load_test_dataset.py  # Dataset loading script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React app with routing
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── services/          # API & WebSocket services
│   │   └── styles/            # CSS styles
│   └── package.json
├── UNSW_NB15_training-set.csv # Training dataset
└── UNSW_NB15_testing-set.csv  # Testing dataset
```

## 🚀 Quick Start

### 1. Install Dependencies

#### Backend Dependencies
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate     # Linux/Mac

# Install Python packages
cd backend
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
# Install Node.js packages
npm install
cd frontend
npm install
```

### 2. Start the Servers

#### Option A: Start Both Servers (Recommended)
```bash
# From project root
npm start
```

#### Option B: Start Servers Separately
```bash
# Terminal 1 - Backend
.\.venv\Scripts\Activate.ps1
python backend\app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Access the Application

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Status**: http://localhost:5000/api/model/status

## 📊 Using the Dataset

### Load Test Dataset

#### Method 1: Using the Script
```bash
# Make sure backend server is running
python backend/scripts/load_test_dataset.py
```

#### Method 2: Using API
```bash
# Load dataset via API
curl -X POST http://localhost:5000/api/dataset/load \
  -H "Content-Type: application/json" \
  -d '{"file_path": "D:/dlsec2db/UNSW_NB15_testing-set.csv"}'
```

#### Method 3: Upload via Frontend
1. Open the dashboard at http://localhost:5173
2. Navigate to the Dataset page (to be implemented)
3. Upload your CSV/Excel file

### Process Dataset

#### Process Single Record
```bash
curl -X POST http://localhost:5000/api/dataset/process \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 1}'
```

#### Process Batch
```bash
curl -X POST http://localhost:5000/api/dataset/process \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 10}'
```

### Stream Dataset in Real-Time

#### Start Streaming
```bash
curl -X POST http://localhost:5000/api/dataset/stream/start \
  -H "Content-Type: application/json" \
  -d '{"interval": 2.0, "use_dataset": true}'
```

#### Stop Streaming
```bash
curl -X POST http://localhost:5000/api/dataset/stream/stop
```

#### Check Streaming Status
```bash
curl http://localhost:5000/api/dataset/stream/status
```

## 🔌 API Endpoints

### Threat Detection

- `POST /api/threats/detect` - Detect threat from network traffic data
- `GET /api/threats` - Get all threats (with optional filtering)
- `GET /api/threats/:id` - Get specific threat
- `GET /api/threats/:id/actions` - Get suggested actions for threat
- `PATCH /api/threats/:id` - Update threat status

### Actions

- `GET /api/actions/:id` - Get action details
- `POST /api/actions/:id/execute` - Execute an action
- `GET /api/actions/threat/:threat_id` - Get actions for a threat

### Model

- `GET /api/model/status` - Get model health and status
- `POST /api/model/predict` - Single prediction endpoint

### Dataset

- `POST /api/dataset/upload` - Upload dataset file
- `POST /api/dataset/load` - Load dataset from file path
- `GET /api/dataset/stats` - Get dataset statistics
- `GET /api/dataset/sample` - Get sample records
- `POST /api/dataset/process` - Process dataset records
- `POST /api/dataset/stream/start` - Start real-time streaming
- `POST /api/dataset/stream/stop` - Stop streaming
- `GET /api/dataset/stream/status` - Get streaming status
- `POST /api/dataset/reset` - Reset dataset stream

## 🔄 Real-Time Data Flow

### 1. Dataset Processing Flow
```
CSV/Excel File
    ↓
Dataset Service (Load & Clean)
    ↓
Model Service (Preprocess & Predict)
    ↓
Threat Detection (Create Threat Record)
    ↓
Action Service (Generate Recommended Actions)
    ↓
WebSocket (Emit to Frontend)
    ↓
React Dashboard (Display in Real-Time)
```

### 2. Live API Data Flow
```
Live API Data Stream
    ↓
Data Simulator (Generate/Stream Data)
    ↓
Model Service (Predict)
    ↓
Threat Detection
    ↓
Action Service
    ↓
WebSocket
    ↓
React Dashboard
```

## 🎨 Frontend Dashboard

### Pages

1. **Dashboard** (`/dashboard`) - Main dashboard with all widgets
2. **Real-Time Monitor** (`/monitor`) - Live network activity monitoring
3. **Threat Analytics** (`/analytics`) - Threat analysis and charts
4. **Model Insights** (`/insights`) - Model performance metrics
5. **Logs** (`/logs`) - System and security logs
6. **Settings** (`/settings`) - System configuration

### Components

- **AlertCenter** - Real-time threat alerts and actions
- **ThreatAnalytics** - Pie and line charts for threat analysis
- **RealTimeMonitoring** - Live network activity feed
- **RiskAssessment** - Risk level gauge and top risky IPs
- **ModelInsights** - Model performance metrics
- **ReportsLogs** - Reports and log history

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)

```python
# Model paths
MODEL_PATH = "backend/models/final_cnn_lstm.keras"
SCALER_PATH = "backend/models/scaler.pkl"

# Database
DATABASE_URI = "sqlite:///backend/threats.db"

# Categorical features
CATEGORICAL_COLS = ['proto', 'service', 'state']
```

### Frontend Configuration

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
```

## 📈 Threat Types & Actions

### Threat Types
- **DDoS** - Distributed Denial of Service attacks
- **Malware** - Malicious software detection
- **Brute Force** - Password brute force attempts
- **Exploit** - Vulnerability exploitation attempts
- **Reconnaissance** - Network scanning and reconnaissance
- **Suspicious Activity** - General suspicious behavior

### Action Types
- **block_ip** - Block source IP address
- **isolate** - Isolate affected system
- **alert_admin** - Alert security team
- **monitor** - Enhanced monitoring

### Action Priorities
- **High** - Immediate action required
- **Medium** - Action recommended
- **Low** - Monitor and log

## 🧪 Testing

### Test with Mock Data
```bash
# Start streaming with mock data
curl -X POST http://localhost:5000/api/dataset/stream/start \
  -H "Content-Type: application/json" \
  -d '{"interval": 2.0, "use_dataset": false}'
```

### Test with Real Dataset
```bash
# Load and process test dataset
python backend/scripts/load_test_dataset.py
```

### Test Single Prediction
```bash
curl -X POST http://localhost:5000/api/model/predict \
  -H "Content-Type: application/json" \
  -d '{
    "srcip": "192.168.1.100",
    "dstip": "10.0.0.1",
    "proto": "tcp",
    "service": "http",
    "state": "FIN"
  }'
```

## 🐛 Troubleshooting

### Model Not Loading
- Check if model files exist in `backend/models/`
- Verify model file paths in `backend/config.py`
- Check backend logs for errors

### Dataset Not Loading
- Verify CSV/Excel file path is correct
- Check file permissions
- Ensure file format matches expected schema

### WebSocket Connection Issues
- Verify backend server is running
- Check CORS settings in `backend/app.py`
- Ensure frontend is connecting to correct WebSocket URL

### Frontend Not Updating
- Check browser console for errors
- Verify WebSocket connection in browser DevTools
- Check backend logs for WebSocket events

## 📝 Notes

### Model Requirements
- The model expects specific feature columns (see `CATEGORICAL_COLS` in config)
- Preprocessing includes one-hot encoding and scaling
- Model outputs binary classification (0 = Normal, 1 = Threat)

### Dataset Requirements
- CSV or Excel format
- Must include network traffic features
- Optional: `attack_cat` column for threat type classification
- Optional: `label` column for binary classification

### Performance Considerations
- Model loading happens once at startup
- Dataset streaming can be configured with interval
- WebSocket events are emitted for each threat detection
- Database stores all threats and actions for history

## 🚀 Future Enhancements

1. **API Integration** - Connect to live network traffic APIs
2. **Multi-Model Support** - Support multiple models for different threat types
3. **Advanced Analytics** - Enhanced threat analysis and reporting
4. **Automated Response** - Automatic action execution based on rules
5. **User Authentication** - Add user authentication and authorization
6. **Dashboard Customization** - Customizable dashboard widgets
7. **Export Functionality** - Export threats and reports
8. **Email/SMS Alerts** - Send alerts via email or SMS

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend and frontend logs
3. Check API status endpoint: http://localhost:5000/api/model/status
4. Verify all dependencies are installed

## 📄 License

This project is part of the DL-SEC cybersecurity threat detection system.

