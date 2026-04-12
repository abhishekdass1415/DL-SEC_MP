from flask import Blueprint, request, jsonify
import os
import sys
import threading
from werkzeug.utils import secure_filename

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.dataset_service import dataset_service
from services.data_simulator import data_simulator
from services.model_service import model_service
from services.metrics_service import metrics_service
from services.streaming_service import streaming_service
from database.models import StreamingSession, Alert, Threat, Prediction
from database.db import db
import logging

# Import socketio from app - will be set by app.py
socketio = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dataset_bp = Blueprint('dataset', __name__)

# Configure upload folder (datasets directory as persistent storage)
UPLOAD_FOLDER = os.path.join(backend_dir, 'datasets')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import hashlib
def _get_pseudo_ip(record, threat_type=None, is_source=True):
    """Generate a consistent mock IP to group missing attributes."""
    ip = record.get('srcip' if is_source else 'dstip') or record.get('source_ip' if is_source else 'destination_ip')
    if ip and ip != 'Unknown':
        return ip
        
    base_string = str(threat_type if threat_type else record.get('id', 'unknown'))
    if not is_source:
        base_string += "_dest"
        
    hash_val = int(hashlib.md5(base_string.encode()).hexdigest(), 16)
    prefix = "192.168.1." if is_source else "10.0.0."
    return f"{prefix}{(hash_val % 254) + 1}"


def _make_json_serializable(obj):
    """Convert numpy/pandas types to native Python so jsonify() never blocks or fails."""
    import numpy as np
    if hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_json_serializable(v) for v in obj]
    return obj


