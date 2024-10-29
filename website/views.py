from flask import Blueprint, render_template, request, redirect, url_for
from .models import Event
from . import db

mainbp = Blueprint('main', __name__)

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
