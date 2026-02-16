# Complete Project Setup - Threat Detection Dashboard

This is a complete, working integration of your CNN-LSTM threat detection model with a React frontend dashboard.

## 🚀 Quick Start

### 1. Install Backend Dependencies

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install Python packages
cd backend
pip install -r requirements.txt
```

### 2. Add Your Model Files

Copy your trained model to:
```
backend/models/final_cnn_lstm.keras
backend/models/scaler.pkl
```

### 3. Start Backend Server

**Option A: Use startup script (Easiest)**
```powershell
# From project root
.\start_backend.bat
# OR
.\start_backend.ps1
```

**Option B: Manual start**
```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python app.py
```

### 4. Install Frontend Dependencies

```powershell
# From project root
npm install
```

### 5. Start Frontend

**Option A: Use startup script**
```powershell
.\start_frontend.bat
# OR
.\start_frontend.ps1
```

**Option B: Manual start**
```powershell
npm run dev
```

### 6. Access Dashboard

- **Frontend Dashboard:** http://localhost:5173
- **Backend API:** http://localhost:5000
- **API Status:** http://localhost:5000/api/model/status

## 📁 Project Structure

```
dlsec2db/
├── backend/                    # Python Flask Backend
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # Place your model files here
│   │   ├── final_cnn_lstm.keras
│   │   └── scaler.pkl
│   ├── database/              # Database models
│   │   ├── db.py
│   │   └── models.py
│   ├── routes/                # API endpoints
│   │   ├── threats.py
│   │   ├── actions.py
│   │   └── model.py
│   ├── services/              # Business logic
│   │   ├── model_service.py   # Model inference
│   │   └── action_service.py  # Action recommendations
│   ├── start_server.bat       # Windows startup
│   └── start_server.ps1       # PowerShell startup
├── src/                       # React Frontend
│   ├── components/
│   │   └── Dashboard/
│   │       └── AlertCenter.jsx  # Main threat display
│   └── services/
│       ├── api.js            # API client
│       └── socket.js         # WebSocket client
├── start_backend.bat          # Root level backend starter
├── start_backend.ps1
├── start_frontend.bat         # Frontend starter
├── start_frontend.ps1
└── package.json              # Frontend dependencies
```

## 🔧 Features

### Backend Features
- ✅ Flask REST API with CORS support
- ✅ WebSocket for real-time updates
- ✅ SQLite database for threat storage
- ✅ Model inference service (CNN-LSTM)
- ✅ Automatic action recommendation
- ✅ Mock mode when model files not found

### Frontend Features
- ✅ Real-time threat display
- ✅ Model-suggested actions
- ✅ Execute actions from UI
- ✅ Resolve threats
- ✅ WebSocket integration
- ✅ Expandable threat details

## 📡 API Endpoints

### Threat Detection
- `POST /api/threats/detect` - Detect threat from network data
- `GET /api/threats` - Get all threats
- `GET /api/threats/:id` - Get specific threat
- `GET /api/threats/:id/actions` - Get actions for threat
- `PATCH /api/threats/:id` - Update threat status

### Actions
- `GET /api/actions/:id` - Get action details
- `POST /api/actions/:id/execute` - Execute action
- `GET /api/actions/threat/:id` - Get all actions for threat

### Model
- `GET /api/model/status` - Check model status
- `POST /api/model/predict` - Make prediction

## 🧪 Testing

### Test Backend

```powershell
# Check model status
Invoke-RestMethod -Uri "http://localhost:5000/api/model/status"

# Test threat detection
$body = @{
    srcip = "192.168.1.100"
    dstip = "192.168.1.200"
    proto = "tcp"
    service = "http"
    state = "FIN"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/threats/detect" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

### Test Frontend

1. Open http://localhost:5173
2. AlertCenter should show "No active threats"
3. Send test threat detection request
4. Threat should appear with suggested actions

## 🐛 Troubleshooting

### Backend Issues

**ModuleNotFoundError: No module named 'flask'**
- Solution: Activate virtual environment first
```powershell
.\.venv\Scripts\Activate.ps1
```

**Port 5000 already in use**
- Solution: Change port in `backend/app.py` line 49

**Model not loading**
- Check files exist in `backend/models/`
- System runs in mock mode if files not found (OK for testing)

### Frontend Issues

**Can't connect to backend**
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify CORS is enabled (already configured)

**npm install fails**
- Clear cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

## 📝 Configuration

### Backend Configuration

Edit `backend/config.py`:
- Database path
- Model file paths
- Feature columns

### Frontend Configuration

Edit `src/services/api.js`:
- API base URL (default: http://localhost:5000/api)
- WebSocket URL (default: http://localhost:5000)

Or create `.env` file:
```
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
```

## 🎯 Next Steps

1. **Add your model files** to `backend/models/`
2. **Customize action rules** in `backend/services/action_service.py`
3. **Update threat types** in `backend/services/model_service.py`
4. **Enhance UI** components as needed
5. **Add authentication** if needed
6. **Deploy to production** when ready

## 📚 Documentation

- `SETUP.md` - Detailed setup instructions
- `QUICKSTART.md` - Quick reference guide
- `README_INTEGRATION.md` - Integration details
- `README.md` - Main project documentation

## ✅ What's Working

- ✅ Backend Flask server
- ✅ Model loading and inference
- ✅ Database models and storage
- ✅ API endpoints
- ✅ WebSocket real-time updates
- ✅ Frontend React components
- ✅ API integration
- ✅ Action execution
- ✅ Threat management

## 🎉 You're All Set!

The project is complete and ready to use. Just add your model files and start both servers!

