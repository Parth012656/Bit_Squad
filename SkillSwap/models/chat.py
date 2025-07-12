from extensions import db
from datetime import datetime
class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('ChatMessage', backref='chat_room', lazy=True, order_by='ChatMessage.created_at')
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    
    def get_other_user(self, current_user_id):
        """Get the other user in the chat room"""
        return self.user2 if self.user1_id == current_user_id else self.user1
    
    def get_unread_count(self, user_id):
        """Get unread message count for a user"""
        return ChatMessage.query.filter_by(
            chat_room_id=self.id,
            sender_id=user_id,
            is_read=False
        ).count()
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>' 