from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import db from extensions
from extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # swap_request, ban, report, achievement, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional reference to related content
    related_id = db.Column(db.Integer)  # ID of related exchange, report, etc.
    related_type = db.Column(db.String(50))  # Type of related content
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'related_id': self.related_id,
            'related_type': self.related_type
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>' 