# DL-SEC Quick Start Guide

## 🚀 Start the Complete System

### Step 1: Install Dependencies (if not already installed)

```bash
# Backend dependencies
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Frontend dependencies
npm install
cd frontend
npm install
cd ..
```

### Step 2: Start Both Servers

```bash
# From project root - starts both frontend and backend
npm start
```

This will start:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:5173

### Step 3: Load Test Dataset

Open a new terminal and run:

```bash
python backend/scripts/load_test_dataset.py
```

Or use the API directly:

```bash
curl -X POST http://localhost:5000/api/dataset/load \
  -H "Content-Type: application/json" \
  -d "{\"file_path\": \"$(pwd)/UNSW_NB15_testing-set.csv\"}"
```

### Step 4: Start Real-Time Streaming

```bash
curl -X POST http://localhost:5000/api/dataset/stream/start \
  -H "Content-Type: application/json" \
  -d '{"interval": 2.0, "use_dataset": true}'
```

### Step 5: View Dashboard

Open your browser and go to: **http://localhost:5173**

You should see:
- Real-time threat detections
- Threat analytics charts
- Suggested actions
- System logs

## 📊 Quick API Tests

### Check Model Status
```bash
curl http://localhost:5000/api/model/status
```

### Get Dataset Statistics
```bash
curl http://localhost:5000/api/dataset/stats
```

### Process Single Record
```bash
curl -X POST http://localhost:5000/api/dataset/process \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 1}'
```

### Get Streaming Status
```bash
curl http://localhost:5000/api/dataset/stream/status
```

### Stop Streaming
```bash
curl -X POST http://localhost:5000/api/dataset/stream/stop
```

## 🎯 Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/model/status` | GET | Check model status |
| `/api/dataset/load` | POST | Load dataset from file |
| `/api/dataset/stats` | GET | Get dataset statistics |
| `/api/dataset/process` | POST | Process dataset records |
| `/api/dataset/stream/start` | POST | Start real-time streaming |
| `/api/dataset/stream/stop` | POST | Stop streaming |
| `/api/threats` | GET | Get all threats |
| `/api/threats/detect` | POST | Detect threat from data |

## 🔍 Verify Everything is Working

1. **Check Backend**: http://localhost:5000/api/model/status
2. **Check Frontend**: http://localhost:5173
3. **Check WebSocket**: Open browser console and look for WebSocket connection
4. **Check Database**: Check `backend/threats.db` for stored threats

## 🐛 Troubleshooting

### Backend Not Starting
- Check if port 5000 is available
- Verify virtual environment is activated
- Check if all dependencies are installed

### Frontend Not Loading
- Check if port 5173 is available
- Verify Node.js dependencies are installed
- Check browser console for errors

### Dataset Not Loading
- Verify file path is correct
- Check file permissions
- Ensure file is CSV or Excel format

### WebSocket Not Connecting
- Verify backend is running
- Check CORS settings
- Verify WebSocket URL in frontend

## 📝 Next Steps

1. Load your test dataset
2. Start streaming
3. Monitor the dashboard
4. View detected threats
5. Execute suggested actions

## 🎉 You're Ready!

Your DL-SEC system is now running and ready to detect threats in real-time!

For more details, see:
- `DL_SEC_COMPLETE_GUIDE.md` - Complete documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details

