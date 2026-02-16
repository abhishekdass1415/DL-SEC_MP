# 🔧 Troubleshooting Guide

## ❌ "This site can't be reached" Error

### Step 1: Check if Servers are Running

When you run `npm start`, you should see **TWO** terminal outputs:

1. **FRONTEND** (cyan color) - Should show:
   ```
   VITE v5.x.x  ready in xxx ms
   ➜  Local:   http://localhost:5173/
   ➜  Network: use --host to expose
   ```

2. **BACKEND** (magenta color) - Should show:
   ```
   ==================================================
     Threat Detection Backend Server
   ==================================================
   Backend API: http://localhost:5000
   WebSocket: ws://localhost:5000
   ```

### Step 2: Verify Installation

**Check if dependencies are installed:**

```powershell
cd frontend
npm list framer-motion zustand tailwindcss
```

If you see "empty" or errors, install dependencies:
```powershell
cd frontend
npm install
```

### Step 3: Check Port Availability

**Check if ports are in use:**

```powershell
# Check port 5173 (Frontend)
netstat -ano | findstr :5173

# Check port 5000 (Backend)
netstat -ano | findstr :5000
```

If ports are in use, you can:
- Kill the process using the port
- Or change the port in `vite.config.js` (frontend) or `app.py` (backend)

### Step 4: Start Servers Separately

If `npm start` doesn't work, try starting servers separately:

**Terminal 1 - Backend:**
```powershell
npm run start:backend
```

**Terminal 2 - Frontend:**
```powershell
npm run start:frontend
```

### Step 5: Check Browser URL

Make sure you're accessing:
- ✅ **Frontend**: http://localhost:5173
- ✅ **Backend API**: http://localhost:5000/api/model/status

**NOT:**
- ❌ http://localhost:3000 (wrong port)
- ❌ http://127.0.0.1:5173 (might work, but localhost is preferred)

### Step 6: Check Terminal for Errors

Look for error messages in the terminal:

**Common Errors:**

1. **"Failed to resolve import framer-motion"**
   ```powershell
   cd frontend
   npm install
   ```

2. **"ModuleNotFoundError: No module named 'flask'"**
   ```powershell
   # Activate virtual environment
   .\.venv\Scripts\Activate.ps1
   # Install backend dependencies
   pip install -r backend/requirements.txt
   ```

3. **"Port 5173 is already in use"**
   - Close other applications using port 5173
   - Or change port in `vite.config.js`

4. **"Port 5000 is already in use"**
   - Close other applications using port 5000
   - Or change port in `backend/app.py`

### Step 7: Clear Cache and Reinstall

If nothing works, try a clean install:

```powershell
# Frontend
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install

# Backend
.\.venv\Scripts\Activate.ps1
pip install --upgrade -r backend/requirements.txt
```

## 🔍 Diagnostic Commands

### Check if Frontend Server is Running
```powershell
curl http://localhost:5173
```

### Check if Backend Server is Running
```powershell
curl http://localhost:5000/api/model/status
```

### Check Node.js Version
```powershell
node --version
```
Should be v16+ or v18+

### Check Python Version
```powershell
python --version
```
Should be Python 3.8+

### Check if Virtual Environment is Active
```powershell
python -c "import sys; print(sys.prefix)"
```
Should show path to `.venv`

## 🚀 Quick Fix Checklist

- [ ] Dependencies installed? (`cd frontend && npm install`)
- [ ] Virtual environment activated? (`.\.venv\Scripts\Activate.ps1`)
- [ ] Backend dependencies installed? (`pip install -r backend/requirements.txt`)
- [ ] Ports 5173 and 5000 available?
- [ ] Using correct URL? (http://localhost:5173)
- [ ] Both servers showing in terminal?
- [ ] No error messages in terminal?

## 📞 Still Not Working?

1. **Check the terminal output** - Copy and share any error messages
2. **Check browser console** - Press F12, look for errors in Console tab
3. **Check network tab** - Press F12 → Network tab, see if requests are failing
4. **Try different browser** - Sometimes browser extensions cause issues
5. **Disable firewall/antivirus** - Temporarily disable to test

## ✅ Expected Behavior

When everything works correctly:

1. **Terminal shows:**
   ```
   [FRONTEND] VITE v5.x.x  ready in xxx ms
   [FRONTEND] ➜  Local:   http://localhost:5173/
   
   [BACKEND] ==================================================
   [BACKEND]   Threat Detection Backend Server
   [BACKEND] ==================================================
   [BACKEND] Backend API: http://localhost:5000
   ```

2. **Browser automatically opens** to http://localhost:5173

3. **Dashboard loads** with:
   - Header with status indicator
   - Sidebar navigation
   - Dashboard widgets
   - No console errors

## 🎯 Quick Start (Step by Step)

1. **Install Frontend Dependencies:**
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

2. **Activate Virtual Environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Backend Dependencies (if not done):**
   ```powershell
   pip install -r backend/requirements.txt
   ```

4. **Start Both Servers:**
   ```powershell
   npm start
   ```

5. **Open Browser:**
   - Should auto-open to http://localhost:5173
   - Or manually navigate to http://localhost:5173

If you still see errors, share the terminal output and I'll help you fix it!