@dataset_bp.route('/upload', methods=['POST'])
def upload_dataset():
    """Upload and load a dataset file"""
    import time
    start_time = time.time()

    try:
        logger.info("Upload request received")
        
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Only CSV and Excel files are allowed'}), 400
        
        # Save file into backend/datasets
        logger.info(f"Saving file: {file.filename}")
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        logger.info(f"File saved to: {file_path}")
        
        # Load dataset
        logger.info("Loading dataset...")
        result = dataset_service.load_dataset(file_path)
        logger.info(f"Dataset load result: {result.get('success', False)}")
        
        if result['success']:
            total_records = int(result.get('total_records', 0))

            # Configure data simulator to use dataset
            data_simulator.set_dataset_service(dataset_service)

            # Create a StreamingSession record for this dataset
            dataset_name = filename
            try:
                session = StreamingSession(
                    dataset_name=dataset_name,
                    file_path=file_path,
                    total_records=total_records,
                    processed_records=0,
                    status='ready',
                )
                db.session.add(session)
                db.session.commit()
                session_id = session.id
            except Exception as e:
                logger.error(f"Failed to create StreamingSession: {e}", exc_info=True)
                db.session.rollback()
                session_id = None

            # Update high-level metrics in a background thread so upload stays non-blocking
            def update_metrics_async(total_records_inner: int) -> None:
                try:
                    metrics_service.on_dataset_loaded(total_records_inner)
                except Exception as exc:
                    logger.error(f"Metrics update failed: {exc}")

            threading.Thread(
                target=update_metrics_async,
                args=(total_records,),
                daemon=True,
            ).start()

            logger.info(f"Dataset loaded successfully: {total_records} records")

            processing_time = time.time() - start_time
            logger.info(f"Upload processing time: {processing_time:.2f} seconds")

            # Build response with JSON-serializable values only (avoid numpy types blocking jsonify)
            response_payload = {
                'success': True,
                'file_path': str(result.get('file_path', '')),
                'total_records': total_records,
                'columns': list(result.get('columns', [])),
                'sample_record': _make_json_serializable(result.get('sample_record', {})),
                # Streaming session metadata for new pipeline
                'dataset_name': dataset_name,
                'session_id': session_id,
            }
            logger.info("Returning upload response 200")
            return jsonify(response_payload), 200
        else:
            logger.error(f"Dataset load failed: {result.get('error', 'Unknown error')}")
            processing_time = time.time() - start_time
            logger.info(f"Upload processing time (failed): {processing_time:.2f} seconds")
            response_payload = {'success': False, 'error': str(result.get('error', 'Unknown error'))}
            return jsonify(response_payload), 500

    except Exception as e:
        logger.error(f"Error uploading dataset: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        logger.info(f"Upload processing time (exception): {processing_time:.2f} seconds")
        return jsonify({'error': str(e)}), 500


@dataset_bp.route('/load', methods=['POST'])
def load_dataset():
    """Load dataset from file path"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400
        
        # Load dataset
        result = dataset_service.load_dataset(file_path)
        
        if result['success']:
            # Configure data simulator to use dataset
            data_simulator.set_dataset_service(dataset_service)
            # Update high-level metrics
            metrics_service.on_dataset_loaded(result.get('total_records', 0))

            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/stats', methods=['GET'])
def get_dataset_stats():
    """Get dataset statistics"""
    try:
        stats = dataset_service.get_dataset_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting dataset stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/sample', methods=['GET'])
def get_sample_records():
    """Get sample records from the dataset"""
    try:
        n = request.args.get('n', 5, type=int)
        samples = dataset_service.get_sample_records(n)
        return jsonify({'samples': samples}), 200
        
    except Exception as e:
        logger.error(f"Error getting sample records: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/process', methods=['POST'])
def process_dataset():
    """Process a single record or batch from the dataset"""
    try:
        data = request.get_json()
        batch_size = data.get('batch_size', 1)
        
        if batch_size == 1:
            # Process single record
            record = dataset_service.get_next_record()
            if record is None:
                return jsonify({'error': 'No more records'}), 404
            
            # Make prediction
            prediction = model_service.predict(record)
            is_threat = bool(prediction.get('is_threat'))

            threat = None
            if is_threat:
                from services.action_service import action_service

                threat = Threat(
                    threat_type=prediction['threat_type'],
                    severity=prediction['severity'],
                    source_ip=_get_pseudo_ip(record, prediction['threat_type'], True),
                    destination_ip=_get_pseudo_ip(record, prediction['threat_type'], False),
                    confidence=prediction['confidence'],
                    details=record,
                    status='active'
                )
                db.session.add(threat)
                db.session.flush()

                alert = Alert(
                    attack_type=prediction['threat_type'],
                    severity=prediction['severity'],
                    source_ip=threat.source_ip,
                    destination_ip=threat.destination_ip,
                    confidence=prediction['confidence'],
                    threat_id=threat.id,
                )
                db.session.add(alert)

            # Log prediction row
            pred_row = Prediction(
                source_type='dataset',
                session_id=None,
                threat_id=threat.id if threat else None,
                is_threat=is_threat,
                label='attack' if is_threat else 'benign',
                severity=prediction.get('severity'),
                attack_type=prediction.get('threat_type'),
                confidence=float(prediction.get('confidence', 0.0) or 0.0),
                raw_score=float(prediction.get('raw_prediction', 0.0) or 0.0),
                source_ip=_get_pseudo_ip(record, prediction.get('threat_type'), True),
                destination_ip=_get_pseudo_ip(record, prediction.get('threat_type'), False),
            )
            db.session.add(pred_row)
            db.session.commit()

            if is_threat:
                from services.action_service import action_service

                # Generate actions
                actions = action_service.generate_actions(threat)
                
                # Emit real-time updates
                if socketio:
                    socketio.emit('new_threat', {
                        'threat': threat.to_dict(),
                        'actions': [action.to_dict() for action in actions],
                        'prediction': prediction,
                    })
                    socketio.emit('alert', alert.to_dict())
                
                # Update high-level metrics
                metrics_service.on_record_processed(is_threat=True)

                return jsonify({
                    'record': record,
                    'prediction': prediction,
                    'threat': threat.to_dict(),
                    'actions': [action.to_dict() for action in actions]
                }), 200
            else:
                # Update high-level metrics for non-threat record
                metrics_service.on_record_processed(is_threat=False)

                return jsonify({
                    'record': record,
                    'prediction': prediction,
                    'threat_detected': False
                }), 200
        else:
            # Process batch
            batch = dataset_service.get_batch(batch_size)
            results = []
            
            for record in batch:
                prediction = model_service.predict(record)
                results.append({
                    'record': record,
                    'prediction': prediction
                })

                is_threat = bool(prediction.get('is_threat'))
                # Update high-level metrics per record
                metrics_service.on_record_processed(is_threat=is_threat)

                # Create threat + alert + prediction if detected, else prediction only
                threat = None
                if is_threat:
                    from services.action_service import action_service
                    
                    threat = Threat(
                        threat_type=prediction['threat_type'],
                        severity=prediction['severity'],
                        source_ip=_get_pseudo_ip(record, prediction['threat_type'], True),
                        destination_ip=_get_pseudo_ip(record, prediction['threat_type'], False),
                        confidence=prediction['confidence'],
                        details=record,
                        status='active'
                    )
                    db.session.add(threat)
                    db.session.flush()

                    alert = Alert(
                        attack_type=prediction['threat_type'],
                        severity=prediction['severity'],
                        source_ip=threat.source_ip,
                        destination_ip=threat.destination_ip,
                        confidence=prediction['confidence'],
                        threat_id=threat.id,
                    )
                    db.session.add(alert)

                    # Generate actions
                    actions = action_service.generate_actions(threat)

                    if socketio:
                        socketio.emit('new_threat', {
                            'threat': threat.to_dict(),
                            'actions': [action.to_dict() for action in actions]
                        })
                        socketio.emit('alert', alert.to_dict())

                pred_row = Prediction(
                    source_type='dataset',
                    session_id=None,
                    threat_id=threat.id if threat else None,
                    is_threat=is_threat,
                    label='attack' if is_threat else 'benign',
                    severity=prediction.get('severity'),
                    attack_type=prediction.get('threat_type'),
                    confidence=float(prediction.get('confidence', 0.0) or 0.0),
                    raw_score=float(prediction.get('raw_prediction', 0.0) or 0.0),
                    source_ip=_get_pseudo_ip(record, prediction.get('threat_type'), True),
                    destination_ip=_get_pseudo_ip(record, prediction.get('threat_type'), False),
                )
                db.session.add(pred_row)
                db.session.commit()
            
            return jsonify({
                'processed': len(results),
                'results': results
            }), 200
            
    except Exception as e:
        logger.error(f"Error processing dataset: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/stream/start', methods=['POST'])
def start_streaming():
    """Start streaming dataset in real-time"""
    try:
        data = request.get_json() or {}
        interval = data.get('interval', 2.0)
        # Optional explicit source for streaming: 'dataset' | 'api' | 'mock'
        source = data.get('source') or ('dataset' if data.get('use_dataset', True) else 'mock')
        api_url = data.get('api_url') or data.get('apiUrl')
        session_id = data.get('session_id')
        from flask import current_app
        app_obj = current_app._get_current_object()
        result = streaming_service.start(
            app=app_obj,
            interval=interval,
            source=source,
            api_url=api_url,
            session_id=session_id,
        )

        if not result.get("success"):
            return jsonify(result), 409

        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error starting streaming: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/stream/stop', methods=['POST'])
def stop_streaming():
    """Stop streaming dataset"""
    try:
        result = streaming_service.pause()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error stopping streaming: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/stream/status', methods=['GET'])
def get_streaming_status():
    """Get streaming status"""
    try:
        status = data_simulator.get_status()
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error getting streaming status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/reset', methods=['POST'])
def reset_dataset():
    """Reset dataset stream to beginning"""
    try:
        dataset_service.reset_stream()
        metrics_service.reset()
        return jsonify({
            'success': True,
            'message': 'Dataset stream reset'
        }), 200
        
    except Exception as e:
        logger.error(f"Error resetting dataset: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dataset_bp.route('/configure-stream', methods=['POST'])
def configure_stream():
    """
    Configure the streaming source.

    This endpoint supports switching between:
      - Dataset upload (`source: 'dataset'`)
      - External API (`source: 'api'`, with `apiUrl`)
      - Mock generator (`source: 'mock'`)

    It does NOT start streaming by itself – the client must still
    call /stream/start afterwards.
    """
    try:
        data = request.get_json() or {}
        source = data.get('source', 'dataset')
        api_url = data.get('api_url') or data.get('apiUrl')
        interval = data.get('interval', 2.0)

        # Configure simulator (it remembers the last source/api_url)
        data_simulator.configure(source=source, api_url=api_url, interval=interval)

        # Update high-level metrics
        metrics_service.on_stream_source_configured(source)

        return jsonify({
            'success': True,
            'message': 'Stream configuration updated',
            'source': source,
            'api_url': api_url,
            'interval': interval,
        }), 200
        
    except Exception as e:
        logger.error(f"Error configuring stream: {str(e)}")
        return jsonify({'error': str(e)}), 500