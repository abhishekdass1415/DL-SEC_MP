import os
from pathlib import Path

class Config:
    # Database configuration
    BASE_DIR = Path(__file__).parent
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/threats.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Model configuration
    MODELS_DIR = BASE_DIR / 'models'
    MODEL_PATH = os.getenv('MODEL_PATH', str(MODELS_DIR / 'final_cnn_lstm.keras'))
    SCALER_PATH = os.getenv('SCALER_PATH', str(MODELS_DIR / 'scaler.pkl'))
    
    # Feature configuration
    CATEGORICAL_COLS = ['proto', 'service', 'state']
    NUMERICAL_COLS = None  # Will be set dynamically based on dataset
    
    # API configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

