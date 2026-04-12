from flask import Blueprint, jsonify, request, current_app
import sys
import os
import json
import threading
import subprocess
from datetime import datetime

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

project_root = os.path.dirname(backend_dir)
train_script = os.path.join(backend_dir, "ml", "train_model.py")
latest_metrics_file = os.path.join(backend_dir, "models", "latest_training_metrics.json")

from services.model_service import model_service
from services.metrics_service import metrics_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_bp = Blueprint('model', __name__)


def _run_training_and_finish(session_id, app):
    """
    Run training script in subprocess, then update TrainingSession and persist metrics.
    Uses app context for DB updates (thread-safe).
    """
    try:
        proc = subprocess.run(
            [sys.executable, train_script],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if proc.returncode != 0:
            logger.error("Training script failed: %s\n%s", proc.stderr, proc.stdout)
            with app.app_context():
                from database.models import TrainingSession
                from database.db import db
                session = TrainingSession.query.get(session_id)
                if session:
                    session.status = "failed"
                    session.end_time = datetime.utcnow()
                    db.session.commit()
            metrics_service.finish_training({})
            return

        if not os.path.isfile(latest_metrics_file):
            logger.warning("Latest metrics file not found after training")
            with app.app_context():
                from database.models import TrainingSession
                from database.db import db
                session = TrainingSession.query.get(session_id)
                if session:
                    session.status = "failed"
                    session.end_time = datetime.utcnow()
                    db.session.commit()
            metrics_service.finish_training({})
            return

        with open(latest_metrics_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        with app.app_context():
            from database.models import TrainingSession, ModelMetrics
            from database.db import db

            session = TrainingSession.query.get(session_id)
            if session:
                session.status = "completed"
                session.end_time = datetime.utcnow()
                db.session.commit()

            mm = ModelMetrics(
                training_id=session_id,
                accuracy=float(data.get("accuracy", 0)),
                precision=float(data.get("precision", 0)),
                recall=float(data.get("recall", 0)),
                f1_score=float(data.get("f1_score", 0)),
                confusion_matrix_json=json.dumps(data.get("confusion_matrix", [])),
            )
            db.session.add(mm)
            db.session.commit()

        m = {
            "accuracy": data.get("accuracy", 0),
            "precision": data.get("precision", 0),
            "recall": data.get("recall", 0),
            "f1": data.get("f1_score", 0),
        }
        metrics_service.finish_training({"cnn_lstm": m, "cnn": m, "lstm": m})

        model_service.load_model()
        logger.info("Training completed and model reloaded")
    except subprocess.TimeoutExpired:
        logger.error("Training script timed out")
        with app.app_context():
            from database.models import TrainingSession
            from database.db import db
            session = TrainingSession.query.get(session_id)
            if session:
                session.status = "failed"
                session.end_time = datetime.utcnow()
                db.session.commit()
        metrics_service.finish_training({})
    except Exception as e:
        logger.exception("Error in training completion: %s", e)
        with app.app_context():
            from database.models import TrainingSession
            from database.db import db
            session = TrainingSession.query.get(session_id)
            if session:
                session.status = "failed"
                session.end_time = datetime.utcnow()
                db.session.commit()
        metrics_service.finish_training({})


@model_bp.route('/status', methods=['GET'])
def model_status():
    """Get model health and status"""
    try:
        is_loaded = model_service.model is not None
        scaler_loaded = model_service.scaler is not None
        fc_loaded = model_service.feature_columns is not None

        return jsonify({
            'model_loaded': is_loaded,
            'scaler_loaded': scaler_loaded,
            'feature_columns_loaded': fc_loaded,
            'status': 'ready' if (is_loaded and scaler_loaded and fc_loaded) else 'mock_mode',
            'message': 'Model is ready for predictions' if (is_loaded and scaler_loaded and fc_loaded) else 'Run training pipeline (python backend/ml/train_model.py) or set USE_MOCK_FALLBACK=true'
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
    """Return current model performance metrics. Prefer latest from DB (ModelMetrics)."""
    try:
        metrics = metrics_service.get_model_metrics(app=current_app)
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


@model_bp.route('/training-status', methods=['GET'])
def training_status():
    """
    Return the current or latest training session status (real-time tracking).
    Duration is elapsed seconds: now - start_time if running, else end_time - start_time.
    """
    try:
        from database.models import TrainingSession

        session = TrainingSession.query.order_by(TrainingSession.start_time.desc()).first()
        if session is None:
            return jsonify({
                "status": "idle",
                "message": "No training session found"
            }), 200

        start = session.start_time
        end = session.end_time
        now = datetime.utcnow()
        if session.status == "running" and end is None:
            duration_seconds = (now - start).total_seconds() if start else None
        elif end is not None and start is not None:
            duration_seconds = (end - start).total_seconds()
        else:
            duration_seconds = None

        payload = {
            "id": session.id,
            "model_name": session.model_name,
            "status": session.status,
            "start_time": start.isoformat() if start else None,
            "end_time": end.isoformat() if end else None,
        }
        if duration_seconds is not None:
            payload["duration_seconds"] = round(duration_seconds, 2)

        return jsonify(payload), 200
    except Exception as e:
        logger.exception("Error getting training status: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@model_bp.route('/retrain', methods=['POST'])
def retrain_models():
    """
    Trigger real model training in background.
    Creates a TrainingSession (status=running) before starting; thread updates it on completion/failure.
    Returns 409 if a session is already running (already_running) or in-memory busy (busy).
    """
    try:
        from database.models import TrainingSession
        from database.db import db

        # Prevent duplicate retraining: latest session still running
        latest = TrainingSession.query.order_by(TrainingSession.start_time.desc()).first()
        if latest is not None and latest.status == "running":
            return jsonify({"status": "already_running"}), 409

        if not metrics_service.start_training():
            return jsonify({
                'status': 'busy',
                'message': 'Training is already in progress'
            }), 409

        if not os.path.isfile(train_script):
            metrics_service.finish_training({})
            return jsonify({
                'status': 'error',
                'message': 'Training script not found: backend/ml/train_model.py'
            }), 500

        # Create session record before starting subprocess (status = running)
        session = TrainingSession(
            model_name="CNN-LSTM",
            start_time=datetime.utcnow(),
            dataset_used="UNSW-NB15",
            status="running",
            end_time=None,
        )
        db.session.add(session)
        db.session.commit()
        session_id = session.id

        app = current_app._get_current_object()
        logger.info("Starting background model training via %s (session_id=%s)", train_script, session_id)
        thread = threading.Thread(target=_run_training_and_finish, args=(session_id, app), daemon=True)
        thread.start()

        return jsonify({
            'status': 'started',
            'message': 'Training started in background. Model and metrics will update when complete.'
        }), 202

    except Exception as e:
        logger.exception("Error starting retrain: %s", e)
        metrics_service.finish_training({})
        return jsonify({'error': str(e)}), 500
