#threats.py
from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database.models import Threat, Prediction
from database.db import db
from services.model_service import model_service
from services.action_service import action_service
import logging

# Import socketio from app - will be set by app.py
socketio = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

threats_bp = Blueprint('threats', __name__)

@threats_bp.route('/detect', methods=['POST'])
def detect_threat():
    """Real-time threat detection endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Make prediction using model
        prediction = model_service.predict(data)

        is_threat = bool(prediction.get('is_threat'))
        threat = None

        if is_threat:
            # Create threat record
            threat = Threat(
                threat_type=prediction['threat_type'],
                severity=prediction['severity'],
                source_ip=data.get('srcip', data.get('source_ip', 'Unknown')),
                destination_ip=data.get('dstip', data.get('destination_ip', 'Unknown')),
                confidence=prediction['confidence'],
                details=data,
                status='active'
            )
            db.session.add(threat)
            db.session.flush()

        # Log prediction for analytics
        pred_row = Prediction(
            source_type='realtime',
            session_id=None,
            threat_id=threat.id if threat else None,
            is_threat=is_threat,
            label='attack' if is_threat else 'benign',
            severity=prediction.get('severity'),
            attack_type=prediction.get('threat_type'),
            confidence=float(prediction.get('confidence', 0.0) or 0.0),
            raw_score=float(prediction.get('raw_prediction', 0.0) or 0.0),
            source_ip=data.get('srcip', data.get('source_ip', 'Unknown')),
            destination_ip=data.get('dstip', data.get('destination_ip', 'Unknown')),
        )
        db.session.add(pred_row)
        db.session.commit()

        if is_threat:
            # Generate suggested actions
            actions = action_service.generate_actions(threat)
            
            # Emit real-time update via WebSocket
            if socketio:
                socketio.emit('new_threat', {
                    'threat': threat.to_dict(),
                    'actions': [action.to_dict() for action in actions]
                })
            
            return jsonify({
                'threat_detected': True,
                'threat': threat.to_dict(),
                'actions': [action.to_dict() for action in actions],
                'prediction': prediction
            }), 201
        else:
            return jsonify({
                'threat_detected': False,
                'prediction': prediction
            }), 200
            
    except Exception as e:
        logger.error(f"Error in threat detection: {str(e)}")
        return jsonify({'error': str(e)}), 500

@threats_bp.route('', methods=['GET'])
def get_threats():
    """Get all threats with optional filtering"""
    try:
        status = request.args.get('status', 'active')
        limit = request.args.get('limit', 50, type=int)
        severity = request.args.get('severity')
        
        query = Threat.query
        
        if status:
            query = query.filter(Threat.status == status)
        
        if severity:
            query = query.filter(Threat.severity == severity)
        
        threats = query.order_by(Threat.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'threats': [threat.to_dict() for threat in threats],
            'count': len(threats)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting threats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@threats_bp.route('/<int:threat_id>', methods=['GET'])
def get_threat(threat_id):
    """Get a specific threat by ID"""
    try:
        threat = Threat.query.get(threat_id)
        
        if not threat:
            return jsonify({'error': 'Threat not found'}), 404
        
        return jsonify(threat.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error getting threat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@threats_bp.route('/<int:threat_id>/actions', methods=['GET'])
def get_threat_actions(threat_id):
    """Get suggested actions for a specific threat"""
    try:
        threat = Threat.query.get(threat_id)
        
        if not threat:
            return jsonify({'error': 'Threat not found'}), 404
        
        actions = threat.actions
        
        return jsonify({
            'threat_id': threat_id,
            'actions': [action.to_dict() for action in actions]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting threat actions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@threats_bp.route('/<int:threat_id>', methods=['PATCH'])
def update_threat(threat_id):
    """Update threat status"""
    try:
        threat = Threat.query.get(threat_id)
        
        if not threat:
            return jsonify({'error': 'Threat not found'}), 404
        
        data = request.get_json()
        
        if 'status' in data:
            threat.status = data['status']
            threat.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Emit update via WebSocket
        if socketio:
            socketio.emit('threat_updated', threat.to_dict())
        
        return jsonify(threat.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error updating threat: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@threats_bp.route('/realtime', methods=['GET'])
def realtime_threats():
    """Server-Sent Events endpoint for real-time threat updates"""
    from flask import Response
    import json
    
    def generate():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected'})}\n\n"
        
        # In a real implementation, you would stream new threats here
        # For now, this is a placeholder for SSE implementation
    
    return Response(generate(), mimetype='text/event-stream')

