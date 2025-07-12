from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Import db from extensions
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    profile_photo = db.Column(db.String(255), nullable=True)  # URL or filename
    is_public = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')  # 'user', 'admin', 'moderator'
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.Text)
    banned_at = db.Column(db.DateTime)
    banned_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    skills = db.relationship('Skill', backref='user', lazy=True)
    exchanges_offered = db.relationship('Exchange', foreign_keys='Exchange.offering_user_id', backref='offering_user', lazy=True)
    exchanges_requested = db.relationship('Exchange', foreign_keys='Exchange.requesting_user_id', backref='requesting_user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role in ['admin', 'moderator']
    
    def ban_user(self, reason, banned_by_user):
        self.is_banned = True
        self.ban_reason = reason
        self.banned_at = datetime.utcnow()
        self.banned_by = banned_by_user.id
    
    def unban_user(self):
        self.is_banned = False
        self.ban_reason = None
        self.banned_at = None
        self.banned_by = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'bio': self.bio,
            'location': self.location,
            'role': self.role,
            'is_banned': self.is_banned,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.name}>' 