from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    achievements = db.Column(db.Text)
    daily_tasks_completed = db.Column(db.Integer, default=0)
    weekly_tasks_completed = db.Column(db.Integer, default=0)
    total_rating = db.Column(db.Float, default=0.0)
    total_ratings_count = db.Column(db.Integer, default=0)
    badge = db.Column(db.String(20), default='bronze')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    profile_photo = db.Column(db.String(255), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.Text)
    banned_at = db.Column(db.DateTime)
    banned_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    skills = db.relationship('Skill', backref='user', lazy=True)
    exchanges_offered = db.relationship('Exchange', foreign_keys='Exchange.offering_user_id', backref='offering_user', lazy=True)
    exchanges_requested = db.relationship('Exchange', foreign_keys='Exchange.requesting_user_id', backref='requesting_user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, order_by='Notification.created_at.desc()')
    
    chat_rooms_user1 = db.relationship('ChatRoom', foreign_keys='ChatRoom.user1_id', backref='user1_rel', lazy=True)
    chat_rooms_user2 = db.relationship('ChatRoom', foreign_keys='ChatRoom.user2_id', backref='user2_rel', lazy=True)
    chat_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.sender_id', backref='sender_rel', lazy=True)
    
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
        """Update user badge based on rating only"""
        if self.total_rating >= 4.5:
            self.badge = 'gold'
        elif self.total_rating >= 4.0:
            self.badge = 'silver'
        else:
            self.badge = 'bronze'
    
    @classmethod
    def update_all_badges(cls):
        """Update badges for all users based on ratings only"""
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
    
    def get_chat_rooms(self):
        """Get all chat rooms for this user"""
        from models.chat import ChatRoom
        return ChatRoom.query.filter(
            db.or_(
                ChatRoom.user1_id == self.id,
                ChatRoom.user2_id == self.id
            )
        ).order_by(ChatRoom.last_message_at.desc()).all()
    
    def get_or_create_chat_room(self, other_user_id):
        """Get existing chat room or create new one with another user"""
        from models.chat import ChatRoom
        existing_room = ChatRoom.query.filter(
            db.or_(
                db.and_(ChatRoom.user1_id == self.id, ChatRoom.user2_id == other_user_id),
                db.and_(ChatRoom.user1_id == other_user_id, ChatRoom.user2_id == self.id)
            )
        ).first()
        
        if existing_room:
            return existing_room
        
        new_room = ChatRoom(user1_id=self.id, user2_id=other_user_id)
        db.session.add(new_room)
        db.session.commit()
        return new_room
    
    def get_unread_chat_count(self):
        """Get total unread messages count"""
        from models.chat import ChatMessage, ChatRoom
        return ChatMessage.query.join(ChatRoom).filter(
            db.and_(
                ChatMessage.sender_id != self.id,
                ChatMessage.is_read == False,
                db.or_(
                    ChatRoom.user1_id == self.id,
                    ChatRoom.user2_id == self.id
                )
            )
        ).count()
    
    def get_availability(self):
        """Get user's availability schedule"""
        from models.availability import Availability
        return Availability.query.filter_by(user_id=self.id, is_available=True).order_by(
            db.case(
                (Availability.day_of_week == 'Monday', 1),
                (Availability.day_of_week == 'Tuesday', 2),
                (Availability.day_of_week == 'Wednesday', 3),
                (Availability.day_of_week == 'Thursday', 4),
                (Availability.day_of_week == 'Friday', 5),
                (Availability.day_of_week == 'Saturday', 6),
                (Availability.day_of_week == 'Sunday', 7)
            )
        ).all()
    
    def set_availability(self, day_of_week, start_time, end_time, is_available=True):
        """Set availability for a specific day and time"""
        from models.availability import Availability
        
        existing = Availability.query.filter_by(
            user_id=self.id, 
            day_of_week=day_of_week
        ).first()
        
        if existing:
            existing.start_time = start_time
            existing.end_time = end_time
            existing.is_available = is_available
        else:
            availability = Availability(
                user_id=self.id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                is_available=is_available
            )
            db.session.add(availability)
        
        db.session.commit()
    
    def is_available_at(self, day_of_week, time_slot):
        """Check if user is available at a specific day and time"""
        from models.availability import Availability
        from datetime import time
        
        availability = Availability.query.filter_by(
            user_id=self.id,
            day_of_week=day_of_week,
            is_available=True
        ).first()
        
        if not availability:
            return False
        
        if isinstance(time_slot, str):
            hour, minute = map(int, time_slot.split(':'))
            time_slot = time(hour, minute)
        
        return availability.start_time <= time_slot <= availability.end_time
    
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