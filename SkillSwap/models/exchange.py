from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import db from extensions
from extensions import db

class Exchange(db.Model):
    __tablename__ = 'exchanges'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Completed, Cancelled
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def update_timestamp(self):
        """Safely update the timestamp without affecting other fields"""
        self.updated_at = datetime.utcnow()
    completed_at = db.Column(db.DateTime)
    rating = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    offering_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requesting_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    offered_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    requested_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'message': self.message,
            'offering_user_id': self.offering_user_id,
            'requesting_user_id': self.requesting_user_id,
            'offered_skill_id': self.offered_skill_id,
            'requested_skill_id': self.requested_skill_id,
            'offering_user_name': self.offering_user.name if self.offering_user else None,
            'requesting_user_name': self.requesting_user.name if self.requesting_user else None,
            'offered_skill_name': self.offered_skill.name if self.offered_skill else None,
            'requested_skill_name': self.requested_skill.name if self.requested_skill else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<Exchange {self.id}: {self.offering_user.name} -> {self.requesting_user.name}>' 