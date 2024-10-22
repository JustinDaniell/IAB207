from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    _tablename_ = 'users' # good practice to specify table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
	#password is never stored in the DB, an encrypted password is stored
	# the storage should be at least 255 chars long
    password_hash = db.Column(db.String(255), nullable=False)
    # relation to call user.comments and comment.created_by
    comments = db.relationship('Comment', backref='user')

    # string print method
    def _repr_(self):
        return f"Name: {self.name}"

class Event(db.Model):
    _tablename_ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(200))
    image = db.Column(db.String(400))
    location = db.Column(db.String(100))
    activity = db.Column(db.String(30))
    host_name = db.Column(db.String(100))
    host_experience = db.Column(db.String(200))
    host_contact = db.Column(db.String(100))
    # ... Create the Comments db.relationship
	# relation to call destination.comments and comment.destination
    comments = db.relationship('Comment', backref='destination')
    tickets = db.relationship('Ticket', backref='hotel', lazy='dynamic')
	# string print method

    def to_dict(self):
        h_dict = {
            b.name: str(getattr(self, b.name)) for b in self._table_.columns
        }
        h_tickets = []
        # Add details of related Rooms to the Hotel's h_dict
        for ticket in self.tickets:
            ticket_data = {
                'id': ticket.id,
                'ticket_avaliability': ticket.avaliability,
                'ticket_price': ticket.price,
                'room_description': room.description,
                'room_rate': room.rate,
                'hotel_id': room.hotel_id
            }
            h_tickets.append(room_data)
        h_dict['rooms'] = h_tickets
        return h_dict

class Comment(db.Model):
    _tablename_ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    posted_date = db.Column(db.DateTime, default=datetime.now())
    # add the foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def _repr_(self):
        return f"Comment: {self.text}"

class Ticket(db.Model):
    _tablename_ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float(10), index=True, nullable=False)
    event_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    # Define the one-to-many relationship with the Room model
    event_id = db.relationship('Event', backref='hotel', lazy='dynamic')
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'))