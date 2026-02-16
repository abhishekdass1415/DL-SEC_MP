# 🚀 Quick Start Guide - Backend Server

## The Problem
Your frontend dashboard is running, but it can't connect to the backend server because the backend isn't running. This is why you can't:
- Upload datasets
- Connect to APIs
- Analyze data with AI/ML models
- Perform threat detection

## ✅ Solution: Start the Backend Server

### Method 1: Using the Startup Script (Easiest)

**Double-click or run:**
```powershell
.\start_backend.bat
```

**OR in PowerShell:**
```powershell
.\start_backend.ps1
```

### Method 2: Manual Start

1. **Open a new PowerShell terminal** (keep your frontend running in another terminal)

2. **Navigate to project root:**
```powershell
cd D:\DL-SEC_MP
```

3. **Activate virtual environment:**
```powershell
.\.venv\Scripts\Activate.ps1
```

4. **Navigate to backend:**
```powershell
cd backend
```

5. **Start the server:**
```powershell
python app.py
```

You should see:
```
==================================================
  Threat Detection Backend Server
==================================================
Backend API: http://localhost:5000
WebSocket: ws://localhost:5000
API Status: http://localhost:5000/api/model/status
==================================================
Press CTRL+C to stop the server
==================================================
```

### Method 3: Using npm Script

From project root:
```powershell
npm run start:backend
```

## ✅ Verify Backend is Running

1. **Check the backend terminal** - you should see the server startup messages
2. **Open in browser:** http://localhost:5000/api/model/status
   - Should return JSON with model status
3. **Check frontend console** - errors should disappear and data should load

## 🔧 Troubleshooting

### Backend won't start?

1. **Check if port 5000 is already in use:**
```powershell
netstat -ano | findstr :5000
```
If something is using port 5000, close it or change the port in `backend/app.py`

2. **Check virtual environment:**
```powershell
.\.venv\Scripts\Activate.ps1
python --version
```

3. **Reinstall dependencies:**
```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

4. **Check for Python errors:**
   - Look at the backend terminal window for error messages
   - Common issues: missing dependencies, model files not found

### Still having issues?

- Make sure Python 3.8+ is installed
- Make sure all dependencies in `backend/requirements.txt` are installed
- Check that the virtual environment is activated (you should see `(.venv)` in your terminal prompt)

## 📝 Important Notes

- **Keep both terminals open:**
  - Terminal 1: Frontend (npm run dev) - usually on port 5173
  - Terminal 2: Backend (python app.py) - on port 5000

- **The backend must be running** for the frontend to work properly
- **Don't close the backend terminal** - that will stop the server
- **Press CTRL+C** in the backend terminal to stop the server gracefully

## 🎯 What Should Happen

Once the backend is running:
1. ✅ Frontend console errors disappear
2. ✅ You can upload datasets
3. ✅ You can connect to APIs
4. ✅ Threat detection works
5. ✅ AI/ML model analysis works
6. ✅ Real-time monitoring works

---

**Need help?** Check the backend terminal window for any error messages and share them for troubleshooting.

