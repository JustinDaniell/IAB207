from flask_login import UserMixin
from . import db
from datetime import datetime

class User(db.Model,UserMixin):
    __tablename__ = 'users' # good practice to specify table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    fname = db.Column(db.String(100), index=True, unique=True, nullable=False)
    lname = db.Column(db.String(100), index=True, unique=True, nullable=False)
    emailid = db.Column(db.String(100), index=True, nullable=False)
    number = db.Column(db.Integer, index=True, unique=True, nullable=False)
    address = db.Column(db.String(100), index=True, nullable=False)
	# password is never stored in the DB, an encrypted password is stored
	# the storage should be at least 255 chars long
    password_hash = db.Column(db.String(255), nullable=False)
    # relation to call user.comments and comment.created_by
    comments = db.relationship('Comment', backref='user')
    
    # string print method
    def __repr__(self):
        return f"Name: {self.name}"

class Event(db.Model,UserMixin):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(400))
    location = db.Column(db.String(100), nullable=False)
    activity = db.Column(db.String(30), nullable=False)
    host_name = db.Column(db.String(100), nullable=False)
    host_experience = db.Column(db.String(200))
    host_contact = db.Column(db.String(100), nullable=False)
    experience_required = db.Column(db.String(100), nullable=False)
	# relations
    comments = db.relationship('Comment', backref='event', lazy='dynamic')
    tickets = db.relationship('Ticket', backref='event')
    status = db.relationship('Status', backref='event')

	# string print method
    def __repr__(self):
        return f"Name: {self.name}"

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())
    # add the foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    
    # string print method
    def __repr__(self):
        return f"Comment: {self.text}"
    
class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float(10), index=True, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    # relations
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def _repr_(self):
        return f"id: {self.id}"
    
class Status(db.Model):
    __tablename__ = 'status'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), index=True, nullable=False)
    avaliable_tickets = db.Column(db.Integer, nullable=False)
    # relation
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), unique=True, nullable=False)

    def _repr_(self):
        return f"Status: {self.status}"
