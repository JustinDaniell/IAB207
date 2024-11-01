from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Ticket, Status, Order
from .forms import EventForm, TicketForm
from flask_login import current_user, login_required
from wtforms.validators import ValidationError
from . import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import func

mainbp = Blueprint('main', __name__)

def check_upload_file(form):
  # get file data from form  
  fp = form.image.data
  filename = fp.filename
  # get the current path of the module file… store image file relative to this path  
  BASE_PATH = os.path.dirname(__file__)
  # upload file location – directory of this file/static/image
  upload_path = os.path.join(BASE_PATH, 'static/image', secure_filename(filename))
  # store relative path in DB as image location in HTML is relative
  db_upload_path = '/static/image/' + secure_filename(filename)
  # save the file and return the db upload path  
  fp.save(upload_path)
  return db_upload_path


@mainbp.route('/')
def index():
    # Start with all events
    events_query = db.session.query(Event).join(Ticket).options(joinedload(Event.tickets))
    events_temp = db.session.scalars(db.select(Event).limit(3)).all()
    # Get filter parameters from the request
    activity_filters = request.args.getlist('activity')
    status_filters = request.args.getlist('status')
    proficiency_filters = request.args.getlist('proficiency')

    # Apply filters to the query if provided
    if activity_filters:
        events_query = events_query.filter(Event.activity.in_(activity_filters))

    if status_filters:
        events_query = events_query.join(Status).filter(Status.status.in_(status_filters))

    if proficiency_filters:
        events_query = events_query.filter(Event.experience_required.in_(proficiency_filters))


    # Check for search query
    search_query = request.args.get('search')
    if search_query and search_query != "":
        query = "%" + search_query + "%"
        events_query = events_query.filter(
            (Event.description.like(query)) |
            (Event.name.like(query))
        )

    # Execute the query and get the results
    events = events_query.all()
    for event in events:
        print(event.status[0].status)
    # Order by `start_date` and limit to the first 3 results
    return render_template('index.html', events=events, events_temp=events_temp)  


@mainbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  event_id = request.args.get('event_id')
  show_event = db.session.scalar(db.select(Event).where(Event.id == event_id))
  show_tickets = db.session.scalars(db.select(Ticket).where(Ticket.event_id == event_id, Ticket.user_id == None)).all()
  show_status = db.session.scalar(db.select(Status).where(Status.event_id == event_id))
  form = EventForm()
  if show_tickets: # if there are tickets, prefill the tickets in form
    form.start_date.data = show_tickets[0].start_date
    form.end_date.data = show_tickets[0].end_date
    form.start_time.data = show_tickets[0].start_time
    form.end_time.data = show_tickets[0].end_time
    form.tickets_price.data = show_tickets[0].price
  if show_event: # if there is an event, prefill the event in form
    form.name.data = show_event.name
    form.description.data = show_event.description
    form.location.data = show_event.location
    form.activity.data = show_event.activity
    form.host_name.data = show_event.host_name
    form.host_experience.data = show_event.host_experience
    form.host_contact.data = show_event.host_contact
    form.image.data = show_event.image
    form.tickets_available.data = show_status.available_tickets
    form.host_phone.data = show_event.host_contact
    if show_event and show_event.experience_required: # prefill the experience levels in form
      form.experience_required.data = show_event.experience_required.split(', ')
    else:
      form.experience_required.data = []
  
  print('Method type: ', request.method)
  if request.method == 'POST':
     event_id = request.form.get('event_id')
     if event_id == 'None': # convert to usable values
        event_id = None
     else:
        event_id = int(event_id)
     if 'action' in request.form:
        temp_status = 'Open'
        if request.form['action'] == 'Cancel Event': # if cancelling event, remove all tickets and cancel status
          form.tickets_available.data = 0
          temp_status = 'cancelled'
          flash('Successfully cancelled event', 'success')
        elif form.validate_on_submit():
          try:
            form.validate_dates()
          except ValidationError as e:
            flash(e, 'danger')
            print(form.errors)
            return render_template('hobbies/createevent.html', form=form)
          else:
            # get the selected experience levels and convert to string
            experience_str = ', '.join(form.experience_required.data)
            # call the function that checks and returns image
            db_file_path = check_upload_file(form)
            event_data = {
              "name": form.name.data,
              "description": form.description.data,
              "image": db_file_path,
              "location": form.location.data,
              "activity": form.activity.data,
              "host_name": form.host_name.data,
              "host_experience": form.host_experience.data,
              "host_contact": form.host_contact.data,
              "experience_required": experience_str,
              "location": form.location.data,
              "host_phone": form.host_phone.data,
              "host_id": current_user.id
            }
            if event_id:
              event_data["id"] = event_id if event_id else None
              event = Event(**event_data)
              db.session.merge(event)
            else:
              event = Event(**event_data)
              db.session.add(event)
            # commit to the database
            db.session.commit()
            print(event.id)
            print('Successfully updated event')
            flash('Successfully updated event', 'success')
        else:
          print(form.errors)
          return render_template('hobbies/createevent.html', form=form)

        # create tickets for the event
        db.session.query(Ticket).filter_by(event_id=event_id, user_id = None).delete() # delete all un-bought tickets
        for _ in range(form.tickets_available.data):
          ticket = Ticket(price=form.tickets_price.data, start_date=form.start_date.data,
          end_date=form.end_date.data, start_time=form.start_time.data, end_time=form.end_time.data, event_id=event.id)
          db.session.add(ticket)
        db.session.commit()
        # create status for the event
        if temp_status == 'cancelled':
          current_status = 'Cancelled'
        elif form.start_date.data < datetime.now().date():
            current_status = 'Inactive'
        elif form.start_time.data < datetime.now().time() and form.start_date.data == datetime.now().date():
            current_status = 'Inactive'
        elif form.tickets_available.data == 0:
            current_status = 'Sold Out'
        else:
          current_status = 'Open'

        status_data = {
          "status": current_status,
          "available_tickets": form.tickets_available.data,
        }

        if event_id:
          status_data["event_id"] = event_id
          show_status = db.session.scalar(db.select(Status).where(Status.event_id == event_id))
          if show_status:
              status_data["id"] = show_status.id  # Set the id for existing status
          print(status_data)
        else:
          status_data["event_id"] = event.id

        # Unpack status_data into the Status constructor
        event_status = Status(
          id=status_data.get("id"),  # This will be None if not updating an existing status
          status=status_data["status"],
          available_tickets=status_data["available_tickets"],
          event_id=status_data["event_id"]
        )
        db.session.merge(event_status)
        db.session.commit()
        # Always end with redirect when form is valid

        #### temporarily redirect to image - redir to event's page later
        return redirect(url_for('main.index'))
  return render_template('hobbies/createevent.html', form=form)

