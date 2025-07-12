from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import db from extensions
from extensions import db

class PlatformMessage(db.Model):
    __tablename__ = 'platform_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='info')  # 'info', 'warning', 'alert', 'update'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='platform_messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'message_type': self.message_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.creator.name if self.creator else None
        }

class ModerationAction(db.Model):
    __tablename__ = 'moderation_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False)  # 'skill_rejected', 'user_banned', 'user_unbanned', 'skill_approved'
    target_type = db.Column(db.String(20), nullable=False)  # 'skill', 'user', 'exchange'
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    moderator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    moderator = db.relationship('User', backref='moderation_actions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'action_type': self.action_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'moderator': self.moderator.name if self.moderator else None
        }

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # 'inappropriate_skill', 'spam', 'harassment', 'fake_profile'
    target_type = db.Column(db.String(20), nullable=False)  # 'skill', 'user', 'exchange'
    target_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'investigating', 'resolved', 'dismissed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_filed')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='reports_resolved')
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_type': self.report_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'reporter': self.reporter.name if self.reporter else None,
            'resolver': self.resolver.name if self.resolver else None
        } 