# 🚀 Quick Fix for "This site can't be reached"

## ⚡ Fast Solution

### 1. Install Frontend Dependencies (REQUIRED)
```powershell
cd frontend
npm install
cd ..
```

### 2. Check What's Running
```powershell
.\check-servers.ps1
```

This will show you:
- ✅ Which ports are available
- ✅ Which dependencies are installed
- ✅ What's missing

### 3. Start Servers

**Option A: Start Both Together**
```powershell
npm start
```

**Option B: Start Separately (if Option A fails)**

Terminal 1 - Backend:
```powershell
npm run start:backend
```

Terminal 2 - Frontend:
```powershell
npm run start:frontend
```

### 4. Open Browser

After servers start, you should see:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:5000

The browser should **automatically open** to http://localhost:5173

## 🔍 What to Look For

When `npm start` runs successfully, you should see:

```
[FRONTEND] VITE v5.x.x  ready in xxx ms
[FRONTEND] ➜  Local:   http://localhost:5173/

[BACKEND] ==================================================
[BACKEND]   Threat Detection Backend Server
[BACKEND] ==================================================
[BACKEND] Backend API: http://localhost:5000
```

## ❌ Common Issues

### Issue 1: "Failed to resolve import framer-motion"
**Fix:**
```powershell
cd frontend
npm install
```

### Issue 2: Port already in use
**Fix:** Close the application using port 5173 or 5000

### Issue 3: Backend not starting
**Fix:**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### Issue 4: White screen in browser
**Fix:** Check browser console (F12) for errors. Usually means dependencies aren't installed.

## ✅ Success Checklist

- [ ] Frontend dependencies installed (`cd frontend && npm install`)
- [ ] Backend dependencies installed (in virtual environment)
- [ ] Both servers showing in terminal
- [ ] No error messages
- [ ] Browser opens to http://localhost:5173
- [ ] Dashboard loads (not white screen)

## 🆘 Still Not Working?

Run the diagnostic:
```powershell
.\check-servers.ps1
```

Then share the output with me!