@mainbp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
  event_id = request.args.get('event_id')
  event = db.session.scalar(db.select(Event).where(Event.id == event_id))

  available_tickets = db.session.query(Ticket).filter(
    Ticket.event_id == event_id,
    Ticket.user_id.is_(None)).all()
  form = TicketForm()
  if form.validate_on_submit():
    if form.num_tickets.data <= len(available_tickets):
      new_order = Order(order_date=datetime.now(), user_id=current_user.id)
      db.session.add(new_order)
      db.session.flush()
      if form.num_tickets.data == len(available_tickets):
        status = db.session.scalar(db.select(Status).where(Status.event_id == event_id))
        status.status = 'Sold Out'
        status.available_tickets = 0
        db.session.commit()
      for ticket in available_tickets[:form.num_tickets.data]:
        ticket.user_id = current_user.id
        ticket.order_id = new_order.id
      new_order.ticket_id = available_tickets[0].id

      flash('Tickets bought successfully', 'success')
      event_status = db.session.query(Status).filter(
        Status.event_id == event_id).one()
      event_status.available_tickets -= form.num_tickets.data
      if event_status.available_tickets == 0:
        event_status.status = 'Sold Out'
      db.session.commit()
    else:
      print(form.errors)
      flash('Not enough tickets available', 'danger')
      return render_template('buyTickets.html', form=form, tickets=available_tickets[0], event=event, num_tickets=len(available_tickets), user=current_user)
    
    #### temporarily redirect to index - redir to tickets page later
    return redirect(url_for('main.index'))
  else:
   print(form.errors)
  return render_template('buyTickets.html', form=form, tickets=available_tickets[0], event=event, num_tickets=len(available_tickets), user=current_user)

@mainbp.route('/tickets', methods=['GET', 'POST'])
@login_required
def ticket():
  tickets = db.session.scalars(db.select(Ticket).where(Ticket.user_id == current_user.id)).all()
  # get the event details for each ticket
  ticket_by_event = {}
  for ticket in tickets:
    # remove all tickets which share the same event id
    if ticket.event_id in ticket_by_event:
      ticket_by_event[ticket.event_id]['count'] += 1
      ticket_by_event[ticket.event_id]['total_price'] += ticket.price
    else:
      status = db.session.scalar(db.select(Status).where(Status.event_id == ticket.event_id))
      ticket_by_event[ticket.event_id] = {
        'count': 1,
        'total_price': ticket.price,
        'start_time' : ticket.start_time,
        'end_time' : ticket.end_time,
        'start_date' : ticket.start_date,
        'end_date' : ticket.end_date,
        'order_id' : ticket.order_id,
        'order_date' : ticket.order.order_date,
        'status' : status.status
      }
  print(ticket_by_event)
  events = {}
  for event_id in ticket_by_event.keys():
        event = db.session.scalar(db.select(Event).where(Event.id == event_id))
        if event:
            events[event_id] = event  # Store the event by its ID
  
  print(events)
  return render_template('manageTickets.html', tickets=ticket_by_event, events=events)

@mainbp.route('/my_events', methods=['GET', 'POST'])
@login_required
def my_events():
  events = db.session.scalars(db.select(Event).where(Event.host_id == current_user.id)).all()
  return render_template('myEvents.html', events=events)

