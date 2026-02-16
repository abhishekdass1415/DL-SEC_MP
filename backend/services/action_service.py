from datetime import datetime
import sys
import os

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database.models import Action, Threat
from database.db import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionService:
    """Service for generating and managing threat response actions"""
    
    # Action recommendations based on threat type and severity
    ACTION_RULES = {
        'DDoS': {
            'Critical': [
                {'action': 'Block source IP immediately', 'type': 'block_ip', 'priority': 'High'},
                {'action': 'Enable DDoS protection mode', 'type': 'isolate', 'priority': 'High'},
                {'action': 'Alert network administrator', 'type': 'alert_admin', 'priority': 'High'}
            ],
            'High': [
                {'action': 'Rate limit source IP', 'type': 'monitor', 'priority': 'Medium'},
                {'action': 'Alert security team', 'type': 'alert_admin', 'priority': 'Medium'}
            ],
            'Medium': [
                {'action': 'Monitor source IP activity', 'type': 'monitor', 'priority': 'Low'},
                {'action': 'Log incident for review', 'type': 'alert_admin', 'priority': 'Low'}
            ],
            'Low': [
                {'action': 'Log for analysis', 'type': 'monitor', 'priority': 'Low'}
            ]
        },
        'Malware': {
            'Critical': [
                {'action': 'Isolate affected system', 'type': 'isolate', 'priority': 'High'},
                {'action': 'Block malicious IP addresses', 'type': 'block_ip', 'priority': 'High'},
                {'action': 'Alert security team immediately', 'type': 'alert_admin', 'priority': 'High'}
            ],
            'High': [
                {'action': 'Quarantine suspicious files', 'type': 'isolate', 'priority': 'Medium'},
                {'action': 'Block source IP', 'type': 'block_ip', 'priority': 'Medium'}
            ],
            'Medium': [
                {'action': 'Scan system for malware', 'type': 'monitor', 'priority': 'Medium'},
                {'action': 'Alert administrator', 'type': 'alert_admin', 'priority': 'Low'}
            ],
            'Low': [
                {'action': 'Monitor system activity', 'type': 'monitor', 'priority': 'Low'}
            ]
        },
        'Brute Force': {
            'Critical': [
                {'action': 'Block source IP immediately', 'type': 'block_ip', 'priority': 'High'},
                {'action': 'Lock affected accounts', 'type': 'isolate', 'priority': 'High'},
                {'action': 'Alert security team', 'type': 'alert_admin', 'priority': 'High'}
            ],
            'High': [
                {'action': 'Rate limit login attempts', 'type': 'monitor', 'priority': 'Medium'},
                {'action': 'Block source IP', 'type': 'block_ip', 'priority': 'Medium'}
            ],
            'Medium': [
                {'action': 'Monitor login attempts', 'type': 'monitor', 'priority': 'Low'},
                {'action': 'Alert administrator', 'type': 'alert_admin', 'priority': 'Low'}
            ],
            'Low': [
                {'action': 'Log for review', 'type': 'monitor', 'priority': 'Low'}
            ]
        },
        'Exploit': {
            'Critical': [
                {'action': 'Patch vulnerable system immediately', 'type': 'isolate', 'priority': 'High'},
                {'action': 'Block source IP', 'type': 'block_ip', 'priority': 'High'},
                {'action': 'Alert security team', 'type': 'alert_admin', 'priority': 'High'}
            ],
            'High': [
                {'action': 'Isolate vulnerable system', 'type': 'isolate', 'priority': 'Medium'},
                {'action': 'Block source IP', 'type': 'block_ip', 'priority': 'Medium'}
            ],
            'Medium': [
                {'action': 'Monitor for exploitation attempts', 'type': 'monitor', 'priority': 'Medium'},
                {'action': 'Alert administrator', 'type': 'alert_admin', 'priority': 'Low'}
            ],
            'Low': [
                {'action': 'Review system logs', 'type': 'monitor', 'priority': 'Low'}
            ]
        },
        'Reconnaissance': {
            'Critical': [
                {'action': 'Block source IP', 'type': 'block_ip', 'priority': 'High'},
                {'action': 'Alert security team', 'type': 'alert_admin', 'priority': 'High'}
            ],
            'High': [
                {'action': 'Monitor source IP activity', 'type': 'monitor', 'priority': 'Medium'},
                {'action': 'Block source IP', 'type': 'block_ip', 'priority': 'Medium'}
            ],
            'Medium': [
                {'action': 'Log reconnaissance activity', 'type': 'monitor', 'priority': 'Low'},
                {'action': 'Alert administrator', 'type': 'alert_admin', 'priority': 'Low'}
            ],
            'Low': [
                {'action': 'Log for analysis', 'type': 'monitor', 'priority': 'Low'}
            ]
        },
        'Suspicious Activity': {
            'Critical': [
                {'action': 'Investigate source IP', 'type': 'monitor', 'priority': 'High'},
                {'action': 'Alert security team', 'type': 'alert_admin', 'priority': 'High'}
            ],
            'High': [
                {'action': 'Monitor activity', 'type': 'monitor', 'priority': 'Medium'},
                {'action': 'Alert administrator', 'type': 'alert_admin', 'priority': 'Medium'}
            ],
            'Medium': [
                {'action': 'Log for review', 'type': 'monitor', 'priority': 'Low'}
            ],
            'Low': [
                {'action': 'Log for analysis', 'type': 'monitor', 'priority': 'Low'}
            ]
        }
    }
    
    def generate_actions(self, threat):
        """
        Generate suggested actions for a threat
        Args:
            threat: Threat object
        Returns:
            List of Action objects
        """
        try:
            threat_type = threat.threat_type
            severity = threat.severity
            
            # Get action rules for this threat type
            threat_actions = self.ACTION_RULES.get(threat_type, {})
            severity_actions = threat_actions.get(severity, [])
            
            # If no specific rules, use generic actions
            if not severity_actions:
                severity_actions = self.ACTION_RULES.get('Suspicious Activity', {}).get(severity, [])
            
            # Create action records
            actions = []
            for action_data in severity_actions:
                action = Action(
                    threat_id=threat.id,
                    suggested_action=action_data['action'],
                    action_type=action_data['type'],
                    priority=action_data['priority']
                )
                actions.append(action)
                db.session.add(action)
            
            db.session.commit()
            return actions
            
        except Exception as e:
            logger.error(f"Error generating actions: {str(e)}")
            db.session.rollback()
            return []
    
    def execute_action(self, action_id):
        """
        Execute an action
        Args:
            action_id: ID of the action to execute
        Returns:
            Updated Action object
        """
        try:
            action = Action.query.get(action_id)
            if not action:
                raise ValueError(f"Action with id {action_id} not found")
            
            if action.executed:
                return action
            
            # Simulate action execution
            # In production, this would integrate with actual security systems
            action.executed = True
            action.executed_at = datetime.utcnow()
            
            # Simulate execution result based on action type
            if action.action_type == 'block_ip':
                action.execution_result = f"Successfully blocked IP: {action.threat.source_ip}"
            elif action.action_type == 'isolate':
                action.execution_result = f"System isolated successfully"
            elif action.action_type == 'alert_admin':
                action.execution_result = f"Alert sent to security team"
            elif action.action_type == 'monitor':
                action.execution_result = f"Monitoring enabled for threat #{action.threat_id}"
            else:
                action.execution_result = f"Action executed successfully"
            
            db.session.commit()
            return action
            
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            db.session.rollback()
            raise

# Global action service instance
action_service = ActionService()

