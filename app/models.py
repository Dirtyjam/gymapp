from app import db, jwt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True) 
    phone_number = db.Column(db.String(12), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    is_active = db.Column(db.Boolean, default=True)
    is_trainer = db.Column(db.Boolean, default=False)
    trainer_id = db.Column(db.Integer)
    surname = db.Column(db.String(64))
    name = db.Column(db.String(64))
    patronymic = db.Column(db.String(64))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    gender = db.Column(db.String(16))
    nickname = db.Column(db.String(255))

    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'phone_number': self.phone_number,
            "is_trainer" : self.is_trainer,
            "surname": self.surname,
            "name": self.name,
            "patronymic": self.patronymic,
            "age": self.age,
            "weight": self.weight,
            "height": self.height,
            "gender": self.gender,
            "nickname": self.nickname
        }

    def add_user(self):
        db.session.add(self)
        db.session.commit()

    def put_user(self):
        db.session.commit()
        
    def session_rollback(self):
        db.session.rollback()



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(128))
    duration = db.Column(db.Integer) 
    intensity = db.Column(db.String(64))
    date_time = db.Column(db.DateTime, server_default=func.now())

    trainer = db.relationship('User', foreign_keys=[trainer_id], backref='tasks_given')
    student = db.relationship('User', foreign_keys=[student_id], backref='tasks_received')

    def to_dict(self):
        return {
            "id": self.id,
            "trainer_id": self.trainer_id,
            "student_id": self.student_id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "intensity": self.intensity,
            "date_time": self.date_time.isoformat(),
            "type": self.type
        }
    
    def add_task(self):
        db.session.add(self)
        db.session.commit()

class SummaryReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    difficaulty = db.Column(db.String(128), nullable=False)
    self_health = db.Column(db.String(128), server_default=func.now())
    comment = db.Column(db.Text)
    is_skip = db.Column(db.Boolean, default=False)
    skip_reason = db.Column(db.String(255))
    date = db.Column(db.DateTime, server_default=func.now())

    user = db.relationship('User', backref='summary_reports')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "difficaulty": self.difficaulty,
            "self_health": self.self_health,
            "comment": self.comment,
            "is_skip": self.is_skip,
            "skip_reason": self.skip_reason,
            "date": self.date.isoformat()
        }
    
    def add_report(self):
        db.session.add(self)
        db.session.commit()
