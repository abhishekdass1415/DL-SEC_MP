# Quick Start Guide

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- Your trained model files (`.keras` or `.h5` and `scaler.pkl`)

## Step 1: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create models directory if it doesn't exist
mkdir -p models

# Copy your model files here:
# - final_cnn_lstm.keras (or your model file)
# - scaler.pkl
```

## Step 2: Start Backend Server

```bash
# From backend directory
python app.py

# Or use the run script
python run.py
```

Backend will start on `http://localhost:5000`

## Step 3: Setup Frontend

```bash
# From project root
npm install
```

## Step 4: Start Frontend

```bash
# From project root
npm run dev
```

Frontend will start on `http://localhost:5173` (or similar)

## Step 5: Test Integration

1. Open the frontend dashboard in your browser
2. The AlertCenter should show "No active threats" initially
3. To test threat detection, send a POST request to the API:

```bash
curl -X POST http://localhost:5000/api/threats/detect \
  -H "Content-Type: application/json" \
  -d '{
    "srcip": "192.168.1.100",
    "dstip": "192.168.1.200",
    "proto": "tcp",
    "service": "http",
    "state": "FIN"
  }'
```

Or use the browser console:

```javascript
fetch('http://localhost:5000/api/threats/detect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    srcip: '192.168.1.100',
    dstip: '192.168.1.200',
    proto: 'tcp',
    service: 'http',
    state: 'FIN'
  })
}).then(r => r.json()).then(console.log);
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (should be 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check if port 5000 is available

### Model not loading
- Verify model file exists in `backend/models/`
- Check file paths in `backend/config.py`
- System will run in "mock mode" if model not found (for development)

### Frontend can't connect
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify CORS is enabled (already configured)

### No threats showing
- Check backend logs for errors
- Verify database is created (`threats.db` in backend directory)
- Try sending a test threat detection request

## Next Steps

1. **Add your model files** to `backend/models/`
2. **Customize action rules** in `backend/services/action_service.py`
3. **Update threat types** in model service based on your model output
4. **Enhance UI** components as needed

For detailed documentation, see `README_INTEGRATION.md`

