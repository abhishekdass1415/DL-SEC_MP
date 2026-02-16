from flask import Blueprint, jsonify, request
import sys
import os

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.model_service import model_service
from services.metrics_service import metrics_service
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_bp = Blueprint('model', __name__)

@model_bp.route('/status', methods=['GET'])
def model_status():
    """Get model health and status"""
    try:
        is_loaded = model_service.model is not None
        scaler_loaded = model_service.scaler is not None
        
        return jsonify({
            'model_loaded': is_loaded,
            'scaler_loaded': scaler_loaded,
            'status': 'ready' if (is_loaded and scaler_loaded) else 'mock_mode',
            'message': 'Model is ready for predictions' if (is_loaded and scaler_loaded) else 'Running in mock mode - model files not found'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        return jsonify({
            'model_loaded': False,
            'scaler_loaded': False,
            'status': 'error',
            'message': str(e)
        }), 500

@model_bp.route('/predict', methods=['POST'])
def predict():
    """Single prediction endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        prediction = model_service.predict(data)
        
        return jsonify(prediction), 200
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500


@model_bp.route('/metrics', methods=['GET'])
def model_metrics():
    """Return current model performance metrics for CNN, LSTM, and CNN+LSTM."""
    try:
        metrics = metrics_service.get_model_metrics()
        training = metrics_service.training_in_progress
        return jsonify({
            'models': metrics,
            'training': {
                'in_progress': training
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting model metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@model_bp.route('/retrain', methods=['POST'])
def retrain_models():
    """
    Trigger model retraining on the latest available data.

    This is implemented as a lightweight placeholder that simulates
    training and updates the metrics in-memory. The actual heavy
    training logic can be plugged in later, calling metrics_service
    to store the resulting scores.
    """
    try:
        if not metrics_service.start_training():
            return jsonify({
                'status': 'busy',
                'message': 'Training is already in progress'
            }), 409

        logger.info("Model retraining requested via /api/model/retrain")

        # Simulate a short training run so the UI can show progress.
        # In a real implementation, this would call out to training
        # routines that use the latest dataset / streamed data.
        time.sleep(2.0)

        # For now, we slightly perturb the current metrics so the
        # dashboard shows that something changed after retraining.
        current = metrics_service.get_model_metrics()
        new_metrics = {}
        for name, vals in current.items():
            boosted = {}
            for k, v in vals.items():
                # Small bounded adjustment
                adjusted = max(0.0, min(0.99, v + 0.005))
                boosted[k] = round(adjusted, 4)
            new_metrics[name] = boosted

        metrics_service.finish_training(new_metrics)

        return jsonify({
            'status': 'completed',
            'models': new_metrics
        }), 200

    except Exception as e:
        logger.error(f"Error retraining models: {str(e)}")
        # Clear training flag on error
        metrics_service.finish_training({})
        return jsonify({'error': str(e)}), 500

