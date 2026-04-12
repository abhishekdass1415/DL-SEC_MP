# Application Setup Guide: DL-SEC (Deep Learning based Security System for Threat Detection)

## 1. Project Overview

**DL-SEC** is an advanced security system that leverages deep learning to perform real-time threat detection and analysis.

### System Architecture
- **Frontend Dashboard:** A responsive web application built with React, providing user interfaces for data uploading, real-time detection monitoring, and result visualization.
- **Backend API:** A Node.js and Express server that handles user authentication, database operations, and orchestrates communication between the frontend and the machine learning service.
- **Deep Learning Model (ML Module):** A Python-based inference engine utilizing modern frameworks (e.g., TensorFlow/PyTorch) to process datasets and run threat detection algorithms.
- **Data Layer:** A MongoDB database storing user profiles, historical scan results, and configuration settings.

---

## 2. System Requirements

### Hardware Requirements
- **RAM:** 8 GB minimum (16 GB recommended for handling large datasets)
- **CPU:** Multi-core processor (Intel i5/Ryzen 5 or higher)
- **GPU:** Optional but highly recommended (NVIDIA GPU with CUDA support for faster ML model inference)
- **Storage:** At least 20 GB of free space

### Software Requirements
- **Operating System:** Windows 10/11, macOS, or Linux (Ubuntu 20.04+)
- **Node.js:** v18.x or higher
- **npm:** v9.x or higher (comes with Node.js)
- **Python:** v3.9 to v3.11
- **MongoDB:** v6.0 or higher (Locally installed or MongoDB Atlas cloud instance)
- **Git:** For version control and repository management

---

## 3. Folder Structure Overview

The repository is organized into three main directories, each serving a specific purpose in the architecture:

```text
DL-SEC/
├── client/           # React frontend application
├── server/           # Node.js / Express backend server
└── ml_engine/        # Python Deep Learning environment
```

- **`client/`**: Contains React components, UI assets, and state management for the user dashboard.
- **`server/`**: Contains API routes, database models, controllers, and middleware for the backend system.
- **`ml_engine/`**: Contains the pre-trained deep learning models, datasets, inference scripts, and FastAPI/Flask endpoints for model execution.

---

## 4. Installation Steps

### Step 4.1: Clone the Repository

Open your terminal or command prompt and run:
```bash
git clone https://github.com/abhishekdass1415/DL-SEC_MP.git
cd DL-SEC_MP
```

### Step 4.2: Frontend Installation (Client)
Navigate to the `client` directory and install the required JavaScript dependencies:
```bash
cd client
npm install
```

### Step 4.3: Backend Installation (Server)
Open a new terminal window, navigate to the `server` directory, and install dependencies:
```bash
cd server
npm install
```

### Step 4.4: ML Module Installation (Python)
It is highly recommended to use a virtual environment for the Python module to prevent dependency conflicts.
Open a new terminal window, navigate to the `ml_engine` directory, and run:
```bash
cd ml_engine

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt
```

---

## 5. Environment Variables Setup

Configuration variables securely manage credentials and runtime behavior. You need to create `.env` files in both the `server` and `client` directories.

### Backend (`server/.env`)
Create a file named `.env` in the `server` directory and add the following:
```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/dl_sec_db
JWT_SECRET=super_secret_jwt_signature_key_2026
ML_API_URL=http://localhost:8000/api/detect
CLIENT_URL=http://localhost:3000
```

### Frontend (`client/.env`)
Create a file named `.env` in the `client` directory:
```env
# If using Create React App
REACT_APP_API_BASE_URL=http://localhost:5000/api

# If using Vite
VITE_API_BASE_URL=http://localhost:5000/api
```

### ML Engine (`ml_engine/.env` - Optional)
```env
PORT=8000
MODEL_PATH=./models/threat_detector_v2.h5
CONFIDENCE_THRESHOLD=0.85
```

---

## 6. Running the Application Locally

To fully launch the system, you need to spin up all three layers in separate terminal windows.

