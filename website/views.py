from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Ticket, Status
from .forms import EventForm, TicketForm
from flask_login import current_user, login_required
from . import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

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
    events = db.session.scalars(db.select(Event)).all()
    return render_template('index.html', events=events )

@mainbp.route('/search')
def search():
    # Initialize active filters dictionary
    active_filters = {}

    # Check if the search query is provided
    if 'search' in request.args and request.args['search']:
        search_query = request.args['search']
        print(search_query)
        query = "%" + search_query + "%"

        # Collect active filters from the request args
        if 'inactive' in request.args:
            active_filters['Inactive'] = 'Yes'
        if 'sold_out' in request.args:
            active_filters['Sold Out'] = 'Yes'
        if 'open' in request.args:
            active_filters['Open'] = 'Yes'
        if 'cancelled' in request.args:
            active_filters['Cancelled'] = 'Yes'

        # Fetch events based on search query and filters
        events = db.session.scalars(
            db.select(Event).where(
                (Event.description.like(query)) |
                (Event.name.like(query))
            )
        ).all()

        # Pass events and active_filters to the template
        return render_template('index.html', events=events, active_filters=active_filters)

    else:
        return redirect(url_for('main.index'))

@mainbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  print('Method type: ', request.method)
  form = EventForm()
  if form.validate_on_submit():
    # get the selected experience levels and convert to string
    experience_selected = form.experience_required.data.get('checkboxes', [])
    experience_str = ', '.join(experience_selected)

    # call the function that checks and returns image
    db_file_path = check_upload_file(form)
    event = Event(name=form.name.data, description=form.description.data, 
    image=db_file_path, location=form.location.data, 
    activity=form.activity.data, host_name=form.host_name.data, 
    host_experience=form.host_experience.data, host_contact=form.host_contact.data,
    experience_required=experience_str)
    # add the objects to the db session
    db.session.add(event)
    # commit to the database
    db.session.commit()
    print('Successfully created new event', 'success')
    # create tickets for the event
    for _ in range(form.tickets_avaliable.data):
       ticket = Ticket(price=form.tickets_price.data, start_date=form.start_date.data,
       end_date=form.end_date.data, start_time=form.start_time.data, end_time=form.end_time.data, event_id=event.id)
       db.session.add(ticket)
    db.session.commit()
    # create status for the event
    if form.start_date.data < datetime.now().date():
        current_status = 'Inactive'
    elif form.start_time.data < datetime.now().time() and form.start_date.data == datetime.now().date():
        current_status = 'Inactive'
    elif form.tickets_avaliable.data == 0:
        current_status = 'Sold Out'
    else:
       current_status = 'Open'
    event_status = Status(status=current_status, avaliable_tickets=form.tickets_avaliable.data, event_id=event.id)
    db.session.add(event_status)
    db.session.commit()
    # Always end with redirect when form is valid

    #### temporarily redirect to image - redir to event's page later
    return redirect(url_for('main.index'))
  else:
   print(form.errors)
  return render_template('hobbies/createevent.html', form=form)

@mainbp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
  event_id = request.args.get('event_id')
  event = db.session.scalar(db.select(Event).where(Event.id == event_id))
  print('Method type: ', request.method)
  print('user id: ', current_user)
  available_tickets = db.session.query(Ticket).filter(
    Ticket.event_id == event_id,
    Ticket.user_id.is_(None)).all()
  form = TicketForm()
  if form.validate_on_submit():
    if form.num_tickets.data <= len(available_tickets):
      for ticket in available_tickets[:form.num_tickets.data]:
         ticket.user_id = current_user.id
      db.session.commit()
      # flash('Tickets bought successfully', 'success')
    else:
      print(form.errors)
      # flash('Not enough tickets available', 'error')
      return render_template('buyTickets.html', form=form, tickets=available_tickets[0], event=event, num_tickets=len(available_tickets), user=current_user)

    #### temporarily redirect to index - redir to tickets page later
    return redirect(url_for('main.index'))
  else:
   print(form.errors)
  return render_template('buyTickets.html', form=form, tickets=available_tickets[0], event=event, num_tickets=len(available_tickets), user=current_user)