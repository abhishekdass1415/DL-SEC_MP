# Complete Setup Guide

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- Virtual environment created (`.venv` folder)

## Step 1: Create Virtual Environment (if not already created)

```powershell
# From project root
python -m venv .venv
```

## Step 2: Install Backend Dependencies

### Option A: Using the startup script (Recommended)
```powershell
# Double-click or run:
start_backend.bat
# OR
.\start_backend.ps1
```

### Option B: Manual installation
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Add Your Model Files

Place your trained model files in `backend/models/`:

```
backend/models/
├── final_cnn_lstm.keras  (or your model filename)
└── scaler.pkl
```

**Note:** If model files are not present, the system will run in "mock mode" for development/testing.

## Step 4: Install Frontend Dependencies

```powershell
# From project root
npm install
```

## Step 5: Start the Servers

### Terminal 1 - Backend Server
```powershell
# Option A: Use startup script
.\start_backend.bat
# OR
.\start_backend.ps1

# Option B: Manual start
.\.venv\Scripts\Activate.ps1
cd backend
python app.py
```

Backend will run on: `http://localhost:5000`

### Terminal 2 - Frontend Server
```powershell
# Option A: Use startup script
.\start_frontend.bat
# OR
.\start_frontend.ps1

# Option B: Manual start
npm run dev
```

Frontend will run on: `http://localhost:5173` (or similar)

## Step 6: Access the Dashboard

Open your browser and navigate to:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000/api/model/status`

## Troubleshooting

### Backend won't start
1. **Check virtual environment is activated:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Verify dependencies are installed:**
   ```powershell
   pip list | findstr Flask
   ```

3. **Check Python version:**
   ```powershell
   python --version  # Should be 3.8+
   ```

### ModuleNotFoundError
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port already in use
- Change port in `backend/app.py` (line 49)
- Or stop the process using port 5000

### Model not loading
- Check model files exist in `backend/models/`
- Verify file paths in `backend/config.py`
- System will run in mock mode if files not found (this is OK for testing)

### Frontend can't connect to backend
- Ensure backend is running on port 5000
- Check browser console for CORS errors
- Verify API URL in `src/services/api.js`

## Testing the Integration

### Test Backend API
```powershell
# Check model status
curl http://localhost:5000/api/model/status

# Test threat detection (PowerShell)
$body = @{
    srcip = "192.168.1.100"
    dstip = "192.168.1.200"
    proto = "tcp"
    service = "http"
    state = "FIN"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/threats/detect" -Method Post -Body $body -ContentType "application/json"
```

### Test Frontend
1. Open browser to `http://localhost:5173`
2. Check AlertCenter component loads
3. Send a test threat detection request
4. Verify threats appear with suggested actions

## Project Structure

```
dlsec2db/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main application
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── models/             # Place model files here
│   ├── start_server.bat    # Windows startup script
│   ├── start_server.ps1    # PowerShell startup script
│   ├── database/           # Database models
│   ├── routes/             # API endpoints
│   └── services/           # Business logic
├── src/                    # React frontend
│   ├── components/        # React components
│   └── services/          # API clients
├── start_backend.bat      # Root level backend starter
├── start_backend.ps1      # Root level backend starter
├── start_frontend.bat     # Frontend starter
└── start_frontend.ps1     # Frontend starter
```

## Next Steps

1. **Add your model files** to `backend/models/`
2. **Customize action rules** in `backend/services/action_service.py`
3. **Update threat types** based on your model output
4. **Enhance UI** components as needed

For more details, see:
- `QUICKSTART.md` - Quick reference
- `README_INTEGRATION.md` - Detailed integration docs

