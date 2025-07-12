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
    gender = db.Column(db.String(20))  # male, female, other, prefer_not_to_say
    achievements = db.Column(db.Text)  # JSON string of achievements
    daily_tasks_completed = db.Column(db.Integer, default=0)
    weekly_tasks_completed = db.Column(db.Integer, default=0)
    total_rating = db.Column(db.Float, default=0.0)
    total_ratings_count = db.Column(db.Integer, default=0)
    badge = db.Column(db.String(20), default='bronze')  # bronze, silver, gold
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
    notifications = db.relationship('Notification', backref='user', lazy=True, order_by='Notification.created_at.desc()')
    
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
    
    def update_rating(self, new_rating):
        """Update user's average rating"""
        self.total_ratings_count += 1
        total_rating_sum = (self.total_rating * (self.total_ratings_count - 1)) + new_rating
        self.total_rating = total_rating_sum / self.total_ratings_count
        self.update_badge()
    
    def update_badge(self):
        """Update user badge based on rating and activity"""
        # Calculate total activity score
        total_activity = self.daily_tasks_completed + self.weekly_tasks_completed
        
        # Update badge based on rating and activity
        if self.total_rating >= 4.5 and total_activity >= 30:
            self.badge = 'gold'
        elif self.total_rating >= 4.0 and total_activity >= 15:
            self.badge = 'silver'
        elif self.total_rating >= 3.5 and total_activity >= 5:
            self.badge = 'silver'
        else:
            self.badge = 'bronze'
    
    @classmethod
    def update_all_badges(cls):
        """Update badges for all users"""
        users = cls.query.all()
        for user in users:
            user.update_badge()
        db.session.commit()
    
    def add_achievement(self, achievement):
        """Add a new achievement"""
        import json
        achievements_list = []
        if self.achievements:
            try:
                achievements_list = json.loads(self.achievements)
            except:
                achievements_list = []
        
        achievements_list.append({
            'title': achievement['title'],
            'description': achievement['description'],
            'date': datetime.utcnow().isoformat(),
            'type': achievement.get('type', 'general')
        })
        
        self.achievements = json.dumps(achievements_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'bio': self.bio,
            'location': self.location,
            'gender': self.gender,
            'role': self.role,
            'is_banned': self.is_banned,
            'badge': self.badge,
            'total_rating': self.total_rating,
            'total_ratings_count': self.total_ratings_count,
            'daily_tasks_completed': self.daily_tasks_completed,
            'weekly_tasks_completed': self.weekly_tasks_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.name}>' 