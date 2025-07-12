from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import db from extensions
from extensions import db

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), default='Beginner')  # Beginner, Intermediate, Advanced, Expert
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    exchanges_offered = db.relationship('Exchange', foreign_keys='Exchange.offered_skill_id', backref='offered_skill', lazy=True)
    exchanges_requested = db.relationship('Exchange', foreign_keys='Exchange.requested_skill_id', backref='requested_skill', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'is_available': self.is_available,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Skill {self.name}>' 