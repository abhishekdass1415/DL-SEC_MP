from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
import sys

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from routes.threats import threats_bp
from routes.actions import actions_bp
from routes.model import model_bp
from routes.dataset import dataset_bp
from routes.report import report_bp
from routes.stream import stream_bp
from routes.analytics import analytics_bp
from services import streaming_service as streaming_service_module
from services.metrics_service import metrics_service
from database.db import init_db, db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
# Force threading mode to avoid eventlet/ssl issues on Windows/Python 3.12+
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

db.init_app(app)

# Set socketio in routes modules
from routes import threats, actions, dataset
threats.socketio = socketio
actions.socketio = socketio
dataset.socketio = socketio

# Set socketio in streaming service
streaming_service_module.socketio = socketio

# Register blueprints
app.register_blueprint(threats_bp, url_prefix='/api/threats')
app.register_blueprint(actions_bp, url_prefix='/api/actions')
app.register_blueprint(model_bp, url_prefix='/api/model')
app.register_blueprint(dataset_bp, url_prefix='/api/dataset')
app.register_blueprint(report_bp, url_prefix='/api/report')
app.register_blueprint(stream_bp, url_prefix='/api/stream')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Unified metrics endpoint for dashboard consumption.
    Model metrics are read from DB (latest TrainingSession) when available.
    """
    from flask import current_app
    payload = metrics_service.get_full_metrics_payload(app=current_app)
    return jsonify(payload), 200

# Initialize database
with app.app_context():
    init_db()

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to threat detection server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("=" * 50)
    print("  Threat Detection Backend Server")
    print("=" * 50)
    print(f"Backend API: http://localhost:5000")
    print(f"WebSocket: ws://localhost:5000")
    print(f"API Status: http://localhost:5000/api/model/status")
    print("=" * 50)
    print("Press CTRL+C to stop the server")
    print("=" * 50)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

