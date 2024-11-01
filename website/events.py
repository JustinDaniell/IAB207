from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Comment, Ticket, Status
from .forms import CommentForm, EventForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

eventbp = Blueprint('event', __name__, url_prefix='/events')

@eventbp.route('/<id>')
def show(id):
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    tickets = db.session.scalars(db.select(Ticket).where(Ticket.event_id == event.id, Ticket.user_id == None)).first()
    status = db.session.scalar(db.select(Status).where(Status.event_id == event.id))
    # create the comment form
    cform = CommentForm()    
    return render_template('hobbies/showevent.html', event=event, form=cform, ticket=tickets, status=status) 

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


@eventbp.route('/<id>/comment', methods=['GET', 'POST'])
@login_required  
def comment(id):  
    form = CommentForm()  
    # get the event object associated to the page and the comment
    event = db.session.scalar(db.select(Event).where(Event.id==id))  
    if form.validate_on_submit():  
      # read the comment from the form
      comment = Comment(title=form.title.data, text=form.text.data, event=event, user=current_user) 
      # here the back-referencing works - comment.event is set
      # and the link is created
      db.session.add(comment) 
      db.session.commit() 

      # flashing a message which needs to be handled by the html  
      flash('Your comment has been added', 'success') 
    # using redirect sends a GET request to event.show
    return redirect(url_for('event.show', id=id))