### 1. Start the Machine Learning Service
```bash
cd ml_engine
# Ensure your virtual env is activated!
python app.py
```
*Service will start on: **http://localhost:8000***

### 2. Start the Backend Server
```bash
cd server
npm run dev
```
*Server will start on: **http://localhost:5000***

### 3. Start the Frontend Application
```bash
cd client
npm start
# Or if using Vite:
npm run dev
```
*Dashboard will start on: **http://localhost:3000***

---

## 7. External Services Configuration

### Cloud Hosting & Exposing Localhost
If you need to expose your local backend securely (for external webhooks or quick mobile testing), you can use a tunneling service.

**Using ngrok:**
```bash
ngrok http 5000
```
This generates a public URL (e.g., `https://1234-abcd.ngrok-free.app`). 
Update `VITE_API_BASE_URL` in your frontend `.env` to this new URL if testing on external devices.

**Database Hosting:**
If not using local MongoDB, replace `MONGODB_URI` with your MongoDB Atlas connection string:
```env
MONGODB_URI=mongodb+srv://admin:securePassword@cluster0.mongodb.net/dl_sec?retryWrites=true&w=majority
```

---

## 8. Configuration File Updates

### CORS Settings (Backend)
In your `server/server.js` or `app.js`, ensure CORS accepts requests from the frontend URL:
```javascript
const cors = require('cors');

app.use(cors({
    origin: process.env.CLIENT_URL || 'http://localhost:3000',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    credentials: true,
}));
```

### Frontend Build Setup (`vite.config.js` example)
If strictly using Vite, setting the server port explicitly is good practice:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
```

---

## 9. How to Use the Application

Once everything is running, follow this general workflow:

1. **Access the Dashboard:** Open your browser and navigate to `http://localhost:3000`.
2. **Authentication:** 
   - Click "Register" to create an admin account.
   - "Login" with your new credentials.
3. **Data Upload / Scanning:**
   - Navigate to the **"New Scan"** tab.
   - Upload network logs, packet captures (PCAP), or targeted dataset files via the drag-and-drop interface.
   - Click **"Analyze"**. The frontend sends data to the Node backend, which proxies the request to the Python ML engine.
4. **View Results:**
   - Once inference is completed, you will be redirected to the **"Results"** dashboard.
   - Threats detected will be highlighted, and logs will be permanently saved to MongoDB for historical review.

---

## 10. Troubleshooting

### Common Errors and Fixes

- **Error:** `Port 3000 (or 5000) is already in use.`
  - **Fix:** Kill the process running on that port. 
  - Windows: `netstat -ano | findstr :3000` then `taskkill /PID <PID> /F`
  - Linux/Mac: `lsof -i :3000` then `kill -9 <PID>`

- **Error:** `MongoNetworkError: failed to connect to server [localhost:27017]`
  - **Fix:** Ensure the MongoDB underlying service is actively running on your machine.
  - Windows: Open Services app -> Start "MongoDB".

- **Error:** `ModuleNotFoundError: No module named 'tensorflow'`
  - **Fix:** Your virtual environment is likely not activated. Activate it (`venv\Scripts\activate`) and re-run `pip install -r requirements.txt`.

- **Error:** Model fails to load / `FileNotFoundError`
  - **Fix:** Double-check your `MODEL_PATH` in the `.env` file of your `ml_engine`. Ensure the `.h5` or `.pt` files were not ignored by `.gitignore` and are physically present in the directory.

---

## 11. Notes & Best Practices

- **Security Considerations:**
  - Never commit `.env` files to version control. Let an `.env.example` file securely hold dummy variables for reference.
  - Ensure API endpoints interacting with ML models implement rate-limiting to prevent denial of service by heavy automated requests.
- **Performance Tips:**
  - For large scan files, implement WebSockets to stream progress from the backend server to the frontend instead of waiting for a single large HTTP response.
  - Make sure TensorFlow/PyTorch utilizes the GPU if available (install appropriate CUDA toolkit versions).
