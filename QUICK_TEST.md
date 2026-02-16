# ⚡ Quick Test Guide - DL-SEC

## 🚀 Fast Testing (5 Minutes)

### Step 1: Start Servers (30 seconds)
```bash
npm start
```
Wait for both servers to show "ready"

### Step 2: Open Dashboard (10 seconds)
Open: **http://localhost:5173**

**Check:**
- ✅ Dashboard loads
- ✅ All widgets visible
- ✅ No console errors (F12)

### Step 3: Load Dataset (30 seconds)
1. Find **Dataset Manager** widget
2. Click **"Load Test Dataset"**
3. Enter: `D:\dlsec2db\UNSW_NB15_testing-set.csv`
4. Click OK

**Check:**
- ✅ Success message appears
- ✅ Statistics show record count

### Step 4: Start Streaming (10 seconds)
1. Set interval: 2.0 seconds
2. Click **"Start Streaming"**

**Check:**
- ✅ Status shows "● Streaming Active"

### Step 5: Watch Real-Time Detection (2 minutes)
**Watch for:**
- ✅ Threats appearing in Alert Center
- ✅ Charts updating in Threat Analytics
- ✅ Activity bars updating
- ✅ Risk levels changing

### Step 6: Test Actions (30 seconds)
1. Click on a threat
2. Click "Execute" on an action
3. Verify action executes

**Check:**
- ✅ Action status updates
- ✅ Checkmark appears

### Step 7: Stop Streaming (10 seconds)
1. Click **"Stop Streaming"**

**Check:**
- ✅ Status shows "○ Streaming Stopped"
- ✅ No new threats appear

---

## ✅ Success Indicators

- ✅ Dashboard loads without errors
- ✅ Dataset loads successfully
- ✅ Streaming starts and stops
- ✅ Threats appear in real-time
- ✅ Actions can be executed
- ✅ All widgets update correctly

---

## 🐛 Quick Troubleshooting

**Backend not starting?**
- Check port 5000 is free
- Verify virtual environment is activated
- Check: `pip install -r backend/requirements.txt`

**Frontend not loading?**
- Check port 5173 is free
- Verify: `npm install` and `cd frontend && npm install`

**Dataset not loading?**
- Verify file path is correct
- Check file exists and is readable
- Use absolute path: `D:\dlsec2db\UNSW_NB15_testing-set.csv`

**No threats detected?**
- Check model status: http://localhost:5000/api/model/status
- If model not loaded, system uses mock predictions
- Verify dataset contains threat records

**WebSocket not connecting?**
- Check browser console (F12)
- Verify backend is running
- Check CORS settings

---

## 📊 Expected Results

After 2 minutes of streaming:
- ✅ 5-10 threats detected (depending on dataset)
- ✅ Charts show threat distribution
- ✅ Alert Center shows active threats
- ✅ Actions are suggested for each threat
- ✅ Database contains threat records

---

## 🎯 Test Complete!

If all checks pass, your system is working correctly! 🎉

For detailed testing, see: `COMPLETE_TESTING_CHECKLIST.md`

