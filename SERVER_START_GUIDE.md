# 🚀 Server Start Guide

## ✅ What Just Happened

1. **Dependencies Installed**: All frontend packages (framer-motion, zustand, tailwindcss, etc.) are now installed
2. **Servers Starting**: Both frontend and backend servers are starting in the background

## 🔍 How to Verify Servers Are Running

### Check Terminal Output

You should see output like this:

```
[FRONTEND] 
[FRONTEND]   VITE v5.x.x  ready in xxx ms
[FRONTEND] 
[FRONTEND]   ➜  Local:   http://localhost:5173/
[FRONTEND]   ➜  Network: use --host to expose
[FRONTEND]   ➜  press h to show help
[FRONTEND] 

[BACKEND] ==================================================
[BACKEND]   Threat Detection Backend Server
[BACKEND] ==================================================
[BACKEND] Backend API: http://localhost:5000
[BACKEND] WebSocket: ws://localhost:5000
[BACKEND] API Status: http://localhost:5000/api/model/status
[BACKEND] ==================================================
```

### Check in Browser

1. **Wait 10-15 seconds** for servers to fully start
2. **Open browser** and go to: **http://localhost:5173**
3. You should see the dashboard (not a white screen or error)

### Test Backend API

Open in browser: **http://localhost:5000/api/model/status**

You should see JSON response like:
```json
{
  "status": "ready",
  "model_loaded": true,
  ...
}
```

## 🐛 If Servers Didn't Start

### Option 1: Start Manually (Recommended)

**Terminal 1 - Frontend:**
```powershell
.\test-frontend-only.ps1
```

**Terminal 2 - Backend:**
```powershell
.\test-backend-only.ps1
```

### Option 2: Use the Manual Script
```powershell
.\start-servers-manually.ps1
```

### Option 3: Start Separately

**Terminal 1:**
```powershell
npm run start:frontend
```

**Terminal 2:**
```powershell
npm run start:backend
```

## 🔧 Troubleshooting

### Issue: Still seeing "ERR_CONNECTION_REFUSED"

**Check 1: Are servers actually running?**
- Look at your terminal - do you see the Vite and Flask startup messages?
- If not, there's an error preventing startup

**Check 2: Port conflicts**
```powershell
netstat -ano | findstr :5173
netstat -ano | findstr :5000
```
If ports are in use, close those applications

**Check 3: Dependencies**
```powershell
cd frontend
npm list framer-motion
```
Should show version number, not "empty"

**Check 4: Virtual Environment**
```powershell
.\.venv\Scripts\Activate.ps1
python -c "import flask; print('OK')"
```
Should print "OK"

### Issue: White Screen in Browser

1. **Open Browser Console** (F12)
2. **Check for errors** in Console tab
3. **Common errors:**
   - "Failed to resolve import" → Dependencies not installed
   - "Cannot find module" → Missing package
   - Network errors → Backend not running

### Issue: Backend Not Starting

**Check Python/Flask:**
```powershell
.\.venv\Scripts\Activate.ps1
pip list | findstr flask
```

If Flask is not listed:
```powershell
pip install -r backend/requirements.txt
```

## 📋 Quick Checklist

- [ ] Dependencies installed? (`cd frontend && npm install` - DONE ✅)
- [ ] Frontend server showing in terminal? (Check for Vite message)
- [ ] Backend server showing in terminal? (Check for Flask message)
- [ ] Ports 5173 and 5000 available?
- [ ] Browser opens to http://localhost:5173?
- [ ] Dashboard loads (not white screen)?

## 🎯 Expected Result

When everything works:

1. **Terminal shows both servers running**
2. **Browser automatically opens** to http://localhost:5173
3. **Dashboard displays** with:
   - Header with status indicator
   - Sidebar navigation
   - Dashboard widgets
   - No console errors (F12 → Console tab)

## 🆘 Still Not Working?

**Share with me:**
1. Terminal output from `npm start`
2. Browser console errors (F12 → Console)
3. Output from `.\check-servers.ps1`

I'll help you fix it!

