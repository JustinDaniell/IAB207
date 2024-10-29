from flask import Blueprint, render_template, request, redirect, url_for
from .models import Event, User
from .forms import EventForm
from . import db
import os
from werkzeug.utils import secure_filename

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
def create():
  print('Method type: ', request.method)
  form = EventForm()
  if form.validate_on_submit():
    # call the function that checks and returns image
    db_file_path = check_upload_file(form)
    event = Event(name=form.name.data, description=form.description.data, 
    image=db_file_path, location=form.location.data, 
    activity=form.activity.data, host_name=form.host_name.data, 
    host_experience=form.host_experience.data, host_contact=form.host_contact.data,
    experience_required=form.experience_required.data)
    # add the object to the db session
    db.session.add(event)
    # commit to the database
    db.session.commit()
    print('Successfully created new event', 'success')
    # Always end with redirect when form is valid
    return redirect(url_for('event.create'))
  else:
   print(form.errors)
   form.image.data = None
  return render_template('hobbies/createevent.html', form=form)