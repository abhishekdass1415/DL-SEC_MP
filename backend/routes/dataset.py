from flask import Blueprint, request, jsonify
import os
import sys
from werkzeug.utils import secure_filename

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.dataset_service import dataset_service
from services.data_simulator import data_simulator
from services.model_service import model_service
from services.metrics_service import metrics_service
import logging

# Import socketio from app - will be set by app.py
socketio = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dataset_bp = Blueprint('dataset', __name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(backend_dir, 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dataset_bp.route('/upload', methods=['POST'])
def upload_dataset():
    """Upload and load a dataset file"""
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
        
        # Save file
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
            # Configure data simulator to use dataset
            data_simulator.set_dataset_service(dataset_service)
            # Update high-level metrics
            metrics_service.on_dataset_loaded(result.get('total_records', 0))
            logger.info(f"Dataset loaded successfully: {result.get('total_records', 0)} records")

            return jsonify(result), 200
        else:
            logger.error(f"Dataset load failed: {result.get('error', 'Unknown error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error uploading dataset: {str(e)}", exc_info=True)
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
            
            # If threat detected, create threat record
            is_threat = bool(prediction.get('is_threat'))
            if is_threat:
                from database.models import Threat
                from database.db import db
                from services.action_service import action_service
                
                threat = Threat(
                    threat_type=prediction['threat_type'],
                    severity=prediction['severity'],
                    source_ip=record.get('srcip', record.get('source_ip', 'Unknown')),
                    destination_ip=record.get('dstip', record.get('destination_ip', 'Unknown')),
                    confidence=prediction['confidence'],
                    details=record,
                    status='active'
                )
                
                db.session.add(threat)
                db.session.commit()
                
                # Generate actions
                actions = action_service.generate_actions(threat)
                
                # Emit real-time update
                if socketio:
                    socketio.emit('new_threat', {
                        'threat': threat.to_dict(),
                        'actions': [action.to_dict() for action in actions]
                    })
                
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

                # Create threat if detected
                if prediction.get('is_threat'):
                    from database.models import Threat
                    from database.db import db
                    from services.action_service import action_service
                    
                    threat = Threat(
                        threat_type=prediction['threat_type'],
                        severity=prediction['severity'],
                        source_ip=record.get('srcip', record.get('source_ip', 'Unknown')),
                        destination_ip=record.get('dstip', record.get('destination_ip', 'Unknown')),
                        confidence=prediction['confidence'],
                        details=record,
                        status='active'
                    )
                    
                    db.session.add(threat)
                    db.session.commit()
                    
                    # Generate actions
                    actions = action_service.generate_actions(threat)
                    
                    # Emit real-time update
                    if socketio:
                        socketio.emit('new_threat', {
                            'threat': threat.to_dict(),
                            'actions': [action.to_dict() for action in actions]
                        })
            
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
        use_dataset = data.get('use_dataset', True)
        # Optional explicit source for streaming: 'dataset' | 'api' | 'mock'
        source = data.get('source')
        api_url = data.get('api_url') or data.get('apiUrl')
        
        def process_streaming_data(record_data):
            """Process each streaming data point"""
            try:
                # Make prediction
                prediction = model_service.predict(record_data)
                
                # If threat detected, create threat record
                is_threat = bool(prediction.get('is_threat'))
                if is_threat:
                    from database.models import Threat
                    from database.db import db
                    from services.action_service import action_service
                    
                    threat = Threat(
                        threat_type=prediction['threat_type'],
                        severity=prediction['severity'],
                        source_ip=record_data.get('srcip', record_data.get('source_ip', 'Unknown')),
                        destination_ip=record_data.get('dstip', record_data.get('destination_ip', 'Unknown')),
                        confidence=prediction['confidence'],
                        details=record_data,
                        status='active'
                    )
                    
                    db.session.add(threat)
                    db.session.commit()
                    
                    # Generate actions
                    actions = action_service.generate_actions(threat)
                    
                    # Emit real-time update via WebSocket
                    if socketio:
                        socketio.emit('new_threat', {
                            'threat': threat.to_dict(),
                            'actions': [action.to_dict() for action in actions],
                            'prediction': prediction
                        })
                else:
                    # Emit normal activity (optional)
                    if socketio:
                        socketio.emit('normal_activity', {
                            'record': record_data,
                            'prediction': prediction
                        })

                # Update high-level metrics regardless of threat / normal
                metrics_service.on_record_processed(is_threat=is_threat)
                        
            except Exception as e:
                logger.error(f"Error processing streaming data: {str(e)}")
        
        # Start streaming
        data_simulator.start_streaming(
            process_streaming_data,
            interval,
            use_dataset,
            source=source,
            api_url=api_url,
        )

        # Notify metrics service about the active source
        effective_source = source
        if not effective_source:
            effective_source = "dataset" if use_dataset else "mock"
        metrics_service.on_stream_source_configured(effective_source)

        return jsonify({
            'success': True,
            'message': 'Streaming started',
            'interval': interval,
            'use_dataset': use_dataset,
            'source': effective_source,
            'api_url': api_url,
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting streaming: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/stream/stop', methods=['POST'])
def stop_streaming():
    """Stop streaming dataset"""
    try:
        data_simulator.stop_streaming()
        return jsonify({
            'success': True,
            'message': 'Streaming stopped'
        }), 200
        
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