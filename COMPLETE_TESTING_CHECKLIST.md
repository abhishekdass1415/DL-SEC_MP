# 🧪 Complete Testing Checklist for DL-SEC

## Step-by-Step Testing Guide

### ✅ Phase 1: Server Startup Verification

#### 1.1 Start the Servers
```bash
# From project root
npm start
```

**Expected Output:**
- [BACKEND] Flask server starting on port 5000
- [FRONTEND] Vite dev server starting on port 5173
- Both servers should show "ready" messages

**Check:**
- [ ] Backend shows: "Threat Detection Backend Server"
- [ ] Backend shows: "Running on http://127.0.0.1:5000"
- [ ] Frontend shows: "Local: http://localhost:5173/"
- [ ] No error messages in terminal

#### 1.2 Verify Backend API
Open in browser or use curl:
```
http://localhost:5000/api/model/status
```

**Expected Response:**
```json
{
  "model_loaded": true/false,
  "scaler_loaded": true/false,
  "status": "ready" or "mock_mode",
  "message": "..."
}
```

**Check:**
- [ ] API responds with status 200
- [ ] JSON response is valid
- [ ] Status field is present

#### 1.3 Verify Frontend
Open in browser:
```
http://localhost:5173
```

**Expected:**
- [ ] Dashboard loads without errors
- [ ] All widgets are visible
- [ ] No console errors in browser DevTools (F12)
- [ ] Sidebar navigation works

---

### ✅ Phase 2: Dashboard Visual Verification

#### 2.1 Check Dashboard Layout
On the dashboard page, verify:

- [ ] **Dataset Manager** widget is visible (top of dashboard)
- [ ] **Alert Center** widget is visible
- [ ] **Threat Analytics** widget is visible (with charts)
- [ ] **Real-Time Monitoring** widget is visible
- [ ] **Reports & Logs** widget is visible
- [ ] **Model Insights** widget is visible
- [ ] **Risk Assessment** widget is visible (with gauge)

#### 2.2 Check Navigation
Click through all menu items:

- [ ] Home (/dashboard) - loads correctly
- [ ] Real-Time Monitor (/monitor) - loads correctly
- [ ] Threat Analytics (/analytics) - loads correctly
- [ ] Model Insights (/insights) - loads correctly
- [ ] Dataset (/dataset) - loads correctly
- [ ] Logs (/logs) - loads correctly
- [ ] Settings (/settings) - loads correctly

#### 2.3 Check WebSocket Connection
Open browser DevTools (F12) → Console tab:

- [ ] Look for: "Connected to threat detection server"
- [ ] No WebSocket connection errors
- [ ] Socket.io client is connected

---

### ✅ Phase 3: Dataset Management Testing

#### 3.1 Load Test Dataset

**Method 1: Using Dashboard**
1. Go to Dashboard page
2. Find **Dataset Manager** widget
3. Click **"Load Test Dataset"** button
4. Enter path: `D:\dlsec2db\UNSW_NB15_testing-set.csv`
5. Click OK

**Expected:**
- [ ] Success message appears: "Dataset loaded successfully! X records loaded."
- [ ] Dataset statistics appear in widget
- [ ] Shows: Total Records, Current Index, Remaining Records

**Method 2: Using API**
```bash
curl -X POST http://localhost:5000/api/dataset/load ^
  -H "Content-Type: application/json" ^
  -d "{\"file_path\": \"D:/dlsec2db/UNSW_NB15_testing-set.csv\"}"
```

**Check:**
- [ ] Response status: 200
- [ ] Response contains: "total_records"
- [ ] Response contains: "columns"

#### 3.2 Verify Dataset Statistics
In Dataset Manager widget, check:

- [ ] Total Records shows a number > 0
- [ ] Current Index shows 0 (or current position)
- [ ] Remaining Records shows correct count
- [ ] If available, Threats count is shown

#### 3.3 Test Dataset Reset
1. Click **"Reset Stream"** button
2. Verify Current Index resets to 0

**Check:**
- [ ] Success message appears
- [ ] Current Index shows 0
- [ ] Remaining Records equals Total Records

---

### ✅ Phase 4: Real-Time Streaming Testing

#### 4.1 Start Streaming
1. In Dataset Manager widget
2. Set interval to 2.0 seconds
3. Click **"Start Streaming"** button

**Expected:**
- [ ] Success message: "Streaming started successfully!"
- [ ] Status changes to "● Streaming Active"
- [ ] Button changes to "Stop Streaming" (red)

