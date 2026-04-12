# DL-SEC Production ML Integration – Change Log

This document lists all changes made to upgrade from simulated ML behavior to real production-integrated CNN-LSTM model training and inference. No existing APIs were removed or renamed; new files and optional parameters were added.

---

## Summary

- **Phase 1:** New production training script `backend/ml/train_model.py`.
- **Phase 2:** `model_service.py` loads real artifacts (model, scaler, feature_columns) and uses optional mock fallback only when configured.
- **Phase 3:** `/api/model/retrain` triggers real training in a background subprocess and no longer simulates with a 2s delay.
- **Phase 4:** New DB models `TrainingSession` and `ModelMetrics`; metrics are persisted and `/api/metrics` and `/api/model/metrics` prefer latest DB metrics.
- **Phase 5:** No backend change; `GET /api/threats` already returns real DB records (id, timestamp, threat_type, severity, confidence, source_ip, status, etc.) for the Logs page.

---

## New Files

### 1. `backend/ml/__init__.py`
- Empty package marker for the `ml` module.

### 2. `backend/ml/train_model.py`
- **Purpose:** Standalone production training pipeline for CNN-LSTM on UNSW-NB15.
- **Run from project root:** `python backend/ml/train_model.py`
- **Behavior:**
  - Loads `UNSW_NB15_training-set.csv` and `UNSW_NB15_testing-set.csv` from project root (paths overridable via `--train` and `--test`).
  - Drops `id` and `attack_cat`; replaces `-` in `service` with `unknown`; fills missing categoricals and numerics.
  - One-hot encodes `proto`, `service`, `state`; scales numericals with `MinMaxScaler`; aligns train/test columns.
  - Binary target: `label` column.
  - Builds CNN-LSTM: Conv1D(64,128,256) + MaxPool + Dropout, LSTM(128,64,32) + Dropout, Dense(64), Dense(1, sigmoid).
  - Trains with validation split; evaluates on test set (accuracy, precision, recall, F1, confusion matrix).
- **Outputs (under `backend/models/`):**
  - `cnn_lstm_model.h5` – Keras model.
  - `scaler.pkl` – joblib MinMaxScaler.
  - `feature_columns.pkl` – joblib dict: `{"feature_columns": list, "numerical_cols": list}`.
  - `latest_training_metrics.json` – JSON with `accuracy`, `precision`, `recall`, `f1_score`, `confusion_matrix` for the Flask backend to read and store in DB.

---

## Modified Files

### 3. `backend/config.py`
- **MODEL_PATH:** Default changed from `final_cnn_lstm.keras` to `cnn_lstm_model.h5`.
- **FEATURE_COLUMNS_PATH:** New default `models/feature_columns.pkl` (with optional env override).
- **USE_MOCK_FALLBACK:** New config (env `USE_MOCK_FALLBACK`). When `false` (default), prediction fails with a clear error if model/artifacts are missing; when `true`, mock prediction is used as fallback.

### 4. `backend/requirements.txt`
- **Added:** `joblib>=1.3.0` for saving/loading scaler and feature_columns.

### 5. `backend/database/models.py`
- **New model `TrainingSession`:**
  - `id`, `model_name`, `start_time`, `end_time`, `dataset_used`, `status`, `created_at`.
  - Used to record each training run.
- **New model `ModelMetrics`:**
  - `id`, `training_id` (FK to `TrainingSession`), `accuracy`, `precision`, `recall`, `f1_score`, `confusion_matrix_json`, `created_at`.
  - One row per training run; used for real metrics in APIs.
- **Existing tables:** Unchanged (no deletions or renames).

### 6. `backend/services/model_service.py`
- **Artifacts:** Loads `scaler` and `feature_columns` from config paths; uses **joblib** for both (and for feature_columns dict).
- **feature_columns.pkl:** Expects a dict `{"feature_columns": list, "numerical_cols": list}`; falls back to list-only for backward compatibility.
- **Prediction:** Uses loaded model + scaler + feature_columns only. No mock unless `Config.USE_MOCK_FALLBACK` is True. On missing model/artifacts, returns a structured error in the response instead of mocking.
- **Preprocessing:** Aligns input to `feature_columns`, scales numericals, one-hot categoricals, reshapes to `(samples, 1, n_features)` for CNN-LSTM.
- **Removed:** Default mock prediction when model is missing (now opt-in via `USE_MOCK_FALLBACK`).

