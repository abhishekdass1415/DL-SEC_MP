from flask import Blueprint, request, jsonify
import sys
import os

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database.models import Action
from database.db import db
from services.action_service import action_service
import logging

# Import socketio from app - will be set by app.py
socketio = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

actions_bp = Blueprint('actions', __name__)

@actions_bp.route('/<int:action_id>', methods=['GET'])
def get_action(action_id):
    """Get a specific action by ID"""
    try:
        action = Action.query.get(action_id)
        
        if not action:
            return jsonify({'error': 'Action not found'}), 404
        
        return jsonify(action.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error getting action: {str(e)}")
        return jsonify({'error': str(e)}), 500

@actions_bp.route('/<int:action_id>/execute', methods=['POST'])
def execute_action(action_id):
    """Execute an action on a threat"""
    try:
        action = action_service.execute_action(action_id)
        
        # Emit update via WebSocket
        if socketio:
            socketio.emit('action_executed', action.to_dict())
        
        return jsonify({
            'success': True,
            'action': action.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error executing action: {str(e)}")
        return jsonify({'error': str(e)}), 500

@actions_bp.route('/threat/<int:threat_id>', methods=['GET'])
def get_threat_actions(threat_id):
    """Get all actions for a specific threat"""
    try:
        actions = Action.query.filter_by(threat_id=threat_id).all()
        
        return jsonify({
            'threat_id': threat_id,
            'actions': [action.to_dict() for action in actions]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting threat actions: {str(e)}")
        return jsonify({'error': str(e)}), 500

