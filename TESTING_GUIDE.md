# DL-SEC Testing Guide

## 🧪 Complete Testing Workflow

### Step 1: Start the Servers

```bash
# From project root
npm start
```

This will start:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:5173

### Step 2: Verify Backend is Running

Open a new terminal and check the backend status:

```bash
curl http://localhost:5000/api/model/status
```

Expected response:
```json
{
  "model_loaded": true/false,
  "scaler_loaded": true/false,
  "status": "ready" or "mock_mode",
  "message": "Model is ready for predictions"
}
```

### Step 3: Access the Dashboard

1. Open your browser and navigate to: **http://localhost:5173**
2. You should see the DL-SEC dashboard with:
   - Dataset Manager widget
   - Alert Center
   - Threat Analytics
   - Real-Time Monitoring
   - Risk Assessment
   - Model Insights

### Step 4: Load the Test Dataset

#### Option A: Using the Dashboard (Recommended)

1. On the dashboard, find the **Dataset Manager** widget
2. Click **"Load Test Dataset"** button
3. When prompted, enter the full path to your test dataset:
   - Example: `D:\dlsec2db\UNSW_NB15_testing-set.csv`
4. Click OK
5. Wait for the success message showing the number of records loaded

#### Option B: Using API

```bash
curl -X POST http://localhost:5000/api/dataset/load \
  -H "Content-Type: application/json" \
  -d "{\"file_path\": \"D:/dlsec2db/UNSW_NB15_testing-set.csv\"}"
```

#### Option C: Using the Script

```bash
python backend/scripts/load_test_dataset.py
```

### Step 5: Verify Dataset is Loaded

Check the **Dataset Manager** widget on the dashboard. You should see:
- Total Records: [number]
- Current Index: 0
- Remaining Records: [number]
- Threats: [number] (if available)

Or check via API:

```bash
curl http://localhost:5000/api/dataset/stats
```

### Step 6: Start Real-Time Streaming

#### Option A: Using the Dashboard

1. In the **Dataset Manager** widget, set the streaming interval (default: 2 seconds)
2. Click **"Start Streaming"** button
3. You should see the status change to "● Streaming Active"

#### Option B: Using API

```bash
curl -X POST http://localhost:5000/api/dataset/stream/start \
  -H "Content-Type: application/json" \
  -d '{"interval": 2.0, "use_dataset": true}'
```

### Step 7: Monitor Real-Time Threat Detection

Once streaming is active, you should see:

1. **Alert Center**: New threats appearing in real-time
2. **Threat Analytics**: Charts updating with threat data
3. **Real-Time Monitoring**: Network activity bars updating
4. **Risk Assessment**: Risk levels and risky IPs updating

### Step 8: Test Action Execution

1. In the **Alert Center**, click on a threat to expand it
2. You should see suggested actions
3. Click **"Execute"** on any action
4. The action status should update to show it's been executed

### Step 9: Process Batch (Alternative to Streaming)

Instead of streaming, you can process records in batches:

1. In the **Dataset Manager** widget, click **"Process Batch (10)"**
2. This will process 10 records at once
3. Check the **Alert Center** for detected threats

### Step 10: Stop Streaming

When you're done testing:

1. Click **"Stop Streaming"** in the Dataset Manager widget
2. Or use the API:
   ```bash
   curl -X POST http://localhost:5000/api/dataset/stream/stop
   ```

## 📊 What to Check

### ✅ Backend Checks

- [ ] Backend server is running on port 5000
- [ ] Model status endpoint returns valid response
- [ ] Dataset can be loaded successfully
- [ ] Dataset statistics are accurate
- [ ] Streaming can be started and stopped
- [ ] Threats are being detected and stored
- [ ] Actions are being generated correctly
- [ ] WebSocket events are being emitted

### ✅ Frontend Checks

- [ ] Frontend loads on port 5173
- [ ] Dashboard displays all widgets
- [ ] Dataset Manager widget is visible
- [ ] Can load dataset from dashboard
- [ ] Dataset statistics are displayed
- [ ] Can start/stop streaming from dashboard
- [ ] Alert Center shows threats in real-time
- [ ] Threat Analytics charts update
- [ ] Real-Time Monitoring shows activity
- [ ] Actions can be executed
- [ ] WebSocket connection is established

