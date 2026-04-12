import numpy as np
import pandas as pd
import joblib
import os
import sys
import threading
from tensorflow.keras.models import load_model
import logging

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelService:
    """Service for loading and using the threat detection model (production CNN-LSTM)."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.categorical_cols = Config.CATEGORICAL_COLS
        self.numerical_cols = None  # Set from feature_columns when loading
        self._use_mock_fallback = getattr(Config, "USE_MOCK_FALLBACK", False)
        self._model_lock = threading.Lock()
        self.load_model()

    def load_model(self):
        """Load the trained model and preprocessing artifacts (scaler, feature_columns)."""
        try:
            model_path = Config.MODEL_PATH if os.path.isabs(Config.MODEL_PATH) else os.path.join(Config.BASE_DIR, Config.MODEL_PATH)
            scaler_path = Config.SCALER_PATH if os.path.isabs(Config.SCALER_PATH) else os.path.join(Config.BASE_DIR, Config.SCALER_PATH)
            fc_path = getattr(Config, "FEATURE_COLUMNS_PATH", None) or os.path.join(Config.MODELS_DIR, "feature_columns.pkl")
            if not os.path.isabs(fc_path):
                fc_path = os.path.join(Config.BASE_DIR, fc_path)

            if not os.path.exists(model_path):
                logger.warning("Model file not found at %s", model_path)
                self.model = None
                if not self._use_mock_fallback:
                    logger.warning("USE_MOCK_FALLBACK is False; predictions will fail until model is trained.")
                return

            if not os.path.exists(scaler_path):
                logger.warning("Scaler file not found at %s", scaler_path)
                self.scaler = None
                self.model = None
                return

            logger.info("Loading model from %s", model_path)
            new_model = load_model(model_path)
            with self._model_lock:
                self.model = new_model

            logger.info("Loading scaler from %s", scaler_path)
            self.scaler = joblib.load(scaler_path)

            if os.path.exists(fc_path):
                fc_data = joblib.load(fc_path)
                if isinstance(fc_data, dict):
                    self.feature_columns = fc_data.get("feature_columns")
                    self.numerical_cols = fc_data.get("numerical_cols")
                else:
                    self.feature_columns = fc_data if isinstance(fc_data, list) else None
                    self.numerical_cols = None
                logger.info("Loaded feature_columns (%s) from %s", len(self.feature_columns) if self.feature_columns else 0, fc_path)
            else:
                logger.warning("feature_columns.pkl not found at %s; column alignment may fail at prediction.", fc_path)
                self.feature_columns = None
                self.numerical_cols = None

            logger.info("Model and preprocessing artifacts loaded successfully")
        except Exception as e:
            logger.error("Error loading model: %s", e, exc_info=True)
            self.model = None
            self.scaler = None
            self.feature_columns = None

    def preprocess_data(self, data):
        """
        Preprocess input data for model prediction.
        Aligns to saved feature_columns, scales numericals, one-hot categoricals, reshapes for CNN-LSTM.
        """
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()

        for col in ["id", "attack_cat"]:
            if col in df.columns:
                df = df.drop(columns=[col], errors="ignore")

        if "service" in df.columns:
            df["service"] = df["service"].replace("-", "unknown")

        for col in self.categorical_cols:
            if col in df.columns:
                df[col] = df[col].fillna("unknown").astype(str)

        if self.feature_columns is None:
            raise ValueError("feature_columns not loaded; run training pipeline first or provide feature_columns.pkl")

        if self.numerical_cols is None:
            self.numerical_cols = [c for c in self.feature_columns if not c.startswith("proto_") and not c.startswith("service_") and not c.startswith("state_")]

        # Ensure df has all numerical columns (missing -> 0)
        num_in_df = [c for c in self.numerical_cols if c in df.columns]
        missing_num = [c for c in self.numerical_cols if c not in df.columns]
        if missing_num:
            for c in missing_num:
                df[c] = 0
        df_numerical = df[self.numerical_cols].fillna(0)

        if self.scaler is not None:
            X_num = pd.DataFrame(
                self.scaler.transform(df_numerical),
                columns=self.numerical_cols,
                index=df.index,
            )
        else:
            X_num = df_numerical.copy()

        df_cat = pd.get_dummies(df[self.categorical_cols], dtype=int)
        X = pd.concat([X_num, df_cat], axis=1)
        X = X.reindex(columns=self.feature_columns, fill_value=0)

        n_features = X.shape[1]

# ---- DEBUG SHAPE CHECK ----
        

        X_reshaped = X.values.reshape((X.shape[0], 1, n_features))

        
# ----------------------------

        return X_reshaped


    def predict(self, data):
        """
        Predict threat from network traffic data using loaded CNN-LSTM model.
        Returns dict with is_threat, confidence, severity, threat_type, raw_prediction.
        """
        try:
            if self.model is None or self.scaler is None:
                if self._use_mock_fallback:
                    return self._mock_predict(data)
                return {
                    "is_threat": False,
                    "confidence": 0.0,
                    "severity": "Low",
                    "threat_type": "Unknown",
                    "raw_prediction": 0.0,
                    "error": "Model or scaler not loaded. Run training pipeline (backend/ml/train_model.py) or set USE_MOCK_FALLBACK=true.",
                }
            if self.feature_columns is None:
                if self._use_mock_fallback:
                    return self._mock_predict(data)
                return {
                    "is_threat": False,
                    "confidence": 0.0,
                    "severity": "Low",
                    "threat_type": "Unknown",
                    "raw_prediction": 0.0,
                    "error": "Feature columns not loaded. Run training pipeline.",
                }

            X_processed = self.preprocess_data(data)
            with self._model_lock:
                prediction = self.model.predict(X_processed, verbose=0)
            raw = float(prediction[0][0])
            is_threat = raw > 0.5
            confidence = raw if is_threat else (1.0 - raw)

            if confidence >= 0.9:
                severity = "Critical"
            elif confidence >= 0.75:
                severity = "High"
            elif confidence >= 0.6:
                severity = "Medium"
            else:
                severity = "Low"

            return {
                "is_threat": bool(is_threat),
                "confidence": round(confidence, 4),
                "severity": severity,
                "threat_type": self._determine_threat_type(data, confidence) if is_threat else "Normal",
                "raw_prediction": raw,
            }
        except Exception as e:
            logger.error("Error making prediction: %s", e, exc_info=True)
            if self._use_mock_fallback:
                return self._mock_predict(data)
            return {
                "is_threat": False,
                "confidence": 0.0,
                "severity": "Low",
                "threat_type": "Unknown",
                "raw_prediction": 0.0,
                "error": str(e),
            }

    def _determine_threat_type(self, data, confidence):
        """Determine threat type from attack_cat if present, else heuristics."""
        if "attack_cat" in data and data["attack_cat"] and str(data["attack_cat"]).lower() != "normal":
            attack_cat = str(data["attack_cat"]).strip().lower()
            mapping = {
                "fuzzers": "Malware", "analysis": "Reconnaissance", "backdoors": "Exploit",
                "dos": "DDoS", "exploits": "Exploit", "generic": "Suspicious Activity",
                "reconnaissance": "Reconnaissance", "shellcode": "Exploit", "worms": "Malware",
                "ddos": "DDoS", "brute force": "Brute Force", "sql injection": "Exploit", "xss": "Exploit",
            }
            for key, threat_type in mapping.items():
                if key in attack_cat:
                    return threat_type
            return data["attack_cat"].title() if isinstance(data["attack_cat"], str) else "Suspicious Activity"

        if "proto" in data and "spkts" in data and "dpkts" in data:
            total_pkts = data.get("spkts", 0) + data.get("dpkts", 0)
            if total_pkts > 1000 and confidence > 0.8:
                return "DDoS"
        if "sbytes" in data and "dbytes" in data:
            total_bytes = data.get("sbytes", 0) + data.get("dbytes", 0)
            if total_bytes > 1000000 and confidence > 0.7:
                return "Malware"
        if str(data.get("proto", "")).lower() == "tcp" and str(data.get("service", "")).lower() in ("ssh", "ftp", "telnet") and confidence > 0.75:
            return "Brute Force"
        if str(data.get("state", "")).upper() in ("REQ", "INT") and confidence > 0.6:
            return "Reconnaissance"

        if confidence > 0.9:
            return "DDoS"
        if confidence > 0.8:
            return "Malware"
        if confidence > 0.7:
            return "Exploit"
        if confidence > 0.6:
            return "Reconnaissance"
        return "Suspicious Activity"

    def _mock_predict(self, data):
        """Optional mock prediction when model is not available (only if USE_MOCK_FALLBACK is True)."""
        import random
        is_threat = random.random() > 0.3
        confidence = random.uniform(0.6, 0.99) if is_threat else random.uniform(0.1, 0.4)
        if confidence >= 0.9:
            severity = "Critical"
        elif confidence >= 0.75:
            severity = "High"
        elif confidence >= 0.6:
            severity = "Medium"
        else:
            severity = "Low"
        threat_types = ["DDoS", "Malware", "Brute Force", "Exploit", "Reconnaissance"]
        threat_type = random.choice(threat_types) if is_threat else "Normal"
        return {
            "is_threat": is_threat,
            "confidence": round(confidence, 4),
            "severity": severity,
            "threat_type": threat_type,
            "raw_prediction": confidence,
        }


model_service = ModelService()
