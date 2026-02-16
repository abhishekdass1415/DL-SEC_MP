# Backend-Frontend Integration Guide

This guide explains how to integrate the ML model with the frontend dashboard.

## Project Structure

```
dlsec2db/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   ├── models/             # Place your model files here
│   │   ├── final_cnn_lstm.keras  # Your trained model
│   │   └── scaler.pkl      # Preprocessing scaler
│   ├── database/
│   │   ├── db.py           # Database initialization
│   │   └── models.py       # Database models
│   ├── routes/
│   │   ├── threats.py      # Threat detection endpoints
│   │   ├── actions.py      # Action management endpoints
│   │   └── model.py        # Model status endpoints
│   └── services/
│       ├── model_service.py    # Model inference service
│       └── action_service.py   # Action recommendation service
├── src/                    # React frontend
│   ├── components/
│   │   └── Dashboard/
│   │       └── AlertCenter.jsx  # Updated with API integration
│   └── services/
│       ├── api.js          # API client
│       └── socket.js       # WebSocket client
└── package.json            # Frontend dependencies
```

## Setup Instructions

### 1. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Place Model Files

Copy your trained model files to the `backend/models/` directory:

```bash
# Copy your model file (adjust filename as needed)
cp /path/to/your/final_cnn_lstm.keras backend/models/
cp /path/to/your/scaler.pkl backend/models/
```

#### Configure Environment

Create a `.env` file in the `backend/` directory (or use the example):

```bash
cp backend/.env.example backend/.env
```

Edit `.env` with your configuration:
```
DATABASE_URL=sqlite:///threats.db
MODEL_PATH=models/final_cnn_lstm.keras
SCALER_PATH=models/scaler.pkl
SECRET_KEY=your-secret-key-here
```

#### Run Backend Server

```bash
cd backend
python app.py
```

The backend will run on `http://localhost:5000`

### 2. Frontend Setup

#### Install Dependencies

```bash
npm install
```

#### Configure API URL (Optional)

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
```

#### Run Frontend

```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (or similar Vite port)

## API Endpoints

### Threat Detection

- `POST /api/threats/detect` - Detect threat from network traffic data
- `GET /api/threats` - Get all threats (with optional filters)
- `GET /api/threats/:id` - Get specific threat
- `GET /api/threats/:id/actions` - Get suggested actions for threat
- `PATCH /api/threats/:id` - Update threat status

### Actions

- `GET /api/actions/:id` - Get specific action
- `POST /api/actions/:id/execute` - Execute an action
- `GET /api/actions/threat/:id` - Get all actions for a threat

### Model

- `GET /api/model/status` - Get model health status
- `POST /api/model/predict` - Make a single prediction

## WebSocket Events

The backend emits the following WebSocket events:

- `new_threat` - When a new threat is detected
- `threat_updated` - When a threat status is updated
- `action_executed` - When an action is executed

## Usage Example

### Detecting a Threat

Send a POST request to `/api/threats/detect` with network traffic data:

```javascript
const response = await fetch('http://localhost:5000/api/threats/detect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    srcip: '192.168.1.100',
    dstip: '192.168.1.200',
    proto: 'tcp',
    service: 'http',
    state: 'FIN',
    // ... other network traffic features
  })
});
```

### Frontend Integration

The `AlertCenter` component automatically:
- Fetches threats from the API
- Connects to WebSocket for real-time updates
- Displays threats with suggested actions
- Allows executing actions and resolving threats

## Model Requirements

Your model should:
- Be saved as `.keras` or `.h5` file
- Accept input shape: `(samples, 1, n_features)` where n_features is typically 194
- Output binary classification (0 = Normal, 1 = Attack)
- Use MinMaxScaler for preprocessing (saved as `scaler.pkl`)

## Troubleshooting

### Model Not Loading

If the model file is not found, the system will run in "mock mode" with simulated predictions. Check:
1. Model file path in `config.py` or `.env`
2. File exists in `backend/models/` directory
3. File format is correct (`.keras` or `.h5`)

### CORS Errors

If you see CORS errors, ensure:
1. Backend CORS is configured (already set in `app.py`)
2. Frontend API URL matches backend URL

### WebSocket Connection Issues

If WebSocket doesn't connect:
1. Check backend is running
2. Verify `socket.io-client` is installed
3. Check browser console for connection errors

## Next Steps

1. **Add Model Files**: Place your trained model and scaler in `backend/models/`
2. **Test API**: Use Postman or curl to test endpoints
3. **Monitor Logs**: Check backend console for model loading and prediction logs
4. **Customize Actions**: Modify `action_service.py` to add custom action rules
5. **Enhance UI**: Update frontend components to show more threat details

## Development Notes

- The backend uses SQLite by default (can be changed to PostgreSQL)
- Model runs in mock mode if files are not found (for development)
- WebSocket provides real-time updates to all connected clients
- Actions are automatically generated based on threat type and severity

