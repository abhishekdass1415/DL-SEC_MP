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