**Check:**
- [ ] Streaming status updates correctly
- [ ] No error messages

#### 4.2 Monitor Real-Time Updates

**Alert Center:**
- [ ] New threats appear in real-time
- [ ] Threat details are displayed correctly
- [ ] Timestamps are shown
- [ ] Severity badges are colored correctly
- [ ] Source IPs are displayed

**Threat Analytics:**
- [ ] Pie chart updates with new threat types
- [ ] Line chart updates with threat counts over time
- [ ] Charts are responsive and readable

**Real-Time Monitoring:**
- [ ] Activity bars update dynamically
- [ ] IP addresses are shown
- [ ] Activity levels change based on data

**Risk Assessment:**
- [ ] Risk gauge updates
- [ ] Risky IPs list updates
- [ ] Risk levels change

#### 4.3 Test Action Execution
1. Wait for a threat to appear in Alert Center
2. Click on the threat row to expand it
3. View suggested actions
4. Click **"Execute"** on an action

**Expected:**
- [ ] Action button shows "Executing..." while processing
- [ ] Action status updates to executed
- [ ] Checkmark appears next to executed action
- [ ] Execution result is displayed

**Check:**
- [ ] Actions are generated for threats
- [ ] Actions can be executed
- [ ] Execution status updates correctly
- [ ] No errors during execution

#### 4.4 Stop Streaming
1. Click **"Stop Streaming"** button

**Expected:**
- [ ] Success message: "Streaming stopped successfully!"
- [ ] Status changes to "○ Streaming Stopped"
- [ ] Button changes back to "Start Streaming"

**Check:**
- [ ] Streaming stops immediately
- [ ] No new threats appear after stopping
- [ ] Status updates correctly

---

### ✅ Phase 5: Batch Processing Testing

#### 5.1 Process Batch
1. Make sure streaming is stopped
2. Click **"Process Batch (10)"** button

**Expected:**
- [ ] Success message: "Processed 10 records successfully!"
- [ ] Threats appear in Alert Center (if any detected)
- [ ] Dataset statistics update

**Check:**
- [ ] Batch processing completes
- [ ] Threats are detected and displayed
- [ ] Current Index increases by 10
- [ ] Remaining Records decreases

---

### ✅ Phase 6: API Endpoint Testing

#### 6.1 Test All Endpoints

**Model Status:**
```bash
curl http://localhost:5000/api/model/status
```
- [ ] Returns model status
- [ ] Shows model_loaded and scaler_loaded

**Dataset Stats:**
```bash
curl http://localhost:5000/api/dataset/stats
```
- [ ] Returns dataset statistics
- [ ] Shows total_records, current_index, remaining_records

**Get Threats:**
```bash
curl http://localhost:5000/api/threats
```
- [ ] Returns list of threats
- [ ] Shows threat details

**Streaming Status:**
```bash
curl http://localhost:5000/api/dataset/stream/status
```
- [ ] Returns streaming status
- [ ] Shows is_running, interval

---

### ✅ Phase 7: Error Handling Testing

#### 7.1 Test Error Scenarios

**Invalid File Path:**
- [ ] Try loading dataset with invalid path
- [ ] Error message should appear
- [ ] System should not crash

**Stop Streaming When Not Running:**
- [ ] Try stopping when streaming is already stopped
- [ ] Should handle gracefully

**Process Batch When No Dataset:**
- [ ] Try processing batch without loading dataset
- [ ] Error message should appear

**Execute Action Multiple Times:**
- [ ] Try executing same action twice
- [ ] Should handle gracefully

---

### ✅ Phase 8: Performance Testing

#### 8.1 Test Performance Metrics

**Dataset Loading:**
- [ ] Load time: < 10 seconds for 10,000 records
- [ ] Memory usage: reasonable

**Threat Detection:**
- [ ] Detection time: < 200ms per record
- [ ] No lag in UI updates

**Streaming:**
- [ ] Streaming interval is accurate
- [ ] No dropped records
- [ ] WebSocket latency: < 100ms

**Frontend Updates:**
- [ ] UI updates smoothly
- [ ] No lag or freezing
- [ ] Charts render correctly

---

### ✅ Phase 9: Database Verification

#### 9.1 Check Database Storage

**Check Threats Table:**
- [ ] Threats are stored in database
- [ ] All threat fields are saved correctly
- [ ] Timestamps are accurate

