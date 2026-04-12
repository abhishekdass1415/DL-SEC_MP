import os
from pathlib import Path

class Config:
    # Database configuration
    BASE_DIR = Path(__file__).parent
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/threats.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Model configuration
    MODELS_DIR = BASE_DIR / 'models'
    MODEL_PATH = os.getenv('MODEL_PATH', str(MODELS_DIR / 'cnn_lstm_model.h5'))
    SCALER_PATH = os.getenv('SCALER_PATH', str(MODELS_DIR / 'scaler.pkl'))
    FEATURE_COLUMNS_PATH = os.getenv('FEATURE_COLUMNS_PATH', str(MODELS_DIR / 'feature_columns.pkl'))
    # Optional: set to true to allow mock prediction when model/artifacts missing
    USE_MOCK_FALLBACK = os.getenv('USE_MOCK_FALLBACK', 'false').lower() in ('1', 'true', 'yes')
    
    # Feature configuration
    CATEGORICAL_COLS = ['proto', 'service', 'state']
    NUMERICAL_COLS = None  # Will be set dynamically based on dataset
    
    # API configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

