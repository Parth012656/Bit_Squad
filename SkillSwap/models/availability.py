from extensions import db
from datetime import datetime, time
class Availability(db.Model):
    __tablename__ = 'availabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='availabilities')
    
    def to_dict(self):
        return {
            'id': self.id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'is_available': self.is_available
        }
    
    def __repr__(self):
        return f'<Availability {self.day_of_week} {self.start_time}-{self.end_time}>'
class ExchangeSchedule(db.Model):
    __tablename__ = 'exchange_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchanges.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200))
    meeting_type = db.Column(db.String(20), default='in_person')
    meeting_link = db.Column(db.String(500))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    exchange = db.relationship('Exchange', backref='schedules')
    
    def to_dict(self):
        return {
            'id': self.id,
            'exchange_id': self.exchange_id,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'location': self.location,
            'meeting_type': self.meeting_type,
            'meeting_link': self.meeting_link,
            'notes': self.notes,
            'status': self.status
        } 