### ✅ Data Flow Checks

- [ ] Dataset records are processed correctly
- [ ] Model predictions are accurate
- [ ] Threat types are classified correctly
- [ ] Severity levels are assigned correctly
- [ ] Actions are generated based on threat type
- [ ] WebSocket events are received by frontend
- [ ] Database stores threats and actions
- [ ] Frontend updates in real-time

## 🐛 Common Issues & Solutions

### Issue: Dataset Not Loading

**Symptoms:**
- Error message when trying to load dataset
- Dataset statistics show error

**Solutions:**
1. Verify the file path is correct and absolute
2. Check file permissions
3. Ensure the file is CSV or Excel format
4. Check backend logs for detailed error messages

### Issue: Streaming Not Working

**Symptoms:**
- Streaming status shows as stopped
- No threats appearing in dashboard

**Solutions:**
1. Verify dataset is loaded first
2. Check backend logs for errors
3. Verify WebSocket connection is established
4. Check browser console for errors

### Issue: No Threats Detected

**Symptoms:**
- Streaming is active but no threats appear
- All records show as "Normal"

**Solutions:**
1. Check if model is loaded (model status endpoint)
2. If model is not loaded, it will use mock predictions
3. Verify dataset contains threat records
4. Check model prediction confidence thresholds

### Issue: Frontend Not Updating

**Symptoms:**
- Backend shows threats but frontend doesn't update
- WebSocket events not received

**Solutions:**
1. Check browser console for WebSocket errors
2. Verify WebSocket URL in frontend config
3. Check CORS settings in backend
4. Verify WebSocket connection in browser DevTools

### Issue: Actions Not Executing

**Symptoms:**
- Action buttons don't work
- Actions don't update after execution

**Solutions:**
1. Check browser console for errors
2. Verify backend API is responding
3. Check database for action records
4. Verify action execution endpoint is working

## 📈 Performance Testing

### Test with Small Dataset

1. Load a small subset of the dataset (first 100 records)
2. Process records one by one
3. Monitor response times
4. Check memory usage

### Test with Large Dataset

1. Load the full test dataset
2. Start streaming with different intervals
3. Monitor system resources
4. Check for memory leaks
5. Verify database performance

### Test Concurrent Requests

1. Start multiple streaming sessions
2. Process batches simultaneously
3. Monitor backend performance
4. Check for race conditions

## 🎯 Expected Results

### Successful Test Run

- ✅ Dataset loads successfully
- ✅ Streaming starts without errors
- ✅ Threats are detected and displayed
- ✅ Actions are generated and can be executed
- ✅ Frontend updates in real-time
- ✅ All widgets display data correctly
- ✅ WebSocket connection is stable
- ✅ Database stores all threats and actions

### Performance Metrics

- Dataset loading: < 5 seconds for 10,000 records
- Threat detection: < 100ms per record
- WebSocket latency: < 50ms
- Frontend update: < 200ms after threat detection
- Database operations: < 50ms per query

## 📝 Test Report Template

```
Test Date: [Date]
Tester: [Name]
Environment: [OS, Browser, Node version, Python version]

Backend Tests:
- [ ] Server starts successfully
- [ ] Model loads correctly
- [ ] Dataset loads successfully
- [ ] Streaming works
- [ ] Threats are detected
- [ ] Actions are generated
- [ ] WebSocket events are emitted

Frontend Tests:
- [ ] Dashboard loads
- [ ] Dataset Manager works
- [ ] Alert Center displays threats
- [ ] Charts update correctly
- [ ] Actions can be executed
- [ ] Real-time updates work

Issues Found:
1. [Issue description]
2. [Issue description]

Performance:
- Dataset load time: [time]
- Threat detection time: [time]
- WebSocket latency: [time]
- Frontend update time: [time]
```

## 🚀 Next Steps After Testing

1. Review test results
2. Fix any issues found
3. Optimize performance if needed
4. Add additional tests
5. Document any issues
6. Prepare for production deployment

## 📞 Support

If you encounter any issues during testing:
1. Check the troubleshooting section
2. Review backend and frontend logs
3. Check the browser console
4. Verify all dependencies are installed
5. Check the API status endpoints

