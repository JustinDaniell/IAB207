from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    _tablename_ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # relations
    comments = db.relationship('Comment', backref='user')
    tickets = db.relationship('Ticket', backref='user')

    # string print method
    def _repr_(self):
        return f"Name: {self.name}"

class Event(db.Model):
    _tablename_ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(400))
    location = db.Column(db.String(100), nullable=False)
    activity = db.Column(db.String(30), nullable=False)
    host_name = db.Column(db.String(100), nullable=False)
    host_experience = db.Column(db.String(200))
    host_contact = db.Column(db.String(100), nullable=False)
	# relations
    comments = db.relationship('Comment', backref='event', lazy='dynamic')
    tickets = db.relationship('Ticket', backref='event')
    status = db.relationship('Status', backref='event')

    # string print method
    def to_dict(self):
        e_dict = {
            b.name: str(getattr(self, b.name)) for b in self._table_.columns
        }
        e_tickets = []
        # Add details of related tickets to the Hotel's h_dict
        for ticket in self.tickets:
            ticket_data = {
                'id': ticket.id,
                'ticket_price': ticket.price,
                'ticket_date': ticket.event_date,
                'ticket_ST': ticket.start_time,
                'ticket_ET': ticket.end_time,
            }
            e_tickets.append(ticket_data)
        e_dict['event'] = e_tickets
        return e_dict

class Comment(db.Model):
    _tablename_ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    posted_date = db.Column(db.DateTime, default=datetime.now())
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    # string print method
    def _repr_(self):
        return f"Comment: {self.text}"

class Ticket(db.Model):
    _tablename_ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float(10), index=True, nullable=False)
    event_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    # relations
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def _repr_(self):
        return f"id: {self.id}"

class Status(db.Model):
    _tablename_ = 'status'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Float(10), index=True, nullable=False)
    ticket_count = db.Column(db.Date)
    # relation
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), unique=True, nullable=False)

    def _repr_(self):
        return f"Status: {self.status}"

    