### 7. `backend/services/metrics_service.py`
- **get_model_metrics(app=None):** Optional `app` argument. When `app` is provided, fetches latest `ModelMetrics` from DB and returns metrics for `cnn`, `lstm`, `cnn_lstm` from that row (same values for all three for backward compatibility).
- **get_full_metrics_payload(app=None):** Accepts optional `app`; forwards it to `get_model_metrics(app)` so unified metrics can reflect DB-backed model metrics.

### 8. `backend/app.py`
- **GET /api/metrics:** Passes `current_app` into `metrics_service.get_full_metrics_payload(app=current_app)` so model metrics come from DB when available.

### 9. `backend/routes/model.py`
- **GET /api/model/status:** Response unchanged in spirit; added `feature_columns_loaded` and updated `message` to mention training script or `USE_MOCK_FALLBACK`. Existing keys kept.
- **GET /api/model/metrics:** Uses `metrics_service.get_model_metrics(app=current_app)` so returned metrics are from DB when a `ModelMetrics` row exists.
- **POST /api/model/retrain:**  
  - No more simulated 2s delay or artificial metric boost.  
  - Starts a **background thread** that:
    1. Runs `python backend/ml/train_model.py` in a subprocess (from project root).
    2. Waits for it to finish (timeout 3600s).
    3. Reads `backend/models/latest_training_metrics.json`.
    4. Creates `TrainingSession` and `ModelMetrics` in the DB.
    5. Calls `metrics_service.finish_training(...)` with the new metrics.
    6. Calls `model_service.load_model()` to reload the new model and artifacts.
  - Returns **202 Accepted** immediately with `status: 'started'` and a message that training is running in the background.
  - If training is already in progress, returns **409** as before.

---

## API Behavior (Backward Compatibility)

- **GET /api/metrics** – Same shape; `models` may now be filled from DB (latest `ModelMetrics`).
- **GET /api/model/status** – Same keys plus `feature_columns_loaded`; `message` text updated.
- **GET /api/model/metrics** – Same shape; values from DB when available.
- **POST /api/model/retrain** – Now returns 202 and runs real training in background; 409 when busy unchanged.
- **GET /api/threats** – Unchanged; still returns real threat records from DB (used by Logs page).
- All other routes and request/response shapes are unchanged.

---

## How to Use

1. **First-time setup (train model once)**  
   From project root:
   ```bash
   python backend/ml/train_model.py
   ```
   Ensure `UNSW_NB15_training-set.csv` and `UNSW_NB15_testing-set.csv` are in the project root (or pass `--train` / `--test`).

2. **Start backend**  
   Model, scaler, and feature_columns are loaded from `backend/models/` at startup. If any are missing and `USE_MOCK_FALLBACK` is not set, predictions will return an error payload until training is run.

3. **Retrain from API**  
   `POST /api/model/retrain` starts training in the background and returns 202. When the script finishes, metrics are stored in DB and the model is reloaded; no server restart needed.

4. **Optional mock fallback**  
   If you want predictions to fall back to mock when artifacts are missing (e.g. dev without running training):
   ```bash
   set USE_MOCK_FALLBACK=true
   ```
   (or equivalent in your environment).

---

## What Was Not Changed

- No refactor of the whole project.
- No removal or renaming of existing APIs.
- Frontend not modified (only backend changes).
- Existing dataset upload, streaming, and threat detection flows unchanged.
- `dataset_service`, `data_simulator`, threat/action routes, and WebSocket behavior unchanged.
- Existing DB tables (threats, actions, threat_history) unchanged; only new tables added.

---

## File Checklist

| Item | Path | Action |
|------|------|--------|
| Training script | `backend/ml/train_model.py` | **NEW** |
| ML package | `backend/ml/__init__.py` | **NEW** |
| Config | `backend/config.py` | **MODIFIED** |
| Requirements | `backend/requirements.txt` | **MODIFIED** (joblib) |
| DB models | `backend/database/models.py` | **MODIFIED** (TrainingSession, ModelMetrics) |
| Model service | `backend/services/model_service.py` | **MODIFIED** |
| Metrics service | `backend/services/metrics_service.py` | **MODIFIED** |
| App metrics route | `backend/app.py` | **MODIFIED** |
| Model routes | `backend/routes/model.py` | **MODIFIED** (retrain, status, metrics) |
| Logs / threats | `backend/routes/threats.py` | **UNCHANGED** (already returns real DB data) |
