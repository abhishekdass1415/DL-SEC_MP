import numpy as np
import pandas as pd
import pickle
import os
import sys
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
    """Service for loading and using the threat detection model"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.categorical_cols = Config.CATEGORICAL_COLS
        self.numerical_cols = None
        self.feature_columns = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and preprocessing objects"""
        try:
            # Use absolute paths from config
            model_path = Config.MODEL_PATH if os.path.isabs(Config.MODEL_PATH) else os.path.join(Config.BASE_DIR, Config.MODEL_PATH)
            scaler_path = Config.SCALER_PATH if os.path.isabs(Config.SCALER_PATH) else os.path.join(Config.BASE_DIR, Config.SCALER_PATH)
            
            if not os.path.exists(model_path):
                logger.warning(f"Model file not found at {model_path}. Using mock predictions.")
                self.model = None
                return
            
            if not os.path.exists(scaler_path):
                logger.warning(f"Scaler file not found at {scaler_path}. Using mock predictions.")
                self.scaler = None
                return
            
            # Load model
            logger.info(f"Loading model from {model_path}")
            self.model = load_model(model_path)
            
            # Load scaler
            logger.info(f"Loading scaler from {scaler_path}")
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            logger.info("Model and scaler loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
            self.scaler = None
    
    def preprocess_data(self, data):
        """
        Preprocess input data for model prediction
        Args:
            data: dict or pandas DataFrame with network traffic features
        Returns:
            Preprocessed numpy array ready for model prediction
        """
        try:
            # Convert to DataFrame if dict
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = data.copy()
            
            # Drop unnecessary columns if present
            columns_to_drop = ['id', 'attack_cat']
            for col in columns_to_drop:
                if col in df.columns:
                    df = df.drop(col, axis=1)
            
            # Handle service column
            if 'service' in df.columns:
                df['service'] = df['service'].replace('-', 'unknown')
            
            # Separate categorical and numerical columns
            if self.numerical_cols is None:
                # Infer numerical columns (all except categorical and target)
                all_cols = set(df.columns)
                categorical_set = set(self.categorical_cols)
                target_set = {'label'}
                self.numerical_cols = list(all_cols - categorical_set - target_set)
            
            # One-hot encode categorical columns
            df_categorical = pd.get_dummies(df[self.categorical_cols], dtype=int)
            
            # Scale numerical columns
            if self.scaler is not None:
                df_numerical = pd.DataFrame(
                    self.scaler.transform(df[self.numerical_cols]),
                    columns=self.numerical_cols
                )
            else:
                # If no scaler, use original values
                df_numerical = df[self.numerical_cols].copy()
            
            # Combine processed features
            X = pd.concat([df_numerical, df_categorical], axis=1)
            
            # Align columns if feature_columns is set
            if self.feature_columns is not None:
                X = X.reindex(columns=self.feature_columns, fill_value=0)
            
            # Reshape for CNN-LSTM: (samples, timesteps, features)
            n_features = X.shape[1]
            X_reshaped = X.values.reshape((X.shape[0], 1, n_features))
            
            return X_reshaped
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise
    
    def predict(self, data):
        """
        Predict threat from network traffic data
        Args:
            data: dict or DataFrame with network traffic features
        Returns:
            dict with prediction results
        """
        try:
            if self.model is None:
                # Mock prediction for development
                return self._mock_predict(data)
            
            # Preprocess data
            X_processed = self.preprocess_data(data)
            
            # Make prediction
            prediction = self.model.predict(X_processed, verbose=0)
            
            # Binary classification: 0 = Normal, 1 = Attack
            is_threat = prediction[0][0] > 0.5
            confidence = float(prediction[0][0]) if is_threat else float(1 - prediction[0][0])
            
            # Determine severity based on confidence
            if confidence >= 0.9:
                severity = 'Critical'
            elif confidence >= 0.75:
                severity = 'High'
            elif confidence >= 0.6:
                severity = 'Medium'
            else:
                severity = 'Low'
            
            return {
                'is_threat': bool(is_threat),
                'confidence': round(confidence, 4),
                'severity': severity,
                'threat_type': self._determine_threat_type(data, confidence) if is_threat else 'Normal',
                'raw_prediction': float(prediction[0][0])
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return {
                'is_threat': False,
                'confidence': 0.0,
                'severity': 'Low',
                'threat_type': 'Unknown',
                'error': str(e)
            }
    
    def _determine_threat_type(self, data, confidence):
        """Determine threat type based on features and confidence"""
        # First, check if attack_cat is available in the data (from dataset)
        if 'attack_cat' in data and data['attack_cat'] and str(data['attack_cat']).lower() != 'normal':
            attack_cat = str(data['attack_cat']).strip()
            
            # Map dataset attack categories to our threat types
            attack_category_mapping = {
                'fuzzers': 'Malware',
                'analysis': 'Reconnaissance',
                'backdoors': 'Exploit',
                'dos': 'DDoS',
                'exploits': 'Exploit',
                'generic': 'Suspicious Activity',
                'reconnaissance': 'Reconnaissance',
                'shellcode': 'Exploit',
                'worms': 'Malware',
                'ddos': 'DDoS',
                'brute force': 'Brute Force',
                'sql injection': 'Exploit',
                'xss': 'Exploit'
            }
            
            # Try to map the attack category
            attack_lower = attack_cat.lower()
            for key, threat_type in attack_category_mapping.items():
                if key in attack_lower:
                    return threat_type
            
            # If no mapping found, use the attack category name (capitalized)
            return attack_cat.title()
        
        # If attack_cat not available, use heuristics based on features
        threat_types = ['DDoS', 'Malware', 'Brute Force', 'Exploit', 'Reconnaissance']
        
        # Heuristic based on protocol and other features
        if 'proto' in data:
            proto = str(data.get('proto', '')).lower()
            
            # Check for high packet counts (DDoS indicator)
            if 'spkts' in data and 'dpkts' in data:
                total_pkts = data.get('spkts', 0) + data.get('dpkts', 0)
                if total_pkts > 1000 and confidence > 0.8:
                    return 'DDoS'
            
            # Check for high byte counts (Malware/Data exfiltration)
            if 'sbytes' in data and 'dbytes' in data:
                total_bytes = data.get('sbytes', 0) + data.get('dbytes', 0)
                if total_bytes > 1000000 and confidence > 0.7:
                    return 'Malware'
            
            # Check for TCP connections (Brute Force indicator)
            if 'tcp' in proto and 'service' in data:
                service = str(data.get('service', '')).lower()
                if service in ['ssh', 'ftp', 'telnet'] and confidence > 0.75:
                    return 'Brute Force'
            
            # Check for suspicious state patterns (Reconnaissance)
            if 'state' in data:
                state = str(data.get('state', '')).upper()
                if state in ['REQ', 'INT'] and confidence > 0.6:
                    return 'Reconnaissance'
        
        # Default based on confidence
        if confidence > 0.9:
            return 'DDoS'
        elif confidence > 0.8:
            return 'Malware'
        elif confidence > 0.7:
            return 'Exploit'
        elif confidence > 0.6:
            return 'Reconnaissance'
        else:
            return 'Suspicious Activity'
    
    def _mock_predict(self, data):
        """Mock prediction for development when model is not available"""
        import random
        is_threat = random.random() > 0.3  # 70% chance of threat for demo
        confidence = random.uniform(0.6, 0.99) if is_threat else random.uniform(0.1, 0.4)
        
        if confidence >= 0.9:
            severity = 'Critical'
        elif confidence >= 0.75:
            severity = 'High'
        elif confidence >= 0.6:
            severity = 'Medium'
        else:
            severity = 'Low'
        
        threat_types = ['DDoS', 'Malware', 'Brute Force', 'Exploit', 'Reconnaissance']
        threat_type = random.choice(threat_types) if is_threat else 'Normal'
        
        return {
            'is_threat': is_threat,
            'confidence': round(confidence, 4),
            'severity': severity,
            'threat_type': threat_type,
            'raw_prediction': confidence
        }

# Global model service instance
model_service = ModelService()

