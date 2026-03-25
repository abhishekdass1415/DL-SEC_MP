from database.db import db
from datetime import datetime

class Threat(db.Model):
    """Threat detection model"""
    __tablename__ = 'threats'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    threat_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # Critical, High, Medium, Low
    source_ip = db.Column(db.String(50))
    destination_ip = db.Column(db.String(50))
    confidence = db.Column(db.Float, nullable=False)  # Model confidence score
    details = db.Column(db.JSON)  # Additional threat details
    status = db.Column(db.String(20), default='active')  # active, resolved, false_positive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to actions
    actions = db.relationship('Action', backref='threat', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'threat_type': self.threat_type,
            'severity': self.severity,
            'source_ip': self.source_ip,
            'destination_ip': self.destination_ip,
            'confidence': self.confidence,
            'details': self.details,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Action(db.Model):
    """Suggested actions for threats"""
    __tablename__ = 'actions'
    
    id = db.Column(db.Integer, primary_key=True)
    threat_id = db.Column(db.Integer, db.ForeignKey('threats.id'), nullable=False)
    suggested_action = db.Column(db.String(200), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # block_ip, alert_admin, isolate, monitor
    priority = db.Column(db.String(20), nullable=False)  # High, Medium, Low
    executed = db.Column(db.Boolean, default=False)
    executed_at = db.Column(db.DateTime)
    execution_result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'threat_id': self.threat_id,
            'suggested_action': self.suggested_action,
            'action_type': self.action_type,
            'priority': self.priority,
            'executed': self.executed,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'execution_result': self.execution_result,
            'created_at': self.created_at.isoformat()
        }

class ThreatHistory(db.Model):
    """History of threat status changes"""
    __tablename__ = 'threat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    threat_id = db.Column(db.Integer, db.ForeignKey('threats.id'), nullable=False)
    status_changes = db.Column(db.JSON)
    action_log = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'threat_id': self.threat_id,
            'status_changes': self.status_changes,
            'action_log': self.action_log,
            'created_at': self.created_at.isoformat()
        }


class TrainingSession(db.Model):
    """Record of a model training run."""
    __tablename__ = 'training_sessions'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False, default='cnn_lstm')
    start_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    end_time = db.Column(db.DateTime)
    dataset_used = db.Column(db.String(500))
    status = db.Column(db.String(50), default='running')  # running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    metrics = db.relationship('ModelMetrics', backref='training_session', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'dataset_used': self.dataset_used,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ModelMetrics(db.Model):
    """Metrics from a training session (one per session)."""
    __tablename__ = 'model_metrics'

    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    confusion_matrix_json = db.Column(db.Text)  # JSON string of 2D list
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'training_id': self.training_id,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'confusion_matrix': self.confusion_matrix_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class StreamingSession(db.Model):
    """Dataset streaming session metadata."""
    __tablename__ = 'streaming_sessions'

    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(1024), nullable=False)
    total_records = db.Column(db.Integer, nullable=False, default=0)
    processed_records = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(50), nullable=False, default='ready')  # ready, streaming, completed, paused, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'dataset_name': self.dataset_name,
            'file_path': self.file_path,
            'total_records': self.total_records,
            'processed_records': self.processed_records,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Alert(db.Model):
    """Security alert derived from model predictions."""
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    attack_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    source_ip = db.Column(db.String(50))
    destination_ip = db.Column(db.String(50))
    confidence = db.Column(db.Float, nullable=False)
    threat_id = db.Column(db.Integer, db.ForeignKey('threats.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'attack_type': self.attack_type,
            'severity': self.severity,
            'source_ip': self.source_ip,
            'destination_ip': self.destination_ip,
            'confidence': self.confidence,
            'threat_id': self.threat_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