**Check Actions Table:**
- [ ] Actions are stored in database
- [ ] Actions are linked to threats correctly
- [ ] Execution status is saved

**Check Database File:**
- [ ] File exists: `backend/threats.db`
- [ ] File size increases as data is added
- [ ] No database errors in logs

---

### ✅ Phase 10: Complete Workflow Test

#### 10.1 End-to-End Test

1. **Start System**
   - [ ] Start both servers
   - [ ] Verify both are running

2. **Load Dataset**
   - [ ] Load test dataset
   - [ ] Verify statistics

3. **Start Streaming**
   - [ ] Start real-time streaming
   - [ ] Verify status

4. **Monitor Detection**
   - [ ] Watch threats appear
   - [ ] Verify all widgets update

5. **Execute Actions**
   - [ ] Execute actions on threats
   - [ ] Verify execution status

6. **Stop Streaming**
   - [ ] Stop streaming
   - [ ] Verify status

7. **Check Database**
   - [ ] Verify threats are stored
   - [ ] Verify actions are stored

8. **Review Dashboard**
   - [ ] All widgets show data
   - [ ] Charts are populated
   - [ ] No errors in console

---

## 📊 Test Results Template

```
Test Date: _______________
Tester: _______________
Environment: Windows/Linux/Mac

Phase 1: Server Startup
- Backend: [ ] Pass [ ] Fail
- Frontend: [ ] Pass [ ] Fail
- API Status: [ ] Pass [ ] Fail

Phase 2: Dashboard Visual
- Layout: [ ] Pass [ ] Fail
- Navigation: [ ] Pass [ ] Fail
- WebSocket: [ ] Pass [ ] Fail

Phase 3: Dataset Management
- Load Dataset: [ ] Pass [ ] Fail
- Statistics: [ ] Pass [ ] Fail
- Reset: [ ] Pass [ ] Fail

Phase 4: Real-Time Streaming
- Start Streaming: [ ] Pass [ ] Fail
- Real-Time Updates: [ ] Pass [ ] Fail
- Action Execution: [ ] Pass [ ] Fail
- Stop Streaming: [ ] Pass [ ] Fail

Phase 5: Batch Processing
- Process Batch: [ ] Pass [ ] Fail

Phase 6: API Endpoints
- All Endpoints: [ ] Pass [ ] Fail

Phase 7: Error Handling
- Error Scenarios: [ ] Pass [ ] Fail

Phase 8: Performance
- Performance Metrics: [ ] Pass [ ] Fail

Phase 9: Database
- Database Storage: [ ] Pass [ ] Fail

Phase 10: Complete Workflow
- End-to-End: [ ] Pass [ ] Fail

Issues Found:
1. ________________________________
2. ________________________________
3. ________________________________

Overall Status: [ ] All Tests Passed [ ] Some Tests Failed
```

---

## 🎯 Quick Test Commands

### Check Backend
```bash
curl http://localhost:5000/api/model/status
```

### Check Frontend
Open: http://localhost:5173

### Load Dataset
```bash
curl -X POST http://localhost:5000/api/dataset/load -H "Content-Type: application/json" -d "{\"file_path\": \"D:/dlsec2db/UNSW_NB15_testing-set.csv\"}"
```

### Start Streaming
```bash
curl -X POST http://localhost:5000/api/dataset/stream/start -H "Content-Type: application/json" -d "{\"interval\": 2.0, \"use_dataset\": true}"
```

### Get Threats
```bash
curl http://localhost:5000/api/threats
```

---

## ✅ Success Criteria

All tests pass if:
- ✅ Servers start without errors
- ✅ Dashboard loads and displays correctly
- ✅ Dataset loads successfully
- ✅ Streaming works and updates in real-time
- ✅ Threats are detected and displayed
- ✅ Actions are generated and can be executed
- ✅ All widgets update correctly
- ✅ WebSocket connection is stable
- ✅ Database stores data correctly
- ✅ No critical errors in logs

---

## 🐛 If Tests Fail

1. Check backend logs for errors
2. Check frontend console (F12) for errors
3. Verify all dependencies are installed
4. Check file paths are correct
5. Verify ports 5000 and 5173 are available
6. Check database file permissions
7. Review error messages carefully

---

## 📝 Notes

- Keep browser DevTools open during testing
- Monitor backend terminal for errors
- Check database file after testing
- Take screenshots of any issues
- Document any unexpected behavior

Good luck with testing! 🚀

